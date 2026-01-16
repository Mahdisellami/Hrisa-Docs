"""Tests for RAG Pipeline."""

from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.wip  # Skip in CI until API stabilizes

from docprocessor.core.rag_pipeline import RAGPipeline


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = MagicMock()
    store.search_by_text.return_value = [
        {
            "id": "chunk1",
            "text": "AI governance requires transparency.",
            "metadata": {"document_id": "doc123", "page_number": 1},
        },
        {
            "id": "chunk2",
            "text": "Algorithmic accountability is essential.",
            "metadata": {"document_id": "doc456", "page_number": 2},
        },
    ]
    return store


@pytest.fixture
def mock_embedder():
    """Mock embedder."""
    embedder = MagicMock()
    embedder.embed_text.return_value = [0.1] * 384  # Mock embedding
    return embedder


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client."""
    client = MagicMock()
    client.generate.return_value = "AI governance is crucial for ethical AI development."
    return client


@pytest.fixture
def mock_prompt_manager():
    """Mock prompt manager."""
    manager = MagicMock()
    manager.get_rag_prompt.return_value = (
        "You are a helpful assistant.",
        "Answer the question based on context.",
    )
    return manager


@pytest.fixture
def rag_pipeline(mock_vector_store, mock_embedder, mock_ollama_client, mock_prompt_manager):
    """Create RAG pipeline with mocks."""
    return RAGPipeline(
        vector_store=mock_vector_store,
        embedder=mock_embedder,
        ollama_client=mock_ollama_client,
        prompt_manager=mock_prompt_manager,
        n_results=5,
    )


class TestRAGPipelineInitialization:
    """Test RAG pipeline initialization."""

    def test_initialization(self, mock_vector_store, mock_embedder):
        """Test basic initialization."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            n_results=10,
        )
        assert pipeline.vector_store == mock_vector_store
        assert pipeline.embedder == mock_embedder
        assert pipeline.n_results == 10
        assert pipeline.ollama_client is not None
        assert pipeline.prompt_manager is not None

    def test_initialization_with_custom_clients(
        self, mock_vector_store, mock_embedder, mock_ollama_client, mock_prompt_manager
    ):
        """Test initialization with custom clients."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            ollama_client=mock_ollama_client,
            prompt_manager=mock_prompt_manager,
        )
        assert pipeline.ollama_client == mock_ollama_client
        assert pipeline.prompt_manager == mock_prompt_manager


class TestRetrieval:
    """Test retrieval functionality."""

    def test_retrieve_basic(self, rag_pipeline, mock_vector_store, mock_embedder):
        """Test basic retrieval."""
        results = rag_pipeline.retrieve("What is AI governance?")

        assert len(results) == 2
        assert results[0]["text"] == "AI governance requires transparency."
        assert results[1]["text"] == "Algorithmic accountability is essential."

        mock_vector_store.search_by_text.assert_called_once_with(
            query_text="What is AI governance?",
            embedder=mock_embedder,
            n_results=5,
            where=None,
        )

    def test_retrieve_with_custom_n_results(self, rag_pipeline, mock_vector_store):
        """Test retrieval with custom number of results."""
        rag_pipeline.retrieve("test query", n_results=3)

        mock_vector_store.search_by_text.assert_called_with(
            query_text="test query",
            embedder=rag_pipeline.embedder,
            n_results=3,
            where=None,
        )

    def test_retrieve_with_filters(self, rag_pipeline, mock_vector_store):
        """Test retrieval with metadata filters."""
        filters = {"document_id": "doc123"}
        rag_pipeline.retrieve("test query", filters=filters)

        mock_vector_store.search_by_text.assert_called_with(
            query_text="test query",
            embedder=rag_pipeline.embedder,
            n_results=5,
            where=filters,
        )

    def test_retrieve_empty_results(self, rag_pipeline, mock_vector_store):
        """Test retrieval with no results."""
        mock_vector_store.search_by_text.return_value = []

        results = rag_pipeline.retrieve("nonexistent topic")
        assert results == []


class TestContextBuilding:
    """Test context building functionality."""

    def test_build_context_with_metadata(self, rag_pipeline):
        """Test building context with metadata."""
        results = [
            {
                "text": "First chunk of text.",
                "metadata": {"document_id": "doc123abc", "page_number": 1},
            },
            {
                "text": "Second chunk of text.",
                "metadata": {"document_id": "doc456def", "page_number": 2},
            },
        ]

        context = rag_pipeline.build_context(results, include_metadata=True)

        assert "[Source 1: Document doc123ab, Page 1]" in context
        assert "First chunk of text." in context
        assert "[Source 2: Document doc456de, Page 2]" in context
        assert "Second chunk of text." in context
        assert "---" in context

    def test_build_context_without_metadata(self, rag_pipeline):
        """Test building context without metadata."""
        results = [
            {"text": "First chunk.", "metadata": {"document_id": "doc1", "page_number": 1}},
            {"text": "Second chunk.", "metadata": {"document_id": "doc2", "page_number": 2}},
        ]

        context = rag_pipeline.build_context(results, include_metadata=False)

        assert "First chunk." in context
        assert "Second chunk." in context
        assert "---" in context
        assert "Source" not in context
        assert "Document" not in context

    def test_build_context_empty_results(self, rag_pipeline):
        """Test building context with no results."""
        context = rag_pipeline.build_context([])
        assert context == ""

    def test_build_context_missing_metadata(self, rag_pipeline):
        """Test building context with missing metadata fields."""
        results = [
            {"text": "Text without complete metadata.", "metadata": {}},
        ]

        context = rag_pipeline.build_context(results, include_metadata=True)
        assert "Text without complete metadata." in context
        assert "unknown" in context or "?" in context


class TestGeneration:
    """Test generation functionality."""

    def test_generate_basic(self, rag_pipeline, mock_ollama_client, mock_prompt_manager):
        """Test basic generation."""
        query = "What is AI governance?"
        context = "AI governance includes rules and standards."

        answer = rag_pipeline.generate(query, context)

        assert answer == "AI governance is crucial for ethical AI development."
        mock_prompt_manager.get_rag_prompt.assert_called_once_with(
            context=context,
            question=query,
        )
        mock_ollama_client.generate.assert_called_once()

    def test_generate_with_temperature(self, rag_pipeline, mock_ollama_client):
        """Test generation with custom temperature."""
        rag_pipeline.generate("test query", "test context", temperature=0.7)

        mock_ollama_client.generate.assert_called_once()
        call_kwargs = mock_ollama_client.generate.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.7

    def test_generate_with_streaming(self, rag_pipeline, mock_ollama_client):
        """Test generation with streaming flag."""
        rag_pipeline.generate("test query", "test context", stream=True)

        mock_ollama_client.generate.assert_called_once()
        call_kwargs = mock_ollama_client.generate.call_args.kwargs
        assert call_kwargs.get("stream") is True


class TestGenerateStreaming:
    """Test streaming generation."""

    def test_generate_streaming(self, rag_pipeline, mock_ollama_client, mock_prompt_manager):
        """Test streaming generation."""
        mock_ollama_client.generate_stream.return_value = iter(
            ["AI ", "governance ", "is important."]
        )

        query = "What is AI?"
        context = "AI stands for artificial intelligence."

        # Call generate_streaming
        chunks = list(rag_pipeline.generate_streaming(query, context))

        assert chunks == ["AI ", "governance ", "is important."]
        mock_prompt_manager.get_rag_prompt.assert_called_once_with(
            context=context,
            question=query,
        )

    def test_generate_streaming_with_temperature(self, rag_pipeline, mock_ollama_client):
        """Test streaming generation with custom temperature."""
        mock_ollama_client.generate_stream.return_value = iter(["test"])

        list(rag_pipeline.generate_streaming("query", "context", temperature=0.5))

        mock_ollama_client.generate_stream.assert_called_once()
        call_kwargs = mock_ollama_client.generate_stream.call_args.kwargs
        assert call_kwargs.get("temperature") == 0.5


class TestQueryIntegration:
    """Test full query flow."""

    def test_query_full_pipeline(self, rag_pipeline, mock_vector_store, mock_ollama_client):
        """Test complete query flow from retrieval to generation."""
        # Retrieve
        results = rag_pipeline.retrieve("What is AI governance?")
        assert len(results) == 2

        # Build context
        context = rag_pipeline.build_context(results)
        assert len(context) > 0

        # Generate
        answer = rag_pipeline.generate("What is AI governance?", context)
        assert answer == "AI governance is crucial for ethical AI development."

    def test_query_with_no_results(self, rag_pipeline, mock_vector_store, mock_ollama_client):
        """Test query when no results found."""
        mock_vector_store.search_by_text.return_value = []

        results = rag_pipeline.retrieve("nonexistent topic")
        context = rag_pipeline.build_context(results)

        assert context == ""

        # Generate should still work with empty context
        answer = rag_pipeline.generate("query", context)
        assert isinstance(answer, str)


class TestErrorHandling:
    """Test error handling."""

    def test_retrieve_with_vector_store_error(self, rag_pipeline, mock_vector_store):
        """Test handling of vector store errors."""
        mock_vector_store.search_by_text.side_effect = Exception("Vector store error")

        with pytest.raises(Exception, match="Vector store error"):
            rag_pipeline.retrieve("test query")

    def test_generate_with_ollama_error(self, rag_pipeline, mock_ollama_client):
        """Test handling of Ollama errors."""
        mock_ollama_client.generate.side_effect = Exception("Ollama error")

        with pytest.raises(Exception, match="Ollama error"):
            rag_pipeline.generate("query", "context")
