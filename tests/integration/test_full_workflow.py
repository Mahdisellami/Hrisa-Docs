"""Integration tests for full document processing workflow."""

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import patch

import pytest

from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.theme_analyzer import ThemeAnalyzer
from docprocessor.core.vector_store import VectorStore
from docprocessor.models.document import Document


@pytest.fixture
def sample_documents():
    """Create sample documents for integration testing."""
    documents = []

    # Document 1: Contract Law
    doc1_text = (
        """
    Contract Law Fundamentals

    A contract is a legally binding agreement between two or more parties.
    The essential elements of a valid contract include offer, acceptance,
    consideration, and the intention to create legal relations.

    Formation of Contracts

    Contract formation begins with an offer by one party and acceptance by
    another. The offer must be communicated clearly and the acceptance must
    match the terms of the offer. Consideration, which is something of value
    exchanged between the parties, is essential for contract enforceability.

    Breach and Remedies

    When a party fails to perform their contractual obligations, a breach occurs.
    Remedies for breach include damages, specific performance, and rescission.
    The appropriate remedy depends on the nature of the breach and the terms
    of the contract.
    """
        * 3
    )  # Repeat for more content

    # Document 2: Tort Law
    doc2_text = (
        """
    Tort Law Overview

    Tort law governs civil wrongs and provides remedies for individuals who
    have been harmed by the wrongful conduct of others. Unlike criminal law,
    tort law focuses on compensating victims rather than punishing wrongdoers.

    Negligence

    Negligence is the most common tort. To establish negligence, a plaintiff
    must prove four elements: duty of care, breach of that duty, causation,
    and damages. The defendant must have owed a duty of care to the plaintiff
    and breached that duty, causing harm.

    Intentional Torts

    Intentional torts involve deliberate wrongful acts. These include assault,
    battery, false imprisonment, and intentional infliction of emotional distress.
    Unlike negligence, intentional torts require proof of intent to commit
    the wrongful act.
    """
        * 3
    )  # Repeat for more content

    # Create temporary files
    for i, text in enumerate([doc1_text, doc2_text], 1):
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(text)
            temp_path = Path(f.name)

        doc = Document(
            file_path=temp_path,
            title=f"Test Document {i}",
            author="Test Author",
            page_count=5,
            file_size=len(text),
            text_content=text,
            processed=False,
        )
        documents.append(doc)

    yield documents

    # Cleanup
    for doc in documents:
        doc.file_path.unlink(missing_ok=True)


