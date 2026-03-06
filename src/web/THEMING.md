# Theming Guide

## Overview

This application uses a centralized design token system for easy theming and maintenance. All colors, shadows, and visual effects are defined in `app/globals.css` and cascade throughout the application.

## Quick Theme Change

Want to change the entire color scheme? Just update the CSS variables in `app/globals.css`:

```css
:root {
  /* Change these values to customize your theme */
  --neon-green: #00ff41; /* Main accent color */
  --neon-pink: #ff006e; /* Secondary accent */
  --neon-yellow: #ffaa00; /* Tertiary accent */
  --neon-cyan: #00ffff; /* Quaternary accent */

  --purple-dark: #1a0033; /* Gradient start */
  --purple-mid: #2d1b4e; /* User message background */

  --gray-dark: #1a1a1a; /* Agent message background */
  --gray-mid: #2a2a2a; /* Code background */
}
```

## Design Token Structure

### Color Variables

- **Hex values**: `--neon-green: #00ff41`
- **RGB values**: `--neon-green-rgb: 0, 255, 65` (for rgba usage in shadows/glows)

### Semantic Classes

Components use semantic CSS classes that automatically apply the correct colors:

- `.chat-header` - Header bar styling
- `.chat-title` - Main title color
- `.chat-subtitle` - Subtitle color
- `.message-bubble-user` - User message styling
- `.message-bubble-agent` - Agent message styling
- `.agent-name` - Agent name label
- `.send-button` - Send button styling
- `.clear-button` - Clear button styling

### Neon Effects

Pre-built glow and shadow effects:

- `.neon-glow-green` - Green text glow
- `.neon-glow-pink` - Pink text glow
- `.neon-glow-yellow` - Yellow text glow
- `.neon-shadow-green` - Green box shadow
- `.neon-shadow-pink` - Pink box shadow
- `.neon-shadow-cyan` - Cyan box shadow
- `.neon-shadow-yellow` - Yellow box shadow

## Example Theme Variations

### Ocean Blue Theme

```css
--neon-green: #00ffff; /* Cyan */
--neon-pink: #0066ff; /* Blue */
--neon-yellow: #00ccff; /* Light blue */
--neon-cyan: #ffffff; /* White */
--purple-dark: #001a33; /* Deep blue */
--purple-mid: #003366; /* Mid blue */
```

### Sunset Theme

```css
--neon-green: #ff6b00; /* Orange */
--neon-pink: #ff006b; /* Hot pink */
--neon-yellow: #ffcc00; /* Gold */
--neon-cyan: #ff00ff; /* Magenta */
--purple-dark: #330011; /* Deep red */
--purple-mid: #660033; /* Purple-red */
```

### Matrix Theme

```css
--neon-green: #00ff00; /* Bright green */
--neon-pink: #00ff00; /* Also green */
--neon-yellow: #00cc00; /* Dark green */
--neon-cyan: #00ff00; /* Green again */
--purple-dark: #000500; /* Almost black */
--purple-mid: #001a00; /* Very dark green */
```

## Benefits

✅ **Single source of truth** - All colors defined in one place
✅ **No hardcoded values** - Components use semantic classes
✅ **Easy experimentation** - Change theme in seconds
✅ **Maintainable** - Clear structure and documentation
✅ **Consistent** - Automatic cascade to all components
✅ **Type-safe** - CSS variables prevent typos

## Component Structure

Each component now uses semantic classes instead of inline styles:

**Before:**

```tsx
<div style={{ boxShadow: "0 0 15px rgba(255, 0, 110, 0.5)" }}>
```

**After:**

```tsx
<div className="neon-shadow-pink">
```

This makes components cleaner, more readable, and easier to maintain!
