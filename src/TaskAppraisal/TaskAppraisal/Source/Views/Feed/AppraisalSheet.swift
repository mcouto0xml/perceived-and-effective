import SwiftUI

struct AppraisalSheet: View {
    let task: GitLabTask
    let onSubmit: (_ perceived: Int, _ explanation: String?) async -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var score: Double       = 5
    @State private var explanation         = ""
    @State private var isSubmitting        = false
    @FocusState private var textFocused: Bool

    // MARK: Score helpers

    private var intScore: Int { Int(score) }

    private var scoreColor: Color {
        switch intScore {
        case 0...3:  return .red
        case 4...5:  return .orange
        case 6...7:  return .yellow
        case 8...9:  return .green
        default:     return Color(hue: 0.38, saturation: 0.9, brightness: 0.75) // deep green for 10
        }
    }

    private var scoreLabel: String {
        switch intScore {
        case 0...2:  return "Muito abaixo do esperado"
        case 3...4:  return "Abaixo do esperado"
        case 5...6:  return "Dentro do esperado"
        case 7...8:  return "Acima do esperado"
        default:     return "Excepcional"
        }
    }

    // MARK: Body

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    taskSummaryCard
                    scoreCard
                    explanationCard
                    submitButton
                }
                .padding(16)
                .padding(.bottom, 8)
            }
            .background(Color.appBackground.ignoresSafeArea())
            .navigationTitle("Avaliar Task")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancelar") { dismiss() }
                        .disabled(isSubmitting)
                }
                ToolbarItem(placement: .keyboard) {
                    Button("OK") { textFocused = false }
                }
            }
        }
    }

    // MARK: - Sub-views

    private var taskSummaryCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(task.title)
                .font(.headline)

            if !task.body.isEmpty {
                Text(task.body)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(6)
            }

            if let url = task.url {
                Label(url, systemImage: "link")
                    .font(.caption)
                    .foregroundStyle(.blue)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.appCard, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private var scoreCard: some View {
        VStack(spacing: 20) {
            Text("Nota")
                .font(.headline)

            // Arc dial
            ZStack {
                // Track
                Circle()
                    .trim(from: 0.1, to: 0.9)
                    .stroke(scoreColor.opacity(0.15), style: StrokeStyle(lineWidth: 12, lineCap: .round))
                    .rotationEffect(.degrees(90))
                    .frame(width: 120, height: 120)

                // Progress
                Circle()
                    .trim(from: 0.1, to: 0.1 + (0.8 * CGFloat(score) / 10))
                    .stroke(scoreColor.gradient, style: StrokeStyle(lineWidth: 12, lineCap: .round))
                    .rotationEffect(.degrees(90))
                    .frame(width: 120, height: 120)
                    .animation(.spring(response: 0.3, dampingFraction: 0.7), value: score)

                VStack(spacing: 2) {
                    Text("\(intScore)")
                        .font(.system(size: 40, weight: .bold, design: .rounded))
                        .foregroundStyle(scoreColor)
                        .contentTransition(.numericText())
                        .animation(.spring(response: 0.3), value: intScore)

                    Text("/ 10")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Text(scoreLabel)
                .font(.subheadline.bold())
                .foregroundStyle(scoreColor)
                .animation(.easeInOut(duration: 0.2), value: intScore)

            // Slider
            VStack(spacing: 6) {
                Slider(value: $score, in: 0...10, step: 1)
                    .tint(scoreColor)
                    .animation(.easeInOut(duration: 0.1), value: score)

                HStack {
                    ForEach([0, 2, 4, 6, 8, 10], id: \.self) { v in
                        Text("\(v)")
                            .font(.caption2)
                            .foregroundStyle(intScore == v ? scoreColor : .secondary)
                            .frame(maxWidth: .infinity)
                    }
                }
            }
        }
        .padding(16)
        .background(Color.appCard, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private var explanationCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Justificativa")
                    .font(.headline)
                Spacer()
                Text("Opcional")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            TextField(
                "Ex: O código está bem estruturado, mas faltou cobertura de testes...",
                text: $explanation,
                axis: .vertical
            )
            .lineLimit(4...10)
            .focused($textFocused)
            .padding(12)
            .background(Color.appSurface, in: RoundedRectangle(cornerRadius: 10, style: .continuous))
            .font(.subheadline)
        }
        .padding(16)
        .background(Color.appCard, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private var submitButton: some View {
        PrimaryButton(title: "Enviar Avaliação", isLoading: isSubmitting) {
            isSubmitting = true
            await onSubmit(intScore, explanation.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : explanation)
            isSubmitting = false
            dismiss()
        }
    }
}
