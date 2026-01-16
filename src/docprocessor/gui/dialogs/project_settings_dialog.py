"""Project settings dialog for editing project configuration."""

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from docprocessor.models.project import Project
from docprocessor.utils.language_manager import get_language_manager


class ProjectSettingsDialog(QDialog):
    """Dialog for editing project settings."""

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.lang_manager = get_language_manager()

        self.setWindowTitle(
            self.lang_manager.get("dialog_project_settings", "Paramètres du projet")
        )
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Project Information Section
        info_group = self.create_info_section()
        layout.addWidget(info_group)

        # Language & LLM Settings Section
        llm_group = self.create_llm_section()
        layout.addWidget(llm_group)

        # Document Processing Settings Section
        processing_group = self.create_processing_section()
        layout.addWidget(processing_group)

        # Output Settings Section
        output_group = self.create_output_section()
        layout.addWidget(output_group)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_info_section(self):
        """Create project information section."""
        group = QGroupBox(self.lang_manager.get("section_project_info", "Informations du projet"))
        layout = QFormLayout(group)

        # Project name
        self.name_edit = QLineEdit()
        layout.addRow(
            self.lang_manager.get("label_project_name", "Nom du projet") + ":", self.name_edit
        )

        # Project description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        layout.addRow(
            self.lang_manager.get("label_description", "Description") + ":", self.description_edit
        )

        # Author
        self.author_edit = QLineEdit()
        layout.addRow(self.lang_manager.get("label_author", "Auteur") + ":", self.author_edit)

        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText(
            self.lang_manager.get("placeholder_tags", "Comma-separated tags")
        )
        layout.addRow(self.lang_manager.get("label_tags", "Tags") + ":", self.tags_edit)

        return group

    def create_llm_section(self):
        """Create LLM settings section."""
        group = QGroupBox(self.lang_manager.get("section_llm_settings", "Language Model Settings"))
        layout = QFormLayout(group)

        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["fr", "en", "ar"])
        layout.addRow(
            self.lang_manager.get("label_language", "Language") + ":", self.language_combo
        )

        # LLM Model
        self.llm_model_edit = QLineEdit()
        self.llm_model_edit.setPlaceholderText("mistral:latest")
        layout.addRow(
            self.lang_manager.get("label_llm_model", "LLM Model") + ":", self.llm_model_edit
        )

        # Temperature
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(1)
        layout.addRow(
            self.lang_manager.get("label_temperature", "Temperature") + ":", self.temperature_spin
        )

        # Embedding Model
        self.embedding_model_edit = QLineEdit()
        self.embedding_model_edit.setPlaceholderText("sentence-transformers/all-MiniLM-L6-v2")
        layout.addRow(
            self.lang_manager.get("label_embedding_model", "Embedding Model") + ":",
            self.embedding_model_edit,
        )

        return group

    def create_processing_section(self):
        """Create document processing settings section."""
        group = QGroupBox(
            self.lang_manager.get("section_processing_settings", "Processing Settings")
        )
        layout = QFormLayout(group)

        # Chunk size
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 5000)
        self.chunk_size_spin.setSingleStep(100)
        layout.addRow(
            self.lang_manager.get("label_chunk_size", "Chunk Size") + ":", self.chunk_size_spin
        )

        # Chunk overlap
        self.chunk_overlap_spin = QSpinBox()
        self.chunk_overlap_spin.setRange(0, 500)
        self.chunk_overlap_spin.setSingleStep(10)
        layout.addRow(
            self.lang_manager.get("label_chunk_overlap", "Chunk Overlap") + ":",
            self.chunk_overlap_spin,
        )

        return group

    def create_output_section(self):
        """Create output settings section."""
        group = QGroupBox(self.lang_manager.get("section_output_settings", "Output Settings"))
        layout = QFormLayout(group)

        # Output format
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["markdown", "docx", "pdf", "both"])
        layout.addRow(
            self.lang_manager.get("label_output_format", "Default Output Format") + ":",
            self.output_format_combo,
        )

        # Include citations
        self.include_citations_check = QCheckBox(
            self.lang_manager.get("label_include_citations", "Include Citations")
        )
        layout.addRow("", self.include_citations_check)

        # Citation style
        self.citation_style_combo = QComboBox()
        self.citation_style_combo.addItems(["APA", "MLA", "Chicago", "IEEE"])
        layout.addRow(
            self.lang_manager.get("label_citation_style", "Citation Style") + ":",
            self.citation_style_combo,
        )

        return group

    def load_settings(self):
        """Load project settings into UI fields."""
        # Project info
        self.name_edit.setText(self.project.name)
        self.description_edit.setPlainText(self.project.description)
        self.author_edit.setText(self.project.author)
        self.tags_edit.setText(", ".join(self.project.tags))

        # LLM settings
        settings = self.project.settings
        lang_index = self.language_combo.findText(settings.language)
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)

        self.llm_model_edit.setText(settings.llm_model)
        self.temperature_spin.setValue(settings.temperature)
        self.embedding_model_edit.setText(settings.embedding_model)

        # Processing settings
        self.chunk_size_spin.setValue(settings.chunk_size)
        self.chunk_overlap_spin.setValue(settings.chunk_overlap)

        # Output settings
        format_index = self.output_format_combo.findText(settings.default_output_format)
        if format_index >= 0:
            self.output_format_combo.setCurrentIndex(format_index)

        self.include_citations_check.setChecked(settings.include_citations)

        style_index = self.citation_style_combo.findText(settings.citation_style)
        if style_index >= 0:
            self.citation_style_combo.setCurrentIndex(style_index)

    def save_settings(self):
        """Save UI fields back to project settings."""
        # Project info
        self.project.name = self.name_edit.text().strip()
        self.project.description = self.description_edit.toPlainText().strip()
        self.project.author = self.author_edit.text().strip()

        # Parse tags
        tags_text = self.tags_edit.text().strip()
        if tags_text:
            self.project.tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        else:
            self.project.tags = []

        # LLM settings
        self.project.settings.language = self.language_combo.currentText()
        self.project.settings.llm_model = self.llm_model_edit.text().strip()
        self.project.settings.temperature = self.temperature_spin.value()
        self.project.settings.embedding_model = self.embedding_model_edit.text().strip()

        # Processing settings
        self.project.settings.chunk_size = self.chunk_size_spin.value()
        self.project.settings.chunk_overlap = self.chunk_overlap_spin.value()

        # Output settings
        self.project.settings.default_output_format = self.output_format_combo.currentText()
        self.project.settings.include_citations = self.include_citations_check.isChecked()
        self.project.settings.citation_style = self.citation_style_combo.currentText()

        # Update timestamp
        self.project.update_timestamp()

    def accept(self):
        """Handle dialog acceptance - save settings."""
        self.save_settings()
        super().accept()
