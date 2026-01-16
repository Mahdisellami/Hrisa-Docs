"""Theme editor widget."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from docprocessor.gui.styles import Styles
from docprocessor.utils.language_manager import get_language_manager


class ThemeEditorWidget(QWidget):
    """Widget for editing and managing themes."""

    themes_changed = pyqtSignal(list)  # Emitted when themes change

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.themes = []
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.lang_manager.get("label_discovered_themes"))
        header.setStyleSheet(Styles.LABEL_HEADER)
        layout.addWidget(header)

        # Theme list
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        # Enable multi-selection with Cmd/Ctrl+Click
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.rename_btn = QPushButton(self.lang_manager.get("btn_rename"))
        self.rename_btn.setToolTip(self.lang_manager.get("tooltip_rename_theme"))
        self.rename_btn.setEnabled(False)
        button_layout.addWidget(self.rename_btn)

        self.merge_btn = QPushButton(self.lang_manager.get("btn_merge"))
        self.merge_btn.setToolTip(self.lang_manager.get("tooltip_merge_themes"))
        self.merge_btn.setEnabled(False)
        button_layout.addWidget(self.merge_btn)

        self.delete_btn = QPushButton(self.lang_manager.get("btn_delete"))
        self.delete_btn.setToolTip(self.lang_manager.get("tooltip_delete_theme"))
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel(self.lang_manager.get("status_no_themes"))
        self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)
        layout.addWidget(self.status_label)

        # Connect signals
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.rename_btn.clicked.connect(self.rename_theme)
        self.merge_btn.clicked.connect(self.merge_themes)
        self.delete_btn.clicked.connect(self.delete_theme)

    def set_themes(self, themes):
        """Set the list of themes."""
        self.themes = themes
        self.list_widget.clear()

        for i, theme in enumerate(themes):
            # Extract theme info
            label = theme.get("label", f"Theme {i+1}")
            chunk_count = len(theme.get("chunk_ids", []))
            importance = theme.get("importance_score", 0.0)

            # Create list item
            chunks_text = self.lang_manager.get("label_chunks")
            item = QListWidgetItem(f"{label} ({chunk_count} {chunks_text}, {importance:.1%})")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.list_widget.addItem(item)

        self.update_status()
        self.themes_changed.emit(self.themes)

    def rename_theme(self):
        """Rename selected theme."""
        current = self.list_widget.currentItem()
        if current:
            idx = current.data(Qt.ItemDataRole.UserRole)
            old_label = self.themes[idx].get("label", "")

            new_label, ok = QInputDialog.getText(
                self,
                self.lang_manager.get("dialog_rename_theme"),
                self.lang_manager.get("dialog_rename_theme_msg"),
                text=old_label,
            )

            if ok and new_label:
                self.themes[idx]["label"] = new_label
                self.set_themes(self.themes)

    def delete_theme(self):
        """Delete selected theme."""
        current = self.list_widget.currentItem()
        if current:
            idx = current.data(Qt.ItemDataRole.UserRole)
            self.themes.pop(idx)
            self.set_themes(self.themes)

    def merge_themes(self):
        """Merge selected themes with validation and LLM-based label generation."""
        selected_items = self.list_widget.selectedItems()
        if len(selected_items) < 2:
            return

        # Get indices of selected themes
        indices = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        indices.sort(reverse=True)

        # Step 1: Validate semantic coherence
        should_merge = self._validate_merge(indices)
        if not should_merge:
            return

        # Step 2: Perform smart merge with LLM
        self._perform_smart_merge(indices)

    def _validate_merge(self, indices):
        """Validate if themes are semantically coherent enough to merge."""
        # Get theme labels for display
        theme_labels = [self.themes[idx].get("label", f"Theme {idx+1}") for idx in indices]

        # For now, we'll check based on chunk count similarity
        # A more sophisticated check would use embeddings
        chunk_counts = [len(self.themes[idx].get("chunk_ids", [])) for idx in indices]
        total_chunks = sum(chunk_counts)

        # Calculate balance - if themes are very imbalanced, warn user
        max_proportion = max(chunk_counts) / total_chunks if total_chunks > 0 else 0

        # If one theme dominates (>80%), warn user
        if max_proportion > 0.8:
            chunks_text = self.lang_manager.get("label_chunks")
            themes_list = "\n".join(
                [
                    f"  • {label} ({count} {chunks_text})"
                    for label, count in zip(theme_labels, chunk_counts)
                ]
            )

            reply = QMessageBox.question(
                self,
                self.lang_manager.get("dialog_confirm_merge"),
                self.lang_manager.get("dialog_confirm_merge_msg", themes_list),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            return reply == QMessageBox.StandardButton.Yes

        # Otherwise, proceed with merge
        return True

    def _perform_smart_merge(self, indices):
        """Perform smart merge with LLM-generated unified label."""
        # Get base theme (first in sorted list)
        base_idx = indices[-1]
        base_theme = self.themes[base_idx]

        # Collect all chunk IDs and labels
        merged_chunks = []
        theme_labels = []

        for idx in indices:
            theme = self.themes[idx]
            merged_chunks.extend(theme.get("chunk_ids", []))
            theme_labels.append(theme.get("label", f"Theme {idx+1}"))

        # Try to generate unified label with LLM
        unified_label = self._generate_unified_label(theme_labels)

        # Remove merged themes (except base) FIRST
        for idx in indices[:-1]:
            self.themes.pop(idx)

        # Update base theme AFTER removal
        base_theme["label"] = unified_label
        base_theme["chunk_ids"] = merged_chunks

        # Recalculate importance scores for all remaining themes
        total_chunks = sum(len(t.get("chunk_ids", [])) for t in self.themes)
        for theme in self.themes:
            theme["importance_score"] = (
                len(theme.get("chunk_ids", [])) / total_chunks if total_chunks > 0 else 1.0
            )

        # Refresh display
        self.set_themes(self.themes)

    def _generate_unified_label(self, theme_labels):
        """Generate unified theme label using LLM."""
        try:
            from docprocessor.llm.ollama_client import OllamaClient
            from docprocessor.utils.language_detector import LanguageDetector

            ollama = OllamaClient()

            # Detect language from original labels
            combined_text = " ".join(theme_labels)
            language = LanguageDetector.detect_language(combined_text)

            # Language-specific instructions
            lang_instruction = ""
            if language == "fr":
                lang_instruction = (
                    "\n\nIMPORTANT: The themes are in French. Your unified label MUST be in French."
                )
            elif language == "en":
                lang_instruction = "\n\nIMPORTANT: The themes are in English. Your unified label MUST be in English."

            # Create prompt for unifying theme labels
            themes_text = "\n".join([f"- {label}" for label in theme_labels])
            prompt = f"""Given these related themes that are being merged:

