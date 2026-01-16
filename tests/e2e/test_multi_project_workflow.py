"""End-to-end tests for multi-project workflows.

These tests validate complete user workflows from start to finish,
ensuring that the multi-project system works correctly in realistic scenarios.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from docprocessor.core.project_manager import (
    ProjectManager,
    get_project_manager,
    set_project_manager,
)
from docprocessor.models.project import DocumentInfo


@pytest.fixture
def temp_projects_dir():
    """Create a temporary directory for projects."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def isolated_project_manager(temp_projects_dir):
    """Create an isolated project manager for testing."""
    manager = ProjectManager(projects_dir=temp_projects_dir)
    # Save current global manager
    original_manager = get_project_manager()
    # Set our test manager as global
    set_project_manager(manager)
    yield manager
    # Restore original manager
    set_project_manager(original_manager)


@pytest.fixture
def sample_document_path(temp_projects_dir):
    """Create a sample document file."""
    doc_path = temp_projects_dir / "sample_document.txt"
    doc_path.write_text("This is a sample document for testing.\n" * 100)
    return doc_path


@pytest.mark.e2e
class TestProjectCreationWorkflow:
    """Test complete project creation workflow."""

    def test_create_project_from_scratch(self, isolated_project_manager):
        """Test creating a new project and setting it up."""
        manager = isolated_project_manager

        # Step 1: Create project
        project = manager.create_project(
            name="Research Project",
            description="My research on AI",
            tags=["AI", "research"],
            author="Test User",
        )

        assert project is not None
        assert project.name == "Research Project"
        assert project.author == "Test User"
        assert "AI" in project.tags

        # Step 2: Verify project is saved
        project_dir = manager._get_project_dir(project.id)
        assert project_dir.exists()

        # Step 3: Load project from disk
        loaded = manager.load_project(project.id)
        assert loaded is not None
        assert loaded.name == project.name
        assert loaded.id == project.id

        # Step 4: Verify project appears in list
        all_projects = manager.list_projects()
        assert any(p.id == project.id for p in all_projects)

    def test_create_project_from_template(self, isolated_project_manager):
        """Test creating project from a template."""
        manager = isolated_project_manager

        # Create from academic template
        project = manager.create_project_from_template(
            name="Academic Paper", template_name="academic"
        )

        assert project.name == "Academic Paper"
        # Academic template should have specific settings
        assert project.settings.include_citations is True
        assert project.settings.temperature == 0.5

        # Verify saved correctly
        loaded = manager.load_project(project.id)
        assert loaded.settings.include_citations is True


@pytest.mark.e2e
class TestProjectSwitchingWorkflow:
    """Test switching between multiple projects."""

    def test_switch_between_projects(self, isolated_project_manager):
        """Test creating and switching between multiple projects."""
        manager = isolated_project_manager

        # Create multiple projects
        project1 = manager.create_project(name="Project Alpha")
        project2 = manager.create_project(name="Project Beta")
        project3 = manager.create_project(name="Project Gamma")

        # Add data to each project
        doc1 = DocumentInfo(id="doc1", file_path="/path1", title="Doc1", file_size=1000)
        project1.add_document(doc1)
        manager.save_project(project1)

        doc2 = DocumentInfo(id="doc2", file_path="/path2", title="Doc2", file_size=2000)
        project2.add_document(doc2)
        manager.save_project(project2)

        # Load each project and verify state isolation
        p1_loaded = manager.load_project(project1.id)
        assert len(p1_loaded.documents) == 1
        assert p1_loaded.documents[0].id == "doc1"

        p2_loaded = manager.load_project(project2.id)
        assert len(p2_loaded.documents) == 1
        assert p2_loaded.documents[0].id == "doc2"

        p3_loaded = manager.load_project(project3.id)
        assert len(p3_loaded.documents) == 0

        # Verify projects are independent
        assert p1_loaded.id != p2_loaded.id != p3_loaded.id

    def test_project_state_persistence(self, isolated_project_manager):
        """Test that project state persists across saves and loads."""
        manager = isolated_project_manager

        # Create and populate project
        project = manager.create_project(name="Persistent Project")

        # Add documents
        doc1 = DocumentInfo(id="d1", file_path="/p1", title="D1", file_size=100)
        doc2 = DocumentInfo(id="d2", file_path="/p2", title="D2", file_size=200)
        project.add_document(doc1)
        project.add_document(doc2)

        # Add themes
        themes = [
            {"id": "t1", "label": "Theme 1", "chunk_ids": ["c1", "c2"]},
            {"id": "t2", "label": "Theme 2", "chunk_ids": ["c3", "c4"]},
        ]
        project.set_themes(themes)

        # Update settings
        project.settings.temperature = 0.8
        project.settings.include_citations = False

        # Save
        manager.save_project(project)
        project_id = project.id

        # Clear cache and reload
        manager.clear_cache()
        loaded = manager.load_project(project_id)

        # Verify all state persisted
        assert loaded.name == "Persistent Project"
        assert len(loaded.documents) == 2
        assert loaded.documents[0].id == "d1"
        assert len(loaded.themes) == 2
        assert loaded.themes[0]["label"] == "Theme 1"
        assert loaded.settings.temperature == 0.8
        assert loaded.settings.include_citations is False


