"""User preferences manager for persistent application settings.

This module handles loading, saving, and managing user preferences including
theme, size profile, and other application-wide settings.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from docprocessor.gui.size_profile import SizeProfileType
from docprocessor.gui.theme_manager import ThemeType
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SearchHistoryEntry:
    """Single entry in search history."""

    query: str
    timestamp: str  # ISO format
    sources: List[str]  # e.g., ["data.gov.tn"]
    strategy: str  # "auto", "google", "native"
    result_count: int
    handler_used: str  # "google", "ckan", "mixed"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "timestamp": self.timestamp,
            "sources": self.sources,
            "strategy": self.strategy,
            "result_count": self.result_count,
            "handler_used": self.handler_used,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SearchHistoryEntry":
        """Create from dictionary."""
        return cls(
            query=data["query"],
            timestamp=data["timestamp"],
            sources=data.get("sources", []),
            strategy=data.get("strategy", "google"),
            result_count=data.get("result_count", 0),
            handler_used=data.get("handler_used", "unknown"),
        )


class UserPreferences:
    """User preferences data model."""

    def __init__(
        self,
        theme: str = "dark",
        size_profile: str = "small",
        language: str = "fr",
        last_project_id: Optional[str] = None,
        window_geometry: Optional[dict] = None,
        search_history: Optional[List[dict]] = None,
    ):
        self.theme = theme
        self.size_profile = size_profile
        self.language = language
        self.last_project_id = last_project_id
        self.window_geometry = window_geometry or {}
        self.search_history = search_history or []
        self.last_modified = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert preferences to dictionary."""
        return {
            "theme": self.theme,
            "size_profile": self.size_profile,
            "language": self.language,
            "last_project_id": self.last_project_id,
            "window_geometry": self.window_geometry,
            "search_history": self.search_history,
            "last_modified": self.last_modified,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create preferences from dictionary."""
        return cls(
            theme=data.get("theme", "dark"),
            size_profile=data.get("size_profile", "small"),
            language=data.get("language", "fr"),
            last_project_id=data.get("last_project_id"),
            window_geometry=data.get("window_geometry", {}),
            search_history=data.get("search_history", []),
        )


class UserPreferencesManager:
    """Manages loading and saving user preferences."""

    _instance: Optional["UserPreferencesManager"] = None
    _preferences_file: Path = Path.home() / ".docprocessor" / "preferences.json"

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize preferences manager."""
        if not hasattr(self, "_initialized"):
            self._preferences: Optional[UserPreferences] = None
            self._initialized = True

            # Ensure preferences directory exists
            self._preferences_file.parent.mkdir(parents=True, exist_ok=True)

            # Load preferences
            self.load()

    @classmethod
    def get_instance(cls) -> "UserPreferencesManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> UserPreferences:
        """Load preferences from file."""
        if self._preferences_file.exists():
            try:
                with open(self._preferences_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._preferences = UserPreferences.from_dict(data)
                    logger.info(f"Loaded user preferences from {self._preferences_file}")
            except Exception as e:
                logger.warning(f"Failed to load preferences: {e}. Using defaults.")
                self._preferences = UserPreferences()
        else:
            logger.info("No preferences file found. Using defaults.")
            self._preferences = UserPreferences()

        return self._preferences

    def save(self) -> bool:
        """Save preferences to file."""
        if self._preferences is None:
            logger.warning("No preferences to save")
            return False

        try:
            # Update last modified timestamp
            self._preferences.last_modified = datetime.now().isoformat()

            # Write to file
            with open(self._preferences_file, "w", encoding="utf-8") as f:
                json.dump(self._preferences.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Saved user preferences to {self._preferences_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def get_preferences(self) -> UserPreferences:
        """Get current preferences."""
        if self._preferences is None:
            self.load()
        return self._preferences

    def get_theme(self) -> ThemeType:
        """Get theme preference."""
        prefs = self.get_preferences()
        try:
            return ThemeType(prefs.theme)
        except ValueError:
            logger.warning(f"Invalid theme value: {prefs.theme}. Using DARK.")
            return ThemeType.DARK

    def set_theme(self, theme: ThemeType) -> bool:
        """Set theme preference and save."""
        prefs = self.get_preferences()
        prefs.theme = theme.value
        return self.save()

    def get_size_profile(self) -> SizeProfileType:
        """Get size profile preference."""
        prefs = self.get_preferences()
        try:
            return SizeProfileType(prefs.size_profile)
        except ValueError:
            logger.warning(f"Invalid size profile value: {prefs.size_profile}. Using SMALL.")
            return SizeProfileType.SMALL

    def set_size_profile(self, size_profile: SizeProfileType) -> bool:
        """Set size profile preference and save."""
        prefs = self.get_preferences()
        prefs.size_profile = size_profile.value
        return self.save()

    def get_language(self) -> str:
        """Get language preference."""
        return self.get_preferences().language

    def set_language(self, language: str) -> bool:
        """Set language preference and save."""
        prefs = self.get_preferences()
        prefs.language = language
        return self.save()

    def get_last_project_id(self) -> Optional[str]:
        """Get last opened project ID."""
        return self.get_preferences().last_project_id

    def set_last_project_id(self, project_id: Optional[str]) -> bool:
        """Set last opened project ID and save."""
        prefs = self.get_preferences()
        prefs.last_project_id = project_id
        return self.save()

    def get_window_geometry(self) -> dict:
        """Get window geometry (position and size)."""
        return self.get_preferences().window_geometry

    def set_window_geometry(self, geometry: dict) -> bool:
        """Set window geometry and save."""
        prefs = self.get_preferences()
        prefs.window_geometry = geometry
        return self.save()

    # Search History Management

    def add_search_history_entry(
        self,
        query: str,
        sources: List[str],
        strategy: str,
        result_count: int,
        handler_used: str,
    ) -> bool:
        """
        Add entry to search history (max 20, FIFO).

        Args:
            query: Search query text
            sources: List of source domains searched
            strategy: Search strategy used ("auto", "google", "native")
            result_count: Number of results found
            handler_used: Handler that was used ("google", "ckan", "mixed")

        Returns:
            bool: True if saved successfully
        """
        prefs = self.get_preferences()

        entry = SearchHistoryEntry(
            query=query,
            timestamp=datetime.now().isoformat(),
            sources=sources,
            strategy=strategy,
            result_count=result_count,
            handler_used=handler_used,
        )

        # Add to front, limit to 20
        prefs.search_history.insert(0, entry.to_dict())
        prefs.search_history = prefs.search_history[:20]

        return self.save()

    def get_search_history(self) -> List[SearchHistoryEntry]:
        """
        Get search history as list of SearchHistoryEntry objects.

        Returns:
            List[SearchHistoryEntry]: List of history entries (most recent first)
        """
        prefs = self.get_preferences()
        try:
            return [SearchHistoryEntry.from_dict(e) for e in prefs.search_history]
        except Exception as e:
            logger.error(f"Failed to load search history: {e}")
            # Clear corrupted history
            prefs.search_history = []
            self.save()
            return []

    def clear_search_history(self) -> bool:
        """
        Clear all search history.

        Returns:
            bool: True if cleared successfully
        """
        prefs = self.get_preferences()
        prefs.search_history = []
        return self.save()

    def remove_search_history_entry(self, index: int) -> bool:
        """
        Remove specific history entry by index.

        Args:
            index: Index of entry to remove (0 = most recent)

        Returns:
            bool: True if removed successfully
        """
        prefs = self.get_preferences()
        if 0 <= index < len(prefs.search_history):
            prefs.search_history.pop(index)
            return self.save()
        return False

    def reset_to_defaults(self) -> bool:
        """Reset all preferences to defaults."""
        self._preferences = UserPreferences()
        return self.save()

    def get_preferences_file_path(self) -> Path:
        """Get path to preferences file."""
        return self._preferences_file


def get_user_preferences_manager() -> UserPreferencesManager:
    """Get the global user preferences manager instance."""
    return UserPreferencesManager.get_instance()
