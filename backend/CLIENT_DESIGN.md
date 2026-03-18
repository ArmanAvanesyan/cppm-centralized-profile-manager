# CPPM Client Design
**Centralized Professional Profile Manager — Client Architecture**

---

## 1. Backend API Surface (Reference)

The backend exposes six feature modules via REST at `/api/v1/`:

| Module | Prefix | Key Operations |
|---|---|---|
| Auth | `/auth` | Email OTP signup/verify, Google / Microsoft / LinkedIn OAuth, refresh, logout, `/me` |
| Profile | `/profile` | GET profile, PUT profile (basics, experience, skills), POST `/merge` |
| Resume Import | `/resume` | POST `/upload`, POST `/{id}/extract`, POST `/{id}/parse` (async jobs) |
| LinkedIn Import | `/linkedin` | POST `/import`, POST `/import/{id}/parse` (async jobs) |
| Cloud Storage | `/storage` | POST `/connect/{provider}`, GET `/callback/{provider}`, GET `/accounts` |
| Encryption | `/encryption` | POST `/init`, POST `/rotate`, GET `/status` |

Auth model: JWT access token (30 min) + refresh token (7 days). All protected routes require `Authorization: Bearer <access_token>`.

Async jobs: upload returns a `job_id`; clients must poll or await a push notification for completion status.

---

## 2. Telegram Bot (`tg-bot`)

### 2.1 Rationale & Scope

The Telegram Bot is the **lightweight, always-available** client. It targets users who want quick profile checks, async job status updates, and friction-free file imports directly from their phone without opening a full app. It is *not* suited for deep profile editing or OAuth cloud storage linking (those belong in the Flutter client).

### 2.2 Technology Stack

| Concern | Choice | Reason |
|---|---|---|
| Runtime | Python 3.12+ | Same language as backend; fast iteration |
| Framework | **aiogram 3.x** | Modern async, native FSM, webhook-first |
| HTTP client to backend | **httpx** (async) | Mirrors FastAPI's async model |
| FSM / state storage | **Redis** (via aiogram FSM Redis storage) | Persists state across restarts |
| Session storage | Redis `bot:session:{chat_id}` | Stores JWT pair per user |
| Deployment | Docker, webhook via nginx | Stateless; scales horizontally |

### 2.3 Directory Structure

```
tg-bot/
├── bot.py                  # Entry point — webhook/polling setup
├── config.py               # Settings (CPPM_API_URL, BOT_TOKEN, REDIS_URL)
├── api/
│   └── client.py           # Async CPPM API wrapper (auth, profile, resume, linkedin)
├── middlewares/
│   ├── auth.py             # Load JWT from Redis; inject into handler data
│   └── throttle.py         # Rate limiting
├── handlers/
│   ├── auth.py             # /start, email OTP flow, logout
│   ├── profile.py          # /profile view
│   ├── import_.py          # File upload → resume/linkedin import
│   ├── status.py           # /status — job status + encryption
│   └── help.py             # /help
├── states/
│   └── auth_states.py      # FSM: WaitingEmail, WaitingOTP
├── keyboards/
│   ├── main_menu.py        # Persistent reply keyboard
│   └── inline.py           # Inline keyboards for actions
├── filters/
│   └── authenticated.py    # Filter: block unauthenticated commands
└── requirements.txt
```

### 2.4 Authentication Flow

Because the bot cannot complete browser-based OAuth redirects, **Email OTP** is the primary login method. OAuth social login is surfaced as a deep-link button to the Flutter/Web client.

```
User: /start
Bot:  "Welcome! Send your email address to sign in."
      [FSM → WaitingEmail]

User: user@example.com
Bot:  "OTP sent to user@example.com. Enter the 6-digit code."
      [POST /auth/email/signup]  [FSM → WaitingOTP]

User: 123456
Bot:  "✅ Signed in! Here's your main menu."
      [POST /auth/email/verify → store access_token + refresh_token in Redis]
      [FSM → cleared]

— OR —
Bot: inline button "Sign in with Google / Microsoft →"
     → Opens CPPM Web app deep link (Telegram WebApp or external browser)
```

