"""Prompt template management system."""

import sys
from pathlib import Path
from typing import Dict, Optional

import yaml

from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in development mode
        base_path = Path(__file__).parent.parent.parent.parent

    return base_path / relative_path


class PromptManager:
    """Manages prompt templates for LLM interactions."""

    def __init__(self, prompts_file: Optional[Path] = None):
        """
        Initialize prompt manager.

        Args:
            prompts_file: Path to YAML file containing prompts (default: config/prompts.yaml)
        """
        if prompts_file is None:
            prompts_file = get_resource_path("config/prompts.yaml")

        self.prompts_file = prompts_file
        self.prompts: Dict = {}

        if self.prompts_file.exists():
            self.load_prompts()
            logger.info(f"Loaded {len(self.prompts)} prompt templates from {self.prompts_file}")
        else:
            logger.warning(f"Prompts file not found: {self.prompts_file}")
            self._create_default_prompts()

    def load_prompts(self) -> None:
        """Load prompts from YAML file."""
        try:
            with open(self.prompts_file, "r", encoding="utf-8") as f:
                self.prompts = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading prompts file: {e}")
            self.prompts = {}

    def _create_default_prompts(self) -> None:
        """Create default prompts as fallback."""
        self.prompts = {
            "rag_query": {
                "system": "You are a helpful assistant that answers questions based on provided context. Always cite the sources when possible.",
                "user": "Context:\n{context}\n\nQuestion: {question}\n\nProvide a detailed answer based on the context above.",
            },
            "theme_labeling": {
                "system": "You are an expert at analyzing text and identifying themes.",
                "user": "Analyze the following text chunks and provide a concise theme label (2-5 words) that captures the main topic:\n\n{chunks}\n\nTheme:",
            },
            "chapter_synthesis": {
                "system": "You are an expert academic writer helping synthesize research papers into a coherent book chapter.",
                "user": "Theme: {theme}\n\nRelevant excerpts:\n{chunks}\n\nWrite a comprehensive chapter section that synthesizes these excerpts. Include citations to source documents.",
            },
        }
        logger.info("Using default prompts")

    def get_prompt(self, prompt_name: str, **kwargs) -> tuple[str, str]:
        """
        Get a prompt template and fill in variables.

        Args:
            prompt_name: Name of the prompt template
            **kwargs: Variables to fill in the template

        Returns:
            Tuple of (system_prompt, user_prompt)

        Raises:
            KeyError: If prompt template not found
        """
        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt template '{prompt_name}' not found")

        prompt_template = self.prompts[prompt_name]
        system_prompt = prompt_template.get("system", "")
        user_template = prompt_template.get("user", "")

        # Fill in template variables
        try:
            user_prompt = user_template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise

        return system_prompt, user_prompt

    def get_rag_prompt(self, context: str, question: str) -> tuple[str, str]:
        """
        Get RAG query prompt.

        Args:
            context: Retrieved context chunks
            question: User question

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return self.get_prompt("rag_query", context=context, question=question)

    def get_theme_labeling_prompt(self, chunks: str) -> tuple[str, str]:
        """
        Get theme labeling prompt.

        Args:
            chunks: Text chunks to analyze

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return self.get_prompt("theme_labeling", chunks=chunks)

    def get_chapter_synthesis_prompt(
        self, theme: str, chunks: str, target_words: int = 1500
    ) -> tuple[str, str]:
        """
        Get chapter synthesis prompt.

        Args:
            theme: Chapter theme
            chunks: Relevant text excerpts
            target_words: Target word count for the chapter

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return self.get_prompt(
            "chapter_synthesis", theme=theme, chunks=chunks, target_words=target_words
        )

    def get_chapter_outline_prompt(self, theme: str, chunks: str) -> tuple[str, str]:
        """
        Get chapter outline prompt.

        Args:
            theme: Chapter theme
            chunks: Available content

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return self.get_prompt("chapter_outline", theme=theme, chunks=chunks)

    def get_chapter_sequencing_prompt(self, themes: str) -> tuple[str, str]:
        """
        Get chapter sequencing prompt.

        Args:
            themes: List of themes to order

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        return self.get_prompt("chapter_sequencing", themes=themes)

    def add_prompt(self, name: str, system: str, user: str) -> None:
        """
        Add a new prompt template.

        Args:
            name: Prompt name
            system: System prompt
            user: User prompt template
        """
        self.prompts[name] = {"system": system, "user": user}
        logger.info(f"Added prompt template: {name}")

    def list_prompts(self) -> list[str]:
        """Get list of available prompt names."""
        return list(self.prompts.keys())
