import SwiftUI
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

// MARK: - Colors (semânticos, respeitam dark mode)

extension Color {
    static let appBackground: Color = {
        #if canImport(UIKit)
        return Color(UIColor.systemGroupedBackground)
        #else
        return Color(NSColor.windowBackgroundColor)
        #endif
    }()

    static let appCard: Color = {
        #if canImport(UIKit)
        return Color(UIColor.secondarySystemGroupedBackground)
        #else
        return Color(NSColor.controlBackgroundColor)
        #endif
    }()

    static let appSurface: Color = {
        #if canImport(UIKit)
        return Color(UIColor.tertiarySystemGroupedBackground)
        #else
        return Color(NSColor.underPageBackgroundColor)
        #endif
    }()
}

// MARK: - AuthTextField

struct AuthTextField: View {
    let icon: String
    let placeholder: String
    @Binding var text: String
    var isSecure: Bool = false

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: icon)
                .foregroundStyle(.secondary)
                .frame(width: 20)

            if isSecure {
                SecureField(placeholder, text: $text)
                    .textContentType(isSecure ? .password : .none)
            } else {
                TextField(placeholder, text: $text)
                    .autocorrectionDisabled()
            }
        }
        .padding(16)
        .background(Color.appCard, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
    }
}

// MARK: - PrimaryButton

struct PrimaryButton: View {
    let title: String
    var isLoading: Bool = false
    let action: () async -> Void

    var body: some View {
        Button {
            Task { await action() }
        } label: {
            ZStack {
                if isLoading {
                    ProgressView().tint(.white)
                } else {
                    Text(title)
                        .font(.headline)
                        .foregroundStyle(.white)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 52)
            .background(
                isLoading
                    ? AnyShapeStyle(Color.blue.opacity(0.6))
                    : AnyShapeStyle(LinearGradient(colors: [.blue, .blue.opacity(0.8)], startPoint: .leading, endPoint: .trailing)),
                in: RoundedRectangle(cornerRadius: 13, style: .continuous)
            )
        }
        .disabled(isLoading)
    }
}

// MARK: - ErrorBanner

struct ErrorBanner: View {
    let message: String

    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: "exclamationmark.circle.fill")
                .foregroundStyle(.red)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.red)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.red.opacity(0.08), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }
}

// MARK: - LoadingView

struct LoadingView: View {
    var message: String = "Carregando..."

    var body: some View {
        VStack(spacing: 14) {
            ProgressView()
                .scaleEffect(1.4)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
}

// MARK: - EmptyStateView

struct EmptyStateView: View {
    let icon: String
    let iconColor: Color
    let title: String
    let message: String
    var actionLabel: String = "Atualizar"
    let onAction: () -> Void

    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: icon)
                .font(.system(size: 64))
                .foregroundStyle(iconColor.gradient)

            VStack(spacing: 6) {
                Text(title)
                    .font(.title3.bold())
                Text(message)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
            }

            Button(actionLabel, action: onAction)
                .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

// MARK: - ScoreBadge

struct ScoreBadge: View {
    let score: Int

    private var color: Color {
        switch score {
        case 0...3:  return .red
        case 4...6:  return .orange
        case 7...8:  return .yellow
        default:     return .green
        }
    }

    var body: some View {
        Text("\(score)")
            .font(.system(.callout, design: .rounded, weight: .bold))
            .foregroundStyle(.white)
            .frame(width: 32, height: 32)
            .background(color.gradient, in: Circle())
    }
}
