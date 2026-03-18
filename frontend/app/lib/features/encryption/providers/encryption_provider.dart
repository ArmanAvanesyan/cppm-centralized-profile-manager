import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/encryption/encryption_helper.dart';

/// Whether encryption has been set up (passphrase chosen and confirmed).
final encryptionEnabledProvider = StateProvider<bool>((ref) => false);

/// Whether the app is currently locked (key not in memory).
final encryptionLockedProvider = StateProvider<bool>((ref) => false);

/// In-memory key (stub: never persist; clear on lock).
/// In production use a secure enclave or short-lived in-memory only.
final _encryptionKeyProvider = StateProvider<List<int>?>((ref) => null);

/// Setup encryption with passphrase. Call after user confirms passphrase and backup reminder.
void setEncryptionPassphrase(Ref ref, String passphrase) {
  final key = EncryptionHelper.deriveKey(passphrase);
  ref.read(_encryptionKeyProvider.notifier).state = key;
  ref.read(encryptionEnabledProvider.notifier).state = true;
  ref.read(encryptionLockedProvider.notifier).state = false;
}

/// Unlock with passphrase (key loaded into memory).
bool unlockWithPassphrase(Ref ref, String passphrase) {
  final key = EncryptionHelper.deriveKey(passphrase);
  ref.read(_encryptionKeyProvider.notifier).state = key;
  ref.read(encryptionLockedProvider.notifier).state = false;
  return true;
}

/// Lock: clear key from memory.
void lockEncryption(Ref ref) {
  ref.read(_encryptionKeyProvider.notifier).state = null;
  ref.read(encryptionLockedProvider.notifier).state = true;
}

/// Get current key (for encrypt/decrypt). Returns null if locked.
List<int>? getEncryptionKey(Ref ref) {
  return ref.read(_encryptionKeyProvider);
}
