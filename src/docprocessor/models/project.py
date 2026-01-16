"""Project data model for multi-project support.

A Project contains:
- Documents (PDFs, text files, web imports, etc.)
- Task execution history and results
- Project-specific settings (LLM model, language, etc.)
- Themes (for synthesis tasks)
- Metadata (title, description, tags, etc.)
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def convert_uuids_to_strings(obj: Any) -> Any:
    """Recursively convert UUID objects to strings in nested structures."""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_uuids_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuids_to_strings(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_uuids_to_strings(item) for item in obj)
    else:
        return obj


@dataclass
class ProjectSettings:
    """Project-specific settings."""

    # Language & Localization
    language: str = "fr"  # UI language (fr, en, ar)

    # LLM Configuration
    llm_model: str = "llama3.1:latest"  # Ollama model
    embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformer model
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # Vector Database
    vector_db_collection: Optional[str] = None  # ChromaDB collection name

    # Processing Parameters
    chunk_size: int = 1000  # Max tokens per chunk
    chunk_overlap: int = 100  # Token overlap between chunks

    # Output Preferences
    default_output_format: str = "docx"
    include_citations: bool = True
    citation_style: str = "APA"  # APA, MLA, Chicago, IEEE

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "language": self.language,
            "llm_model": self.llm_model,
            "embedding_model": self.embedding_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "vector_db_collection": self.vector_db_collection,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "default_output_format": self.default_output_format,
            "include_citations": self.include_citations,
            "citation_style": self.citation_style,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectSettings":
        """Create settings from dictionary."""
        return cls(
            language=data.get("language", "fr"),
            llm_model=data.get("llm_model", "llama3.1:latest"),
            embedding_model=data.get("embedding_model", "all-MiniLM-L6-v2"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            vector_db_collection=data.get("vector_db_collection"),
            chunk_size=data.get("chunk_size", 1000),
            chunk_overlap=data.get("chunk_overlap", 100),
            default_output_format=data.get("default_output_format", "docx"),
            include_citations=data.get("include_citations", True),
            citation_style=data.get("citation_style", "APA"),
        )


@dataclass
class DocumentInfo:
    """Information about a document in the project."""

    id: str  # Unique document ID
    file_path: str  # Path to document file
    title: str  # Document title
    file_size: int  # Size in bytes

    # Metadata
    author: Optional[str] = None
    publication_date: Optional[str] = None
    source_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    # Processing state
    processed: bool = False
    processing_date: Optional[datetime] = None
    num_chunks: int = 0

    # Timestamps
    added_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),  # Ensure UUID objects are converted to strings
            "file_path": self.file_path,
            "title": self.title,
            "file_size": self.file_size,
            "author": self.author,
            "publication_date": self.publication_date,
            "source_url": self.source_url,
            "tags": self.tags,
            "custom_metadata": self.custom_metadata,
            "processed": self.processed,
            "processing_date": self.processing_date.isoformat() if self.processing_date else None,
            "num_chunks": self.num_chunks,
            "added_at": self.added_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentInfo":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            file_path=data["file_path"],
            title=data["title"],
            file_size=data["file_size"],
            author=data.get("author"),
            publication_date=data.get("publication_date"),
            source_url=data.get("source_url"),
            tags=data.get("tags", []),
            custom_metadata=data.get("custom_metadata", {}),
            processed=data.get("processed", False),
            processing_date=(
                datetime.fromisoformat(data["processing_date"])
                if data.get("processing_date")
                else None
            ),
            num_chunks=data.get("num_chunks", 0),
            added_at=datetime.fromisoformat(data["added_at"]),
        )


@dataclass
class SearchResult:
    """Result from a search query (for search & import feature)."""

    title: str  # Document/page title
    url: str  # URL to document
    snippet: str  # Preview/description text
    source_name: str  # Source website (e.g., "finances.gov.tn")
    file_type: str  # "pdf", "html", "docx", etc.

    # Optional metadata
    publication_date: Optional[datetime] = None
    relevance_score: float = 0.0  # 0-1, higher is more relevant
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    search_query: Optional[str] = None  # Original query that found this
    found_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source_name": self.source_name,
            "file_type": self.file_type,
            "publication_date": (
                self.publication_date.isoformat() if self.publication_date else None
            ),
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "search_query": self.search_query,
            "found_at": self.found_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create from dictionary."""
        return cls(
            title=data["title"],
            url=data["url"],
            snippet=data["snippet"],
            source_name=data["source_name"],
            file_type=data["file_type"],
            publication_date=(
                datetime.fromisoformat(data["publication_date"])
                if data.get("publication_date")
                else None
            ),
            relevance_score=data.get("relevance_score", 0.0),
            metadata=data.get("metadata", {}),
            search_query=data.get("search_query"),
            found_at=datetime.fromisoformat(data["found_at"]),
        )


