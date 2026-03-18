import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/auth_provider.dart';
import '../../../../router/app_router.dart';

class OtpScreen extends ConsumerStatefulWidget {
  const OtpScreen({super.key, required this.email});

  final String email;

  @override
  ConsumerState<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends ConsumerState<OtpScreen> {
  final _formKey = GlobalKey<FormState>();
  final _codeController = TextEditingController();
  String? _errorText;

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _verify() async {
    _errorText = null;
    if (!_formKey.currentState!.validate()) return;
    final code = _codeController.text.trim();
    final ok = await ref.read(authNotifierProvider.notifier).verifyOtp(widget.email, code);
    if (!mounted) return;
    if (ok) {
      ref.read(authStateProvider.notifier).state = true;
      context.go(RouteNames.home);
    } else {
      setState(() => _errorText = 'Invalid or expired code. Try again or request a new code.');
    }
  }

  Future<void> _resend() async {
    _errorText = null;
    await ref.read(authNotifierProvider.notifier).sendOtp(widget.email);
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final loading = ref.watch(authNotifierProvider).isLoading;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Enter code'),
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
                  'We sent a code to ${widget.email}',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: AppSpacing.xl),
                AppTextField(
                  controller: _codeController,
                  label: 'Verification code',
                  hint: '000000',
                  keyboardType: TextInputType.number,
                  errorText: _errorText,
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Enter the code';
                    return null;
                  },
                ),
                const SizedBox(height: AppSpacing.xl),
                AppButton(
                  label: 'Verify',
                  variant: AppButtonVariant.primary,
                  isLoading: loading,
                  onPressed: _verify,
                ),
                const SizedBox(height: AppSpacing.md),
                TextButton(
                  onPressed: loading ? null : _resend,
                  child: const Text('Resend code'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
