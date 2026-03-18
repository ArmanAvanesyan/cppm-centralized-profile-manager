import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../auth/providers/auth_provider.dart';
import '../../router/app_router.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return AppScaffold(
      title: 'CPPM',
      actions: [
        IconButton(
          icon: const Icon(Icons.logout),
          onPressed: () async {
            await ref.read(authNotifierProvider.notifier).signOut();
            if (context.mounted) {
              ref.read(authStateProvider.notifier).state = false;
              context.go(RouteNames.welcome);
            }
          },
        ),
      ],
      body: ResponsiveContainer(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('Home'),
              const SizedBox(height: 24),
              AppButton(
                label: 'Cloud Storage',
                variant: AppButtonVariant.primary,
                onPressed: () => context.push(RouteNames.storage),
              ),
              const SizedBox(height: 16),
              AppButton(
                label: 'Import Resume / LinkedIn',
                variant: AppButtonVariant.secondary,
                onPressed: () => context.push(RouteNames.import),
              ),
              const SizedBox(height: 16),
              AppButton(
                label: 'Encryption',
                variant: AppButtonVariant.ghost,
                onPressed: () => context.push(RouteNames.encryptionSetup),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
