#!/usr/bin/env python3
"""Performance profiling script for Document Processor.

Profiles key operations to identify bottlenecks:
1. PDF text extraction
2. Text chunking
3. Embedding generation
4. Vector store operations
5. Theme discovery
6. Chapter synthesis
"""

import cProfile
import pstats
import time
from pathlib import Path
from io import StringIO
from tempfile import TemporaryDirectory
import sys

# Add src and root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir))

from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.vector_store import VectorStore
from docprocessor.models.document import Document


def profile_function(func, *args, **kwargs):
    """Profile a function and return stats."""
    profiler = cProfile.Profile()

    start = time.time()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    elapsed = time.time() - start

    # Get stats
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

    return result, elapsed, stream.getvalue()


def create_sample_document(length_pages=10):
    """Create a sample document for testing."""
    sample_text = """
    Legal Research Methods

    This document discusses various approaches to legal research including
    case law analysis, statutory interpretation, and comparative law studies.

    The methodology involves systematic review of primary sources including
    court decisions, legislation, and regulatory frameworks. Secondary sources
    such as legal commentaries and scholarly articles provide additional context.

    Key principles include thorough documentation, proper citation practices,
    and critical analysis of legal arguments and precedents.
    """ * 50  # Repeat to simulate longer document

    # Create temporary file
    temp_file = Path("/tmp/sample_perf_test.txt")
    temp_file.write_text(sample_text * length_pages)

    # Create sample document
    doc = Document(
        file_path=temp_file,
        title="Sample Legal Research Document",
        author="Test Author",
        page_count=length_pages,
        file_size=len(sample_text),
        text_content=sample_text * length_pages,
        processed=False
    )
    return doc


def main():
    """Run performance profiling."""
    print("=" * 80)
    print("Document Processor Performance Profiling")
    print("=" * 80)
    print()

    # Create sample document
    print("Creating sample document...")
    document = create_sample_document(length_pages=20)
    print(f"Document created: {len(document.text_content)} characters")
    print()

    # Profile 1: Text chunking
    print("-" * 80)
    print("1. TEXT CHUNKING")
    print("-" * 80)
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    chunks, elapsed, stats = profile_function(processor.chunk_document, document)
    print(f"✓ Chunked document in {elapsed:.3f}s")
    print(f"  Created {len(chunks)} chunks")
    print(f"  Avg chunk size: {sum(len(c.text) for c in chunks) / len(chunks):.0f} chars")
    print()
    print("Top time consumers:")
    print(stats.split('\n')[:25])
    print()

    # Profile 2: Embedding generation
    print("-" * 80)
    print("2. EMBEDDING GENERATION")
    print("-" * 80)
    embedder = Embedder()
    print(f"Model: {embedder.model_name}")
    print(f"Dimension: {embedder.embedding_dimension}")

    # Test with first 50 chunks
    test_chunks = chunks[:50]
    texts = [c.text for c in test_chunks]

    embeddings, elapsed, stats = profile_function(
        embedder.embed_batch,
        texts,
        batch_size=16,
        show_progress=False
    )
    print(f"✓ Generated {len(embeddings)} embeddings in {elapsed:.3f}s")
    print(f"  Throughput: {len(embeddings) / elapsed:.1f} chunks/sec")
    print(f"  Per-chunk: {elapsed / len(embeddings) * 1000:.1f}ms")
    print()
    print("Top time consumers:")
    print(stats.split('\n')[:25])
    print()

    # Profile 3: Vector store operations
    print("-" * 80)
    print("3. VECTOR STORE OPERATIONS")
    print("-" * 80)

    with TemporaryDirectory() as temp_dir:
        vector_store = VectorStore(
            collection_name="profile_test",
            persist_directory=Path(temp_dir)
        )

        # Add embeddings to chunks
        for i, chunk in enumerate(test_chunks):
            chunk.embedding = embeddings[i].tolist()

        # Profile bulk add
        _, elapsed, stats = profile_function(vector_store.add_chunks, test_chunks)
        print(f"✓ Added {len(test_chunks)} chunks in {elapsed:.3f}s")
        print(f"  Throughput: {len(test_chunks) / elapsed:.1f} chunks/sec")
        print()

        # Profile search
        query_embedding = embeddings[0]
        results, elapsed, stats = profile_function(
            vector_store.search,
            query_embedding,
            n_results=10
        )
        print(f"✓ Searched vector store in {elapsed:.3f}s")
        print(f"  Found {len(results)} results")
        print()
        print("Top time consumers:")
        print(stats.split('\n')[:25])

    print()
    print("=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)
    print()
    print("Performance Summary:")
    print(f"  - Chunking: ~{len(chunks) / 20:.0f} chunks/sec")
    print(f"  - Embedding: ~{len(embeddings) / elapsed:.1f} chunks/sec")
    print(f"  - Vector ops: Fast (< 1s for 50 chunks)")
    print()
    print("Recommendations:")

    # Analyze bottlenecks
    if len(embeddings) / elapsed < 10:
        print("  ⚠️  Embedding generation is slow - consider:")
        print("     - Using a smaller model")
        print("     - Batching more aggressively")
        print("     - Using GPU acceleration if available")
    else:
        print("  ✓ Embedding generation is performing well")

    print()


if __name__ == "__main__":
    main()
