#!/usr/bin/env python3
"""Standalone test script for figure extraction functionality.

This script allows testing the figure extraction feature without full GUI integration.

Usage:
    python test_figure_extraction.py <path_to_document>

Examples:
    python test_figure_extraction.py data/test_document.pdf
    python test_figure_extraction.py data/test_document.docx
    python test_figure_extraction.py data/test_document.txt
"""

import sys
from pathlib import Path
from docprocessor.core.figure_extractor import FigureExtractor
from docprocessor.models.extracted_figure import FigureType


def print_separator():
    """Print a visual separator."""
    print("=" * 80)


def main():
    """Run figure extraction test."""
    if len(sys.argv) < 2:
        print("Usage: python test_figure_extraction.py <path_to_document>")
        print("\nExamples:")
        print("  python test_figure_extraction.py data/test_document.pdf")
        print("  python test_figure_extraction.py data/test_document.docx")
        sys.exit(1)

    document_path = Path(sys.argv[1])

    if not document_path.exists():
        print(f"Error: File not found: {document_path}")
        sys.exit(1)

    print(f"📄 Testing Figure Extraction")
    print_separator()
    print(f"Document: {document_path}")
    print(f"File size: {document_path.stat().st_size / 1024:.2f} KB")
    print_separator()

    # Create extractor
    print("\n🔍 Initializing figure extractor...")
    extractor = FigureExtractor()

    # Extract figures
    print(f"📊 Extracting figures from {document_path.name}...")
    result = extractor.extract_from_document(document_path)

    # Print results
    print_separator()
    print("✅ EXTRACTION RESULTS")
    print_separator()
    print(f"Total figures extracted: {result.total_figures}")
    print(f"Tables parsed: {result.tables_parsed}")
    print(f"Extraction time: {result.extraction_time_seconds:.2f} seconds")

    if result.errors:
        print(f"\n⚠️  Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error}")

    # Print breakdown by type
    print("\n📈 Breakdown by Type:")
    for fig_type, count in result.figures_by_type.items():
        print(f"  {fig_type.capitalize()}: {count}")

    # Print detailed figures
    if result.figures:
        print("\n" + "=" * 80)
        print("📋 DETAILED FIGURES")
        print_separator()

        for i, figure in enumerate(result.figures[:20], 1):  # Show first 20
            print(f"\n[{i}] {figure.figure_type.value.upper()}")
            print(f"  Value: {figure.value}")
            if figure.numeric_value:
                print(f"  Numeric: {figure.numeric_value:,.2f}")
            if figure.unit:
                print(f"  Unit: {figure.unit}")
            if figure.currency_code:
                print(f"  Currency: {figure.currency_code}")
            if figure.year:
                print(f"  Year: {figure.year}")

            # Location
            if figure.is_from_table:
                location = f"Table {figure.table_index}, Row {figure.table_row}, Col {figure.table_column}"
                if figure.table_column_header:
                    location += f" (Column: {figure.table_column_header})"
                print(f"  Location: {location}")
            elif figure.page_number:
                print(f"  Location: Page {figure.page_number}, Paragraph {figure.paragraph_number}")
            else:
                print(f"  Location: Paragraph {figure.paragraph_number}")

            # Context (truncated)
            context = figure.context_sentence[:100]
            if len(figure.context_sentence) > 100:
                context += "..."
            print(f"  Context: {context}")

        if len(result.figures) > 20:
            print(f"\n... and {len(result.figures) - 20} more figures")

    print("\n" + "=" * 80)
    print("✅ Test complete!")
    print_separator()

    # Summary for different figure types
    print("\n📊 SUMMARY BY TYPE:")

    # Currency figures
    currency_figs = result.get_figures_by_type(FigureType.CURRENCY)
    if currency_figs:
        print(f"\n💰 Currency Figures ({len(currency_figs)}):")
        for fig in currency_figs[:5]:
            print(f"  - {fig.value} (Year: {fig.year or 'N/A'})")

    # Percentage figures
    percentage_figs = result.get_figures_by_type(FigureType.PERCENTAGE)
    if percentage_figs:
        print(f"\n📊 Percentages ({len(percentage_figs)}):")
        for fig in percentage_figs[:5]:
            print(f"  - {fig.value} (Year: {fig.year or 'N/A'})")

    # Date figures
    date_figs = result.get_figures_by_type(FigureType.DATE)
    if date_figs:
        print(f"\n📅 Dates ({len(date_figs)}):")
        years = set(f.year for f in date_figs if f.year)
        print(f"  Years found: {sorted(years)}")

    print("\n✨ Done!")


if __name__ == "__main__":
    main()