Token refresh is handled transparently in `api/client.py`: on 401, call `POST /auth/refresh`, update Redis, retry once.

### 2.5 Command & Conversation Map

| Trigger | Description | Auth Required |
|---|---|---|
| `/start` | Greeting + login flow if not authenticated | No |
| `/profile` | Show profile summary (name, headline, top skills, job count) | Yes |
| `/import` | Guided file import (accepts PDF resume or LinkedIn ZIP) | Yes |
| `/storage` | List connected cloud accounts | Yes |
| `/encryption` | Show encryption status; prompt to init if not set | Yes |
| `/status` | Show pending/recent async jobs | Yes |
| `/logout` | Revoke refresh token, clear Redis session | Yes |
| `/help` | Command reference | No |
| *(any document)* | Auto-detect file type → route to resume or LinkedIn import | Yes |

### 2.6 Import Flow (Async Job Handling)

```
User sends PDF file
Bot: "📄 Resume detected. Uploading…"
     [POST /resume/upload → resume_id]
Bot: "Extracting text…"
     [POST /resume/{id}/extract → job_id]
Bot: "Parsing structured data…"
     [POST /resume/{id}/parse → job_id]
     — stores job_id in Redis with TTL 1h —
Bot: "⏳ Processing in background. I'll notify you when done."

[Background task polls job or receives webhook push]
Bot: "✅ Resume parsed! Use /profile to review, or head to the app to merge."
```

For LinkedIn: user sends a `.zip` file → `POST /linkedin/import` → `POST /linkedin/import/{id}/parse`.

File type is determined by MIME type + extension. Unknown types prompt an explanation.

### 2.7 Profile View (Read-Only in Bot)

The bot renders the profile as a formatted Telegram message — not inline-editable (to keep UX simple). Editing is delegated to the full app.

```
👤 Arman Avanesyan
💼 Senior Software Engineer at Acme Corp (2021–present)
🏢 Previous: 2 positions
🛠 Skills: Go, Python, Kubernetes, PostgreSQL (+8 more)
🔐 Encryption: ✅ Active

[Edit in App →]   [Import Resume →]
```

### 2.8 Key Design Decisions

- **No inline profile editing** — too error-prone in chat; users are redirected to the Flutter app.
- **Stateless bot processes** — all state in Redis; multiple bot replicas can run in parallel.
- **Transparent token refresh** — `api/client.py` wraps every call; the handler never sees 401.
- **Document handler catches all uploads** — auto-routes to correct import type; user doesn't need to run a command first.
- **Webhook-first** — polling only for local development (`BOT_POLLING=true`).

---

## 3. Flutter Client (Desktop · Web SPA/PWA · Mobile iOS/Android)

### 3.1 Rationale & Platform Matrix

Flutter is chosen as a single codebase targeting all five surface areas. The same business logic, state management, and API layer are shared; only layout, navigation paradigm, and platform-specific adapters differ.

| Platform | Navigation | File Picking | OAuth Redirect | Secure Storage |
|---|---|---|---|---|
| **Mobile iOS** | Bottom nav bar | `file_picker` | `flutter_web_auth_2` + custom URL scheme | `flutter_secure_storage` (Keychain) |
| **Mobile Android** | Bottom nav bar | `file_picker` | `flutter_web_auth_2` + custom URL scheme | `flutter_secure_storage` (Keystore) |
| **Web (SPA/PWA)** | Top nav / sidebar | Drag-and-drop + `file_picker` | Redirect + `/oauth/callback` route | `flutter_secure_storage` (localStorage fallback) |
| **Desktop macOS** | Sidebar + menu bar | Native file dialog | Loopback HTTP server on `localhost:PORT` | `flutter_secure_storage` (Keychain) |
| **Desktop Windows/Linux** | Sidebar | Native file dialog | Loopback HTTP server on `localhost:PORT` | `flutter_secure_storage` (Credential Manager / libsecret) |

