"""Unit tests for Project data model."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.docprocessor.models.project import (
    DocumentInfo,
    Project,
    ProjectSettings,
    TaskExecutionRecord,
)


class TestProjectSettings:
    """Tests for ProjectSettings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = ProjectSettings()

        assert settings.language == "fr"
        assert settings.llm_model == "llama3.1:latest"
        assert settings.embedding_model == "all-MiniLM-L6-v2"
        assert settings.temperature == 0.7
        assert settings.chunk_size == 1000
        assert settings.chunk_overlap == 100
        assert settings.include_citations is True

    def test_settings_to_dict(self):
        """Test settings serialization to dict."""
        settings = ProjectSettings(language="en", temperature=0.5)
        data = settings.to_dict()

        assert isinstance(data, dict)
        assert data["language"] == "en"
        assert data["temperature"] == 0.5
        assert data["llm_model"] == "llama3.1:latest"

    def test_settings_from_dict(self):
        """Test settings deserialization from dict."""
        data = {"language": "ar", "llm_model": "llama2", "temperature": 0.8, "chunk_size": 500}
        settings = ProjectSettings.from_dict(data)

        assert settings.language == "ar"
        assert settings.llm_model == "llama2"
        assert settings.temperature == 0.8
        assert settings.chunk_size == 500
        # Defaults should still be present
        assert settings.chunk_overlap == 100


class TestDocumentInfo:
    """Tests for DocumentInfo class."""

    def test_document_creation(self):
        """Test creating a document info."""
        doc = DocumentInfo(
            id="doc123",
            file_path="/path/to/file.pdf",
            title="Test Document",
            file_size=1024,
            author="John Doe",
        )

        assert doc.id == "doc123"
        assert doc.title == "Test Document"
        assert doc.author == "John Doe"
        assert doc.processed is False
        assert len(doc.tags) == 0

    def test_document_to_dict(self):
        """Test document serialization."""
        doc = DocumentInfo(
            id="doc123",
            file_path="/path/to/file.pdf",
            title="Test Document",
            file_size=1024,
            tags=["tag1", "tag2"],
        )
        data = doc.to_dict()

        assert data["id"] == "doc123"
        assert data["title"] == "Test Document"
        assert data["tags"] == ["tag1", "tag2"]
        assert "added_at" in data

    def test_document_from_dict(self):
        """Test document deserialization."""
        data = {
            "id": "doc456",
            "file_path": "/path/to/file.pdf",
            "title": "Another Document",
            "file_size": 2048,
            "author": "Jane Smith",
            "tags": ["research"],
            "processed": True,
            "num_chunks": 10,
            "added_at": datetime.now().isoformat(),
        }
        doc = DocumentInfo.from_dict(data)

        assert doc.id == "doc456"
        assert doc.author == "Jane Smith"
        assert doc.processed is True
        assert doc.num_chunks == 10


class TestTaskExecutionRecord:
    """Tests for TaskExecutionRecord class."""

    def test_record_creation(self):
        """Test creating a task execution record."""
        record = TaskExecutionRecord(
            task_name="summarize",
            task_display_name="Summarize Documents",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=120.5,
            input_document_ids=["doc1", "doc2"],
            output_files=["/path/to/output.md"],
            output_data={"num_chapters": 5},
            config_used={"synthesis_level": "normal"},
        )

        assert record.task_name == "summarize"
        assert record.status == "completed"
        assert record.duration_seconds == 120.5
        assert len(record.input_document_ids) == 2

    def test_record_serialization(self):
        """Test record to/from dict."""
        record = TaskExecutionRecord(
            task_name="ai_detect",
            task_display_name="AI Detection",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=45.2,
            input_document_ids=["doc1"],
            output_files=[],
            output_data={"ai_percentage": 15},
            config_used={},
        )

        # To dict
        data = record.to_dict()
        assert data["task_name"] == "ai_detect"
        assert data["output_data"]["ai_percentage"] == 15

        # From dict
        restored = TaskExecutionRecord.from_dict(data)
        assert restored.task_name == record.task_name
        assert restored.duration_seconds == record.duration_seconds


