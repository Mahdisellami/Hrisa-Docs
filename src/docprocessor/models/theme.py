"""Theme model representing a discovered theme from document corpus."""

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Theme(BaseModel):
    """Represents a discovered theme from document analysis."""

    id: UUID = Field(default_factory=uuid4, description="Unique theme identifier")
    label: str = Field(..., description="Human-readable theme label")
    description: Optional[str] = Field(None, description="Detailed theme description")
    chunk_ids: list[UUID] = Field(default_factory=list, description="IDs of chunks in this theme")
    keywords: list[str] = Field(default_factory=list, description="Key terms for this theme")
    importance_score: float = Field(
        0.0, ge=0.0, le=1.0, description="Importance score (0.0 to 1.0)"
    )
    chapter_order: Optional[int] = Field(None, description="Order in final book structure")
    merged_from: list[UUID] = Field(
        default_factory=list, description="Theme IDs that were merged into this one"
    )

    @property
    def chunk_count(self) -> int:
        """Number of chunks in this theme."""
        return len(self.chunk_ids)

    def __str__(self) -> str:
        """String representation."""
        return f"Theme('{self.label}', {self.chunk_count} chunks)"
