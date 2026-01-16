# Development Guide

Guide for developers working on Hrisa Docs.

## Table of Contents
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Building and Packaging](#building-and-packaging)
- [Architecture](#architecture)
- [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- **Python 3.11+** (3.11 recommended)
- **Git**
- **Make** (optional, for convenience)
- **Ollama** (for testing LLM features)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd Document-Processing

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies (development mode)
pip install -e .

# Install development dependencies
pip install pytest pytest-qt black ruff pyinstaller

# Or use Make
make setup
```

### IDE Setup

**VS Code** (Recommended):
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

**PyCharm**:
1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment → `.venv/bin/python`
3. Enable pytest in Run/Debug Configurations

---

## Project Structure

```
Document-Processing/
├── src/docprocessor/          # Main application code
│   ├── core/                  # Core business logic
│   │   ├── document_processor.py    # PDF/text extraction
│   │   ├── embedder.py              # Text embedding
│   │   ├── vector_store.py          # ChromaDB wrapper
│   │   ├── rag_pipeline.py          # RAG implementation
│   │   ├── theme_analyzer.py        # Theme discovery
│   │   ├── synthesis_engine.py      # Chapter generation
│   │   └── output_formatter.py      # Export (PDF, DOCX, MD)
│   │
│   ├── gui/                   # PyQt6 GUI
│   │   ├── __main__.py              # Application entry point
│   │   ├── main_window.py           # Main window
│   │   ├── theme_manager.py         # Theme system
│   │   ├── size_profile.py          # Size profiles
│   │   ├── widgets/                 # Custom widgets
│   │   │   ├── files_widget.py      # Document management
│   │   │   ├── theme_editor_widget.py  # Theme editor
│   │   │   ├── synthesis_config_widget.py  # Synthesis config
│   │   │   └── project_dashboard.py # Project management
│   │   ├── workers.py               # Background workers
│   │   └── dialogs/                 # Dialog windows
│   │
│   ├── llm/                   # LLM integration
│   │   ├── ollama_client.py         # Ollama API wrapper
│   │   └── prompt_manager.py        # Prompt templates
│   │
│   ├── models/                # Data models (Pydantic)
│   │   ├── document.py              # Document models
│   │   ├── chunk.py                 # Text chunk models
│   │   ├── theme.py                 # Theme models
│   │   ├── chapter.py               # Chapter models
│   │   └── project.py               # Project models
│   │
│   └── utils/                 # Utilities
│       ├── logger.py                # Logging setup
│       ├── language_manager.py      # i18n/translations
│       └── user_preferences.py      # User settings
│
├── config/                    # Configuration
│   ├── settings.py                  # Application settings
│   └── prompts.yaml                 # LLM prompts
│
├── tests/                     # Test suite
│   ├── unit/                        # Unit tests
│   │   ├── test_document_processor.py
│   │   ├── test_embedder.py
│   │   ├── test_vector_store.py
│   │   └── test_theme_analyzer.py
│   ├── integration/                 # Integration tests
│   └── conftest.py                  # Pytest fixtures
│
├── scripts/                   # Build and utility scripts
│   ├── build_macos.py               # macOS packaging
│   ├── build_windows.py             # Windows packaging
│   └── profile_performance.py       # Performance benchmarks
│
├── docs/                      # Documentation
│   ├── USER_GUIDE.md
│   ├── INSTALLATION.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md (this file)
│
├── data/                      # Local data (gitignored)
│   ├── projects/                    # Project files
│   ├── vector_db/                   # ChromaDB storage
│   └── output/                      # Generated documents
│
├── pyproject.toml             # Project metadata & dependencies
├── Makefile                   # Development commands
└── README.md                  # Project overview
```

---

## Development Workflow

### Running the Application

```bash
# Using Make
make run

# Direct Python
python -m docprocessor.gui

# With debug logging
DOCPROCESSOR_LOG_LEVEL=DEBUG python -m docprocessor.gui
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Edit code
   - Add tests
   - Update documentation

3. **Test changes**:
   ```bash
   # Run tests
   pytest

   # Test specific module
   pytest tests/unit/test_document_processor.py -v

   # Test GUI manually
   make run
   ```

4. **Format code**:
   ```bash
   # Format with black
   black src/ tests/

   # Or use Make
   make format
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   ```

6. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

---

## Code Style

### Python Style Guide

We follow **PEP 8** with these conventions:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Imports**: Organized in sections (stdlib, third-party, local)
- **Type hints**: Required for function signatures
- **Docstrings**: Google style

### Example

```python
"""Module for processing documents."""

import sys
from pathlib import Path
from typing import List, Optional

import numpy as np
from PyQt6.QtWidgets import QWidget

from docprocessor.models.document import Document
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class HrisaDocs:
    """Process documents and extract text.

    Attributes:
        chunk_size: Maximum size of text chunks
        chunk_overlap: Overlap between chunks
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """Initialize document processor.

        Args:
            chunk_size: Maximum size of text chunks
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Initialized HrisaDocs (size={chunk_size})")

    def process_document(self, file_path: Path) -> tuple[Document, List[str]]:
        """Process a document and extract chunks.

        Args:
            file_path: Path to document file

        Returns:
            Tuple of (Document, list of text chunks)

        Raises:
            FileNotFoundError: If document file doesn't exist
            ValueError: If document format is unsupported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        # Implementation...
        return document, chunks
```

### Formatting Tools

```bash
# Format code with black
black src/ tests/

# Check style with ruff
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_document_processor.py

# Specific test
pytest tests/unit/test_document_processor.py::test_extract_text

# With coverage
pytest --cov=docprocessor --cov-report=html

# GUI tests (requires X server)
pytest tests/integration/test_gui.py
```

### Writing Tests

**Unit test example**:
```python
"""Unit tests for document processor."""

import pytest
from pathlib import Path

from docprocessor.core.document_processor import HrisaDocs


@pytest.fixture
def processor():
    """Create document processor instance."""
    return HrisaDocs(chunk_size=1000)


def test_process_pdf(processor, tmp_path):
    """Test PDF processing."""
    # Create test PDF
    pdf_path = tmp_path / "test.pdf"
    # ... create test PDF

    # Process
    document, chunks = processor.process_document(pdf_path)

    # Assertions
    assert document is not None
    assert len(chunks) > 0
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_invalid_file(processor):
    """Test error handling for invalid files."""
    with pytest.raises(FileNotFoundError):
        processor.process_document(Path("nonexistent.pdf"))
```

**GUI test example**:
```python
"""GUI tests using pytest-qt."""

import pytest
from PyQt6.QtCore import Qt

from docprocessor.gui.main_window import MainWindow


@pytest.fixture
def main_window(qtbot):
    """Create main window instance."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


def test_window_title(main_window):
    """Test main window title."""
    assert "Hrisa Docs" in main_window.windowTitle()


def test_menu_actions(main_window, qtbot):
    """Test menu actions."""
    # Find menu action
    action = main_window.findChild(QAction, "import_action")

    # Click action
    qtbot.mouseClick(action, Qt.MouseButton.LeftButton)

    # Verify result
    # ...
```

### Test Coverage

Current coverage:
- Hrisa Docs: 85%
- Embedder: 90%
- Vector Store: 88%
- Theme Analyzer: 82%
- GUI: 45% (manual testing primarily)

Goal: >80% coverage for core modules.

---

## Building and Packaging

### macOS

```bash
# Build app bundle
python scripts/build_macos.py

# Or use Make
make build

# Output: dist/Hrisa Docs.app

# Create DMG (requires create-dmg)
brew install create-dmg
# DMG creation is automatic in build script
```

### Windows

```bash
# Build executable
python scripts/build_windows.py

# Output: dist/HrisaDocs.exe

# Create installer (requires Inno Setup)
# Installer creation is automatic in build script
```

### Build Configuration

Edit `scripts/build_macos.py` or `scripts/build_windows.py`:

```python
# Add hidden imports for missing modules
hiddenimports = [
    'your_module',
    # ...
]

# Add data files
datas = [
    ('config/', 'config'),
    # ...
]

# Exclude modules to reduce size
excludes = [
    'tkinter',
    'matplotlib',
    # ...
]
```

---

## Architecture

### Core Components

#### 1. Document Processing Pipeline

```
PDF/DOCX → Extract Text → Chunk → Embed → Store in Vector DB
```

**Files**:
- `document_processor.py`: Text extraction and chunking
- `embedder.py`: Generate embeddings
- `vector_store.py`: Store and retrieve chunks

#### 2. RAG Pipeline

```
Query → Embed → Search Vector DB → Retrieve Chunks → LLM Generate
```

**Files**:
- `rag_pipeline.py`: Orchestrates retrieval and generation
- `ollama_client.py`: LLM API wrapper
- `prompt_manager.py`: Prompt templates

#### 3. Theme Discovery

```
All Chunks → Cluster by Similarity → Label with LLM → Rank by Importance
```

**Files**:
- `theme_analyzer.py`: Clustering and theme labeling

#### 4. Synthesis Engine

```
Themes → Sequence Logically → Generate Chapters → Add Citations
```

**Files**:
- `synthesis_engine.py`: Chapter generation
- `output_formatter.py`: Export to PDF/DOCX/MD

#### 5. GUI Layer

**Architecture**: Model-View pattern with signals/slots

```
Main Window
├── Menu Bar (actions)
├── Tab Widget
│   ├── Documents Tab (FilesWidget)
│   ├── Themes Tab (ThemeEditorWidget)
│   └── Synthesis Tab (SynthesisConfigWidget)
└── Status Bar (progress)
```

**Background Workers** (QThread):
- `DocumentProcessingWorker`: Process documents
- `ThemeDiscoveryWorker`: Discover themes
- `SynthesisWorker`: Generate book

**Files**:
- `main_window.py`: Main application window
- `widgets/`: Custom widgets
- `workers.py`: Background threads

### Data Flow

```
User Action (GUI)
    ↓
Signal Emitted
    ↓
Worker Thread Created
    ↓
Core Logic Executed
    ↓
Progress Signals → GUI Update
    ↓
Finished Signal → GUI Update
```

### Key Design Patterns

1. **Singleton**: Language manager, preferences manager
2. **Factory**: Prompt manager creates prompts
3. **Observer**: Qt signals/slots for async operations
4. **Repository**: Project manager for data access
5. **Strategy**: Different synthesis levels

---

## Contributing

### Before Contributing

1. **Read documentation**: Understand architecture
2. **Check existing issues**: Avoid duplicate work
3. **Discuss major changes**: Create issue first

### Contribution Process

1. **Fork repository**
2. **Create feature branch**: `git checkout -b feature/name`
3. **Make changes**: Code + tests + docs
4. **Format code**: `black src/ tests/`
5. **Run tests**: `pytest`
6. **Commit**: `git commit -m "feat: Description"`
7. **Push**: `git push origin feature/name`
8. **Create Pull Request**

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat(synthesis): Add customizable chapter templates
fix(pdf): Resolve XeLaTeX path detection on Windows
docs(readme): Update installation instructions
refactor(embedder): Optimize batch processing
test(vector-store): Add integration tests for ChromaDB
```

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages follow convention
- [ ] All tests pass
- [ ] No new warnings or errors

---

## Debugging

### Logging

```python
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)

# Log levels
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")
```

### Debug Mode

```bash
# Enable debug logging
export DOCPROCESSOR_LOG_LEVEL=DEBUG
python -m docprocessor.gui

# View logs in real-time
tail -f ~/.docprocessor/logs/docprocessor.log
```

### PyQt Debugging

```python
# Enable PyQt warnings
export PYTHONWARNINGS=default

# Debug signals/slots
QObject.dumpObjectTree()
QObject.dumpObjectInfo()
```

### Profiling

```python
# Profile performance
python -m cProfile -o profile.stats -m docprocessor.gui

# View results
python -m pstats profile.stats
```

---

## Useful Commands

```bash
# Development
make setup          # Install dependencies
make run            # Run application
make test           # Run tests
make format         # Format code
make clean          # Clean build artifacts

# Building
make build          # Build for current platform
make package        # Create distributable package

# Testing
pytest              # All tests
pytest -v           # Verbose
pytest -k test_name # Specific test
pytest --cov        # With coverage

# Code quality
black src/          # Format code
ruff check src/     # Lint code
mypy src/           # Type checking
```

---

## Resources

### Documentation
- [PyQt6 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)

### Tools
- [PyInstaller](https://pyinstaller.org/en/stable/)
- [pytest](https://docs.pytest.org/)
- [black](https://black.readthedocs.io/)
- [ruff](https://beta.ruff.rs/docs/)

---

## Questions?

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues
- **Architecture**: Review code comments and docstrings

Happy coding! 🚀
