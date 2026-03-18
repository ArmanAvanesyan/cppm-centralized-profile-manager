# Auth Flow

End-to-end authentication flows and error handling (including session management).

## Flows

1. **Splash** – Check auth state; redirect to welcome (unauthenticated) or home (authenticated).
2. **Welcome** – Choose sign-in method: Email (OTP) or Google/Microsoft OAuth.
3. **Email OTP** – Enter email → send OTP → enter OTP → success or error (rate limit, invalid code).
4. **OAuth** – Provider selection → open web view / SDK → callback → success or error.
5. **Session** – Store token/session; refresh on expiry; on expiry show re-auth or lock screen.

## Sequence

```
Splash (/) → [auth check] → Welcome (/welcome) or Home (/home)
Welcome → [Email] → /auth/email → [Send OTP] → /auth/otp?email=... → [Verify] → Home
Welcome → [Google/Microsoft] → [OAuth flow] → Home or /auth/error?message=...
Auth error → [Try again] → Welcome
Home → [Sign out] → Welcome
```

## Implementation (frontend)

- **Router**: go_router with routes: `/`, `/welcome`, `/auth/email`, `/auth/otp`, `/auth/error`, `/home`.
- **State**: `authStateProvider` (StateProvider<bool>) holds whether user is authenticated; set true after OTP verify or OAuth success, false on sign out. Replace with secure storage + backend session later.
- **Screens**: SplashScreen, WelcomeScreen, EmailAuthScreen, OtpScreen, AuthErrorScreen, HomeScreen. All use design system (AppButton, AppTextField, ResponsiveContainer).
- **AuthNotifier**: sendOtp, verifyOtp, signInWithGoogle, signInWithMicrosoft, signOut (stub implementations; wire to backend APIs when ready).

## Error handling

- **Invalid OTP** – Inline error on OTP screen; "Resend code" available.
- **Rate limit** – Backend returns error; frontend shows message (e.g. "Too many attempts; try again in X minutes.").
- **OAuth cancelled/failed** – Navigate to `/auth/error?message=...`; "Try again" returns to welcome.
- **Session expired** – (Future) Redirect to re-auth or "Session expired" screen when backend returns 401.

## Backend alignment

- Document backend auth endpoints (OTP send/verify, OAuth init/callback, token refresh) in backend-auth.md or here. Frontend consumes these for all auth steps.
