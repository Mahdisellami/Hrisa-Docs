"""Integration tests for language detection throughout the pipeline."""

from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.wip  # Skip in CI - setup issues


@pytest.mark.integration
class TestLanguageDetection:
    """Test language detection and consistency across the pipeline."""

    def test_french_document_produces_french_output(
        self, sample_text_french, temp_dir, mock_ollama_client
    ):
        """Test that French input produces French output."""
        import uuid

        from docprocessor.core.output_formatter import OutputFormatter
        from docprocessor.models.chapter import Chapter

        # Create chapter with French content
        chapter = Chapter(
            chapter_number=1,
            title="Droit constitutionnel",
            content=sample_text_french,
            theme_id=uuid.uuid4(),
            word_count=100,
            citations=[],
            metadata={},
        )

        formatter = OutputFormatter(output_dir=temp_dir)
        output_path = formatter.export_markdown(
            chapters=[chapter], title="Livre Test", author="Auteur Test"
        )

        content = output_path.read_text()

        # Should contain French labels
        assert "Par" in content or "Généré le" in content
        # Should not contain English labels for these fields
        assert "Generated" not in content or "Généré le" in content

    def test_english_document_produces_english_output(self, sample_text_english, temp_dir):
        """Test that English input produces English output."""
        import uuid

        from docprocessor.core.output_formatter import OutputFormatter
        from docprocessor.models.chapter import Chapter

        # Create chapter with English content
        chapter = Chapter(
            chapter_number=1,
            title="Constitutional Law",
            content=sample_text_english,
            theme_id=uuid.uuid4(),
            word_count=100,
            citations=[],
            metadata={},
        )

        formatter = OutputFormatter(output_dir=temp_dir)
        output_path = formatter.export_markdown(
            chapters=[chapter], title="Test Book", author="Test Author"
        )

        content = output_path.read_text()

        # Should contain English labels
        assert "By" in content or "Generated" in content

    @pytest.mark.skip(
        reason="label_theme method removed - labeling now done within discover_themes"
    )
    def test_theme_labeling_respects_language(
        self, sample_chunks, mock_vector_store, mock_prompt_manager
    ):
        """Test that theme labeling uses source language."""
        from docprocessor.core.theme_analyzer import ThemeAnalyzer

        # Mock LLM to return French response
        mock_ollama = Mock()
        mock_ollama.generate.return_value = """
Thème : Droit fiscal
Description: Analyse du système fiscal.
        """.strip()

        analyzer = ThemeAnalyzer(
            vector_store=mock_vector_store,
            ollama_client=mock_ollama,
            prompt_manager=mock_prompt_manager,
        )

        import uuid

        from docprocessor.models.theme import Theme

        theme = Theme(
            theme_id=uuid.uuid4(),
            label="",
            description="",
            chunk_ids=[c.id for c in sample_chunks],
            importance_score=0.5,
            metadata={},
        )

        labeled_theme = analyzer.label_theme(theme, sample_chunks)

        # Label should be cleaned (no "Thème :" prefix)
        assert not labeled_theme.label.startswith("Thème :")
        assert labeled_theme.description != ""

    def test_mixed_content_detection(self, temp_dir):
        """Test language detection with mixed content."""
        from docprocessor.utils.language_detector import LanguageDetector

        # Mostly French with some English
        mixed_text = """
        Le droit constitutionnel est fondamental. Les principes de base incluent
        la séparation des pouvoirs et les droits fondamentaux. Some English words here.
        """

        language = LanguageDetector.detect_language(mixed_text)

        # Should detect as French (majority)
        assert language == "french"

    def test_language_labels_complete_set(self):
        """Test that all required labels exist for each language."""
        from docprocessor.utils.language_detector import LanguageDetector

        required_keys = ["by", "generated", "table_of_contents", "chapter", "theme", "description"]

        for language in ["english", "french"]:
            labels = LanguageDetector.get_labels(language)
            for key in required_keys:
                assert key in labels
                assert labels[key] != ""
