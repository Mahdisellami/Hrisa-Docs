"""Integration tests for multi-project workflow."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from docprocessor.core.project_manager import ProjectManager
from docprocessor.models.project import DocumentInfo, TaskExecutionRecord


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_manager(temp_data_dir):
    """Create a ProjectManager with temporary storage."""
    return ProjectManager(projects_dir=temp_data_dir)


class TestMultiProjectWorkflow:
    """Integration tests for complete multi-project workflows."""

    def test_create_project_add_documents_workflow(self, project_manager):
        """Test creating a project and adding documents."""
        # Create project
        project = project_manager.create_project(
            name="Research Project", description="Academic research compilation"
        )
        assert project.id is not None
        assert project.name == "Research Project"

        # Add documents
        doc1 = DocumentInfo(
            id="doc1", file_path="/path/to/paper1.pdf", title="Paper 1", file_size=1024 * 100
        )
        doc2 = DocumentInfo(
            id="doc2", file_path="/path/to/paper2.pdf", title="Paper 2", file_size=1024 * 200
        )

        project.add_document(doc1)
        project.add_document(doc2)
        assert len(project.documents) == 2

        # Save project
        project_manager.save_project(project)

        # Load project and verify documents persisted
        loaded = project_manager.load_project(project.id)
        assert loaded is not None
        assert len(loaded.documents) == 2
        assert loaded.documents[0].title == "Paper 1"
        assert loaded.documents[1].title == "Paper 2"

    def test_project_switching_workflow(self, project_manager):
        """Test switching between multiple projects."""
        # Create multiple projects
        project1 = project_manager.create_project(name="Project 1")
        project2 = project_manager.create_project(name="Project 2")

        # Add documents to project 1
        doc1 = DocumentInfo(id="doc1", file_path="/path/1.pdf", title="Doc 1", file_size=1000)
        project1.add_document(doc1)

        # Add documents to project 2
        doc2 = DocumentInfo(id="doc2", file_path="/path/2.pdf", title="Doc 2", file_size=2000)
        project2.add_document(doc2)

        # Save both
        project_manager.save_project(project1)
        project_manager.save_project(project2)

        # Load project 1 and verify
        loaded1 = project_manager.load_project(project1.id)
        assert len(loaded1.documents) == 1
        assert loaded1.documents[0].title == "Doc 1"

        # Load project 2 and verify
        loaded2 = project_manager.load_project(project2.id)
        assert len(loaded2.documents) == 1
        assert loaded2.documents[0].title == "Doc 2"

        # Verify they're independent
        assert loaded1.id != loaded2.id

    def test_document_modification_workflow(self, project_manager):
        """Test adding and removing documents from a project."""
        # Create project
        project = project_manager.create_project(name="Test Project")

        # Add multiple documents
        for i in range(5):
            doc = DocumentInfo(
                id=f"doc{i}",
                file_path=f"/path/doc{i}.pdf",
                title=f"Document {i}",
                file_size=1000 * (i + 1),
            )
            project.add_document(doc)

        assert len(project.documents) == 5
        project_manager.save_project(project)

        # Remove some documents
        project.remove_document("doc1")
        project.remove_document("doc3")
        assert len(project.documents) == 3

        # Save and reload
        project_manager.save_project(project)
        loaded = project_manager.load_project(project.id)

        # Verify correct documents remain
        assert len(loaded.documents) == 3
        doc_ids = [doc.id for doc in loaded.documents]
        assert "doc0" in doc_ids
        assert "doc2" in doc_ids
        assert "doc4" in doc_ids
        assert "doc1" not in doc_ids
        assert "doc3" not in doc_ids

    def test_project_settings_modification_workflow(self, project_manager):
        """Test modifying project settings."""
        # Create project with default settings
        project = project_manager.create_project(name="Settings Test")

        # Modify settings
        project.settings.language = "en"
        project.settings.llm_model = "llama2:latest"
        project.settings.temperature = 0.8
        project.settings.chunk_size = 800
        project.settings.chunk_overlap = 100
        project.settings.output_format = "docx"
        project.settings.include_citations = True
        project.settings.citation_style = "APA"

        # Save project
        project_manager.save_project(project)

        # Load and verify settings persisted
        loaded = project_manager.load_project(project.id)
        assert loaded.settings.language == "en"
        assert loaded.settings.llm_model == "llama2:latest"
        assert loaded.settings.temperature == 0.8
        assert loaded.settings.chunk_size == 800
        assert loaded.settings.chunk_overlap == 100
        assert loaded.settings.output_format == "docx"
        assert loaded.settings.include_citations is True
        assert loaded.settings.citation_style == "APA"

    def test_task_history_workflow(self, project_manager):
        """Test adding and retrieving task execution records."""
        # Create project
        project = project_manager.create_project(name="Task Test")

        # Add documents
        doc = DocumentInfo(id="doc1", file_path="/path/doc.pdf", title="Doc", file_size=1000)
        project.add_document(doc)

        # Simulate task executions
        task1 = TaskExecutionRecord(
            task_name="summarization",
            task_display_name="Document Summarization",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=120.5,
            input_document_ids=["doc1"],
            output_files=["summary.md"],
            output_data={},
            config_used={"level": "detailed"},
        )

        task2 = TaskExecutionRecord(
            task_name="url_import",
            task_display_name="Import from URL",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=30.2,
            input_document_ids=[],
            output_files=["imported_doc.pdf"],
            output_data={},
            config_used={"url": "https://example.com"},
        )

        project.add_task_record(task1)
        project.add_task_record(task2)

        # Save and reload
        project_manager.save_project(project)
        loaded = project_manager.load_project(project.id)

        # Verify task history
        assert len(loaded.task_history) == 2
        assert loaded.task_history[0].task_name == "summarization"
        assert loaded.task_history[1].task_name == "url_import"

        # Test filtering
        summary_tasks = loaded.get_task_history("summarization")
        assert len(summary_tasks) == 1
        assert summary_tasks[0].task_display_name == "Document Summarization"

    def test_themes_workflow(self, project_manager):
        """Test adding and managing themes in a project."""
        # Create project
        project = project_manager.create_project(name="Themes Test")

        # Add themes
        themes = [
            {"label": "Introduction", "cluster_id": 0, "size": 50},
            {"label": "Methodology", "cluster_id": 1, "size": 75},
            {"label": "Results", "cluster_id": 2, "size": 100},
        ]

        project.set_themes(themes)
        assert len(project.themes) == 3

        # Save and reload
        project_manager.save_project(project)
        loaded = project_manager.load_project(project.id)

        # Verify themes persisted
        assert len(loaded.themes) == 3
        assert loaded.themes[0]["label"] == "Introduction"
        assert loaded.themes[1]["label"] == "Methodology"
        assert loaded.themes[2]["label"] == "Results"

    def test_project_metadata_workflow(self, project_manager):
        """Test project metadata (tags, favorite, archive)."""
        # Create project
        project = project_manager.create_project(name="Metadata Test")

        # Set metadata
        project.tags = ["research", "academic", "2024"]
        project.is_favorite = True
        project.author = "Test User"
        project.notes = "Important research project"
        project.color = "#FF5733"

        # Save and reload
        project_manager.save_project(project)
        loaded = project_manager.load_project(project.id)

        # Verify metadata
        assert loaded.tags == ["research", "academic", "2024"]
        assert loaded.is_favorite is True
        assert loaded.author == "Test User"
        assert loaded.notes == "Important research project"
        assert loaded.color == "#FF5733"

    def test_project_statistics_workflow(self, project_manager):
        """Test project statistics calculation."""
        # Create project
        project = project_manager.create_project(name="Stats Test")

        # Add documents
        for i in range(3):
            doc = DocumentInfo(
                id=f"doc{i}",
                file_path=f"/path/{i}.pdf",
                title=f"Doc {i}",
                file_size=1000,
                processed=(i < 2),  # First 2 are processed
            )
            project.add_document(doc)

        # Add themes
        project.set_themes([{"label": f"Theme {i}"} for i in range(4)])

        # Add tasks
        for i in range(5):
            task = TaskExecutionRecord(
                task_name=f"task{i}",
                task_display_name=f"Task {i}",
                executed_at=datetime.now(),
                status="completed",
                duration_seconds=10.0,
                input_document_ids=[],
                output_files=[],
                output_data={},
                config_used={},
            )
            project.add_task_record(task)

        # Get statistics
        stats = project.get_statistics()

        # Verify
        assert stats["total_documents"] == 3
        assert stats["processed_documents"] == 2
        assert stats["unprocessed_documents"] == 1
        assert stats["total_themes"] == 4
        assert stats["total_tasks_executed"] == 5

    def test_get_document_by_path(self, project_manager):
        """Test finding documents by file path."""
        # Create project
        project = project_manager.create_project(name="Path Test")

        # Add documents with different paths
        doc1 = DocumentInfo(
            id="doc1", file_path="/data/papers/paper1.pdf", title="Paper 1", file_size=1000
        )
        doc2 = DocumentInfo(
            id="doc2", file_path="/data/papers/paper2.pdf", title="Paper 2", file_size=2000
        )
        doc3 = DocumentInfo(
            id="doc3", file_path="/data/books/book1.pdf", title="Book 1", file_size=3000
        )

        project.add_document(doc1)
        project.add_document(doc2)
        project.add_document(doc3)

        # Save and reload
        project_manager.save_project(project)
        loaded = project_manager.load_project(project.id)

        # Find by path
        found = loaded.get_document_by_path("/data/papers/paper2.pdf")
        assert found is not None
        assert found.id == "doc2"
        assert found.title == "Paper 2"

        # Try non-existent path
        not_found = loaded.get_document_by_path("/nonexistent/path.pdf")
        assert not_found is None

    def test_complete_project_lifecycle(self, project_manager):
        """Test complete project lifecycle from creation to archive."""
        # 1. Create project
        project = project_manager.create_project(
            name="Full Lifecycle Test", description="Testing complete workflow"
        )

        # 2. Configure settings
        project.settings.language = "en"
        project.settings.llm_model = "mistral:latest"

        # 3. Add documents
        for i in range(3):
            doc = DocumentInfo(
                id=f"doc{i}",
                file_path=f"/test/doc{i}.pdf",
                title=f"Document {i}",
                file_size=1000 * (i + 1),
            )
            project.add_document(doc)

        # 4. Add themes
        project.set_themes([{"label": "Chapter 1"}, {"label": "Chapter 2"}])

        # 5. Add task records
        task = TaskExecutionRecord(
            task_name="synthesis",
            task_display_name="Synthesis",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=180.0,
            input_document_ids=[],
            output_files=[],
            output_data={},
            config_used={},
        )
        project.add_task_record(task)

        # 6. Mark as favorite
        project.is_favorite = True

        # 7. Save
        project_manager.save_project(project)

        # 8. Verify can be loaded
        loaded = project_manager.load_project(project.id)
        assert loaded is not None
        assert len(loaded.documents) == 3
        assert len(loaded.themes) == 2
        assert len(loaded.task_history) == 1
        assert loaded.is_favorite is True

        # 9. Archive project
        project_manager.delete_project(loaded.id, permanent=False)
        loaded = project_manager.load_project(project.id)
        assert loaded.is_archived is True

        # 10. Restore project
        project_manager.restore_project(project.id)
        loaded = project_manager.load_project(project.id)
        assert loaded.is_archived is False

        # 11. Permanent delete
        project_manager.delete_project(project.id, permanent=True)
        loaded = project_manager.load_project(project.id)
        assert loaded is None

    def test_project_duplication_workflow(self, project_manager):
        """Test duplicating a project with all its data."""
        # Create original project with full setup
        original = project_manager.create_project(
            name="Original Research",
            description="Main research project",
            tags=["research", "2024"],
            author="Test User",
            is_favorite=True,
        )

        # Add documents
        for i in range(3):
            doc = DocumentInfo(
                id=f"doc{i}",
                file_path=f"/test/doc{i}.pdf",
                title=f"Paper {i}",
                file_size=1000 * (i + 1),
                processed=True,
            )
            original.add_document(doc)

        # Add themes
        original.set_themes([{"label": "Theme 1", "id": "t1"}, {"label": "Theme 2", "id": "t2"}])

        # Add task history
        task = TaskExecutionRecord(
            task_name="processing",
            task_display_name="Document Processing",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=60.0,
            input_document_ids=["doc0", "doc1", "doc2"],
            output_files=[],
            output_data={},
            config_used={},
        )
        original.add_task_record(task)

        project_manager.save_project(original)

        # Duplicate with documents
        duplicate = project_manager.duplicate_project(original.id, new_name="Research Copy")

        # Verify duplicate
        assert duplicate is not None
        assert duplicate.id != original.id
        assert duplicate.name == "Research Copy"
        assert duplicate.description == original.description
        assert duplicate.tags == original.tags
        assert duplicate.author == original.author

        # Documents should be copied
        assert len(duplicate.documents) == 3
        assert duplicate.documents[0].title == "Paper 0"

        # Themes should be copied
        assert len(duplicate.themes) == 2
        assert duplicate.themes[0]["label"] == "Theme 1"

        # Task history should be cleared (fresh start)
        assert len(duplicate.task_history) == 0

        # Timestamps should be new
        assert duplicate.created_at > original.created_at

        # Can be saved and loaded
        project_manager.save_project(duplicate)
        loaded = project_manager.load_project(duplicate.id)
        assert loaded is not None
        assert loaded.name == "Research Copy"

    def test_project_rename_workflow(self, project_manager):
        """Test renaming a project."""
        # Create project
        project = project_manager.create_project(name="Old Project Name")
        original_id = project.id

        # Add some data
        doc = DocumentInfo(id="doc1", file_path="/test.pdf", title="Doc", file_size=1000)
        project.add_document(doc)
        project_manager.save_project(project)

        # Rename
        success = project_manager.rename_project(project.id, "New Project Name")
        assert success is True

        # Verify rename
        loaded = project_manager.load_project(original_id)
        assert loaded is not None
        assert loaded.id == original_id  # ID unchanged
        assert loaded.name == "New Project Name"  # Name changed
        assert len(loaded.documents) == 1  # Data intact

    def test_bulk_archive_restore_workflow(self, project_manager):
        """Test archiving and restoring multiple projects."""
        # Create 5 projects
        projects = []
        for i in range(5):
            proj = project_manager.create_project(name=f"Project {i}")
            projects.append(proj)

        # Archive first 3
        ids_to_archive = [p.id for p in projects[:3]]
        results = project_manager.archive_projects(ids_to_archive)

        # Verify all successful
        for proj_id in ids_to_archive:
            assert results[proj_id] is True

        # Verify archived
        for i in range(3):
            loaded = project_manager.load_project(projects[i].id)
            assert loaded.is_archived is True

        # Verify others not archived
        for i in range(3, 5):
            loaded = project_manager.load_project(projects[i].id)
            assert loaded.is_archived is False

        # Restore first 2 archived projects
        ids_to_restore = [projects[0].id, projects[1].id]
        results = project_manager.restore_projects(ids_to_restore)

        # Verify all successful
        for proj_id in ids_to_restore:
            assert results[proj_id] is True

        # Verify restored
        for i in range(2):
            loaded = project_manager.load_project(projects[i].id)
            assert loaded.is_archived is False

        # Third one still archived
        loaded = project_manager.load_project(projects[2].id)
        assert loaded.is_archived is True

    def test_bulk_delete_workflow(self, project_manager):
        """Test permanently deleting multiple projects."""
        # Create 4 projects
        projects = []
        for i in range(4):
            proj = project_manager.create_project(name=f"Delete Test {i}")
            # Add some data to make it realistic
            doc = DocumentInfo(
                id=f"doc{i}", file_path=f"/test{i}.pdf", title=f"Doc {i}", file_size=1000
            )
            proj.add_document(doc)
            project_manager.save_project(proj)
            projects.append(proj)

        # Delete first 2 permanently
        ids_to_delete = [projects[0].id, projects[1].id]
        results = project_manager.delete_projects(ids_to_delete, permanent=True)

        # Verify all successful
        for proj_id in ids_to_delete:
            assert results[proj_id] is True

        # Verify deleted
        for i in range(2):
            loaded = project_manager.load_project(projects[i].id)
            assert loaded is None

        # Verify others still exist
        for i in range(2, 4):
            loaded = project_manager.load_project(projects[i].id)
            assert loaded is not None
            assert loaded.name == f"Delete Test {i}"

    def test_mixed_bulk_operations_workflow(self, project_manager):
        """Test bulk operations with some failures."""
        # Create 3 real projects
        p1 = project_manager.create_project(name="P1")
        p2 = project_manager.create_project(name="P2")
        p3 = project_manager.create_project(name="P3")

        # Try to archive mix of real and fake IDs
        results = project_manager.archive_projects([p1.id, "fake-id-1", p2.id, "fake-id-2"])

        # Verify results
        assert results[p1.id] is True
        assert results[p2.id] is True
        assert results["fake-id-1"] is False
        assert results["fake-id-2"] is False

        # Verify real ones were archived
        loaded_p1 = project_manager.load_project(p1.id)
        loaded_p2 = project_manager.load_project(p2.id)
        assert loaded_p1.is_archived is True
        assert loaded_p2.is_archived is True

        # p3 unaffected
        loaded_p3 = project_manager.load_project(p3.id)
        assert loaded_p3.is_archived is False
