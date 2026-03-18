# Implementation Roadmap

Phased development plan and milestones for CPPM frontend.

## Epic-to-Phase Mapping

| Epic | Phase | Deliverables |
|------|-------|--------------|
| Authentication | 3 | Splash, welcome, email/OTP, OAuth stubs, session state, auth-flow.md |
| Cloud Storage | 4 | Storage overview, connect/disconnect UI, cloud-storage-flows.md |
| Resume Import | 5 | Import wizard, resume + LinkedIn flows, review/merge, import-flows.md |
| LinkedIn Import | 5 | Same wizard, LinkedIn source and parsing path |
| Encryption | 6 | Setup/unlock screens, EncryptionHelper, encryption-model.md |

## Phase 0 – Repo & Tooling

- [x] Flutter workspace: `frontend/app`, `frontend/packages/design_system`.
- [x] Multi-platform targets (iOS, Android, Windows, macOS) – structure in place; run `flutter create` in app if needed.
- [x] State management: Riverpod. Routing: go_router.
- [x] Docs skeleton under `/docs`.

## Phase 1 – Design System Foundations

- [x] Theme and tokens (colors, typography, spacing, radius, elevation).
- [x] First wave of components (buttons, inputs, cards, layout, navigation, dialog).

## Phase 2 – App Shell & Navigation

- [x] go_router routes for Auth, Storage, Import, Encryption, Home.
- [x] Responsive layout via design system (ResponsiveContainer, breakpoints).
- [ ] App scaffolding with drawer/sidebar and bottom nav (optional polish).

## Phase 3 – Authentication Epic

- [x] All auth screens (splash, welcome, email, OTP, OAuth buttons, error).
- [x] Auth state (Riverpod: authStateProvider, AuthNotifier).
- [x] auth-flow.md updated with sequences and errors.

## Phase 4 – Cloud Storage Epic

- [x] Storage overview screen and provider cards (Google Drive, Dropbox, OneDrive).
- [x] Connect/disconnect flows (stub state).
- [ ] Backend APIs for folder and profile.json (integration pending).
- [x] cloud-storage-flows.md updated.

## Phase 5 – Resume & LinkedIn Import

- [x] Shared import wizard (4 steps: source, file, parsing, review).
- [x] Resume and LinkedIn upload + review/merge UI.
- [x] import-flows.md updated.
- [ ] Backend parse API integration (stub in place).

## Phase 6 – Encryption Epic

- [x] Encryption setup and unlock screens.
- [x] EncryptionHelper abstraction and encryption-model.md.
- [ ] Real AES + key derivation (stub in place).

## Phase 7 – Polish & Accessibility

- [ ] Keyboard navigation, focus, screen readers.
- [ ] Layout tweaks for tablet and large desktop.
- [ ] Final docs and UX notes.
