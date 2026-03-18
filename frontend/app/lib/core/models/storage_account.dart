/// Cloud storage provider type.
enum StorageProvider {
  googleDrive,
  dropbox,
  oneDrive,
}

/// Connected storage account and status.
class StorageAccount {
  const StorageAccount({
    required this.provider,
    required this.displayName,
    this.lastSyncAt,
    this.error,
  });

  final StorageProvider provider;
  final String displayName;
  final DateTime? lastSyncAt;
  final String? error;

  bool get isConnected => error == null;
}
