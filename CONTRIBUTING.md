# Contributing to Hrisa Docs

Thank you for your interest in contributing to Hrisa Docs! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Message Conventions](#commit-message-conventions)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

Before you start contributing:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Hrisa-Docs.git
   cd Hrisa-Docs
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Mahdisellami/Hrisa-Docs.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Ollama (for LLM integration)
- Git

### Setup Development Environment

```bash
# Create virtual environment and install dependencies
make setup

# Run the application
make run

# Run tests
make test

# Format code
make format

# Run linters
make lint
```

### Install Development Dependencies

```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"
```

This installs:
- `pytest` - Testing framework
- `pytest-qt` - PyQt6 testing support
- `black` - Code formatter
- `ruff` - Fast Python linter
- `pytest-cov` - Coverage reporting

## How to Contribute

### Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Ollama version)
- Relevant logs from `~/.docprocessor/logs/docprocessor.log`

### Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Any relevant examples or mockups

### Contributing Code

1. **Find an issue** to work on or create a new one
2. **Comment** on the issue to let others know you're working on it
3. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```
4. **Make your changes** following the code style guidelines
5. **Add tests** for new functionality
6. **Update documentation** if needed
7. **Commit your changes** using conventional commit format
8. **Push to your fork** and create a pull request

## Code Style Guidelines

### Python Code Style

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use `isort` or organize manually:
  ```python
  # Standard library
  import os
  from pathlib import Path
  
  # Third-party
  from PyQt6.QtWidgets import QWidget
  import chromadb
  
  # Local
  from docprocessor.core import DocumentProcessor
  ```
- **Type hints**: Use type hints for function signatures
  ```python
  def process_document(path: Path, chunk_size: int = 1000) -> List[Chunk]:
      ...
  ```
- **Docstrings**: Use Google-style docstrings
  ```python
  def synthesize_chapter(theme: Theme, context: str) -> str:
      """Generate a chapter from a theme using RAG.
      
      Args:
          theme: The theme to synthesize
          context: Additional context for generation
          
      Returns:
          The generated chapter text
          
      Raises:
          LLMError: If generation fails
      """
      ...
  ```

### Formatting

**Before committing**, format your code:

```bash
# Format with Black
black src/ tests/

# Check with ruff
ruff check src/ tests/

# Or use make commands
make format
make lint
```

### GUI Code Guidelines

- Keep business logic separate from UI code
- Use signals and slots for communication
- Run heavy operations in background threads (QThread)
- Always test GUI changes manually

## Commit Message Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements
- `style:` - Code style changes (formatting)

### Examples

```bash
# Feature
feat(gui): add dark mode toggle to settings

# Bug fix
fix(pdf): handle corrupted PDF files gracefully

# Documentation
docs: add installation guide for Windows

# Test
test(embedder): add unit tests for batch processing

# Refactor
refactor(core): extract theme clustering into separate class
```

### Commit Guidelines

- Use the imperative mood ("add" not "added" or "adds")
- Keep subject line under 72 characters
- Reference issues in footer: `Fixes #123`, `Closes #456`
- Break down large changes into logical commits

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   pytest tests/ -v
   ```

3. **Check code quality**:
   ```bash
   black --check src/ tests/
   ruff check src/ tests/
   ```

4. **Update documentation** if you changed APIs or added features

### Submitting the PR

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub with:
   - Clear title following conventional commit format
   - Description of changes
   - Link to related issue(s)
   - Screenshots (for UI changes)
   - Testing notes

3. **PR Template** - Fill out the template:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   How were these changes tested?
   
   ## Checklist
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

### Code Review

- Be responsive to feedback
- Make requested changes promptly
- Keep discussions professional and constructive
- Squash commits before merging (if requested)

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_document_processor.py -v

# With coverage
pytest --cov=docprocessor --cov-report=html

# GUI tests (requires X11/display)
pytest tests/unit/gui/ -v
```

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test component interactions
- **GUI tests**: Use `pytest-qt` for PyQt6 testing

Example test:

```python
def test_document_processor_chunks_text():
    """Test that documents are chunked correctly."""
    processor = DocumentProcessor(chunk_size=1000, overlap=100)
    
    # Create test document
    doc = Document(content="..." * 2000, metadata={})
    
    # Process
    chunks = processor.chunk_document(doc)
    
    # Assert
    assert len(chunks) > 1
    assert all(len(c.content) <= 1000 for c in chunks)
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and methods
- Use type hints for function parameters and return values
- Keep docstrings up to date with code changes

### User Documentation

Update relevant documentation in `docs/`:
- `USER_GUIDE.md` - For user-facing features
- `DEVELOPMENT.md` - For developer setup changes
- `TROUBLESHOOTING.md` - For common issues
- `README.md` - For major changes

### Changelog

When your PR is merged, a maintainer will update `CHANGELOG.md` based on your commit messages (using conventional commits format).

## Project Structure

```
Hrisa-Docs/
├── src/docprocessor/       # Application source
│   ├── core/               # Business logic
│   ├── gui/                # PyQt6 interface
│   ├── llm/                # LLM integration
│   ├── models/             # Data models
│   └── utils/              # Utilities
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── config/                 # Configuration
├── docs/                   # Documentation
└── scripts/                # Build & utility scripts
```

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion (if enabled)
- **Documentation**: Check `docs/` folder for guides

## Recognition

Contributors will be recognized in:
- `CHANGELOG.md` entries (via git commits)
- GitHub contributors page
- Release notes

Thank you for contributing to Hrisa Docs!
