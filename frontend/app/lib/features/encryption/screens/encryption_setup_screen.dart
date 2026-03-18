import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/encryption_provider.dart';
import '../../../router/app_router.dart';

class EncryptionSetupScreen extends ConsumerStatefulWidget {
  const EncryptionSetupScreen({super.key});

  @override
  ConsumerState<EncryptionSetupScreen> createState() => _EncryptionSetupScreenState();
}

class _EncryptionSetupScreenState extends ConsumerState<EncryptionSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passphraseController = TextEditingController();
  final _confirmController = TextEditingController();
  String? _errorText;
  bool _obscurePassphrase = true;
  bool _obscureConfirm = true;

  @override
  void dispose() {
    _passphraseController.dispose();
    _confirmController.dispose();
    super.dispose();
  }

  void _submit() {
    _errorText = null;
    if (!_formKey.currentState!.validate()) return;
    final pass = _passphraseController.text;
    final confirm = _confirmController.text;
    if (pass != confirm) {
      setState(() => _errorText = 'Passphrases do not match');
      return;
    }
    if (pass.length < 8) {
      setState(() => _errorText = 'Use at least 8 characters');
      return;
    }
    setEncryptionPassphrase(ref, pass);
    if (mounted) context.go(RouteNames.home);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Enable encryption'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: ResponsiveContainer(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.xl),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Your profile data will be encrypted on this device. You will need this passphrase to unlock it.',
                  style: theme.textTheme.bodyLarge,
                ),
                const SizedBox(height: AppSpacing.xxl),
                AppTextField(
                  controller: _passphraseController,
                  label: 'Passphrase',
                  hint: 'Enter a strong passphrase',
                  obscureText: _obscurePassphrase,
                  errorText: _errorText,
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Enter a passphrase';
                    if (v.length < 8) return 'At least 8 characters';
                    return null;
                  },
                  suffixIcon: IconButton(
                    icon: Icon(_obscurePassphrase ? Icons.visibility : Icons.visibility_off),
                    onPressed: () => setState(() => _obscurePassphrase = !_obscurePassphrase),
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                AppTextField(
                  controller: _confirmController,
                  label: 'Confirm passphrase',
                  hint: 'Re-enter passphrase',
                  obscureText: _obscureConfirm,
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Confirm your passphrase';
                    return null;
                  },
                  suffixIcon: IconButton(
                    icon: Icon(_obscureConfirm ? Icons.visibility : Icons.visibility_off),
                    onPressed: () => setState(() => _obscureConfirm = !_obscureConfirm),
                  ),
                ),
                const SizedBox(height: AppSpacing.xl),
                Card(
                  color: theme.colorScheme.primaryContainer.withOpacity(0.3),
                  child: const Padding(
                    padding: EdgeInsets.all(AppSpacing.lg),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline),
                        SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Save your passphrase securely. If you lose it, encrypted data cannot be recovered.',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.xxl),
                AppButton(
                  label: 'Enable encryption',
                  variant: AppButtonVariant.primary,
                  onPressed: _submit,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
