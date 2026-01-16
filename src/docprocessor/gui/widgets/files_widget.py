"""Unified files management widget for input and output."""

import os
import uuid
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from config.settings import settings
from docprocessor.gui.styles import Styles
from docprocessor.models.project import DocumentInfo
from docprocessor.utils.language_manager import get_language_manager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class FilesWidget(QWidget):
    """Widget for managing input PDFs and output files."""

    # Signals
    documents_changed = pyqtSignal(list)  # Emitted when document list changes
    process_requested = pyqtSignal(list)  # Emitted when user wants to process documents

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.documents = []  # Legacy list of document paths
        self.current_project = None  # Current project reference
        self.output_dir = settings.output_dir
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Create splitter for input/output sections
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Input section (Documents source)
        input_section = self.create_input_section()
        splitter.addWidget(input_section)

        # Output section (Generated files)
        output_section = self.create_output_section()
        splitter.addWidget(output_section)

        # Set initial sizes (60% input, 40% output)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)

    def create_input_section(self):
        """Create input documents section."""
        group = QGroupBox("📥 " + self.lang_manager.get("section_input_docs", "Documents sources"))
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Header with document count
        header_layout = QHBoxLayout()
        self.input_status_label = QLabel(self.lang_manager.get("status_no_docs", "Aucun document"))
        self.input_status_label.setStyleSheet(Styles.LABEL_SECONDARY)
        header_layout.addWidget(self.input_status_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Document list
        self.documents_list = QListWidget()
        self.documents_list.setAlternatingRowColors(True)
        self.documents_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.documents_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.documents_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton(self.lang_manager.get("btn_add", "Ajouter"))
        self.add_btn.setToolTip(
            self.lang_manager.get("tooltip_add_docs", "Ajouter des fichiers PDF")
        )
        self.add_btn.clicked.connect(self.import_documents)
        button_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton(self.lang_manager.get("btn_remove", "Retirer"))
        self.remove_btn.setToolTip(
            self.lang_manager.get("tooltip_remove_doc", "Retirer les documents sélectionnés")
        )
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton(self.lang_manager.get("btn_clear_all", "Tout effacer"))
        self.clear_btn.setToolTip(
            self.lang_manager.get("tooltip_clear_all", "Effacer tous les documents")
        )
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)

        self.process_btn = QPushButton(self.lang_manager.get("btn_process", "Traiter"))
        self.process_btn.setToolTip(
            self.lang_manager.get("tooltip_process_docs", "Traiter les documents")
        )
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.on_process_clicked)
        button_layout.addWidget(self.process_btn)

        self.clear_db_btn = QPushButton(self.lang_manager.get("btn_clear_database", "Vider BDD"))
        self.clear_db_btn.setToolTip(
            self.lang_manager.get("tooltip_clear_database", "Vider la base de données")
        )
        button_layout.addWidget(self.clear_db_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return group

    def create_output_section(self):
        """Create output files section."""
        group = QGroupBox("📤 " + self.lang_manager.get("section_output_files", "Fichiers générés"))
        layout = QVBoxLayout(group)

        # Header with file count
        header_layout = QHBoxLayout()
        self.output_status_label = QLabel(
            self.lang_manager.get("status_no_output_files", "Aucun fichier généré")
        )
        self.output_status_label.setStyleSheet(Styles.LABEL_SECONDARY)
        header_layout.addWidget(self.output_status_label)
        header_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 " + self.lang_manager.get("btn_refresh", "Actualiser"))
        self.refresh_btn.setToolTip(
            self.lang_manager.get("tooltip_refresh_files", "Actualiser la liste")
        )
        self.refresh_btn.clicked.connect(self.refresh_output_files)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Output files list
        self.output_list = QListWidget()
        self.output_list.setAlternatingRowColors(True)
        self.output_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )  # Enable multi-selection
        self.output_list.itemSelectionChanged.connect(self.on_output_selection_changed)
        layout.addWidget(self.output_list)

        # Action buttons
        button_layout = QHBoxLayout()

        self.open_btn = QPushButton(self.lang_manager.get("btn_open", "Ouvrir"))
        self.open_btn.setToolTip(self.lang_manager.get("tooltip_open_file", "Ouvrir le fichier"))
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_selected_file)
        button_layout.addWidget(self.open_btn)

        self.open_folder_btn = QPushButton(
            self.lang_manager.get("btn_open_folder", "Ouvrir le dossier")
        )
        self.open_folder_btn.setToolTip(
            self.lang_manager.get("tooltip_open_folder", "Ouvrir le dossier de sortie")
        )
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        button_layout.addWidget(self.open_folder_btn)

        self.delete_output_btn = QPushButton(self.lang_manager.get("btn_delete", "Supprimer"))
        self.delete_output_btn.setToolTip(
            self.lang_manager.get("tooltip_delete_file", "Supprimer le fichier sélectionné")
        )
        self.delete_output_btn.setEnabled(False)
        self.delete_output_btn.clicked.connect(self.delete_selected_output)
        button_layout.addWidget(self.delete_output_btn)

        self.delete_all_output_btn = QPushButton(
            self.lang_manager.get("btn_delete_all", "Tout supprimer")
        )
        self.delete_all_output_btn.setToolTip(
            self.lang_manager.get(
                "tooltip_delete_all_outputs", "Supprimer tous les fichiers générés"
            )
        )
        self.delete_all_output_btn.setEnabled(False)
        self.delete_all_output_btn.clicked.connect(self.delete_all_outputs)
        button_layout.addWidget(self.delete_all_output_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return group

    def set_project(self, project):
        """Set the current project and load its documents."""
        self.current_project = project

        # Clear current UI
        self.documents = []
        self.documents_list.clear()

        # Load documents from project
        if project:
            for doc_info in project.documents:
                # Add to legacy documents list (for compatibility)
                self.documents.append(doc_info.file_path)

                # Create list item with file info
                file_path = Path(doc_info.file_path)
                if file_path.exists():
                    file_size = file_path.stat().st_size / 1024  # KB
                    item_text = f"{file_path.name} ({file_size:.1f} KB)"
                else:
                    # File may have been moved/deleted
                    item_text = f"{file_path.name} [File not found]"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, doc_info.file_path)
                item.setToolTip(doc_info.file_path)
                self.documents_list.addItem(item)

        self.update_input_status()
        self.refresh_output_files()

        # Emit signal to notify other widgets about document changes
        self.documents_changed.emit(self.documents)

    def import_documents(self):
        """Import PDF documents."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            self.lang_manager.get("dialog_select_pdfs"),
            "",
            self.lang_manager.get("dialog_pdf_filter"),
        )

        if file_paths:
            self.add_documents(file_paths)

    def add_documents(self, file_paths):
        """Add documents to the list and project."""
        for path in file_paths:
            if path not in self.documents:
                self.documents.append(path)

                # Add to project if we have one
                if self.current_project:
                    file_path = Path(path)
                    doc_info = DocumentInfo(
                        id=str(uuid.uuid4()),
                        file_path=path,
                        title=file_path.stem,  # Use filename without extension as title
                        file_size=file_path.stat().st_size,
                    )
                    self.current_project.add_document(doc_info)

                # Create list item with file info
                file_path = Path(path)
                file_size = file_path.stat().st_size / 1024  # KB
                item_text = f"{file_path.name} ({file_size:.1f} KB)"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setToolTip(path)
                self.documents_list.addItem(item)

        self.update_input_status()
        self.documents_changed.emit(self.documents)

    def remove_selected(self):
        """Remove selected documents from list and project."""
        selected_items = self.documents_list.selectedItems()
        for item in selected_items:
            path = item.data(Qt.ItemDataRole.UserRole)
            self.documents.remove(path)

            # Remove from project if we have one
            if self.current_project:
                # Find document by file path
                doc = self.current_project.get_document_by_path(path)
                if doc:
                    self.current_project.remove_document(doc.id)

            self.documents_list.takeItem(self.documents_list.row(item))

        self.update_input_status()
        self.documents_changed.emit(self.documents)

    def clear_all(self):
        """Clear all documents from list and project."""
        self.documents = []
        self.documents_list.clear()

        # Clear documents from project if we have one
        if self.current_project:
            # Get all document IDs and remove them
            doc_ids = [doc.id for doc in self.current_project.documents]
            for doc_id in doc_ids:
                self.current_project.remove_document(doc_id)

        self.update_input_status()
        self.documents_changed.emit(self.documents)

    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = len(self.documents_list.selectedItems()) > 0
        self.remove_btn.setEnabled(has_selection)

    def on_process_clicked(self):
        """Handle process button click."""
        self.process_requested.emit(self.documents)

    def update_input_status(self):
        """Update input status label."""
        count = len(self.documents)
        if count == 0:
            self.input_status_label.setText(self.lang_manager.get("status_no_docs"))
            self.process_btn.setEnabled(False)
            self.clear_btn.setEnabled(False)
        else:
            self.input_status_label.setText(self.lang_manager.get("status_n_docs", count))
            self.process_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)

    def refresh_output_files(self):
        """Refresh output files list."""
        self.output_list.clear()

        if not self.output_dir.exists():
            self.update_output_status(0)
            return

        # Get all files in output directory
        files = []
        for ext in ["*.md", "*.docx", "*.pdf"]:
            files.extend(self.output_dir.glob(ext))

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for file_path in files:
            # Get file info
            stat = file_path.stat()
            size = stat.st_size / 1024  # KB
            mod_time = datetime.fromtimestamp(stat.st_mtime)

            # Format item text
            item_text = f"{file_path.name} ({size:.1f} KB) - {mod_time.strftime('%Y-%m-%d %H:%M')}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, str(file_path))
            item.setToolTip(str(file_path))
            self.output_list.addItem(item)

        self.update_output_status(len(files))

    def update_output_status(self, count):
        """Update output status label."""
        if count == 0:
            self.output_status_label.setText(self.lang_manager.get("status_no_output_files"))
            self.delete_all_output_btn.setEnabled(False)
        else:
            self.output_status_label.setText(self.lang_manager.get("status_n_output_files", count))
            self.delete_all_output_btn.setEnabled(True)

    def on_output_selection_changed(self):
        """Handle output selection change."""
        has_selection = len(self.output_list.selectedItems()) > 0
        self.open_btn.setEnabled(has_selection)
        self.delete_output_btn.setEnabled(has_selection)

    def open_selected_file(self):
        """Open selected output file."""
        selected = self.output_list.selectedItems()
        if selected:
            file_path = selected[0].data(Qt.ItemDataRole.UserRole)
            # Open with default application
            if os.name == "posix":  # macOS/Linux
                os.system(f'open "{file_path}"')
            elif os.name == "nt":  # Windows
                os.startfile(file_path)

    def open_output_folder(self):
        """Open output folder in file explorer."""
        if self.output_dir.exists():
            if os.name == "posix":  # macOS/Linux
                os.system(f'open "{self.output_dir}"')
            elif os.name == "nt":  # Windows
                os.startfile(self.output_dir)

    def delete_selected_output(self):
        """Delete selected output file(s)."""
        selected = self.output_list.selectedItems()
        if not selected:
            return

        # Confirm deletion if multiple files selected
        if len(selected) > 1:
            from PyQt6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                self.lang_manager.get("confirm_delete", "Confirm Delete"),
                self.lang_manager.get(
                    "confirm_delete_multiple", "Are you sure you want to delete {0} selected files?"
                ).format(len(selected)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Delete all selected files
        for item in selected:
            file_path = Path(item.data(Qt.ItemDataRole.UserRole))
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")

        self.refresh_output_files()

    def delete_all_outputs(self):
        """Delete all output files."""
        if self.output_list.count() == 0:
            return

        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            self.lang_manager.get("confirm_delete_all", "Confirm Delete All"),
            self.lang_manager.get(
                "confirm_delete_all_msg", "Are you sure you want to delete ALL {0} generated files?"
            ).format(self.output_list.count()),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete all files in output directory
        if self.output_dir.exists():
            for file_path in self.output_dir.glob("*"):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        logger.error(f"Failed to delete {file_path}: {e}")

        self.refresh_output_files()

    def get_documents(self):
        """Get list of document paths."""
        return self.documents

    def get_selected_documents(self):
        """Get list of currently selected document paths."""
        selected_items = self.documents_list.selectedItems()
        return [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]

    def set_process_enabled(self, enabled):
        """Enable/disable process button."""
        self.process_btn.setEnabled(enabled and len(self.documents) > 0)
