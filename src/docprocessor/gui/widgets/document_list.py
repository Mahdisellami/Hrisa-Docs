"""Document list widget."""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from docprocessor.utils.language_manager import get_language_manager


class DocumentListWidget(QWidget):
    """Widget for displaying and managing documents."""

    documents_changed = pyqtSignal(list)  # Emitted when document list changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.documents = []
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(self.lang_manager.get("tab_documents"))
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Document list
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton(self.lang_manager.get("btn_add"))
        self.add_btn.setToolTip(self.lang_manager.get("tooltip_add_docs"))
        button_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton(self.lang_manager.get("btn_remove"))
        self.remove_btn.setToolTip(self.lang_manager.get("tooltip_remove_doc"))
        self.remove_btn.setEnabled(False)
        button_layout.addWidget(self.remove_btn)

        self.clear_btn = QPushButton(self.lang_manager.get("btn_clear_all"))
        self.clear_btn.setToolTip(self.lang_manager.get("tooltip_clear_all"))
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel(self.lang_manager.get("status_no_docs"))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        # Connect signals
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.clear_btn.clicked.connect(self.clear_all)

    def add_documents(self, file_paths):
        """Add documents to the list."""
        for path in file_paths:
            if path not in self.documents:
                self.documents.append(path)
                item = QListWidgetItem(Path(path).name)
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setToolTip(path)
                self.list_widget.addItem(item)

        self.update_status()
        self.documents_changed.emit(self.documents)

    def remove_selected(self):
        """Remove selected document."""
        current = self.list_widget.currentItem()
        if current:
            path = current.data(Qt.ItemDataRole.UserRole)
            self.documents.remove(path)
            self.list_widget.takeItem(self.list_widget.row(current))
            self.update_status()
            self.documents_changed.emit(self.documents)

    def clear_all(self):
        """Clear all documents."""
        self.documents.clear()
        self.list_widget.clear()
        self.update_status()
        self.documents_changed.emit(self.documents)

    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = self.list_widget.currentItem() is not None
        self.remove_btn.setEnabled(has_selection)

    def update_status(self):
        """Update status label."""
        count = len(self.documents)
        if count == 0:
            self.status_label.setText(self.lang_manager.get("status_no_docs"))
            self.clear_btn.setEnabled(False)
        else:
            self.status_label.setText(self.lang_manager.get("status_n_docs", count))
            self.clear_btn.setEnabled(True)

    def get_documents(self):
        """Get list of document paths."""
        return self.documents.copy()
