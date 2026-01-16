"""Background worker threads for GUI operations."""

import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import QThread, pyqtSignal

from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.output_formatter import OutputFormatter
from docprocessor.core.rag_pipeline import RAGPipeline
from docprocessor.core.synthesis_engine import SynthesisEngine
from docprocessor.core.theme_analyzer import ThemeAnalyzer
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.llm.prompt_manager import PromptManager
from docprocessor.models.project import SynthesisCache
from docprocessor.utils.language_manager import get_language_manager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


def sanitize_collection_name(name: str) -> str:
    """Sanitize a name for use as ChromaDB collection name.

    ChromaDB requires:
    - 3-512 characters
    - Only alphanumeric, underscores, hyphens
    - Start and end with alphanumeric
    """
    # Replace spaces and invalid characters with underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")
    # Ensure it starts and ends with alphanumeric
    sanitized = re.sub(r"^[^a-zA-Z0-9]+", "", sanitized)
    sanitized = re.sub(r"[^a-zA-Z0-9]+$", "", sanitized)
    # Ensure minimum length
    if len(sanitized) < 3:
        sanitized = f"project_{sanitized}"
    return sanitized


class DocumentProcessingWorker(QThread):
    """Worker thread for processing documents."""

    progress = pyqtSignal(int, str)  # (percent, message)
    finished = pyqtSignal(int)  # total_chunks
    error = pyqtSignal(str)  # error_message

    def __init__(self, document_paths: List[str], project_name: str = "default"):
        super().__init__()
        self.document_paths = document_paths
        self.project_name = project_name

    def run(self):
        """Process documents in background."""
        try:
            lang_mgr = get_language_manager()
            self.progress.emit(0, lang_mgr.get("worker_initializing"))

            # Initialize components
            doc_processor = DocumentProcessor()
            embedder = Embedder()
            vector_store = VectorStore(collection_name=sanitize_collection_name(self.project_name))

            total_docs = len(self.document_paths)
            all_chunks = []

            # Process each document
            for i, doc_path in enumerate(self.document_paths):
                doc_name = Path(doc_path).name
                percent = int((i / total_docs) * 50)
                self.progress.emit(percent, lang_mgr.get("worker_processing_doc", doc_name))

                # Extract and chunk (process_document returns both)
                document, chunks = doc_processor.process_document(Path(doc_path))
                all_chunks.extend(chunks)

                logger.info(f"Processed {doc_name}: {len(chunks)} chunks")

            # Embed and store
            self.progress.emit(50, lang_mgr.get("worker_embedding_chunks", len(all_chunks)))

            for i, chunk in enumerate(all_chunks):
                if i % 10 == 0:  # Update every 10 chunks
                    percent = 50 + int((i / len(all_chunks)) * 50)
                    self.progress.emit(
                        percent, lang_mgr.get("worker_embedding_chunk", i + 1, len(all_chunks))
                    )

                # Generate embedding and attach to chunk
                embedding = embedder.embed_text(chunk.text)
                # Convert numpy array to list
                chunk.embedding = (
                    embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
                )
                # Add chunk to vector store
                vector_store.add_chunk(chunk)

            self.progress.emit(100, lang_mgr.get("worker_completed_stored", len(all_chunks)))
            self.finished.emit(len(all_chunks))

        except Exception as e:
            error_msg = f"Error processing documents: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error.emit(str(e))


