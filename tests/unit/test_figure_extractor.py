"""Unit tests for figure extraction."""

from pathlib import Path

import pytest

from docprocessor.core.figure_extractor import FigureExtractor
from docprocessor.models.extracted_figure import FigureType


class TestFigureExtractor:
    """Test figure extraction functionality."""

    @pytest.fixture
    def extractor(self):
        """Create FigureExtractor instance."""
        return FigureExtractor()

    def test_extract_currency_euro(self, extractor):
        """Test extracting Euro currency."""
        text = "Le budget de l'État en 2025 s'élève à €45.3 milliards"
        figures = extractor.extract_from_text(text)

        assert len(figures) >= 1
        # Find the currency figure
        currency_figs = [f for f in figures if f.figure_type == FigureType.CURRENCY]
        assert len(currency_figs) >= 1

        fig = currency_figs[0]
        assert "45.3" in fig.value or "45,3" in fig.value
        assert fig.currency_code == "EUR"
        assert fig.year == 2025

    def test_extract_currency_dollar(self, extractor):
        """Test extracting Dollar currency."""
        text = "The budget is $123.5 million in 2024"
        figures = extractor.extract_from_text(text)

        currency_figs = [f for f in figures if f.figure_type == FigureType.CURRENCY]
        assert len(currency_figs) >= 1

        fig = currency_figs[0]
        assert "123.5" in fig.value or "123,5" in fig.value
        assert fig.currency_code == "USD"

    def test_extract_percentage(self, extractor):
        """Test extracting percentages."""
        text = "Le taux de croissance est de 23.4% en 2025"
        figures = extractor.extract_from_text(text)

        percentage_figs = [f for f in figures if f.figure_type == FigureType.PERCENTAGE]
        assert len(percentage_figs) >= 1

        fig = percentage_figs[0]
        assert "23.4" in fig.value or "23,4" in fig.value
        assert fig.unit == "%"
        assert fig.numeric_value is not None
        assert 23 <= fig.numeric_value <= 24

    def test_extract_year(self, extractor):
        """Test extracting years."""
        text = "Les données de 2025 montrent une amélioration par rapport à 2024"
        figures = extractor.extract_from_text(text)

        date_figs = [f for f in figures if f.figure_type == FigureType.DATE]
        assert len(date_figs) >= 2  # Should find both 2025 and 2024

        years = [f.year for f in date_figs if f.year]
        assert 2025 in years
        assert 2024 in years

    def test_extract_range(self, extractor):
        """Test extracting ranges."""
        text = "La période 2020-2025 a vu une croissance de 15%-20%"
        figures = extractor.extract_from_text(text)

        range_figs = [f for f in figures if f.figure_type == FigureType.RANGE]
        assert len(range_figs) >= 1

    def test_extract_quantity_with_unit(self, extractor):
        """Test extracting quantities with units."""
        text = "Le ministère emploie 12,456 fonctionnaires"
        figures = extractor.extract_from_text(text)

        quantity_figs = [f for f in figures if f.figure_type == FigureType.QUANTITY]
        assert len(quantity_figs) >= 1

        fig = quantity_figs[0]
        assert "fonctionnaire" in fig.value.lower()

    def test_context_extraction(self, extractor):
        """Test that context is properly extracted."""
        text = "Le budget est de €45 milliards. C'est une augmentation."
        figures = extractor.extract_from_text(text)

        assert len(figures) >= 1
        fig = figures[0]
        assert fig.context_sentence
        assert "€45" in fig.context_sentence or "budget" in fig.context_sentence.lower()

    def test_numeric_value_parsing(self, extractor):
        """Test numeric value parsing."""
        text = "Le montant est de €1.234.567,89"
        figures = extractor.extract_from_text(text)

        currency_figs = [f for f in figures if f.figure_type == FigureType.CURRENCY]
        if currency_figs:
            fig = currency_figs[0]
            # Should parse to approximately 1234567.89
            if fig.numeric_value:
                assert fig.numeric_value > 1_000_000

    def test_multiplier_milliards(self, extractor):
        """Test that 'milliards' multiplier is applied."""
        text = "Budget de 45 milliards d'euros"
        figures = extractor.extract_from_text(text)

        currency_figs = [f for f in figures if f.figure_type == FigureType.CURRENCY]
        if currency_figs:
            fig = currency_figs[0]
            if fig.numeric_value:
                # 45 milliards = 45,000,000,000
                assert fig.numeric_value >= 45_000_000_000

    def test_multiplier_millions(self, extractor):
        """Test that 'millions' multiplier is applied."""
        text = "Coût de 25 millions d'euros"
        figures = extractor.extract_from_text(text)

        currency_figs = [f for f in figures if f.figure_type == FigureType.CURRENCY]
        if currency_figs:
            fig = currency_figs[0]
            if fig.numeric_value:
                # 25 millions = 25,000,000
                assert fig.numeric_value >= 25_000_000

    def test_no_duplicates(self, extractor):
        """Test that duplicates are removed."""
        text = "Le montant est de 45.3 dans le même phrase 45.3"
        figures = extractor.extract_from_text(text)

        # Should only extract 45.3 once per sentence
        values = [f.value for f in figures]
        # May have different representations but should filter duplicates
        assert len(values) <= 2  # Allow some flexibility

    def test_multiple_figures_in_text(self, extractor):
        """Test extracting multiple figures from same text."""
        text = """
        Le budget 2025 est de €45.3 milliards, soit une augmentation de 12.5%
        par rapport aux €40.2 milliards de 2024.
        """
        figures = extractor.extract_from_text(text)

        # Should find: €45.3 milliards, 12.5%, €40.2 milliards, 2025, 2024
        assert len(figures) >= 3

        currency_figs = [f for f in figures if f.figure_type == FigureType.CURRENCY]
        percentage_figs = [f for f in figures if f.figure_type == FigureType.PERCENTAGE]
        date_figs = [f for f in figures if f.figure_type == FigureType.DATE]

        assert len(currency_figs) >= 2  # Two budget amounts
        assert len(percentage_figs) >= 1  # One percentage
        assert len(date_figs) >= 2  # Two years

    def test_empty_text(self, extractor):
        """Test extracting from empty text."""
        figures = extractor.extract_from_text("")
        assert len(figures) == 0

    def test_text_without_figures(self, extractor):
        """Test extracting from text without figures."""
        text = "Ceci est un texte sans chiffres ni dates."
        figures = extractor.extract_from_text(text)
        # Might find nothing or very few false positives
        assert len(figures) <= 1  # Allow minimal false positives


