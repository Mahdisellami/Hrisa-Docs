#!/usr/bin/env python3
"""Test script for theme discovery and analysis."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.theme_analyzer import ThemeAnalyzer
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.utils.logger import setup_logger

logger = setup_logger("test_themes", level=settings.log_level_int)


def test_theme_discovery(
    pdf_paths: list[Path] = None,
    n_themes: int = None,
    use_existing: bool = False,
) -> None:
    """
    Test theme discovery from documents.

    Args:
        pdf_paths: List of PDF files to process
        n_themes: Number of themes (auto-detect if None)
        use_existing: Use existing vector store data
    """
    print("\n" + "=" * 80)
    print("THEME DISCOVERY TEST")
    print("=" * 80)

    # Initialize components
    print("\n[1/5] Initializing components...")
    vector_store = VectorStore(collection_name="test_collection")
    embedder = Embedder()

    print(f"  Current collection: {vector_store.count()} chunks")

    # Check Ollama
    print("\n[2/5] Checking Ollama...")
    try:
        ollama_client = OllamaClient()
        print(f"  ✓ Ollama running with model: {ollama_client.model}")
    except Exception as e:
        print(f"  ✗ Ollama error: {e}")
        print("\n  Please ensure Ollama is running")
        return

    # Process PDFs if provided
    if pdf_paths and not use_existing:
        print(f"\n[3/5] Processing {len(pdf_paths)} PDFs...")
        processor = DocumentProcessor()

        all_chunks = []
        for pdf_path in pdf_paths:
            print(f"  Processing: {pdf_path.name}")
            document, chunks = processor.process_document(pdf_path)
            all_chunks.extend(chunks)
            print(f"    ✓ {len(chunks)} chunks")

        print(f"\n  Total chunks: {len(all_chunks)}")

        print("\n[4/5] Generating embeddings and storing...")
        chunks_with_embeddings = embedder.embed_chunks(all_chunks, show_progress=False)
        vector_store.add_chunks(chunks_with_embeddings)
        print(f"  ✓ Stored {len(chunks_with_embeddings)} chunks")
    else:
        print(f"\n[3/5] Using existing data")
        print(f"[4/5] Current collection: {vector_store.count()} chunks")

    if vector_store.count() < 3:
        print("\n✗ Need at least 3 chunks for theme discovery")
        print("  Process more PDFs first")
        return

    # Discover themes
    print(f"\n[5/5] Discovering themes...")
    analyzer = ThemeAnalyzer(
        vector_store=vector_store,
        ollama_client=ollama_client,
    )

    if n_themes:
        print(f"  Requested themes: {n_themes}")
    else:
        print(f"  Auto-detecting optimal number of themes...")

    themes = analyzer.discover_themes(n_themes=n_themes)

    # Display results
    print("\n" + "=" * 80)
    print(f"DISCOVERED {len(themes)} THEMES")
    print("=" * 80)

    for i, theme in enumerate(themes, 1):
        print(f"\n{i}. {theme.label}")
        print(f"   Importance: {theme.importance_score:.1%}")
        print(f"   Chunks: {len(theme.chunk_ids)}")

        if theme.description:
            print(f"   Description: {theme.description}")

        if theme.keywords:
            print(f"   Keywords: {', '.join(theme.keywords[:7])}")

    # Show sample chunks for first theme
    if themes:
        print("\n" + "=" * 80)
        print(f"SAMPLE CHUNKS FROM THEME 1: {themes[0].label}")
        print("=" * 80)

        # Get first 3 chunks
        for i, chunk_id in enumerate(list(themes[0].chunk_ids)[:3], 1):
            chunk = vector_store.get_by_id(chunk_id)
            if chunk:
                print(f"\nChunk {i}:")
                print(f"  {chunk['text'][:200]}...")

    print("\n" + "=" * 80)
    print("✓ THEME DISCOVERY COMPLETE")
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test theme discovery from documents")
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

    args = parser.parse_args()

    # Validate PDF paths
    if args.pdf_paths:
        for pdf_path in args.pdf_paths:
            if not pdf_path.exists():
                print(f"Error: PDF file not found: {pdf_path}")
                sys.exit(1)

    test_theme_discovery(
        pdf_paths=args.pdf_paths if args.pdf_paths else None,
        n_themes=args.n_themes,
        use_existing=args.use_existing,
    )


if __name__ == "__main__":
    main()
