# CPPM Design System

Shared Flutter package for CPPM: theme tokens and reusable UI components.

## Usage

```dart
import 'package:design_system/design_system.dart';
```

## Theme & tokens

- **AppTheme** – `AppTheme.light`, `AppTheme.dark` for `MaterialApp.theme` / `darkTheme`.
- **AppColors** – semantic colors (primary, surface, error, success, warning, info).
- **AppSpacing** – spacing scale (xxs, xs, sm, md, lg, xl, xxl, xxxl).
- **AppRadius** – border radius (xs–xl, full) and `BorderRadius` getters.
- **AppElevation** – elevation levels (none, sm, md, lg, xl, xxl).
- **AppTextStyles** – typography (display, headline, title, body, label).

## Components

### Buttons

- **AppButton** – variants: primary, secondary, danger, ghost; supports loading, icon, icon-only.
- **AppButtonVariant** – enum for variant.

### Inputs

- **AppTextField** – text field with label, hint, helper/error text, prefix/suffix icons.

### Layout

- **AppCard** – card with optional padding, elevation, onTap.
- **ResponsiveContainer** – max-width + horizontal padding from breakpoints (mobile 600, tablet 900, desktop 1200).
- **Breakpoints** – mobile, tablet, desktop constants.
- **AppSplitPane** – two-pane layout; secondary hides below breakpoint.

### Navigation

- **AppScaffold** – app bar, drawer, body, bottom nav, FAB.
- **AppBottomNavBar** / **AppBottomNavItem** – bottom navigation.
- **AppSidebar** / **AppSidebarItem** – sidebar list for desktop.

### Feedback

- **AppDialog** – dialog with title, content, actions; `AppDialog.show()`.

## Dependencies

- Flutter SDK only.
