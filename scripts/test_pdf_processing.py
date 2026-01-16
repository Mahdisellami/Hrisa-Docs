#!/usr/bin/env python3
"""Test script for PDF processing functionality."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.utils.logger import setup_logger

logger = setup_logger("test_pdf", level=settings.log_level_int)


def test_pdf_processing(pdf_path: Path, verbose: bool = False) -> None:
    """
    Test PDF processing on a given file.

    Args:
        pdf_path: Path to PDF file
        verbose: Print detailed output
    """
    logger.info(f"Testing PDF processing on: {pdf_path}")

    processor = DocumentProcessor()

    try:
        document, chunks = processor.process_document(pdf_path)

        print("\n" + "=" * 80)
        print("DOCUMENT INFORMATION")
        print("=" * 80)
        print(f"Title: {document.title}")
        print(f"Author: {document.author or 'Unknown'}")
        print(f"Pages: {document.page_count}")
        print(f"File Size: {document.file_size:,} bytes")
        print(f"Total Characters: {len(document.text_content):,}")
        print(f"Processed: {document.processed}")

        print("\n" + "=" * 80)
        print("CHUNKING RESULTS")
        print("=" * 80)
        print(f"Total Chunks: {len(chunks)}")
        print(f"Chunk Size Setting: {processor.chunk_size} tokens")
        print(f"Chunk Overlap: {processor.chunk_overlap} tokens")

        if chunks:
            avg_chunk_size = sum(chunk.token_count for chunk in chunks) / len(chunks)
            min_chunk_size = min(chunk.token_count for chunk in chunks)
            max_chunk_size = max(chunk.token_count for chunk in chunks)

            print(f"\nChunk Statistics:")
            print(f"  Average size: {avg_chunk_size:.0f} tokens")
            print(f"  Min size: {min_chunk_size} tokens")
            print(f"  Max size: {max_chunk_size} tokens")

        if verbose and chunks:
            print("\n" + "=" * 80)
            print("FIRST 3 CHUNKS (PREVIEW)")
            print("=" * 80)
            for i, chunk in enumerate(chunks[:3], 1):
                print(f"\nChunk {i}:")
                print(f"  Page: {chunk.page_number}")
                print(f"  Tokens: {chunk.token_count}")
                print(f"  Position: chars {chunk.start_char}-{chunk.end_char}")
                print(f"  Text Preview: {chunk.text[:200]}...")

        print("\n" + "=" * 80)
        print("TEST PASSED ✓")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print("\n" + "=" * 80)
        print("TEST FAILED ✗")
        print("=" * 80)
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test PDF processing functionality")
    parser.add_argument("pdf_path", type=Path, help="Path to PDF file to test")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed chunk information"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.chunk_size,
        help=f"Chunk size in tokens (default: {settings.chunk_size})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.chunk_overlap,
        help=f"Chunk overlap in tokens (default: {settings.chunk_overlap})",
    )

    args = parser.parse_args()

    if not args.pdf_path.exists():
        print(f"Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)

    if args.chunk_size != settings.chunk_size or args.chunk_overlap != settings.chunk_overlap:
        settings.chunk_size = args.chunk_size
        settings.chunk_overlap = args.chunk_overlap

    test_pdf_processing(args.pdf_path, verbose=args.verbose)


if __name__ == "__main__":
    main()
