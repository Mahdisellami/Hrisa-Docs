"""Shared pytest fixtures and configuration."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir))


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def sample_pdf_path(test_data_dir):
    """Path to sample PDF for testing (if available)."""
    pdf_path = test_data_dir / "sample.pdf"
    if pdf_path.exists():
        return pdf_path
    return None


@pytest.fixture
def mock_ollama_client(monkeypatch):
    """Mock Ollama client for testing without LLM."""
    from unittest.mock import Mock

    mock_client = Mock()
    mock_client.generate.return_value = {"response": "Mocked LLM response for testing"}

    return mock_client


@pytest.fixture
def disable_logging(caplog):
    """Disable logging during tests to reduce noise."""
    import logging

    caplog.set_level(logging.CRITICAL)


# Markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "requires_ollama: marks tests that require Ollama running")
    config.addinivalue_line("markers", "requires_gpu: marks tests that require GPU")
