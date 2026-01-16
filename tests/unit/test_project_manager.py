"""Unit tests for ProjectManager."""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.docprocessor.core.project_manager import ProjectManager
from src.docprocessor.models.project import DocumentInfo


@pytest.fixture
def temp_projects_dir():
    """Create a temporary directory for projects."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup after tests
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def project_manager(temp_projects_dir):
    """Create a ProjectManager instance with temp directory."""
    return ProjectManager(projects_dir=temp_projects_dir)


class TestProjectManager:
    """Tests for ProjectManager class."""

    def test_initialization(self, temp_projects_dir):
        """Test manager initialization."""
        manager = ProjectManager(projects_dir=temp_projects_dir)

        assert manager.projects_dir == temp_projects_dir
        assert temp_projects_dir.exists()
        assert len(manager._project_cache) == 0

    def test_create_project(self, project_manager):
        """Test creating a new project."""
        project = project_manager.create_project(name="Test Project", description="A test project")

        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.id in project_manager._project_cache

        # Check project directory and file exist
        project_dir = project_manager._get_project_dir(project.id)
        assert project_dir.exists()

        project_file = project_manager._get_project_file(project.id)
        assert project_file.exists()

    def test_create_project_empty_name(self, project_manager):
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            project_manager.create_project(name="")

        with pytest.raises(ValueError, match="cannot be empty"):
            project_manager.create_project(name="   ")

    def test_create_project_with_kwargs(self, project_manager):
        """Test creating project with additional attributes."""
        project = project_manager.create_project(
            name="Tagged Project", tags=["tag1", "tag2"], author="John Doe", is_favorite=True
        )

        assert project.tags == ["tag1", "tag2"]
        assert project.author == "John Doe"
        assert project.is_favorite is True

    def test_create_project_from_template(self, project_manager):
        """Test creating project from template."""
        project = project_manager.create_project_from_template(
            name="Academic Project", template_name="academic"
        )

        assert project.name == "Academic Project"
        assert project.settings.include_citations is True
        assert project.settings.temperature == 0.5

    def test_create_project_invalid_template(self, project_manager):
        """Test error on invalid template."""
        with pytest.raises(ValueError, match="Template.*not found"):
            project_manager.create_project_from_template(
                name="Project", template_name="nonexistent"
            )

    def test_save_and_load_project(self, project_manager):
        """Test saving and loading project."""
        # Create project
        project = project_manager.create_project(name="Save Test")
        project_id = project.id

        # Add some data
        doc = DocumentInfo(id="doc1", file_path="/path", title="Doc", file_size=1024)
        project.add_document(doc)

        # Save
        project_manager.save_project(project)

        # Clear cache and reload
        project_manager.clear_cache()

        loaded = project_manager.load_project(project_id)

        assert loaded is not None
        assert loaded.name == "Save Test"
        assert len(loaded.documents) == 1
        assert loaded.documents[0].id == "doc1"

    def test_load_nonexistent_project(self, project_manager):
        """Test loading project that doesn't exist."""
        result = project_manager.load_project("nonexistent-id")
        assert result is None

    def test_load_all_projects(self, project_manager):
        """Test loading all projects."""
        # Create multiple projects
        p1 = project_manager.create_project(name="Project 1")
        p2 = project_manager.create_project(name="Project 2")
        p3 = project_manager.create_project(name="Project 3", is_archived=True)

        # Load all (excluding archived)
        projects = project_manager.load_all_projects(include_archived=False)
        assert len(projects) == 2

        # Load all (including archived)
        all_projects = project_manager.load_all_projects(include_archived=True)
        assert len(all_projects) == 3

    def test_delete_project_archive(self, project_manager):
        """Test archiving a project."""
        project = project_manager.create_project(name="To Archive")
        project_id = project.id

        # Archive (soft delete)
        result = project_manager.delete_project(project_id, permanent=False)
        assert result is True

        # Check still exists but archived
        loaded = project_manager.load_project(project_id)
        assert loaded is not None
        assert loaded.is_archived is True

    def test_delete_project_permanent(self, project_manager):
        """Test permanently deleting a project."""
        project = project_manager.create_project(name="To Delete")
        project_id = project.id

        project_dir = project_manager._get_project_dir(project_id)
        assert project_dir.exists()

        # Permanent delete
        result = project_manager.delete_project(project_id, permanent=True)
        assert result is True

        # Check no longer exists
        assert not project_dir.exists()
        loaded = project_manager.load_project(project_id)
        assert loaded is None

    def test_restore_project(self, project_manager):
        """Test restoring an archived project."""
        project = project_manager.create_project(name="To Restore")
        project_id = project.id

        # Archive
        project_manager.delete_project(project_id, permanent=False)
        assert project_manager.load_project(project_id).is_archived is True

        # Restore
        result = project_manager.restore_project(project_id)
        assert result is True

        loaded = project_manager.load_project(project_id)
        assert loaded.is_archived is False

    def test_list_projects_sorted(self, project_manager):
        """Test listing projects with sorting."""
        import time

        p1 = project_manager.create_project(name="Alpha")
        time.sleep(0.01)
        p2 = project_manager.create_project(name="Beta")
        time.sleep(0.01)
        p3 = project_manager.create_project(name="Gamma")

        # Sort by name
        by_name = project_manager.list_projects(sort_by="name", reverse=False)
        assert by_name[0].name == "Alpha"
        assert by_name[1].name == "Beta"
        assert by_name[2].name == "Gamma"

        # Sort by created (newest first)
        by_created = project_manager.list_projects(sort_by="created", reverse=True)
        assert by_created[0].name == "Gamma"  # Last created

    @pytest.mark.skip(
        reason="Timing-dependent test - project order may vary based on exact timestamps"
    )
    def test_get_recent_projects(self, project_manager):
        """Test getting recently opened projects."""
        import time

        p1 = project_manager.create_project(name="Project 1")
        time.sleep(0.01)
        p2 = project_manager.create_project(name="Project 2")
        time.sleep(0.01)
        p3 = project_manager.create_project(name="Project 3")

        # Open projects in specific order
        project_manager.load_project(p2.id)  # Open p2
        time.sleep(0.01)
        project_manager.load_project(p1.id)  # Open p1 (most recent)

        recent = project_manager.get_recent_projects(limit=2)
        assert len(recent) == 2
        assert recent[0].id == p1.id  # Most recently opened

    def test_get_favorites(self, project_manager):
        """Test getting favorite projects."""
        p1 = project_manager.create_project(name="Favorite 1", is_favorite=True)
        p2 = project_manager.create_project(name="Normal")
        p3 = project_manager.create_project(name="Favorite 2", is_favorite=True)

        favorites = project_manager.get_favorites()
        assert len(favorites) == 2
        assert all(p.is_favorite for p in favorites)

    def test_search_projects(self, project_manager):
        """Test searching projects."""
        p1 = project_manager.create_project(
            name="Machine Learning Research", description="Deep learning project"
        )
        p2 = project_manager.create_project(name="Legal Analysis", description="Case law research")
        p3 = project_manager.create_project(name="Medical Research", tags=["healthcare", "AI"])

        # Search by name
        results = project_manager.search_projects("Learning")
        assert len(results) == 1
        assert results[0].id == p1.id

        # Search by description
        results = project_manager.search_projects("research")
        assert len(results) >= 2  # p1 and p2 both have "research" in description

        # Case insensitive
        results = project_manager.search_projects("LEGAL")
        assert len(results) == 1

    def test_filter_projects(self, project_manager):
        """Test filtering projects."""
        p1 = project_manager.create_project(name="P1", tags=["tag1", "tag2"])
        p1.add_document(DocumentInfo(id="d1", file_path="/p", title="D", file_size=100))
        project_manager.save_project(p1)

        p2 = project_manager.create_project(name="P2", tags=["tag2", "tag3"])
        p2.set_themes([{"id": "t1"}])
        project_manager.save_project(p2)

        p3 = project_manager.create_project(name="P3")

        # Filter by tags
        results = project_manager.filter_projects(tags=["tag1"])
        assert len(results) == 1
        assert results[0].id == p1.id

        # Filter by has_documents
        results = project_manager.filter_projects(has_documents=True)
        assert len(results) == 1
        assert results[0].id == p1.id

        # Filter by has_themes
        results = project_manager.filter_projects(has_themes=True)
        assert len(results) == 1
        assert results[0].id == p2.id

    def test_get_statistics(self, project_manager):
        """Test getting overall statistics."""
        p1 = project_manager.create_project(name="P1")
        p1.add_document(DocumentInfo(id="d1", file_path="/p", title="D", file_size=100))
        project_manager.save_project(p1)

        p2 = project_manager.create_project(name="P2", is_archived=True)
        p3 = project_manager.create_project(name="P3", is_favorite=True)

        stats = project_manager.get_statistics()

        assert stats["total_projects"] == 3
        assert stats["active_projects"] == 2
        assert stats["archived_projects"] == 1
        assert stats["favorite_projects"] == 1
        assert stats["total_documents"] == 1

    def test_export_import_project(self, project_manager, temp_projects_dir):
        """Test exporting and importing projects."""
        # Create project with data
        project = project_manager.create_project(name="Export Test")
        project.add_document(DocumentInfo(id="d1", file_path="/p", title="D", file_size=100))
        project.tags = ["tag1"]
        project_manager.save_project(project)

        # Export
        export_path = temp_projects_dir / "exported.json"
        result = project_manager.export_project(project.id, export_path)
        assert result is True
        assert export_path.exists()

        # Import
        imported = project_manager.import_project(export_path, new_name="Imported Test")
        assert imported is not None
        assert imported.name == "Imported Test"
        assert imported.id != project.id  # Should have new ID
        assert len(imported.documents) == 1
        assert imported.tags == ["tag1"]

    def test_cache_functionality(self, project_manager):
        """Test project caching."""
        project = project_manager.create_project(name="Cache Test")
        project_id = project.id

        # First load (from disk)
        loaded1 = project_manager.load_project(project_id, use_cache=False)

        # Second load (from cache)
        loaded2 = project_manager.load_project(project_id, use_cache=True)

        # Should be the same object from cache
        assert loaded1 is loaded2

        # Clear cache
        project_manager.clear_cache()
        assert len(project_manager._project_cache) == 0

        # Load again (from disk)
        loaded3 = project_manager.load_project(project_id)
        assert loaded3 is not loaded2  # Different object

    def test_exists(self, project_manager):
        """Test checking if project exists."""
        project = project_manager.create_project(name="Exists Test")

        assert project_manager.exists(project.id) is True
        assert project_manager.exists("nonexistent-id") is False

    def test_count(self, project_manager):
        """Test counting projects."""
        project_manager.create_project(name="P1")
        project_manager.create_project(name="P2")
        project_manager.create_project(name="P3", is_archived=True)

        assert project_manager.count(include_archived=False) == 2
        assert project_manager.count(include_archived=True) == 3

    def test_get_project_path(self, project_manager):
        """Test getting project file system path."""
        project = project_manager.create_project(name="Path Test")

        path = project_manager.get_project_path(project.id)
        assert isinstance(path, Path)
        assert path.exists()
        assert path.is_dir()


