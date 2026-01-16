"""GUI widgets for Hrisa Docs."""

from .document_list import DocumentListWidget
from .files_widget import FilesWidget
from .project_dashboard import ProjectDashboard
from .synthesis_config import SynthesisConfigWidget
from .theme_editor import ThemeEditorWidget

__all__ = [
    "DocumentListWidget",
    "ThemeEditorWidget",
    "SynthesisConfigWidget",
    "FilesWidget",
    "ProjectDashboard",
]
