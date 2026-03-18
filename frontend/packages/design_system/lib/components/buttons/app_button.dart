import 'package:flutter/material.dart';

import '../../theme/app_radius.dart';
import '../../theme/app_spacing.dart';

/// CPPM button variants: primary, secondary, danger, ghost, icon-only.
enum AppButtonVariant {
  primary,
  secondary,
  danger,
  ghost,
}

/// Design system button with loading and disabled states.
class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.isLoading = false,
    this.icon,
    this.iconOnly = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final bool isLoading;
  final Widget? icon;
  final bool iconOnly;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final effectiveOnPressed = isLoading ? null : onPressed;

    if (iconOnly && icon != null) {
      return _buildIconButton(context, theme, effectiveOnPressed);
    }

    switch (variant) {
      case AppButtonVariant.primary:
        return ElevatedButton(
          onPressed: effectiveOnPressed,
          child: _buildChild(context),
        );
      case AppButtonVariant.secondary:
        return OutlinedButton(
          onPressed: effectiveOnPressed,
          child: _buildChild(context),
        );
      case AppButtonVariant.danger:
        return ElevatedButton(
          onPressed: effectiveOnPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.error,
            foregroundColor: theme.colorScheme.onError,
          ),
          child: _buildChild(context),
        );
      case AppButtonVariant.ghost:
        return TextButton(
          onPressed: effectiveOnPressed,
          child: _buildChild(context),
        );
    }
  }

  Widget _buildChild(BuildContext context) {
    if (isLoading) {
      return SizedBox(
        height: 20,
        width: 20,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: variant == AppButtonVariant.primary ||
                  variant == AppButtonVariant.danger
              ? null
              : Theme.of(context).colorScheme.primary,
        ),
      );
    }
    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          icon!,
          const SizedBox(width: AppSpacing.sm),
          Text(label),
        ],
      );
    }
    return Text(label);
  }

  Widget _buildIconButton(
    BuildContext context,
    ThemeData theme,
    VoidCallback? effectiveOnPressed,
  ) {
    return IconButton(
      onPressed: effectiveOnPressed,
      icon: isLoading
          ? SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : icon!,
      style: variant == AppButtonVariant.primary
          ? IconButton.styleFrom(
              backgroundColor: theme.colorScheme.primary,
              foregroundColor: theme.colorScheme.onPrimary,
            )
          : null,
    );
  }
}
