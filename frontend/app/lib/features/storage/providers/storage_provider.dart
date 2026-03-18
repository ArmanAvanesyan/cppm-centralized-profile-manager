import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/storage_account.dart';

/// List of connected storage accounts. Replace with API-backed repository.
final storageAccountsProvider = StateProvider<List<StorageAccount>>((ref) => []);

/// Connect a provider (stub: simulates OAuth and folder creation).
Future<void> connectStorageProvider(
  Ref ref,
  StorageProvider provider,
) async {
  await Future.delayed(const Duration(seconds: 2));
  final name = switch (provider) {
    StorageProvider.googleDrive => 'Google Drive',
    StorageProvider.dropbox => 'Dropbox',
    StorageProvider.oneDrive => 'OneDrive',
  };
  ref.read(storageAccountsProvider.notifier).update((list) {
    if (list.any((a) => a.provider == provider)) return list;
    return [
      ...list,
      StorageAccount(
        provider: provider,
        displayName: name,
        lastSyncAt: DateTime.now(),
      ),
    ];
  });
}

/// Disconnect a provider.
void disconnectStorageProvider(Ref ref, StorageProvider provider) {
  ref.read(storageAccountsProvider.notifier).update((list) {
    return list.where((a) => a.provider != provider).toList();
  });
}
