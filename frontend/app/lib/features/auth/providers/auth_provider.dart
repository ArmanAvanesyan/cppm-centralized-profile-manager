import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Auth state. Replace with real session check (e.g. secure storage + backend).
/// Set to true after OTP verify or OAuth success.
final authStateProvider = StateProvider<bool>((ref) => false);

/// Notifier for auth actions: send OTP, verify OTP, OAuth, sign out.
class AuthNotifier extends StateNotifier<AsyncValue<void>> {
  AuthNotifier() : super(const AsyncValue.data(null));

  Future<void> sendOtp(String email) async {
    state = const AsyncValue.loading();
    await Future.delayed(const Duration(seconds: 1));
    state = const AsyncValue.data(null);
  }

  Future<bool> verifyOtp(String email, String code) async {
    state = const AsyncValue.loading();
    await Future.delayed(const Duration(milliseconds: 800));
    state = const AsyncValue.data(null);
    return code.length >= 4;
  }

  Future<void> signInWithGoogle() async {
    state = const AsyncValue.loading();
    await Future.delayed(const Duration(seconds: 1));
    state = const AsyncValue.data(null);
  }

  Future<void> signInWithMicrosoft() async {
    state = const AsyncValue.loading();
    await Future.delayed(const Duration(seconds: 1));
    state = const AsyncValue.data(null);
  }

  Future<void> signOut() async {
    state = const AsyncValue.loading();
    await Future.delayed(const Duration(milliseconds: 300));
    state = const AsyncValue.data(null);
  }
}

final authNotifierProvider = StateNotifierProvider<AuthNotifier, AsyncValue<void>>((ref) {
  return AuthNotifier();
});
