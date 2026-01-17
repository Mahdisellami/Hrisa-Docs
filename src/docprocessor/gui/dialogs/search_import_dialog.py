"""Search & Import Dialog for searching and importing documents from research sources."""

from datetime import datetime

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from docprocessor.core.task_base import TaskConfig, TaskStatus
from docprocessor.core.tasks.search_import_task import SearchImportTask
from docprocessor.core.tasks.url_import_task import URLImportTask
from docprocessor.gui.styles import Colors, Styles
from docprocessor.models.project import SearchResult
from docprocessor.utils.language_manager import get_language_manager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class SearchWorker(QThread):
    """Worker thread for search task."""

    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(object)  # result
    error = pyqtSignal(str)  # error_message

    def __init__(self, queries, config):
        super().__init__()
        self.queries = queries
        self.config = config
        self.task = SearchImportTask()

    def run(self):
        """Execute search task."""
        try:
            result = self.task.execute(
                inputs=self.queries,
                config=self.config,
                progress_callback=lambda p, m: self.progress.emit(p, m),
            )
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.error.emit(str(e))


class ImportWorker(QThread):
    """Worker thread for importing selected results."""

    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(list)  # imported documents
    error = pyqtSignal(str)  # error_message

    def __init__(self, urls, config):
        super().__init__()
        self.urls = urls
        self.config = config
        self.task = URLImportTask()

    def run(self):
        """Execute import task."""
        try:
            result = self.task.execute(
                inputs=self.urls,
                config=self.config,
                progress_callback=lambda p, m: self.progress.emit(p, m),
            )
            if result.status == TaskStatus.COMPLETED:
                self.finished.emit(result.output_data.get("imported", []))
            else:
                self.error.emit(result.error_message or "Import failed")
        except Exception as e:
            logger.error(f"Import error: {e}")
            self.error.emit(str(e))


class CredentialsLoaderWorker(QThread):
    """Worker thread for loading credentials from keyring without blocking UI."""

    credentials_loaded = pyqtSignal(str, str)  # api_key, engine_id
    loading_failed = pyqtSignal()  # No credentials or error

    def run(self):
        """Load credentials in background thread."""
        try:
            from docprocessor.utils.credentials_manager import get_credentials_manager

            creds_manager = get_credentials_manager()

            # Check if keyring is available (can block, but we're in background thread)
            if not creds_manager.is_keyring_available():
                logger.debug("Keyring not available")
                self.loading_failed.emit()
                return

            # Load credentials (can block, but we're in background thread)
            credentials = creds_manager.load_google_credentials()

            if credentials:
                api_key, engine_id = credentials
                self.credentials_loaded.emit(api_key, engine_id)
                logger.info("Loaded saved Google API credentials")
            else:
                self.loading_failed.emit()
        except Exception as e:
            logger.warning(f"Could not load saved credentials: {e}")
            self.loading_failed.emit()


