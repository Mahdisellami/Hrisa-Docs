# GUI Parameterization System - Implementation Guide

## Overview

A comprehensive theme and accessibility system has been implemented to allow users to customize the application's appearance and adapt it to their needs. The system includes:

1. **Theme Management** - Switch between Dark and Light themes
2. **Size Profiles** - Three size presets (Small, Medium, Large) for accessibility
3. **Dynamic Styles** - All UI components automatically adapt to user preferences
4. **Appearance Settings Dialog** - User-friendly interface for configuration

---

## Architecture

### Core Components

#### 1. Theme Manager (`src/docprocessor/gui/theme_manager.py`)

Manages theme switching with two color palettes:

- **ColorsDark**: Dark theme optimized for low-light environments
- **ColorsLight**: Light theme with high contrast for well-lit environments

```python
from docprocessor.gui.theme_manager import get_theme_manager, ThemeType

# Get theme manager
theme_manager = get_theme_manager()

# Switch theme
theme_manager.set_theme(ThemeType.DARK)  # or ThemeType.LIGHT

# Get current colors
colors = theme_manager.get_colors()
print(colors.PRIMARY)  # Returns current theme's primary color
```

#### 2. Size Profile Manager (`src/docprocessor/gui/size_profile.py`)

Manages size presets for fonts, buttons, and spacing:

- **SMALL**: Compact interface (11px base font, 32px buttons)
- **MEDIUM**: Balanced interface (13px base font, 38px buttons) - Default
- **LARGE**: Accessible interface (16px base font, 48px buttons)

```python
from docprocessor.gui.size_profile import get_size_profile_manager, SizeProfileType

# Get size profile manager
size_manager = get_size_profile_manager()

# Switch size profile
size_manager.set_profile(SizeProfileType.MEDIUM)

# Get current profile
profile = size_manager.get_current_profile()
print(profile.font_size_base)  # Returns current base font size
```

#### 3. Dynamic Styles (`src/docprocessor/gui/styles_dynamic.py`)

Provides dynamic style generation that adapts to theme and size profile:

```python
from docprocessor.gui.styles_dynamic import Styles, Colors

# Use dynamic styles (automatically adapts to current theme/size)
button.setStyleSheet(Styles.BUTTON_PRIMARY)
label.setStyleSheet(Styles.LABEL_HEADER)

# Access dynamic colors
status_label.setStyleSheet(f"color: {Colors.SUCCESS};")
```

**Key Feature**: All `Styles` properties are generated dynamically, so changing theme or size profile automatically updates all components on next access.

#### 4. Appearance Settings Dialog (`src/docprocessor/gui/dialogs/appearance_settings_dialog.py`)

User-friendly dialog for changing appearance settings with live preview descriptions.

---

## Integration Steps

### Step 1: Update Imports in Existing Files

**Current (static styles):**
```python
from docprocessor.gui.styles import Styles, Colors
```

**New (dynamic styles):**
```python
# Option A: Replace import (recommended)
from docprocessor.gui.styles_dynamic import Styles, Colors

# Option B: Keep both during transition
from docprocessor.gui import styles  # Old static
from docprocessor.gui import styles_dynamic  # New dynamic
```

### Step 2: Add Appearance Settings Menu Item

In `main_window.py`, add menu item to open appearance settings:

```python
def create_menu_bar(self):
    # ... existing menu code ...

    # Settings menu
    settings_menu = menubar.addMenu(self.lang_manager.get('menu_settings', 'Settings'))

    appearance_action = QAction("🎨 " + self.lang_manager.get('menu_appearance'), self)
    appearance_action.triggered.connect(self.show_appearance_settings)
    settings_menu.addAction(appearance_action)

def show_appearance_settings(self):
    """Show appearance settings dialog."""
    from docprocessor.gui.dialogs.appearance_settings_dialog import AppearanceSettingsDialog

    dialog = AppearanceSettingsDialog(self)
    dialog.settings_applied.connect(self.on_appearance_changed)
    dialog.exec()

def on_appearance_changed(self):
    """Handle appearance settings change."""
    # Option 1: Full app restart (cleanest)
    QMessageBox.information(
        self,
        "Settings Applied",
        "Please restart the application for all changes to take effect."
    )

    # Option 2: Dynamic reload (more complex)
    # self.refresh_all_widgets()
```

