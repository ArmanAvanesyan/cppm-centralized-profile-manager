# Design Components Catalog

Props and usage guidelines for reusable components in `design_system`.

## Buttons

### AppButton

- **Props**: `label`, `onPressed`, `variant` (primary | secondary | danger | ghost), `isLoading`, `icon`, `iconOnly`.
- **Usage**: Primary actions = primary; secondary actions = secondary or ghost; destructive = danger. Use `isLoading` during async submit.

## Inputs

### AppTextField

- **Props**: `controller`, `label`, `hint`, `helperText`, `errorText`, `prefixIcon`, `suffixIcon`, `obscureText`, `enabled`, `maxLines`/`minLines`, `keyboardType`, `validator`, etc.
- **Usage**: All form text inputs; set `errorText` for validation feedback.

## Layout

### AppCard

- **Props**: `child`, `padding`, `elevation`, `onTap`.
- **Usage**: Content grouping; use `onTap` for tappable cards.

### ResponsiveContainer

- **Props**: `child`, `maxWidth`, `padding`.
- **Usage**: Wrap page content to limit width and add horizontal padding; uses `Breakpoints` (600 / 900 / 1200).

### AppSplitPane

- **Props**: `primary`, `secondary`, `breakpoint`, `primaryFlex`, `secondaryFlex`.
- **Usage**: List + detail on desktop; below breakpoint only primary is shown.

## Navigation

### AppScaffold

- **Props**: `title`, `actions`, `body`, `drawer`, `bottomNavigationBar`, `floatingActionButton`, `showDrawerButton`, `onDrawerPressed`.
- **Usage**: Main app shell; combine with sidebar (drawer) on desktop and bottom nav on mobile.

### AppBottomNavBar / AppBottomNavItem

- **Usage**: Mobile bottom navigation; pass `items`, `currentIndex`, `onTap`.

### AppSidebar / AppSidebarItem

- **Usage**: Desktop sidebar; pass `items`, `onSelected`, optional `header`.

## Feedback

### AppDialog

- **Props**: `title`, `content`, `actions`, `barrierDismissible`.
- **Usage**: Modal dialogs; use `AppDialog.show(context, ...)` for one-off dialogs.
