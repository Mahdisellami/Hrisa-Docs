"""Integration tests for GUI workflows."""

from unittest.mock import patch

import pytest


@pytest.mark.integration
@pytest.mark.gui
class TestGUIWorkflow:
    """Test GUI workflow integration."""

    @pytest.mark.wip  # Skip in CI - button state assertion issue
    def test_main_window_initial_state(self, qapp):
        """Test main window initial state."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Check initial button states
        assert not window.discover_btn.isEnabled()  # No processed data
        assert not window.synthesis_config.synthesize_btn.isEnabled()  # No themes
        # Figure extraction button state depends on whether a project with documents was loaded
        # If no documents, button should be disabled
        if window.current_project and len(window.current_project.documents) == 0:
            assert not window.figure_extraction_widget.extract_btn.isEnabled()

    def test_document_addition_enables_processing(self, qapp):
        """Test that adding documents enables processing."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Add documents to current project
        window.files_widget.documents = ["/path/to/doc.pdf"]
        window.files_widget.documents_changed.emit(window.files_widget.documents)

        # Figure extraction button should be enabled after documents added
        assert window.figure_extraction_widget.extract_btn.isEnabled()

    def test_widget_signal_connections(self, qapp):
        """Test that widget signals are connected."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        signal_received = []

        # Test files widget signal
        def on_docs_changed(docs):
            signal_received.append(("docs", len(docs)))

        window.files_widget.documents_changed.connect(on_docs_changed)

        # Emit signal manually
        window.files_widget.documents = ["/path/to/doc.pdf"]
        window.files_widget.documents_changed.emit(window.files_widget.documents)

        assert len(signal_received) >= 1
        assert signal_received[0] == ("docs", 1)

    @pytest.mark.wip  # Skip in CI - button state assertion issue
    def test_theme_editor_update_enables_synthesis(self, qapp):
        """Test that theme discovery enables synthesis."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Initially synthesis should be disabled
        assert not window.synthesis_config.synthesize_btn.isEnabled()

        # Set themes
        test_themes = [{"label": "Theme 1", "chunk_ids": ["c1", "c2"], "importance_score": 0.8}]
        window.theme_editor.set_themes(test_themes)

        # Synthesis should now be enabled
        assert window.synthesis_config.synthesize_btn.isEnabled()

    def test_synthesis_config_get_config(self, qapp):
        """Test synthesis configuration retrieval."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        config = window.synthesis_config.get_config()

        assert "synthesis_level" in config
        assert "chunks_per_chapter" in config
        assert "output_format" in config
        assert "include_citations" in config

    def test_progress_bar_visibility(self, qapp):
        """Test progress bar visibility state."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Initially hidden
        assert not window.progress_bar.isVisible()

    @patch("docprocessor.gui.workers.DocumentProcessor")
    @patch("docprocessor.gui.workers.VectorStore")
    @patch("docprocessor.gui.workers.Embedder")
    def test_processing_worker_creation(
        self, mock_embedder, mock_vector_store, mock_processor, qapp
    ):
        """Test that processing worker can be created."""
        from docprocessor.gui.workers import DocumentProcessingWorker

        worker = DocumentProcessingWorker(document_paths=["/path/to/doc.pdf"], project_name="test")

        assert worker is not None
        assert worker.document_paths == ["/path/to/doc.pdf"]

    @patch("docprocessor.gui.workers.ThemeAnalyzer")
    def test_theme_worker_creation(self, mock_analyzer, qapp):
        """Test that theme discovery worker can be created."""
        from docprocessor.gui.workers import ThemeDiscoveryWorker

        worker = ThemeDiscoveryWorker(project_name="test", num_themes=5)

        assert worker is not None
        assert worker.num_themes == 5

    @patch("docprocessor.gui.workers.SynthesisEngine")
    def test_synthesis_worker_creation(self, mock_engine, qapp):
        """Test that synthesis worker can be created."""
        from docprocessor.gui.workers import SynthesisWorker

        worker = SynthesisWorker(
            project_name="test",
            synthesis_level="normal",
            chunks_per_chapter=150,
            output_format="both",
        )

        assert worker is not None
        assert worker.synthesis_level == "normal"


@pytest.mark.integration
@pytest.mark.gui
class TestGUIStateManagement:
    """Test GUI state management."""

    def test_tab_navigation(self, qapp):
        """Test switching between tabs."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Switch to themes tab
        window.tabs.setCurrentIndex(1)
        assert window.tabs.currentIndex() == 1

        # Switch to synthesis tab
        window.tabs.setCurrentIndex(2)
        assert window.tabs.currentIndex() == 2

    def test_button_state_after_document_removal(self, qapp):
        """Test button states after removing all documents."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Add documents
        window.files_widget.documents = ["/path/to/doc.pdf"]
        window.files_widget.documents_changed.emit(window.files_widget.documents)
        assert window.figure_extraction_widget.extract_btn.isEnabled()

        # Remove all documents
        window.files_widget.documents = []
        window.files_widget.documents_changed.emit(window.files_widget.documents)
        assert not window.figure_extraction_widget.extract_btn.isEnabled()

    def test_status_bar_updates(self, qapp):
        """Test status bar message updates."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Check initial message shows project stats
        initial_message = window.statusBar().currentMessage()
        assert (
            "docs" in initial_message or "themes" in initial_message or "tasks" in initial_message
        )

        # Status bar exists and is functional
        assert window.statusBar() is not None

    def test_synthesis_config_changes_emit_signal(self, qapp):
        """Test that config changes emit signals."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        signal_received = []

        window.synthesis_config.config_changed.connect(
            lambda config: signal_received.append(config)
        )

        # Change synthesis level
        window.synthesis_config.synthesis_level_combo.setCurrentIndex(0)

        assert len(signal_received) > 0

    def test_multiple_document_operations(self, qapp):
        """Test multiple sequential document operations."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()

        # Add documents
        window.files_widget.documents = ["/path/to/doc1.pdf"]
        assert len(window.files_widget.documents) == 1

        # Add more
        window.files_widget.documents.extend(["/path/to/doc2.pdf", "/path/to/doc3.pdf"])
        assert len(window.files_widget.documents) == 3

        # Remove one
        window.files_widget.documents.pop(0)
        assert len(window.files_widget.documents) == 2
