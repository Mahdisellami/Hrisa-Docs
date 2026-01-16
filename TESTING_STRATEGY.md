# Testing Strategy

## Overview

This document outlines the testing strategy for the Document Processing & RAG Synthesis Application, with emphasis on the new multi-project and multi-task architecture.

---

## Testing Philosophy

1. **Test Pyramid Approach**
   - **Unit Tests (70%)**: Fast, isolated tests for individual components
   - **Integration Tests (20%)**: Test component interactions
   - **End-to-End Tests (10%)**: Full workflow testing

2. **Test-Driven Development (TDD)** where appropriate
   - Write tests for new features before implementation
   - Ensures testability and good design

3. **Continuous Testing**
   - Run unit tests frequently during development
   - Run full test suite before commits
   - Automated testing in CI/CD (future)

---

## Test Organization

```
tests/
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_project_model.py     # Project data model tests ✅
│   ├── test_project_manager.py   # ProjectManager CRUD tests ✅
│   ├── test_task_base.py         # Task abstraction tests
│   ├── test_tasks/                # Individual task tests
│   │   ├── test_summarization_task.py
│   │   ├── test_url_import_task.py
│   │   └── ...
│   ├── test_document_processor.py
│   ├── test_vector_store.py
│   ├── test_rag_pipeline.py
│   └── ...
│
├── integration/                   # Integration tests (moderate speed)
│   ├── test_project_workflow.py  # Multi-project workflows
│   ├── test_task_execution.py    # Task execution integration
│   ├── test_pdf_to_synthesis.py  # Full processing pipeline
│   └── test_vector_db_integration.py
│
├── e2e/                          # End-to-end tests (slow)
│   ├── test_gui_workflows.py    # GUI interaction tests
│   ├── test_full_synthesis.py   # Complete synthesis workflow
│   └── ...
│
├── fixtures/                     # Shared test fixtures
│   ├── sample_pdfs/
│   ├── test_projects/
│   └── mock_data/
│
└── conftest.py                   # Pytest configuration and fixtures
```

---

## Unit Testing Strategy

### What to Unit Test

1. **Data Models**
   - Serialization/deserialization
   - Validation logic
   - Business logic methods
   - Edge cases

2. **Business Logic**
   - ProjectManager CRUD operations
   - Task execution logic
   - Document processing
   - Theme discovery algorithms

3. **Utilities**
   - Helper functions
   - Text processing
   - File operations

### Unit Test Guidelines

```python
# Good unit test structure
def test_descriptive_name():
    # Arrange: Set up test data
    project = Project(name="Test")

    # Act: Perform action
    project.add_document(doc)

    # Assert: Verify result
    assert len(project.documents) == 1
```

**Best Practices:**
- One assertion per test (when possible)
- Descriptive test names
- Test both success and failure cases
- Use fixtures for common setup
- Mock external dependencies

### Current Unit Test Coverage

✅ **Completed:**
- `test_project_model.py` (17 tests)
  - ProjectSettings serialization
  - DocumentInfo CRUD
  - TaskExecutionRecord tracking
  - Project methods and statistics
  - File persistence

- `test_project_manager.py` (23 tests)
  - Project creation/deletion
  - Save/load operations
  - Search and filtering
  - Template support
  - Import/export
  - Cache functionality

⏳ **TODO:**
- `test_task_base.py` - Task abstraction framework
- `test_summarization_task.py` - Synthesis task
- `test_url_import_task.py` - URL import task
- `test_document_processor.py` - PDF processing
- `test_vector_store.py` - ChromaDB integration
- `test_rag_pipeline.py` - RAG functionality

---

## Integration Testing Strategy

### What to Integration Test

1. **Cross-Component Workflows**
   - Document import → Processing → Vector storage
   - Theme discovery → Synthesis → Output
   - Project save → Load → Verify consistency

2. **External Service Integration**
   - ChromaDB operations
   - Ollama LLM calls
   - File system operations
   - Web scraping (when implemented)

3. **Multi-Task Workflows**
   - Sequential task execution
   - Task result dependencies
   - Project state across tasks

### Integration Test Examples

```python
def test_full_document_processing_workflow():
    """Test: Import PDF → Process → Store embeddings → Verify"""
    # 1. Import document
    doc = import_pdf("test.pdf")

    # 2. Process document
    chunks = process_document(doc)

    # 3. Store in vector DB
    vector_store.add_chunks(chunks)

    # 4. Verify retrieval
    results = vector_store.search("query")
    assert len(results) > 0

def test_project_persistence_across_save_load():
    """Test: Create project → Add data → Save → Load → Verify"""
    # Create project with data
    project = manager.create_project("Test")
    project.add_document(doc)
    project.set_themes(themes)

    # Save
    manager.save_project(project)

    # Clear cache and reload
    manager.clear_cache()
    loaded = manager.load_project(project.id)

    # Verify all data intact
    assert loaded.name == "Test"
    assert len(loaded.documents) == 1
    assert len(loaded.themes) > 0
```

