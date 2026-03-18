import 'package:flutter/material.dart';

import '../../theme/app_elevation.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_spacing.dart';

/// Design system card with optional padding and elevation override.
class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.elevation,
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double? elevation;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final effectivePadding = padding ?? const EdgeInsets.all(AppSpacing.lg);
    final effectiveElevation = elevation ?? AppElevation.md;

    Widget content = Padding(
      padding: effectivePadding,
      child: child,
    );

    if (onTap != null) {
      content = InkWell(
        onTap: onTap,
        borderRadius: AppRadius.radiusMd,
        child: content,
      );
    }

    return Material(
      color: theme.cardTheme.color ?? theme.colorScheme.surface,
      elevation: effectiveElevation,
      shadowColor: theme.cardTheme.shadowColor,
      shape: RoundedRectangleBorder(
        borderRadius: AppRadius.radiusMd,
      ),
      child: content,
    );
  }
}
