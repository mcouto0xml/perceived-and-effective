import Foundation
import SwiftUI
import Combine

final class AuthManager: ObservableObject {
    @Published var currentUser: AuthResponse?
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let sessionKey = "auth_user_v1"

    init() { restoreSession() }

    // MARK: - Public

    func register(email: String, password: String) async {
        begin()
        do {
            let user = try await APIService.shared.register(email: email, password: password)
            commit(user)
        } catch {
            fail(error)
        }
    }

    func login(email: String, password: String) async {
        begin()
        do {
            let user = try await APIService.shared.login(email: email, password: password)
            commit(user)
        } catch {
            fail(error)
        }
    }

    func logout() {
        currentUser = nil
        isAuthenticated = false
        UserDefaults.standard.removeObject(forKey: sessionKey)
    }

    func clearError() { errorMessage = nil }

    // MARK: - Private (MainActor para tocar @Published com segurança)

    @MainActor
    private func begin() {
        isLoading = true
        errorMessage = nil
    }

    @MainActor
    private func commit(_ user: AuthResponse) {
        currentUser = user
        isAuthenticated = true
        isLoading = false
        persist(user)
    }

    @MainActor
    private func fail(_ error: Error) {
        errorMessage = error.localizedDescription
        isLoading = false
    }

    private func persist(_ user: AuthResponse) {
        if let data = try? JSONEncoder().encode(user) {
            UserDefaults.standard.set(data, forKey: sessionKey)
        }
    }

    private func restoreSession() {
        guard
            let data = UserDefaults.standard.data(forKey: sessionKey),
            let user = try? JSONDecoder().decode(AuthResponse.self, from: data)
        else { return }
        currentUser = user
        isAuthenticated = true
    }
}