@pytest.mark.e2e
class TestDocumentProcessingWorkflow:
    """Test complete document processing workflow."""

    def test_add_and_process_documents(self, isolated_project_manager, sample_document_path):
        """Test adding documents to project and marking them as processed."""
        manager = isolated_project_manager

        # Create project
        project = manager.create_project(name="Document Processing Test")

        # Add document
        doc = DocumentInfo(
            id="doc1",
            file_path=str(sample_document_path),
            title="Sample Document",
            file_size=sample_document_path.stat().st_size,
        )
        project.add_document(doc)
        manager.save_project(project)

        # Reload and verify
        loaded = manager.load_project(project.id)
        assert len(loaded.documents) == 1
        assert not loaded.documents[0].processed

        # Mark as processed
        loaded.documents[0].processed = True
        loaded.documents[0].num_chunks = 42
        manager.save_project(loaded)

        # Reload and verify processed state
        final = manager.load_project(project.id)
        assert final.documents[0].processed is True
        assert final.documents[0].num_chunks == 42

    def test_remove_document_from_project(self, isolated_project_manager):
        """Test removing documents from a project."""
        manager = isolated_project_manager

        project = manager.create_project(name="Document Removal Test")

        # Add multiple documents
        doc1 = DocumentInfo(id="d1", file_path="/p1", title="D1", file_size=100)
        doc2 = DocumentInfo(id="d2", file_path="/p2", title="D2", file_size=200)
        doc3 = DocumentInfo(id="d3", file_path="/p3", title="D3", file_size=300)

        project.add_document(doc1)
        project.add_document(doc2)
        project.add_document(doc3)
        manager.save_project(project)

        # Remove middle document
        loaded = manager.load_project(project.id)
        assert len(loaded.documents) == 3

        removed = loaded.remove_document("d2")
        assert removed is True
        manager.save_project(loaded)

        # Verify removal persisted
        final = manager.load_project(project.id)
        assert len(final.documents) == 2
        assert final.documents[0].id == "d1"
        assert final.documents[1].id == "d3"


@pytest.mark.e2e
class TestProjectLifecycleWorkflow:
    """Test complete project lifecycle from creation to deletion."""

    def test_full_project_lifecycle(self, isolated_project_manager):
        """Test creating, using, archiving, restoring, and deleting a project."""
        manager = isolated_project_manager

        # Step 1: Create project
        project = manager.create_project(name="Lifecycle Test")
        project_id = project.id

        # Step 2: Use project (add data)
        doc = DocumentInfo(id="d1", file_path="/p", title="D", file_size=100)
        project.add_document(doc)
        manager.save_project(project)

        # Step 3: Mark as favorite
        project.is_favorite = True
        manager.save_project(project)

        # Verify favorite
        loaded = manager.load_project(project_id)
        assert loaded.is_favorite is True

        # Step 4: Archive project (soft delete)
        result = manager.delete_project(project_id, permanent=False)
        assert result is True

        archived = manager.load_project(project_id)
        assert archived.is_archived is True

        # Verify not in active list
        active = manager.list_projects(include_archived=False)
        assert not any(p.id == project_id for p in active)

        # But is in archived list
        all_projects = manager.list_projects(include_archived=True)
        assert any(p.id == project_id for p in all_projects)

        # Step 5: Restore project
        result = manager.restore_project(project_id)
        assert result is True

        restored = manager.load_project(project_id)
        assert restored.is_archived is False

        # Step 6: Delete permanently
        result = manager.delete_project(project_id, permanent=True)
        assert result is True

        # Verify completely gone
        deleted = manager.load_project(project_id)
        assert deleted is None

        project_dir = manager._get_project_dir(project_id)
        assert not project_dir.exists()