### Integration Test TODO

- [ ] Test full PDF → Synthesis workflow
- [ ] Test ChromaDB persistence across restarts
- [ ] Test multi-project vector DB isolation
- [ ] Test task execution with real LLM
- [ ] Test GUI → Backend integration

---

## End-to-End Testing Strategy

### What to E2E Test

1. **Complete User Workflows**
   - Create project → Import PDFs → Process → Generate synthesis → Export
   - Switch between projects
   - Edit themes and regenerate
   - Execute multiple task types in sequence

2. **GUI Workflows** (using PyQt testing)
   - Button clicks and form inputs
   - Tab navigation
   - Dialog interactions
   - Progress bar updates
   - Error message display

### E2E Test Approach

**Tools:**
- `pytest-qt` for PyQt GUI testing
- Real Ollama instance for LLM calls
- Real test PDFs (small samples)
- Temporary test directories

**Example:**
```python
def test_complete_synthesis_workflow_gui(qtbot):
    """Test full workflow through GUI"""
    # 1. Launch main window
    window = HrisaDocsWindow()
    qtbot.addWidget(window)

    # 2. Create new project (via GUI)
    # Click "New Project" button
    # Fill in project name
    # Click "Create"

    # 3. Import documents
    # Click "Import" button
    # Select test PDFs

    # 4. Process documents
    # Click "Process" button
    # Wait for processing complete

    # 5. Discover themes
    # Switch to Themes tab
    # Click "Discover Themes"
    # Wait for completion

    # 6. Generate synthesis
    # Switch to Synthesis tab
    # Configure settings
    # Click "Generate"
    # Wait for completion

    # 7. Verify output files exist
    output_dir = project.output_dir
    assert (output_dir / "synthesis.md").exists()
```

### E2E Test TODO

- [ ] Test complete synthesis workflow
- [ ] Test project switching in GUI
- [ ] Test error handling in GUI
- [ ] Test progress reporting
- [ ] Test file management tab
- [ ] Test settings persistence

---

## Test Fixtures & Utilities

### Shared Fixtures (`conftest.py`)

```python
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_dir():
    """Temporary directory for tests."""
    temp = Path(tempfile.mkdtemp())
    yield temp
    shutil.rmtree(temp)

@pytest.fixture
def sample_pdf():
    """Path to sample test PDF."""
    return Path(__file__).parent / "fixtures" / "sample.pdf"

@pytest.fixture
def project_manager(temp_dir):
    """ProjectManager with temp directory."""
    from src.docprocessor.core.project_manager import ProjectManager
    return ProjectManager(projects_dir=temp_dir)

@pytest.fixture
def mock_llm():
    """Mock LLM for testing without Ollama."""
    # Return mock that simulates LLM responses
    pass
```

### Test Data

