import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/auth/screens/auth_error_screen.dart';
import '../features/auth/screens/email_auth_screen.dart';
import '../features/auth/screens/otp_screen.dart';
import '../features/auth/screens/welcome_screen.dart';
import '../features/home/home_screen.dart';
import '../features/encryption/screens/encryption_setup_screen.dart';
import '../features/encryption/screens/encryption_unlock_screen.dart';
import '../features/import/screens/import_wizard_screen.dart';
import '../features/storage/screens/storage_overview_screen.dart';
import 'splash_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

GoRouter createAppRouter() {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: RouteNames.splash,
    routes: [
      GoRoute(
        path: RouteNames.splash,
        name: 'splash',
        builder: (_, __) => const SplashScreen(),
      ),
      GoRoute(
        path: RouteNames.welcome,
        name: 'welcome',
        builder: (_, __) => const WelcomeScreen(),
      ),
      GoRoute(
        path: RouteNames.emailAuth,
        name: 'emailAuth',
        builder: (_, __) => const EmailAuthScreen(),
      ),
      GoRoute(
        path: RouteNames.otp,
        name: 'otp',
        builder: (_, state) {
          final email = state.uri.queryParameters['email'] ?? '';
          return OtpScreen(email: email);
        },
      ),
      GoRoute(
        path: RouteNames.authError,
        name: 'authError',
        builder: (_, state) {
          final message = state.uri.queryParameters['message'] ?? 'Something went wrong';
          return AuthErrorScreen(message: message);
        },
      ),
      GoRoute(
        path: RouteNames.home,
        name: 'home',
        builder: (_, __) => const HomeScreen(),
      ),
      GoRoute(
        path: RouteNames.storage,
        name: 'storage',
        builder: (_, __) => const StorageOverviewScreen(),
      ),
      GoRoute(
        path: RouteNames.import,
        name: 'import',
        builder: (_, __) => const ImportWizardScreen(),
      ),
      GoRoute(
        path: RouteNames.encryptionSetup,
        name: 'encryptionSetup',
        builder: (_, __) => const EncryptionSetupScreen(),
      ),
      GoRoute(
        path: RouteNames.encryptionUnlock,
        name: 'encryptionUnlock',
        builder: (_, __) => const EncryptionUnlockScreen(),
      ),
    ],
  );
}

abstract class RouteNames {
  static const String splash = '/';
  static const String welcome = '/welcome';
  static const String emailAuth = '/auth/email';
  static const String otp = '/auth/otp';
  static const String authError = '/auth/error';
  static const String home = '/home';
  static const String storage = '/storage';
  static const String import = '/import';
  static const String encryptionSetup = '/encryption/setup';
  static const String encryptionUnlock = '/encryption/unlock';
}

final appRouterProvider = Provider<GoRouter>((ref) => createAppRouter());
