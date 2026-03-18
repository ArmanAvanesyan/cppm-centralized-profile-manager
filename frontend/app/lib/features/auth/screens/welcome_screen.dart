import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/auth_provider.dart';
import '../../../../router/app_router.dart';

class WelcomeScreen extends ConsumerWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    return Scaffold(
      body: ResponsiveContainer(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'CPPM',
                  style: theme.textTheme.displayMedium?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  'Centralized Professional Profile Manager',
                  style: theme.textTheme.bodyLarge?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: AppSpacing.xxl),
                AppButton(
                  label: 'Continue with Email',
                  variant: AppButtonVariant.primary,
                  onPressed: () => context.push(RouteNames.emailAuth),
                ),
                const SizedBox(height: AppSpacing.lg),
                AppButton(
                  label: 'Continue with Google',
                  variant: AppButtonVariant.secondary,
                  icon: const Icon(Icons.g_mobiledata, size: 24),
                  onPressed: () => _signInWithGoogle(context, ref),
                ),
                const SizedBox(height: AppSpacing.lg),
                AppButton(
                  label: 'Continue with Microsoft',
                  variant: AppButtonVariant.secondary,
                  icon: const Icon(Icons.windows, size: 24),
                  onPressed: () => _signInWithMicrosoft(context, ref),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _signInWithGoogle(BuildContext context, WidgetRef ref) async {
    await ref.read(authNotifierProvider.notifier).signInWithGoogle();
    if (context.mounted) {
      final err = ref.read(authNotifierProvider).error;
      if (err != null) {
        context.pushUri(Uri(path: RouteNames.authError, queryParameters: {'message': err.toString()}));
      } else {
        ref.read(authStateProvider.notifier).state = true;
        context.go(RouteNames.home);
      }
    }
  }

  Future<void> _signInWithMicrosoft(BuildContext context, WidgetRef ref) async {
    await ref.read(authNotifierProvider.notifier).signInWithMicrosoft();
    if (context.mounted) {
      final err = ref.read(authNotifierProvider).error;
      if (err != null) {
        context.pushUri(Uri(path: RouteNames.authError, queryParameters: {'message': err.toString()}));
      } else {
        ref.read(authStateProvider.notifier).state = true;
        context.go(RouteNames.home);
      }
    }
  }
}