class ThemeDiscoveryWorker(QThread):
    """Worker thread for discovering themes."""

    progress = pyqtSignal(int, str)  # (percent, message)
    finished = pyqtSignal(list)  # themes
    error = pyqtSignal(str)  # error_message

    def __init__(self, project_name: str = "default", num_themes: Optional[int] = None):
        super().__init__()
        self.project_name = project_name
        self.num_themes = num_themes

    def run(self):
        """Discover themes in background."""
        try:
            lang_mgr = get_language_manager()
            self.progress.emit(0, lang_mgr.get("worker_initializing"))

            # Initialize components
            vector_store = VectorStore(collection_name=sanitize_collection_name(self.project_name))
            embedder = Embedder()
            ollama_client = OllamaClient()
            prompt_manager = PromptManager()

            self.progress.emit(10, lang_mgr.get("worker_retrieving_chunks"))
            chunk_count = vector_store.count()

            if chunk_count == 0:
                raise ValueError("No chunks found. Please process documents first.")

            self.progress.emit(20, lang_mgr.get("worker_analyzing_chunks", chunk_count))

            # Initialize theme analyzer (vector_store is required parameter)
            theme_analyzer = ThemeAnalyzer(
                vector_store=vector_store,
                ollama_client=ollama_client,
                prompt_manager=prompt_manager,
            )

            self.progress.emit(40, lang_mgr.get("worker_clustering"))

            # Discover themes (n_themes not num_themes, no vector_store parameter)
            themes = theme_analyzer.discover_themes(n_themes=self.num_themes)

            self.progress.emit(100, lang_mgr.get("worker_discovered_themes", len(themes)))
            self.finished.emit([t.model_dump() for t in themes])

        except Exception as e:
            error_msg = f"Error discovering themes: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error.emit(str(e))


