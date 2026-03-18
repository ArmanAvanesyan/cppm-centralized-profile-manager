import 'package:flutter/material.dart';

import '../../theme/app_spacing.dart';

/// Sidebar navigation item.
class AppSidebarItem {
  const AppSidebarItem({
    required this.icon,
    required this.label,
    this.selected = false,
  });

  final IconData icon;
  final String label;
  final bool selected;
}

/// Design system sidebar (e.g. for desktop). Use inside a Drawer or as a persistent rail.
class AppSidebar extends StatelessWidget {
  const AppSidebar({
    super.key,
    required this.items,
    this.onSelected,
    this.header,
  });

  final List<AppSidebarItem> items;
  final ValueChanged<int>? onSelected;
  final Widget? header;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (header != null) ...[
          Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: header,
          ),
          const Divider(height: 1),
        ],
        ...List.generate(items.length, (i) {
          final item = items[i];
          return ListTile(
            leading: Icon(
              item.icon,
              color: item.selected
                  ? theme.colorScheme.primary
                  : theme.colorScheme.onSurfaceVariant,
            ),
            title: Text(
              item.label,
              style: TextStyle(
                fontWeight: item.selected ? FontWeight.w600 : FontWeight.normal,
                color: item.selected
                    ? theme.colorScheme.primary
                    : theme.colorScheme.onSurface,
              ),
            ),
            selected: item.selected,
            onTap: () => onSelected?.call(i),
          );
        }),
      ],
    );
  }
}
