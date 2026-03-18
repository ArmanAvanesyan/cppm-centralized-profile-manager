# CPPM Product Epics

Detailed epic descriptions and acceptance criteria for the frontend scope.

---

## EPIC: Authentication

**Stories**

- Email signup/sign-in (always OTP, no password).
- Google OAuth sign-in.
- Microsoft OAuth sign-in.
- Session management (store, refresh, expiry, re-auth prompts).

**Acceptance criteria**

- User can sign in with email by receiving and entering OTP.
- User can sign in with Google and Microsoft OAuth.
- Session is persisted and refreshed; expired session shows re-auth flow.
- Clear error messages for invalid OTP, rate limits, and OAuth failures.

---

## EPIC: Cloud Storage

**Stories**

- Google Drive connect.
- Dropbox connect.
- OneDrive connect.
- CPPM folder creation per provider.
- `profile.json` management (read/write) within CPPM folder.

**Acceptance criteria**

- User can connect each provider via OAuth-like consent.
- App creates a dedicated CPPM folder when not present.
- User can view/sync profile from connected storage; changes are written back to `profile.json`.

---

## EPIC: Resume Import

**Stories**

- Upload PDF.
- Upload DOCX.
- Extract text, parse experience and skills.
- Map parsed data into profile and allow review/approve.

**Acceptance criteria**

- User can select PDF or DOCX (file picker / drag-drop on desktop).
- Backend extracts and parses; frontend shows progress and result.
- User can review detected experience/skills and merge or discard.

---

## EPIC: LinkedIn Import

**Stories**

- Upload LinkedIn PDF export.
- Parse experience and education.
- Merge with existing `profile.json`.

**Acceptance criteria**

- User can upload LinkedIn PDF and see parsing progress.
- Review screen shows existing vs imported experience/education; user can merge or skip.

---

## EPIC: Encryption

**Stories**

- AES encryption module; client-side encryption of sensitive data.
- Secure key handling (creation, backup reminder, re-entry, device handling).

**Acceptance criteria**

- User can set up encryption (passphrase/key); backup reminder is shown.
- Encrypted data is decrypted on unlock; lock/unlock flow is clear and secure.
