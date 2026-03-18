# Encryption Model

Client-side encryption model, UX, and integration points.

## Model

- **AES** (or agreed algorithm) for encrypting sensitive profile data (or selected fields) before sending to storage/backend.
- **Key handling**: User creates or provides passphrase; key derived for encryption. Key is not sent to backend; user must re-enter passphrase to unlock on new device or after lock.

## User journeys

1. **First-time setup** – Prompt to enable encryption → user sets passphrase → confirmation and backup reminder (e.g. "Save recovery key securely") → encryption enabled.
2. **Unlock** – On app open or when accessing encrypted data: show unlock screen (passphrase entry) → derive key → decrypt in memory → proceed.
3. **Lock** – After idle timeout or explicit "Lock" action; key cleared from memory; next access requires unlock.
4. **Key reset** – (If supported) Clear key and re-onboard; may require re-encryption or data migration.

## Integration

- Encryption layer sits between app and storage/API: data is encrypted before write and decrypted after read when encryption is enabled.
- Backend may store ciphertext only; decryption is client-only. Document any backend expectations (e.g. key ID or version) if applicable.

## Implementation (frontend)

- **Routes**: `/encryption/setup` (EncryptionSetupScreen), `/encryption/unlock` (EncryptionUnlockScreen).
- **State**: encryptionEnabledProvider, encryptionLockedProvider; setEncryptionPassphrase(), unlockWithPassphrase(), lockEncryption(). Key derived via EncryptionHelper.deriveKey(passphrase) and held in memory only (stub; replace with secure key storage / enclave as needed).
- **EncryptionHelper** (core/encryption/): deriveKey(), encrypt(), decrypt() – stub implementations; replace with real AES (e.g. package:encrypt or package:cryptography) and PBKDF2/Argon2 for key derivation.
- **Setup flow**: Passphrase + confirm, backup reminder card, "Enable encryption" → setEncryptionPassphrase() → go home.
- **Unlock flow**: Passphrase field, "Unlock" → unlockWithPassphrase() → go home. Shown when encryption is enabled and locked (e.g. on app launch or after lock).

## Security assumptions

- Passphrase/key never logged or sent over network.
- Lock policy (timeout, on background) documented and configurable where appropriate.
