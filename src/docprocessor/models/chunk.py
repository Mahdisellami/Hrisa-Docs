"""Chunk model representing a text chunk from a document."""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """Represents a chunk of text from a document."""

    id: UUID = Field(default_factory=uuid4, description="Unique chunk identifier")
    document_id: UUID = Field(..., description="ID of the source document")
    text: str = Field(..., description="Chunk text content")
    page_number: Optional[int] = Field(None, description="Source page number")
    section: Optional[str] = Field(None, description="Section or heading")
    chunk_index: int = Field(..., description="Sequential index of this chunk in the document")
    start_char: int = Field(..., description="Starting character position in document")
    end_char: int = Field(..., description="Ending character position in document")
    token_count: int = Field(0, description="Number of tokens in this chunk")
    embedding: Optional[list[float]] = Field(None, description="Vector embedding")
    theme_id: Optional[UUID] = Field(None, description="Assigned theme ID")

    def __str__(self) -> str:
        """String representation showing truncated text."""
        preview = self.text[:100] + "..." if len(self.text) > 100 else self.text
        return f"Chunk({self.chunk_index}, page={self.page_number}, text='{preview}')"
