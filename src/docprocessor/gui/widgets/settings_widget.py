"""Settings widget for application configuration."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from docprocessor.utils.language_manager import (
    Language,
    LanguageManager,
    get_language_manager,
    set_global_language,
)
from docprocessor.utils.user_preferences import get_user_preferences_manager


class SettingsWidget(QWidget):
    """Widget for application settings."""

    language_changed = pyqtSignal(str)  # Emitted when language changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.lang_manager.get("tab_settings"))
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Language Settings Group
        lang_group = QGroupBox(self.lang_manager.get("label_language"))
        lang_layout = QFormLayout()

        # UI Language
        self.ui_lang_combo = QComboBox()
        for lang in LanguageManager.get_available_languages():
            self.ui_lang_combo.addItem(self.lang_manager.get_language_name(lang), lang.value)
        # Set current language
        current_lang_code = settings.language
        index = self.ui_lang_combo.findData(current_lang_code)
        if index >= 0:
            self.ui_lang_combo.setCurrentIndex(index)

        lang_layout.addRow(self.lang_manager.get("label_language_ui"), self.ui_lang_combo)

        # Pipeline Language
        self.pipeline_lang_combo = QComboBox()
        self.pipeline_lang_combo.addItem("Auto-detect", "auto")
        for lang in LanguageManager.get_available_languages():
            self.pipeline_lang_combo.addItem(self.lang_manager.get_language_name(lang), lang.value)
        # Set current pipeline language
        current_pipeline_lang = settings.pipeline_language
        index = self.pipeline_lang_combo.findData(current_pipeline_lang)
        if index >= 0:
            self.pipeline_lang_combo.setCurrentIndex(index)

        lang_layout.addRow(
            self.lang_manager.get("label_language_pipeline"), self.pipeline_lang_combo
        )

        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # System Settings Group
        system_group = QGroupBox("System Settings")
        system_layout = QFormLayout()

        # Read-only settings display
        self.ollama_label = QLabel(settings.ollama_model)
        system_layout.addRow(self.lang_manager.get("label_ollama_model"), self.ollama_label)

        self.vector_store_label = QLabel("ChromaDB")
        system_layout.addRow(self.lang_manager.get("label_vector_store"), self.vector_store_label)

        self.output_dir_label = QLabel(str(settings.output_dir))
        system_layout.addRow(self.lang_manager.get("label_output_dir"), self.output_dir_label)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Apply button
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Info label
        info_label = QLabel(
            "Note: Changing UI language requires application restart.\n"
            "Pipeline language affects theme labeling and synthesis output."
        )
        info_label.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        layout.addWidget(info_label)

        layout.addStretch()

        # Connect signals
        self.ui_lang_combo.currentIndexChanged.connect(self.on_ui_language_changed)
        self.pipeline_lang_combo.currentIndexChanged.connect(self.on_pipeline_language_changed)

    def on_ui_language_changed(self, index):
        """Handle UI language change."""
        lang_code = self.ui_lang_combo.currentData()
        # Update global language manager
        lang_enum = Language(lang_code)
        set_global_language(lang_enum)
        self.lang_manager = get_language_manager()

        # Note: Full UI translation would require recreating all widgets
        # For now, show a message about restart requirement
        QMessageBox.information(
            self,
            "Language Changed",
            f"UI language changed to {self.lang_manager.get_language_name(lang_enum)}.\n\n"
            "Please restart the application for changes to take full effect.",
        )

    def on_pipeline_language_changed(self, index):
        """Handle pipeline language change."""
        # This will be used when generating themes and chapters
        pass

    def apply_settings(self):
        """Apply and save settings."""
        ui_lang = self.ui_lang_combo.currentData()
        pipeline_lang = self.pipeline_lang_combo.currentData()

        # Update global settings
        settings.language = ui_lang
        settings.pipeline_language = pipeline_lang

        # Save to user preferences for persistence
        prefs_manager = get_user_preferences_manager()
        prefs_manager.set_language(ui_lang)

        # Emit signal
        self.language_changed.emit(ui_lang)

        QMessageBox.information(
            self,
            self.lang_manager.get("ok"),
            "Settings saved successfully!\n\n"
            "UI language: Requires restart\n"
            f"Pipeline language: {pipeline_lang}",
        )

    def refresh_translations(self):
        """Refresh all translatable text (for language changes)."""
        # This would be called when language changes
        # For now, this is a placeholder
        pass
