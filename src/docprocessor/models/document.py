"""Document model representing a document (PDF, TXT, DOCX)."""

from datetime import datetime
from pathlib import Path
from typing import ClassVar, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Document(BaseModel):
    """Represents a document with metadata."""

    # Supported file extensions
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".pdf", ".txt", ".docx"}

    id: UUID = Field(default_factory=uuid4, description="Unique document identifier")
    file_path: Path = Field(..., description="Path to the document file")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    page_count: int = Field(0, description="Number of pages in the document")
    file_size: int = Field(0, description="File size in bytes")
    text_content: Optional[str] = Field(None, description="Full extracted text content")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when document was added"
    )
    processed: bool = Field(False, description="Whether document has been processed")

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: Path) -> Path:
        """Validate that the file path exists and is a supported document type."""
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        if v.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {v.suffix}. "
                f"Supported types: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
        return v

    class Config:
        arbitrary_types_allowed = True
