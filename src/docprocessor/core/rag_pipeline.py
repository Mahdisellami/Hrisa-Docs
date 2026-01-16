"""RAG (Retrieval-Augmented Generation) pipeline."""

from typing import Dict, Iterator, List, Optional

from config.settings import settings
from docprocessor.core.embedder import Embedder
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.llm.prompt_manager import PromptManager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Orchestrates retrieval and generation for question answering."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Embedder,
        ollama_client: Optional[OllamaClient] = None,
        prompt_manager: Optional[PromptManager] = None,
        n_results: int = settings.max_retrieval_chunks,
    ):
        """
        Initialize RAG pipeline.

        Args:
            vector_store: Vector store for retrieval
            embedder: Embedder for query encoding
            ollama_client: Optional Ollama client (creates new if not provided)
            prompt_manager: Optional prompt manager (creates new if not provided)
            n_results: Number of chunks to retrieve
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.n_results = n_results

        logger.info(f"RAGPipeline initialized with n_results={n_results}")

    def retrieve(
        self,
        query: str,
        n_results: Optional[int] = None,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            n_results: Number of results (overrides default)
            filters: Optional metadata filters

        Returns:
            List of retrieved chunk dictionaries
        """
        n = n_results if n_results is not None else self.n_results

        logger.debug(f"Retrieving {n} chunks for query: '{query[:100]}...'")

        results = self.vector_store.search_by_text(
            query_text=query,
            embedder=self.embedder,
            n_results=n,
            where=filters,
        )

        logger.info(f"Retrieved {len(results)} chunks")
        return results

    def build_context(self, results: List[Dict], include_metadata: bool = True) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            results: Retrieved chunk dictionaries
            include_metadata: Include source metadata (document, page)

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, result in enumerate(results, 1):
            text = result["text"]
            metadata = result["metadata"]

            if include_metadata:
                doc_id = metadata.get("document_id", "unknown")[:8]
                page = metadata.get("page_number", "?")
                header = f"[Source {i}: Document {doc_id}, Page {page}]"
                context_parts.append(f"{header}\n{text}")
            else:
                context_parts.append(text)

        context = "\n\n---\n\n".join(context_parts)
        logger.debug(f"Built context with {len(results)} chunks, {len(context)} characters")
        return context

    def generate(
        self,
        query: str,
        context: str,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate answer using retrieved context.

        Args:
            query: User question
            context: Retrieved context
            temperature: Generation temperature
            stream: Whether to stream response

        Returns:
            Generated answer
        """
        system_prompt, user_prompt = self.prompt_manager.get_rag_prompt(
            context=context,
            question=query,
        )

        logger.debug(f"Generating answer for query: '{query[:100]}...'")

        answer = self.ollama_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            stream=stream,
        )

        logger.info(f"Generated answer: {len(answer)} characters")
        return answer

    def generate_streaming(
        self,
        query: str,
        context: str,
        temperature: Optional[float] = None,
    ) -> Iterator[str]:
        """
        Generate answer with streaming.

        Args:
            query: User question
            context: Retrieved context
            temperature: Generation temperature

        Yields:
            Answer chunks as they are generated
        """
        system_prompt, user_prompt = self.prompt_manager.get_rag_prompt(
            context=context,
            question=query,
        )

        logger.debug(f"Streaming answer for query: '{query[:100]}...'")

        for chunk in self.ollama_client.generate_streaming(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        ):
            yield chunk

    def query(
        self,
        question: str,
        n_results: Optional[int] = None,
        filters: Optional[Dict] = None,
        temperature: Optional[float] = None,
        include_sources: bool = True,
        stream: bool = False,
    ) -> Dict:
        """
        Complete RAG query: retrieve and generate.

        Args:
            question: User question
            n_results: Number of chunks to retrieve
            filters: Optional metadata filters
            temperature: Generation temperature
            include_sources: Include source information in result
            stream: Whether to stream response

        Returns:
            Dictionary with 'answer' and optionally 'sources'
        """
        logger.info(f"RAG query: '{question[:100]}...'")

        # Retrieve relevant chunks
        results = self.retrieve(question, n_results, filters)

        if not results:
            logger.warning("No relevant chunks found")
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": [] if include_sources else None,
            }

        # Build context
        context = self.build_context(results, include_metadata=True)

        # Generate answer
        answer = self.generate(question, context, temperature, stream)

        # Prepare response
        response = {"answer": answer}

        if include_sources:
            sources = []
            for result in results:
                metadata = result["metadata"]
                sources.append(
                    {
                        "document_id": metadata.get("document_id", "unknown"),
                        "page": metadata.get("page_number", None),
                        "chunk_index": metadata.get("chunk_index", None),
                        "similarity": 1 - result["distance"],
                        "text_preview": result["text"][:200] + "...",
                    }
                )
            response["sources"] = sources

        logger.info(f"Query completed with {len(results)} sources")
        return response

    def query_streaming(
        self,
        question: str,
        n_results: Optional[int] = None,
        filters: Optional[Dict] = None,
        temperature: Optional[float] = None,
    ) -> tuple[Iterator[str], List[Dict]]:
        """
        Complete RAG query with streaming.

        Args:
            question: User question
            n_results: Number of chunks to retrieve
            filters: Optional metadata filters
            temperature: Generation temperature

        Returns:
            Tuple of (answer_iterator, sources_list)
        """
        logger.info(f"RAG streaming query: '{question[:100]}...'")

        # Retrieve
        results = self.retrieve(question, n_results, filters)

        if not results:
            logger.warning("No relevant chunks found")

            def empty_generator():
                yield "I couldn't find any relevant information to answer your question."

            return empty_generator(), []

        # Build context
        context = self.build_context(results, include_metadata=True)

        # Prepare sources
        sources = []
        for result in results:
            metadata = result["metadata"]
            sources.append(
                {
                    "document_id": metadata.get("document_id", "unknown"),
                    "page": metadata.get("page_number", None),
                    "similarity": 1 - result["distance"],
                    "text_preview": result["text"][:200] + "...",
                }
            )

        # Generate streaming
        answer_iterator = self.generate_streaming(question, context, temperature)

        return answer_iterator, sources
