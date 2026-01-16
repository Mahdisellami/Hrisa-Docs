"""Smoke tests for GUI initialization."""

import pytest


@pytest.mark.smoke
@pytest.mark.gui
class TestGUILaunch:
    """Test that GUI components can be initialized."""

    def test_main_window_init(self, qapp):
        """Test main window initialization."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        assert window is not None
        # Window title now includes current project name and app name
        assert "Hrisa Docs" in window.windowTitle()
        assert window.current_project is not None
        # Note: themes may be loaded from existing project data
        assert window.themes is not None

    def test_document_list_widget_init(self, qapp):
        """Test FilesWidget initialization."""
        from docprocessor.gui.widgets import FilesWidget

        widget = FilesWidget()
        assert widget is not None
        assert widget.documents == []
        assert widget.documents_list is not None

    def test_theme_editor_widget_init(self, qapp):
        """Test ThemeEditorWidget initialization."""
        from docprocessor.gui.widgets import ThemeEditorWidget

        widget = ThemeEditorWidget()
        assert widget is not None
        assert widget.themes == []
        assert widget.list_widget is not None

    def test_synthesis_config_widget_init(self, qapp):
        """Test SynthesisConfigWidget initialization."""
        from docprocessor.gui.widgets import SynthesisConfigWidget

        widget = SynthesisConfigWidget()
        assert widget is not None
        config = widget.get_config()
        assert config is not None
        assert "synthesis_level" in config
        assert "output_format" in config


@pytest.mark.smoke
@pytest.mark.gui
class TestGUIComponents:
    """Test GUI component structure."""

    def test_main_window_has_tabs(self, qapp):
        """Test main window has all tabs."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        assert window.tabs is not None
        assert window.tabs.count() == 5  # 5 tabs (added figure extraction)

        # Check tab titles (may be in French or English depending on language setting)
        tab_titles = [window.tabs.tabText(i) for i in range(window.tabs.count())]
        # Just check that we have the expected number of tabs
        assert len(tab_titles) == 5

    def test_main_window_has_widgets(self, qapp):
        """Test main window has required widgets."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        assert hasattr(window, "files_widget")
        assert hasattr(window, "theme_editor")
        assert hasattr(window, "synthesis_config")
        assert hasattr(window, "progress_bar")
        assert hasattr(window, "figure_extraction_widget")

    def test_main_window_has_menubar(self, qapp):
        """Test main window has menubar."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        menubar = window.menuBar()
        assert menubar is not None

        actions = menubar.actions()
        assert len(actions) > 0

    def test_main_window_has_statusbar(self, qapp):
        """Test main window has statusbar."""
        from docprocessor.gui.main_window import DocumentProcessorWindow

        window = DocumentProcessorWindow()
        statusbar = window.statusBar()
        assert statusbar is not None
        # Status bar now shows project statistics
        message = statusbar.currentMessage()
        assert "docs" in message or "themes" in message or "tasks" in message
