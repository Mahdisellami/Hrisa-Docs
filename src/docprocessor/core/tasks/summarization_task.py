"""Summarization/Synthesis Task implementation.

This task wraps the existing document synthesis functionality
in the new Task abstraction framework.

## Integration Architecture

This task integrates several core components:

1. **ThemeAnalyzer**: Discovers semantic themes from document corpus using
   clustering and LLM-based labeling

2. **SynthesisEngine**: Generates coherent chapters from themes using RAG
   (Retrieval-Augmented Generation):
   - Plans logical chapter sequence
   - Generates chapter outlines
   - Produces detailed content with citations

3. **OutputFormatter**: Exports generated content to multiple formats
   (Markdown, DOCX, PDF)

## Workflow

```
Documents → Theme Discovery → Chapter Planning → Chapter Generation → Export
    ↓              ↓                  ↓                    ↓              ↓
VectorStore   ThemeAnalyzer    SynthesisEngine      RAGPipeline    OutputFormatter
```

## Usage

```python
task = SummarizationTask(project_name="my_project")
config = task.get_default_config()
config.set("synthesis_level", "high")
config.set("output_format", "markdown+docx")

result = task.execute(
    inputs=[],  # Uses all documents in project
    config=config,
    progress_callback=lambda p, m: print(f"{p}%: {m}")
)
```

## Progress Reporting

- 0-10%: Initialization
- 10-30%: Theme discovery
- 30-40%: Preparing synthesis
- 40-80%: Generating chapters (incremental updates)
- 80-90%: Exporting to files
- 90-100%: Finalizing
"""

from datetime import datetime
from typing import Any, Callable, List, Optional

from ...utils.logger import get_logger
from ..embedder import Embedder
from ..output_formatter import OutputFormatter
from ..synthesis_engine import SynthesisEngine
from ..task_base import Task, TaskCategory, TaskConfig, TaskResult, TaskStatus
from ..theme_analyzer import ThemeAnalyzer
from ..vector_store import VectorStore

logger = get_logger(__name__)


