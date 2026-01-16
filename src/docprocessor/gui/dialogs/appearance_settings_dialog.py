"""Appearance settings dialog for theme and accessibility options."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from docprocessor.gui.size_profile import SizeProfileType, get_size_profile_manager
from docprocessor.gui.theme_manager import ThemeType, get_theme_manager
from docprocessor.utils.language_manager import get_language_manager
from docprocessor.utils.user_preferences import get_user_preferences_manager


class AppearanceSettingsDialog(QDialog):
    """Dialog for configuring appearance settings."""

    settings_applied = pyqtSignal()  # Emitted when settings are applied

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.theme_manager = get_theme_manager()
        self.size_manager = get_size_profile_manager()

        self.setWindowTitle(
            self.lang_manager.get("dialog_appearance_settings", "Appearance Settings")
        )
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Theme section
        theme_group = self.create_theme_section()
        layout.addWidget(theme_group)

        # Size profile section
        size_group = self.create_size_section()
        layout.addWidget(size_group)

        # Info label
        info_label = QLabel(
            self.lang_manager.get(
                "appearance_info",
                "Changes will be applied immediately. You may need to restart the application for all changes to take effect.",
            )
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: #666; font-style: italic; padding: 10px; background: #f5f5f5; border-radius: 4px;"
        )
        layout.addWidget(info_label)

        layout.addStretch()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.on_apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_theme_section(self):
        """Create theme selection section."""
        group = QGroupBox(self.lang_manager.get("section_theme", "Theme"))
        layout = QFormLayout(group)

        # Theme combo box
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self.lang_manager.get("theme_dark", "Dark"), ThemeType.DARK)
        self.theme_combo.addItem(self.lang_manager.get("theme_light", "Light"), ThemeType.LIGHT)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_preview)
        layout.addRow(self.lang_manager.get("label_theme", "Theme") + ":", self.theme_combo)

        # Theme description
        self.theme_description = QLabel()
        self.theme_description.setWordWrap(True)
        self.theme_description.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addRow("", self.theme_description)

        return group

    def create_size_section(self):
        """Create size profile selection section."""
        group = QGroupBox(self.lang_manager.get("section_size", "Size & Accessibility"))
        layout = QFormLayout(group)

        # Size profile combo box
        self.size_combo = QComboBox()
        self.size_combo.addItem(
            self.lang_manager.get("size_small", "Small (Compact)"), SizeProfileType.SMALL
        )
        self.size_combo.addItem(
            self.lang_manager.get("size_medium", "Medium (Comfortable)"), SizeProfileType.MEDIUM
        )
        self.size_combo.addItem(
            self.lang_manager.get("size_large", "Large (Accessible)"), SizeProfileType.LARGE
        )
        self.size_combo.currentIndexChanged.connect(self.on_size_preview)
        layout.addRow(
            self.lang_manager.get("label_size_profile", "Size Profile") + ":", self.size_combo
        )

        # Size description
        self.size_description = QLabel()
        self.size_description.setWordWrap(True)
        self.size_description.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addRow("", self.size_description)

        # Size info
        size_info = QLabel(
            self.lang_manager.get(
                "size_info",
                "Choose a larger size profile for better readability and accessibility. "
                "This affects font sizes, button dimensions, and spacing throughout the application.",
            )
        )
        size_info.setWordWrap(True)
        size_info.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        layout.addRow("", size_info)

        return group

    def load_current_settings(self):
        """Load current settings into UI."""
        # Load theme
        current_theme = self.theme_manager.get_current_theme()
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)

        # Load size profile
        current_size = self.size_manager.get_current_profile_type()
        size_index = self.size_combo.findData(current_size)
        if size_index >= 0:
            self.size_combo.setCurrentIndex(size_index)

        # Update descriptions
        self.update_theme_description()
        self.update_size_description()

    def on_theme_preview(self):
        """Handle theme selection change (preview)."""
        self.update_theme_description()

    def on_size_preview(self):
        """Handle size profile selection change (preview)."""
        self.update_size_description()

    def update_theme_description(self):
        """Update theme description label."""
        theme_type = self.theme_combo.currentData()

        if theme_type == ThemeType.DARK:
            desc = self.lang_manager.get(
                "theme_dark_desc",
                "Dark theme reduces eye strain in low-light environments and saves battery on OLED screens.",
            )
        else:
            desc = self.lang_manager.get(
                "theme_light_desc",
                "Light theme provides high contrast and is ideal for well-lit environments.",
            )

        self.theme_description.setText(desc)

    def update_size_description(self):
        """Update size profile description label."""
        size_type = self.size_combo.currentData()

        if size_type == SizeProfileType.SMALL:
            desc = self.lang_manager.get(
                "size_small_desc",
                "Compact interface with smaller fonts and controls. Maximizes screen space.",
            )
        elif size_type == SizeProfileType.MEDIUM:
            desc = self.lang_manager.get(
                "size_medium_desc",
                "Balanced interface with comfortable sizes. Recommended for most users.",
            )
        else:  # LARGE
            desc = self.lang_manager.get(
                "size_large_desc",
                "Larger fonts and controls for improved readability. Ideal for accessibility needs or larger displays.",
            )

        self.size_description.setText(desc)

    def on_apply(self):
        """Apply settings without closing dialog."""
        self.apply_settings()

    def apply_settings(self):
        """Apply selected settings."""
        # Apply theme
        selected_theme = self.theme_combo.currentData()
        self.theme_manager.set_theme(selected_theme)

        # Apply size profile
        selected_size = self.size_combo.currentData()
        self.size_manager.set_profile(selected_size)

        # Save to user preferences
        prefs_manager = get_user_preferences_manager()
        prefs_manager.set_theme(selected_theme)
        prefs_manager.set_size_profile(selected_size)

        # Emit signal for UI refresh
        self.settings_applied.emit()

        # Show success message
        QMessageBox.information(
            self,
            self.lang_manager.get("settings_applied", "Settings Applied"),
            self.lang_manager.get(
                "settings_applied_msg",
                "Appearance settings have been applied. Some changes may require restarting the application.",
            ),
        )

    def accept(self):
        """Apply settings and close dialog."""
        self.apply_settings()
        super().accept()
