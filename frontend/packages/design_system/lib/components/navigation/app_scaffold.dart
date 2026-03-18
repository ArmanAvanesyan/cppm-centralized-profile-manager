import 'package:flutter/material.dart';

/// App shell with optional app bar, drawer/sidebar, bottom nav, and body.
class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    this.title,
    this.actions,
    this.body,
    this.drawer,
    this.bottomNavigationBar,
    this.floatingActionButton,
    this.showDrawerButton = false,
    this.onDrawerPressed,
  });

  final String? title;
  final List<Widget>? actions;
  final Widget? body;
  final Widget? drawer;
  final Widget? bottomNavigationBar;
  final Widget? floatingActionButton;
  final bool showDrawerButton;
  final VoidCallback? onDrawerPressed;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: title != null || actions != null
          ? AppBar(
              title: title != null ? Text(title!) : null,
              actions: actions,
              leading: showDrawerButton
                  ? IconButton(
                      icon: const Icon(Icons.menu),
                      onPressed: onDrawerPressed ?? () => Scaffold.of(context).openDrawer(),
                    )
                  : null,
            )
          : null,
      drawer: drawer,
      body: body ?? const SizedBox.shrink(),
      bottomNavigationBar: bottomNavigationBar,
      floatingActionButton: floatingActionButton,
    );
  }
}