class SynthesisWorker(QThread):
    """Worker thread for synthesizing book."""

    progress = pyqtSignal(int, str)  # (percent, message)
    finished = pyqtSignal(str, str, str, object)  # (markdown_path, docx_path, pdf_path, cache)
    error = pyqtSignal(str)  # error_message

    def __init__(
        self,
        project_name: str = "default",
        synthesis_level: str = "normal",
        chunks_per_chapter: int = 150,
        output_format: str = "both",
        title: str = "Synthesized Document",
        author: Optional[str] = None,
    ):
        super().__init__()
        self.project_name = project_name
        self.synthesis_level = synthesis_level
        self.chunks_per_chapter = chunks_per_chapter
        self.output_format = output_format
        self.title = title
        self.author = author

    def run(self):
        """Synthesize book in background."""
        try:
            lang_mgr = get_language_manager()
            self.progress.emit(0, lang_mgr.get("worker_initializing"))

            # Initialize components with progress updates
            self.progress.emit(
                1, lang_mgr.get("worker_loading_vector_db", "Loading vector database...")
            )
            vector_store = VectorStore(collection_name=sanitize_collection_name(self.project_name))

            self.progress.emit(
                2, lang_mgr.get("worker_loading_embedding", "Loading embedding model...")
            )
            embedder = Embedder()

            self.progress.emit(4, lang_mgr.get("worker_connecting_llm", "Connecting to LLM..."))
            ollama_client = OllamaClient()

            self.progress.emit(6, lang_mgr.get("worker_loading_prompts", "Loading prompts..."))
            prompt_manager = PromptManager()

            rag_pipeline = RAGPipeline(
                vector_store=vector_store,
                embedder=embedder,
                ollama_client=ollama_client,
                prompt_manager=prompt_manager,
            )

            # SynthesisEngine only takes vector_store and rag_pipeline
            synthesis_engine = SynthesisEngine(vector_store=vector_store, rag_pipeline=rag_pipeline)

            self.progress.emit(10, lang_mgr.get("worker_loading_themes"))

            # Get themes from vector store metadata
            # For now, rediscover themes
            theme_analyzer = ThemeAnalyzer(
                vector_store=vector_store,
                ollama_client=ollama_client,
                prompt_manager=prompt_manager,
            )

            themes = theme_analyzer.discover_themes()

            self.progress.emit(20, lang_mgr.get("worker_synthesizing_chapters", len(themes)))

            # Calculate target chapter length
            total_chunks = vector_store.count()
            avg_chunk_words = 150
            total_source_words = total_chunks * avg_chunk_words

            ratio_map = {"short": 0.15, "normal": 0.30, "comprehensive": 0.50}
            ratio = ratio_map.get(self.synthesis_level, 0.30)

            target_total_words = int(total_source_words * ratio)
            target_chapter_length = target_total_words // len(themes) if themes else 1000

            # Generate chapters
            chapters = []
            for i, theme in enumerate(themes):
                percent = 20 + int((i / len(themes)) * 60)
                # Use status_writing_chapter for the main progress message
                chapter_msg = lang_mgr.get("status_writing_chapter", i + 1, len(themes))
                self.progress.emit(percent, f"{chapter_msg}: {theme.label}...")

                # Use generate_chapter with max_chunks to control synthesis density
                # More chunks = more comprehensive, fewer chunks = more condensed
                chapter = synthesis_engine.generate_chapter(
                    theme=theme,
                    chapter_number=i + 1,
                    target_length=target_chapter_length,
                    max_chunks=self.chunks_per_chapter,
                )
                chapters.append(chapter)

            self.progress.emit(80, lang_mgr.get("status_formatting_output"))

            # Export to files
            output_formatter = OutputFormatter()

            markdown_path = None
            docx_path = None
            pdf_path = None

            # Handle different output formats
            if self.output_format in ["markdown", "both", "all"]:
                self.progress.emit(80, lang_mgr.get("worker_generating_markdown"))
                markdown_path = str(
                    output_formatter.export_markdown(
                        chapters=chapters, title=self.title, author=self.author
                    )
                )

            if self.output_format in ["docx", "both", "all"]:
                self.progress.emit(85, lang_mgr.get("worker_generating_docx"))
                docx_path = str(
                    output_formatter.export_docx(
                        chapters=chapters, title=self.title, author=self.author
                    )
                )

            pdf_error = None
            if self.output_format in ["pdf", "all"]:
                self.progress.emit(90, lang_mgr.get("worker_generating_pdf"))
                try:
                    pdf_path = str(
                        output_formatter.export_pdf(
                            chapters=chapters, title=self.title, author=self.author
                        )
                    )
                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"PDF export failed: {error_msg}")
                    pdf_error = error_msg
                    # Continue with other formats if PDF fails
                    pdf_path = None

            self.progress.emit(100, lang_mgr.get("worker_synthesis_complete"))

            # Create synthesis cache
            total_words = sum(chapter.word_count for chapter in chapters)
            total_citations = sum(len(chapter.citations) for chapter in chapters)
            theme_ids = [str(theme.id) for theme in themes]

            # Convert chapters to dicts for storage
            chapters_data = []
            for chapter in chapters:
                chapter_dict = chapter.model_dump()
                # Convert UUIDs to strings
                chapter_dict["id"] = str(chapter_dict["id"])
                chapter_dict["theme_id"] = str(chapter_dict["theme_id"])
                chapter_dict["source_chunks"] = [str(c) for c in chapter_dict["source_chunks"]]
                chapters_data.append(chapter_dict)

            cache = SynthesisCache(
                chapters=chapters_data,
                generated_at=datetime.now(),
                synthesis_level=self.synthesis_level,
                theme_ids=theme_ids,
                total_words=total_words,
                total_citations=total_citations,
                config_used={
                    "synthesis_level": self.synthesis_level,
                    "chunks_per_chapter": self.chunks_per_chapter,
                    "output_format": self.output_format,
                    "title": self.title,
                    "author": self.author,
                },
            )

            # Emit finished with cache and all output paths
            self.finished.emit(markdown_path or "", docx_path or "", pdf_path or "", cache)

            # Show PDF error if it occurred (after emitting finished so synthesis is saved)
            if pdf_error:
                self.error.emit(f"PDF export failed: {pdf_error}")

        except Exception as e:
            error_msg = f"Error synthesizing book: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error.emit(str(e))


class FigureExtractionWorker(QThread):
    """Worker thread for extracting figures from documents."""

    progress = pyqtSignal(int, str)  # (percent, message)
    finished = pyqtSignal(object)  # FigureExtractionResult
    error = pyqtSignal(str)  # error_message

    def __init__(self, document_path: str):
        super().__init__()
        self.document_path = document_path

    def run(self):
        """Extract figures in background."""
        try:
            from docprocessor.core.figure_extractor import FigureExtractor

            self.progress.emit(0, "Initializing figure extractor...")

            # Create extractor
            extractor = FigureExtractor()

            self.progress.emit(20, "Loading document...")

            # Extract figures
            from pathlib import Path

            result = extractor.extract_from_document(Path(self.document_path))

            self.progress.emit(80, f"Extracted {result.total_figures} figures...")

            # Emit results
            self.progress.emit(100, "Extraction complete!")
            self.finished.emit(result)

        except Exception as e:
            error_msg = f"Error extracting figures: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error.emit(str(e))
