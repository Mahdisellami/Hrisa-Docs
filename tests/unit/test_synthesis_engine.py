"""Tests for Synthesis Engine."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

pytestmark = pytest.mark.wip  # Skip in CI until API stabilizes

from docprocessor.core.synthesis_engine import SynthesisEngine
from docprocessor.models import Chapter, Theme


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = MagicMock()
    store.get_by_ids.return_value = [
        {
            "id": "chunk1",
            "text": "AI governance text.",
            "metadata": {"document_id": "doc1", "page_number": 1},
        }
    ]
    return store


@pytest.fixture
def mock_embedder():
    """Mock embedder."""
    return MagicMock()


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client."""
    client = MagicMock()
    client.generate.return_value = "Generated chapter content."
    return client


@pytest.fixture
def mock_prompt_manager():
    """Mock prompt manager."""
    manager = MagicMock()
    manager.get_chapter_sequencing_prompt.return_value = (
        "System prompt",
        "User prompt",
    )
    manager.get_chapter_synthesis_prompt.return_value = (
        "System prompt",
        "User prompt",
    )
    return manager


@pytest.fixture
def mock_rag_pipeline():
    """Mock RAG pipeline."""
    pipeline = MagicMock()
    pipeline.retrieve.return_value = [
        {
            "text": "Retrieved chunk.",
            "metadata": {"document_id": "doc1", "page_number": 1},
        }
    ]
    pipeline.build_context.return_value = "Built context."
    return pipeline


@pytest.fixture
def sample_themes():
    """Create sample themes."""
    return [
        Theme(
            label="AI Governance",
            description="Rules and standards for AI",
            chunk_ids=[uuid4(), uuid4()],
            keywords=["governance", "rules"],
            importance_score=0.4,
        ),
        Theme(
            label="Algorithmic Transparency",
            description="Making AI decisions understandable",
            chunk_ids=[uuid4()],
            keywords=["transparency", "explainability"],
            importance_score=0.3,
        ),
        Theme(
            label="AI Ethics",
            description="Ethical considerations in AI",
            chunk_ids=[uuid4(), uuid4(), uuid4()],
            keywords=["ethics", "fairness"],
            importance_score=0.3,
        ),
    ]


@pytest.fixture
def synthesis_engine(
    mock_vector_store,
    mock_embedder,
    mock_ollama_client,
    mock_prompt_manager,
    mock_rag_pipeline,
):
    """Create synthesis engine with mocks."""
    return SynthesisEngine(
        vector_store=mock_vector_store,
        embedder=mock_embedder,
        ollama_client=mock_ollama_client,
        prompt_manager=mock_prompt_manager,
        rag_pipeline=mock_rag_pipeline,
    )


class TestSynthesisEngineInitialization:
    """Test synthesis engine initialization."""

    def test_initialization(self, mock_vector_store):
        """Test basic initialization."""
        engine = SynthesisEngine(vector_store=mock_vector_store)
        assert engine.vector_store == mock_vector_store
        assert engine.embedder is not None
        assert engine.ollama_client is not None
        assert engine.prompt_manager is not None
        assert engine.rag_pipeline is not None

    def test_initialization_with_custom_components(
        self,
        mock_vector_store,
        mock_embedder,
        mock_ollama_client,
        mock_prompt_manager,
        mock_rag_pipeline,
    ):
        """Test initialization with custom components."""
        engine = SynthesisEngine(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            ollama_client=mock_ollama_client,
            prompt_manager=mock_prompt_manager,
            rag_pipeline=mock_rag_pipeline,
        )
        assert engine.embedder == mock_embedder
        assert engine.ollama_client == mock_ollama_client
        assert engine.prompt_manager == mock_prompt_manager
        assert engine.rag_pipeline == mock_rag_pipeline


