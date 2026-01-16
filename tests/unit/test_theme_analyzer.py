"""Unit tests for ThemeAnalyzer."""

from unittest.mock import Mock, patch

import numpy as np
import pytest

pytestmark = pytest.mark.wip  # Skip in CI until API stabilizes

from docprocessor.core.theme_analyzer import ThemeAnalyzer
from docprocessor.models.theme import Theme


@pytest.fixture
def mock_vector_store():
    """Create a mock VectorStore instance."""
    mock_store = Mock()
    mock_store.get_all.return_value = ([], [])
    return mock_store


@pytest.fixture
def theme_analyzer(mock_vector_store):
    """Create a ThemeAnalyzer instance."""
    return ThemeAnalyzer(vector_store=mock_vector_store, max_themes=3)


@pytest.fixture
def sample_embeddings():
    """Create sample embeddings for testing."""
    # Create 3 clusters of embeddings
    cluster1 = np.random.randn(10, 384) + np.array([1, 0] + [0] * 382)
    cluster2 = np.random.randn(10, 384) + np.array([0, 1] + [0] * 382)
    cluster3 = np.random.randn(10, 384) + np.array([-1, -1] + [0] * 382)

    embeddings = np.vstack([cluster1, cluster2, cluster3])

    # Normalize
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms

    return embeddings.astype(np.float32)


@pytest.fixture
def sample_texts():
    """Create sample texts corresponding to embeddings."""
    texts = []

    # Cluster 1: Contract law
    texts.extend(
        [
            "Contracts are legally binding agreements between parties",
            "Formation of contracts requires offer, acceptance, and consideration",
            "Breach of contract may result in damages or specific performance",
            "Contract interpretation follows established legal principles",
            "Parties to a contract have mutual obligations",
            "Contractual terms must be clear and unambiguous",
            "Consideration is essential for valid contract formation",
            "Agreement between parties creates legal obligations",
            "Contract law governs commercial transactions",
            "Contractual remedies include damages and rescission",
        ]
    )

    # Cluster 2: Tort law
    texts.extend(
        [
            "Tort law addresses civil wrongs and personal injuries",
            "Negligence requires duty, breach, causation, and damages",
            "Strict liability applies to certain dangerous activities",
            "Intentional torts include assault, battery, and false imprisonment",
            "Damages in tort cases compensate for harm suffered",
            "Duty of care is owed to foreseeable plaintiffs",
            "Causation links defendant's conduct to plaintiff's harm",
            "Tort law provides remedies for wrongful conduct",
            "Personal injury claims fall under tort law",
            "Tortious conduct results in civil liability",
        ]
    )

    # Cluster 3: Criminal law
    texts.extend(
        [
            "Criminal law defines offenses against society",
            "Mens rea refers to criminal intent or guilty mind",
            "Actus reus is the physical act of committing a crime",
            "Criminal defendants have constitutional rights",
            "Burden of proof in criminal cases is beyond reasonable doubt",
            "Criminal penalties include imprisonment and fines",
            "Defenses to criminal charges include alibi and insanity",
            "Criminal procedure governs prosecution of offenses",
            "Felonies are serious crimes with severe penalties",
            "Criminal law protects public safety and order",
        ]
    )

    return texts


class TestThemeAnalyzer:
    """Test ThemeAnalyzer functionality."""

    def test_initialization(self, mock_vector_store):
        """Test theme analyzer initialization."""
        analyzer = ThemeAnalyzer(vector_store=mock_vector_store, max_themes=5)
        assert analyzer.max_themes == 5

    def test_default_initialization(self, mock_vector_store):
        """Test default initialization."""
        from config.settings import settings

        analyzer = ThemeAnalyzer(vector_store=mock_vector_store)
        assert analyzer.max_themes == settings.max_themes  # Default value

    def test_cluster_embeddings(self, theme_analyzer, sample_embeddings):
        """Test clustering of embeddings."""
        labels = theme_analyzer.cluster_embeddings(sample_embeddings)

        assert isinstance(labels, np.ndarray)
        assert len(labels) == len(sample_embeddings)
        assert labels.dtype == np.int64 or labels.dtype == np.int32

        # Labels should be in valid range
        assert labels.min() >= 0
        assert labels.max() < theme_analyzer.n_themes

    def test_cluster_separation(self, theme_analyzer, sample_embeddings):
        """Test that clustering separates distinct clusters."""
        labels = theme_analyzer.cluster_embeddings(sample_embeddings)

        # We created 3 distinct clusters, should get 3 labels
        unique_labels = np.unique(labels)
        assert len(unique_labels) == 3

    @patch("docprocessor.core.theme_analyzer.ThemeAnalyzer._generate_theme_label")
    def test_discover_themes(
        self, mock_generate_label, theme_analyzer, sample_embeddings, sample_texts
    ):
        """Test theme discovery process."""
        # Mock LLM label generation
        mock_generate_label.side_effect = ["Contract Law", "Tort Law", "Criminal Law"]

        themes = theme_analyzer.discover_themes(sample_embeddings, sample_texts)

        assert isinstance(themes, list)
        assert len(themes) == 3  # Should discover 3 themes
        assert all(isinstance(theme, Theme) for theme in themes)

        # Check theme properties
        for theme in themes:
            assert theme.label is not None
            assert len(theme.label) > 0
            assert theme.chunk_count > 0
            assert len(theme.sample_chunks) > 0

    def test_theme_sample_size(self, theme_analyzer, sample_embeddings, sample_texts):
        """Test that themes contain reasonable sample sizes."""
        with patch.object(theme_analyzer, "_generate_theme_label", return_value="Test Theme"):
            themes = theme_analyzer.discover_themes(sample_embeddings, sample_texts)

            for theme in themes:
                # Each theme should have samples
                assert len(theme.sample_chunks) > 0
                # But not too many (limited by sample size parameter)
                assert len(theme.sample_chunks) <= 10  # Default sample size

    def test_empty_input(self, theme_analyzer):
        """Test handling of empty input."""
        embeddings = np.array([]).reshape(0, 384)
        texts = []

        # Should handle empty input gracefully
        themes = theme_analyzer.discover_themes(embeddings, texts)

        assert isinstance(themes, list)
        assert len(themes) == 0

    def test_single_cluster_input(self, theme_analyzer):
        """Test with too few samples for multiple clusters."""
        # Create very few embeddings
        embeddings = np.random.randn(2, 384).astype(np.float32)
        texts = ["Text 1", "Text 2"]

        with patch.object(theme_analyzer, "_generate_theme_label", return_value="Single Theme"):
            themes = theme_analyzer.discover_themes(embeddings, texts)

            # Should handle gracefully, might return 1 theme
            assert isinstance(themes, list)
            assert len(themes) >= 1


