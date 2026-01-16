"""Project Dashboard widget for managing multiple projects."""

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from docprocessor.core.project_manager import get_project_manager
from docprocessor.gui.styles import Styles
from docprocessor.models.project import Project
from docprocessor.utils.language_manager import get_language_manager


class ProjectListItem(QListWidgetItem):
    """Custom list item for projects with rich information."""

    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self.update_display()

    def update_display(self):
        """Update the display text with project info."""
        project = self.project
        stats = project.get_statistics()

        lines = []

        # Title
        title = project.name
        lines.append(title)

        # Description
        if project.description:
            desc = (
                project.description[:60] + "..."
                if len(project.description) > 60
                else project.description
            )
            lines.append(f"  {desc}")

        # Statistics
        stats_text = f"  {stats['total_documents']} docs"
        if stats["total_themes"] > 0:
            stats_text += f" • {stats['total_themes']} themes"
        if stats["total_tasks_executed"] > 0:
            stats_text += f" • {stats['total_tasks_executed']} tasks"
        lines.append(stats_text)

        # Last modified
        last_modified = project.updated_at.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {last_modified}")

        # Tags
        if project.tags:
            tags_str = " ".join(f"#{tag}" for tag in project.tags[:3])
            if len(project.tags) > 3:
                tags_str += f" +{len(project.tags) - 3}"
            lines.append(f"  {tags_str}")

        self.setText("\n".join(lines))

        # Set tooltip
        tooltip_lines = [
            f"Name: {project.name}",
            f"ID: {project.id}",
            f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"Updated: {project.updated_at.strftime('%Y-%m-%d %H:%M')}",
            f"Documents: {stats['total_documents']}",
            f"Themes: {stats['total_themes']}",
            f"Tasks: {stats['total_tasks_executed']}",
        ]
        if project.author:
            tooltip_lines.append(f"Author: {project.author}")
        if project.tags:
            tooltip_lines.append(f"Tags: {', '.join(project.tags)}")

        self.setToolTip("\n".join(tooltip_lines))


