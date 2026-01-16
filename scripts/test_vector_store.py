#!/usr/bin/env python3
"""Test script for complete pipeline: PDF processing, embedding, and vector storage."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.vector_store import VectorStore
from docprocessor.utils.logger import setup_logger

logger = setup_logger("test_vector_store", level=settings.log_level_int)


def test_full_pipeline(pdf_path: Path, query: str = None, auto_clear: bool = False) -> None:
    """
    Test the complete pipeline: extract, chunk, embed, store, and search.

    Args:
        pdf_path: Path to PDF file
        query: Optional search query to test retrieval
        auto_clear: Auto-clear existing data without prompting
    """
    print("\n" + "=" * 80)
    print("DOCUMENT PROCESSING & VECTOR STORAGE TEST")
    print("=" * 80)

    # Step 1: Process PDF
    print("\n[1/5] Processing PDF...")
    processor = DocumentProcessor()
    document, chunks = processor.process_document(pdf_path)
    print(f"✓ Extracted {len(chunks)} chunks from {document.title}")

    # Step 2: Generate embeddings
    print("\n[2/5] Generating embeddings...")
    embedder = Embedder()
    chunks_with_embeddings = embedder.embed_chunks(chunks, show_progress=True)
    print(f"✓ Generated embeddings (dimension: {embedder.embedding_dimension})")

    # Step 3: Store in vector database
    print("\n[3/5] Storing in vector database...")
    vector_store = VectorStore(collection_name="test_collection")

    existing_count = vector_store.count()
    if existing_count > 0:
        print(f"  Note: Collection already has {existing_count} chunks")
        if auto_clear:
            print("  Auto-clearing existing data...")
            vector_store.clear_collection()
            print("  ✓ Collection cleared")
        else:
            clear = input("  Clear existing data? (y/N): ").strip().lower()
            if clear == "y":
                vector_store.clear_collection()
                print("  ✓ Collection cleared")

    vector_store.add_chunks(chunks_with_embeddings)
    print(f"✓ Stored {len(chunks_with_embeddings)} chunks")

    # Step 4: Test retrieval by ID
    print("\n[4/5] Testing retrieval by ID...")
    test_chunk = chunks_with_embeddings[0]
    retrieved = vector_store.get_by_id(test_chunk.id)
    if retrieved:
        print(f"✓ Successfully retrieved chunk by ID")
        print(f"  Chunk text preview: {retrieved['text'][:100]}...")
    else:
        print("✗ Failed to retrieve chunk by ID")

    # Step 5: Test semantic search
    print("\n[5/5] Testing semantic search...")
    if query:
        search_query = query
    else:
        search_query = chunks[0].text[:200]
        print(f"  Using first chunk as query (no query provided)")

    print(f"  Query: '{search_query[:100]}...'")

    results = vector_store.search_by_text(
        query_text=search_query,
        embedder=embedder,
        n_results=5,
    )

    print(f"\n  Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        similarity = 1 - result["distance"]
        print(f"\n  Result {i} (similarity: {similarity:.3f}):")
        print(f"    Page: {result['metadata']['page_number']}")
        print(f"    Text: {result['text'][:150]}...")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Document: {document.title}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Embeddings generated: {len(chunks_with_embeddings)}")
    print(f"Chunks stored: {vector_store.count()}")
    print(f"Embedding dimension: {embedder.embedding_dimension}")
    print(f"Search results: {len(results)}")
    print("\n✓ ALL TESTS PASSED")
    print("=" * 80)


def test_storage_only(clear: bool = False) -> None:
    """Test vector storage operations without new documents."""
    print("\n" + "=" * 80)
    print("VECTOR STORAGE TEST (Existing Data)")
    print("=" * 80)

    vector_store = VectorStore(collection_name="test_collection")
    embedder = Embedder()

    info = vector_store.get_collection_info()
    print(f"\nCollection: {info['name']}")
    print(f"Total chunks: {info['count']}")
    print(f"Persist directory: {info['persist_directory']}")

    if info["count"] == 0:
        print("\n✗ No data in collection. Run with a PDF first.")
        return

    if clear:
        vector_store.clear_collection()
        print("\n✓ Collection cleared")
        return

    # Test search
    query = input("\nEnter search query (or press Enter to skip): ").strip()
    if query:
        results = vector_store.search_by_text(
            query_text=query,
            embedder=embedder,
            n_results=5,
        )

        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            similarity = 1 - result["distance"]
            print(f"\nResult {i} (similarity: {similarity:.3f}):")
            print(f"  Document: {result['metadata']['document_id']}")
            print(f"  Page: {result['metadata']['page_number']}")
            print(f"  Text: {result['text'][:200]}...")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test vector storage and retrieval functionality"
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        nargs="?",
        help="Path to PDF file (optional if testing existing data)",
    )
    parser.add_argument(
        "-q", "--query", type=str, help="Search query to test retrieval"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing vector store"
    )
    parser.add_argument(
        "--test-storage",
        action="store_true",
        help="Test storage operations with existing data",
    )

    args = parser.parse_args()

    if args.test_storage:
        test_storage_only(clear=args.clear)
    elif args.pdf_path:
        if not args.pdf_path.exists():
            print(f"Error: PDF file not found: {args.pdf_path}")
            sys.exit(1)
        test_full_pipeline(args.pdf_path, query=args.query, auto_clear=args.clear)
    else:
        print("Error: Please provide a PDF path or use --test-storage")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