{themes_text}

Generate a single, concise unified theme label (max 8 words) that captures the essence of all themes.{lang_instruction}
Respond with ONLY the unified label, nothing else."""

            response = ollama.generate(
                prompt=prompt,
                system_prompt="You are a helpful assistant that creates concise, meaningful theme labels in the same language as the input.",
                temperature=0.3,
            )

            # Clean up response
            unified_label = response.strip()

            # If response is too long or empty, fallback to simple combination
            if len(unified_label) > 100 or not unified_label:
                unified_label = " + ".join(theme_labels)

            return unified_label

        except Exception as e:
            # Fallback to simple combination if LLM fails
            print(f"LLM generation failed: {e}")
            return " + ".join(theme_labels)

    def on_selection_changed(self):
        """Handle selection change."""
        selected_count = len(self.list_widget.selectedItems())
        self.rename_btn.setEnabled(selected_count == 1)
        self.delete_btn.setEnabled(selected_count == 1)
        self.merge_btn.setEnabled(selected_count >= 2)

    def update_status(self):
        """Update status label."""
        count = len(self.themes)
        if count == 0:
            self.status_label.setText(self.lang_manager.get("status_no_themes"))
        else:
            self.status_label.setText(self.lang_manager.get("status_n_themes", count))

    def get_themes(self):
        """Get list of themes."""
        return self.themes.copy()