### 3.2 Technology Stack

| Concern | Package | Notes |
|---|---|---|
| State management | **Riverpod 2** (code-gen) | Composable, testable, no BuildContext threading |
| HTTP client | **Dio** + interceptors | Token refresh interceptor; multipart for file upload |
| Routing | **go_router** | Declarative; deep-link aware; guards for auth state |
| OAuth / WebAuth | **flutter_web_auth_2** | Handles redirect on all platforms |
| Secure storage | **flutter_secure_storage** | Platform-native secret storage |
| File picking | **file_picker** | Cross-platform; filters by extension |
| Form validation | **reactive_forms** | Type-safe form state |
| Serialization | **freezed** + **json_serializable** | Immutable models with copy-with |
| Local DB / cache | **drift** (SQLite) | Offline profile cache; job queue |
| Notifications | **flutter_local_notifications** | Job completion alerts (mobile/desktop) |
| PWA | Flutter web build + manifest | Service worker via flutter build web |

### 3.3 Directory Structure

```
flutter_app/
├── lib/
│   ├── main.dart
│   ├── app.dart                         # MaterialApp.router + ProviderScope
│   │
│   ├── core/
│   │   ├── api/
│   │   │   ├── dio_client.dart          # Dio setup, base URL, interceptors
│   │   │   ├── auth_interceptor.dart    # Attach Bearer token; refresh on 401
│   │   │   └── api_error.dart          # Typed API error model
│   │   ├── auth/
│   │   │   ├── auth_provider.dart       # Riverpod: current auth state
│   │   │   └── token_storage.dart       # flutter_secure_storage wrapper
│   │   ├── router/
│   │   │   ├── app_router.dart          # go_router routes + auth guard
│   │   │   └── routes.dart             # Named route constants
│   │   └── theme/
│   │       ├── app_theme.dart
│   │       └── color_tokens.dart
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   └── auth_repository.dart
│   │   │   ├── domain/
│   │   │   │   └── auth_models.dart     # TokenPair, CurrentUser (freezed)
│   │   │   └── presentation/
│   │   │       ├── login_screen.dart    # Entry: choose auth method
│   │   │       ├── email_otp_screen.dart
│   │   │       └── oauth_screen.dart    # Google / Microsoft / LinkedIn
│   │   │
│   │   ├── profile/
│   │   │   ├── data/
│   │   │   │   └── profile_repository.dart
│   │   │   ├── domain/
│   │   │   │   └── profile_models.dart  # Profile, Basics, Experience, Skill
│   │   │   └── presentation/
│   │   │       ├── profile_screen.dart  # Master view (all sections)
│   │   │       ├── basics_form.dart     # Inline editing
│   │   │       ├── experience_list.dart
│   │   │       └── skills_editor.dart
│   │   │
│   │   ├── import/
│   │   │   ├── data/
│   │   │   │   ├── resume_repository.dart
│   │   │   │   └── linkedin_repository.dart
│   │   │   ├── domain/
│   │   │   │   └── import_job.dart      # ImportJob, JobStatus enum
│   │   │   └── presentation/
│   │   │       ├── import_center_screen.dart  # Tab: Resume | LinkedIn
│   │   │       ├── resume_import_card.dart     # Drop zone + job tracker
│   │   │       └── linkedin_import_card.dart
│   │   │
│   │   ├── cloud_storage/
│   │   │   ├── data/
│   │   │   │   └── storage_repository.dart
│   │   │   └── presentation/
│   │   │       └── storage_screen.dart  # List accounts; connect buttons
│   │   │
│   │   └── encryption/
│   │       ├── data/
│   │       │   └── encryption_repository.dart
│   │       └── presentation/
│   │           └── encryption_screen.dart
│   │
│   ├── shared/
│   │   ├── widgets/
│   │   │   ├── async_value_widget.dart  # Generic AsyncValue builder
│   │   │   ├── job_status_badge.dart    # pending / processing / done / error
│   │   │   ├── file_drop_zone.dart      # Drag-and-drop + tap-to-pick
│   │   │   └── section_card.dart
│   │   └── utils/
│   │       ├── file_type_detector.dart
│   │       └── date_formatter.dart
│   │
│   └── platform/
│       ├── oauth_handler_mobile.dart    # flutter_web_auth_2 deep-link
│       ├── oauth_handler_web.dart       # Redirect + query param parsing
│       └── oauth_handler_desktop.dart   # Loopback HTTP server
│
├── web/
│   ├── manifest.json                    # PWA manifest
│   └── index.html                       # Service worker registration
├── macos/   android/   ios/   windows/  linux/   # Platform runners
└── pubspec.yaml
```

