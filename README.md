# Perceived & Effective

Um sistema que mede e age sobre a diferença entre o **valor que as pessoas acham que uma tarefa entrega** e o **valor que ela realmente entrega**.

---

## A Proposta

Equipes de software frequentemente sofrem de dois problemas silenciosos:

- **Trabalho subvalorizado:** a tarefa entrega muito, mas ninguém percebe. A documentação é fraca, o impacto é invisível, e o trabalho passa despercebido nas revisões de prioridade.
- **Expectativas infladas:** stakeholders acreditam que a tarefa vai resolver mais do que ela realmente resolve. Isso leva a decepções, retrabalho, e decisões de priorização equivocadas.

O *Perceived & Effective* expõe esse gap. Para cada issue do GitLab, o sistema:

1. **Calcula o valor efetivo** — dois agentes de IA independentes avaliam a tarefa: um pela ótica de negócio (impacto, alcance, alinhamento estratégico), outro pela ótica técnica (manutenibilidade, observabilidade, redução de dívida técnica). A nota final é a média das duas avaliações.

2. **Coleta o valor percebido** — managers e membros do time registram o quanto acham que a tarefa vale (0–10) e por quê.

3. **Detecta divergências** — quando a diferença entre percebido e efetivo ultrapassa 3 pontos, o sistema aciona um terceiro agente.

4. **Gera uma recomendação** — o agente analisa a direção do gap ("trabalho invisível" vs "expectativa inflada") e produz um parágrafo concreto e acionável para o criador da tarefa, postado diretamente como comentário na issue do GitLab.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│  BFF (porta 8000)                                   │
│  FastAPI · PostgreSQL · APScheduler                 │
│                                                     │
│  • CRUD de usuários, tarefas e avaliações           │
│  • Cron job: sincroniza issues abertas do GitLab    │
│    a cada POLL_INTERVAL_MINUTES minutos             │
│  • Chama o serviço de agentes quando necessário     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────┐
│  Agents (porta 8001)                                │
│  FastAPI · Google ADK · Gemini                      │
│                                                     │
│  POST /appraisal       → avalia valor efetivo       │
│  POST /recommendation  → gera recomendação          │
└─────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  PostgreSQL (porta 5432)                            │
│  Tabelas: users, tasks, appraisals, recommendations │
└─────────────────────────────────────────────────────┘
```

**Fluxo do cron job (por run):**

```
GitLab API
    │
    ▼
Busca issues abertas
    │
    ▼ para cada issue
Upsert como Task no banco
    │
    ├── task.effective é NULL? ──► chama /appraisal (max 3 por run)
    │                                      │
    │                               armazena effective + explanation
    │
    └── para cada appraisal da task
            │
            └── |perceived - effective| > 3? ──► chama /recommendation
                                                         │
                                                  salva no banco
                                                         │
                                                  posta comentário na issue
```

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Chave de API do Google Gemini (**AI Studio**, não Google Cloud)
  - Acesse `aistudio.google.com` → Get API key → Create API key
  - A chave começa com `AIzaSy...`
- Token de acesso pessoal do GitLab com permissão `read_api`
- ID numérico do projeto GitLab a ser sincronizado

---

## Configuração

Copie o arquivo de exemplo e preencha os valores:

```bash
cp src/.env.example src/.env
```

```env
# Gemini (serviço de agentes)
GOOGLE_API_KEY=AIzaSy...sua-chave-aqui
GEMINI_MODEL=gemini-2.5-flash

# GitLab (BFF)
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-...seu-token-aqui
GITLAB_PROJECT_ID=12345678

# Intervalo do cron job em minutos
POLL_INTERVAL_MINUTES=1
```

> **Atenção:** O free tier do Gemini tem limite de 15 requisições/minuto e 1.500/dia. Com `POLL_INTERVAL_MINUTES=1` e múltiplas tasks sem avaliação, o limite diário é atingido rapidamente. Recomenda-se `POLL_INTERVAL_MINUTES=5` ou mais em ambientes de desenvolvimento.

---

## Como rodar

```bash
cd src
docker compose up --build
```

Os serviços sobem na seguinte ordem:
1. **PostgreSQL** — aguarda `pg_isready`
2. **Agents** — aguarda PostgreSQL; inicia na porta `8001`
3. **BFF** — aguarda ambos; cria as tabelas e agenda o cron; inicia na porta `8000`

Para rodar em background:

```bash
docker compose up --build -d
docker compose logs -f
```

---

## API

### BFF — `http://localhost:8000`

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/auth/register` | Cria conta (email, password) |
| `POST` | `/auth/login` | Autentica usuário |
| `GET` | `/tasks/unevaluated/{user_id}` | Tasks ainda não avaliadas pelo usuário |
| `GET` | `/tasks/effective` | Todas as tasks com valor efetivo calculado |
| `GET` | `/tasks/effective/{task_id}` | Task individual |
| `POST` | `/appraisals` | Registra avaliação percebida (user_id, task_id, perceived 0–10, explanation) |

Documentação interativa disponível em `http://localhost:8000/docs`.

### Agents — `http://localhost:8001`

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/appraisal` | Avalia valor efetivo de uma task |
| `POST` | `/recommendation` | Gera recomendação para fechar o gap |

Documentação interativa disponível em `http://localhost:8001/docs`.

---

## Estrutura do projeto

```
perceived-and-effective/
├── src/
│   ├── docker-compose.yaml
│   ├── .env.example
│   │
│   ├── bff/                         # Backend for Frontend
│   │   └── src/
│   │       ├── main.py              # App + scheduler
│   │       ├── core/                # Config, database, security
│   │       ├── data/models/         # Users, Tasks, Appraisals, Recommendations
│   │       ├── api/routes/          # auth, tasks, appraisals
│   │       └── pipeline/gitlab_sync/sync.py  # Lógica do cron job
│   │
│   └── agents/                      # Serviço de agentes IA
│       └── src/
│           ├── agents/
│           │   ├── effective.py     # Dois agentes independentes (negócio + técnico)
│           │   └── recommendation.py
│           ├── routes/              # /appraisal, /recommendation
│           └── prompts.py           # System prompts dos agentes
```

## Link para o vídeo
https://canva.link/mkrr7y5nquu3t4d