"""Project Manager for multi-project support.

Handles CRUD operations for projects:
- Create new projects
- Load existing projects
- Save projects
- List/search projects
- Delete projects
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import settings

from ..models.project import Project, ProjectSettings


class ProjectManager:
    """Manages document processing projects.

    Responsibilities:
    - Project file system management
    - CRUD operations
    - Project discovery and listing
    - Search and filtering
    """

    def __init__(self, projects_dir: Optional[Path] = None):
        """Initialize project manager.

        Args:
            projects_dir: Directory where projects are stored.
                         Defaults to {app_data}/projects
        """
        if projects_dir is None:
            projects_dir = settings.projects_dir

        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

        # Cache of loaded projects (project_id -> Project)
        self._project_cache: Dict[str, Project] = {}

    # ========== Project Creation ==========

    def create_project(
        self, name: str, description: str = "", settings: Optional[ProjectSettings] = None, **kwargs
    ) -> Project:
        """Create a new project.

        Args:
            name: Project name
            description: Optional project description
            settings: Optional project settings (uses defaults if not provided)
            **kwargs: Additional project attributes (tags, author, etc.)

        Returns:
            Newly created Project instance

        Raises:
            ValueError: If project name is empty
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty")

        # Create project instance
        project = Project(
            name=name.strip(),
            description=description,
            settings=settings or ProjectSettings(),
            **kwargs,
        )

        # Create project directory
        project_dir = self._get_project_dir(project.id)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save project file
        self.save_project(project)

        # Add to cache
        self._project_cache[project.id] = project

        return project

    def create_project_from_template(self, name: str, template_name: str, **kwargs) -> Project:
        """Create a project from a template.

        Args:
            name: Project name
            template_name: Name of template to use
            **kwargs: Additional project attributes

        Returns:
            Newly created Project instance

        Raises:
            ValueError: If template doesn't exist
        """
        # Get template settings
        template_settings = self._get_template_settings(template_name)
        if template_settings is None:
            raise ValueError(f"Template '{template_name}' not found")

        return self.create_project(name=name, settings=template_settings, **kwargs)

    # ========== Project Loading ==========

    def load_project(self, project_id: str, use_cache: bool = True) -> Optional[Project]:
        """Load a project by ID.

        Args:
            project_id: Project ID
            use_cache: Whether to use cached version if available

        Returns:
            Project instance or None if not found
        """
        # Check cache first
        if use_cache and project_id in self._project_cache:
            return self._project_cache[project_id]

        # Load from disk
        project_file = self._get_project_file(project_id)
        if not project_file.exists():
            return None

        try:
            project = Project.load_from_file(project_file)
            project.mark_opened()  # Update last opened timestamp
            self.save_project(project)  # Save updated timestamp

            # Update cache
            self._project_cache[project_id] = project

            return project
        except Exception as e:
            print(f"Error loading project {project_id}: {e}")
            return None

    def load_all_projects(self, include_archived: bool = False) -> List[Project]:
        """Load all projects.

        Args:
            include_archived: Whether to include archived projects

        Returns:
            List of all projects
        """
        projects = []

        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            project_id = project_dir.name
            project = self.load_project(project_id)

            if project:
                if include_archived or not project.is_archived:
                    projects.append(project)

        return projects

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID (alias for load_project).

        Args:
            project_id: Project ID

        Returns:
            Project instance or None if not found
        """
        return self.load_project(project_id)

    # ========== Project Saving ==========

    def save_project(self, project: Project):
        """Save a project to disk.

        Args:
            project: Project to save
        """
        project.update_timestamp()
        project_file = self._get_project_file(project.id)
        project_file.parent.mkdir(parents=True, exist_ok=True)
        project.save_to_file(project_file)

        # Update cache
        self._project_cache[project.id] = project

    def save_all_projects(self):
        """Save all cached projects to disk."""
        for project in self._project_cache.values():
            self.save_project(project)

    # ========== Project Deletion ==========

    def delete_project(self, project_id: str, permanent: bool = False) -> bool:
        """Delete a project.

        Args:
            project_id: Project ID to delete
            permanent: If True, permanently delete. If False, just archive.

        Returns:
            True if successful, False if project not found
        """
        project = self.load_project(project_id)
        if not project:
            return False

        if permanent:
            # Permanently delete project directory
            project_dir = self._get_project_dir(project_id)
            if project_dir.exists():
                shutil.rmtree(project_dir)

            # Remove from cache
            if project_id in self._project_cache:
                del self._project_cache[project_id]

            return True
        else:
            # Just archive it
            project.is_archived = True
            self.save_project(project)
            return True

    def restore_project(self, project_id: str) -> bool:
        """Restore an archived project.

        Args:
            project_id: Project ID to restore

        Returns:
            True if successful, False if project not found
        """
        project = self.load_project(project_id)
        if not project:
            return False

        project.is_archived = False
        self.save_project(project)
        return True

    # ========== Project Listing & Search ==========

    def list_projects(
        self, include_archived: bool = False, sort_by: str = "updated", reverse: bool = True
    ) -> List[Project]:
        """List projects with sorting.

        Args:
            include_archived: Whether to include archived projects
            sort_by: Sort field ('name', 'created', 'updated', 'opened')
            reverse: Sort in reverse order (newest first)

        Returns:
            Sorted list of projects
        """
        projects = self.load_all_projects(include_archived=include_archived)

        # Sort projects
        if sort_by == "name":
            projects.sort(key=lambda p: p.name.lower(), reverse=reverse)
        elif sort_by == "created":
            projects.sort(key=lambda p: p.created_at, reverse=reverse)
        elif sort_by == "updated":
            projects.sort(key=lambda p: p.updated_at, reverse=reverse)
        elif sort_by == "opened":
            projects.sort(key=lambda p: p.last_opened_at or datetime.min, reverse=reverse)

        return projects

    def get_recent_projects(self, limit: int = 10) -> List[Project]:
        """Get recently opened projects.

        Args:
            limit: Maximum number of projects to return

        Returns:
            List of recently opened projects
        """
        projects = self.list_projects(include_archived=False, sort_by="opened", reverse=True)
        return projects[:limit]

    def get_favorites(self) -> List[Project]:
        """Get favorite projects.

        Returns:
            List of favorite projects
        """
        projects = self.load_all_projects(include_archived=False)
        return [p for p in projects if p.is_favorite]

    def search_projects(self, query: str, search_in: List[str] = None) -> List[Project]:
        """Search projects by text query.

        Args:
            query: Search query
            search_in: Fields to search in ['name', 'description', 'tags', 'author']
                      Defaults to all fields

        Returns:
            List of matching projects
        """
        if search_in is None:
            search_in = ["name", "description", "tags", "author"]

        query_lower = query.lower()
        projects = self.load_all_projects(include_archived=False)
        matches = []

        for project in projects:
            # Search in specified fields
            if "name" in search_in and query_lower in project.name.lower():
                matches.append(project)
                continue

            if "description" in search_in and query_lower in project.description.lower():
                matches.append(project)
                continue

            if "tags" in search_in and any(query_lower in tag.lower() for tag in project.tags):
                matches.append(project)
                continue

            if "author" in search_in and query_lower in project.author.lower():
                matches.append(project)
                continue

        return matches

    def filter_projects(
        self,
        tags: Optional[List[str]] = None,
        has_documents: Optional[bool] = None,
        has_themes: Optional[bool] = None,
    ) -> List[Project]:
        """Filter projects by criteria.

        Args:
            tags: Filter by tags (any match)
            has_documents: Filter by presence of documents
            has_themes: Filter by presence of themes

        Returns:
            List of matching projects
        """
        projects = self.load_all_projects(include_archived=False)
        filtered = []

        for project in projects:
            # Check tag filter
            if tags and not any(tag in project.tags for tag in tags):
                continue

            # Check documents filter
            if has_documents is not None:
                if has_documents and len(project.documents) == 0:
                    continue
                if not has_documents and len(project.documents) > 0:
                    continue

            # Check themes filter
            if has_themes is not None:
                if has_themes and len(project.themes) == 0:
                    continue
                if not has_themes and len(project.themes) > 0:
                    continue

            filtered.append(project)

        return filtered

    # ========== Project Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about all projects.

        Returns:
            Dictionary with statistics
        """
        projects = self.load_all_projects(include_archived=True)

        total_documents = sum(len(p.documents) for p in projects)
        total_tasks = sum(len(p.task_history) for p in projects)
        total_themes = sum(len(p.themes) for p in projects)

        return {
            "total_projects": len(projects),
            "active_projects": sum(1 for p in projects if not p.is_archived),
            "archived_projects": sum(1 for p in projects if p.is_archived),
            "favorite_projects": sum(1 for p in projects if p.is_favorite),
            "total_documents": total_documents,
            "total_tasks_executed": total_tasks,
            "total_themes": total_themes,
        }

    # ========== Project Import/Export ==========

    def export_project(self, project_id: str, export_path: Path) -> bool:
        """Export a project to a file (for sharing/backup).

        Args:
            project_id: Project ID to export
            export_path: Path to export file (.json)

        Returns:
            True if successful
        """
        project = self.load_project(project_id)
        if not project:
            return False

        try:
            project.save_to_file(export_path)
            return True
        except Exception as e:
            print(f"Error exporting project: {e}")
            return False

    def import_project(
        self, import_path: Path, new_name: Optional[str] = None
    ) -> Optional[Project]:
        """Import a project from a file.

        Args:
            import_path: Path to project file (.json)
            new_name: Optional new name for imported project

        Returns:
            Imported Project instance or None on failure
        """
        try:
            project = Project.load_from_file(import_path)

            # Generate new ID to avoid conflicts
            project.id = str(Project().id)  # Generate new UUID

            if new_name:
                project.name = new_name

            # Save to projects directory
            self.save_project(project)

            return project
        except Exception as e:
            print(f"Error importing project: {e}")
            return None

    # ========== Project Duplication & Renaming ==========

    def duplicate_project(
        self, project_id: str, new_name: Optional[str] = None, copy_documents: bool = True
    ) -> Optional[Project]:
        """Duplicate an existing project.

        Args:
            project_id: ID of project to duplicate
            new_name: Name for the duplicated project (defaults to "Copy of {original_name}")
            copy_documents: Whether to copy document references

        Returns:
            Duplicated Project instance or None on failure
        """
        original = self.load_project(project_id)
        if not original:
            return None

        try:
            # Create copy with new ID
            import uuid
            from copy import deepcopy

            duplicated = deepcopy(original)
            duplicated.id = str(uuid.uuid4())

            # Set new name
            if new_name:
                duplicated.name = new_name
            else:
                duplicated.name = f"Copy of {original.name}"

            # Reset timestamps
            duplicated.created_at = datetime.now()
            duplicated.updated_at = datetime.now()
            duplicated.last_opened_at = None

            # Optionally clear documents
            if not copy_documents:
                duplicated.documents = []

            # Clear task history and synthesis cache (fresh start)
            duplicated.task_history = []
            duplicated.synthesis_cache = None

            # Save duplicated project
            self.save_project(duplicated)

            return duplicated
        except Exception as e:
            print(f"Error duplicating project: {e}")
            return None

    def rename_project(self, project_id: str, new_name: str) -> bool:
        """Rename a project.

        Args:
            project_id: ID of project to rename
            new_name: New name for the project

        Returns:
            True if successful, False otherwise
        """
        if not new_name or not new_name.strip():
            return False

        project = self.load_project(project_id)
        if not project:
            return False

        try:
            project.name = new_name.strip()
            self.save_project(project)
            return True
        except Exception as e:
            print(f"Error renaming project: {e}")
            return False

    # ========== Bulk Operations ==========

    def archive_projects(self, project_ids: List[str]) -> Dict[str, bool]:
        """Archive multiple projects.

        Args:
            project_ids: List of project IDs to archive

        Returns:
            Dictionary mapping project_id to success status
        """
        results = {}
        for project_id in project_ids:
            results[project_id] = self.delete_project(project_id, permanent=False)
        return results

    def delete_projects(self, project_ids: List[str], permanent: bool = False) -> Dict[str, bool]:
        """Delete multiple projects.

        Args:
            project_ids: List of project IDs to delete
            permanent: If True, permanently delete. If False, archive.

        Returns:
            Dictionary mapping project_id to success status
        """
        results = {}
        for project_id in project_ids:
            results[project_id] = self.delete_project(project_id, permanent=permanent)
        return results

    def restore_projects(self, project_ids: List[str]) -> Dict[str, bool]:
        """Restore multiple archived projects.

        Args:
            project_ids: List of project IDs to restore

        Returns:
            Dictionary mapping project_id to success status
        """
        results = {}
        for project_id in project_ids:
            results[project_id] = self.restore_project(project_id)
        return results

    # ========== Helper Methods ==========

    def _get_project_dir(self, project_id: str) -> Path:
        """Get directory for a project.

        Args:
            project_id: Project ID

        Returns:
            Path to project directory
        """
        return self.projects_dir / project_id

    def _get_project_file(self, project_id: str) -> Path:
        """Get project file path.

        Args:
            project_id: Project ID

        Returns:
            Path to project.json file
        """
        return self._get_project_dir(project_id) / "project.json"

    def _get_template_settings(self, template_name: str) -> Optional[ProjectSettings]:
        """Get settings for a project template.

        Args:
            template_name: Template name

        Returns:
            ProjectSettings or None if template not found
        """
        templates = {
            "default": ProjectSettings(),
            "academic": ProjectSettings(
                default_output_format="markdown+docx", include_citations=True, temperature=0.5
            ),
            "legal": ProjectSettings(
                default_output_format="docx", include_citations=True, temperature=0.3
            ),
            "creative": ProjectSettings(
                default_output_format="markdown", include_citations=False, temperature=0.8
            ),
            "technical": ProjectSettings(
                default_output_format="markdown+docx", include_citations=True, temperature=0.4
            ),
        }

        return templates.get(template_name)

    def exists(self, project_id: str) -> bool:
        """Check if a project exists.

        Args:
            project_id: Project ID

        Returns:
            True if project exists
        """
        return self._get_project_file(project_id).exists()

    def count(self, include_archived: bool = False) -> int:
        """Count total number of projects.

        Args:
            include_archived: Whether to include archived projects

        Returns:
            Number of projects
        """
        return len(self.load_all_projects(include_archived=include_archived))

    def clear_cache(self):
        """Clear the project cache."""
        self._project_cache.clear()

    def get_project_path(self, project_id: str) -> Path:
        """Get the file system path for a project.

        Args:
            project_id: Project ID

        Returns:
            Path to project directory
        """
        return self._get_project_dir(project_id)


# ========== Global Instance ==========

_global_manager: Optional[ProjectManager] = None


def get_project_manager() -> ProjectManager:
    """Get the global project manager instance.

    Returns:
        ProjectManager instance
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = ProjectManager()
    return _global_manager


def set_project_manager(manager: ProjectManager):
    """Set the global project manager instance.

    Args:
        manager: ProjectManager instance to use globally
    """
    global _global_manager
    _global_manager = manager
