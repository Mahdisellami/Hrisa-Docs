"""Chapter model representing a synthesized chapter in the output document."""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    """Represents a chapter in the synthesized document."""

    id: UUID = Field(default_factory=uuid4, description="Unique chapter identifier")
    theme_id: UUID = Field(..., description="ID of the theme this chapter is based on")
    title: str = Field(..., description="Chapter title")
    content: Optional[str] = Field(None, description="Generated chapter content")
    chapter_number: int = Field(..., description="Chapter number in the book")
    outline: Optional[str] = Field(None, description="Chapter outline/plan")
    source_chunks: list[UUID] = Field(
        default_factory=list, description="IDs of chunks used to generate this chapter"
    )
    citations: list[dict[str, str]] = Field(
        default_factory=list,
        description="Citations to source documents (e.g., [{'document_id': '...', 'page': '12'}])",
    )
    word_count: int = Field(0, description="Word count of generated content")
    generated: bool = Field(False, description="Whether content has been generated")

    def add_citation(self, document_id: str, page: Optional[int] = None) -> None:
        """Add a citation to a source document."""
        citation = {"document_id": document_id}
        if page is not None:
            citation["page"] = str(page)

        if citation not in self.citations:
            self.citations.append(citation)

    def __str__(self) -> str:
        """String representation."""
        status = "generated" if self.generated else "pending"
        return f"Chapter {self.chapter_number}: {self.title} ({status})"