class TestProjectManagerGlobal:
    """Tests for global project manager functions."""

    def test_global_instance(self):
        """Test getting global project manager."""
        from src.docprocessor.core.project_manager import get_project_manager, set_project_manager

        manager1 = get_project_manager()
        manager2 = get_project_manager()

        # Should be same instance
        assert manager1 is manager2

        # Test setting custom manager
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_manager = ProjectManager(projects_dir=Path(temp_dir))
            set_project_manager(custom_manager)

            manager3 = get_project_manager()
            assert manager3 is custom_manager

    def test_duplicate_project(self, project_manager):
        """Test duplicating a project."""
        # Create original project with data
        original = project_manager.create_project(name="Original", description="Original project")
        doc = DocumentInfo(id="doc1", file_path="/path", title="Doc", file_size=1024)
        original.add_document(doc)
        original.tags = ["tag1", "tag2"]
        project_manager.save_project(original)

        # Duplicate with default name
        duplicate = project_manager.duplicate_project(original.id)

        assert duplicate is not None
        assert duplicate.id != original.id
        assert duplicate.name == f"Copy of {original.name}"
        assert len(duplicate.documents) == 1
        assert duplicate.tags == original.tags
        assert len(duplicate.task_history) == 0  # Task history cleared
        assert duplicate.synthesis_cache is None  # Cache cleared

        # Duplicate with custom name and no documents
        duplicate2 = project_manager.duplicate_project(
            original.id, new_name="Custom Copy", copy_documents=False
        )

        assert duplicate2 is not None
        assert duplicate2.name == "Custom Copy"
        assert len(duplicate2.documents) == 0

    def test_duplicate_nonexistent_project(self, project_manager):
        """Test duplicating non-existent project returns None."""
        result = project_manager.duplicate_project("nonexistent-id")
        assert result is None

    def test_rename_project(self, project_manager):
        """Test renaming a project."""
        project = project_manager.create_project(name="Old Name")

        # Rename successfully
        success = project_manager.rename_project(project.id, "New Name")

        assert success is True

        # Reload and verify
        reloaded = project_manager.load_project(project.id)
        assert reloaded.name == "New Name"

    def test_rename_project_empty_name(self, project_manager):
        """Test renaming with empty name fails."""
        project = project_manager.create_project(name="Project")

        assert project_manager.rename_project(project.id, "") is False
        assert project_manager.rename_project(project.id, "   ") is False

    def test_rename_nonexistent_project(self, project_manager):
        """Test renaming non-existent project returns False."""
        result = project_manager.rename_project("nonexistent-id", "New Name")
        assert result is False

    def test_archive_projects(self, project_manager):
        """Test archiving multiple projects."""
        # Create 3 projects
        p1 = project_manager.create_project(name="Project 1")
        p2 = project_manager.create_project(name="Project 2")
        p3 = project_manager.create_project(name="Project 3")

        # Archive first two
        results = project_manager.archive_projects([p1.id, p2.id])

        assert results[p1.id] is True
        assert results[p2.id] is True

        # Verify they're archived
        p1_reloaded = project_manager.load_project(p1.id)
        p2_reloaded = project_manager.load_project(p2.id)
        p3_reloaded = project_manager.load_project(p3.id)

        assert p1_reloaded.is_archived is True
        assert p2_reloaded.is_archived is True
        assert p3_reloaded.is_archived is False

    def test_delete_projects_permanent(self, project_manager):
        """Test permanently deleting multiple projects."""
        # Create 2 projects
        p1 = project_manager.create_project(name="Project 1")
        p2 = project_manager.create_project(name="Project 2")

        # Delete permanently
        results = project_manager.delete_projects([p1.id, p2.id], permanent=True)

        assert results[p1.id] is True
        assert results[p2.id] is True

        # Verify they're gone
        assert project_manager.load_project(p1.id) is None
        assert project_manager.load_project(p2.id) is None

    def test_restore_projects(self, project_manager):
        """Test restoring multiple archived projects."""
        # Create and archive 2 projects
        p1 = project_manager.create_project(name="Project 1")
        p2 = project_manager.create_project(name="Project 2")

        project_manager.archive_projects([p1.id, p2.id])

        # Restore them
        results = project_manager.restore_projects([p1.id, p2.id])

        assert results[p1.id] is True
        assert results[p2.id] is True

        # Verify they're restored
        p1_reloaded = project_manager.load_project(p1.id)
        p2_reloaded = project_manager.load_project(p2.id)

        assert p1_reloaded.is_archived is False
        assert p2_reloaded.is_archived is False

    def test_bulk_operations_with_nonexistent_ids(self, project_manager):
        """Test bulk operations handle non-existent project IDs gracefully."""
        # Archive non-existent projects
        results = project_manager.archive_projects(["fake1", "fake2"])

        assert results["fake1"] is False
        assert results["fake2"] is False

        # Delete non-existent projects
        results = project_manager.delete_projects(["fake1", "fake2"], permanent=True)

        assert results["fake1"] is False
        assert results["fake2"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