**fixtures/sample_pdfs/**
- `short_paper.pdf` (2 pages, ~1000 words)
- `medium_paper.pdf` (10 pages, ~5000 words)
- `multi_author.pdf` (with metadata)
- `scanned.pdf` (to test OCR handling)

**fixtures/test_projects/**
- `simple_project.json` - Minimal project
- `full_project.json` - Project with all features
- `archived_project.json` - Archived project

---

## Mocking Strategy

### When to Mock

1. **External Services**
   - Ollama LLM calls (expensive, slow)
   - Web scraping requests
   - External APIs

2. **File System Operations** (in some tests)
   - Large file operations
   - Network file systems

3. **Time-dependent Operations**
   - Use freezegun or similar

### When NOT to Mock

1. **Data Models** - Test real implementations
2. **Business Logic** - Test actual code
3. **Database Operations** - Use test database
4. **File Operations** - Use temp directories

### Mock Examples

```python
from unittest.mock import Mock, patch

def test_llm_generation_mocked():
    """Test synthesis with mocked LLM."""
    with patch('src.docprocessor.llm.ollama_client.OllamaClient') as mock_llm:
        mock_llm.generate.return_value = "Mocked synthesis output"

        result = synthesize_chapter(theme)

        assert "Mocked" in result

def test_web_scraping_mocked():
    """Test URL import with mocked requests."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"<html>Test</html>"

        result = import_url("https://example.com")

        assert result is not None
```

---

## Test Execution

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_project_model.py

# Run specific test
pytest tests/unit/test_project_model.py::TestProject::test_create_project

# Run with coverage
pytest --cov=src/docprocessor --cov-report=html

# Run with verbose output
pytest -v

# Run in parallel (faster)
pytest -n auto
```

### Test Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    gui: marks tests that require GUI
```

### CI/CD Integration (Future)

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run unit tests
        run: pytest tests/unit/ --cov
      - name: Run integration tests
        run: pytest tests/integration/
```

---

## Coverage Goals

### Current Coverage

- **Project Model**: ~95% coverage ✅
- **ProjectManager**: ~90% coverage ✅
- **Task Base**: 0% (not yet tested) ⏳
- **Overall**: ~25% (early stage)

### Target Coverage

- **Unit Tests**: >80% coverage
- **Integration Tests**: >60% coverage
- **E2E Tests**: >50% critical paths

### Coverage Exclusions

- GUI boilerplate code
- Debug utilities
- Deprecated code

---

## Test Maintenance

### Regular Activities

1. **After Each Feature**
   - Add unit tests for new code
   - Update integration tests if workflow changes
   - Update fixtures if data models change

2. **Before Releases**
   - Run full test suite
   - Check coverage reports
   - Fix flaky tests
   - Update test documentation

3. **Monthly**
   - Review slow tests
   - Update test data
   - Refactor duplicated test code
   - Check for deprecated tests

---

## Testing Anti-Patterns to Avoid

❌ **Don't:**
- Test implementation details (test behavior, not internals)
- Write brittle tests that break with small changes
- Have tests depend on each other
- Use production data in tests
- Skip tests or mark as "TODO" indefinitely
- Test external services directly (mock them)

✅ **Do:**
- Test public interfaces
- Write resilient tests
- Keep tests independent
- Use test fixtures and mocks
- Fix or delete failing tests promptly
- Use integration tests for external services

---

## Testing New Task Types

When adding a new task (e.g., plagiarism detection, AI detection):

1. **Unit Test the Task**
   ```python
   # tests/unit/test_tasks/test_plagiarism_task.py
   def test_plagiarism_task_execution():
       task = PlagiarismTask()
       config = task.get_default_config()
       result = task.execute(documents, config)
       assert result.status == TaskStatus.COMPLETED
   ```

2. **Integration Test with ProjectManager**
   ```python
   def test_plagiarism_task_in_project():
       project = manager.create_project("Test")
       # Add documents
       # Execute task
       # Verify task history recorded
   ```

3. **E2E Test in GUI**
   ```python
   def test_plagiarism_task_gui(qtbot):
       # Navigate to Tasks tab
       # Select plagiarism check
       # Run and verify results
   ```

---

## Performance Testing (Future)

### Benchmarks to Track

1. **Processing Speed**
   - Documents per second
   - Chunks per second
   - Embeddings per second

2. **Synthesis Speed**
   - Chapters per minute
   - Words per second

3. **Memory Usage**
   - Peak memory during processing
   - Memory growth over time

4. **Database Performance**
   - Query time (p50, p95, p99)
   - Index size
   - Insertion speed

### Performance Test Example

```python
import time
import pytest

@pytest.mark.slow
def test_process_large_document_performance():
    """Test that large document processing completes in reasonable time."""
    start = time.time()

    process_document(large_pdf)  # 100+ pages

    elapsed = time.time() - start
    assert elapsed < 300  # Should complete in 5 minutes
```

---

## Test Documentation

### Test Docstrings

```python
def test_project_with_multiple_tasks():
    """Test project tracking multiple task executions.

    Scenario:
        1. Create project
        2. Execute summarization task
        3. Execute AI detection task
        4. Execute plagiarism check
        5. Verify all tasks recorded in history
        6. Verify statistics are correct

    Expected:
        - All 3 tasks appear in history
        - Task counts are correct
        - Each task has proper metadata
    """
    # Test implementation
```

---

## Next Steps for Testing

### Immediate (This Sprint)
- [x] Unit tests for Project model
- [x] Unit tests for ProjectManager
- [ ] Run tests and fix any failures
- [ ] Set up pytest configuration

### Short Term (Next Sprint)
- [ ] Unit tests for Task base classes
- [ ] Integration tests for project workflows
- [ ] Set up coverage reporting
- [ ] Create more test fixtures

### Medium Term (1-2 Months)
- [ ] E2E tests for GUI workflows
- [ ] Performance benchmarks
- [ ] CI/CD integration
- [ ] Automated test runs

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-qt](https://pytest-qt.readthedocs.io/) - PyQt testing
- [pytest-cov](https://pytest-cov.readthedocs.io/) - Coverage
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) - Mocking

---

*Last Updated: 2026-01-05*
