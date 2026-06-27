import Foundation

// MARK: - Error

enum APIError: LocalizedError {
    case invalidURL
    case network(Error)
    case decoding(Error)
    case server(Int, String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:          return "URL inválida"
        case .network(let e):      return "Erro de rede: \(e.localizedDescription)"
        case .decoding(let e):     return "Erro ao processar resposta: \(e.localizedDescription)"
        case .server(let c, let m): return "Erro \(c): \(m)"
        }
    }
}

// MARK: - Service

final class APIService {
    static let shared = APIService()
    private init() {}

    // ⚠️ Troque para seu host em produção
    var baseURL = "http://localhost:8000"

    // MARK: Core

    private func perform<T: Decodable>(
        path: String,
        method: String = "GET",
        body: (any Encodable)? = nil
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let body {
            req.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response): (Data, URLResponse)
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.network(error)
        }

        guard let http = response as? HTTPURLResponse else {
            throw APIError.network(URLError(.badServerResponse))
        }

        guard (200...299).contains(http.statusCode) else {
            let msg = String(data: data, encoding: .utf8) ?? "Erro desconhecido"
            throw APIError.server(http.statusCode, msg)
        }

        do {
            // DEBUG — remover após identificar o problema
            if let raw = String(data: data, encoding: .utf8) {
                print("🔍 [\(path)] RAW:", raw)
            }
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw APIError.decoding(error)
        }
    }

    // MARK: Auth

    func register(email: String, password: String) async throws -> AuthResponse {
        try await perform(
            path: "/auth/register",
            method: "POST",
            body: RegisterRequest(email: email, password: password)
        )
    }

    func login(email: String, password: String) async throws -> AuthResponse {
        try await perform(
            path: "/auth/login",
            method: "POST",
            body: LoginRequest(email: email, password: password)
        )
    }

    // MARK: Tasks

    func fetchUnevaluatedTasks(userId: UUID) async throws -> [GitLabTask] {
        try await perform(path: "/tasks/unevaluated/\(userId.uuidString.lowercased())")
    }

    // MARK: Appraisals

    func sendAppraisal(
        userId: UUID,
        taskId: UUID,
        perceived: Int,
        explanation: String?
    ) async throws -> SendAppraisalResponse {
        try await perform(
            path: "/appraisals",
            method: "POST",
            body: SendAppraisalRequest(
                userId: userId,
                taskId: taskId,
                perceived: perceived,
                explanation: explanation
            )
        )
    }
}
