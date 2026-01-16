"""Main window for Hrisa Docs GUI."""

import os

# Optional: Set to '1' to disable model version checks if no internet available
# By default, allows version checks but NEVER sends user data
if os.getenv("OFFLINE_MODE", "0") == "1":
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_OFFLINE"] = "1"

import shutil
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from docprocessor.core.project_manager import get_project_manager
from docprocessor.gui.dialogs import ProjectSettingsDialog
from docprocessor.gui.widgets import (
    FilesWidget,
    ProjectDashboard,
    SynthesisConfigWidget,
    ThemeEditorWidget,
)
from docprocessor.gui.widgets.figure_extraction_widget import FigureExtractionWidget
from docprocessor.gui.workers import (
    DocumentProcessingWorker,
    FigureExtractionWorker,
    SynthesisWorker,
    ThemeDiscoveryWorker,
)
from docprocessor.utils.language_manager import get_language_manager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessorWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Load user preferences and apply theme/size
        self.load_and_apply_user_preferences()

        # Initialize language manager
        self.lang_manager = get_language_manager()

        # Initialize project manager
        self.project_manager = get_project_manager()

        self.setWindowTitle(f"{self.lang_manager.get('app_title')} - RAG Synthesis")
        self.setGeometry(100, 100, 1200, 800)

        # Project state
        self.current_project = None
        self.current_project_id = None
        self.project_name = "default"  # Legacy, will be removed

        # State tracking
        self.themes = []
        self.processing_worker = None
        self.theme_worker = None
        self.synthesis_worker = None
        self.figure_extraction_worker = None

        self.setup_ui()
        self.setup_menubar()
        self.setup_statusbar()

        # Load last project or show dashboard
        self.load_last_project_or_show_dashboard()

        logger.info("Main window initialized")

    def setup_ui(self):
        """Setup main UI components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel(self.lang_manager.get("app_title"))
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Project switcher bar
        self.project_bar = self.create_project_switcher_bar()
        layout.addWidget(self.project_bar)

        # Tab widget for different sections
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Files (replaces Documents tab)
        self.files_widget = FilesWidget()
        self.files_widget.documents_changed.connect(self.on_documents_changed)
        self.files_widget.process_requested.connect(self.on_process_requested)
        self.files_widget.clear_db_btn.clicked.connect(self.clear_database)
        self.files_tab_index = self.tabs.addTab(
            self.files_widget, self.lang_manager.get("section_input_docs")
        )

        # Tab 2: Themes
        self.themes_tab = self.create_themes_tab()
        self.themes_tab_index = self.tabs.addTab(
            self.themes_tab, self.lang_manager.get("tab_themes")
        )

        # Tab 3: Synthesis
        self.synthesis_tab = self.create_synthesis_tab()
        self.tabs.addTab(self.synthesis_tab, self.lang_manager.get("tab_synthesis"))

        # Tab 4: Data Update (Figure Extraction)
        self.figure_extraction_tab = self.create_figure_extraction_tab()
        self.tabs.addTab(self.figure_extraction_tab, self.lang_manager.get("tab_data_update"))

        # Tab 5: Settings
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, self.lang_manager.get("tab_settings"))

        # Shared progress bar and status (below tabs)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.status_label)

    def on_documents_changed(self, documents):
        """Handle document list changes."""
        # Update Files tab label with document count badge
        doc_count = len(documents) if documents else 0
        tab_label = self.lang_manager.get("section_input_docs")
        if doc_count > 0:
            tab_label += f" ({doc_count})"
        self.tabs.setTabText(self.files_tab_index, tab_label)

        # Enable/disable discover button based on whether processing has been done
        # This will be updated after processing completes

        # Enable/disable figure extraction button based on document availability
        if documents and len(documents) > 0:
            self.figure_extraction_widget.extract_btn.setEnabled(True)
            # Update status to show ready state
            doc_word = (
                self.lang_manager.get("word_document")
                if doc_count == 1
                else self.lang_manager.get("word_documents")
            )
            status_msg = self.lang_manager.get("status_ready_extract_count").format(
                doc_count, doc_word
            )
            self.figure_extraction_widget.status_label.setText(status_msg)
        else:
            self.figure_extraction_widget.extract_btn.setEnabled(False)
            self.figure_extraction_widget.status_label.setText(
                self.lang_manager.get("status_no_document")
            )

    def on_process_requested(self, documents):
        """Handle process request from Files widget."""
        self.process_documents(documents)

    def create_themes_tab(self):
        """Create theme discovery tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.discover_btn = QPushButton(self.lang_manager.get("btn_discover_themes"))
        self.discover_btn.clicked.connect(self.discover_themes)
        self.discover_btn.setEnabled(False)
        self.discover_btn.setToolTip(self.lang_manager.get("tooltip_discover_themes"))
        button_layout.addWidget(self.discover_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Theme editor widget
        self.theme_editor = ThemeEditorWidget()
        self.theme_editor.themes_changed.connect(self.on_themes_changed)
        layout.addWidget(self.theme_editor)

        return widget

    def create_synthesis_tab(self):
        """Create book synthesis tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Synthesis configuration widget
        self.synthesis_config = SynthesisConfigWidget()
        layout.addWidget(self.synthesis_config)

        # Connect signals
        self.synthesis_config.synthesis_requested.connect(self.generate_book)

        return widget

    def create_figure_extraction_tab(self):
        """Create figure extraction tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Figure extraction widget
        self.figure_extraction_widget = FigureExtractionWidget()

        # Connect extract button to handler
        self.figure_extraction_widget.extract_btn.clicked.connect(self.extract_figures)

        layout.addWidget(self.figure_extraction_widget)

        return widget

    def create_settings_tab(self):
        """Create settings tab."""
        from docprocessor.gui.widgets.settings_widget import SettingsWidget

        settings_widget = SettingsWidget()
        settings_widget.language_changed.connect(self.on_language_changed)

        return settings_widget

    def on_language_changed(self, language_code):
        """Handle language change."""
        # Language change would require recreating UI widgets
        # For now, just acknowledge the change
        pass

    def setup_menubar(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu(self.lang_manager.get("menu_file"))

        import_action = QAction(self.lang_manager.get("menu_import"), self)
        import_action.setShortcut(QKeySequence.StandardKey.Open)
        import_action.setToolTip("Import PDF documents into your project (Cmd+O)")
        import_action.setStatusTip("Import one or more PDF files to process")
        import_action.triggered.connect(self.files_widget.import_documents)
        file_menu.addAction(import_action)

        import_url_action = QAction(self.lang_manager.get("menu_import_url"), self)
        import_url_action.setShortcut(QKeySequence("Ctrl+Shift+U"))
        import_url_action.setToolTip("Import documents from a URL (Ctrl+Shift+U)")
        import_url_action.setStatusTip("Download and import documents from web URLs")
        import_url_action.triggered.connect(self.show_url_import_dialog)
        file_menu.addAction(import_url_action)

        search_import_action = QAction(self.lang_manager.get("menu_search_import"), self)
        search_import_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        search_import_action.setToolTip("Search and import from research sources (Ctrl+Shift+S)")
        search_import_action.setStatusTip("Search government and legal databases for documents")
        search_import_action.triggered.connect(self.show_search_import_dialog)
        file_menu.addAction(search_import_action)

        open_file_action = QAction(self.lang_manager.get("menu_open_file"), self)
        open_file_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_file_action.setToolTip(
            "Open an existing file in your default application (Ctrl+Shift+O)"
        )
        open_file_action.setStatusTip("Browse and open any file from your file system")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        file_menu.addSeparator()

        exit_action = QAction(self.lang_manager.get("menu_exit"), self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Project menu (new!)
        project_menu = menubar.addMenu(self.lang_manager.get("menu_project"))

        new_project_action = QAction(self.lang_manager.get("menu_new_project"), self)
        new_project_action.setShortcut(QKeySequence.StandardKey.New)
        new_project_action.setToolTip("Create a new project (Cmd+N)")
        new_project_action.setStatusTip("Start a new document processing project")
        new_project_action.triggered.connect(self.create_new_project)
        project_menu.addAction(new_project_action)

        manage_projects_action = QAction(self.lang_manager.get("menu_manage_projects"), self)
        manage_projects_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        manage_projects_action.setToolTip("View and manage all projects (Ctrl+Shift+P)")
        manage_projects_action.setStatusTip("Open the projects dashboard")
        manage_projects_action.triggered.connect(self.show_project_dashboard)
        project_menu.addAction(manage_projects_action)

        project_menu.addSeparator()

        self.project_settings_action = QAction(self.lang_manager.get("menu_project_settings"), self)
        self.project_settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        self.project_settings_action.setToolTip("Configure current project settings (Cmd+,)")
        self.project_settings_action.setStatusTip("Edit project name, description, and tags")
        self.project_settings_action.triggered.connect(self.show_project_settings)
        self.project_settings_action.setEnabled(False)  # Disabled until project is loaded
        project_menu.addAction(self.project_settings_action)

        # Settings menu
        settings_menu = menubar.addMenu(self.lang_manager.get("menu_settings"))

        appearance_action = QAction(self.lang_manager.get("menu_appearance"), self)
        appearance_action.triggered.connect(self.show_appearance_settings)
        settings_menu.addAction(appearance_action)

        chunk_settings_action = QAction(self.lang_manager.get("menu_chunk_settings"), self)
        chunk_settings_action.triggered.connect(self.show_chunk_settings)
        settings_menu.addAction(chunk_settings_action)

        model_settings_action = QAction(self.lang_manager.get("menu_model_settings"), self)
        model_settings_action.triggered.connect(self.show_model_settings)
        settings_menu.addAction(model_settings_action)

        # Help menu
        help_menu = menubar.addMenu(self.lang_manager.get("menu_help"))

        about_action = QAction(self.lang_manager.get("menu_about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """Setup status bar."""
        self.statusBar().showMessage(self.lang_manager.get("status_ready_local"))

    # Project Management
    def create_project_switcher_bar(self):
        """Create the project switcher toolbar."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)

        # Current project label
        project_label = QLabel(self.lang_manager.get("current_project", "Projet actuel") + ":")
        layout.addWidget(project_label)

        # Project dropdown (replaces label with interactive combobox)
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.setToolTip(
            self.lang_manager.get("tooltip_select_project", "Sélectionner un projet")
        )
        self.project_combo.currentIndexChanged.connect(self.on_project_combo_changed)
        layout.addWidget(self.project_combo)

        layout.addStretch()

        # Manage Projects button
        self.manage_projects_btn = QPushButton(
            self.lang_manager.get("btn_manage_projects", "Gérer les projets")
        )
        self.manage_projects_btn.setToolTip("Voir tous vos projets")
        self.manage_projects_btn.clicked.connect(self.show_project_dashboard)
        layout.addWidget(self.manage_projects_btn)

        # Settings button
        self.project_settings_btn = QPushButton(
            self.lang_manager.get("btn_project_settings", "Paramètres du projet")
        )
        self.project_settings_btn.setToolTip("Configuration du projet actuel")
        self.project_settings_btn.setEnabled(False)
        self.project_settings_btn.clicked.connect(self.show_project_settings)
        layout.addWidget(self.project_settings_btn)

        return widget

    def load_last_project_or_show_dashboard(self):
        """Load the last opened project or show dashboard if none."""
        # Try to load last project from settings
        last_project_id = self.load_last_project_id()

        if last_project_id:
            project = self.project_manager.load_project(last_project_id)
            if project:
                self.switch_to_project(project.id)
                return

        # No valid last project, show dashboard
        self.show_project_dashboard()

    def load_last_project_id(self):
        """Load last opened project ID from user preferences."""
        from docprocessor.utils.user_preferences import get_user_preferences_manager

        prefs_manager = get_user_preferences_manager()
        return prefs_manager.get_last_project_id()

    def save_last_project_id(self, project_id):
        """Save last opened project ID to user preferences."""
        from docprocessor.utils.user_preferences import get_user_preferences_manager

        prefs_manager = get_user_preferences_manager()
        if not prefs_manager.set_last_project_id(project_id):
            logger.error("Error saving last project ID to preferences")

    def show_project_dashboard(self):
        """Show the project dashboard dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle(self.lang_manager.get("projects_dashboard", "Projects Dashboard"))
        dialog.setMinimumSize(900, 600)

        layout = QVBoxLayout(dialog)

        # Add dashboard widget
        dashboard = ProjectDashboard()
        dashboard.project_selected.connect(
            lambda pid: self.on_project_selected_from_dashboard(pid, dialog)
        )
        dashboard.project_created.connect(
            lambda pid: self.on_project_selected_from_dashboard(pid, dialog)
        )
        layout.addWidget(dashboard)

        dialog.exec()

        # Refresh project combo after dashboard closes (in case projects were added/renamed/deleted)
        self.refresh_project_combo()

    def on_project_selected_from_dashboard(self, project_id, dialog):
        """Handle project selection from dashboard."""
        self.switch_to_project(project_id)
        dialog.accept()

    def switch_to_project(self, project_id):
        """Switch to a different project."""
        # Load project
        project = self.project_manager.load_project(project_id)
        if not project:
            QMessageBox.warning(
                self,
                self.lang_manager.get("error", "Error"),
                self.lang_manager.get("msg_project_load_error", "Failed to load project"),
            )
            return

        # Save current project if needed
        if self.current_project:
            self.save_current_project()

        # Switch to new project
        self.current_project = project
        self.current_project_id = project_id
        self.project_name = project.name  # Legacy compatibility

        # Update UI
        self.update_project_ui()

        # Load project data
        self.load_project_data()

        # Save as last opened
        self.save_last_project_id(project_id)

        logger.info(f"Switched to project: {project.name}")

    def refresh_project_combo(self):
        """Refresh the project dropdown with all available projects."""
        # Block signals to prevent triggering switch during refresh
        self.project_combo.blockSignals(True)

        # Clear and repopulate
        self.project_combo.clear()

        # Get all projects
        projects = self.project_manager.list_projects()

        if not projects:
            self.project_combo.addItem(self.lang_manager.get("no_project", "Aucun projet"), None)
            self.project_combo.setEnabled(False)
        else:
            self.project_combo.setEnabled(True)
            for project in projects:
                self.project_combo.addItem(project.name, project.id)

            # Select current project
            if self.current_project_id:
                index = self.project_combo.findData(self.current_project_id)
                if index >= 0:
                    self.project_combo.setCurrentIndex(index)

        # Unblock signals
        self.project_combo.blockSignals(False)

    def on_project_combo_changed(self, index):
        """Handle project selection from dropdown."""
        if index < 0:
            return

        project_id = self.project_combo.itemData(index)

        # If no project ID (e.g., "No Project" placeholder), ignore
        if not project_id:
            return

        # If already on this project, ignore
        if project_id == self.current_project_id:
            return

        # Switch to selected project
        self.switch_to_project(project_id)

    def update_project_ui(self):
        """Update UI to reflect current project."""
        # Refresh project dropdown
        self.refresh_project_combo()

        if self.current_project:
            # Update window title
            self.setWindowTitle(
                f"{self.current_project.name} - {self.lang_manager.get('app_title')}"
            )

            # Enable project settings button and menu action
            self.project_settings_btn.setEnabled(True)
            self.project_settings_action.setEnabled(True)
        else:
            self.setWindowTitle(f"{self.lang_manager.get('app_title')} - RAG Synthesis")
            self.project_settings_btn.setEnabled(False)
            self.project_settings_action.setEnabled(False)

    def load_project_data(self):
        """Load project data into UI widgets."""
        if not self.current_project:
            # Clear UI when no project
            self.files_widget.set_project(None)
            self.synthesis_config.update_cache_status(None)
            return

        # Load documents into Files widget from project
        self.files_widget.set_project(self.current_project)

        # Load themes
        if self.current_project.themes:
            self.theme_editor.set_themes(self.current_project.themes)
            self.themes = self.current_project.themes

        # Update cache status
        if self.current_project.synthesis_cache:
            self.synthesis_config.update_cache_status(self.current_project.synthesis_cache)
        else:
            self.synthesis_config.update_cache_status(None)

        # Update status
        stats = self.current_project.get_statistics()
        status_msg = f"{stats['total_documents']} docs, {stats['total_themes']} themes, {stats['total_tasks_executed']} tasks"
        self.statusBar().showMessage(status_msg)

    def save_current_project(self):
        """Save current project state."""
        if not self.current_project:
            return

        # Save themes
        self.current_project.set_themes(self.themes)

        # Save to disk
        self.project_manager.save_project(self.current_project)
        logger.info(f"Saved project: {self.current_project.name}")

    def show_project_settings(self):
        """Show project settings dialog."""
        if not self.current_project:
            return

        dialog = ProjectSettingsDialog(self.current_project, self)
        if dialog.exec():
            # Settings were saved by the dialog
            # Save the project to disk
            self.project_manager.save_project(self.current_project)

            # Update UI with new project name if changed
            self.update_project_ui()

            # Update status bar
            self.statusBar().showMessage(
                self.lang_manager.get("msg_settings_saved", "Project settings saved successfully"),
                3000,
            )

    def create_new_project(self):
        """Create a new project directly."""
        from PyQt6.QtWidgets import QDialog

        from docprocessor.gui.widgets.project_dashboard import NewProjectDialog

        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_project_data()

            # Create project
            project = self.project_manager.create_project(
                name=data["name"], description=data["description"], tags=data["tags"]
            )

            if project:
                # Save the project
                self.project_manager.save_project(project)

                # Switch to new project
                self.switch_to_project(project.id)

                # Update project list
                self.update_project_combo()

                self.statusBar().showMessage(
                    self.lang_manager.get(
                        "msg_project_created", f'Project "{project.name}" created successfully'
                    ),
                    3000,
                )

    def show_chunk_settings(self):
        """Show chunk settings dialog."""
        from PyQt6.QtWidgets import (
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QSpinBox,
            QVBoxLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle(self.lang_manager.get("menu_chunk_settings"))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()

        chunk_size_spin = QSpinBox()
        chunk_size_spin.setRange(100, 5000)
        chunk_size_spin.setValue(settings.chunk_size)
        form_layout.addRow("Chunk Size:", chunk_size_spin)

        chunk_overlap_spin = QSpinBox()
        chunk_overlap_spin.setRange(0, 500)
        chunk_overlap_spin.setValue(settings.chunk_overlap)
        form_layout.addRow("Chunk Overlap:", chunk_overlap_spin)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            # Note: These changes would require app restart or reprocessing
            QMessageBox.information(
                self,
                "Info",
                "Chunk settings viewed. Changing these settings would require reprocessing documents.",
            )

    def show_model_settings(self):
        """Show model settings dialog."""
        from PyQt6.QtWidgets import (
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QLineEdit,
            QVBoxLayout,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle(self.lang_manager.get("menu_model_settings"))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        form_layout = QFormLayout()

        ollama_model_edit = QLineEdit(settings.ollama_model)
        form_layout.addRow("Ollama Model:", ollama_model_edit)

        embedding_model_edit = QLineEdit(settings.embedding_model)
        form_layout.addRow("Embedding Model:", embedding_model_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            # Note: These changes would require app restart
            QMessageBox.information(
                self,
                "Info",
                "Model settings viewed. Changing these settings would require app restart.",
            )

    # Event handlers
    def on_themes_changed(self, themes):
        """Handle theme list changes."""
        self.themes = themes

        # Update Themes tab label with theme count badge
        theme_count = len(themes) if themes else 0
        tab_label = self.lang_manager.get("tab_themes")
        if theme_count > 0:
            tab_label += f" ({theme_count})"
        self.tabs.setTabText(self.themes_tab_index, tab_label)

        self.synthesis_config.set_ready_for_synthesis(len(themes) > 0)

    def process_documents(self, documents):
        """Process documents (extract, chunk, embed)."""
        if not documents:
            QMessageBox.warning(
                self,
                self.lang_manager.get("dialog_no_documents"),
                self.lang_manager.get("dialog_no_documents_msg"),
            )
            return

        # Disable buttons
        self.files_widget.set_process_enabled(False)
        self.files_widget.add_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start worker
        self.processing_worker = DocumentProcessingWorker(documents, self.project_name)
        self.processing_worker.progress.connect(self.on_processing_progress)
        self.processing_worker.finished.connect(self.on_processing_finished)
        self.processing_worker.error.connect(self.on_processing_error)
        self.processing_worker.start()

        self.statusBar().showMessage(self.lang_manager.get("status_processing"))

    def on_processing_progress(self, percent, message):
        """Handle processing progress updates."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def on_processing_finished(self, total_chunks):
        """Handle processing completion."""
        self.progress_bar.setVisible(False)
        success_msg = f"✓ {self.lang_manager.get('status_complete', total_chunks)}"
        self.status_label.setText(success_msg)
        self.status_label.setStyleSheet("padding: 5px; color: #28a745; font-weight: bold;")

        # Show success in status bar with timeout
        self.statusBar().showMessage(
            f"✓ {self.lang_manager.get('status_complete', total_chunks)}", 5000
        )

        # Re-enable buttons
        self.files_widget.set_process_enabled(True)
        self.files_widget.add_btn.setEnabled(True)
        self.discover_btn.setEnabled(True)

        # Refresh output files list
        self.files_widget.refresh_output_files()

        # Properly cleanup worker thread
        if self.processing_worker:
            self.processing_worker.wait()
            self.processing_worker.deleteLater()
            self.processing_worker = None

        # Show success dialog with icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(self.lang_manager.get("dialog_processing_complete"))
        msg_box.setText(
            f"✓ {self.lang_manager.get('dialog_processing_complete_msg', total_chunks)}"
        )
        msg_box.setInformativeText(f"\n{self.lang_manager.get('dialog_can_discover_themes')}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def on_processing_error(self, error_message):
        """Handle processing error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✗ {self.lang_manager.get('error')}: {error_message}")
        self.status_label.setStyleSheet("padding: 5px; color: #dc3545; font-weight: bold;")
        self.statusBar().showMessage(self.lang_manager.get("status_processing_failed"))

        # Re-enable buttons
        self.files_widget.set_process_enabled(True)
        self.files_widget.add_btn.setEnabled(True)

        # Properly cleanup worker thread
        if self.processing_worker:
            self.processing_worker.wait()
            self.processing_worker.deleteLater()
            self.processing_worker = None

        # Provide helpful error message with troubleshooting
        detailed_message = f"❌ {error_message}\n\n"

        # Add specific troubleshooting based on error type
        if "ollama" in error_message.lower() or "connection" in error_message.lower():
            detailed_message += "🔧 Troubleshooting:\n"
            detailed_message += "1. Check if Ollama is running:\n"
            detailed_message += "   curl http://localhost:11434/api/version\n\n"
            detailed_message += "2. Start Ollama if needed:\n"
            detailed_message += "   ollama serve\n\n"
            detailed_message += "3. Verify model is downloaded:\n"
            detailed_message += "   ollama list"
        elif "memory" in error_message.lower() or "ram" in error_message.lower():
            detailed_message += "🔧 Troubleshooting:\n"
            detailed_message += "• Try processing fewer documents at once\n"
            detailed_message += "• Close other applications to free memory\n"
            detailed_message += "• Restart the application"
        elif "file" in error_message.lower() or "path" in error_message.lower():
            detailed_message += "🔧 Troubleshooting:\n"
            detailed_message += "• Check that all PDFs exist and are readable\n"
            detailed_message += "• Remove corrupted files from the list\n"
            detailed_message += "• Ensure you have read permissions"
        else:
            detailed_message += "📖 See Troubleshooting Guide in docs/ for more help"

        QMessageBox.critical(
            self,
            self.lang_manager.get("dialog_processing_error"),
            detailed_message,
        )

    def clear_database(self):
        """Clear the vector database completely."""
        # Create message box with custom buttons for translation
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(self.lang_manager.get("dialog_clear_database"))
        msg_box.setText(self.lang_manager.get("dialog_clear_database_msg"))

        # Add custom buttons with translated text
        yes_btn = msg_box.addButton(self.lang_manager.get("yes"), QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton(self.lang_manager.get("no"), QMessageBox.ButtonRole.NoRole)
        msg_box.setDefaultButton(no_btn)

        # Show dialog and get result
        msg_box.exec()

        if msg_box.clickedButton() == yes_btn:
            try:
                # Get vector database path from config
                from config.settings import settings

                vector_db_path = Path(settings.vector_db_dir)

                # Remove the entire vector database directory
                if vector_db_path.exists():
                    shutil.rmtree(vector_db_path)
                    logger.info(f"Cleared vector database at {vector_db_path}")

                # Clear themes from UI
                self.themes = []
                self.theme_editor.set_themes([])

                # Reset synthesis button
                self.synthesis_config.synthesize_btn.setEnabled(False)
                self.discover_btn.setEnabled(False)

                # Show success message with translated OK button
                success_box = QMessageBox(self)
                success_box.setIcon(QMessageBox.Icon.Information)
                success_box.setWindowTitle(self.lang_manager.get("dialog_database_cleared"))
                success_box.setText(self.lang_manager.get("dialog_database_cleared_msg"))
                success_box.addButton(
                    self.lang_manager.get("ok"), QMessageBox.ButtonRole.AcceptRole
                )
                success_box.exec()

                self.statusBar().showMessage(self.lang_manager.get("dialog_database_cleared"))

            except Exception as e:
                error_msg = f"Failed to clear database: {str(e)}"
                logger.error(error_msg)

                # Show error with translated OK button
                error_box = QMessageBox(self)
                error_box.setIcon(QMessageBox.Icon.Critical)
                error_box.setWindowTitle(self.lang_manager.get("error"))
                error_box.setText(error_msg)
                error_box.addButton(self.lang_manager.get("ok"), QMessageBox.ButtonRole.AcceptRole)
                error_box.exec()

    def discover_themes(self):
        """Discover themes from processed documents."""
        # Get configuration
        config = self.synthesis_config.get_config()
        num_themes = config.get("num_themes")  # None if auto-detect

        # Disable buttons
        self.discover_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start worker
        self.theme_worker = ThemeDiscoveryWorker(self.project_name, num_themes)
        self.theme_worker.progress.connect(self.on_theme_progress)
        self.theme_worker.finished.connect(self.on_theme_finished)
        self.theme_worker.error.connect(self.on_theme_error)
        self.theme_worker.start()

        self.statusBar().showMessage(self.lang_manager.get("status_discovering_themes"))

    def on_theme_progress(self, percent, message):
        """Handle theme discovery progress."""
        self.progress_bar.setValue(percent)
        self.theme_editor.status_label.setText(message)

    def on_theme_finished(self, themes):
        """Handle theme discovery completion."""
        self.progress_bar.setVisible(False)
        success_msg = f"✓ {self.lang_manager.get('theme_discovery_complete', len(themes))}"
        self.statusBar().showMessage(success_msg, 5000)

        # Update theme editor
        self.theme_editor.set_themes(themes)

        # Re-enable button
        self.discover_btn.setEnabled(True)

        # Properly cleanup worker thread
        if self.theme_worker:
            self.theme_worker.wait()
            self.theme_worker.deleteLater()
            self.theme_worker = None

        # Invalidate synthesis cache (themes changed)
        if self.current_project and self.current_project.synthesis_cache:
            logger.info("Invalidating synthesis cache (themes changed)")
            self.current_project.synthesis_cache = None
            self.project_manager.save_project(self.current_project)
            self.synthesis_config.update_cache_status(None)

        # Show success dialog with icon
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(self.lang_manager.get("dialog_theme_discovery_complete"))
        msg_box.setText(
            f"✓ {self.lang_manager.get('dialog_theme_discovery_complete_msg', len(themes))}"
        )
        msg_box.setInformativeText(
            f"\n🎯 Discovered {len(themes)} themes. You can now generate your synthesis."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def on_theme_error(self, error_message):
        """Handle theme discovery error."""
        self.progress_bar.setVisible(False)
        self.theme_editor.status_label.setText(
            f"✗ {self.lang_manager.get('error')}: {error_message}"
        )
        self.statusBar().showMessage(self.lang_manager.get("status_theme_discovery_failed"))

        # Re-enable button
        self.discover_btn.setEnabled(True)

        # Properly cleanup worker thread
        if self.theme_worker:
            self.theme_worker.wait()
            self.theme_worker.deleteLater()
            self.theme_worker = None

        # Provide helpful error message
        detailed_message = f"❌ {error_message}\n\n"

        if "ollama" in error_message.lower() or "connection" in error_message.lower():
            detailed_message += "🔧 Ollama Connection Issue:\n"
            detailed_message += "• Start Ollama: ollama serve\n"
            detailed_message += "• Verify it's running: curl http://localhost:11434/api/version"
        elif "empty" in error_message.lower() or "no chunks" in error_message.lower():
            detailed_message += "🔧 No Data to Analyze:\n"
            detailed_message += "• Process documents first (go to Files tab)\n"
            detailed_message += "• Ensure documents were processed successfully\n"
            detailed_message += "• Check that vector database has data"
        else:
            detailed_message += "💡 Suggestions:\n"
            detailed_message += "• Try processing fewer documents\n"
            detailed_message += "• Clear database and reprocess\n"
            detailed_message += "• Check logs for details"

        QMessageBox.critical(
            self,
            self.lang_manager.get("dialog_theme_discovery_error"),
            detailed_message,
        )

    def _is_cache_valid(self, cache, config):
        """Check if cached synthesis is still valid for current configuration.

        Returns:
            True if cache can be reused, False if regeneration is needed
            Note: Output format changes don't invalidate cache, just re-export
        """
        if not cache:
            return False

        # Get current theme IDs
        current_theme_ids = [t.get("id") for t in self.themes]

        # Check if themes changed
        if set(cache.theme_ids) != set(current_theme_ids):
            logger.info("Cache invalid: themes changed")
            return False

        # Check if synthesis level changed
        if cache.synthesis_level != config["synthesis_level"]:
            logger.info("Cache invalid: synthesis level changed")
            return False

        # Check if chunks_per_chapter changed (affects content)
        if cache.config_used.get("chunks_per_chapter") != config["chunks_per_chapter"]:
            logger.info("Cache invalid: chunks_per_chapter changed")
            return False

        logger.info("Cache is valid")
        return True

    def _export_from_cache(self, cache, config):
        """Export cached chapters to selected format without regeneration."""
        try:
            from docprocessor.core.output_formatter import OutputFormatter
            from docprocessor.models.chapter import Chapter

            logger.info(
                f"Exporting from cache: {cache.total_words} words, {len(cache.chapters)} chapters"
            )

            # Convert cached chapter dicts back to Chapter objects
            chapters = []
            for chapter_dict in cache.chapters:
                # Chapter is a Pydantic model, use model_validate
                chapter = Chapter.model_validate(chapter_dict)
                chapters.append(chapter)

            # Create output formatter
            output_formatter = OutputFormatter()

            # Track generated file paths
            markdown_path = None
            docx_path = None

            # Export to selected format(s)
            if config["output_format"] in ["markdown", "both", "all"]:
                logger.info("Exporting cached chapters to Markdown")
                markdown_path = str(
                    output_formatter.export_markdown(
                        chapters=chapters,
                        title=cache.config_used.get("title", "Synthesized Document"),
                        author=cache.config_used.get("author"),
                    )
                )

            if config["output_format"] in ["docx", "both", "all"]:
                logger.info("Exporting cached chapters to DOCX")
                docx_path = str(
                    output_formatter.export_docx(
                        chapters=chapters,
                        title=cache.config_used.get("title", "Synthesized Document"),
                        author=cache.config_used.get("author"),
                    )
                )

            if config["output_format"] in ["pdf", "all"]:
                logger.info("Exporting cached chapters to PDF")
                try:
                    pdf_path = str(
                        output_formatter.export_pdf(
                            chapters=chapters,
                            title=cache.config_used.get("title", "Synthesized Document"),
                            author=cache.config_used.get("author"),
                        )
                    )
                except Exception as e:
                    logger.warning(f"PDF export from cache failed: {e}")

            # Refresh output files list
            self.files_widget.refresh_output_files()

            # Show success message
            message = self.lang_manager.get("dialog_synthesis_success") + "\n\n"
            message += (
                f"✨ {self.lang_manager.get('status_used_cache', 'Used cached synthesis')}\n\n"
            )
            if markdown_path:
                message += f"Markdown: {markdown_path}\n"
            if docx_path:
                message += f"DOCX: {docx_path}"

            QMessageBox.information(
                self, self.lang_manager.get("dialog_synthesis_complete"), message
            )

            self.statusBar().showMessage(self.lang_manager.get("synthesis_complete"))

        except Exception as e:
            logger.error(f"Error exporting from cache: {e}")
            QMessageBox.warning(
                self,
                self.lang_manager.get("error"),
                f"Failed to export from cache: {str(e)}\nWill regenerate synthesis.",
            )
            # Fall back to regeneration
            self._start_synthesis_worker(config)

    def _start_synthesis_worker(self, config):
        """Start the synthesis worker thread."""
        # Disable synthesis button and show progress bar
        self.synthesis_config.synthesize_btn.setEnabled(False)
        self.synthesis_config.progress_bar.setVisible(True)
        self.synthesis_config.progress_bar.setValue(0)

        # Create and start worker
        self.synthesis_worker = SynthesisWorker(
            project_name=self.project_name,
            synthesis_level=config["synthesis_level"],
            chunks_per_chapter=config["chunks_per_chapter"],
            output_format=config["output_format"],
            title="Synthesized Document",
            author=None,
        )
        self.synthesis_worker.progress.connect(self.on_synthesis_progress)
        self.synthesis_worker.finished.connect(self.on_synthesis_finished)
        self.synthesis_worker.error.connect(self.on_synthesis_error)
        self.synthesis_worker.start()

        self.statusBar().showMessage(self.lang_manager.get("status_generating_book"))

    def generate_book(self):
        """Generate synthesized book."""
        if not self.themes:
            QMessageBox.warning(
                self,
                self.lang_manager.get("dialog_no_themes"),
                self.lang_manager.get("dialog_no_themes_msg"),
            )
            return

        # Get configuration
        config = self.synthesis_config.get_config()

        # Check if cached synthesis exists
        if self.current_project and self.current_project.synthesis_cache:
            cache = self.current_project.synthesis_cache

            # Check if cache is still valid
            if self._is_cache_valid(cache, config):
                # Offer to use cache
                cache_date = cache.generated_at.strftime("%Y-%m-%d %H:%M")
                reply = QMessageBox.question(
                    self,
                    "Use Cached Synthesis?",
                    f"Found existing synthesis from {cache_date}\n\n"
                    f"Level: {cache.synthesis_level}\n"
                    f"Chapters: {len(cache.chapters)}\n"
                    f"Total words: {cache.total_words:,}\n"
                    f"Citations: {cache.total_citations}\n\n"
                    "Use cached synthesis (instant) or regenerate?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Use cached chapters
                    self._export_from_cache(cache, config)
                    return

        # Proceed with normal synthesis
        self._start_synthesis_worker(config)

    def on_synthesis_progress(self, percent, message):
        """Handle synthesis progress."""
        self.synthesis_config.progress_bar.setValue(percent)
        self.synthesis_config.update_status(message)

    def on_synthesis_finished(self, markdown_path, docx_path, pdf_path, cache):
        """Handle synthesis completion."""
        self.synthesis_config.progress_bar.setVisible(False)
        self.synthesis_config.update_status(f"✓ {self.lang_manager.get('synthesis_complete')}")
        self.statusBar().showMessage(f"✨ {self.lang_manager.get('synthesis_complete')}", 5000)

        # Re-enable synthesis button
        self.synthesis_config.synthesize_btn.setEnabled(True)

        # Properly cleanup worker thread
        if self.synthesis_worker:
            self.synthesis_worker.wait()  # Wait for thread to finish
            self.synthesis_worker.deleteLater()  # Schedule for deletion
            self.synthesis_worker = None

        # Save cache to project
        if self.current_project and cache:
            self.current_project.synthesis_cache = cache
            self.project_manager.save_project(self.current_project)
            logger.info(
                f"Saved synthesis cache: {cache.total_words} words, {cache.total_citations} citations"
            )
            # Update cache status in UI
            self.synthesis_config.update_cache_status(cache)

        # Refresh output files list
        self.files_widget.refresh_output_files()

        # Show completion message with file paths
        message = f"✨ {self.lang_manager.get('dialog_synthesis_success')}\n\n"
        files_created = []
        if markdown_path:
            files_created.append(f"📄 Markdown: {markdown_path}")
        if docx_path:
            files_created.append(f"📘 DOCX: {docx_path}")
        if pdf_path:
            files_created.append(f"📕 PDF: {pdf_path}")

        if files_created:
            message += "\n".join(files_created)

        # Add summary if cache exists
        if cache:
            message += (
                f"\n\n📊 Summary: {cache.total_words:,} words, {cache.total_citations} citations"
            )

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(self.lang_manager.get("dialog_synthesis_complete"))
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def on_synthesis_error(self, error_message):
        """Handle synthesis error."""
        self.progress_bar.setVisible(False)
        self.synthesis_config.progress_bar.setVisible(False)
        self.synthesis_config.update_status(
            f"✗ {self.lang_manager.get('error')}: {error_message}", is_error=True
        )
        self.statusBar().showMessage(self.lang_manager.get("status_synthesis_failed"))

        # Re-enable synthesis button
        self.synthesis_config.synthesize_btn.setEnabled(True)

        # Properly cleanup worker thread
        if self.synthesis_worker:
            self.synthesis_worker.wait()  # Wait for thread to finish
            self.synthesis_worker.deleteLater()  # Schedule for deletion
            self.synthesis_worker = None

        # Provide helpful error message
        detailed_message = f"❌ {error_message}\n\n"

        if "ollama" in error_message.lower() or "connection" in error_message.lower():
            detailed_message += "🔧 Ollama Connection Issue:\n"
            detailed_message += "• Start Ollama: ollama serve\n"
            detailed_message += "• Verify model: ollama list\n"
            detailed_message += "• Check connection: curl http://localhost:11434/api/version"
        elif "theme" in error_message.lower():
            detailed_message += "🔧 Missing Themes:\n"
            detailed_message += "• Discover themes first (go to Themes tab)\n"
            detailed_message += "• Click 'Discover Themes' button\n"
            detailed_message += "• Verify themes were discovered successfully"
        elif "pandoc" in error_message.lower() or "pdf" in error_message.lower():
            detailed_message += "🔧 PDF Export Setup:\n"
            detailed_message += "• Install pandoc: brew install pandoc (macOS)\n"
            detailed_message += "• Install LaTeX: brew install --cask mactex-no-gui (macOS)\n"
            detailed_message += "• See docs/PDF_EXPORT_SETUP.md for details"
        else:
            detailed_message += "💡 Suggestions:\n"
            detailed_message += "• Try selecting fewer themes\n"
            detailed_message += "• Use a lower synthesis level\n"
            detailed_message += "• Check logs: ~/.docprocessor/logs/docprocessor.log"

        QMessageBox.critical(
            self,
            self.lang_manager.get("dialog_synthesis_error"),
            detailed_message,
        )

    def extract_figures(self):
        """Extract figures from a document."""
        # Get selected document from Files widget
        selected_docs = self.files_widget.get_selected_documents()

        if not selected_docs:
            # If no selection, let user pick a file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Document for Figure Extraction",
                "",
                "Documents (*.pdf *.docx *.txt);;All Files (*)",
            )

            if not file_path:
                return  # User cancelled
        else:
            # Use first selected document
            file_path = selected_docs[0]

        # Disable extract button and show progress
        self.figure_extraction_widget.extract_btn.setEnabled(False)
        self.figure_extraction_widget.progress_bar.setVisible(True)
        self.figure_extraction_widget.progress_bar.setValue(0)
        self.figure_extraction_widget.update_status("Starting extraction...", is_error=False)

        # Create and start worker
        self.figure_extraction_worker = FigureExtractionWorker(file_path)
        self.figure_extraction_worker.progress.connect(self.on_figure_extraction_progress)
        self.figure_extraction_worker.finished.connect(self.on_figure_extraction_finished)
        self.figure_extraction_worker.error.connect(self.on_figure_extraction_error)
        self.figure_extraction_worker.start()

        logger.info(f"Started figure extraction for: {file_path}")

    def on_figure_extraction_progress(self, percent, message):
        """Handle figure extraction progress."""
        self.figure_extraction_widget.progress_bar.setValue(percent)
        self.figure_extraction_widget.update_status(message, is_error=False)

    def on_figure_extraction_finished(self, result):
        """Handle figure extraction completion."""
        self.figure_extraction_widget.progress_bar.setVisible(False)

        # Display results in widget
        self.figure_extraction_widget.show_results(result)

        # Show success status
        self.statusBar().showMessage(
            f"✓ Figure extraction complete: {result.total_figures} figures found", 5000
        )

        # Re-enable extract button
        self.figure_extraction_widget.extract_btn.setEnabled(True)

        # Cleanup worker
        if self.figure_extraction_worker:
            self.figure_extraction_worker.wait()
            self.figure_extraction_worker.deleteLater()
            self.figure_extraction_worker = None

        logger.info(f"Figure extraction completed: {result.total_figures} figures found")

    def on_figure_extraction_error(self, error_message):
        """Handle figure extraction error."""
        self.figure_extraction_widget.progress_bar.setVisible(False)
        self.figure_extraction_widget.update_status(f"Error: {error_message}", is_error=True)

        # Re-enable extract button
        self.figure_extraction_widget.extract_btn.setEnabled(True)

        # Cleanup worker
        if self.figure_extraction_worker:
            self.figure_extraction_worker.wait()
            self.figure_extraction_worker.deleteLater()
            self.figure_extraction_worker = None

        QMessageBox.critical(
            self, "Figure Extraction Error", f"Failed to extract figures:\n{error_message}"
        )

        logger.error(f"Figure extraction error: {error_message}")

    def show_url_import_dialog(self):
        """Show URL import dialog."""
        from docprocessor.gui.dialogs.url_import_dialog import URLImportDialog

        dialog = URLImportDialog(self)
        dialog.documents_imported.connect(self.on_documents_imported_from_url)
        dialog.exec()

    def on_documents_imported_from_url(self, imported_docs):
        """Handle imported documents from URL."""
        if not self.current_project:
            QMessageBox.warning(
                self,
                self.lang_manager.get("warning"),
                self.lang_manager.get("dialog_no_documents_msg"),
            )
            return

        import uuid

        from docprocessor.models.project import DocumentInfo

        # Add imported documents to current project
        for doc in imported_docs:
            # Create DocumentInfo for each imported document
            doc_info = DocumentInfo(
                id=str(uuid.uuid4()),
                file_path=doc["file_path"],
                title=doc["title"],
                file_size=doc["metadata"]["file_size"],
                source_url=doc.get("url"),  # Store the original URL
            )
            self.current_project.add_document(doc_info)

        # Save project and refresh UI
        self.save_current_project()
        self.load_project_data()

        # Show success message
        count = len(imported_docs)
        QMessageBox.information(
            self,
            self.lang_manager.get("success"),
            self.lang_manager.get("summary_import_success").format(count),
        )

        logger.info(
            f"Added {count} documents from URL import to project {self.current_project.name}"
        )

    def show_search_import_dialog(self):
        """Show search and import dialog."""
        from docprocessor.gui.dialogs.search_import_dialog import SearchImportDialog

        dialog = SearchImportDialog(self)
        dialog.documents_imported.connect(self.on_documents_imported_from_search)
        dialog.exec()

    def on_documents_imported_from_search(self, imported_docs):
        """Handle imported documents from search."""
        # Reuse same logic as URL import
        self.on_documents_imported_from_url(imported_docs)
        logger.info(
            f"Added {len(imported_docs)} documents from search import to project {self.current_project.name}"
        )

    def open_file(self):
        """Open a file from the file system."""
        import os

        from config.settings import settings

        # Let user select a file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.lang_manager.get("menu_open_file"),
            str(settings.output_dir),  # Start in output directory
            "All Files (*.*)",
        )

        if file_path:
            # Open with default application
            if os.name == "posix":  # macOS/Linux
                os.system(f'open "{file_path}"')
            elif os.name == "nt":  # Windows
                os.startfile(file_path)

    def load_and_apply_user_preferences(self):
        """Load user preferences and apply theme, size profile, and language."""
        from docprocessor.gui.size_profile import get_size_profile_manager
        from docprocessor.gui.theme_manager import get_theme_manager
        from docprocessor.utils.language_manager import Language, set_global_language
        from docprocessor.utils.user_preferences import get_user_preferences_manager

        prefs_manager = get_user_preferences_manager()
        theme_manager = get_theme_manager()
        size_manager = get_size_profile_manager()

        # Load and apply language (must be done before language manager is used)
        saved_language = prefs_manager.get_language()
        try:
            lang_enum = Language(saved_language)
            set_global_language(lang_enum)
            logger.info(f"Applied saved language: {saved_language}")
        except ValueError:
            logger.warning(
                f"Invalid language value in preferences: {saved_language}, using default"
            )

        # Load and apply theme
        saved_theme = prefs_manager.get_theme()
        theme_manager.set_theme(saved_theme)
        logger.info(f"Applied saved theme: {saved_theme.value}")

        # Load and apply size profile
        saved_size = prefs_manager.get_size_profile()
        size_manager.set_profile(saved_size)
        logger.info(f"Applied saved size profile: {saved_size.value}")

    def show_appearance_settings(self):
        """Show appearance settings dialog."""
        from docprocessor.gui.dialogs.appearance_settings_dialog import AppearanceSettingsDialog

        dialog = AppearanceSettingsDialog(self)
        dialog.settings_applied.connect(self.on_appearance_changed)
        dialog.exec()

    def on_appearance_changed(self):
        """Handle appearance settings change."""
        # Notify user that some changes may require restart
        QMessageBox.information(
            self,
            self.lang_manager.get("settings_applied", "Settings Applied"),
            self.lang_manager.get(
                "appearance_restart_msg",
                "Appearance settings have been updated. Some changes may require restarting the application for full effect.",
            ),
        )
        logger.info("Appearance settings changed")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            self.lang_manager.get("dialog_about_title"),
            self.lang_manager.get("dialog_about_content"),
        )

    def closeEvent(self, event):
        """Handle window close event - save project before closing."""
        if self.current_project:
            try:
                self.save_current_project()
                logger.info("Project saved before closing")
            except Exception as e:
                logger.error(f"Error saving project on close: {e}")

        event.accept()


def main():
    """Main entry point for GUI application."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("Hrisa Docs")

    window = DocumentProcessorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
