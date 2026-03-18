# Cloud Storage Flows

Integration flows for Google Drive, Dropbox, and OneDrive.

## Overview

- User connects each provider via OAuth-like consent.
- App ensures a dedicated **CPPM folder** exists (create if not).
- Canonical **profile.json** is read/written within that folder; sync state is shown in UI.

## Flows

1. **Connect provider** – User taps "Connect Google Drive" (or Dropbox/OneDrive) → OAuth → backend creates/locates CPPM folder → frontend stores connection and shows success.
2. **Storage dashboard** – List connected providers, status (connected/disconnected/error), last sync time. Allow disconnect.
3. **Profile sync** – Read profile.json from selected/default storage; on save, write back. Show progress and errors.

## Implementation (frontend)

- **Route**: `/storage` – StorageOverviewScreen.
- **State**: `storageAccountsProvider` (StateProvider<List<StorageAccount>>). Each account has provider, displayName, lastSyncAt, error. Stub: connect/disconnect update local state; replace with backend APIs for OAuth init, folder creation, and profile.json read/write.
- **UI**: Provider cards (Google Drive, Dropbox, OneDrive) with icon, name, status text ("Connected – CPPM folder ready" / "Not connected"), Connect or Disconnect button. Use AppCard, AppButton, design system.
- **Connect flow**: On Connect, call backend (or stub delay); on success add to list; on failure show error. Loading overlay or button loading state during connect recommended.

## Error handling

- OAuth cancelled or failed → message and retry.
- Folder creation failure → clear error and retry.
- Read/write failure (e.g. network, permission) → show error and last known state.

## Backend alignment

- Backend (or BFF) handles OAuth with each provider and folder creation. Frontend calls APIs to connect, get status, and read/write profile.json.
