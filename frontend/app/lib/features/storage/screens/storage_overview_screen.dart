import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/models/storage_account.dart';
import '../providers/storage_provider.dart';
import '../../../router/app_router.dart';

class StorageOverviewScreen extends ConsumerWidget {
  const StorageOverviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final accounts = ref.watch(storageAccountsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Cloud Storage'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go(RouteNames.home),
        ),
      ),
      body: ResponsiveContainer(
        child: ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            Text(
              'Connect storage to sync your profile (profile.json) across devices.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSpacing.xl),
            _ProviderCard(
              provider: StorageProvider.googleDrive,
              displayName: 'Google Drive',
              icon: Icons.drive_file_move,
              isConnected: accounts.any((a) => a.provider == StorageProvider.googleDrive),
              onConnect: () => _connect(context, ref, StorageProvider.googleDrive),
              onDisconnect: () => disconnectStorageProvider(ref, StorageProvider.googleDrive),
            ),
            const SizedBox(height: AppSpacing.md),
            _ProviderCard(
              provider: StorageProvider.dropbox,
              displayName: 'Dropbox',
              icon: Icons.folder,
              isConnected: accounts.any((a) => a.provider == StorageProvider.dropbox),
              onConnect: () => _connect(context, ref, StorageProvider.dropbox),
              onDisconnect: () => disconnectStorageProvider(ref, StorageProvider.dropbox),
            ),
            const SizedBox(height: AppSpacing.md),
            _ProviderCard(
              provider: StorageProvider.oneDrive,
              displayName: 'OneDrive',
              icon: Icons.cloud,
              isConnected: accounts.any((a) => a.provider == StorageProvider.oneDrive),
              onConnect: () => _connect(context, ref, StorageProvider.oneDrive),
              onDisconnect: () => disconnectStorageProvider(ref, StorageProvider.oneDrive),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _connect(BuildContext context, WidgetRef ref, StorageProvider provider) async {
    await connectStorageProvider(ref, provider);
    if (context.mounted) {}
  }
}

class _ProviderCard extends StatelessWidget {
  const _ProviderCard({
    required this.provider,
    required this.displayName,
    required this.icon,
    required this.isConnected,
    required this.onConnect,
    required this.onDisconnect,
  });

  final StorageProvider provider;
  final String displayName;
  final IconData icon;
  final bool isConnected;
  final VoidCallback onConnect;
  final VoidCallback onDisconnect;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AppCard(
      child: Row(
        children: [
          Icon(icon, size: 40, color: theme.colorScheme.primary),
          const SizedBox(width: AppSpacing.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(displayName, style: theme.textTheme.titleMedium),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  isConnected ? 'Connected – CPPM folder ready' : 'Not connected',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: isConnected
                        ? theme.colorScheme.primary
                        : theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          if (isConnected)
            TextButton(
              onPressed: onDisconnect,
              child: const Text('Disconnect'),
            )
          else
            AppButton(
              label: 'Connect',
              variant: AppButtonVariant.primary,
              onPressed: onConnect,
            ),
        ],
      ),
    );
  }
}