### 3.4 Routing & Auth Guard

```
/                   → redirect to /profile (if auth) or /login
/login              → LoginScreen
/login/email        → EmailOtpScreen
/oauth/callback     → OAuthCallbackScreen  (Web only; captures code param)
/profile            → ProfileScreen        [AUTH REQUIRED]
/profile/edit       → ProfileEditScreen    [AUTH REQUIRED]
/import             → ImportCenterScreen   [AUTH REQUIRED]
/storage            → StorageScreen        [AUTH REQUIRED]
/encryption         → EncryptionScreen     [AUTH REQUIRED]
/settings           → SettingsScreen       [AUTH REQUIRED]
```

The `go_router` `redirect` callback reads from `authProvider`: if `unauthenticated` and route requires auth → `/login`.

### 3.5 Auth Flow

**Email OTP (all platforms)**
```
LoginScreen → "Continue with Email"
EmailOtpScreen (step 1): email field → POST /auth/email/signup
EmailOtpScreen (step 2): OTP field  → POST /auth/email/verify
→ store TokenPair in flutter_secure_storage
→ router redirects to /profile
```

**OAuth (Google / Microsoft / LinkedIn)**
```
LoginScreen → "Continue with Google"

Mobile/Desktop:
  flutter_web_auth_2.authenticate(
    url: "https://accounts.google.com/o/oauth2/...",
    callbackUrlScheme: "cppm"
  )
  → receives id_token/access_token in deep-link
  → POST /auth/google { id_token }

Web:
  redirect to Google auth URL with redirect_uri = /oauth/callback?provider=google
  OAuthCallbackScreen parses ?code=...
  → POST /auth/google { id_token }
```