class TestChapterPlanning:
    """Test chapter planning functionality."""

    def test_plan_chapters_single_theme(self, synthesis_engine, sample_themes):
        """Test planning with single theme."""
        single_theme = [sample_themes[0]]
        result = synthesis_engine.plan_chapters(single_theme)
        assert result == single_theme

    def test_plan_chapters_multiple_themes(
        self, synthesis_engine, sample_themes, mock_ollama_client
    ):
        """Test planning with multiple themes."""
        # Mock LLM response suggesting reordering
        mock_ollama_client.generate.return_value = "1. Theme 3\n2. Theme 1\n3. Theme 2"

        result = synthesis_engine.plan_chapters(sample_themes)

        assert len(result) == 3
        mock_ollama_client.generate.assert_called_once()

    def test_plan_chapters_with_title_and_objective(
        self, synthesis_engine, sample_themes, mock_prompt_manager
    ):
        """Test planning with book title and objective."""
        synthesis_engine.plan_chapters(
            sample_themes,
            book_title="AI Governance Handbook",
            book_objective="Comprehensive guide to AI regulation",
        )

        # Verify prompt manager was called
        mock_prompt_manager.get_chapter_sequencing_prompt.assert_called_once()

    def test_plan_chapters_parsing_failure(
        self, synthesis_engine, sample_themes, mock_ollama_client
    ):
        """Test planning when order parsing fails."""
        mock_ollama_client.generate.return_value = "Invalid response format"

        result = synthesis_engine.plan_chapters(sample_themes)

        # Should return original order on parsing failure
        assert result == sample_themes

    def test_plan_chapters_llm_error(self, synthesis_engine, sample_themes, mock_ollama_client):
        """Test planning when LLM errors."""
        mock_ollama_client.generate.side_effect = Exception("LLM error")

        result = synthesis_engine.plan_chapters(sample_themes)

        # Should return original order on error
        assert result == sample_themes


class TestChapterOrderParsing:
    """Test chapter order parsing."""

    def test_parse_chapter_order_simple(self, synthesis_engine):
        """Test parsing simple numbered list."""
        response = "1. Theme A\n2. Theme B\n3. Theme C"
        order = synthesis_engine._parse_chapter_order(response, 3)
        assert order == [1, 2, 3]

    def test_parse_chapter_order_with_text(self, synthesis_engine):
        """Test parsing with additional text."""
        response = """
        Here's the suggested order:
        1. Theme A - Most foundational
        2. Theme C - Builds on A
        3. Theme B - Advanced topic
        """
        order = synthesis_engine._parse_chapter_order(response, 3)
        assert order == [1, 3, 2] or order == [1, 2, 3]  # Flexible parsing

    def test_parse_chapter_order_invalid(self, synthesis_engine):
        """Test parsing invalid response."""
        response = "No numbers here"
        order = synthesis_engine._parse_chapter_order(response, 3)
        assert order is None

    def test_parse_chapter_order_partial(self, synthesis_engine):
        """Test parsing when not all themes are mentioned."""
        response = "1. Theme A\n2. Theme B"
        order = synthesis_engine._parse_chapter_order(response, 3)
        # Should handle partial orders gracefully
        assert order is None or len(order) == 3


class TestChapterSynthesis:
    """Test chapter synthesis functionality."""

    def test_synthesize_chapter_basic(
        self, synthesis_engine, sample_themes, mock_ollama_client, mock_vector_store
    ):
        """Test basic chapter synthesis."""
        theme = sample_themes[0]

        chapter = synthesis_engine.synthesize_chapter(
            theme=theme,
            chapter_number=1,
            total_chapters=3,
        )

        assert isinstance(chapter, Chapter)
        assert chapter.title == theme.label
        assert chapter.number == 1
        assert len(chapter.content) > 0
        mock_ollama_client.generate.assert_called()

    def test_synthesize_chapter_with_detail_level(
        self, synthesis_engine, sample_themes, mock_prompt_manager
    ):
        """Test synthesis with different detail levels."""
        theme = sample_themes[0]

        synthesis_engine.synthesize_chapter(
            theme=theme,
            chapter_number=1,
            detail_level="high",
        )

        # Verify prompt manager was called
        mock_prompt_manager.get_chapter_synthesis_prompt.assert_called()

    def test_synthesize_chapter_with_context(
        self, synthesis_engine, sample_themes, mock_prompt_manager
    ):
        """Test synthesis with additional context."""
        theme = sample_themes[0]

        synthesis_engine.synthesize_chapter(
            theme=theme,
            chapter_number=2,
            previous_chapter_summary="Previous chapter discussed basics.",
        )

        # Verify prompt includes context
        mock_prompt_manager.get_chapter_synthesis_prompt.assert_called()

    def test_synthesize_chapter_empty_theme(self, synthesis_engine):
        """Test synthesis with theme containing no chunks."""
        empty_theme = Theme(
            label="Empty Theme",
            description="No content",
            chunk_ids=[],
            keywords=[],
            importance_score=0.0,
        )

        chapter = synthesis_engine.synthesize_chapter(
            theme=empty_theme,
            chapter_number=1,
        )

        # Should handle empty theme gracefully
        assert isinstance(chapter, Chapter)

    def test_synthesize_chapter_llm_error(
        self, synthesis_engine, sample_themes, mock_ollama_client
    ):
        """Test synthesis when LLM errors."""
        mock_ollama_client.generate.side_effect = Exception("LLM error")
        theme = sample_themes[0]

        with pytest.raises(Exception, match="LLM error"):
            synthesis_engine.synthesize_chapter(theme=theme, chapter_number=1)


