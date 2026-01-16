"""URL Import Dialog for importing documents from web URLs."""

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from docprocessor.core.task_base import TaskStatus
from docprocessor.core.tasks.url_import_task import URLImportTask
from docprocessor.gui.styles import Colors, Styles
from docprocessor.utils.language_manager import get_language_manager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class URLImportWorker(QThread):
    """Worker thread for URL import task."""

    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(object)  # result
    error = pyqtSignal(str)  # error_message

    def __init__(self, urls, config):
        super().__init__()
        self.urls = urls
        self.config = config
        self.task = URLImportTask()

    def run(self):
        """Execute URL import task."""
        try:
            result = self.task.execute(
                inputs=self.urls,
                config=self.config,
                progress_callback=lambda p, m: self.progress.emit(p, m),
            )
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"URL import error: {e}")
            self.error.emit(str(e))


class URLImportDialog(QDialog):
    """Dialog for importing documents from URLs."""

    # Signal emitted when documents are imported
    documents_imported = pyqtSignal(list)  # list of imported document dicts

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.worker = None
        self.imported_docs = []

        self.setWindowTitle(self.lang_manager.get("dialog_url_import", "Import from URL"))
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel(
            self.lang_manager.get(
                "url_import_instructions",
                "Enter URLs to import (one per line). Supports PDF, HTML pages, and text files.",
            )
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(Styles.INFO_BOX)
        layout.addWidget(instructions)

        # URL input section
        url_group = self.create_url_input_section()
        layout.addWidget(url_group)

        # Settings section
        settings_group = self.create_settings_section()
        layout.addWidget(settings_group)

        # Progress section
        progress_group = self.create_progress_section()
        layout.addWidget(progress_group)

        # Results section
        results_group = self.create_results_section()
        layout.addWidget(results_group)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def create_url_input_section(self):
        """Create URL input section."""
        group = QGroupBox(self.lang_manager.get("section_urls", "URLs"))
        layout = QVBoxLayout(group)

        # URL text area
        self.url_text = QTextEdit()
        self.url_text.setPlaceholderText(
            "https://example.com/document.pdf\n"
            "https://example.org/article.html\n"
            "https://example.net/data.txt"
        )
        self.url_text.setMaximumHeight(120)
        self.url_text.setStyleSheet(Styles.TEXT_EDIT_CODE)
        layout.addWidget(self.url_text)

        # Quick add section
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel(self.lang_manager.get("label_quick_add", "Quick add") + ":"))

        self.quick_url_edit = QLineEdit()
        self.quick_url_edit.setPlaceholderText("https://...")
        self.quick_url_edit.returnPressed.connect(self.add_quick_url)
        self.quick_url_edit.setStyleSheet(Styles.LINE_EDIT)
        quick_layout.addWidget(self.quick_url_edit)

        add_btn = QPushButton(self.lang_manager.get("btn_add", "Add"))
        add_btn.setStyleSheet(Styles.BUTTON_SMALL)
        add_btn.clicked.connect(self.add_quick_url)
        quick_layout.addWidget(add_btn)

        layout.addLayout(quick_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.import_btn = QPushButton(self.lang_manager.get("btn_import", "Import"))
        self.import_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.import_btn.clicked.connect(self.start_import)
        button_layout.addWidget(self.import_btn)

        self.clear_btn = QPushButton(self.lang_manager.get("btn_clear_all", "Clear"))
        self.clear_btn.setStyleSheet(Styles.BUTTON_SECONDARY)
        self.clear_btn.clicked.connect(self.url_text.clear)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return group

    def create_settings_section(self):
        """Create settings section."""
        group = QGroupBox(self.lang_manager.get("section_settings", "Settings"))
        layout = QFormLayout(group)

        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" s")
        layout.addRow(self.lang_manager.get("label_timeout", "Timeout") + ":", self.timeout_spin)

        # Convert HTML checkbox
        self.convert_html_check = QCheckBox(
            self.lang_manager.get("label_convert_html", "Convert HTML pages to text")
        )
        self.convert_html_check.setChecked(True)
        layout.addRow("", self.convert_html_check)

        # Verify SSL checkbox
        self.verify_ssl_check = QCheckBox(
            self.lang_manager.get("label_verify_ssl", "Verify SSL certificates")
        )
        self.verify_ssl_check.setChecked(True)
        layout.addRow("", self.verify_ssl_check)

        return group

    def create_progress_section(self):
        """Create progress display section."""
        group = QGroupBox(self.lang_manager.get("section_progress", "Progress"))
        layout = QVBoxLayout(group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(Styles.PROGRESS_BAR)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(self.lang_manager.get("status_ready", "Ready to import"))
        self.status_label.setStyleSheet(Styles.LABEL_SECONDARY)
        layout.addWidget(self.status_label)

        return group

    def create_results_section(self):
        """Create results display section."""
        group = QGroupBox(self.lang_manager.get("section_results", "Results"))
        layout = QVBoxLayout(group)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(150)
        self.results_list.setStyleSheet(Styles.LIST_WIDGET)
        layout.addWidget(self.results_list)

        # Summary label
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(Styles.LABEL_SECONDARY)
        layout.addWidget(self.summary_label)

        return group

    def add_quick_url(self):
        """Add URL from quick add field."""
        url = self.quick_url_edit.text().strip()
        if url:
            current_text = self.url_text.toPlainText().strip()
            if current_text:
                self.url_text.setPlainText(current_text + "\n" + url)
            else:
                self.url_text.setPlainText(url)
            self.quick_url_edit.clear()

    def get_urls(self):
        """Get list of URLs from input."""
        text = self.url_text.toPlainText().strip()
        if not text:
            return []

        urls = [line.strip() for line in text.split("\n") if line.strip()]
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        return unique_urls

    def start_import(self):
        """Start URL import process."""
        urls = self.get_urls()

        if not urls:
            QMessageBox.warning(
                self,
                self.lang_manager.get("warning", "Warning"),
                self.lang_manager.get("warning_no_urls", "Please enter at least one URL."),
            )
            return

        # Create config
        task = URLImportTask()
        config = task.get_default_config()
        config.set("timeout", self.timeout_spin.value())
        config.set("convert_html", self.convert_html_check.isChecked())
        config.set("verify_ssl", self.verify_ssl_check.isChecked())

        # Validate URLs first
        is_valid, error_msg = task.validate_inputs(urls)
        if not is_valid:
            QMessageBox.critical(self, self.lang_manager.get("error", "Error"), error_msg)
            return

        # Disable UI during import
        self.import_btn.setEnabled(False)
        self.url_text.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_list.clear()
        self.summary_label.clear()

        # Start worker
        self.worker = URLImportWorker(urls, config)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

        logger.info(f"Starting URL import for {len(urls)} URLs")

    def on_progress(self, percent, message):
        """Handle progress update."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def on_finished(self, result):
        """Handle import completion."""
        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)
        self.url_text.setEnabled(True)
        self.clear_btn.setEnabled(True)

        # Display results
        success_count = result.output_data.get("success_count", 0)
        failure_count = result.output_data.get("failure_count", 0)
        imported = result.output_data.get("imported", [])
        failed = result.output_data.get("failed", [])

        # Add successful imports to list
        for doc in imported:
            item = QListWidgetItem(f"[OK] {doc['title']} ({doc['content_type']})")
            item.setForeground(Qt.GlobalColor.darkGreen)
            self.results_list.addItem(item)

        # Add failed imports to list
        for fail in failed:
            item = QListWidgetItem(f"[FAIL] {fail['url']}: {fail['error'][:50]}")
            item.setForeground(Qt.GlobalColor.red)
            self.results_list.addItem(item)

        # Update summary
        if result.status == TaskStatus.COMPLETED:
            self.status_label.setText(
                self.lang_manager.get("status_import_complete", "Import complete!")
            )
            self.status_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: bold;")

            summary = self.lang_manager.get(
                "summary_import_success", "Successfully imported {0} document(s)."
            ).format(success_count)

            if failure_count > 0:
                summary += " " + self.lang_manager.get(
                    "summary_import_partial", "{0} URL(s) failed."
                ).format(failure_count)

            self.summary_label.setText(summary)

            # Store imported docs
            self.imported_docs = imported

            # Show success message
            QMessageBox.information(self, self.lang_manager.get("success", "Success"), summary)

        else:
            self.status_label.setText(
                self.lang_manager.get("status_import_failed", "Import failed")
            )
            self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-weight: bold;")

            self.summary_label.setText(result.error_message or "Unknown error")

        # Emit signal with imported documents
        if imported:
            self.documents_imported.emit(imported)

        logger.info(f"URL import finished: {success_count} success, {failure_count} failed")

    def on_error(self, error_message):
        """Handle import error."""
        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)
        self.url_text.setEnabled(True)
        self.clear_btn.setEnabled(True)

        self.status_label.setText(self.lang_manager.get("status_error", "Error"))
        self.status_label.setStyleSheet(f"color: {Colors.ERROR}; font-weight: bold;")

        QMessageBox.critical(
            self,
            self.lang_manager.get("error", "Error"),
            self.lang_manager.get("error_import_failed", "Import failed") + f":\n{error_message}",
        )

        logger.error(f"URL import error: {error_message}")
