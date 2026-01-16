#!/usr/bin/env python3
"""Test CSV export functionality."""

import sys
import csv
from pathlib import Path
from docprocessor.core.figure_extractor import FigureExtractor


def test_csv_export():
    """Test extracting figures and exporting to CSV."""

    # Create test document
    test_file = Path("test_documents/test_csv_export.txt")
    test_file.parent.mkdir(exist_ok=True)

    test_content = """
Le budget de l'État en 2025 s'élève à €45.3 milliards.
Le taux de croissance est de 23.4% par rapport à 2024.
Le ministère emploie 12,456 fonctionnaires.
Les recettes fiscales ont atteint €42.8 milliards en 2024.
La population est de 67.5 millions d'habitants.
"""

    test_file.write_text(test_content)
    print(f"✅ Created test file: {test_file}")

    # Extract figures
    print("\n🔍 Extracting figures...")
    extractor = FigureExtractor()
    result = extractor.extract_from_document(test_file)

    print(f"✅ Extracted {result.total_figures} figures")
    print(f"   Currency: {result.figures_by_type.get('currency', 0)}")
    print(f"   Percentage: {result.figures_by_type.get('percentage', 0)}")
    print(f"   Date: {result.figures_by_type.get('date', 0)}")
    print(f"   Quantity: {result.figures_by_type.get('quantity', 0)}")

    # Export to CSV
    csv_file = Path("test_documents/test_export.csv")
    print(f"\n📄 Exporting to CSV: {csv_file}")

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow([
            'Type',
            'Value',
            'Numeric Value',
            'Unit/Currency',
            'Year',
            'Page',
            'Paragraph',
            'Is From Table',
            'Table Index',
            'Table Row',
            'Table Column',
            'Table Row Header',
            'Table Column Header',
            'Context Sentence',
            'Confidence Score'
        ])

        # Write data rows
        for figure in result.figures:
            writer.writerow([
                figure.figure_type.value,
                figure.value,
                figure.numeric_value if figure.numeric_value else '',
                figure.currency_code or figure.unit or '',
                figure.year if figure.year else '',
                figure.page_number if figure.page_number else '',
                figure.paragraph_number if figure.paragraph_number else '',
                'Yes' if figure.is_from_table else 'No',
                figure.table_index if figure.table_index is not None else '',
                figure.table_row if figure.table_row is not None else '',
                figure.table_column if figure.table_column is not None else '',
                figure.table_row_header or '',
                figure.table_column_header or '',
                figure.context_sentence,
                figure.confidence_score
            ])

    print(f"✅ CSV export successful!")
    print(f"\n📊 CSV contains {result.total_figures} rows")

    # Verify CSV can be read back
    print("\n🔍 Verifying CSV...")
    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        print(f"✅ CSV readable: {len(rows)} rows")

        # Show first 3 rows
        print("\n📋 First 3 rows:")
        for i, row in enumerate(rows[:3], 1):
            print(f"\n   [{i}] {row['Type']}: {row['Value']}")
            print(f"       Numeric: {row['Numeric Value']}")
            print(f"       Year: {row['Year']}")
            print(f"       Context: {row['Context Sentence'][:60]}...")

    print("\n" + "=" * 80)
    print("✅ CSV Export Test PASSED!")
    print("=" * 80)


if __name__ == "__main__":
    test_csv_export()
