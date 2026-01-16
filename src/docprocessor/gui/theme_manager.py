"""Theme management system for dynamic UI theming.

This module provides theme switching capabilities between dark and light modes.
"""

from enum import Enum
from typing import Optional


class ThemeType(Enum):
    """Available theme types."""

    DARK = "dark"
    LIGHT = "light"


class ColorsDark:
    """Dark theme color palette."""

    # Backgrounds
    BG_DARK = "#1e1e1e"  # Very dark - for lists, code areas
    BG_MEDIUM = "#2b2b2b"  # Medium dark - for input fields
    BG_LIGHT = "#3a3a3a"  # Light dark - for buttons
    BG_HOVER = "#4a4a4a"  # Hover state
    BG_PRESSED = "#2a2a2a"  # Pressed state

    # Borders
    BORDER_DARK = "#333"  # Dark borders
    BORDER_NORMAL = "#444"  # Normal borders
    BORDER_LIGHT = "#555"  # Light borders
    BORDER_FOCUS = "#2196F3"  # Focus state - blue

    # Text
    TEXT_PRIMARY = "#ffffff"  # Primary text - white
    TEXT_SECONDARY = "#aaa"  # Secondary text - light gray
    TEXT_DISABLED = "#666"  # Disabled text
    TEXT_HINT = "#888"  # Hint/placeholder text

    # Primary Actions
    PRIMARY = "#2196F3"  # Primary button color - blue
    PRIMARY_HOVER = "#1976D2"  # Primary hover
    PRIMARY_PRESSED = "#0D47A1"  # Primary pressed

    # Success/Error/Warning
    SUCCESS = "#4CAF50"  # Success green
    SUCCESS_HOVER = "#45a049"  # Success hover
    ERROR = "#f44336"  # Error red
    ERROR_HOVER = "#d32f2f"  # Error hover
    WARNING = "#ff9800"  # Warning orange
    WARNING_HOVER = "#f57c00"  # Warning hover

    # Special
    SELECTION = "#264f78"  # Selection background
    DISABLED_BG = "#555555"  # Disabled background
    DISABLED_TEXT = "#888888"  # Disabled text


class ColorsLight:
    """Light theme color palette."""

    # Backgrounds
    BG_DARK = "#f5f5f5"  # Light gray - for lists, code areas
    BG_MEDIUM = "#ffffff"  # White - for input fields
    BG_LIGHT = "#e0e0e0"  # Light gray - for buttons
    BG_HOVER = "#d0d0d0"  # Hover state
    BG_PRESSED = "#c0c0c0"  # Pressed state

    # Borders
    BORDER_DARK = "#bbb"  # Dark borders
    BORDER_NORMAL = "#ccc"  # Normal borders
    BORDER_LIGHT = "#ddd"  # Light borders
    BORDER_FOCUS = "#2196F3"  # Focus state - blue

    # Text
    TEXT_PRIMARY = "#212121"  # Primary text - dark gray
    TEXT_SECONDARY = "#666"  # Secondary text - gray
    TEXT_DISABLED = "#aaa"  # Disabled text
    TEXT_HINT = "#999"  # Hint/placeholder text

    # Primary Actions
    PRIMARY = "#2196F3"  # Primary button color - blue
    PRIMARY_HOVER = "#1976D2"  # Primary hover
    PRIMARY_PRESSED = "#0D47A1"  # Primary pressed

    # Success/Error/Warning
    SUCCESS = "#4CAF50"  # Success green
    SUCCESS_HOVER = "#45a049"  # Success hover
    ERROR = "#f44336"  # Error red
    ERROR_HOVER = "#d32f2f"  # Error hover
    WARNING = "#ff9800"  # Warning orange
    WARNING_HOVER = "#f57c00"  # Warning hover

    # Special
    SELECTION = "#90CAF9"  # Selection background - light blue
    DISABLED_BG = "#e0e0e0"  # Disabled background
    DISABLED_TEXT = "#bbb"  # Disabled text


class ThemeManager:
    """Manages application theme switching."""

    _instance: Optional["ThemeManager"] = None
    _current_theme: ThemeType = ThemeType.DARK
    _observers = []

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ThemeManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_current_theme(self) -> ThemeType:
        """Get current theme type."""
        return self._current_theme

    def set_theme(self, theme: ThemeType):
        """Set current theme and notify observers."""
        if self._current_theme != theme:
            self._current_theme = theme
            self._notify_observers()

    def get_colors(self):
        """Get color palette for current theme."""
        if self._current_theme == ThemeType.DARK:
            return ColorsDark
        else:
            return ColorsLight

    def register_observer(self, callback):
        """Register a callback to be notified of theme changes."""
        if callback not in self._observers:
            self._observers.append(callback)

    def unregister_observer(self, callback):
        """Unregister a theme change observer."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Notify all observers of theme change."""
        for callback in self._observers:
            try:
                callback(self._current_theme)
            except Exception as e:
                print(f"Error notifying theme observer: {e}")


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return ThemeManager.get_instance()
