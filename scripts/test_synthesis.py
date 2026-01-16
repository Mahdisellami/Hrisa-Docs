#!/usr/bin/env python3
"""Test script for book synthesis from document collection."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.output_formatter import OutputFormatter
from docprocessor.core.synthesis_engine import SynthesisEngine
from docprocessor.core.theme_analyzer import ThemeAnalyzer
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.utils.logger import setup_logger

logger = setup_logger("test_synthesis", level=settings.log_level_int)


def test_synthesis(
    pdf_paths: list[Path] = None,
    use_existing: bool = False,
    n_themes: int = None,
    book_title: str = "Synthesized Document",
    book_author: str = None,
    target_chapter_length: int = 1500,
    chunks_per_chapter: int = 100,
    output_format: str = "all",
    pdf_template: str = "academic",
    synthesis_level: str = None,
) -> None:
    """
    Test end-to-end book synthesis from documents.

    Args:
        pdf_paths: List of PDF files to process
        use_existing: Use existing vector store data
        n_themes: Number of themes (auto-detect if None)
        book_title: Title for generated book
        book_author: Optional author name
        target_chapter_length: Target word count per chapter
        output_format: Output format (markdown, docx, text, or all)
    """
    print("\n" + "=" * 80)
    print("BOOK SYNTHESIS TEST")
    print("=" * 80)

    # Initialize components
    print("\n[1/8] Initializing components...")
    vector_store = VectorStore(collection_name="test_collection")
    embedder = Embedder()

    print(f"  Current collection: {vector_store.count()} chunks")

    # Check Ollama
    print("\n[2/8] Checking Ollama...")
    try:
        ollama_client = OllamaClient()
        print(f"  [OK] Ollama running with model: {ollama_client.model}")
    except Exception as e:
        print(f"  [ERROR] Ollama error: {e}")
        print("\n  Please ensure Ollama is running")
        return

    # Process PDFs if provided
    if pdf_paths and not use_existing:
        print(f"\n[3/8] Processing {len(pdf_paths)} PDFs...")
        processor = DocumentProcessor()

        all_chunks = []
        for pdf_path in pdf_paths:
            print(f"  Processing: {pdf_path.name}")
            document, chunks = processor.process_document(pdf_path)
            all_chunks.extend(chunks)
            print(f"    [OK] {len(chunks)} chunks")

        print(f"\n  Total chunks: {len(all_chunks)}")

        print("\n[4/8] Generating embeddings and storing...")
        chunks_with_embeddings = embedder.embed_chunks(all_chunks, show_progress=False)
        vector_store.clear_collection()
        vector_store.add_chunks(chunks_with_embeddings)
        print(f"  [OK] Stored {len(chunks_with_embeddings)} chunks")
    else:
        print(f"\n[3/8] Using existing data")
        print(f"[4/8] Current collection: {vector_store.count()} chunks")

    if vector_store.count() < 3:
        print("\n[ERROR] Need at least 3 chunks for synthesis")
        print("  Process more PDFs first")
        return

    # Discover themes
    print(f"\n[5/8] Discovering themes...")
    analyzer = ThemeAnalyzer(
        vector_store=vector_store,
        ollama_client=ollama_client,
    )

    if n_themes:
        print(f"  Requested themes: {n_themes}")
    else:
        print(f"  Auto-detecting optimal number of themes...")

    themes = analyzer.discover_themes(n_themes=n_themes)

    if not themes:
        print("\n[ERROR] No themes discovered")
        return

    print(f"\n  Discovered {len(themes)} themes:")
    for i, theme in enumerate(themes, 1):
        print(f"    {i}. {theme.label} ({len(theme.chunk_ids)} chunks, {theme.importance_score:.1%})")

    # Calculate target_chapter_length based on synthesis_level if specified
    if synthesis_level:
        total_chunks = vector_store.count()
        avg_chunk_words = 150  # Rough estimate
        total_source_words = total_chunks * avg_chunk_words

        # Calculate synthesis ratio
        if synthesis_level == "short":
            ratio = 0.15  # 15% of source
        elif synthesis_level == "normal":
            ratio = 0.30  # 30% of source
        else:  # comprehensive
            ratio = 0.50  # 50% of source

        target_total_words = int(total_source_words * ratio)
        target_chapter_length = target_total_words // len(themes)

        print(f"  Synthesis level: {synthesis_level}")
        print(f"  Calculated target: ~{target_total_words} words total, ~{target_chapter_length} per chapter")

    # Generate book
    print(f"\n[6/8] Generating book: '{book_title}'...")
    synthesis_engine = SynthesisEngine(
        vector_store=vector_store,
        ollama_client=ollama_client,
    )

    chapters = synthesis_engine.generate_book(
        themes=themes,
        book_title=book_title,
        target_chapter_length=target_chapter_length,
        max_chunks_per_chapter=chunks_per_chapter,
    )

    print(f"  [OK] Generated {len(chapters)} chapters")
    total_words = sum(c.word_count for c in chapters)
    print(f"  Total words: {total_words}")

    # Display chapter summary
    print("\n  Chapter Summary:")
    for chapter in chapters:
        print(f"    Ch.{chapter.chapter_number}: {chapter.title}")
        print(f"      {chapter.word_count} words, {len(chapter.citations)} citations")

    # Export to formats
    print(f"\n[7/8] Exporting to {output_format} format(s)...")
    formatter = OutputFormatter()

    output_paths = {}
    try:
        if output_format == "all":
            output_paths = formatter.export_all_formats(
                chapters, book_title, book_author,
                include_pdf=True,
                pdf_template=pdf_template
            )
        elif output_format == "markdown":
            output_paths["markdown"] = formatter.export_markdown(chapters, book_title, book_author)
        elif output_format == "docx":
            output_paths["docx"] = formatter.export_docx(chapters, book_title, book_author)
        elif output_format == "text":
            output_paths["text"] = formatter.export_plain_text(chapters, book_title, book_author)
        elif output_format == "pdf":
            output_paths["pdf"] = formatter.export_pdf(
                chapters, book_title, book_author,
                template=pdf_template
            )
        else:
            print(f"  [ERROR] Unknown format: {output_format}")
            return

        print(f"  [OK] Exported to {len(output_paths)} format(s):")
        for fmt, path in output_paths.items():
            print(f"    - {fmt.upper()}: {path}")

    except Exception as e:
        print(f"  [ERROR] Export error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Summary
    print("\n[8/8] Synthesis complete!")
    print("\n" + "=" * 80)
    print("SYNTHESIS SUMMARY")
    print("=" * 80)
    print(f"Book Title: {book_title}")
    if book_author:
        print(f"Author: {book_author}")
    print(f"Themes: {len(themes)}")
    print(f"Chapters: {len(chapters)}")
    print(f"Total Words: {total_words}")
    print(f"Output Files: {len(output_paths)}")
    for fmt, path in output_paths.items():
        print(f"  - {fmt.upper()}: {path.name}")

    print("\n" + "=" * 80)
    print("[OK] BOOK SYNTHESIS COMPLETE")
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test book synthesis from documents")
    parser.add_argument(
        "pdf_paths",
        type=Path,
        nargs="*",
        help="Paths to PDF files (optional if using existing data)",
    )
    parser.add_argument(
        "-n",
        "--n-themes",
        type=int,
        help="Number of themes to discover (auto-detect if not specified)",
    )
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Use existing vector store data",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Synthesized Document",
        help="Book title (default: 'Synthesized Document')",
    )
    parser.add_argument(
        "--author",
        type=str,
        help="Book author name",
    )
    parser.add_argument(
        "--chapter-length",
        type=int,
        default=1500,
        help="Target word count per chapter (default: 1500)",
    )
    parser.add_argument(
        "--target-words",
        type=int,
        help="Target total word count for entire book",
    )
    parser.add_argument(
        "--chunks-per-chapter",
        type=int,
        default=100,
        help="Number of source chunks to use per chapter (default: 100)",
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["summary", "moderate", "comprehensive", "exhaustive"],
        default="moderate",
        help="Content depth level (default: moderate)",
    )
    parser.add_argument(
        "--synthesis-level",
        type=str,
        choices=["short", "normal", "comprehensive"],
        help="Synthesis level relative to source material (overrides --chapter-length)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "docx", "text", "pdf", "all"],
        default="all",
        help="Output format (default: all)",
    )
    parser.add_argument(
        "--pdf-template",
        type=str,
        choices=["academic", "professional", "simple"],
        default="academic",
        help="PDF template style (default: academic)",
    )

    args = parser.parse_args()

    # Validate PDF paths
    if args.pdf_paths:
        for pdf_path in args.pdf_paths:
            if not pdf_path.exists():
                print(f"Error: PDF file not found: {pdf_path}")
                sys.exit(1)

    test_synthesis(
        pdf_paths=args.pdf_paths if args.pdf_paths else None,
        use_existing=args.use_existing,
        n_themes=args.n_themes,
        book_title=args.title,
        book_author=args.author,
        target_chapter_length=args.chapter_length,
        chunks_per_chapter=args.chunks_per_chapter,
        output_format=args.format,
        pdf_template=args.pdf_template,
        synthesis_level=args.synthesis_level,
    )


if __name__ == "__main__":
    main()