@dataclass
class TaskExecutionRecord:
    """Record of a task execution in this project."""

    task_name: str  # Name of the task
    task_display_name: str  # User-friendly name
    executed_at: datetime
    status: str  # completed, failed, cancelled
    duration_seconds: float

    # Input/Output
    input_document_ids: List[str]  # Which documents were used
    output_files: List[str]  # Generated files
    output_data: Dict[str, Any]  # Task-specific output data

    # Metadata
    config_used: Dict[str, Any]  # Configuration that was used
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_name": self.task_name,
            "task_display_name": self.task_display_name,
            "executed_at": self.executed_at.isoformat(),
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "input_document_ids": self.input_document_ids,
            "output_files": self.output_files,
            "output_data": self.output_data,
            "config_used": self.config_used,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskExecutionRecord":
        """Create from dictionary."""
        return cls(
            task_name=data["task_name"],
            task_display_name=data["task_display_name"],
            executed_at=datetime.fromisoformat(data["executed_at"]),
            status=data["status"],
            duration_seconds=data["duration_seconds"],
            input_document_ids=data["input_document_ids"],
            output_files=data["output_files"],
            output_data=data["output_data"],
            config_used=data["config_used"],
            error_message=data.get("error_message"),
        )


@dataclass
class SynthesisCache:
    """Cached synthesis results to avoid regeneration."""

    # Generated chapters
    chapters: List[Dict[str, Any]]  # List of chapter dicts with content, title, etc.

    # Metadata
    generated_at: datetime
    synthesis_level: str  # short, normal, comprehensive
    theme_ids: List[str]  # Which themes were used
    total_words: int
    total_citations: int

    # Settings used
    config_used: Dict[str, Any]  # Synthesis configuration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chapters": self.chapters,
            "generated_at": self.generated_at.isoformat(),
            "synthesis_level": self.synthesis_level,
            "theme_ids": self.theme_ids,
            "total_words": self.total_words,
            "total_citations": self.total_citations,
            "config_used": self.config_used,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SynthesisCache":
        """Create from dictionary."""
        return cls(
            chapters=data["chapters"],
            generated_at=datetime.fromisoformat(data["generated_at"]),
            synthesis_level=data["synthesis_level"],
            theme_ids=data.get("theme_ids", []),
            total_words=data.get("total_words", 0),
            total_citations=data.get("total_citations", 0),
            config_used=data.get("config_used", {}),
        )


