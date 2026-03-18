# CPPM Frontend

Flutter multi-platform app (iOS, Android, Windows, macOS) and shared design system package.

## Structure

- **`app/`** – Main Flutter application. Uses Riverpod and go_router.
- **`packages/design_system/`** – Shared theme, tokens, and UI components.

## Setup

1. Install [Flutter](https://flutter.dev) (stable, with iOS/Android/Windows/macOS support).
2. From this directory:
   ```bash
   cd app
   flutter pub get
   ```
   If platform folders (`android/`, `ios/`, `windows/`, `macos/`) are missing, run:
   ```bash
   flutter create . --platforms=ios,android,windows,macos --org com.cppm
   ```
3. Run:
   ```bash
   flutter run -d windows   # or chrome, macos, ios, android
   ```

## Workspace

The app depends on the local `design_system` package via `path: ../packages/design_system`. No workspace-level `flutter pub get` is required; run `flutter pub get` inside `app/` and `packages/design_system/` as needed.
