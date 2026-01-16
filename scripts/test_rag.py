#!/usr/bin/env python3
"""Test script for RAG (Retrieval-Augmented Generation) pipeline."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.rag_pipeline import RAGPipeline
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.utils.logger import setup_logger

logger = setup_logger("test_rag", level=settings.log_level_int)


def test_rag_pipeline(
    pdf_path: Path = None,
    query: str = None,
    stream: bool = False,
    use_existing: bool = False,
) -> None:
    """
    Test the complete RAG pipeline.

    Args:
        pdf_path: Path to PDF file (if processing new document)
        query: Question to ask
        stream: Use streaming generation
        use_existing: Use existing vector store data
    """
    print("\n" + "=" * 80)
    print("RAG PIPELINE TEST")
    print("=" * 80)

    # Initialize components
    print("\n[1/6] Initializing components...")
    vector_store = VectorStore(collection_name="test_collection")
    embedder = Embedder()

    print(f"  Vector store: {vector_store.count()} chunks")

    # Check if Ollama is available
    print("\n[2/6] Checking Ollama availability...")
    try:
        ollama_client = OllamaClient()
        print(f"  ✓ Ollama is running")
        print(f"  Model: {ollama_client.model}")

        models = ollama_client.list_models()
        print(f"  Available models: {', '.join(models) if models else 'none'}")

        if not ollama_client.check_model_availability():
            print(f"\n  ⚠ Model '{ollama_client.model}' not found!")
            print(f"  Please run: ollama pull {ollama_client.model}")
            return
    except Exception as e:
        print(f"\n  ✗ Ollama error: {e}")
        print("\n  Please ensure Ollama is running:")
        print("    1. Install Ollama: https://ollama.ai")
        print("    2. Start Ollama: ollama serve")
        print(f"    3. Pull model: ollama pull {settings.ollama_model}")
        return

    # Process PDF if provided
    if pdf_path and not use_existing:
        print(f"\n[3/6] Processing PDF: {pdf_path.name}")
        processor = DocumentProcessor()
        document, chunks = processor.process_document(pdf_path)
        print(f"  ✓ Extracted {len(chunks)} chunks")

        print("\n[4/6] Generating embeddings and storing...")
        chunks_with_embeddings = embedder.embed_chunks(chunks, show_progress=False)
        vector_store.add_chunks(chunks_with_embeddings)
        print(f"  ✓ Stored {len(chunks)} chunks. Total: {vector_store.count()}")
    elif use_existing:
        print(f"\n[3/6] Using existing vector store data")
        print(f"[4/6] Current collection: {vector_store.count()} chunks")
    else:
        print("\n[3/6] No new PDF to process")
        print(f"[4/6] Current collection: {vector_store.count()} chunks")

    if vector_store.count() == 0:
        print("\n✗ No documents in vector store!")
        print("  Run with a PDF first: python scripts/test_rag.py <pdf_file>")
        return

    # Initialize RAG pipeline
    print("\n[5/6] Initializing RAG pipeline...")
    rag = RAGPipeline(
        vector_store=vector_store,
        embedder=embedder,
        ollama_client=ollama_client,
    )
    print("  ✓ RAG pipeline ready")

    # Query
    if not query:
        query = "What are the main ethical concerns regarding AI in legal practice?"
        print(f"\n[6/6] Using default query: '{query}'")
    else:
        print(f"\n[6/6] Processing query: '{query}'")

    print("\n" + "-" * 80)
    print("QUERY RESULTS")
    print("-" * 80)

    if stream:
        print("\nAnswer (streaming):")
        print("-" * 40)
        answer_stream, sources = rag.query_streaming(query)

        full_answer = ""
        for chunk in answer_stream:
            print(chunk, end="", flush=True)
            full_answer += chunk
        print("\n" + "-" * 40)

        print(f"\nSources ({len(sources)} chunks retrieved):")
        for i, source in enumerate(sources, 1):
            print(f"\n{i}. Document: {source['document_id'][:8]}..., "
                  f"Page: {source['page']}, Similarity: {source['similarity']:.3f}")
            print(f"   Preview: {source['text_preview']}")
    else:
        result = rag.query(query, include_sources=True)

        print("\nAnswer:")
        print("-" * 40)
        print(result["answer"])
        print("-" * 40)

        if result.get("sources"):
            print(f"\nSources ({len(result['sources'])} chunks retrieved):")
            for i, source in enumerate(result["sources"], 1):
                print(f"\n{i}. Document: {source['document_id'][:8]}..., "
                      f"Page: {source['page']}, Similarity: {source['similarity']:.3f}")
                print(f"   Preview: {source['text_preview']}")

    print("\n" + "=" * 80)
    print("✓ RAG TEST COMPLETED")
    print("=" * 80)


def interactive_mode(vector_store: VectorStore, embedder: Embedder, ollama_client: OllamaClient):
    """Interactive question-answering mode."""
    print("\n" + "=" * 80)
    print("INTERACTIVE RAG MODE")
    print("=" * 80)
    print("\nType your questions (or 'quit' to exit)")
    print(f"Documents in collection: {vector_store.count()} chunks")
    print("-" * 80)

    rag = RAGPipeline(
        vector_store=vector_store,
        embedder=embedder,
        ollama_client=ollama_client,
    )

    while True:
        try:
            query = input("\nYour question: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break

            if not query:
                continue

            print("\nThinking...")
            result = rag.query(query, include_sources=True)

            print("\nAnswer:")
            print("-" * 40)
            print(result["answer"])
            print("-" * 40)

            if result.get("sources"):
                print(f"\nBased on {len(result['sources'])} sources")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test RAG pipeline with document question answering"
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        nargs="?",
        help="Path to PDF file (optional if using existing data)",
    )
    parser.add_argument("-q", "--query", type=str, help="Question to ask")
    parser.add_argument(
        "--stream", action="store_true", help="Use streaming generation"
    )
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Use existing vector store data (don't process PDF)",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive Q&A mode"
    )

    args = parser.parse_args()

    if args.interactive:
        vector_store = VectorStore(collection_name="test_collection")
        embedder = Embedder()
        try:
            ollama_client = OllamaClient()
            interactive_mode(vector_store, embedder, ollama_client)
        except Exception as e:
            print(f"Error: {e}")
            print("\nMake sure Ollama is running: ollama serve")
            sys.exit(1)
    else:
        if args.pdf_path and not args.pdf_path.exists():
            print(f"Error: PDF file not found: {args.pdf_path}")
            sys.exit(1)

        test_rag_pipeline(
            pdf_path=args.pdf_path,
            query=args.query,
            stream=args.stream,
            use_existing=args.use_existing,
        )


if __name__ == "__main__":
    main()