@pytest.mark.e2e
class TestProjectSearchAndFilter:
    """Test searching and filtering projects."""

    def test_search_projects_workflow(self, isolated_project_manager):
        """Test searching projects by various criteria."""
        manager = isolated_project_manager

        # Create diverse set of projects
        p1 = manager.create_project(
            name="Machine Learning Research", description="Deep learning for NLP", tags=["ML", "AI"]
        )

        p2 = manager.create_project(
            name="Legal Case Analysis",
            description="Analyzing precedent cases",
            tags=["legal", "research"],
        )

        p3 = manager.create_project(
            name="Medical AI Research",
            description="Machine learning in healthcare",
            tags=["ML", "medical"],
        )

        # Search by name - matches both p1 (name) and p3 (description)
        results = manager.search_projects("Machine Learning")
        assert (
            len(results) == 2
        )  # p1 name has "Machine Learning", p3 description has "machine learning"
        assert any(p.id == p1.id for p in results)
        assert any(p.id == p3.id for p in results)

        # Search by description keyword
        results = manager.search_projects("machine learning")
        assert len(results) == 2  # p1 and p3
        assert any(p.id == p1.id for p in results)
        assert any(p.id == p3.id for p in results)

        # Search case-insensitive
        results = manager.search_projects("LEGAL")
        assert len(results) == 1
        assert results[0].id == p2.id

    def test_filter_projects_workflow(self, isolated_project_manager):
        """Test filtering projects by various attributes."""
        manager = isolated_project_manager

        # Create projects with different attributes
        p1 = manager.create_project(name="P1", tags=["tag1", "tag2"])
        doc1 = DocumentInfo(id="d1", file_path="/p", title="D", file_size=100)
        p1.add_document(doc1)
        manager.save_project(p1)

        p2 = manager.create_project(name="P2", tags=["tag2", "tag3"])
        p2.set_themes([{"id": "t1", "label": "Theme"}])
        manager.save_project(p2)

        p3 = manager.create_project(name="P3")

        # Filter by tag
        results = manager.filter_projects(tags=["tag1"])
        assert len(results) == 1
        assert results[0].id == p1.id

        # Filter by has_documents
        results = manager.filter_projects(has_documents=True)
        assert len(results) == 1
        assert results[0].id == p1.id

        # Filter by has_themes
        results = manager.filter_projects(has_themes=True)
        assert len(results) == 1
        assert results[0].id == p2.id


@pytest.mark.e2e
class TestProjectImportExport:
    """Test importing and exporting projects."""

    def test_export_import_workflow(self, isolated_project_manager, temp_projects_dir):
        """Test exporting a project and importing it back."""
        manager = isolated_project_manager

        # Create complex project
        project = manager.create_project(
            name="Export Test", description="Testing export/import", tags=["test", "export"]
        )

        # Add documents
        doc1 = DocumentInfo(id="d1", file_path="/p1", title="Doc1", file_size=100)
        doc2 = DocumentInfo(id="d2", file_path="/p2", title="Doc2", file_size=200)
        project.add_document(doc1)
        project.add_document(doc2)

        # Add themes
        themes = [{"id": "t1", "label": "Theme 1", "chunk_ids": ["c1"]}]
        project.set_themes(themes)

        manager.save_project(project)
        original_id = project.id

        # Export project
        export_path = temp_projects_dir / "exported_project.json"
        result = manager.export_project(project.id, export_path)
        assert result is True
        assert export_path.exists()

        # Import as new project
        imported = manager.import_project(export_path, new_name="Imported Project")
        assert imported is not None
        assert imported.name == "Imported Project"
        assert imported.id != original_id  # Should have new ID
        assert imported.description == "Testing export/import"
        assert len(imported.documents) == 2
        assert len(imported.themes) == 1
        assert "test" in imported.tags

        # Verify both projects exist independently
        original = manager.load_project(original_id)
        assert original is not None
        assert original.name == "Export Test"


@pytest.mark.e2e
class TestProjectStatistics:
    """Test project statistics gathering."""

    def test_overall_statistics_workflow(self, isolated_project_manager):
        """Test gathering statistics across all projects."""
        manager = isolated_project_manager

        # Create projects with various states
        p1 = manager.create_project(name="P1", is_favorite=True)
        doc1 = DocumentInfo(id="d1", file_path="/p", title="D", file_size=100)
        p1.add_document(doc1)
        manager.save_project(p1)

        p2 = manager.create_project(name="P2", is_archived=True)
        doc2 = DocumentInfo(id="d2", file_path="/p", title="D", file_size=100)
        p2.add_document(doc2)
        manager.save_project(p2)

        p3 = manager.create_project(name="P3", is_favorite=True)

        # Get statistics
        stats = manager.get_statistics()

        assert stats["total_projects"] == 3
        assert stats["active_projects"] == 2  # p1 and p3
        assert stats["archived_projects"] == 1  # p2
        assert stats["favorite_projects"] == 2  # p1 and p3
        assert stats["total_documents"] == 2  # p1 and p2 have docs


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
