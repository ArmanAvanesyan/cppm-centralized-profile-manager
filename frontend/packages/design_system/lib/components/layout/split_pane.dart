import 'package:flutter/material.dart';

import '../../theme/app_spacing.dart';

/// Two-pane layout: list/detail or master/detail. Second pane hides on narrow width.
class AppSplitPane extends StatelessWidget {
  const AppSplitPane({
    super.key,
    required this.primary,
    required this.secondary,
    this.breakpoint = 900,
    this.primaryFlex = 1,
    this.secondaryFlex = 1,
  });

  final Widget primary;
  final Widget secondary;
  final double breakpoint;
  final int primaryFlex;
  final int secondaryFlex;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < breakpoint) {
          return primary;
        }
        return Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              flex: primaryFlex,
              child: primary,
            ),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              flex: secondaryFlex,
              child: secondary,
            ),
          ],
        );
      },
    );
  }
}
