# CPPM Product Overview

## Vision

CPPM (Centralized Professional Profile Manager) is a multi-platform application that lets professionals maintain a single, authoritative profile and sync it across cloud storage and use cases (resumes, LinkedIn, applications).

## Target Users

- Professionals who maintain multiple profiles (LinkedIn, resume, portfolio).
- Users who want one source of truth for experience, skills, and education.
- People who store files in Google Drive, Dropbox, or OneDrive and want profile data alongside.

## Value Propositions

1. **Single profile** – One `profile.json` (or equivalent) as the canonical record.
2. **Cloud-native** – Connect Google Drive, Dropbox, OneDrive; CPPM creates a dedicated folder and manages the profile file there.
3. **Import from existing assets** – Upload PDF/DOCX resumes or LinkedIn PDF exports; parse and merge into the profile.
4. **Security** – Optional client-side encryption for sensitive data.
5. **Multi-platform** – Native iOS, Android, Windows, and macOS from one Flutter codebase.

## Product Boundaries

- **In scope**: Authentication (OTP + Google/Microsoft OAuth), cloud storage connections, resume/LinkedIn import, client-side encryption, profile viewing/editing.
- **Out of scope (for initial release)**: Real-time collaboration, public portfolio hosting, ATS-specific exports (beyond standard resume formats).
