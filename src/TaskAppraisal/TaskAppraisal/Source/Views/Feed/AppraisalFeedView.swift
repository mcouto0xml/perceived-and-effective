import SwiftUI
import Combine

// MARK: - ViewModel

final class FeedViewModel: ObservableObject {
    @Published var tasks: [GitLabTask]  = []
    @Published var isLoading            = false
    @Published var errorMessage: String?
    @Published var selectedTask: GitLabTask?
    @Published var toast: ToastItem?

    struct ToastItem: Identifiable {
        let id = UUID()
        let score: Int
        let title: String
    }

    @MainActor
    func load(userId: UUID) async {
        isLoading = true
        errorMessage = nil
        do {
            tasks = try await APIService.shared.fetchUnevaluatedTasks(userId: userId)
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    @MainActor
    func submitAppraisal(
        task: GitLabTask,
        userId: UUID,
        perceived: Int,
        explanation: String?
    ) async {
        do {
            _ = try await APIService.shared.sendAppraisal(
                userId: userId,
                taskId: task.id,
                perceived: perceived,
                explanation: explanation
            )
            withAnimation(.spring(response: 0.4, dampingFraction: 0.75)) {
                tasks.removeAll { $0.id == task.id }
            }
            toast = ToastItem(score: perceived, title: task.title)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// MARK: - Feed View

struct AppraisalFeedView: View {
    @EnvironmentObject var auth: AuthManager
    @StateObject private var vm = FeedViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                Color.appBackground.ignoresSafeArea()
                content
            }
            .navigationTitle("Tasks")
            .navigationBarTitleDisplayMode(.large)
            .toolbar { toolbarContent }
            .sheet(item: $vm.selectedTask) { task in
                AppraisalSheet(task: task) { perceived, explanation in
                    guard let user = auth.currentUser else { return }
                    await vm.submitAppraisal(
                        task: task,
                        userId: user.id,
                        perceived: perceived,
                        explanation: explanation
                    )
                }
                .presentationDetents([.large])
                .presentationDragIndicator(.visible)
            }
            .task {
                guard let user = auth.currentUser else { return }
                await vm.load(userId: user.id)
            }
            .refreshable {
                guard let user = auth.currentUser else { return }
                await vm.load(userId: user.id)
            }
            .overlay(alignment: .bottom) {
                if let toast = vm.toast {
                    ToastView(score: toast.score, taskTitle: toast.title)
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                        .onAppear {
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2.8) {
                                withAnimation { vm.toast = nil }
                            }
                        }
                        .id(toast.id)
                }
            }
        }
    }

    // MARK: - Content switch

    @ViewBuilder
    private var content: some View {
        if vm.isLoading && vm.tasks.isEmpty {
            LoadingView(message: "Carregando tasks...")
        } else if let error = vm.errorMessage, vm.tasks.isEmpty {
            EmptyStateView(
                icon: "exclamationmark.triangle.fill",
                iconColor: .orange,
                title: "Erro ao carregar",
                message: error,
                actionLabel: "Tentar novamente"
            ) {
                Task {
                    guard let user = auth.currentUser else { return }
                    await vm.load(userId: user.id)
                }
            }
        } else if vm.tasks.isEmpty && !vm.isLoading {
            EmptyStateView(
                icon: "checkmark.circle.fill",
                iconColor: .green,
                title: "Tudo avaliado!",
                message: "Você avaliou todas as tasks disponíveis no momento.",
                actionLabel: "Verificar novamente"
            ) {
                Task {
                    guard let user = auth.currentUser else { return }
                    await vm.load(userId: user.id)
                }
            }
        } else {
            feedList
        }
    }

    private var feedList: some View {
        ScrollView {
            LazyVStack(spacing: 14) {
                // Summary pill
                if !vm.tasks.isEmpty {
                    HStack(spacing: 6) {
                        Image(systemName: "clock.badge.exclamationmark.fill")
                            .foregroundStyle(.orange)
                        Text("\(vm.tasks.count) task\(vm.tasks.count > 1 ? "s" : "") pendente\(vm.tasks.count > 1 ? "s" : "")")
                            .font(.subheadline.bold())
                            .foregroundStyle(.primary)
                    }
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                    .background(Color.appCard, in: Capsule())
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                ForEach(vm.tasks) { task in
                    TaskCard(task: task) {
                        vm.selectedTask = task
                    }
                    .transition(
                        .asymmetric(
                            insertion: .opacity.combined(with: .move(edge: .top)),
                            removal:   .opacity.combined(with: .scale(scale: 0.95))
                        )
                    )
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
        }
    }

    // MARK: - Toolbar

    @ToolbarContentBuilder
    private var toolbarContent: some ToolbarContent {
        ToolbarItem(placement: .navigationBarLeading) {
            if let email = auth.currentUser?.email {
                Label(email, systemImage: "person.crop.circle.fill")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
        }
        ToolbarItem(placement: .navigationBarTrailing) {
            Button {
                auth.logout()
            } label: {
                Image(systemName: "rectangle.portrait.and.arrow.right")
                    .foregroundStyle(.red)
            }
        }
    }
}

// MARK: - Toast

struct ToastView: View {
    let score: Int
    let taskTitle: String

    private var scoreColor: Color {
        switch score {
        case 0...3: return .red
        case 4...6: return .orange
        case 7...8: return .yellow
        default:    return .green
        }
    }

    var body: some View {
        HStack(spacing: 12) {
            ScoreBadge(score: score)
            VStack(alignment: .leading, spacing: 2) {
                Text("Avaliação enviada!")
                    .font(.subheadline.bold())
                Text(taskTitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
            Spacer()
            Image(systemName: "checkmark.circle.fill")
                .foregroundStyle(.green)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        .shadow(color: .black.opacity(0.12), radius: 12, y: 6)
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
    }
}
