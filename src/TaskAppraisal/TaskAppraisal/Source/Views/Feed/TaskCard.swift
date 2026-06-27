import SwiftUI

struct TaskCard: View {
    let task: GitLabTask
    let onEvaluate: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {

            // Title
            Text(task.title)
                .font(.headline)
                .foregroundStyle(.primary)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)

            // Description
            if !task.body.isEmpty {
                Text(task.body)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(5)
                    .fixedSize(horizontal: false, vertical: true)
            }

            // URL badge
            if let url = task.url {
                Label(url, systemImage: "link")
                    .font(.caption)
                    .foregroundStyle(.blue)
                    .lineLimit(1)
                    .truncationMode(.middle)
            }

            Divider()

            // Evaluate button
            Button(action: onEvaluate) {
                HStack(spacing: 6) {
                    Image(systemName: "star.fill")
                        .font(.caption)
                    Text("Avaliar task")
                        .font(.subheadline.bold())
                }
                .frame(maxWidth: .infinity)
                .frame(height: 40)
                .background(.blue.opacity(0.1), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
                .foregroundStyle(.blue)
            }
            .buttonStyle(.plain)
        }
        .padding(16)
        .background(Color.appCard, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        .shadow(color: .black.opacity(0.05), radius: 10, y: 4)
    }
}