### Step 3: Apply Dark Theme to QApplication (Optional)

For a cohesive dark theme, apply palette to entire application:

```python
# In main.py or main_window initialization
from docprocessor.gui.styles import apply_dark_theme_to_app

app = QApplication(sys.argv)
apply_dark_theme_to_app(app)  # Global dark theme
```

---

## Usage Examples

### Example 1: Theme-Aware Widget

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from docprocessor.gui.styles_dynamic import Styles, Colors

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Header with dynamic style
        header = QLabel("My Widget")
        header.setStyleSheet(Styles.LABEL_HEADER)
        layout.addWidget(header)

        # Button with dynamic style
        button = QPushButton("Click Me")
        button.setStyleSheet(Styles.BUTTON_PRIMARY)
        layout.addWidget(button)

        # Status label with dynamic color
        status = QLabel("Ready")
        status.setStyleSheet(f"color: {Colors.SUCCESS};")
        layout.addWidget(status)
```

### Example 2: Responding to Theme Changes

```python
from docprocessor.gui.theme_manager import get_theme_manager

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

        # Register for theme change notifications
        theme_manager = get_theme_manager()
        theme_manager.register_observer(self.on_theme_changed)

    def on_theme_changed(self, new_theme):
        """Refresh widget when theme changes."""
        # Re-apply all styles
        self.header.setStyleSheet(Styles.LABEL_HEADER)
        self.button.setStyleSheet(Styles.BUTTON_PRIMARY)
        # ... etc

    def closeEvent(self, event):
        """Cleanup on widget close."""
        theme_manager = get_theme_manager()
        theme_manager.unregister_observer(self.on_theme_changed)
        super().closeEvent(event)
```

### Example 3: Size-Aware Layout

```python
from docprocessor.gui.size_profile import get_size_profile_manager

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Get current size profile
        profile = get_size_profile_manager().get_current_profile()

        # Use profile for layout spacing
        layout = QVBoxLayout(self)
        layout.setSpacing(profile.spacing_medium)
        layout.setContentsMargins(
            profile.spacing_large,
            profile.spacing_large,
            profile.spacing_large,
            profile.spacing_large
        )
