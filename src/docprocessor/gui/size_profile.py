"""Size profile system for UI accessibility and customization.

This module provides different size profiles for fonts, buttons, and spacing
to accommodate different user needs and preferences.
"""

from enum import Enum
from typing import Optional


class SizeProfileType(Enum):
    """Available size profile types."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class SizeProfile:
    """Size profile defining font sizes, button dimensions, and spacing."""

    def __init__(
        self,
        font_size_base: int,
        font_size_header: int,
        font_size_subheader: int,
        font_size_small: int,
        button_height: int,
        button_padding: int,
        button_min_width: int,
        input_height: int,
        input_padding: int,
        spacing_small: int,
        spacing_medium: int,
        spacing_large: int,
        border_width: int,
        border_radius: int,
    ):
        self.font_size_base = font_size_base
        self.font_size_header = font_size_header
        self.font_size_subheader = font_size_subheader
        self.font_size_small = font_size_small
        self.button_height = button_height
        self.button_padding = button_padding
        self.button_min_width = button_min_width
        self.input_height = input_height
        self.input_padding = input_padding
        self.spacing_small = spacing_small
        self.spacing_medium = spacing_medium
        self.spacing_large = spacing_large
        self.border_width = border_width
        self.border_radius = border_radius


# Predefined size profiles
SIZE_PROFILES = {
    SizeProfileType.SMALL: SizeProfile(
        font_size_base=11,
        font_size_header=14,
        font_size_subheader=12,
        font_size_small=10,
        button_height=32,
        button_padding=8,
        button_min_width=80,
        input_height=28,
        input_padding=6,
        spacing_small=4,
        spacing_medium=8,
        spacing_large=12,
        border_width=1,
        border_radius=4,
    ),
    SizeProfileType.MEDIUM: SizeProfile(
        font_size_base=13,
        font_size_header=16,
        font_size_subheader=14,
        font_size_small=11,
        button_height=38,
        button_padding=10,
        button_min_width=100,
        input_height=34,
        input_padding=8,
        spacing_small=6,
        spacing_medium=10,
        spacing_large=16,
        border_width=2,
        border_radius=5,
    ),
    SizeProfileType.LARGE: SizeProfile(
        font_size_base=16,
        font_size_header=20,
        font_size_subheader=17,
        font_size_small=13,
        button_height=48,
        button_padding=12,
        button_min_width=120,
        input_height=42,
        input_padding=10,
        spacing_small=8,
        spacing_medium=12,
        spacing_large=20,
        border_width=2,
        border_radius=6,
    ),
}


class SizeProfileManager:
    """Manages size profile selection and application."""

    _instance: Optional["SizeProfileManager"] = None
    _current_profile: SizeProfileType = SizeProfileType.SMALL
    _observers = []

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "SizeProfileManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_current_profile_type(self) -> SizeProfileType:
        """Get current size profile type."""
        return self._current_profile

    def get_current_profile(self) -> SizeProfile:
        """Get current size profile."""
        return SIZE_PROFILES[self._current_profile]

    def set_profile(self, profile_type: SizeProfileType):
        """Set current size profile and notify observers."""
        if self._current_profile != profile_type:
            self._current_profile = profile_type
            self._notify_observers()

    def register_observer(self, callback):
        """Register a callback to be notified of profile changes."""
        if callback not in self._observers:
            self._observers.append(callback)

    def unregister_observer(self, callback):
        """Unregister a profile change observer."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Notify all observers of profile change."""
        for callback in self._observers:
            try:
                callback(self._current_profile)
            except Exception as e:
                print(f"Error notifying size profile observer: {e}")


def get_size_profile_manager() -> SizeProfileManager:
    """Get the global size profile manager instance."""
    return SizeProfileManager.get_instance()