Note: The CPPM backend accepts already-exchanged tokens, so the Flutter client handles the OAuth authorization code → token exchange with the provider directly (or delegates to the backend's own OAuth endpoints when those are added).

### 3.6 API Layer (`dio_client.dart` + `auth_interceptor.dart`)

```dart
// auth_interceptor.dart
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(options, handler) {
    final token = tokenStorage.accessToken;
    if (token != null) options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  }

  @override
  void onError(DioException err, handler) async {
    if (err.response?.statusCode == 401) {
      final refreshed = await authRepository.refresh();
      if (refreshed) {
        // retry original request with new token
        return handler.resolve(await _retry(err.requestOptions));
      }
      authNotifier.logout();
    }
    handler.next(err);
  }
}
```

All repository methods return typed models via `freezed`. Error handling uses a sealed `ApiResult<T>` type (success / apiError / networkError).

### 3.7 Async Job Polling

Resume and LinkedIn parse jobs are async. The client polls every 3 seconds (capped at 2 minutes) using a Riverpod `StreamProvider`:

```dart
// import_job_provider.dart
final jobStatusProvider = StreamProvider.family<JobStatus, String>((ref, jobId) async* {
  while (true) {
    final status = await importRepository.getJobStatus(jobId);
    yield status;
    if (status == JobStatus.done || status == JobStatus.error) break;
    await Future.delayed(const Duration(seconds: 3));
  }
});
```

On mobile, completed jobs also fire a local notification (flutter_local_notifications).

### 3.8 Layout Adaptation

**Mobile (≤600 dp):** Single-column. `BottomNavigationBar` with tabs: Profile · Import · Storage · Settings.

**Tablet / Web (600–1200 dp):** `NavigationRail` on the left (collapsed). Main content area fills remaining space. Profile sections shown in two-column grid.

**Desktop / Wide Web (>1200 dp):** Persistent `NavigationDrawer` (sidebar, 240 dp). Profile shows basics + experience in left pane, skills + encryption status in right pane. File import shows a large drag-and-drop zone.

The `LayoutBuilder` / `AdaptiveLayout` widget (or `flutter_adaptive_scaffold`) handles breakpoint switching. No per-platform `if (Platform.isAndroid)` in UI code — only in the `platform/` adapters.

### 3.9 Offline & PWA Strategy

**PWA (web build):**
- Service worker caches app shell (Flutter engine + assets) for offline launch.
- Profile data cached in `drift` SQLite (WASM backend for web) with a `staleWhileRevalidate` strategy.
- Import and storage actions require connectivity; shown with a graceful offline banner.

**Mobile/Desktop:**
- `drift` caches profile locally. Writes are queued and replayed when reconnected.
- JWT is stored in secure storage; the app can open and display cached profile fully offline.

### 3.10 Encryption UX

The encryption feature requires a user-set password to init. The Flutter client handles this with care:

- On first profile view, if `GET /encryption/status` returns `initialized: false`, a non-blocking banner prompts: *"Protect your data — set an encryption password."*
- The `EncryptionScreen` has two states: init form (password + confirm) and status view (initialized date + rotate button).
- The password is **never stored** on-device; it is sent to the server once per action (`POST /encryption/init`).
- Key rotation is a single-tap action with a confirmation dialog.

---

## 4. Cross-Cutting Concerns

### 4.1 Token Lifecycle (shared contract)

Both clients implement the same token lifecycle:

1. On login: store `access_token` + `refresh_token`.
2. Every API call: attach `access_token` in `Authorization` header.
3. On 401: call `POST /auth/refresh` with `refresh_token`.
4. On successful refresh: update stored tokens, retry original call.
5. On failed refresh (expired / revoked): clear storage, redirect to login.
6. On explicit logout: call `POST /auth/logout` with `refresh_token`, clear storage.

### 4.2 Error Handling Philosophy

- **4xx errors** → show user-facing message (toast / chat message).
- **5xx errors** → generic "something went wrong" with retry option.
- **Network errors** → "No connection" with offline indicator.
- **Job failures** → show error in job status badge; offer retry button.

### 4.3 File Type Routing

Both clients use the same logic for auto-detecting import type:

| Extension / MIME | Route to |
|---|---|
| `.pdf`, `application/pdf` | Resume import |
| `.docx`, `.doc` | Resume import |
| `.zip` containing LinkedIn CSVs | LinkedIn import |
| Other `.zip` | Prompt user to select type |
| Other | Error: unsupported format |

### 4.4 Security Notes

- JWT stored in platform-native secure storage on all clients (Keychain, Keystore, bot Redis with encryption-at-rest).
- The bot never logs message content containing OTP codes.
- CORS on the backend currently allows `*` — should be tightened to the Flutter web origin and bot server IP before production.
- Encryption password is never persisted client-side.

---

## 5. Development Roadmap

| Phase | Deliverable |
|---|---|
| **P0** | Flutter auth screens (email OTP + OAuth) + profile view |
| **P0** | Bot auth flow + `/profile` command |
| **P1** | Flutter import center (resume + LinkedIn) with job polling |
| **P1** | Bot file upload handler + async job notifications |
| **P1** | Flutter cloud storage connect/list screens |
| **P2** | Flutter profile edit forms (basics, experience, skills) |
| **P2** | Flutter encryption screen |
| **P2** | Bot `/encryption` and `/storage` commands |
| **P3** | PWA offline support + service worker |
| **P3** | Desktop-specific layout polish (sidebar, native menus) |
| **P3** | Push notifications for job completion (mobile) |
