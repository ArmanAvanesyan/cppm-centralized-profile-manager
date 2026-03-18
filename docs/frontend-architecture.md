# Frontend Architecture

## Layers (inside `frontend/app`)

1. **Presentation** – Screens, routes, widgets that compose design-system components. No business logic; only UI and user events.
2. **Application** – State management (Riverpod), use cases, navigation flows. Orchestrates data and UI state.
3. **Data** – API clients, storage connectors (Google Drive, Dropbox, OneDrive), file/upload handling. Talks to backend and platform APIs.
4. **Core** – Models, value objects (Profile, Experience, Skill, Education, StorageAccount), encryption helpers. Shared across layers.

## State management

- **Riverpod** – Providers for auth state, storage connections, import state, encryption lock state. Use `flutter_riverpod` and keep providers close to features.

## Navigation

- **go_router** – Declarative routing; URL-like paths for deep linking and desktop. Routes for: splash, welcome, auth (email, OTP, OAuth), storage, import, encryption, profile.

## Module boundaries

- **design_system** – No dependency on app or backend; only Flutter SDK.
- **app** – Depends on `design_system`; may depend on backend API client packages or HTTP directly.

## Platform-specific notes

- **iOS/Android** – Use platform configs in `ios/` and `android/`; test on devices/simulators.
- **Windows/macOS** – Enable desktop in Flutter; use responsive layouts and optional keyboard shortcuts. Run `flutter create . --platforms=windows,macos` in `app/` if platform folders are missing.

## Key files (to be created)

- `lib/app.dart` – Root widget and theme.
- `lib/router.dart` – go_router configuration.
- `lib/features/auth/` – Auth screens and providers.
- `lib/features/storage/` – Storage screens and providers.
- `lib/features/import/` – Resume/LinkedIn import screens and providers.
- `lib/features/encryption/` – Encryption setup/unlock screens and providers.
- `lib/core/models/` – Profile, Experience, Skill, etc.