class SummarizationTask(Task):
    """Task for synthesizing/summarizing multiple documents into a cohesive output.

    This is the original core functionality of the application, now
    wrapped as a Task in the multi-task architecture.
    """

    def __init__(self, project_name: str):
        """Initialize the summarization task.

        Args:
            project_name: Name of the project (for vector store collection)
        """
        super().__init__()
        self.project_name = project_name

        # Initialize components (lazy initialization)
        self._vector_store = None
        self._embedder = None
        self._theme_analyzer = None
        self._synthesis_engine = None
        self._output_formatter = None

    def _get_vector_store(self) -> VectorStore:
        """Get or create vector store instance."""
        if self._vector_store is None:
            self._vector_store = VectorStore(collection_name=self.project_name)
        return self._vector_store

    def _get_embedder(self) -> Embedder:
        """Get or create embedder instance."""
        if self._embedder is None:
            self._embedder = Embedder()
        return self._embedder

    def _get_theme_analyzer(self) -> ThemeAnalyzer:
        """Get or create theme analyzer instance."""
        if self._theme_analyzer is None:
            self._theme_analyzer = ThemeAnalyzer(vector_store=self._get_vector_store())
        return self._theme_analyzer

    def _get_synthesis_engine(self) -> SynthesisEngine:
        """Get or create synthesis engine instance."""
        if self._synthesis_engine is None:
            self._synthesis_engine = SynthesisEngine(
                vector_store=self._get_vector_store(), embedder=self._get_embedder()
            )
        return self._synthesis_engine

    def _get_output_formatter(self) -> OutputFormatter:
        """Get or create output formatter instance."""
        if self._output_formatter is None:
            self._output_formatter = OutputFormatter()
        return self._output_formatter

    @property
    def name(self) -> str:
        return "summarize"

    @property
    def display_name(self) -> str:
        return "Summarize & Synthesize"

    @property
    def description(self) -> str:
        return (
            "Generate a comprehensive synthesis from multiple documents "
            "using RAG (Retrieval-Augmented Generation). Automatically discovers "
            "themes, organizes content, and creates a coherent narrative with citations."
        )

    @property
    def category(self) -> TaskCategory:
        return TaskCategory.GENERATION

    @property
    def icon(self) -> str:
        return "📚"

    # ========== Requirements ==========

    @property
    def input_types(self) -> List[str]:
        return ["document_collection", "pdf"]

    @property
    def output_types(self) -> List[str]:
        return ["markdown", "docx", "pdf"]

    @property
    def requires_llm(self) -> bool:
        return True

    @property
    def requires_embeddings(self) -> bool:
        return True

    @property
    def min_inputs(self) -> int:
        return 1  # At least one document

    # ========== Configuration ==========

    def get_default_config(self) -> TaskConfig:
        """Default synthesis configuration."""
        config = TaskConfig()

        # Theme discovery
        config.set("num_themes", None)  # Auto-detect
        config.set("auto_detect_themes", True)

        # Synthesis parameters
        config.set("synthesis_level", "normal")  # low, normal, high
        config.set("chunks_per_chapter", 150)

        # Output parameters
        config.set("output_format", "markdown+docx")  # markdown, docx, pdf, all
        config.set("include_citations", True)

        # Document metadata
        config.set("title", "Synthesized Document")
        config.set("author", None)

        return config

    def validate_config(self, config: TaskConfig) -> tuple[bool, Optional[str]]:
        """Validate configuration parameters."""

        # Validate synthesis level
        synthesis_level = config.get("synthesis_level", "normal")
        if synthesis_level not in ["low", "normal", "high"]:
            return (
                False,
                f"Invalid synthesis_level: {synthesis_level}. Must be 'low', 'normal', or 'high'",
            )

        # Validate chunks per chapter
        chunks = config.get("chunks_per_chapter", 150)
        if not isinstance(chunks, int) or chunks < 10 or chunks > 1000:
            return False, f"chunks_per_chapter must be between 10 and 1000, got {chunks}"

        # Validate num_themes if specified
        num_themes = config.get("num_themes")
        if num_themes is not None:
            if not isinstance(num_themes, int) or num_themes < 2 or num_themes > 20:
                return False, f"num_themes must be between 2 and 20, got {num_themes}"

        # Validate output format
        output_format = config.get("output_format", "markdown+docx")
        valid_formats = ["markdown", "docx", "pdf", "markdown+docx", "all"]
        if output_format not in valid_formats:
            return False, f"Invalid output_format: {output_format}. Must be one of {valid_formats}"

        return True, None

    # ========== Input Validation ==========

    def validate_inputs(self, inputs: List[Any]) -> tuple[bool, Optional[str]]:
        """Validate that we have documents to process."""

        if not inputs or len(inputs) == 0:
            return False, "At least one document is required for summarization"

        # Check that documents have been processed (have embeddings)
        # This would check the actual document objects in real implementation
        # For now, just validate we have inputs

        return True, None

    # ========== Execution ==========

    def execute(
        self,
        inputs: List[Any],
        config: TaskConfig,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> TaskResult:
        """Execute the summarization task.

        This wraps the existing synthesis workflow:
        1. Discover themes (if not already done)
        2. Generate synthesis from themes
        3. Export to requested formats

        Args:
            inputs: List of documents (or document IDs) to synthesize
            config: Task configuration
            progress_callback: Progress reporting callback

        Returns:
            TaskResult with generated files and metadata
        """
        started_at = datetime.now()

        try:
            # Report starting
            self.report_progress(0, "Starting synthesis...", progress_callback)

            # Validate inputs
            is_valid, error_msg = self.validate_inputs(inputs)
            if not is_valid:
                return self.create_result(
                    status=TaskStatus.FAILED, started_at=started_at, error_message=error_msg
                )

            # Validate config
            is_valid, error_msg = self.validate_config(config)
            if not is_valid:
                return self.create_result(
                    status=TaskStatus.FAILED, started_at=started_at, error_message=error_msg
                )

            # Phase 1: Theme Discovery (if needed)
            self.report_progress(10, "Discovering themes...", progress_callback)

            if self.is_cancelled():
                return self.create_result(status=TaskStatus.CANCELLED, started_at=started_at)

            # Discover themes from documents
            themes = self._discover_themes(inputs, config)
            logger.info(f"Discovered {len(themes)} themes")
            self.report_progress(30, f"Discovered {len(themes)} themes", progress_callback)

            if len(themes) == 0:
                return self.create_result(
                    status=TaskStatus.FAILED,
                    started_at=started_at,
                    error_message="No themes discovered from documents",
                )

            # Phase 2: Generate Synthesis
            self.report_progress(40, "Generating synthesis...", progress_callback)

            if self.is_cancelled():
                return self.create_result(status=TaskStatus.CANCELLED, started_at=started_at)

            # Generate chapters from themes
            chapters = self._generate_chapters(themes, config, progress_callback)
            logger.info(f"Generated {len(chapters)} chapters")
            self.report_progress(80, f"Generated {len(chapters)} chapters", progress_callback)

            if len(chapters) == 0:
                return self.create_result(
                    status=TaskStatus.FAILED,
                    started_at=started_at,
                    error_message="No chapters generated",
                )

            # Phase 3: Export
            self.report_progress(90, "Exporting documents...", progress_callback)

            # Export to requested formats
            output_files = self._export_synthesis(chapters, config)
            logger.info(f"Exported to {len(output_files)} files")

            self.report_progress(100, "Synthesis complete!", progress_callback)

            # Calculate total word count
            total_words = sum(chapter.word_count for chapter in chapters)

            # Return result
            return self.create_result(
                status=TaskStatus.COMPLETED,
                started_at=started_at,
                output_data={
                    "num_themes": len(themes),
                    "num_chapters": len(chapters),
                    "word_count": total_words,
                },
                output_files=output_files,
                metadata={
                    "synthesis_level": config.get("synthesis_level"),
                    "include_citations": config.get("include_citations"),
                    "themes": [
                        {"label": t.label, "importance": t.importance_score} for t in themes
                    ],
                },
            )

        except Exception as e:
            return self.create_result(
                status=TaskStatus.FAILED, started_at=started_at, error_message=str(e)
            )

    # ========== Helper Methods ==========

    def _discover_themes(self, documents, config):
        """Discover themes from documents.

        Args:
            documents: List of document IDs or paths
            config: Task configuration

        Returns:
            List of Theme objects
        """
        theme_analyzer = self._get_theme_analyzer()

        # Get configuration
        num_themes = config.get("num_themes")
        auto_detect = config.get("auto_detect_themes", True)

        if auto_detect:
            num_themes = None  # Let analyzer auto-detect

        # Discover themes
        themes = theme_analyzer.discover_themes(n_themes=num_themes)

        return themes

    def _generate_chapters(self, themes, config, progress_callback):
        """Generate chapters from themes.

        Args:
            themes: List of Theme objects
            config: Task configuration
            progress_callback: Progress reporting callback

        Returns:
            List of Chapter objects
        """
        synthesis_engine = self._get_synthesis_engine()

        # Plan chapter sequence
        ordered_themes = synthesis_engine.plan_chapters(themes)

        # Get configuration
        synthesis_level = config.get("synthesis_level", "normal")
        chunks_per_chapter = config.get("chunks_per_chapter", 150)

        # Map synthesis level to target word count
        target_length_map = {
            "low": 1000,  # Shorter chapters
            "normal": 1500,  # Standard length
            "high": 2500,  # Longer, more detailed chapters
        }
        target_length = target_length_map.get(synthesis_level, 1500)

        # Generate chapters
        chapters = []
        previous_summary = None

        for i, theme in enumerate(ordered_themes, 1):
            if self.is_cancelled():
                break

            # Report progress for this chapter
            progress = 40 + int((i / len(ordered_themes)) * 40)  # 40-80%
            self.report_progress(
                progress,
                f"Generating chapter {i}/{len(ordered_themes)}: {theme.label}",
                progress_callback,
            )

            # Generate chapter
            chapter = synthesis_engine.generate_chapter(
                theme=theme,
                chapter_number=i,
                target_length=target_length,
                previous_chapter_summary=previous_summary,
                max_chunks=chunks_per_chapter,
            )

            chapters.append(chapter)

            # Update previous summary for next chapter
            # (simple summary: first 200 words)
            words = chapter.content.split()[:200]
            previous_summary = " ".join(words) + "..."

        return chapters

    def _export_synthesis(self, chapters, config):
        """Export synthesis to files.

        Args:
            chapters: List of Chapter objects
            config: Task configuration

        Returns:
            List of output file paths
        """
        output_formatter = self._get_output_formatter()

        # Get configuration
        output_format = config.get("output_format", "markdown+docx")
        include_citations = config.get("include_citations", True)
        title = config.get("title", "Synthesized Document")
        author = config.get("author")

        # Parse output format (can be comma or plus separated)
        formats = output_format.replace("+", ",").split(",")
        formats = [f.strip().lower() for f in formats]

        # Handle "all" format
        if "all" in formats:
            formats = ["markdown", "docx", "pdf"]

        # Generate output files
        output_files = []

        # Base filename (timestamp for uniqueness)
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{title.replace(' ', '_')}_{timestamp}"

        for format_type in formats:
            try:
                if format_type == "markdown":
                    output_path = output_formatter.export_markdown(
                        chapters=chapters,
                        filename=f"{base_filename}.md",
                        title=title,
                        author=author,
                        include_citations=include_citations,
                    )
                    output_files.append(str(output_path))

                elif format_type == "docx":
                    output_path = output_formatter.export_docx(
                        chapters=chapters,
                        filename=f"{base_filename}.docx",
                        title=title,
                        author=author,
                        include_citations=include_citations,
                    )
                    output_files.append(str(output_path))

                elif format_type == "pdf":
                    output_path = output_formatter.export_pdf(
                        chapters=chapters,
                        filename=f"{base_filename}.pdf",
                        title=title,
                        author=author,
                        include_citations=include_citations,
                    )
                    output_files.append(str(output_path))

            except Exception as e:
                logger.error(f"Failed to export as {format_type}: {e}")
                # Continue with other formats

        return output_files
