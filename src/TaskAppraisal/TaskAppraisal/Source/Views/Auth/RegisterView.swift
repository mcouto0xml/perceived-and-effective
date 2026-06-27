import SwiftUI

struct RegisterView: View {
    @EnvironmentObject var auth: AuthManager
    @Environment(\.dismiss) var dismiss

    @State private var email           = ""
    @State private var password        = ""
    @State private var confirmPassword = ""
    @State private var localError: String?

    private var formError: String? { localError ?? auth.errorMessage }

    var body: some View {
        ZStack {
            Color.appBackground.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 32) {
                    // Hero
                    VStack(spacing: 10) {
                        ZStack {
                            Circle()
                                .fill(.blue.opacity(0.12))
                                .frame(width: 96, height: 96)
                            Image(systemName: "person.badge.plus.fill")
                                .font(.system(size: 44))
                                .foregroundStyle(.blue.gradient)
                        }

                        Text("Criar Conta")
                            .font(.system(.largeTitle, design: .rounded, weight: .bold))

                        Text("Comece a avaliar tasks agora")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.top, 48)

                    // Form
                    VStack(spacing: 14) {
                        AuthTextField(icon: "envelope.fill", placeholder: "Email", text: $email)
                            .keyboardType(.emailAddress)
                            .textInputAutocapitalization(.never)

                        AuthTextField(icon: "lock.fill", placeholder: "Senha", text: $password, isSecure: true)

                        AuthTextField(
                            icon: "lock.rotation",
                            placeholder: "Confirmar senha",
                            text: $confirmPassword,
                            isSecure: true
                        )
                    }

                    if let error = formError {
                        ErrorBanner(message: error)
                    }

                    PrimaryButton(title: "Cadastrar", isLoading: auth.isLoading) {
                        localError = nil
                        auth.clearError()
                        guard !email.isEmpty, !password.isEmpty else {
                            localError = "Preencha todos os campos"
                            return
                        }
                        guard password == confirmPassword else {
                            localError = "As senhas não coincidem"
                            return
                        }
                        await auth.register(email: email, password: password)
                    }

                    Button("Já tenho conta") { dismiss() }
                        .font(.subheadline)
                        .foregroundStyle(.blue)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 40)
            }
        }
        .navigationTitle("Cadastro")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    NavigationStack { RegisterView() }
        .environmentObject(AuthManager())
}