class NewProjectDialog(QDialog):
    """Dialog for creating a new project."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(self.lang_manager.get("dialog_new_project", "Nouveau Projet"))
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Project name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Ma recherche 2026")
        form_layout.addRow(
            self.lang_manager.get("label_name", "Nom du projet") + " *:", self.name_input
        )

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description optionnelle...")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow(
            self.lang_manager.get("label_description", "Description") + ":", self.description_input
        )

        # Template selection
        self.template_combo = QComboBox()
        self.template_combo.addItems(
            [
                self.lang_manager.get("template_default", "Standard"),
                self.lang_manager.get("template_academic", "Recherche"),
                self.lang_manager.get("template_legal", "Juridique"),
                self.lang_manager.get("template_creative", "Créatif"),
                self.lang_manager.get("template_technical", "Technique"),
            ]
        )
        form_layout.addRow("Type de projet:", self.template_combo)

        # Favorite checkbox
        self.favorite_checkbox = QCheckBox(
            self.lang_manager.get("label_mark_favorite", "Marquer comme favori")
        )
        form_layout.addRow("", self.favorite_checkbox)

        layout.addLayout(form_layout)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_project_data(self):
        """Get project data from form."""
        template_map = {0: "default", 1: "academic", 2: "legal", 3: "creative", 4: "technical"}

        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "template": template_map[self.template_combo.currentIndex()],
            "is_favorite": self.favorite_checkbox.isChecked(),
        }


class ProjectDashboard(QWidget):
    """Dashboard widget for managing multiple projects."""

    # Signals
    project_selected = pyqtSignal(str)  # Emits project_id when project is opened
    project_created = pyqtSignal(str)  # Emits project_id when new project is created

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_manager = get_language_manager()
        self.project_manager = get_project_manager()
        self.current_filter = "all"  # all, active, archived, favorites
        self.current_sort = "updated"  # name, created, updated, opened
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        """Setup UI components - IMPROVED DESIGN."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with title and stats
        header_layout = QHBoxLayout()

        title_label = QLabel(self.lang_manager.get("projects_dashboard", "Mes Projets"))
        title_label.setStyleSheet(Styles.LABEL_HEADER)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(Styles.LABEL_SUBHEADER)
        header_layout.addWidget(self.stats_label)

        layout.addLayout(header_layout)

        # Search and filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            self.lang_manager.get("placeholder_search", "Rechercher un projet...")
        )
        self.search_input.setStyleSheet(Styles.LINE_EDIT)
        self.search_input.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_input, 3)

        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                self.lang_manager.get("filter_all", "Tous"),
                self.lang_manager.get("filter_active", "Actifs"),
                self.lang_manager.get("filter_archived", "Archivés"),
                self.lang_manager.get("filter_favorites", "Favoris"),
            ]
        )
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo, 1)

        # Sort combo
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(
            [
                self.lang_manager.get("sort_updated", "Modifié"),
                self.lang_manager.get("sort_created", "Créé"),
                self.lang_manager.get("sort_opened", "Ouvert"),
                self.lang_manager.get("sort_name", "Nom"),
            ]
        )
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        filter_layout.addWidget(self.sort_combo, 1)

        layout.addLayout(filter_layout)

        # Projects list
        self.projects_list = QListWidget()
        self.projects_list.setAlternatingRowColors(True)
        self.projects_list.setStyleSheet(Styles.LIST_WIDGET)
        self.projects_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )  # Multi-select
        self.projects_list.itemDoubleClicked.connect(self.on_project_double_clicked)
        self.projects_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.projects_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.projects_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.projects_list)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.new_btn = QPushButton(self.lang_manager.get("btn_new_project", "Nouveau Projet"))
        self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_btn.setToolTip("Créer un nouveau projet")
        self.new_btn.clicked.connect(self.create_new_project)
        button_layout.addWidget(self.new_btn)

        self.open_btn = QPushButton(self.lang_manager.get("btn_open", "Ouvrir"))
        self.open_btn.setEnabled(False)
        self.open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_btn.setToolTip("Ouvrir le projet sélectionné")
        self.open_btn.clicked.connect(self.open_selected_project)
        button_layout.addWidget(self.open_btn)

        self.duplicate_btn = QPushButton(self.lang_manager.get("btn_duplicate", "Dupliquer"))
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.duplicate_btn.setToolTip("Créer une copie du projet sélectionné")
        self.duplicate_btn.clicked.connect(self.duplicate_selected_project)
        button_layout.addWidget(self.duplicate_btn)

        self.rename_btn = QPushButton(self.lang_manager.get("btn_rename", "Renommer"))
        self.rename_btn.setEnabled(False)
        self.rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rename_btn.setToolTip("Renommer le projet sélectionné")
        self.rename_btn.clicked.connect(self.rename_selected_project)
        button_layout.addWidget(self.rename_btn)

        self.favorite_btn = QPushButton(self.lang_manager.get("btn_favorite", "Favori"))
        self.favorite_btn.setEnabled(False)
        self.favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_btn.setToolTip("Marquer comme favori")
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        button_layout.addWidget(self.favorite_btn)

        self.delete_btn = QPushButton(self.lang_manager.get("btn_delete", "Supprimer"))
        self.delete_btn.setEnabled(False)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setToolTip("Archiver ou supprimer le(s) projet(s) sélectionné(s)")
        self.delete_btn.clicked.connect(self.delete_selected_project)
        button_layout.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton(self.lang_manager.get("btn_refresh", "Actualiser"))
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setToolTip("Recharger la liste des projets")
        self.refresh_btn.clicked.connect(self.load_projects)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def load_projects(self):
        """Load and display projects."""
        self.projects_list.clear()

        # Determine which projects to load based on filter
        if self.current_filter == "archived":
            projects = self.project_manager.load_all_projects(include_archived=True)
            projects = [p for p in projects if p.is_archived]
        elif self.current_filter == "favorites":
            projects = self.project_manager.get_favorites()
        elif self.current_filter == "active":
            projects = self.project_manager.load_all_projects(include_archived=False)
        else:  # all
            projects = self.project_manager.load_all_projects(include_archived=True)

        # Apply search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            projects = [
                p
                for p in projects
                if search_text in p.name.lower()
                or search_text in p.description.lower()
                or any(search_text in tag.lower() for tag in p.tags)
            ]

        # Sort projects
        sort_map = {0: "updated", 1: "created", 2: "opened", 3: "name"}
        sort_by = sort_map[self.sort_combo.currentIndex()]

        if sort_by == "name":
            projects.sort(key=lambda p: p.name.lower())
        elif sort_by == "created":
            projects.sort(key=lambda p: p.created_at, reverse=True)
        elif sort_by == "updated":
            projects.sort(key=lambda p: p.updated_at, reverse=True)
        elif sort_by == "opened":
            projects.sort(key=lambda p: p.last_opened_at or datetime.min, reverse=True)

        # Add to list
        for project in projects:
            item = ProjectListItem(project)
            self.projects_list.addItem(item)

        # Update stats
        self.update_stats()

    def update_stats(self):
        """Update statistics label."""
        stats = self.project_manager.get_statistics()
        stats_text = (
            f"{stats['total_projects']} total • "
            f"{stats['active_projects']} active • "
            f"{stats['favorite_projects']} favorites"
        )
        self.stats_label.setText(stats_text)

    def on_search_changed(self):
        """Handle search text change."""
        self.load_projects()

    def on_filter_changed(self, index):
        """Handle filter change."""
        filter_map = {0: "all", 1: "active", 2: "archived", 3: "favorites"}
        self.current_filter = filter_map[index]
        self.load_projects()

    def on_sort_changed(self, index):
        """Handle sort change."""
        self.load_projects()

    def on_selection_changed(self):
        """Handle project selection change."""
        selected_count = len(self.projects_list.selectedItems())
        has_selection = selected_count > 0
        single_selection = selected_count == 1

        # Enable/disable buttons based on selection
        self.open_btn.setEnabled(single_selection)
        self.duplicate_btn.setEnabled(single_selection)
        self.rename_btn.setEnabled(single_selection)
        self.favorite_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

        # Update favorite button text
        if single_selection:
            selected_item = self.projects_list.selectedItems()[0]
            if isinstance(selected_item, ProjectListItem):
                if selected_item.project.is_favorite:
                    self.favorite_btn.setText(self.lang_manager.get("btn_unfavorite", "Unfavorite"))
                else:
                    self.favorite_btn.setText(self.lang_manager.get("btn_favorite", "Favorite"))

        # Update delete button text for bulk operations
        if selected_count > 1:
            self.delete_btn.setText(
                f"{self.lang_manager.get('btn_delete', 'Supprimer')} ({selected_count})"
            )

    def on_project_double_clicked(self, item):
        """Handle double-click on project."""
        if isinstance(item, ProjectListItem):
            self.open_selected_project()

    def create_new_project(self):
        """Create a new project."""
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_project_data()

            if not data["name"]:
                QMessageBox.warning(
                    self,
                    self.lang_manager.get("warning", "Warning"),
                    self.lang_manager.get("msg_project_name_required", "Project name is required"),
                )
                return

            try:
                # Create project
                if data["template"] == "default":
                    project = self.project_manager.create_project(
                        name=data["name"],
                        description=data["description"],
                        is_favorite=data["is_favorite"],
                    )
                else:
                    project = self.project_manager.create_project_from_template(
                        name=data["name"],
                        template_name=data["template"],
                        description=data["description"],
                        is_favorite=data["is_favorite"],
                    )

                # Reload list
                self.load_projects()

                # Emit signal
                self.project_created.emit(project.id)

                QMessageBox.information(
                    self,
                    self.lang_manager.get("success", "Success"),
                    self.lang_manager.get("msg_project_created", "Project created successfully!"),
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.lang_manager.get("error", "Error"),
                    f"{self.lang_manager.get('msg_create_project_error', 'Error creating project')}: {str(e)}",
                )

    def open_selected_project(self):
        """Open the selected project."""
        selected_items = self.projects_list.selectedItems()
        if selected_items and isinstance(selected_items[0], ProjectListItem):
            project_id = selected_items[0].project.id
            self.project_selected.emit(project_id)

    def toggle_favorite(self):
        """Toggle favorite status of selected project."""
        selected_items = self.projects_list.selectedItems()
        if selected_items and isinstance(selected_items[0], ProjectListItem):
            project = selected_items[0].project
            project.is_favorite = not project.is_favorite
            self.project_manager.save_project(project)
            self.load_projects()

    def delete_selected_project(self):
        """Delete the selected project(s) - supports bulk operations."""
        selected_items = self.projects_list.selectedItems()
        if not selected_items:
            return

        selected_projects = [
            item.project for item in selected_items if isinstance(item, ProjectListItem)
        ]
        if not selected_projects:
            return

        # Handle single vs multiple deletions
        if len(selected_projects) == 1:
            project = selected_projects[0]

            # Create custom message box with translated buttons
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle(self.lang_manager.get("dialog_delete_project", "Delete Project"))

            if project.is_archived:
                msg_box.setText(
                    self.lang_manager.get(
                        "msg_delete_archived_project", "Permanently delete this archived project?"
                    )
                )
                archive_btn = None
                delete_btn = msg_box.addButton(
                    self.lang_manager.get("btn_delete_permanent", "Delete Permanently"),
                    QMessageBox.ButtonRole.DestructiveRole,
                )
            else:
                msg_box.setText(
                    self.lang_manager.get(
                        "msg_delete_active_project", "Archive or permanently delete this project?"
                    )
                )
                archive_btn = msg_box.addButton(
                    self.lang_manager.get("btn_archive", "Archive"),
                    QMessageBox.ButtonRole.AcceptRole,
                )
                delete_btn = msg_box.addButton(
                    self.lang_manager.get("btn_delete_permanent", "Delete Permanently"),
                    QMessageBox.ButtonRole.DestructiveRole,
                )

            cancel_btn = msg_box.addButton(
                self.lang_manager.get("btn_cancel", "Cancel"), QMessageBox.ButtonRole.RejectRole
            )
            msg_box.setDefaultButton(cancel_btn)

            msg_box.exec()

            clicked = msg_box.clickedButton()

            if clicked == cancel_btn:
                return
            elif clicked == delete_btn:
                # Permanent delete
                self.project_manager.delete_project(project.id, permanent=True)
                QMessageBox.information(
                    self,
                    self.lang_manager.get("success", "Success"),
                    self.lang_manager.get("msg_project_deleted", "Project deleted permanently"),
                )
            elif clicked == archive_btn:
                # Archive
                self.project_manager.delete_project(project.id, permanent=False)
                QMessageBox.information(
                    self,
                    self.lang_manager.get("success", "Success"),
                    self.lang_manager.get("msg_project_archived", "Project archived"),
                )
        else:
            # Bulk deletion
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setWindowTitle(f"Delete {len(selected_projects)} Projects")
            msg_box.setText(f"Archive or permanently delete {len(selected_projects)} projects?")

            archive_btn = msg_box.addButton("Archive All", QMessageBox.ButtonRole.AcceptRole)
            delete_btn = msg_box.addButton(
                "Delete All Permanently", QMessageBox.ButtonRole.DestructiveRole
            )
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(cancel_btn)

            msg_box.exec()

            clicked = msg_box.clickedButton()

            if clicked == cancel_btn:
                return

            project_ids = [p.id for p in selected_projects]

            if clicked == delete_btn:
                # Permanent delete all
                results = self.project_manager.delete_projects(project_ids, permanent=True)
                success_count = sum(1 for success in results.values() if success)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Deleted {success_count} project(s) permanently.",
                )
            elif clicked == archive_btn:
                # Archive all
                results = self.project_manager.archive_projects(project_ids)
                success_count = sum(1 for success in results.values() if success)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Archived {success_count} project(s).",
                )

        self.load_projects()

    def get_selected_project_id(self):
        """Get the ID of the selected project."""
        selected_items = self.projects_list.selectedItems()
        if selected_items and isinstance(selected_items[0], ProjectListItem):
            return selected_items[0].project.id
        return None

    def duplicate_selected_project(self):
        """Duplicate the selected project."""
        selected_items = self.projects_list.selectedItems()
        if not selected_items or not isinstance(selected_items[0], ProjectListItem):
            return

        project = selected_items[0].project

        # Ask for new name
        new_name, ok = QInputDialog.getText(
            self,
            "Duplicate Project",
            "Enter name for duplicated project:",
            text=f"Copy of {project.name}",
        )

        if ok and new_name:
            try:
                duplicated = self.project_manager.duplicate_project(
                    project.id, new_name=new_name, copy_documents=True
                )

                if duplicated:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"✓ Project '{new_name}' created successfully!",
                    )
                    self.load_projects()
                    self.project_created.emit(duplicated.id)
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Failed to duplicate project.",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error duplicating project: {str(e)}",
                )

    def rename_selected_project(self):
        """Rename the selected project."""
        selected_items = self.projects_list.selectedItems()
        if not selected_items or not isinstance(selected_items[0], ProjectListItem):
            return

        project = selected_items[0].project

        # Ask for new name
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Project",
            "Enter new name for project:",
            text=project.name,
        )

        if ok and new_name and new_name != project.name:
            try:
                success = self.project_manager.rename_project(project.id, new_name)

                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"✓ Project renamed to '{new_name}'!",
                    )
                    self.load_projects()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Failed to rename project.",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error renaming project: {str(e)}",
                )

    def show_context_menu(self, position):
        """Show context menu for project list."""
        item = self.projects_list.itemAt(position)
        if not item or not isinstance(item, ProjectListItem):
            return

        project = item.project

        menu = QMenu(self)

        # Open action
        open_action = menu.addAction("📂 Open")
        open_action.triggered.connect(self.open_selected_project)

        menu.addSeparator()

        # Duplicate action
        duplicate_action = menu.addAction("📋 Duplicate")
        duplicate_action.triggered.connect(self.duplicate_selected_project)

        # Rename action
        rename_action = menu.addAction("✏️ Rename")
        rename_action.triggered.connect(self.rename_selected_project)

        menu.addSeparator()

        # Favorite action
        if project.is_favorite:
            favorite_action = menu.addAction("⭐ Remove from Favorites")
        else:
            favorite_action = menu.addAction("☆ Add to Favorites")
        favorite_action.triggered.connect(self.toggle_favorite)

        menu.addSeparator()

        # Archive/Delete actions
        if project.is_archived:
            restore_action = menu.addAction("♻️ Restore")
            restore_action.triggered.connect(lambda: self._restore_project(project.id))

            menu.addSeparator()

            delete_action = menu.addAction("🗑️ Delete Permanently")
            delete_action.triggered.connect(self.delete_selected_project)
        else:
            archive_action = menu.addAction("📦 Archive")
            archive_action.triggered.connect(self.delete_selected_project)

        # Show menu at cursor position
        menu.exec(self.projects_list.mapToGlobal(position))

    def _restore_project(self, project_id: str):
        """Restore an archived project."""
        try:
            success = self.project_manager.restore_project(project_id)
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "✓ Project restored successfully!",
                )
                self.load_projects()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to restore project.",
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error restoring project: {str(e)}",
            )
