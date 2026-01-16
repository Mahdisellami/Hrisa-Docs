"""Language detection utility."""


class LanguageDetector:
    """Detect language from text samples."""

    # Common words for language detection
    LANGUAGE_MARKERS = {
        "french": {
            "words": [
                "le",
                "la",
                "les",
                "de",
                "des",
                "un",
                "une",
                "et",
                "est",
                "dans",
                "pour",
                "que",
                "qui",
                "avec",
                "sur",
            ],
            "labels": {
                "by": "Par",
                "generated": "Généré le",
                "table_of_contents": "Table des matières",
                "chapter": "Chapitre",
                "theme": "Thème",
                "description": "Description",
            },
        },
        "english": {
            "words": [
                "the",
                "of",
                "and",
                "to",
                "in",
                "is",
                "that",
                "for",
                "it",
                "with",
                "as",
                "was",
                "on",
                "are",
            ],
            "labels": {
                "by": "By",
                "generated": "Generated",
                "table_of_contents": "Table of Contents",
                "chapter": "Chapter",
                "theme": "Theme",
                "description": "Description",
            },
        },
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detect language from text sample.

        Args:
            text: Text to analyze

        Returns:
            Language code ('french', 'english', etc.)
        """
        if not text:
            return "english"  # Default fallback

        # Normalize text
        text_lower = text.lower()
        words = text_lower.split()

        if len(words) < 10:
            return "english"  # Too short, use default

        # Count language markers
        scores = {}
        for lang, markers in cls.LANGUAGE_MARKERS.items():
            score = sum(1 for word in words if word in markers["words"])
            scores[lang] = score

        # Return language with highest score
        if scores:
            detected = max(scores, key=scores.get)
            # Only return if we have reasonable confidence (at least 3 matches)
            if scores[detected] >= 3:
                return detected

        return "english"  # Default fallback

    @classmethod
    def get_labels(cls, language: str) -> dict:
        """
        Get language-specific labels.

        Args:
            language: Language code

        Returns:
            Dictionary of labels
        """
        return cls.LANGUAGE_MARKERS.get(language, cls.LANGUAGE_MARKERS["english"])["labels"]

    @classmethod
    def detect_from_chunks(cls, chunks: list, sample_size: int = 5) -> str:
        """
        Detect language from chunk samples.

        Args:
            chunks: List of chunks with 'text' field
            sample_size: Number of chunks to sample

        Returns:
            Detected language code
        """
        if not chunks:
            return "english"

        # Sample first few chunks
        sample_chunks = chunks[: min(sample_size, len(chunks))]
        combined_text = " ".join(chunk.get("text", "") for chunk in sample_chunks)

        return cls.detect_language(combined_text)