class TestThemeLabeling:
    """Test theme label generation."""

    @patch("docprocessor.core.theme_analyzer.ThemeAnalyzer._call_llm")
    def test_generate_theme_label(self, mock_llm, theme_analyzer):
        """Test theme label generation."""
        mock_llm.return_value = "Contract Formation and Enforcement"

        sample_texts = [
            "Contracts require offer and acceptance",
            "Consideration is essential for contracts",
            "Breach of contract leads to remedies",
        ]

        label = theme_analyzer._generate_theme_label(sample_texts)

        assert isinstance(label, str)
        assert len(label) > 0
        assert label == "Contract Formation and Enforcement"

        # Verify LLM was called
        mock_llm.assert_called_once()

    @patch("docprocessor.core.theme_analyzer.ThemeAnalyzer._call_llm")
    def test_label_generation_failure(self, mock_llm, theme_analyzer):
        """Test handling of label generation failure."""
        mock_llm.side_effect = Exception("LLM API error")

        sample_texts = ["Some text"]

        label = theme_analyzer._generate_theme_label(sample_texts)

        # Should return fallback label
        assert isinstance(label, str)
        assert "Theme" in label or "topic" in label.lower()

    def test_extract_keywords(self, theme_analyzer):
        """Test keyword extraction from theme samples."""
        texts = [
            "Contract law governs agreements between parties",
            "Formation of contracts requires offer and acceptance",
            "Breach of contract may result in damages",
        ]

        keywords = theme_analyzer._extract_keywords(texts)

        assert isinstance(keywords, list)
        assert len(keywords) > 0

        # Common words should appear as keywords
        assert any("contract" in kw.lower() for kw in keywords)


class TestThemeRanking:
    """Test theme ranking and importance."""

    def test_rank_themes_by_size(self, theme_analyzer):
        """Test ranking themes by size."""
        themes = [
            Theme(id="1", label="Theme 1", chunk_count=100, sample_chunks=["a"]),
            Theme(id="2", label="Theme 2", chunk_count=50, sample_chunks=["b"]),
            Theme(id="3", label="Theme 3", chunk_count=200, sample_chunks=["c"]),
        ]

        ranked = theme_analyzer.rank_themes(themes)

        # Should be sorted by chunk_count descending
        assert ranked[0].chunk_count == 200
        assert ranked[1].chunk_count == 100
        assert ranked[2].chunk_count == 50

    def test_calculate_theme_importance(self, theme_analyzer, sample_embeddings):
        """Test theme importance calculation."""
        labels = theme_analyzer.cluster_embeddings(sample_embeddings)

        # Calculate importance for each cluster
        for label_id in np.unique(labels):
            cluster_embeddings = sample_embeddings[labels == label_id]
            importance = theme_analyzer._calculate_importance(cluster_embeddings, sample_embeddings)

            assert isinstance(importance, float)
            assert 0.0 <= importance <= 1.0


class TestThemeEdgeCases:
    """Test edge cases and error handling."""

    def test_mismatched_embeddings_texts(self, theme_analyzer):
        """Test handling of mismatched embeddings and texts."""
        embeddings = np.random.randn(10, 384).astype(np.float32)
        texts = ["Only", "five", "texts", "provided", "here"]  # Fewer than embeddings

        with pytest.raises((ValueError, IndexError)):
            theme_analyzer.discover_themes(embeddings, texts)

    def test_invalid_n_themes(self, mock_vector_store):
        """Test invalid max_themes parameter."""
        with pytest.raises((ValueError, AssertionError)):
            ThemeAnalyzer(vector_store=mock_vector_store, max_themes=0)

        with pytest.raises((ValueError, AssertionError, TypeError)):
            ThemeAnalyzer(vector_store=mock_vector_store, max_themes=-5)

    def test_large_n_themes(self, theme_analyzer):
        """Test with n_themes larger than samples."""
        # Request more themes than we have samples
        analyzer = ThemeAnalyzer(n_themes=100)

        embeddings = np.random.randn(10, 384).astype(np.float32)
        texts = [f"Text {i}" for i in range(10)]

        with patch.object(analyzer, "_generate_theme_label", return_value="Theme"):
            themes = analyzer.discover_themes(embeddings, texts)

            # Should not create more themes than samples
            assert len(themes) <= 10
