"""Unit tests for VectorStore."""

from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import numpy as np
import pytest

from docprocessor.core.vector_store import VectorStore
from docprocessor.models.chunk import Chunk


@pytest.fixture
def temp_dir():
    """Create a temporary directory for vector store."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def vector_store(temp_dir):
    """Create a VectorStore instance."""
    return VectorStore(collection_name="test_collection", persist_directory=temp_dir)


@pytest.fixture
def sample_chunks():
    """Create sample chunks with embeddings."""
    texts = [
        "Contract law governs agreements between parties",
        "Tort law deals with civil wrongs and damages",
        "Criminal law defines offenses against society",
        "Constitutional law establishes government structure",
        "Property law regulates ownership of assets",
    ]

    chunks = []
    for i, text in enumerate(texts):
        # Create random embedding (in real use, would be from embedder)
        embedding = np.random.randn(384).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize

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

    return chunks


class TestVectorStore:
    """Test VectorStore functionality."""

    def test_initialization(self, vector_store):
        """Test vector store initialization."""
        assert vector_store.collection is not None
        assert vector_store.collection_name == "test_collection"

        # Should start empty
        count = vector_store.count()
        assert count == 0

    def test_add_single_chunk(self, vector_store, sample_chunks):
        """Test adding a single chunk."""
        chunk = sample_chunks[0]
        vector_store.add_chunks([chunk])

        assert vector_store.count() == 1

    def test_add_multiple_chunks(self, vector_store, sample_chunks):
        """Test adding multiple chunks."""
        vector_store.add_chunks(sample_chunks)

        assert vector_store.count() == len(sample_chunks)

    def test_search(self, vector_store, sample_chunks):
        """Test vector similarity search."""
        # Add chunks
        vector_store.add_chunks(sample_chunks)

        # Search with first chunk's embedding
        query_embedding = np.array(sample_chunks[0].embedding)
        results = vector_store.search(query_embedding, n_results=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        assert len(results) > 0

        # Results should have required fields
        for result in results:
            assert "id" in result or result.get("chunk") is not None
            assert "text" in result or (result.get("chunk") and "text" in result["chunk"])
            # ChromaDB returns distance or doesn't return score

    def test_search_returns_most_similar(self, vector_store, sample_chunks):
        """Test that search returns most similar chunks."""
        vector_store.add_chunks(sample_chunks)

        # Search with exact chunk embedding - should return itself first
        query_embedding = np.array(sample_chunks[0].embedding)
        results = vector_store.search(query_embedding, n_results=1)

        assert len(results) == 1
        # The most similar should be the query itself (check text or chunk)
        result_text = results[0].get("text") or results[0].get("chunk", {}).get("text")
        assert result_text == sample_chunks[0].text

    def test_get_all_chunks(self, vector_store, sample_chunks):
        """Test retrieving all chunks."""
        vector_store.add_chunks(sample_chunks)

        all_chunks = vector_store.get_all_chunks()

        assert len(all_chunks) == len(sample_chunks)
        # Each chunk should have text
        for chunk in all_chunks:
            assert "text" in chunk or (chunk.get("chunk") and "text" in chunk["chunk"])

    def test_delete_by_document(self, vector_store, sample_chunks):
        """Test deleting chunks by document ID."""
        # Assign same document ID to first 2 chunks
        doc_id = str(uuid4())
        for chunk in sample_chunks[:2]:
            chunk.document_id = doc_id

        vector_store.add_chunks(sample_chunks)
        assert vector_store.count() == 5

        # Delete chunks from specific document
        vector_store.delete_by_document(doc_id)

        # Should have deleted 2 chunks
        assert vector_store.count() == 3

    def test_clear_collection(self, vector_store, sample_chunks):
        """Test clearing entire collection."""
        vector_store.add_chunks(sample_chunks)
        assert vector_store.count() > 0

        vector_store.clear_collection()

        # Collection should be empty but still exist
        assert vector_store.count() == 0

    def test_persistence(self, temp_dir, sample_chunks):
        """Test that data persists across instances."""
        # Create store and add data
        store1 = VectorStore(collection_name="persist_test", persist_directory=temp_dir)
        store1.add_chunks(sample_chunks)
        count1 = store1.count()

        # Create new instance with same directory
        store2 = VectorStore(collection_name="persist_test", persist_directory=temp_dir)
        count2 = store2.count()

        # Data should persist
        assert count2 == count1

    def test_empty_search(self, vector_store):
        """Test search on empty collection."""
        query_embedding = np.random.randn(384).astype(np.float32)
        results = vector_store.search(query_embedding, n_results=5)

        assert isinstance(results, list)
        assert len(results) == 0

    def test_add_without_embedding(self, vector_store):
        """Test that adding chunk without embedding raises error."""
        chunk = Chunk(
            id=str(uuid4()),
            document_id=str(uuid4()),
            text="Test chunk without embedding",
            chunk_index=0,
            start_char=0,
            end_char=100,
            embedding=None,  # No embedding
        )

        with pytest.raises((ValueError, AttributeError, TypeError)):
            vector_store.add_chunks([chunk])

    def test_metadata_preservation(self, vector_store, sample_chunks):
        """Test that metadata is preserved in storage and retrieval."""
        vector_store.add_chunks(sample_chunks)

        # Retrieve and check metadata
        all_chunks = vector_store.get_all_chunks()

        # Basic checks - metadata structure may vary
        assert len(all_chunks) == len(sample_chunks)
        for chunk_data in all_chunks:
            # Check that we have essential data
            assert "text" in chunk_data or (
                chunk_data.get("chunk") and "text" in chunk_data["chunk"]
            )


class TestVectorStoreEdgeCases:
    """Test edge cases and error handling."""

    def test_large_batch_add(self, vector_store):
        """Test adding a large batch of chunks."""
        # Create 1000 chunks
        chunks = []
        for i in range(1000):
            embedding = np.random.randn(384).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)

            chunk = Chunk(
                id=str(uuid4()),
                document_id=str(uuid4()),
                text=f"Chunk {i}",
                chunk_index=i,
                start_char=i * 100,
                end_char=(i + 1) * 100,
                embedding=embedding.tolist(),
            )
            chunks.append(chunk)

        vector_store.add_chunks(chunks)

        assert vector_store.count() == 1000

    def test_duplicate_chunk_ids(self, vector_store, sample_chunks):
        """Test handling of duplicate chunk IDs."""
        # Add same chunks twice
        vector_store.add_chunks(sample_chunks)
        initial_count = vector_store.count()

        # Adding again might update or skip depending on implementation
        vector_store.add_chunks(sample_chunks)
        final_count = vector_store.count()

        # Should not double the count (either update or skip)
        assert final_count == initial_count
