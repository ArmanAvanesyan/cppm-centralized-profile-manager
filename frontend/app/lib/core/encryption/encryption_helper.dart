/// Client-side encryption abstraction.
/// Replace with real AES (e.g. package:encrypt or package:cryptography) and secure key derivation.
class EncryptionHelper {
  /// Derive key from passphrase (stub: in production use PBKDF2 or Argon2).
  static List<int> deriveKey(String passphrase) {
    return passphrase.codeUnits;
  }

  /// Encrypt plaintext with key (stub: in production use AES-GCM or AES-CBC).
  static List<int> encrypt(List<int> plaintext, List<int> key) {
    if (key.isEmpty) return plaintext;
    return List<int>.from(plaintext, growable: false);
  }

  /// Decrypt ciphertext with key (stub: in production use AES-GCM or AES-CBC).
  static List<int> decrypt(List<int> ciphertext, List<int> key) {
    if (key.isEmpty) return ciphertext;
    return List<int>.from(ciphertext, growable: false);
  }
}
