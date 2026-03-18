import 'package:flutter/material.dart';

/// Bottom navigation item for [AppBottomNavBar].
class AppBottomNavItem {
  const AppBottomNavItem({
    required this.icon,
    required this.label,
    this.selectedIcon,
  });

  final IconData icon;
  final String label;
  final IconData? selectedIcon;
}

/// Design system bottom navigation bar (e.g. for mobile).
class AppBottomNavBar extends StatelessWidget {
  const AppBottomNavBar({
    super.key,
    required this.items,
    required this.currentIndex,
    required this.onTap,
  });

  final List<AppBottomNavItem> items;
  final int currentIndex;
  final ValueChanged<int> onTap;

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: onTap,
      destinations: items
          .map(
            (item) => NavigationDestination(
              icon: Icon(item.selectedIcon ?? item.icon),
              selectedIcon: Icon(item.selectedIcon ?? item.icon),
              label: item.label,
            ),
          )
          .toList(),
    );
  }
}