@dataclass
class Project:
    """A document processing project.

    A project encapsulates:
    - A collection of documents
    - Task execution history
    - Project-specific settings
    - Themes and synthesis results
    - Metadata and organization
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Project"
    description: str = ""

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_opened_at: Optional[datetime] = None

    # Documents
    documents: List[DocumentInfo] = field(default_factory=list)

    # Task History
    task_history: List[TaskExecutionRecord] = field(default_factory=list)

    # Themes (for synthesis)
    themes: List[Dict[str, Any]] = field(default_factory=list)  # Theme objects as dicts

    # Synthesis cache
    synthesis_cache: Optional[SynthesisCache] = None

    # Settings
    settings: ProjectSettings = field(default_factory=ProjectSettings)

    # Organization
    tags: List[str] = field(default_factory=list)
    is_archived: bool = False
    is_favorite: bool = False
    color: Optional[str] = None  # For UI visualization

    # Metadata
    author: str = ""
    notes: str = ""
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    def mark_opened(self):
        """Mark project as opened (for recent projects)."""
        self.last_opened_at = datetime.now()

    def add_document(self, doc_info: DocumentInfo):
        """Add a document to the project."""
        self.documents.append(doc_info)
        self.update_timestamp()

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document by ID. Returns True if found and removed."""
        for i, doc in enumerate(self.documents):
            if doc.id == doc_id:
                self.documents.pop(i)
                self.update_timestamp()
                return True
        return False

    def get_document(self, doc_id: str) -> Optional[DocumentInfo]:
        """Get document by ID."""
        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None

    def get_document_by_path(self, file_path: str) -> Optional[DocumentInfo]:
        """Get document by file path."""
        for doc in self.documents:
            if doc.file_path == file_path:
                return doc
        return None

    def get_processed_documents(self) -> List[DocumentInfo]:
        """Get list of processed documents."""
        return [doc for doc in self.documents if doc.processed]

    def get_unprocessed_documents(self) -> List[DocumentInfo]:
        """Get list of unprocessed documents."""
        return [doc for doc in self.documents if not doc.processed]

    def add_task_record(self, record: TaskExecutionRecord):
        """Add a task execution record."""
        self.task_history.append(record)
        self.update_timestamp()

    def get_task_history(self, task_name: Optional[str] = None) -> List[TaskExecutionRecord]:
        """Get task history, optionally filtered by task name."""
        if task_name:
            return [r for r in self.task_history if r.task_name == task_name]
        return self.task_history

    def get_recent_tasks(self, limit: int = 10) -> List[TaskExecutionRecord]:
        """Get recent task executions."""
        sorted_tasks = sorted(self.task_history, key=lambda r: r.executed_at, reverse=True)
        return sorted_tasks[:limit]

    def set_themes(self, themes: List[Dict[str, Any]]):
        """Set themes for this project."""
        self.themes = themes
        self.update_timestamp()

    def clear_themes(self):
        """Clear all themes."""
        self.themes = []
        self.update_timestamp()

    def get_statistics(self) -> Dict[str, Any]:
        """Get project statistics."""
        total_docs = len(self.documents)
        processed_docs = len(self.get_processed_documents())
        total_size = sum(doc.file_size for doc in self.documents)

        task_counts = {}
        for record in self.task_history:
            task_counts[record.task_name] = task_counts.get(record.task_name, 0) + 1

        return {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "unprocessed_documents": total_docs - processed_docs,
            "total_size_bytes": total_size,
            "total_themes": len(self.themes),
            "total_tasks_executed": len(self.task_history),
            "task_counts": task_counts,
            "age_days": (datetime.now() - self.created_at).days,
        }

    # ========== Serialization ==========

    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for JSON serialization."""
        return {
            "id": str(self.id),  # Ensure UUID objects are converted to strings
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_opened_at": self.last_opened_at.isoformat() if self.last_opened_at else None,
            "documents": [doc.to_dict() for doc in self.documents],
            "task_history": [record.to_dict() for record in self.task_history],
            "themes": convert_uuids_to_strings(self.themes),  # Convert any UUID objects in themes
            "synthesis_cache": self.synthesis_cache.to_dict() if self.synthesis_cache else None,
            "settings": self.settings.to_dict(),
            "tags": self.tags,
            "is_archived": self.is_archived,
            "is_favorite": self.is_favorite,
            "color": self.color,
            "author": self.author,
            "notes": self.notes,
            "custom_fields": self.custom_fields,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create project from dictionary."""
        project = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            last_opened_at=(
                datetime.fromisoformat(data["last_opened_at"])
                if data.get("last_opened_at")
                else None
            ),
            documents=[DocumentInfo.from_dict(d) for d in data.get("documents", [])],
            task_history=[TaskExecutionRecord.from_dict(r) for r in data.get("task_history", [])],
            themes=data.get("themes", []),
            synthesis_cache=(
                SynthesisCache.from_dict(data["synthesis_cache"])
                if data.get("synthesis_cache")
                else None
            ),
            settings=ProjectSettings.from_dict(data.get("settings", {})),
            tags=data.get("tags", []),
            is_archived=data.get("is_archived", False),
            is_favorite=data.get("is_favorite", False),
            color=data.get("color"),
            author=data.get("author", ""),
            notes=data.get("notes", ""),
            custom_fields=data.get("custom_fields", {}),
        )
        return project

    def save_to_file(self, file_path: Path):
        """Save project to JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "Project":
        """Load project from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (
            f"Project('{self.name}', "
            f"{stats['total_documents']} docs, "
            f"{stats['total_themes']} themes, "
            f"{stats['total_tasks_executed']} tasks executed)"
        )
