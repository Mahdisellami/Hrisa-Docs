"""Application configuration settings."""

import logging
import sys
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_base_dir() -> Path:
    """Get base directory for user data, works for dev and PyInstaller.

    Returns:
        Path: Base directory for application data
            - Development: project_root/data/
            - Packaged: ~/.docprocessor/data/
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # In packaged mode, use user's home directory for persistence
        sys._MEIPASS
        return Path.home() / ".docprocessor" / "data"
    except AttributeError:
        # Running in development mode - use project-local data directory
        return Path(__file__).parent.parent / "data"


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="DOCPROCESSOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_root: Path = Field(
        default_factory=lambda: get_base_dir().parent,
        description="Project root directory",
    )

    data_dir: Path = Field(
        default_factory=get_base_dir,
        description="Data directory",
    )

    vector_db_dir: Path = Field(
        default_factory=lambda: get_base_dir() / "vector_db",
        description="ChromaDB persistence directory",
    )

    projects_dir: Path = Field(
        default_factory=lambda: get_base_dir() / "projects",
        description="User projects directory",
    )

    output_dir: Path = Field(
        default_factory=lambda: get_base_dir() / "output",
        description="Output files directory",
    )

    log_file: Optional[Path] = Field(
        default_factory=lambda: get_base_dir() / "docprocessor.log",
        description="Log file path",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    chunk_size: int = Field(
        default=1000,
        description="Maximum chunk size in tokens",
        ge=100,
        le=4000,
    )

    chunk_overlap: int = Field(
        default=100,
        description="Overlap between chunks in tokens",
        ge=0,
        le=500,
    )

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings",
    )

    ollama_model: str = Field(
        default="llama3.1:latest",
        description="Ollama model to use for generation",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL",
    )

    max_retrieval_chunks: int = Field(
        default=10,
        description="Maximum number of chunks to retrieve for RAG",
        ge=1,
        le=50,
    )

    temperature: float = Field(
        default=0.7,
        description="LLM generation temperature",
        ge=0.0,
        le=2.0,
    )

    max_themes: int = Field(
        default=10,
        description="Maximum number of themes to discover",
        ge=2,
        le=30,
    )

    language: str = Field(
        default="fr",
        description="Application language (fr, en, ar)",
    )

    pipeline_language: str = Field(
        default="auto",
        description="Pipeline language for synthesis (auto, fr, en, ar)",
    )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    @property
    def log_level_int(self) -> int:
        """Convert log level string to integer."""
        return getattr(logging, self.log_level.upper(), logging.INFO)


settings = Settings()
settings.ensure_directories()