```

---

## Color Palettes

### Dark Theme (ColorsDark)
```python
BG_DARK = "#1e1e1e"       # Very dark backgrounds
BG_MEDIUM = "#2b2b2b"     # Input fields
BG_LIGHT = "#3a3a3a"      # Buttons
TEXT_PRIMARY = "#ffffff"   # Primary text
TEXT_SECONDARY = "#aaa"    # Secondary text
PRIMARY = "#2196F3"        # Blue primary actions
SUCCESS = "#4CAF50"        # Green success
ERROR = "#f44336"          # Red error
```

### Light Theme (ColorsLight)
```python
BG_DARK = "#f5f5f5"       # Light gray backgrounds
BG_MEDIUM = "#ffffff"     # White input fields
BG_LIGHT = "#e0e0e0"      # Light gray buttons
TEXT_PRIMARY = "#212121"   # Dark gray text
TEXT_SECONDARY = "#666"    # Gray secondary text
PRIMARY = "#2196F3"        # Blue primary actions
SUCCESS = "#4CAF50"        # Green success
ERROR = "#f44336"          # Red error
```

---

## Size Profiles

| Property              | Small | Medium | Large |
|-----------------------|-------|--------|-------|
| Base Font Size        | 11px  | 13px   | 16px  |
| Header Font Size      | 14px  | 16px   | 20px  |
| Button Height         | 32px  | 38px   | 48px  |
| Button Min Width      | 80px  | 100px  | 120px |
| Input Height          | 28px  | 34px   | 42px  |
| Border Width          | 1px   | 2px    | 2px   |
| Spacing (Small)       | 4px   | 6px    | 8px   |
| Spacing (Medium)      | 8px   | 10px   | 12px  |
| Spacing (Large)       | 12px  | 16px   | 20px  |

---

## Available Styles

### Buttons
- `Styles.BUTTON_PRIMARY` - Blue primary action button
- `Styles.BUTTON_SECONDARY` - Gray secondary button
- `Styles.BUTTON_SMALL` - Smaller button (80% size)
- `Styles.BUTTON_SUCCESS` - Green success button

### Input Fields
- `Styles.LINE_EDIT` - Single-line text input
- `Styles.TEXT_EDIT` - Multi-line text input
- `Styles.TEXT_EDIT_CODE` - Code/monospace text input
- `Styles.COMBO_BOX` - Dropdown combo box
- `Styles.SPIN_BOX` - Number spinner input

### Lists & Tables
- `Styles.LIST_WIDGET` - List widget with selection
- (TABLE_WIDGET available in static styles.py if needed)

### Progress
- `Styles.PROGRESS_BAR` - Blue progress bar
- `Styles.PROGRESS_BAR_SUCCESS` - Green progress bar

### Labels
- `Styles.LABEL_HEADER` - Bold header text (14-20px)
- `Styles.LABEL_SUBHEADER` - Bold subheader (12-17px)
- `Styles.LABEL_SECONDARY` - Secondary/italic text
- `Styles.LABEL_HINT` - Small hint text (10-13px)

### Other
- `Styles.INFO_BOX` - Information box with background

---

## Migration Checklist

- [ ] Replace `from docprocessor.gui.styles import Styles, Colors` with dynamic version
- [ ] Test all widgets with Dark theme (default)
- [ ] Test all widgets with Light theme
- [ ] Test all widgets with Small size profile
- [ ] Test all widgets with Medium size profile (default)
- [ ] Test all widgets with Large size profile
- [ ] Add appearance settings menu to main window
- [ ] Add language strings for appearance settings
- [ ] Test theme switching at runtime
- [ ] Test size profile switching at runtime
- [ ] Consider persisting user preferences to project settings

---

## Future Enhancements

1. **Persistent Settings**: Save theme/size preferences to user config file
2. **Auto Theme**: Detect system theme and apply automatically
3. **Custom Themes**: Allow users to create custom color schemes
4. **Font Family Selection**: Add font family chooser (sans-serif vs serif)
5. **High Contrast Mode**: Special mode for vision impairment
6. **Animation Control**: Enable/disable UI transitions
7. **Compact Mode**: Even smaller than "Small" for power users

---

## Troubleshooting

### Issue: Styles not updating after theme change
**Solution**: Ensure you're using dynamic styles (`styles_dynamic.py`), not static styles. The old `styles.py` uses fixed strings that won't update.

### Issue: Widget looks broken with Large size profile
**Solution**: Check if widget has fixed size constraints. Remove fixed widths/heights and let layout managers handle sizing.

### Issue: Colors don't match between widgets
**Solution**: Ensure all widgets use `Colors` from `styles_dynamic`, not hardcoded hex values.

### Issue: Performance problems with many widgets
**Solution**: Consider caching generated styles if the same style is applied to many widgets:
```python
# Cache style string
cached_primary_style = Styles.BUTTON_PRIMARY
for button in many_buttons:
    button.setStyleSheet(cached_primary_style)
```

---

## API Reference

### ThemeManager Methods
- `get_current_theme() -> ThemeType` - Get active theme
- `set_theme(theme: ThemeType)` - Change theme
- `get_colors()` - Get current color palette class
- `register_observer(callback)` - Subscribe to theme changes
- `unregister_observer(callback)` - Unsubscribe from changes

### SizeProfileManager Methods
- `get_current_profile_type() -> SizeProfileType` - Get active profile type
- `get_current_profile() -> SizeProfile` - Get active profile object
- `set_profile(profile_type: SizeProfileType)` - Change profile
- `register_observer(callback)` - Subscribe to profile changes
- `unregister_observer(callback)` - Unsubscribe from changes

### SizeProfile Properties
- `font_size_base` - Base font size in pixels
- `font_size_header` - Header font size
- `font_size_subheader` - Subheader font size
- `font_size_small` - Small font size
- `button_height` - Button minimum height
- `button_padding` - Button padding
- `button_min_width` - Button minimum width
- `input_height` - Input field height
- `input_padding` - Input field padding
- `spacing_small/medium/large` - Layout spacing values
- `border_width` - Border thickness
- `border_radius` - Corner rounding

---

## Contact & Support

For questions or issues with the parameterization system, please refer to:
- This guide (PARAMETERIZATION_GUIDE.md)
- Source code documentation in `src/docprocessor/gui/`
- Theme manager: `theme_manager.py`
- Size profiles: `size_profile.py`
- Dynamic styles: `styles_dynamic.py`