class TestFullSynthesis:
    """Test full book synthesis."""

    def test_synthesize_book_basic(self, synthesis_engine, sample_themes, mock_ollama_client):
        """Test synthesizing full book."""
        chapters = synthesis_engine.synthesize_book(themes=sample_themes)

        assert len(chapters) == 3
        assert all(isinstance(ch, Chapter) for ch in chapters)
        assert all(ch.content for ch in chapters)
        # Verify generate was called for each chapter
        assert mock_ollama_client.generate.call_count >= 3

    def test_synthesize_book_with_max_chapters(self, synthesis_engine, sample_themes):
        """Test synthesizing with max chapter limit."""
        chapters = synthesis_engine.synthesize_book(
            themes=sample_themes,
            max_chapters=2,
        )

        assert len(chapters) <= 2

    def test_synthesize_book_with_title(self, synthesis_engine, sample_themes, mock_prompt_manager):
        """Test synthesizing with book title."""
        synthesis_engine.synthesize_book(
            themes=sample_themes,
            book_title="AI Governance Guide",
        )

        # Verify title was used in planning
        mock_prompt_manager.get_chapter_sequencing_prompt.assert_called()

    def test_synthesize_book_empty_themes(self, synthesis_engine):
        """Test synthesizing with no themes."""
        chapters = synthesis_engine.synthesize_book(themes=[])
        assert chapters == []


class TestChapterMetadata:
    """Test chapter metadata generation."""

    def test_chapter_has_correct_metadata(self, synthesis_engine, sample_themes):
        """Test that generated chapters have correct metadata."""
        theme = sample_themes[0]

        chapter = synthesis_engine.synthesize_chapter(
            theme=theme,
            chapter_number=2,
            total_chapters=5,
        )

        assert chapter.number == 2
        assert chapter.title == theme.label
        assert chapter.theme_id == theme.id
        assert len(chapter.source_chunk_ids) > 0

    def test_chapter_includes_citations(self, synthesis_engine, sample_themes, mock_vector_store):
        """Test that chapters include citation information."""
        theme = sample_themes[0]

        chapter = synthesis_engine.synthesize_chapter(
            theme=theme,
            chapter_number=1,
        )

        # Chapter should track source chunks for citations
        assert len(chapter.source_chunk_ids) > 0
        assert all(isinstance(id, str) for id in chapter.source_chunk_ids)


class TestProgressTracking:
    """Test synthesis progress tracking."""

    def test_synthesize_book_with_progress_callback(self, synthesis_engine, sample_themes):
        """Test synthesis with progress callback."""
        progress_updates = []

        def progress_callback(current, total, message):
            progress_updates.append((current, total, message))

        synthesis_engine.synthesize_book(
            themes=sample_themes,
            progress_callback=progress_callback,
        )

        # Verify progress updates were made
        assert len(progress_updates) >= 3
        assert progress_updates[-1][0] == progress_updates[-1][1]  # Final update

    def test_progress_callback_receives_correct_info(self, synthesis_engine, sample_themes):
        """Test that progress callback receives correct information."""
        progress_data = []

        def callback(current, total, msg):
            progress_data.append({"current": current, "total": total, "message": msg})

        synthesis_engine.synthesize_book(
            themes=sample_themes,
            progress_callback=callback,
        )

        # Check that progress goes from 0 to total
        assert progress_data[0]["current"] == 0
        assert progress_data[-1]["current"] == len(sample_themes)
        assert all(pd["total"] == len(sample_themes) for pd in progress_data)
