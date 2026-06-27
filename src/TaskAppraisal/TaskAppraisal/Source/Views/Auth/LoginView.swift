import SwiftUI

struct LoginView: View {
    @EnvironmentObject var auth: AuthManager

    @State private var email    = ""
    @State private var password = ""
    @State private var goRegister = false

    var body: some View {
        NavigationStack {
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
                                Image(systemName: "checkmark.seal.fill")
                                    .font(.system(size: 48))
                                    .foregroundStyle(.blue.gradient)
                            }

                            Text("Appraisal")
                                .font(.system(.largeTitle, design: .rounded, weight: .bold))

                            Text("Avalie as tasks da sua equipe")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                        .padding(.top, 60)

                        // Form
                        VStack(spacing: 14) {
                            AuthTextField(icon: "envelope.fill", placeholder: "Email", text: $email)
                                .keyboardType(.emailAddress)
                                .textInputAutocapitalization(.never)

                            AuthTextField(icon: "lock.fill", placeholder: "Senha", text: $password, isSecure: true)
                        }

                        if let error = auth.errorMessage {
                            ErrorBanner(message: error)
                        }

                        // CTA
                        VStack(spacing: 14) {
                            PrimaryButton(title: "Entrar", isLoading: auth.isLoading) {
                                await auth.login(email: email, password: password)
                            }

                            Button {
                                auth.clearError()
                                goRegister = true
                            } label: {
                                Text("Não tem conta? ")
                                    .foregroundStyle(.secondary)
                                + Text("Cadastre-se")
                                    .foregroundStyle(.blue)
                                    .bold()
                            }
                            .font(.subheadline)
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 40)
                }
            }
            .navigationDestination(isPresented: $goRegister) {
                RegisterView()
            }
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AuthManager())
}
