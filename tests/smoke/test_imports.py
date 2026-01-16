"""Smoke tests for module imports."""

import pytest


@pytest.mark.smoke
class TestCoreImports:
    """Test that core modules can be imported."""

    def test_import_document_processor(self):
        """Test DocumentProcessor import."""
        from docprocessor.core.document_processor import DocumentProcessor

        assert DocumentProcessor is not None

    def test_import_embedder(self):
        """Test Embedder import."""
        from docprocessor.core.embedder import Embedder

        assert Embedder is not None

    def test_import_vector_store(self):
        """Test VectorStore import."""
        from docprocessor.core.vector_store import VectorStore

        assert VectorStore is not None

    def test_import_theme_analyzer(self):
        """Test ThemeAnalyzer import."""
        from docprocessor.core.theme_analyzer import ThemeAnalyzer

        assert ThemeAnalyzer is not None

    def test_import_rag_pipeline(self):
        """Test RAGPipeline import."""
        from docprocessor.core.rag_pipeline import RAGPipeline

        assert RAGPipeline is not None

    def test_import_synthesis_engine(self):
        """Test SynthesisEngine import."""
        from docprocessor.core.synthesis_engine import SynthesisEngine

        assert SynthesisEngine is not None

    def test_import_output_formatter(self):
        """Test OutputFormatter import."""
        from docprocessor.core.output_formatter import OutputFormatter

        assert OutputFormatter is not None


@pytest.mark.smoke
class TestLLMImports:
    """Test that LLM modules can be imported."""

    def test_import_ollama_client(self):
        """Test OllamaClient import."""
        from docprocessor.llm.ollama_client import OllamaClient

        assert OllamaClient is not None

    def test_import_prompt_manager(self):
        """Test PromptManager import."""
        from docprocessor.llm.prompt_manager import PromptManager

        assert PromptManager is not None


@pytest.mark.smoke
@pytest.mark.gui
class TestGUIImports:
    """Test that GUI modules can be imported."""

    def test_import_main_window(self):
        """Test main window import."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        assert DocumentProcessorWindow is not None

    def test_import_widgets(self):
        """Test widget imports."""
        from docprocessor.gui.widgets import (
            DocumentListWidget,
            SynthesisConfigWidget,
            ThemeEditorWidget,
        )

        assert DocumentListWidget is not None
        assert ThemeEditorWidget is not None
        assert SynthesisConfigWidget is not None

    def test_import_workers(self):
        """Test worker imports."""
        from docprocessor.gui.workers import (
            DocumentProcessingWorker,
            SynthesisWorker,
            ThemeDiscoveryWorker,
        )

        assert DocumentProcessingWorker is not None
        assert ThemeDiscoveryWorker is not None
        assert SynthesisWorker is not None


@pytest.mark.smoke
class TestModelImports:
    """Test that model classes can be imported."""

    def test_import_document_model(self):
        """Test Document model import."""
        from docprocessor.models.document import Document

        assert Document is not None

    def test_import_chunk_model(self):
        """Test Chunk model import."""
        from docprocessor.models.chunk import Chunk

        assert Chunk is not None

    def test_import_theme_model(self):
        """Test Theme model import."""
        from docprocessor.models.theme import Theme

        assert Theme is not None

    def test_import_chapter_model(self):
        """Test Chapter model import."""
        from docprocessor.models.chapter import Chapter

        assert Chapter is not None
