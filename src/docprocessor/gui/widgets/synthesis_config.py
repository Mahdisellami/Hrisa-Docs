"""Synthesis configuration widget."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from docprocessor.gui.styles import Colors, Styles
from docprocessor.utils.language_manager import get_language_manager


class SynthesisConfigWidget(QWidget):
    """Widget for configuring synthesis parameters."""

    config_changed = pyqtSignal(dict)  # Emitted when configuration changes
    synthesis_requested = pyqtSignal()  # Emitted when user clicks synthesize

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.lang_manager.get("label_synthesis_config"))
        header.setStyleSheet(Styles.LABEL_HEADER)
        layout.addWidget(header)

        # Theme settings
        theme_group = QGroupBox(self.lang_manager.get("label_theme_discovery"))
        theme_layout = QFormLayout()

        self.num_themes_spin = QSpinBox()
        self.num_themes_spin.setRange(2, 20)
        self.num_themes_spin.setValue(5)
        self.num_themes_spin.setToolTip(self.lang_manager.get("tooltip_num_themes"))
        theme_layout.addRow(self.lang_manager.get("label_num_themes"), self.num_themes_spin)

        self.auto_themes_check = QCheckBox(self.lang_manager.get("label_auto_detect"))
        self.auto_themes_check.setChecked(True)
        self.auto_themes_check.setToolTip(self.lang_manager.get("tooltip_auto_detect"))
        theme_layout.addRow("", self.auto_themes_check)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Synthesis settings
        synthesis_group = QGroupBox(self.lang_manager.get("label_synthesis_settings"))
        synthesis_layout = QFormLayout()

        self.synthesis_level_combo = QComboBox()
        self.synthesis_level_combo.addItems(
            [
                self.lang_manager.get("synthesis_short"),
                self.lang_manager.get("synthesis_normal"),
                self.lang_manager.get("synthesis_comprehensive"),
            ]
        )
        self.synthesis_level_combo.setCurrentIndex(1)  # Default to Normal
        self.synthesis_level_combo.setToolTip(self.lang_manager.get("tooltip_synthesis_level"))
        synthesis_layout.addRow(
            self.lang_manager.get("label_synthesis_level"), self.synthesis_level_combo
        )

        self.chunks_per_chapter_spin = QSpinBox()
        self.chunks_per_chapter_spin.setRange(50, 300)
        self.chunks_per_chapter_spin.setValue(150)
        self.chunks_per_chapter_spin.setToolTip(self.lang_manager.get("tooltip_chunks_per_chapter"))
        synthesis_layout.addRow(
            self.lang_manager.get("label_chunks_per_chapter"), self.chunks_per_chapter_spin
        )

        synthesis_group.setLayout(synthesis_layout)
        layout.addWidget(synthesis_group)

        # Output settings
        output_group = QGroupBox(self.lang_manager.get("label_output_settings"))
        output_layout = QFormLayout()

        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(
            [
                self.lang_manager.get("format_markdown"),
                self.lang_manager.get("format_docx"),
                self.lang_manager.get("format_pdf"),
                self.lang_manager.get("format_both"),
                self.lang_manager.get("format_all"),
            ]
        )
        self.output_format_combo.setCurrentIndex(3)  # Default to Markdown + DOCX
        self.output_format_combo.setToolTip(self.lang_manager.get("tooltip_output_format"))
        output_layout.addRow(self.lang_manager.get("label_output_format"), self.output_format_combo)

        self.include_citations_check = QCheckBox(self.lang_manager.get("label_include_citations"))
        self.include_citations_check.setChecked(True)
        self.include_citations_check.setToolTip(self.lang_manager.get("tooltip_include_citations"))
        output_layout.addRow("", self.include_citations_check)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.synthesize_btn = QPushButton(self.lang_manager.get("btn_start_synthesis"))
        self.synthesize_btn.setStyleSheet(Styles.BUTTON_SUCCESS)
        self.synthesize_btn.setEnabled(False)
        self.synthesize_btn.setToolTip(self.lang_manager.get("tooltip_start_synthesis"))
        button_layout.addWidget(self.synthesize_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(Styles.PROGRESS_BAR_SUCCESS)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(self.lang_manager.get("status_configure"))
        self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)
        layout.addWidget(self.status_label)

        # Cache status label
        self.cache_status_label = QLabel()
        self.cache_status_label.setStyleSheet(Styles.LABEL_HINT)
        self.cache_status_label.setVisible(False)
        layout.addWidget(self.cache_status_label)

        layout.addStretch()

        # Connect signals
        self.num_themes_spin.valueChanged.connect(self.on_config_changed)
        self.auto_themes_check.stateChanged.connect(self.on_auto_themes_changed)
        self.synthesis_level_combo.currentIndexChanged.connect(self.on_config_changed)
        self.chunks_per_chapter_spin.valueChanged.connect(self.on_config_changed)
        self.output_format_combo.currentIndexChanged.connect(self.on_config_changed)
        self.include_citations_check.stateChanged.connect(self.on_config_changed)
        self.synthesize_btn.clicked.connect(self.on_synthesize_clicked)

    def on_auto_themes_changed(self):
        """Handle auto-detect themes checkbox change."""
        auto_enabled = self.auto_themes_check.isChecked()
        self.num_themes_spin.setEnabled(not auto_enabled)
        self.on_config_changed()

    def on_config_changed(self):
        """Handle configuration change."""
        config = self.get_config()
        self.config_changed.emit(config)

    def on_synthesize_clicked(self):
        """Handle synthesize button click."""
        self.synthesis_requested.emit()

    def get_config(self) -> dict:
        """Get current configuration."""
        # Map synthesis level to string
        synthesis_level_map = {0: "short", 1: "normal", 2: "comprehensive"}

        # Map output format to string
        output_format_map = {
            0: "markdown",
            1: "docx",
            2: "pdf",
            3: "both",  # Markdown + DOCX
            4: "all",  # All formats including PDF
        }

        return {
            "num_themes": (
                None if self.auto_themes_check.isChecked() else self.num_themes_spin.value()
            ),
            "auto_themes": self.auto_themes_check.isChecked(),
            "synthesis_level": synthesis_level_map[self.synthesis_level_combo.currentIndex()],
            "chunks_per_chapter": self.chunks_per_chapter_spin.value(),
            "output_format": output_format_map[self.output_format_combo.currentIndex()],
            "include_citations": self.include_citations_check.isChecked(),
        }

    def set_ready_for_synthesis(self, ready: bool):
        """Enable/disable synthesis button."""
        self.synthesize_btn.setEnabled(ready)
        if ready:
            self.status_label.setText(self.lang_manager.get("status_ready"))
            self.status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-style: italic;")
        else:
            self.status_label.setText(self.lang_manager.get("status_configure"))
            self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)

    def update_status(self, status: str, is_error: bool = False):
        """Update status label."""
        self.status_label.setText(status)
        if is_error:
            self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-style: italic;")
        else:
            self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)

    def update_cache_status(self, cache=None):
        """Update cache status display."""
        if cache:
            cache_date = cache.generated_at.strftime("%Y-%m-%d %H:%M")
            cache_text = (
                f"Cached synthesis available: "
                f"{cache.total_words:,} words, "
                f"{len(cache.chapters)} chapters, "
                f"generated {cache_date}"
            )
            self.cache_status_label.setText(cache_text)
            self.cache_status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 11px;")
            self.cache_status_label.setVisible(True)
        else:
            self.cache_status_label.setVisible(False)