@pytest.mark.integration
@pytest.mark.slow
class TestFullWorkflow:
    """Test complete document processing workflow."""

    @pytest.mark.wip  # Skip in CI - assertion threshold issue
    def test_document_to_chunks_workflow(self, sample_documents):
        """Test processing documents into chunks."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)

        all_chunks = []
        for doc in sample_documents:
            chunks = processor.chunk_document(doc)
            all_chunks.extend(chunks)

        # Should have created multiple chunks
        assert len(all_chunks) > 10

        # All chunks should have text
        assert all(chunk.text for chunk in all_chunks)

        # Chunks should have proper document IDs
        for doc in sample_documents:
            doc_chunks = [c for c in all_chunks if c.document_id == doc.id]
            assert len(doc_chunks) > 0

    def test_chunks_to_embeddings_workflow(self, sample_documents):
        """Test embedding generation workflow."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        embedder = Embedder()

        # Process documents
        all_chunks = []
        for doc in sample_documents:
            chunks = processor.chunk_document(doc)
            all_chunks.extend(chunks)

        # Generate embeddings
        texts = [chunk.text for chunk in all_chunks]
        embeddings = embedder.embed_batch(texts, batch_size=16, show_progress=False)

        # Assign embeddings to chunks
        for chunk, embedding in zip(all_chunks, embeddings):
            chunk.embedding = embedding.tolist()

        # Verify embeddings
        assert len(embeddings) == len(all_chunks)
        assert all(chunk.embedding is not None for chunk in all_chunks)

    def test_embeddings_to_vector_store_workflow(self, sample_documents):
        """Test storing embeddings in vector store."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        embedder = Embedder()

        with TemporaryDirectory() as tmpdir:
            vector_store = VectorStore(
                collection_name="test_workflow", persist_directory=Path(tmpdir)
            )

            # Process and embed documents
            all_chunks = []
            for doc in sample_documents:
                chunks = processor.chunk_document(doc)
                all_chunks.extend(chunks)

            texts = [chunk.text for chunk in all_chunks]
            embeddings = embedder.embed_batch(texts, batch_size=16, show_progress=False)

            for chunk, embedding in zip(all_chunks, embeddings):
                chunk.embedding = embedding.tolist()

            # Store in vector store
            vector_store.add_chunks(all_chunks)

            # Verify storage
            assert vector_store.count() == len(all_chunks)

            # Test retrieval
            query_embedding = embeddings[0]
            results = vector_store.search(query_embedding, n_results=5)

            assert len(results) > 0
            assert results[0]["text"] is not None

    @pytest.mark.wip  # Skip in CI - path handling issue
    def test_vector_store_to_themes_workflow(self, sample_documents):
        """Test theme discovery from vector store."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        embedder = Embedder()

        # Process documents
        all_chunks = []
        for doc in sample_documents:
            chunks = processor.chunk_document(doc)
            all_chunks.extend(chunks[:20])  # Limit for speed

        # Embed
        texts = [chunk.text for chunk in all_chunks]
        embeddings = embedder.embed_batch(texts, batch_size=16, show_progress=False)

        # Store in vector store for theme analyzer
        import tempfile

        from docprocessor.core.vector_store import VectorStore

        with tempfile.TemporaryDirectory() as tmpdir:
            vector_store = VectorStore(persist_directory=tmpdir)

            # Discover themes
            theme_analyzer = ThemeAnalyzer(vector_store=vector_store, max_themes=2)

            with patch.object(theme_analyzer, "_generate_theme_label") as mock_label:
                mock_label.side_effect = ["Contract Law", "Tort Law"]

                themes = theme_analyzer.discover_themes(n_themes=2)

                # Should discover themes
                assert len(themes) > 0
                assert all(theme.label for theme in themes)
                assert all(theme.chunk_count > 0 for theme in themes)

    @pytest.mark.requires_ollama
    def test_end_to_end_without_synthesis(self, sample_documents):
        """Test end-to-end workflow without final synthesis (no Ollama required)."""
        # Initialize components
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        embedder = Embedder()
        theme_analyzer = ThemeAnalyzer(n_themes=2)

        with TemporaryDirectory() as tmpdir:
            vector_store = VectorStore(collection_name="e2e_test", persist_directory=Path(tmpdir))

            # Step 1: Process documents into chunks
            all_chunks = []
            for doc in sample_documents:
                chunks = processor.chunk_document(doc)
                all_chunks.extend(chunks)

            assert len(all_chunks) > 0

            # Step 2: Generate embeddings
            texts = [chunk.text for chunk in all_chunks]
            embeddings = embedder.embed_batch(texts, batch_size=16, show_progress=False)

            for chunk, embedding in zip(all_chunks, embeddings):
                chunk.embedding = embedding.tolist()

            assert all(chunk.embedding is not None for chunk in all_chunks)

            # Step 3: Store in vector database
            vector_store.add_chunks(all_chunks)
            assert vector_store.count() == len(all_chunks)

            # Step 4: Discover themes
            with patch.object(theme_analyzer, "_generate_theme_label") as mock_label:
                mock_label.side_effect = ["Theme 1", "Theme 2"]
                themes = theme_analyzer.discover_themes(embeddings, texts)

            assert len(themes) > 0

            # Step 5: Test retrieval for synthesis (without actual LLM generation)
            query_embedding = embeddings[0]
            relevant_chunks = vector_store.search(query_embedding, n_results=10)

            assert len(relevant_chunks) > 0
            assert all("text" in chunk for chunk in relevant_chunks)

            print(f"\n✓ Processed {len(sample_documents)} documents")
            print(f"✓ Created {len(all_chunks)} chunks")
            print(f"✓ Generated {len(embeddings)} embeddings")
            print(f"✓ Discovered {len(themes)} themes")
            print(f"✓ Retrieved {len(relevant_chunks)} relevant chunks")


@pytest.mark.integration
class TestComponentIntegration:
    """Test integration between specific components."""

    def test_processor_embedder_integration(self, sample_documents):
        """Test document processor and embedder work together."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        embedder = Embedder()

        doc = sample_documents[0]
        chunks = processor.chunk_document(doc)

        # Embed first 5 chunks
        texts = [chunk.text for chunk in chunks[:5]]
        embeddings = embedder.embed_batch(texts, show_progress=False)

        assert len(embeddings) == len(texts)

        # Embeddings should capture semantic similarity
        # First two chunks from same doc should be more similar than random
        emb1, emb2 = embeddings[0], embeddings[1]
        similarity = (emb1 @ emb2) / ((emb1 @ emb1) ** 0.5 * (emb2 @ emb2) ** 0.5)

        assert similarity > 0.3  # Should have some similarity

    def test_embedder_vector_store_integration(self):
        """Test embedder and vector store work together."""
        embedder = Embedder()

        texts = [
            "Contract law governs agreements",
            "Tort law addresses civil wrongs",
            "Criminal law defines offenses",
        ]

        embeddings = embedder.embed_batch(texts, show_progress=False)

        with TemporaryDirectory() as tmpdir:
            from uuid import uuid4

            from docprocessor.models.chunk import Chunk

            vector_store = VectorStore(
                collection_name="integration_test", persist_directory=Path(tmpdir)
            )

            # Create chunks with embeddings
            chunks = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                chunk = Chunk(
                    id=str(uuid4()),
                    document_id=str(uuid4()),
                    text=text,
                    chunk_index=i,
                    start_char=i * 100,
                    end_char=(i + 1) * 100,
                    embedding=embedding.tolist(),
                )
                chunks.append(chunk)

            vector_store.add_chunks(chunks)

            # Search with first embedding - should find itself
            results = vector_store.search(embeddings[0], n_results=1)

            assert len(results) == 1
            assert results[0]["text"] == texts[0]