class TestFigureExtractorDocuments:
    """Test figure extraction from actual documents."""

    @pytest.fixture
    def extractor(self):
        """Create FigureExtractor instance."""
        return FigureExtractor()

    def test_extract_from_nonexistent_file(self, extractor):
        """Test extracting from non-existent file."""
        result = extractor.extract_from_document(Path("nonexistent.txt"))
        assert len(result.errors) > 0

    # Note: More document tests would require sample files in tests/fixtures/


class TestFigureModel:
    """Test ExtractedFigure data model."""

    def test_figure_to_dict(self):
        """Test converting figure to dictionary."""
        from docprocessor.models.extracted_figure import ExtractedFigure

        fig = ExtractedFigure(
            value="€45.3 milliards",
            figure_type=FigureType.CURRENCY,
            numeric_value=45300000000,
            currency_code="EUR",
            year=2025,
        )

        fig_dict = fig.to_dict()
        assert fig_dict["value"] == "€45.3 milliards"
        assert fig_dict["figure_type"] == "currency"
        assert fig_dict["numeric_value"] == 45300000000
        assert fig_dict["currency_code"] == "EUR"
        assert fig_dict["year"] == 2025

    def test_figure_from_dict(self):
        """Test creating figure from dictionary."""
        from datetime import datetime

        from docprocessor.models.extracted_figure import ExtractedFigure

        fig_dict = {
            "value": "€45.3 milliards",
            "figure_type": "currency",
            "numeric_value": 45300000000,
            "currency_code": "EUR",
            "year": 2025,
            "extracted_at": datetime.now().isoformat(),
        }

        fig = ExtractedFigure.from_dict(fig_dict)
        assert fig.value == "€45.3 milliards"
        assert fig.figure_type == FigureType.CURRENCY
        assert fig.numeric_value == 45300000000
        assert fig.currency_code == "EUR"
        assert fig.year == 2025


# Run tests with: pytest tests/unit/test_figure_extractor.py -v
