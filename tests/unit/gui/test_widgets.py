"""Unit tests for GUI widgets."""

import pytest


@pytest.mark.unit
@pytest.mark.gui
class TestDocumentListWidget:
    """Test DocumentListWidget functionality."""

    def test_add_documents(self, qapp):
        """Test adding documents to the list."""
        from docprocessor.gui.widgets import DocumentListWidget

        widget = DocumentListWidget()
        test_docs = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]

        widget.add_documents(test_docs)

        assert len(widget.documents) == 2
        assert widget.list_widget.count() == 2

    def test_add_duplicate_documents(self, qapp):
        """Test that duplicate documents are not added."""
        from docprocessor.gui.widgets import DocumentListWidget

        widget = DocumentListWidget()
        test_doc = "/path/to/doc.pdf"

        widget.add_documents([test_doc])
        widget.add_documents([test_doc])  # Add again

        assert len(widget.documents) == 1
        assert widget.list_widget.count() == 1

    def test_remove_selected_document(self, qapp):
        """Test removing a selected document."""
        from docprocessor.gui.widgets import DocumentListWidget

        widget = DocumentListWidget()
        test_docs = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]
        widget.add_documents(test_docs)

        # Select first item
        widget.list_widget.setCurrentRow(0)
        widget.remove_selected()

        assert len(widget.documents) == 1
        assert widget.list_widget.count() == 1

    def test_clear_all_documents(self, qapp):
        """Test clearing all documents."""
        from docprocessor.gui.widgets import DocumentListWidget

        widget = DocumentListWidget()
        test_docs = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]
        widget.add_documents(test_docs)

        widget.clear_all()

        assert len(widget.documents) == 0
        assert widget.list_widget.count() == 0

    def test_documents_changed_signal(self, qapp):
        """Test that documents_changed signal is emitted."""
        from docprocessor.gui.widgets import DocumentListWidget

        widget = DocumentListWidget()
        signal_received = []

        widget.documents_changed.connect(lambda docs: signal_received.append(docs))
        widget.add_documents(["/path/to/doc.pdf"])

        assert len(signal_received) == 1
        assert len(signal_received[0]) == 1


@pytest.mark.unit
@pytest.mark.gui
class TestThemeEditorWidget:
    """Test ThemeEditorWidget functionality."""

    def test_set_themes(self, qapp):
        """Test setting themes."""
        from docprocessor.gui.widgets import ThemeEditorWidget

        widget = ThemeEditorWidget()
        test_themes = [
            {"label": "Theme 1", "chunk_ids": ["c1", "c2"], "importance_score": 0.8},
            {"label": "Theme 2", "chunk_ids": ["c3", "c4"], "importance_score": 0.6},
        ]

        widget.set_themes(test_themes)

        assert len(widget.themes) == 2
        assert widget.list_widget.count() == 2

    def test_rename_theme(self, qapp, monkeypatch):
        """Test renaming a theme."""
        from PyQt6.QtWidgets import QInputDialog

        from docprocessor.gui.widgets import ThemeEditorWidget

        widget = ThemeEditorWidget()
        test_themes = [{"label": "Old Name", "chunk_ids": [], "importance_score": 0.5}]
        widget.set_themes(test_themes)

        # Mock the input dialog
        monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("New Name", True))

        widget.list_widget.setCurrentRow(0)
        widget.rename_theme()

        assert widget.themes[0]["label"] == "New Name"

    def test_delete_theme(self, qapp):
        """Test deleting a theme."""
        from docprocessor.gui.widgets import ThemeEditorWidget

        widget = ThemeEditorWidget()
        test_themes = [
            {"label": "Theme 1", "chunk_ids": [], "importance_score": 0.5},
            {"label": "Theme 2", "chunk_ids": [], "importance_score": 0.5},
        ]
        widget.set_themes(test_themes)

        widget.list_widget.setCurrentRow(0)
        widget.delete_theme()

        assert len(widget.themes) == 1
        assert widget.themes[0]["label"] == "Theme 2"

    def test_themes_changed_signal(self, qapp):
        """Test that themes_changed signal is emitted."""
        from docprocessor.gui.widgets import ThemeEditorWidget

        widget = ThemeEditorWidget()
        signal_received = []

        widget.themes_changed.connect(lambda themes: signal_received.append(themes))
        widget.set_themes([{"label": "Test", "chunk_ids": [], "importance_score": 0.5}])

        assert len(signal_received) == 1


@pytest.mark.unit
@pytest.mark.gui
class TestSynthesisConfigWidget:
    """Test SynthesisConfigWidget functionality."""

    def test_get_config_default(self, qapp):
        """Test getting default configuration."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()
        config = widget.get_config()

        assert config["synthesis_level"] == "normal"
        assert config["output_format"] == "both"
        assert config["auto_themes"] is True
        assert config["include_citations"] is True

    def test_change_synthesis_level(self, qapp):
        """Test changing synthesis level."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()

        # Change to comprehensive
        widget.synthesis_level_combo.setCurrentIndex(2)
        config = widget.get_config()

        assert config["synthesis_level"] == "comprehensive"

    def test_auto_themes_toggle(self, qapp):
        """Test auto themes checkbox."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()

        # Disable auto themes
        widget.auto_themes_check.setChecked(False)
        config = widget.get_config()

        assert config["auto_themes"] is False
        assert config["num_themes"] == 5  # Default spin value
        assert widget.num_themes_spin.isEnabled()

    def test_set_ready_for_synthesis(self, qapp):
        """Test setting synthesis ready state."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()

        # Initially disabled
        assert not widget.synthesize_btn.isEnabled()

        # Enable
        widget.set_ready_for_synthesis(True)
        assert widget.synthesize_btn.isEnabled()

        # Disable
        widget.set_ready_for_synthesis(False)
        assert not widget.synthesize_btn.isEnabled()

    def test_synthesis_requested_signal(self, qapp):
        """Test synthesis_requested signal."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()
        signal_received = []

        widget.synthesis_requested.connect(lambda: signal_received.append(True))
        widget.set_ready_for_synthesis(True)
        widget.synthesize_btn.click()

        assert len(signal_received) == 1

    def test_config_changed_signal(self, qapp):
        """Test config_changed signal."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()
        signal_received = []

        widget.config_changed.connect(lambda config: signal_received.append(config))

        # Change a setting
        widget.synthesis_level_combo.setCurrentIndex(0)

        assert len(signal_received) > 0
