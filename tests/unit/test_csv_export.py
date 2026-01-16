"""Tests for CSV export functionality."""

import csv

import pytest

from docprocessor.core.figure_extractor import FigureExtractor
from docprocessor.models.extracted_figure import ExtractedFigure, FigureType


class TestCSVExport:
    """Test CSV export functionality."""

    @pytest.fixture
    def sample_figures(self):
        """Create sample figures for testing."""
        return [
            ExtractedFigure(
                value="€45.3 milliards",
                figure_type=FigureType.CURRENCY,
                numeric_value=45300000000.0,
                currency_code="EUR",
                year=2025,
                paragraph_number=1,
                context_sentence="Le budget en 2025 s'élève à €45.3 milliards",
            ),
            ExtractedFigure(
                value="23.4%",
                figure_type=FigureType.PERCENTAGE,
                numeric_value=23.4,
                unit="%",
                year=2024,
                paragraph_number=2,
                context_sentence="La croissance est de 23.4% en 2024",
            ),
            ExtractedFigure(
                value="12,456",
                figure_type=FigureType.QUANTITY,
                numeric_value=12456.0,
                unit="fonctionnaires",
                paragraph_number=3,
                context_sentence="Le ministère emploie 12,456 fonctionnaires",
            ),
        ]

    def test_csv_export_basic(self, sample_figures, tmp_path):
        """Test basic CSV export."""
        csv_file = tmp_path / "test_export.csv"

        # Write CSV
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Value", "Numeric Value", "Year"])

            for figure in sample_figures:
                writer.writerow(
                    [figure.figure_type.value, figure.value, figure.numeric_value, figure.year]
                )

        # Verify file exists
        assert csv_file.exists()

        # Read and verify
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        assert rows[0]["Type"] == "currency"
        assert rows[0]["Value"] == "€45.3 milliards"
        assert rows[1]["Type"] == "percentage"
        assert rows[2]["Type"] == "quantity"

    def test_csv_export_with_table_data(self, tmp_path):
        """Test CSV export with table figures."""
        figure = ExtractedFigure(
            value="40.1",
            figure_type=FigureType.CURRENCY,
            numeric_value=40.1,
            currency_code="EUR",
            is_from_table=True,
            table_index=0,
            table_row=1,
            table_column=1,
            table_column_header="Budget",
            context_sentence="Budget data from table",
        )

        csv_file = tmp_path / "table_export.csv"

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Type",
                    "Value",
                    "Is From Table",
                    "Table Index",
                    "Table Row",
                    "Table Column",
                    "Column Header",
                ]
            )
            writer.writerow(
                [
                    figure.figure_type.value,
                    figure.value,
                    "Yes" if figure.is_from_table else "No",
                    figure.table_index,
                    figure.table_row,
                    figure.table_column,
                    figure.table_column_header,
                ]
            )

        # Verify
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["Is From Table"] == "Yes"
        assert row["Table Index"] == "0"
        assert row["Table Row"] == "1"
        assert row["Column Header"] == "Budget"

    def test_csv_export_unicode(self, tmp_path):
        """Test CSV export with Unicode characters."""
        figure = ExtractedFigure(
            value="€45.3 milliards",
            figure_type=FigureType.CURRENCY,
            numeric_value=45300000000.0,
            currency_code="EUR",
            context_sentence="Le budget français s'élève à €45.3 milliards",
        )

        csv_file = tmp_path / "unicode_export.csv"

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Value", "Context"])
            writer.writerow([figure.figure_type.value, figure.value, figure.context_sentence])

        # Verify Unicode is preserved
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "€" in content
        assert "français" in content
        assert "élève" in content

    def test_csv_export_empty_fields(self, tmp_path):
        """Test CSV export with empty/null fields."""
        figure = ExtractedFigure(
            value="2025",
            figure_type=FigureType.DATE,
            numeric_value=2025.0,
            # No year, no unit, no currency_code
            context_sentence="Year 2025",
        )

        csv_file = tmp_path / "empty_fields.csv"

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Value", "Unit", "Year"])
            writer.writerow(
                [
                    figure.figure_type.value,
                    figure.value,
                    figure.unit or "",
                    figure.year if figure.year else "",
                ]
            )

        # Verify empty fields are handled
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["Type"] == "date"
        assert row["Unit"] == ""
        assert row["Year"] == ""

    def test_csv_export_large_dataset(self, tmp_path):
        """Test CSV export with many figures."""
        figures = []
        for i in range(100):
            figures.append(
                ExtractedFigure(
                    value=f"€{i}.5 millions",
                    figure_type=FigureType.CURRENCY,
                    numeric_value=float(i) * 1000000 + 500000,
                    currency_code="EUR",
                    year=2020 + (i % 6),
                    paragraph_number=i,
                    context_sentence=f"Budget item {i}",
                )
            )

        csv_file = tmp_path / "large_export.csv"

        # Export
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Value", "Numeric Value", "Year"])

            for figure in figures:
                writer.writerow(
                    [figure.figure_type.value, figure.value, figure.numeric_value, figure.year]
                )

        # Verify all rows exported
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 100

    def test_csv_export_special_characters(self, tmp_path):
        """Test CSV export with special characters in context."""
        figure = ExtractedFigure(
            value="€100",
            figure_type=FigureType.CURRENCY,
            numeric_value=100.0,
            currency_code="EUR",
            context_sentence='Budget "quoted", with comma, and newline\nin text',
        )

        csv_file = tmp_path / "special_chars.csv"

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Context"])
            writer.writerow([figure.figure_type.value, figure.context_sentence])

        # Verify special characters are properly escaped
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)

        # CSV should handle quotes and newlines correctly
        assert '"quoted"' in row["Context"] or "quoted" in row["Context"]
        assert "comma" in row["Context"]

    def test_csv_integration_full_workflow(self, tmp_path):
        """Test full workflow: extract → CSV → read back."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text(
            """
Le budget 2025 est de €45.3 milliards.
La croissance est de 23.4%.
Le ministère emploie 12,456 fonctionnaires.
"""
        )

        # Extract
        extractor = FigureExtractor()
        result = extractor.extract_from_document(test_file)

        assert result.total_figures > 0

        # Export to CSV
        csv_file = tmp_path / "export.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Value", "Numeric Value", "Unit/Currency", "Year", "Context"])

            for figure in result.figures:
                writer.writerow(
                    [
                        figure.figure_type.value,
                        figure.value,
                        figure.numeric_value if figure.numeric_value else "",
                        figure.currency_code or figure.unit or "",
                        figure.year if figure.year else "",
                        figure.context_sentence,
                    ]
                )

        # Read back and verify
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == result.total_figures

        # Verify we can find currency figure
        currency_rows = [r for r in rows if r["Type"] == "currency"]
        assert len(currency_rows) > 0
        assert "45.3" in currency_rows[0]["Value"]

        # Verify percentage
        percentage_rows = [r for r in rows if r["Type"] == "percentage"]
        assert len(percentage_rows) > 0
        assert "23.4" in percentage_rows[0]["Value"]
