import Foundation

// MARK: - Auth

struct RegisterRequest: Codable {
    let email: String
    let password: String
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct AuthResponse: Codable, Identifiable {
    let id: UUID
    let email: String
}

// MARK: - Task

struct GitLabTask: Identifiable, Codable {
    let id: UUID
    let name: String          // campo real da API
    let description: String?
    let url: String?

    // Aliases para as views
    var title: String { name }
    var body: String  { description ?? "" }
}

// MARK: - Appraisal

struct SendAppraisalRequest: Codable {
    let userId: UUID
    let taskId: UUID
    let perceived: Int
    let explanation: String?

    enum CodingKeys: String, CodingKey {
        case userId      = "user_id"
        case taskId      = "task_id"
        case perceived, explanation
    }
}

struct SendAppraisalResponse: Codable, Identifiable {
    let id: UUID
    let userId: UUID
    let taskId: UUID
    let perceived: Int
    let explanation: String?

    enum CodingKeys: String, CodingKey {
        case id
        case userId  = "user_id"
        case taskId  = "task_id"
        case perceived, explanation
    }
}
