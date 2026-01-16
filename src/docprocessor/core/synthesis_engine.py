"""Synthesis engine for generating book chapters from document themes."""

from typing import Dict, List, Optional
from uuid import UUID

from docprocessor.core.embedder import Embedder
from docprocessor.core.rag_pipeline import RAGPipeline
from docprocessor.core.vector_store import VectorStore
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.llm.prompt_manager import PromptManager
from docprocessor.models import Chapter, Theme
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)


class SynthesisEngine:
    """Generates book chapters from document themes using RAG."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: Optional[Embedder] = None,
        ollama_client: Optional[OllamaClient] = None,
        prompt_manager: Optional[PromptManager] = None,
        rag_pipeline: Optional[RAGPipeline] = None,
    ):
        """
        Initialize synthesis engine.

        Args:
            vector_store: Vector store containing document chunks
            embedder: Optional embedder (creates new if not provided)
            ollama_client: Optional Ollama client (creates new if not provided)
            prompt_manager: Optional prompt manager (creates new if not provided)
            rag_pipeline: Optional RAG pipeline (creates new if not provided)
        """
        self.vector_store = vector_store
        self.embedder = embedder or Embedder()
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_manager = prompt_manager or PromptManager()
        self.rag_pipeline = rag_pipeline or RAGPipeline(
            vector_store=vector_store,
            embedder=self.embedder,
            ollama_client=self.ollama_client,
            prompt_manager=self.prompt_manager,
        )

        logger.info("SynthesisEngine initialized")

    def plan_chapters(
        self,
        themes: List[Theme],
        book_title: Optional[str] = None,
        book_objective: Optional[str] = None,
    ) -> List[Theme]:
        """
        Plan logical chapter sequence from themes.

        Uses LLM to suggest optimal ordering based on theme relationships
        and logical flow.

        Args:
            themes: List of Theme objects to organize
            book_title: Optional book title for context
            book_objective: Optional book objective for context

        Returns:
            Reordered list of Theme objects with suggested sequence
        """
        logger.info(f"Planning chapter sequence for {len(themes)} themes")

        if len(themes) <= 1:
            logger.info("Only one theme, no sequencing needed")
            return themes

        # Format themes for LLM prompt
        theme_descriptions = []
        for i, theme in enumerate(themes, 1):
            desc = f"{i}. {theme.label}"
            if theme.description:
                desc += f"\n   {theme.description}"
            desc += (
                f"\n   ({len(theme.chunk_ids)} sections, {theme.importance_score:.1%} of content)"
            )
            theme_descriptions.append(desc)

        themes_text = "\n\n".join(theme_descriptions)

        # Get sequencing prompt
        try:
            system_prompt, user_prompt = self.prompt_manager.get_chapter_sequencing_prompt(
                themes=themes_text,
            )

            response = self.ollama_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
            )

            # Parse response to get suggested order
            suggested_order = self._parse_chapter_order(response, len(themes))

            # Reorder themes based on suggestions
            if suggested_order:
                reordered_themes = [themes[i - 1] for i in suggested_order]
                logger.info(f"Reordered themes: {[t.label for t in reordered_themes]}")
                return reordered_themes
            else:
                logger.warning("Could not parse chapter order, using original sequence")
                return themes

        except Exception as e:
            logger.error(f"Error planning chapter sequence: {e}")
            logger.warning("Using original theme order")
            return themes

    def _parse_chapter_order(self, llm_response: str, num_themes: int) -> Optional[List[int]]:
        """
        Parse LLM response to extract chapter order.

        Expected format: "1. Theme X\n2. Theme Y\n3. Theme Z"

        Args:
            llm_response: LLM response text
            num_themes: Expected number of themes

        Returns:
            List of theme indices (1-based) or None if parsing fails
        """
        import re

        order = []
        lines = llm_response.strip().split("\n")

        for line in lines:
            # Look for patterns like "1. Theme" or "1) Theme" or "Chapter 1:"
            match = re.match(r"^(?:Chapter\s+)?(\d+)[.:\)]\s*(.+)", line.strip())
            if match:
                idx = int(match.group(1))
                if 1 <= idx <= num_themes:
                    order.append(idx)

        # Verify we got all themes exactly once
        if len(order) == num_themes and len(set(order)) == num_themes:
            return order

        return None

    def generate_chapter(
        self,
        theme: Theme,
        chapter_number: int,
        target_length: int = 1500,
        previous_chapter_summary: Optional[str] = None,
        max_chunks: int = 100,
    ) -> Chapter:
        """
        Generate chapter content from a theme using RAG.

        Args:
            theme: Theme to generate chapter from
            chapter_number: Chapter number in sequence
            target_length: Target word count for chapter
            previous_chapter_summary: Optional summary of previous chapter for coherence
            max_chunks: Maximum number of source chunks to use

        Returns:
            Chapter object with generated content
        """
        logger.info(f"Generating chapter {chapter_number}: '{theme.label}'")

        # Get all chunks for this theme
        theme_chunk_ids = [str(chunk_id) for chunk_id in theme.chunk_ids]
        logger.info(f"Using {len(theme_chunk_ids)} chunks for chapter content")

        # Build chapter outline first
        outline = self._generate_chapter_outline(theme, target_length)

        # Generate chapter content based on outline
        content = self._generate_chapter_content(
            theme=theme,
            outline=outline,
            target_length=target_length,
            previous_summary=previous_chapter_summary,
            max_chunks=max_chunks,
        )

        # Extract citations from content
        citations = self._extract_citations(content, theme_chunk_ids)

        # Create Chapter object
        chapter = Chapter(
            chapter_number=chapter_number,
            title=theme.label,
            content=content,
            theme_id=theme.id,
            word_count=len(content.split()),
            citations=citations,
            source_chunks=theme.chunk_ids,
            generated=True,
        )

        logger.info(
            f"Generated chapter {chapter_number}: {chapter.word_count} words, "
            f"{len(citations)} citations"
        )

        return chapter

    def _generate_chapter_outline(self, theme: Theme, target_length: int) -> str:
        """
        Generate chapter outline using LLM.

        Args:
            theme: Theme to create outline for
            target_length: Target word count

        Returns:
            Outline text
        """
        # Sample chunks from theme for context
        sample_chunks = self._sample_theme_chunks(theme, max_samples=5)

        try:
            system_prompt, user_prompt = self.prompt_manager.get_chapter_outline_prompt(
                theme=theme.label,
                chunks=sample_chunks,
            )

            outline = self.ollama_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4,
            )

            logger.debug(f"Generated outline for '{theme.label}'")
            return outline

        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            return "Overview\nMain Points\nConclusion"

    def _generate_chapter_content(
        self,
        theme: Theme,
        outline: str,
        target_length: int,
        previous_summary: Optional[str] = None,
        max_chunks: int = 100,
    ) -> str:
        """
        Generate chapter content using RAG synthesis with iterative approach.

        Args:
            theme: Theme for chapter
            outline: Chapter outline
            target_length: Target word count
            previous_summary: Optional previous chapter summary
            max_chunks: Maximum number of source chunks to use

        Returns:
            Generated chapter content
        """
        # Get all chunks for theme
        chunks = []
        for chunk_id in theme.chunk_ids[:max_chunks]:  # Limit to avoid token overflow
            chunk_data = self.vector_store.get_by_id(chunk_id)
            if chunk_data:
                chunks.append(chunk_data)

        # Split chunks into batches for iterative generation
        batch_size = max(20, max_chunks // 3)  # Use ~1/3 of chunks per section
        chunk_batches = [chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)]

        generated_sections = []
        total_words = 0
        target_per_section = target_length // max(
            3, len(chunk_batches)
        )  # Distribute target across sections

        for batch_idx, chunk_batch in enumerate(chunk_batches):
            # Build context from chunk batch
            context_parts = []
            for i, chunk in enumerate(chunk_batch, 1):
                context_parts.append(f"[{i}] {chunk['text'][:500]}...")

            context = "\n\n".join(context_parts)

            # Generate section using synthesis prompt
            try:
                system_prompt, user_prompt = self.prompt_manager.get_chapter_synthesis_prompt(
                    theme=theme.label,
                    chunks=context,
                    target_words=target_per_section,
                )

                section_content = self.ollama_client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.5,
                    max_tokens=target_per_section * 2,  # Rough token estimate
                )

                section_words = len(section_content.split())
                total_words += section_words
                generated_sections.append(section_content)

                logger.debug(
                    f"Generated section {batch_idx + 1}: {section_words} words (total: {total_words}/{target_length})"
                )

                # Continue through all batches to avoid abrupt endings
                # Only stop if we've significantly exceeded target
                if (
                    total_words >= target_length * 1.2
                ):  # 120% - allow overrun for natural completion
                    logger.debug(f"Reached {total_words} words (120% of target), stopping")
                    break

            except Exception as e:
                logger.error(f"Error generating section {batch_idx + 1}: {e}")
                continue

        # Combine sections
        if generated_sections:
            content = "\n\n".join(generated_sections)
            logger.debug(f"Generated {len(content.split())} total words for chapter")
            return content
        else:
            logger.error("Failed to generate any content")
            return f"# {theme.label}\n\n[Content generation failed]"

    def _sample_theme_chunks(self, theme: Theme, max_samples: int = 5) -> str:
        """
        Sample representative chunks from a theme.

        Args:
            theme: Theme to sample from
            max_samples: Maximum number of chunks to sample

        Returns:
            Concatenated sample text
        """
        samples = []
        chunk_ids_to_sample = list(theme.chunk_ids)[:max_samples]

        for chunk_id in chunk_ids_to_sample:
            chunk_data = self.vector_store.get_by_id(chunk_id)
            if chunk_data:
                samples.append(chunk_data["text"][:300])

        return "\n\n---\n\n".join(samples)

    def _extract_citations(self, content: str, chunk_ids: List[UUID]) -> List[Dict[str, str]]:
        """
        Extract citation references from generated content.

        Args:
            content: Generated chapter content
            chunk_ids: List of chunk IDs used

        Returns:
            List of citation dictionaries
        """
        import re

        citations = []

        # Look for citation patterns like [1], [2], etc.
        citation_refs = re.findall(r"\[(\d+)\]", content)

        for ref in set(citation_refs):
            idx = int(ref) - 1
            if 0 <= idx < len(chunk_ids):
                chunk_data = self.vector_store.get_by_id(chunk_ids[idx])
                if chunk_data and "metadata" in chunk_data:
                    metadata = chunk_data["metadata"]
                    citation = {
                        "document_id": str(metadata.get("document_id", "unknown")),
                        "page": str(metadata.get("page_number", "unknown")),
                    }
                    citations.append(citation)

        return citations

    def generate_book(
        self,
        themes: List[Theme],
        book_title: str = "Synthesized Document",
        book_objective: Optional[str] = None,
        target_chapter_length: int = 1500,
        max_chunks_per_chapter: int = 100,
    ) -> List[Chapter]:
        """
        Generate complete book from themes.

        Args:
            themes: List of themes to synthesize
            book_title: Title of the book
            book_objective: Objective or purpose of the book
            target_chapter_length: Target word count per chapter
            max_chunks_per_chapter: Maximum source chunks to use per chapter

        Returns:
            List of Chapter objects
        """
        logger.info(f"Generating book: '{book_title}' from {len(themes)} themes")

        # Step 1: Plan chapter sequence
        ordered_themes = self.plan_chapters(themes, book_title, book_objective)

        # Step 2: Generate chapters
        chapters = []
        previous_summary = None

        for i, theme in enumerate(ordered_themes, 1):
            chapter = self.generate_chapter(
                theme=theme,
                chapter_number=i,
                target_length=target_chapter_length,
                previous_chapter_summary=previous_summary,
                max_chunks=max_chunks_per_chapter,
            )
            chapters.append(chapter)

            # Generate summary for next chapter's context
            previous_summary = self._summarize_chapter(chapter)

        logger.info(
            f"Generated {len(chapters)} chapters, total words: {sum(c.word_count for c in chapters)}"
        )
        return chapters

    def _summarize_chapter(self, chapter: Chapter) -> str:
        """
        Generate brief summary of chapter for context.

        Args:
            chapter: Chapter to summarize

        Returns:
            Summary text
        """
        # Take first and last paragraphs as simple summary
        paragraphs = chapter.content.split("\n\n")
        if len(paragraphs) <= 2:
            return chapter.content[:200]

        summary = paragraphs[0][:150] + "..." + paragraphs[-1][:150]
        return summary
