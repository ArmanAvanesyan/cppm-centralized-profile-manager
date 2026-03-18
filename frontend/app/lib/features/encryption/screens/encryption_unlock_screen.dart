import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/encryption_provider.dart';
import '../../../router/app_router.dart';

class EncryptionUnlockScreen extends ConsumerStatefulWidget {
  const EncryptionUnlockScreen({super.key});

  @override
  ConsumerState<EncryptionUnlockScreen> createState() => _EncryptionUnlockScreenState();
}

class _EncryptionUnlockScreenState extends ConsumerState<EncryptionUnlockScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passphraseController = TextEditingController();
  String? _errorText;
  bool _obscure = true;

  @override
  void dispose() {
    _passphraseController.dispose();
    super.dispose();
  }

  void _unlock() {
    _errorText = null;
    if (!_formKey.currentState!.validate()) return;
    final ok = unlockWithPassphrase(ref, _passphraseController.text);
    if (ok && mounted) {
      context.go(RouteNames.home);
    } else {
      setState(() => _errorText = 'Incorrect passphrase');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ResponsiveContainer(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Icon(
                    Icons.lock_outline,
                    size: 64,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  Text(
                    'Enter passphrase to unlock',
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  AppTextField(
                    controller: _passphraseController,
                    label: 'Passphrase',
                    obscureText: _obscure,
                    errorText: _errorText,
                    validator: (v) => v == null || v.isEmpty ? 'Enter passphrase' : null,
                    suffixIcon: IconButton(
                      icon: Icon(_obscure ? Icons.visibility : Icons.visibility_off),
                      onPressed: () => setState(() => _obscure = !_obscure),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xl),
                  AppButton(
                    label: 'Unlock',
                    variant: AppButtonVariant.primary,
                    onPressed: _unlock,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
