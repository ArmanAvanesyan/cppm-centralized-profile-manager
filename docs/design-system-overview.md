# Design System Overview

## Philosophy

The CPPM design system is a single Flutter package (`frontend/packages/design_system`) that provides:

- **Foundations** – Colors, typography, spacing, radius, elevation (tokens).
- **Primitives** – Buttons, inputs, cards, layout building blocks.
- **Patterns** – App shell, navigation bars, sidebars, dialogs.

All app UI is built by composing these components so that CPPM looks and behaves consistently across iOS, Android, Windows, and macOS.

## Package structure

```
packages/design_system/
  lib/
    theme/           # Tokens and AppTheme
    components/      # Buttons, inputs, layout, navigation, feedback
    design_system.dart  # Single entry point
```

## Theming approach

- **Light and dark** – `AppTheme.light` and `AppTheme.dark`; app uses `themeMode: ThemeMode.system` by default.
- **Semantic colors** – Primary, secondary, surface, error, success, warning, info so that components adapt to theme.
- **Typography** – Scale from display to label; all text styles use the same font family and scale.

## Usage in the app

```dart
import 'package:design_system/design_system.dart';
// Use AppTheme.light / AppTheme.dark in MaterialApp
// Use AppButton, AppTextField, AppCard, etc. in screens
```

See [design-tokens.md](design-tokens.md) and [design-components.md](design-components.md) for details.
