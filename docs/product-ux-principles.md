# CPPM UX Principles

## Design guidelines

1. **Clarity** – Primary actions are obvious; destructive actions require confirmation.
2. **Consistency** – Use the design system everywhere; same patterns for auth, storage, and import flows.
3. **Feedback** – Loading states, success/error toasts, and inline validation for forms.
4. **Accessibility** – Sufficient contrast, focus order, and screen-reader-friendly semantics (to be refined in Phase 7).

## Multi-platform behavior

- **Mobile**: Single-column layouts, bottom navigation, full-screen flows.
- **Desktop**: Sidebar navigation, split-pane list/detail, keyboard shortcuts where useful.
- **Responsive**: Breakpoints (e.g. 600 / 900 / 1200) drive layout changes; touch and pointer both supported.

## Security and trust

- Encryption setup and unlock flows must be clear and non-intrusive.
- Storage connection status and last sync time visible so users understand data location.
