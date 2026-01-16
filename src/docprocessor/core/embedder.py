"""Embedding generation using Sentence Transformers."""

from typing import List, Union

import numpy as np
from sentence_transformers import SentenceTransformer

from config.settings import settings
from docprocessor.models import Chunk
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class Embedder:
    """Handles text embedding generation using Sentence Transformers."""

    def __init__(self, model_name: str = settings.embedding_model):
        """
        Initialize the embedder with a Sentence Transformer model.

        Args:
            model_name: Name of the Sentence Transformer model to use
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")

        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(
                f"Embedding model loaded successfully. Dimension: {self.embedding_dimension}"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.

        Args:
            text: Text to embed

        Returns:
            Numpy array of embeddings
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding, returning zero vector")
            return np.zeros(self.embedding_dimension)

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            show_progress: Show progress bar

        Returns:
            Numpy array of embeddings (shape: [num_texts, embedding_dim])
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return np.array([])

        logger.info(f"Generating embeddings for {len(texts)} texts")

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
            )
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def embed_chunks(
        self,
        chunks: List[Chunk],
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> List[Chunk]:
        """
        Generate embeddings for a list of Chunk objects and update them in place.

        Args:
            chunks: List of Chunk objects
            batch_size: Number of chunks to process at once
            show_progress: Show progress bar

        Returns:
            List of Chunk objects with embeddings added
        """
        if not chunks:
            logger.warning("Empty chunk list provided for embedding")
            return chunks

        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        texts = [chunk.text for chunk in chunks]

        embeddings = self.embed_batch(
            texts,
            batch_size=batch_size,
            show_progress=show_progress,
        )

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()

        logger.info(f"Successfully added embeddings to {len(chunks)} chunks")
        return chunks

    def compute_similarity(
        self,
        embedding1: Union[np.ndarray, List[float]],
        embedding2: Union[np.ndarray, List[float]],
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity score (0-1)
        """
        emb1 = np.array(embedding1) if isinstance(embedding1, list) else embedding1
        emb2 = np.array(embedding2) if isinstance(embedding2, list) else embedding2

        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
