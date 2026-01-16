"""Unit tests for Embedder."""

import numpy as np
import pytest

from docprocessor.core.embedder import Embedder


@pytest.fixture
def embedder():
    """Create an Embedder instance."""
    return Embedder()


class TestEmbedder:
    """Test Embedder functionality."""

    def test_initialization(self, embedder):
        """Test embedder initialization."""
        assert embedder.model is not None
        assert embedder.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert embedder.embedding_dimension == 384

    def test_embed_single_text(self, embedder):
        """Test embedding a single text."""
        text = "This is a sample legal document about contracts."
        embedding = embedder.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        assert embedding.dtype == np.float32

        # Check that embedding has reasonable values
        assert not np.isnan(embedding).any()
        assert not np.isinf(embedding).any()

    def test_embed_batch(self, embedder):
        """Test embedding multiple texts in batch."""
        texts = [
            "Legal research methodology",
            "Contract law principles",
            "Constitutional interpretation",
            "Statutory analysis",
        ]

        embeddings = embedder.embed_batch(texts, batch_size=2, show_progress=False)

        # embed_batch returns numpy array, not list
        assert isinstance(embeddings, (list, np.ndarray))
        assert len(embeddings) == len(texts)

        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (384,)
            assert not np.isnan(embedding).any()

    def test_semantic_similarity(self, embedder):
        """Test that similar texts have similar embeddings."""
        text1 = "Contract law governs agreements between parties."
        text2 = "Contracts are legal agreements that bind parties."
        text3 = "Quantum mechanics studies subatomic particles."  # Unrelated

        emb1 = embedder.embed_text(text1)
        emb2 = embedder.embed_text(text2)
        emb3 = embedder.embed_text(text3)

        # Cosine similarity
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        sim_12 = cosine_similarity(emb1, emb2)  # Similar texts
        sim_13 = cosine_similarity(emb1, emb3)  # Dissimilar texts

        # Similar texts should have higher similarity than dissimilar ones
        assert sim_12 > sim_13
        assert sim_12 > 0.5  # Should be fairly similar

    def test_empty_text_handling(self, embedder):
        """Test handling of empty text."""
        # Embedder should handle empty text gracefully
        embedding = embedder.embed_text("")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)

    def test_batch_consistency(self, embedder):
        """Test that batch and single embeddings are consistent."""
        text = "Sample legal text for consistency testing"

        single_embedding = embedder.embed_text(text)
        batch_embeddings = embedder.embed_batch([text], show_progress=False)

        # Should produce identical or very similar results
        np.testing.assert_allclose(single_embedding, batch_embeddings[0], rtol=1e-5)

    def test_embedding_normalization(self, embedder):
        """Test that embeddings are normalized."""
        text = "This text will be embedded and checked for normalization"
        embedding = embedder.embed_text(text)

        # Check L2 norm is close to 1 (normalized)
        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, rtol=0.1)

    def test_large_batch(self, embedder):
        """Test embedding a large batch of texts."""
        texts = [f"Legal document number {i} about various topics" for i in range(100)]

        embeddings = embedder.embed_batch(texts, batch_size=16, show_progress=False)

        assert len(embeddings) == 100
        assert all(isinstance(e, np.ndarray) for e in embeddings)
        assert all(e.shape == (384,) for e in embeddings)

    def test_special_characters(self, embedder):
        """Test handling of special characters."""
        texts = [
            "Article §123 of the Code",
            "The plaintiff's testimony at 10:30 AM",
            "Cost: $1,000,000 (one million dollars)",
            "See Footnote† for details",
        ]

        embeddings = embedder.embed_batch(texts, show_progress=False)

        assert len(embeddings) == len(texts)
        for embedding in embeddings:
            assert not np.isnan(embedding).any()
            assert not np.isinf(embedding).any()

    def test_multilingual_text(self, embedder):
        """Test handling of multilingual text."""
        texts = [
            "This is English text",
            "Ceci est du texte français",
            "هذا نص عربي",
        ]

        # Should handle different languages (MiniLM supports 100+ languages)
        embeddings = embedder.embed_batch(texts, show_progress=False)

        assert len(embeddings) == len(texts)
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (384,)


class TestEmbeddingQuality:
    """Test embedding quality and semantic properties."""

    def test_legal_domain_concepts(self, embedder):
        """Test embeddings capture legal domain relationships."""
        # Related legal concepts should be closer than unrelated ones
        texts = {
            "contract": "A contract is a legally binding agreement",
            "agreement": "An agreement between two parties",
            "tort": "A tort is a civil wrong",
            "recipe": "A recipe for chocolate cake",
        }

        embeddings = {k: embedder.embed_text(v) for k, v in texts.items()}

        def similarity(k1, k2):
            return np.dot(embeddings[k1], embeddings[k2]) / (
                np.linalg.norm(embeddings[k1]) * np.linalg.norm(embeddings[k2])
            )

        # Contract and agreement should be more similar than contract and recipe
        assert similarity("contract", "agreement") > similarity("contract", "recipe")
        assert similarity("contract", "tort") > similarity("contract", "recipe")
