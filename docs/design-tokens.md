# Design Tokens

Reference for colors, typography, spacing, radius, and elevation.

## Colors

- **Light**: Primary (blue), surface/background (white/off-white), onSurface/onBackground (dark). Semantic: error, success, warning, info.
- **Dark**: Inverted surfaces and appropriate contrast for primary and semantics.
- Exposed via `AppColors` and via `Theme.of(context).colorScheme` when using `AppTheme`.

## Typography

- **Scale**: displayLarge/Medium, headlineLarge/Medium/Small, titleLarge/Medium/Small, bodyLarge/Medium/Small, labelLarge/Medium/Small.
- **Font**: Roboto (default Material font).
- **Usage**: Prefer `Theme.of(context).textTheme` or `AppTextStyles.*` for one-off styles.

## Spacing

- **Scale**: xxs (2), xs (4), sm (8), md (12), lg (16), xl (24), xxl (32), xxxl (48) logical pixels.
- **Usage**: Padding, margins, gaps. Use `AppSpacing` constants.

## Radius

- **Scale**: xs (4), sm (8), md (12), lg (16), xl (24), full (9999).
- **Usage**: Borders, cards, buttons, dialogs. Use `AppRadius` values or getters (e.g. `AppRadius.radiusMd`).

## Elevation

- **Levels**: none (0), sm (1), md (2), lg (4), xl (8), xxl (12).
- **Usage**: Cards, app bar, dialogs. Use `AppElevation` constants.
