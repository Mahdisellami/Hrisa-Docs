"""Vector store wrapper for ChromaDB."""

from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from docprocessor.models import Chunk
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""

    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: Optional[Path] = None,
    ):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory for ChromaDB persistence (default: from settings)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.vector_db_dir

        logger.info(f"Initializing vector store at {self.persist_directory}")

        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        logger.info(
            f"Vector store initialized. Collection: {collection_name}, "
            f"Documents: {self.collection.count()}"
        )

    def add_chunk(self, chunk: Chunk) -> None:
        """
        Add a single chunk to the vector store.

        Args:
            chunk: Chunk object with embedding

        Raises:
            ValueError: If chunk has no embedding
        """
        if not chunk.embedding:
            raise ValueError(f"Chunk {chunk.id} has no embedding")

        self.collection.add(
            ids=[str(chunk.id)],
            embeddings=[chunk.embedding],
            documents=[chunk.text],
            metadatas=[
                {
                    "document_id": str(chunk.document_id),
                    "page_number": chunk.page_number or -1,
                    "chunk_index": chunk.chunk_index,
                    "section": chunk.section or "",
                    "token_count": chunk.token_count,
                    "theme_id": str(chunk.theme_id) if chunk.theme_id else "",
                }
            ],
        )

        logger.debug(f"Added chunk {chunk.id} to vector store")

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """
        Add multiple chunks to the vector store in batch.

        Args:
            chunks: List of Chunk objects with embeddings

        Raises:
            ValueError: If any chunk has no embedding
        """
        if not chunks:
            logger.warning("No chunks provided to add")
            return

        missing_embeddings = [c.id for c in chunks if not c.embedding]
        if missing_embeddings:
            raise ValueError(f"Chunks missing embeddings: {missing_embeddings}")

        logger.info(f"Adding {len(chunks)} chunks to vector store")

        ids = [str(chunk.id) for chunk in chunks]
        embeddings = [chunk.embedding for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "document_id": str(chunk.document_id),
                "page_number": chunk.page_number or -1,
                "chunk_index": chunk.chunk_index,
                "section": chunk.section or "",
                "token_count": chunk.token_count,
                "theme_id": str(chunk.theme_id) if chunk.theme_id else "",
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Successfully added {len(chunks)} chunks. Total: {self.collection.count()}")

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for similar chunks using embedding similarity.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filters (e.g., {"document_id": "123"})

        Returns:
            List of result dictionaries with keys: id, text, metadata, distance
        """
        logger.debug(f"Searching for {n_results} similar chunks")

        # Return empty list if collection is empty
        collection_count = self.collection.count()
        if collection_count == 0:
            logger.debug("Collection is empty, returning empty results")
            return []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection_count),
            where=where,
        )

        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                formatted_results.append(
                    {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

        logger.debug(f"Found {len(formatted_results)} results")
        return formatted_results

    def search_by_text(
        self,
        query_text: str,
        embedder,
        n_results: int = 10,
        where: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for similar chunks using text query (generates embedding first).

        Args:
            query_text: Query text
            embedder: Embedder instance to generate query embedding
            n_results: Number of results to return
            where: Optional metadata filters

        Returns:
            List of result dictionaries
        """
        logger.debug(f"Searching by text: '{query_text[:100]}...'")

        query_embedding = embedder.embed_text(query_text)
        return self.search(query_embedding.tolist(), n_results, where)

    def get_by_id(self, chunk_id: UUID) -> Optional[Dict]:
        """
        Retrieve a chunk by its ID.

        Args:
            chunk_id: Chunk UUID

        Returns:
            Dictionary with chunk data or None if not found
        """
        try:
            result = self.collection.get(
                ids=[str(chunk_id)],
                include=["embeddings", "documents", "metadatas"],
            )

            logger.debug(f"ChromaDB get result keys: {result.keys()}")
            logger.debug(f"Result IDs: {result.get('ids')}")
            logger.debug(f"Embeddings type: {type(result.get('embeddings'))}")

            if result["ids"]:
                embeddings = result.get("embeddings")

                # Check if embeddings exist properly (avoid numpy truth value ambiguity)
                if embeddings is not None and len(embeddings) > 0:
                    embedding = embeddings[0]
                else:
                    embedding = None

                logger.debug(
                    f"Extracted embedding: {embedding is not None} (length: {len(embedding) if embedding is not None else 0})"
                )

                return {
                    "id": result["ids"][0],
                    "text": result["documents"][0],
                    "metadata": result["metadatas"][0],
                    "embedding": embedding,
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving chunk {chunk_id}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def get_all_chunks(
        self,
        where: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Retrieve all chunks, optionally filtered by metadata.

        Args:
            where: Optional metadata filters
            limit: Maximum number of chunks to return

        Returns:
            List of chunk dictionaries
        """
        logger.debug("Retrieving all chunks")

        try:
            result = self.collection.get(
                where=where,
                limit=limit,
            )

            chunks = []
            if result["ids"]:
                for i in range(len(result["ids"])):
                    chunks.append(
                        {
                            "id": result["ids"][i],
                            "text": result["documents"][i],
                            "metadata": result["metadatas"][i],
                        }
                    )

            logger.debug(f"Retrieved {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []

    def delete_chunk(self, chunk_id: UUID) -> None:
        """
        Delete a chunk by ID.

        Args:
            chunk_id: Chunk UUID
        """
        self.collection.delete(ids=[str(chunk_id)])
        logger.debug(f"Deleted chunk {chunk_id}")

    def delete_by_document(self, document_id: UUID) -> None:
        """
        Delete all chunks from a specific document.

        Args:
            document_id: Document UUID
        """
        logger.info(f"Deleting all chunks from document {document_id}")
        self.collection.delete(where={"document_id": str(document_id)})

    def clear_collection(self) -> None:
        """Delete all chunks from the collection."""
        logger.warning(f"Clearing collection {self.collection_name}")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Get the number of chunks in the collection."""
        return self.collection.count()

    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        return {
            "name": self.collection_name,
            "count": self.count(),
            "persist_directory": str(self.persist_directory),
        }
