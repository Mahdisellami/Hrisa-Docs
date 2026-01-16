"""Data models for extracted figures and statistics."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class FigureType(Enum):
    """Type of extracted figure."""

    NUMBER = "number"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DATE = "date"
    QUANTITY = "quantity"  # Number with units (e.g., "1000 fonctionnaires")
    RANGE = "range"  # e.g., "2020-2025"


@dataclass
class ExtractedFigure:
    """Represents a figure/statistic extracted from a document."""

    # Core data
    value: str  # Original value as string (e.g., "€45.3 milliards", "2025", "23.4%")
    figure_type: FigureType

    # Location in document
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    sentence_index: Optional[int] = None

    # For table-extracted figures
    is_from_table: bool = False
    table_index: Optional[int] = None  # Which table in document
    table_row: Optional[int] = None
    table_column: Optional[int] = None
    table_row_header: Optional[str] = None
    table_column_header: Optional[str] = None

    # Context
    context_sentence: str = ""  # Sentence containing the figure
    context_paragraph: str = ""  # Full paragraph
    surrounding_text: str = ""  # 50 chars before + after

    # Parsed values (for comparison/updating)
    numeric_value: Optional[float] = None  # Parsed numeric value
    unit: Optional[str] = None  # e.g., "€", "%", "milliards"
    currency_code: Optional[str] = None  # EUR, USD, TND
    year: Optional[int] = None  # If this is a date or contains year reference

    # Update tracking
    confidence_score: float = 1.0  # How confident we are in the extraction (0-1)
    suggested_update: Optional[str] = None  # Suggested new value
    update_source: Optional[str] = None  # Source URL for suggested update
    update_confidence: Optional[float] = None  # Confidence in suggested update

    # Metadata
    extracted_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """String representation."""
        location = f"Page {self.page_number}" if self.page_number else "Unknown location"
        if self.is_from_table:
            location += (
                f" (Table {self.table_index}, Row {self.table_row}, Col {self.table_column})"
            )
        return f"ExtractedFigure({self.value}, {self.figure_type.value}, {location})"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "value": self.value,
            "figure_type": self.figure_type.value,
            "page_number": self.page_number,
            "paragraph_number": self.paragraph_number,
            "sentence_index": self.sentence_index,
            "is_from_table": self.is_from_table,
            "table_index": self.table_index,
            "table_row": self.table_row,
            "table_column": self.table_column,
            "table_row_header": self.table_row_header,
            "table_column_header": self.table_column_header,
            "context_sentence": self.context_sentence,
            "context_paragraph": self.context_paragraph,
            "surrounding_text": self.surrounding_text,
            "numeric_value": self.numeric_value,
            "unit": self.unit,
            "currency_code": self.currency_code,
            "year": self.year,
            "confidence_score": self.confidence_score,
            "suggested_update": self.suggested_update,
            "update_source": self.update_source,
            "update_confidence": self.update_confidence,
            "extracted_at": self.extracted_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractedFigure":
        """Create from dictionary."""
        # Convert figure_type string back to enum
        figure_type = FigureType(data["figure_type"])

        # Convert extracted_at back to datetime
        extracted_at = (
            datetime.fromisoformat(data["extracted_at"])
            if data.get("extracted_at")
            else datetime.now()
        )

        return cls(
            value=data["value"],
            figure_type=figure_type,
            page_number=data.get("page_number"),
            paragraph_number=data.get("paragraph_number"),
            sentence_index=data.get("sentence_index"),
            is_from_table=data.get("is_from_table", False),
            table_index=data.get("table_index"),
            table_row=data.get("table_row"),
            table_column=data.get("table_column"),
            table_row_header=data.get("table_row_header"),
            table_column_header=data.get("table_column_header"),
            context_sentence=data.get("context_sentence", ""),
            context_paragraph=data.get("context_paragraph", ""),
            surrounding_text=data.get("surrounding_text", ""),
            numeric_value=data.get("numeric_value"),
            unit=data.get("unit"),
            currency_code=data.get("currency_code"),
            year=data.get("year"),
            confidence_score=data.get("confidence_score", 1.0),
            suggested_update=data.get("suggested_update"),
            update_source=data.get("update_source"),
            update_confidence=data.get("update_confidence"),
            extracted_at=extracted_at,
        )


@dataclass
class FigureExtractionResult:
    """Results from figure extraction operation."""

    document_path: str
    figures: List[ExtractedFigure] = field(default_factory=list)
    total_figures: int = 0
    figures_by_type: dict = field(default_factory=dict)  # {FigureType: count}
    tables_parsed: int = 0
    extraction_time_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate statistics after initialization."""
        self.total_figures = len(self.figures)
        self.figures_by_type = {}
        for figure in self.figures:
            fig_type = figure.figure_type.value
            self.figures_by_type[fig_type] = self.figures_by_type.get(fig_type, 0) + 1

    def get_figures_by_type(self, figure_type: FigureType) -> List[ExtractedFigure]:
        """Get all figures of a specific type."""
        return [f for f in self.figures if f.figure_type == figure_type]

    def get_figures_with_year(self, year: int) -> List[ExtractedFigure]:
        """Get all figures associated with a specific year."""
        return [f for f in self.figures if f.year == year]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_path": self.document_path,
            "figures": [f.to_dict() for f in self.figures],
            "total_figures": self.total_figures,
            "figures_by_type": self.figures_by_type,
            "tables_parsed": self.tables_parsed,
            "extraction_time_seconds": self.extraction_time_seconds,
            "errors": self.errors,
        }