class TestProject:
    """Tests for Project class."""

    def test_project_creation(self):
        """Test creating a project."""
        project = Project(name="Test Project", description="A test project")

        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert len(project.documents) == 0
        assert len(project.task_history) == 0
        assert len(project.themes) == 0
        assert project.is_archived is False
        assert project.is_favorite is False

    def test_project_with_settings(self):
        """Test project with custom settings."""
        settings = ProjectSettings(language="en", temperature=0.5)
        project = Project(name="Custom Project", settings=settings)

        assert project.settings.language == "en"
        assert project.settings.temperature == 0.5

    def test_add_document(self):
        """Test adding documents to project."""
        project = Project(name="Test Project")
        doc = DocumentInfo(
            id="doc1", file_path="/path/to/file.pdf", title="Document 1", file_size=1024
        )

        project.add_document(doc)

        assert len(project.documents) == 1
        assert project.documents[0].id == "doc1"

    def test_remove_document(self):
        """Test removing documents from project."""
        project = Project(name="Test Project")
        doc1 = DocumentInfo(id="doc1", file_path="/path1", title="Doc 1", file_size=100)
        doc2 = DocumentInfo(id="doc2", file_path="/path2", title="Doc 2", file_size=200)

        project.add_document(doc1)
        project.add_document(doc2)
        assert len(project.documents) == 2

        result = project.remove_document("doc1")
        assert result is True
        assert len(project.documents) == 1
        assert project.documents[0].id == "doc2"

        # Try removing non-existent document
        result = project.remove_document("doc999")
        assert result is False

    def test_get_document(self):
        """Test getting document by ID."""
        project = Project(name="Test Project")
        doc = DocumentInfo(id="doc1", file_path="/path", title="Doc", file_size=100)
        project.add_document(doc)

        retrieved = project.get_document("doc1")
        assert retrieved is not None
        assert retrieved.id == "doc1"

        not_found = project.get_document("doc999")
        assert not_found is None

    def test_get_document_by_path(self):
        """Test getting document by file path."""
        project = Project(name="Test Project")
        doc1 = DocumentInfo(id="doc1", file_path="/path/to/file1.pdf", title="Doc1", file_size=100)
        doc2 = DocumentInfo(id="doc2", file_path="/path/to/file2.pdf", title="Doc2", file_size=200)
        project.add_document(doc1)
        project.add_document(doc2)

        retrieved = project.get_document_by_path("/path/to/file1.pdf")
        assert retrieved is not None
        assert retrieved.id == "doc1"
        assert retrieved.title == "Doc1"

        not_found = project.get_document_by_path("/nonexistent/path.pdf")
        assert not_found is None

    def test_get_processed_documents(self):
        """Test filtering processed documents."""
        project = Project(name="Test Project")
        doc1 = DocumentInfo(
            id="doc1", file_path="/path1", title="Doc 1", file_size=100, processed=True
        )
        doc2 = DocumentInfo(
            id="doc2", file_path="/path2", title="Doc 2", file_size=200, processed=False
        )
        doc3 = DocumentInfo(
            id="doc3", file_path="/path3", title="Doc 3", file_size=300, processed=True
        )

        project.add_document(doc1)
        project.add_document(doc2)
        project.add_document(doc3)

        processed = project.get_processed_documents()
        assert len(processed) == 2
        assert all(doc.processed for doc in processed)

        unprocessed = project.get_unprocessed_documents()
        assert len(unprocessed) == 1
        assert unprocessed[0].id == "doc2"

    def test_add_task_record(self):
        """Test adding task execution records."""
        project = Project(name="Test Project")
        record = TaskExecutionRecord(
            task_name="summarize",
            task_display_name="Summarize",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=100,
            input_document_ids=["doc1"],
            output_files=[],
            output_data={},
            config_used={},
        )

        project.add_task_record(record)
        assert len(project.task_history) == 1

    def test_get_task_history(self):
        """Test filtering task history."""
        project = Project(name="Test Project")

        record1 = TaskExecutionRecord(
            task_name="summarize",
            task_display_name="Summarize",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=100,
            input_document_ids=[],
            output_files=[],
            output_data={},
            config_used={},
        )
        record2 = TaskExecutionRecord(
            task_name="ai_detect",
            task_display_name="AI Detect",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=50,
            input_document_ids=[],
            output_files=[],
            output_data={},
            config_used={},
        )
        record3 = TaskExecutionRecord(
            task_name="summarize",
            task_display_name="Summarize",
            executed_at=datetime.now(),
            status="failed",
            duration_seconds=10,
            input_document_ids=[],
            output_files=[],
            output_data={},
            config_used={},
        )

        project.add_task_record(record1)
        project.add_task_record(record2)
        project.add_task_record(record3)

        # Get all
        all_tasks = project.get_task_history()
        assert len(all_tasks) == 3

        # Get filtered
        summarize_tasks = project.get_task_history("summarize")
        assert len(summarize_tasks) == 2

    def test_themes(self):
        """Test theme management."""
        project = Project(name="Test Project")

        themes = [{"id": "theme1", "label": "Theme 1"}, {"id": "theme2", "label": "Theme 2"}]

        project.set_themes(themes)
        assert len(project.themes) == 2

        project.clear_themes()
        assert len(project.themes) == 0

    def test_get_statistics(self):
        """Test project statistics."""
        project = Project(name="Test Project")

        # Add documents
        doc1 = DocumentInfo(id="doc1", file_path="/p1", title="D1", file_size=1000, processed=True)
        doc2 = DocumentInfo(id="doc2", file_path="/p2", title="D2", file_size=2000, processed=False)
        project.add_document(doc1)
        project.add_document(doc2)

        # Add themes
        project.set_themes([{"id": "t1"}, {"id": "t2"}])

        # Add task records
        record = TaskExecutionRecord(
            task_name="summarize",
            task_display_name="Summarize",
            executed_at=datetime.now(),
            status="completed",
            duration_seconds=100,
            input_document_ids=[],
            output_files=[],
            output_data={},
            config_used={},
        )
        project.add_task_record(record)

        stats = project.get_statistics()

        assert stats["total_documents"] == 2
        assert stats["processed_documents"] == 1
        assert stats["unprocessed_documents"] == 1
        assert stats["total_size_bytes"] == 3000
        assert stats["total_themes"] == 2
        assert stats["total_tasks_executed"] == 1
        assert "task_counts" in stats

    def test_project_serialization(self):
        """Test project save/load to JSON."""
        project = Project(name="Serialization Test", description="Test project")

        # Add some data
        doc = DocumentInfo(id="doc1", file_path="/path", title="Doc", file_size=1024)
        project.add_document(doc)

        project.set_themes([{"id": "theme1", "label": "Theme 1"}])

        project.tags = ["tag1", "tag2"]
        project.is_favorite = True

        # Serialize to dict
        data = project.to_dict()

        assert data["name"] == "Serialization Test"
        assert len(data["documents"]) == 1
        assert len(data["themes"]) == 1
        assert data["is_favorite"] is True

        # Deserialize from dict
        restored = Project.from_dict(data)

        assert restored.name == project.name
        assert len(restored.documents) == 1
        assert restored.documents[0].id == "doc1"
        assert len(restored.themes) == 1
        assert restored.is_favorite is True

    def test_project_file_persistence(self):
        """Test saving and loading project from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Create and save project
            project = Project(name="File Test", description="Test save/load")
            doc = DocumentInfo(id="doc1", file_path="/path", title="Doc", file_size=1024)
            project.add_document(doc)

            project.save_to_file(temp_file)
            assert temp_file.exists()

            # Load project
            loaded = Project.load_from_file(temp_file)

            assert loaded.name == "File Test"
            assert loaded.description == "Test save/load"
            assert len(loaded.documents) == 1
            assert loaded.documents[0].id == "doc1"

        finally:
            if temp_file.exists():
                temp_file.unlink()

    def test_update_timestamp(self):
        """Test timestamp updates."""
        project = Project(name="Test")
        old_timestamp = project.updated_at

        # Wait a tiny bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        project.update_timestamp()
        assert project.updated_at > old_timestamp

    def test_mark_opened(self):
        """Test marking project as opened."""
        project = Project(name="Test")
        assert project.last_opened_at is None

        project.mark_opened()
        assert project.last_opened_at is not None

    def test_project_string_representation(self):
        """Test __str__ method."""
        project = Project(name="Test Project")
        project.add_document(DocumentInfo(id="d1", file_path="/p", title="D", file_size=100))
        project.set_themes([{"id": "t1"}])

        string = str(project)
        assert "Test Project" in string
        assert "1 docs" in string
        assert "1 themes" in string


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
