import 'package:flutter/material.dart';

import '../../theme/app_spacing.dart';

/// Breakpoints for responsive layout (mobile, tablet, desktop).
class Breakpoints {
  const Breakpoints._();

  static const double mobile = 600;
  static const double tablet = 900;
  static const double desktop = 1200;
}

/// Wraps child with max width and horizontal padding based on breakpoints.
class ResponsiveContainer extends StatelessWidget {
  const ResponsiveContainer({
    super.key,
    required this.child,
    this.maxWidth,
    this.padding,
  });

  final Widget child;
  final double? maxWidth;
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final effectiveMaxWidth = maxWidth ?? Breakpoints.desktop;
        final effectivePadding = padding ??
            EdgeInsets.symmetric(
              horizontal: width < Breakpoints.mobile
                  ? AppSpacing.lg
                  : width < Breakpoints.tablet
                      ? AppSpacing.xl
                      : AppSpacing.xxl,
            );
        return Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: effectiveMaxWidth),
            child: Padding(
              padding: effectivePadding,
              child: child,
            ),
          ),
        );
      },
    );
  }
}
