"""Theme analysis and discovery from document collections."""

from collections import Counter
from typing import Dict, List, Optional
from uuid import UUID

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from config.settings import settings
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.llm.prompt_manager import PromptManager
from docprocessor.models import Theme
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class ThemeAnalyzer:
    """Analyzes document collections to discover and label themes."""

    def __init__(
        self,
        vector_store: VectorStore,
        ollama_client: Optional[OllamaClient] = None,
        prompt_manager: Optional[PromptManager] = None,
        max_themes: int = settings.max_themes,
    ):
        """
        Initialize theme analyzer.

        Args:
            vector_store: Vector store containing document chunks
            ollama_client: Optional Ollama client (creates new if not provided)
            prompt_manager: Optional prompt manager (creates new if not provided)
            max_themes: Maximum number of themes to discover
        """
        self.vector_store = vector_store
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.max_themes = max_themes

        logger.info(f"ThemeAnalyzer initialized with max_themes={max_themes}")

    def discover_themes(
        self,
        n_themes: Optional[int] = None,
        min_cluster_size: int = 2,
    ) -> List[Theme]:
        """
        Discover themes from document collection using clustering.

        Args:
            n_themes: Number of themes to discover (auto-detect if None)
            min_cluster_size: Minimum chunks per theme

        Returns:
            List of Theme objects with labels and chunk assignments
        """
        logger.info("Starting theme discovery...")

        # Get all chunks with embeddings
        chunks = self.vector_store.get_all_chunks()

        if len(chunks) < 3:
            logger.warning(f"Too few chunks ({len(chunks)}) for meaningful theme discovery")
            return []

        # Extract embeddings
        embeddings = []
        chunk_ids = []
        chunk_texts = []

        for chunk in chunks:
            chunk_ids.append(chunk["id"])
            chunk_texts.append(chunk["text"])

            # Get embedding from vector store
            chunk_data = self.vector_store.get_by_id(chunk["id"])
            if chunk_data and chunk_data.get("embedding") is not None:
                embeddings.append(chunk_data["embedding"])
            else:
                logger.warning(f"Chunk {chunk['id']} missing embedding, skipping")

        if len(embeddings) < 3:
            logger.error("Not enough chunks with embeddings")
            return []

        embeddings_array = np.array(embeddings)
        logger.info(f"Clustering {len(embeddings)} chunks")

        # Determine optimal number of clusters
        if n_themes is None:
            n_themes = self._determine_optimal_clusters(
                embeddings_array,
                max_k=min(self.max_themes, len(embeddings) // 2),
            )

        # Perform clustering
        kmeans = KMeans(n_clusters=n_themes, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings_array)

        logger.info(f"Clustered into {n_themes} themes")

        # Group chunks by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(
                {
                    "id": chunk_ids[i],
                    "text": chunk_texts[i],
                }
            )

        # Filter out small clusters
        clusters = {k: v for k, v in clusters.items() if len(v) >= min_cluster_size}

        logger.info(f"Retained {len(clusters)} themes after filtering")

        # Generate theme labels using LLM
        themes = []
        for cluster_id, cluster_chunks in clusters.items():
            theme = self._label_theme(cluster_chunks, cluster_id)
            themes.append(theme)

        # Rank themes by importance
        themes = self._rank_themes(themes)

        logger.info(f"Discovered {len(themes)} themes")
        return themes

    def _determine_optimal_clusters(
        self,
        embeddings: np.ndarray,
        max_k: int,
    ) -> int:
        """
        Determine optimal number of clusters using silhouette score.

        Args:
            embeddings: Embedding matrix
            max_k: Maximum number of clusters to try

        Returns:
            Optimal number of clusters
        """
        if max_k < 2:
            return 2

        max_k = min(max_k, len(embeddings) - 1)

        best_score = -1
        best_k = 2

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)

            logger.debug(f"k={k}, silhouette={score:.3f}")

            if score > best_score:
                best_score = score
                best_k = k

        logger.info(f"Optimal number of clusters: {best_k} (score: {best_score:.3f})")
        return best_k

    def _label_theme(self, cluster_chunks: List[Dict], cluster_id: int) -> Theme:
        """
        Generate theme label using LLM.

        Args:
            cluster_chunks: List of chunk dictionaries
            cluster_id: Cluster identifier

        Returns:
            Theme object
        """
        # Sample chunks for labeling (max 5 to avoid token limits)
        sample_size = min(5, len(cluster_chunks))
        sample_chunks = cluster_chunks[:sample_size]

        # Format chunks for prompt
        chunks_text = "\n\n---\n\n".join(
            [f"Excerpt {i+1}:\n{chunk['text'][:300]}..." for i, chunk in enumerate(sample_chunks)]
        )

        # Get theme label from LLM
        try:
            system_prompt, user_prompt = self.prompt_manager.get_theme_labeling_prompt(
                chunks=chunks_text
            )

            response = self.ollama_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for consistent labels
            )

            # Debug: Log raw response
            logger.debug(f"Raw LLM response for theme labeling:\n{response}")

            # Parse response (expected format: "Theme: <label>\nDescription: <desc>")
            # Support both English and French formats
            lines = response.strip().split("\n")
            label = "Unknown Theme"
            description = None

            for line in lines:
                line_lower = line.lower()
                if line_lower.startswith("theme:") or line_lower.startswith("thème:"):
                    # Extract after the colon, handle both "Theme:" and "Thème:"
                    if ":" in line:
                        label = line.split(":", 1)[1].strip()
                elif line_lower.startswith("description:"):
                    if ":" in line:
                        description = line.split(":", 1)[1].strip()

            # If parsing failed, try to extract from response directly
            if label == "Unknown Theme" and response:
                # Try to find any meaningful text (first non-empty line)
                for line in lines:
                    line = line.strip()
                    if line and not line.lower().startswith(
                        ("analyze", "provide", "excerpts", "critical")
                    ):
                        # Remove common prefixes
                        for prefix in ["Thème:", "Theme:", "Label:", "Titre:"]:
                            if line.startswith(prefix):
                                line = line[len(prefix) :].strip()
                                break
                        if len(line) > 3 and len(line) < 100:  # Reasonable label length
                            label = line
                            break

            # Clean up label - remove markdown formatting and common prefixes
            # First, strip markdown bold markers
            label = label.replace("**", "").strip()

            # Remove common prefixes (with and without markdown)
            for prefix in ["Thème :", "Theme :", "Thème:", "Theme:", "Label:", "Titre:"]:
                if label.startswith(prefix):
                    label = label[len(prefix) :].strip()
                    break

            logger.info(f"Generated theme label: '{label}'")

        except Exception as e:
            logger.error(f"Error generating theme label: {e}")
            label = f"Theme {cluster_id + 1}"
            description = None

        # Extract keywords (most common words in chunks)
        keywords = self._extract_keywords(cluster_chunks)

        # Create Theme object
        theme = Theme(
            label=label,
            description=description,
            chunk_ids=[UUID(chunk["id"]) for chunk in cluster_chunks],
            keywords=keywords,
            importance_score=0.0,  # Will be set by ranking
        )

        return theme

    def _extract_keywords(self, cluster_chunks: List[Dict], top_k: int = 10) -> List[str]:
        """
        Extract keywords from cluster chunks.

        Args:
            cluster_chunks: List of chunk dictionaries
            top_k: Number of keywords to extract

        Returns:
            List of keywords
        """
        # Simple keyword extraction: most common words (excluding stopwords)
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
        }

        words = []
        for chunk in cluster_chunks:
            text = chunk["text"].lower()
            # Simple tokenization
            chunk_words = [w.strip(".,!?;:\"'()[]{}") for w in text.split()]
            chunk_words = [w for w in chunk_words if len(w) > 3 and w not in stopwords]
            words.extend(chunk_words)

        # Get most common
        word_counts = Counter(words)
        keywords = [word for word, count in word_counts.most_common(top_k)]

        return keywords

    def _rank_themes(self, themes: List[Theme]) -> List[Theme]:
        """
        Rank themes by importance.

        Args:
            themes: List of Theme objects

        Returns:
            Sorted list of Theme objects with importance scores
        """
        if not themes:
            return themes

        total_chunks = sum(len(theme.chunk_ids) for theme in themes)

        for theme in themes:
            # Simple ranking: based on number of chunks
            theme.importance_score = len(theme.chunk_ids) / total_chunks

        # Sort by importance (descending)
        themes.sort(key=lambda t: t.importance_score, reverse=True)

        logger.info("Themes ranked by importance")
        for i, theme in enumerate(themes, 1):
            logger.info(
                f"{i}. {theme.label}: {theme.importance_score:.2%} ({len(theme.chunk_ids)} chunks)"
            )

        return themes

    def refine_theme(
        self,
        theme: Theme,
        new_label: Optional[str] = None,
        new_description: Optional[str] = None,
    ) -> Theme:
        """
        Manually refine a theme's label or description.

        Args:
            theme: Theme to refine
            new_label: New label (optional)
            new_description: New description (optional)

        Returns:
            Updated Theme object
        """
        if new_label:
            theme.label = new_label
            logger.info(f"Updated theme label to: '{new_label}'")

        if new_description:
            theme.description = new_description

        return theme

    def merge_themes(self, themes: List[Theme], new_label: str) -> Theme:
        """
        Merge multiple themes into one.

        Args:
            themes: List of themes to merge
            new_label: Label for merged theme

        Returns:
            New merged Theme object
        """
        all_chunk_ids = []
        all_keywords = []
        merged_from = []

        for theme in themes:
            all_chunk_ids.extend(theme.chunk_ids)
            all_keywords.extend(theme.keywords)
            merged_from.append(theme.id)

        # Remove duplicate keywords
        unique_keywords = list(dict.fromkeys(all_keywords))[:10]

        merged_theme = Theme(
            label=new_label,
            description=f"Merged from {len(themes)} themes",
            chunk_ids=all_chunk_ids,
            keywords=unique_keywords,
            importance_score=len(all_chunk_ids) / self.vector_store.count(),
            merged_from=merged_from,
        )

        logger.info(f"Merged {len(themes)} themes into '{new_label}'")
        return merged_theme