class SearchImportDialog(QDialog):
    """Dialog for searching and importing documents from research sources."""

    # Signal emitted when documents are imported
    documents_imported = pyqtSignal(list)  # list of imported document dicts

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.search_worker = None
        self.import_worker = None
        self.credentials_loader_worker = None
        self.search_results = []  # List of SearchResult objects

        self.setWindowTitle(
            self.lang_manager.get("dialog_search_import", "Search & Import from Research Sources")
        )
        self.setMinimumWidth(800)
        self.setMinimumHeight(950)

        self.setup_ui()

        # Start background thread to load credentials (won't block UI)
        self.load_saved_credentials()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel(
            self.lang_manager.get(
                "search_instructions",
                "Enter keywords to search government and legal databases. "
                "Results will be displayed below for review before importing.",
            )
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(Styles.INFO_BOX)
        layout.addWidget(instructions)

        # Query input section
        query_group = self.create_query_section()
        layout.addWidget(query_group)

        # Settings section
        settings_group = self.create_settings_section()
        layout.addWidget(settings_group)

        # Progress section
        progress_group = self.create_progress_section()
        layout.addWidget(progress_group)

        # Results section
        results_group = self.create_results_section()
        layout.addWidget(results_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.search_button = QPushButton(
            self.lang_manager.get("search_button", "Search")
        )
        self.search_button.clicked.connect(self.start_search)
        self.search_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        button_layout.addWidget(self.search_button)

        self.import_button = QPushButton(
            self.lang_manager.get("import_selected_button", "Import Selected")
        )
        self.import_button.clicked.connect(self.import_selected)
        self.import_button.setEnabled(False)
        button_layout.addWidget(self.import_button)

        self.close_button = QPushButton(self.lang_manager.get("close", "Close"))
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def create_query_section(self):
        """Create search query input section."""
        group = QGroupBox(self.lang_manager.get("search_query_label", "Search Query"))
        layout = QVBoxLayout()

        # Query input
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText(
            "Example: BEPS transfer pricing\nExample: économie circulaire\n"
            "Example: finances durables"
        )
        self.query_input.setMaximumHeight(100)
        self.query_input.setStyleSheet(Styles.TEXT_EDIT)
        layout.addWidget(self.query_input)

        # Quick add
        quick_layout = QHBoxLayout()
        self.quick_query = QLineEdit()
        self.quick_query.setPlaceholderText(
            self.lang_manager.get("quick_add_placeholder", "Quick add...")
        )
        self.quick_query.setStyleSheet(Styles.LINE_EDIT)
        self.quick_query.returnPressed.connect(self.quick_add_query)
        quick_layout.addWidget(self.quick_query)

        add_btn = QPushButton(self.lang_manager.get("add_button", "Add"))
        add_btn.clicked.connect(self.quick_add_query)
        quick_layout.addWidget(add_btn)

        clear_btn = QPushButton(self.lang_manager.get("clear_button", "Clear"))
        clear_btn.clicked.connect(lambda: self.query_input.clear())
        quick_layout.addWidget(clear_btn)

        layout.addLayout(quick_layout)

        # Search history section
        history_label = QLabel(self.lang_manager.get("recent_searches", "Recent Searches:"))
        history_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(history_label)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)
        self.history_list.setStyleSheet(Styles.LIST_WIDGET)
        self.history_list.itemClicked.connect(self.load_from_history)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_history_context_menu)
        layout.addWidget(self.history_list)

        # Clear history button
        clear_history_btn = QPushButton(self.lang_manager.get("clear_history", "Clear History"))
        clear_history_btn.clicked.connect(self.clear_history)
        clear_history_btn.setStyleSheet(Styles.BUTTON_SECONDARY)
        layout.addWidget(clear_history_btn)

        # Load history
        self.load_history()

        group.setLayout(layout)
        return group

    def create_settings_section(self):
        """Create settings section."""
        group = QGroupBox(self.lang_manager.get("search_settings_label", "Search Settings"))
        layout = QFormLayout()

        # Max results
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(1, 50)
        self.max_results_spin.setValue(10)
        self.max_results_spin.setStyleSheet(Styles.SPIN_BOX)
        layout.addRow(
            self.lang_manager.get("max_results_label", "Max results per query:"),
            self.max_results_spin,
        )

        # Search Strategy
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Auto (Recommended)", "Google Only", "Native Only"])
        self.strategy_combo.setCurrentIndex(1)  # Default to "Google Only" for backward compatibility
        self.strategy_combo.setStyleSheet(Styles.COMBO_BOX)
        self.strategy_combo.setToolTip(
            "Auto: Try native search first, fallback to Google\n"
            "Google Only: Always use Google API\n"
            "Native Only: Use only native handlers (for testing)"
        )
        layout.addRow(
            self.lang_manager.get("search_strategy_label", "Search Strategy:"),
            self.strategy_combo,
        )

        # Google API Key (collapsible/optional)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter Google Custom Search API key...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setStyleSheet(Styles.LINE_EDIT)
        layout.addRow(
            self.lang_manager.get("google_api_key_label", "Google API Key:"),
            self.api_key_input,
        )

        # Search Engine ID
        self.search_engine_id_input = QLineEdit()
        self.search_engine_id_input.setPlaceholderText("Enter Search Engine ID...")
        self.search_engine_id_input.setStyleSheet(Styles.LINE_EDIT)
        layout.addRow(
            self.lang_manager.get("search_engine_id_label", "Search Engine ID:"),
            self.search_engine_id_input,
        )

        # Help text
        help_label = QLabel(
            '<a href="https://console.cloud.google.com/">Get API Key</a> | '
            '<a href="https://programmablesearchengine.google.com/">Create Search Engine</a>'
        )
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addRow("", help_label)

        # Remember credentials checkbox
        self.remember_credentials_checkbox = QCheckBox(
            self.lang_manager.get(
                "remember_credentials", "Remember credentials (secure)"
            )
        )
        self.remember_credentials_checkbox.setToolTip(
            "Store credentials securely in your system's keyring "
            "(macOS Keychain, Windows Credential Manager)"
        )
        layout.addRow("", self.remember_credentials_checkbox)

        # Clear credentials button
        clear_creds_btn = QPushButton(
            self.lang_manager.get("clear_credentials", "Clear Saved Credentials")
        )
        clear_creds_btn.clicked.connect(self.clear_credentials)
        clear_creds_btn.setStyleSheet(Styles.BUTTON_SECONDARY)
        layout.addRow("", clear_creds_btn)

        # Source Selection (Optional - enables native handlers)
        source_group = QGroupBox(
            self.lang_manager.get("source_selection_label", "Sources (Optional)")
        )
        source_layout = QVBoxLayout()

        # Info label
        info_label = QLabel(
            self.lang_manager.get(
                "source_selection_info",
                "Select specific sources for native search. "
                "Leave unchecked to search all sources via Google."
            )
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        source_layout.addWidget(info_label)

        # data.gov.tn checkbox (only native handler available)
        self.source_data_gov_tn = QCheckBox("data.gov.tn")
        self.source_data_gov_tn.setToolTip(
            "Tunisian open data portal (uses native CKAN API)"
        )
        source_layout.addWidget(self.source_data_gov_tn)

        # "Other sources" label (via Google)
        other_label = QLabel(
            self.lang_manager.get(
                "other_sources_label",
                "Other sources will be searched via Google API"
            )
        )
        other_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        source_layout.addWidget(other_label)

        source_group.setLayout(source_layout)
        layout.addRow("", source_group)

        group.setLayout(layout)
        return group

    def create_progress_section(self):
        """Create progress section."""
        group = QGroupBox(self.lang_manager.get("progress_label", "Progress"))
        layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(Styles.PROGRESS_BAR)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        group.setLayout(layout)
        return group

    def create_results_section(self):
        """Create results display section."""
        group = QGroupBox(self.lang_manager.get("results_label", "Search Results"))
        layout = QVBoxLayout()

        # Results tree (grouped by source)
        self.results_tree = QTreeWidget()
        self.results_tree.setColumnCount(4)
        self.results_tree.setHeaderLabels(["Title", "Source", "Type", "Handler"])
        self.results_tree.header().setStretchLastSection(False)
        self.results_tree.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self.results_tree.setStyleSheet(Styles.TABLE_WIDGET)  # Reuse table style for now
        self.results_tree.itemChanged.connect(self.on_tree_item_changed)
        layout.addWidget(self.results_tree)

        # Summary
        self.results_summary = QLabel("")
        self.results_summary.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.results_summary)

        group.setLayout(layout)
        return group

    def quick_add_query(self):
        """Add query from quick input to main text area."""
        query = self.quick_query.text().strip()
        if query:
            current = self.query_input.toPlainText()
            if current:
                self.query_input.setPlainText(current + "\n" + query)
            else:
                self.query_input.setPlainText(query)
            self.quick_query.clear()

    def start_search(self):
        """Start search operation."""
        # Get queries
        queries = [
            q.strip()
            for q in self.query_input.toPlainText().split("\n")
            if q.strip()
        ]

        if not queries:
            QMessageBox.warning(
                self,
                self.lang_manager.get("warning"),
                self.lang_manager.get("no_queries_warning", "Please enter at least one search query."),
            )
            return

        # Get search strategy and sources
        api_key = self.api_key_input.text().strip()
        search_engine_id = self.search_engine_id_input.text().strip()

        strategy_index = self.strategy_combo.currentIndex()
        sources = []
        if self.source_data_gov_tn.isChecked():
            sources.append("data.gov.tn")

        # Google API required unless using native-only with sources selected
        needs_google_api = strategy_index != 2 or not sources

        if needs_google_api and (not api_key or not search_engine_id):
            QMessageBox.warning(
                self,
                self.lang_manager.get("warning"),
                self.lang_manager.get(
                    "api_key_required_conditional",
                    "Google API Key and Search Engine ID are required for this search strategy.\n\n"
                    "To search without Google API, select 'Native Only' strategy and check data.gov.tn."
                ),
            )
            return

        # Build config
        config = TaskConfig()
        config.set("max_results_per_query", self.max_results_spin.value())
        config.set("google_api_key", api_key)
        config.set("google_search_engine_id", search_engine_id)

        # Get search strategy from combo box
        strategy_map = {
            0: "auto",      # Auto (Recommended)
            1: "google",    # Google Only
            2: "native",    # Native Only
        }
        config.set("search_strategy", strategy_map[strategy_index])
        config.set("sources", sources)

        # Log the configuration for debugging
        logger.info(f"Search strategy: {config.get('search_strategy')}")
        logger.info(f"Selected sources: {sources}")

        # Save credentials if checkbox is checked
        if self.remember_credentials_checkbox.isChecked() and api_key and search_engine_id:
            from docprocessor.utils.credentials_manager import get_credentials_manager

            creds_manager = get_credentials_manager()
            if creds_manager.save_google_credentials(api_key, search_engine_id):
                logger.info("Saved Google API credentials securely")
            else:
                logger.warning("Failed to save credentials - keyring may be unavailable")

        # Disable UI
        self.search_button.setEnabled(False)
        self.import_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Searching...")

        # Clear previous results
        self.results_tree.clear()
        self.search_results = []

        # Start search worker
        self.search_worker = SearchWorker(queries, config)
        self.search_worker.progress.connect(self.on_search_progress)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.start()

    def on_search_progress(self, percent, message):
        """Handle search progress updates."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def on_search_finished(self, result):
        """Handle search completion."""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)

        if result.status == TaskStatus.COMPLETED or result.status == TaskStatus.FAILED:
            # Parse results
            results_data = result.output_data.get("results", [])
            self.search_results = [SearchResult.from_dict(r) for r in results_data]

            # Display results
            self.display_results(self.search_results)

            # Update summary
            count = len(self.search_results)
            self.results_summary.setText(
                self.lang_manager.get("results_count", "Found {} results").format(count)
            )

            if count > 0:
                self.import_button.setEnabled(True)
                self.status_label.setText("Search complete. Select results to import.")
            else:
                self.status_label.setText("No results found.")

            # Save to history (only if results found)
            if count > 0:
                from docprocessor.utils.user_preferences import get_user_preferences_manager

                prefs_manager = get_user_preferences_manager()

                # Determine handler used
                handlers_used = set(
                    r.metadata.get("handler_used", "unknown") for r in self.search_results
                )
                handler_str = "mixed" if len(handlers_used) > 1 else list(handlers_used)[0]

                # Get original config
                sources = []
                if self.source_data_gov_tn.isChecked():
                    sources.append("data.gov.tn")

                strategy_map = {0: "auto", 1: "google", 2: "native"}
                strategy = strategy_map[self.strategy_combo.currentIndex()]

                # Get first query (if multiple were entered)
                first_query = self.query_input.toPlainText().split("\n")[0].strip()

                prefs_manager.add_search_history_entry(
                    query=first_query,
                    sources=sources,
                    strategy=strategy,
                    result_count=count,
                    handler_used=handler_str,
                )

                self.load_history()  # Refresh display

            # Show any errors
            if result.error_message:
                QMessageBox.warning(self, "Search Warning", result.error_message)

    def on_search_error(self, error_message):
        """Handle search error."""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        self.status_label.setText("Search failed")

        QMessageBox.critical(
            self,
            self.lang_manager.get("error"),
            f"Search failed: {error_message}",
        )

    def display_results(self, results):
        """Display search results in grouped tree view."""
        self.results_tree.clear()
        result_groups = self.group_results_by_source(results)

        # Sort sources by result count (descending)
        sorted_sources = sorted(
            result_groups.items(), key=lambda x: len(x[1]), reverse=True
        )

        for source_name, source_results in sorted_sources:
            # Create top-level group item
            group_item = QTreeWidgetItem(self.results_tree)
            group_item.setText(0, f"{source_name} ({len(source_results)} results)")
            group_item.setFlags(
                group_item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsAutoTristate
            )
            group_item.setCheckState(0, Qt.CheckState.Checked)  # Select all by default

            # Style group header
            font = group_item.font(0)
            font.setBold(True)
            group_item.setFont(0, font)
            # Light background with white text (default) removed - caused white on white issue

            # Add child items for each result
            for result in source_results:
                child_item = QTreeWidgetItem(group_item)
                child_item.setFlags(child_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child_item.setCheckState(0, Qt.CheckState.Checked)

                # Store result reference
                child_item.setData(0, Qt.ItemDataRole.UserRole, result)

                # Column 0: Title
                title_text = (
                    result.title[:60] + "..." if len(result.title) > 60 else result.title
                )
                child_item.setText(0, title_text)
                child_item.setToolTip(0, f"{result.title}\n\n{result.snippet}")

                # Column 1: Source
                child_item.setText(1, result.source_name)

                # Column 2: Type
                child_item.setText(2, result.file_type.upper())

                # Column 3: Handler indicator
                handler_used = result.metadata.get("handler_used", "unknown")
                handler_label = self.create_handler_label(handler_used)
                child_item.setText(3, handler_label)
                child_item.setForeground(3, self.get_handler_color(handler_used))

            # Expand group
            group_item.setExpanded(True)

        # Resize columns
        for i in range(4):
            self.results_tree.resizeColumnToContents(i)

    def import_selected(self):
        """Import selected search results from tree."""
        selected_urls = []

        # Iterate through tree structure
        root = self.results_tree.invisibleRootItem()
        for group_idx in range(root.childCount()):
            group_item = root.child(group_idx)

            for child_idx in range(group_item.childCount()):
                child_item = group_item.child(child_idx)

                if child_item.checkState(0) == Qt.CheckState.Checked:
                    result = child_item.data(0, Qt.ItemDataRole.UserRole)
                    selected_urls.append(result.url)

        if not selected_urls:
            QMessageBox.warning(
                self,
                self.lang_manager.get("warning"),
                self.lang_manager.get(
                    "no_selection_warning", "Please select at least one result to import."
                ),
            )
            return

        # Build import config (reuse URLImportTask config)
        config = TaskConfig()
        config.set("timeout", 30)
        config.set("verify_ssl", True)
        config.set("max_file_size", 50 * 1024 * 1024)

        # Disable UI
        self.search_button.setEnabled(False)
        self.import_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Importing documents...")

        # Start import worker
        self.import_worker = ImportWorker(selected_urls, config)
        self.import_worker.progress.connect(self.on_import_progress)
        self.import_worker.finished.connect(self.on_import_finished)
        self.import_worker.error.connect(self.on_import_error)
        self.import_worker.start()

    def on_import_progress(self, percent, message):
        """Handle import progress updates."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def on_import_finished(self, imported_docs):
        """Handle import completion."""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        self.import_button.setEnabled(True)
        self.status_label.setText(f"Imported {len(imported_docs)} documents successfully.")

        # Emit signal
        self.documents_imported.emit(imported_docs)

        # Show success message
        QMessageBox.information(
            self,
            self.lang_manager.get("success"),
            self.lang_manager.get("import_success").format(len(imported_docs)),
        )

        # Close dialog
        self.accept()

    def on_import_error(self, error_message):
        """Handle import error."""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)
        self.import_button.setEnabled(True)
        self.status_label.setText("Import failed")

        QMessageBox.critical(
            self,
            self.lang_manager.get("error"),
            f"Import failed: {error_message}",
        )

    def load_saved_credentials(self):
        """Load saved credentials from keyring using background thread.

        This method starts a background thread to avoid blocking the UI,
        especially on Linux where keyring access may require user interaction
        or may not be available at all.
        """
        # Clean up any existing worker
        if self.credentials_loader_worker is not None:
            self.credentials_loader_worker.quit()
            self.credentials_loader_worker.wait()

        # Create and start background worker
        self.credentials_loader_worker = CredentialsLoaderWorker()
        self.credentials_loader_worker.credentials_loaded.connect(self.on_credentials_loaded)
        self.credentials_loader_worker.loading_failed.connect(self.on_credentials_loading_failed)
        self.credentials_loader_worker.finished.connect(
            lambda: self.credentials_loader_worker.deleteLater()
        )
        self.credentials_loader_worker.start()
        logger.debug("Started background thread to load credentials")

    def on_credentials_loaded(self, api_key: str, engine_id: str):
        """Handle successfully loaded credentials from background thread."""
        self.api_key_input.setText(api_key)
        self.search_engine_id_input.setText(engine_id)
        self.remember_credentials_checkbox.setChecked(True)
        logger.debug("Applied loaded credentials to UI")

    def on_credentials_loading_failed(self):
        """Handle failed credential loading (no credentials or error)."""
        logger.debug("No saved credentials available or keyring unavailable")

    def clear_credentials(self):
        """Clear saved credentials from keyring."""
        from docprocessor.utils.credentials_manager import get_credentials_manager

        reply = QMessageBox.question(
            self,
            self.lang_manager.get("confirm", "Confirm"),
            self.lang_manager.get(
                "confirm_clear_credentials",
                "Are you sure you want to clear saved credentials?",
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            creds_manager = get_credentials_manager()
            if creds_manager.clear_google_credentials():
                self.api_key_input.clear()
                self.search_engine_id_input.clear()
                self.remember_credentials_checkbox.setChecked(False)
                QMessageBox.information(
                    self,
                    self.lang_manager.get("success", "Success"),
                    self.lang_manager.get(
                        "credentials_cleared", "Credentials cleared successfully"
                    ),
                )

    def load_history(self):
        """Load search history into list widget."""
        from docprocessor.utils.user_preferences import get_user_preferences_manager

        prefs_manager = get_user_preferences_manager()
        history = prefs_manager.get_search_history()

        self.history_list.clear()
        for entry in history:
            # Format: "query - 10 results (data.gov.tn) - 2h ago"
            timestamp = datetime.fromisoformat(entry.timestamp)
            time_ago = self.format_time_ago(timestamp)

            sources_str = ", ".join(entry.sources) if entry.sources else "all sources"
            label = f"{entry.query[:40]} - {entry.result_count} results ({sources_str}) - {time_ago}"

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, entry)  # Store full entry
            self.history_list.addItem(item)

    def format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as relative time."""
        now = datetime.now()
        delta = now - timestamp

        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600}h ago"
        elif delta.seconds >= 60:
            return f"{delta.seconds // 60}m ago"
        else:
            return "just now"

    def load_from_history(self, item):
        """Load search parameters from history entry."""
        entry = item.data(Qt.ItemDataRole.UserRole)

        # Populate query
        self.query_input.setPlainText(entry.query)

        # Set strategy
        strategy_map = {"auto": 0, "google": 1, "native": 2}
        self.strategy_combo.setCurrentIndex(strategy_map.get(entry.strategy, 1))

        # Set sources
        self.source_data_gov_tn.setChecked("data.gov.tn" in entry.sources)

        logger.info(f"Loaded search from history: {entry.query}")

    def show_history_context_menu(self, position):
        """Show context menu for history item."""
        item = self.history_list.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        remove_action = menu.addAction(
            self.lang_manager.get("remove_from_history", "Remove")
        )

        action = menu.exec(self.history_list.mapToGlobal(position))
        if action == remove_action:
            row = self.history_list.row(item)
            self.remove_history_entry(row)

    def remove_history_entry(self, index: int):
        """Remove entry from history."""
        from docprocessor.utils.user_preferences import get_user_preferences_manager

        prefs_manager = get_user_preferences_manager()
        if prefs_manager.remove_search_history_entry(index):
            self.load_history()  # Refresh display

    def clear_history(self):
        """Clear all search history."""
        from docprocessor.utils.user_preferences import get_user_preferences_manager

        reply = QMessageBox.question(
            self,
            self.lang_manager.get("confirm", "Confirm"),
            self.lang_manager.get(
                "confirm_clear_history",
                "Are you sure you want to clear search history?",
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            prefs_manager = get_user_preferences_manager()
            if prefs_manager.clear_search_history():
                self.load_history()
                QMessageBox.information(
                    self,
                    self.lang_manager.get("success", "Success"),
                    self.lang_manager.get("history_cleared", "History cleared"),
                )

    def group_results_by_source(self, results):
        """Group search results by source domain."""
        from collections import defaultdict

        groups = defaultdict(list)
        for result in results:
            groups[result.source_name].append(result)

        # Sort each group by relevance score (descending)
        for source in groups:
            groups[source].sort(key=lambda r: r.relevance_score, reverse=True)

        return dict(groups)

    def create_handler_label(self, handler_name: str) -> str:
        """Create display label for handler."""
        handler_map = {
            "google": "🔎 Google",
            "ckan": "🔍 CKAN",
            "unknown": "? Unknown",
        }
        return handler_map.get(handler_name, f"? {handler_name}")

    def get_handler_color(self, handler_name: str) -> QColor:
        """Get color for handler indicator."""
        color_map = {
            "ckan": QColor("#2ecc71"),  # Green - native
            "google": QColor("#3498db"),  # Blue - API fallback
            "unknown": QColor("#95a5a6"),  # Gray - unknown
        }
        return color_map.get(handler_name, QColor("#000000"))

    def on_tree_item_changed(self, item, column):
        """Handle tree item check state changes."""
        # Block signals to prevent recursion
        self.results_tree.blockSignals(True)

        # If parent item, update all children
        if item.parent() is None:  # Top-level group
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, check_state)

        self.results_tree.blockSignals(False)
