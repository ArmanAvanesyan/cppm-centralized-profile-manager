import 'package:design_system/design_system.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../providers/auth_provider.dart';
import '../../../../router/app_router.dart';

class EmailAuthScreen extends ConsumerStatefulWidget {
  const EmailAuthScreen({super.key});

  @override
  ConsumerState<EmailAuthScreen> createState() => _EmailAuthScreenState();
}

class _EmailAuthScreenState extends ConsumerState<EmailAuthScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  String? _errorText;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    _errorText = null;
    if (!_formKey.currentState!.validate()) return;
    final email = _emailController.text.trim();
    await ref.read(authNotifierProvider.notifier).sendOtp(email);
    if (!mounted) return;
    final err = ref.read(authNotifierProvider).error;
    if (err != null) {
      setState(() => _errorText = err.toString());
      return;
    }
    context.push('${RouteNames.otp}?email=${Uri.encodeComponent(email)}');
  }

  @override
  Widget build(BuildContext context) {
    final loading = ref.watch(authNotifierProvider).isLoading;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sign in with Email'),
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
                AppTextField(
                  controller: _emailController,
                  label: 'Email',
                  hint: 'you@example.com',
                  keyboardType: TextInputType.emailAddress,
                  errorText: _errorText,
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Enter your email';
                    if (!v.contains('@')) return 'Enter a valid email';
                    return null;
                  },
                ),
                const SizedBox(height: AppSpacing.xl),
                AppButton(
                  label: 'Send verification code',
                  variant: AppButtonVariant.primary,
                  isLoading: loading,
                  onPressed: _sendOtp,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
