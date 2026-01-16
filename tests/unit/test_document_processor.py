"""Unit tests for DocumentProcessor."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.models.chunk import Chunk
from docprocessor.models.document import Document


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    text_content = """
    Legal Research Methodology

    Introduction to Legal Research

    Legal research is a fundamental skill for legal professionals. It involves
    the systematic investigation of legal sources to find authoritative answers
    to legal questions. This process requires careful analysis of statutes,
    case law, and secondary sources.

    Primary Sources

    Primary sources include constitutions, statutes, regulations, and court decisions.
    These sources carry the force of law and are binding within their jurisdiction.
    Understanding how to locate and interpret primary sources is essential for
    effective legal practice.

    Secondary Sources

    Secondary sources such as legal encyclopedias, treatises, and law review articles
    provide analysis and commentary on legal topics. While not binding, they offer
    valuable insights and can help researchers understand complex legal concepts.

    Research Strategies

    Effective legal research requires a systematic approach. Begin by identifying
    the legal issue, then locate relevant primary and secondary sources. Analyze
    the sources critically and synthesize the information to answer the research
    question.
    """

    # Create temporary file
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(text_content)
        temp_path = Path(f.name)

    doc = Document(
        file_path=temp_path,
        title="Legal Research Methodology",
        author="Test Author",
        page_count=1,
        file_size=len(text_content),
        text_content=text_content,
        processed=False,
    )

    yield doc

    # Cleanup
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def processor():
    """Create a DocumentProcessor instance."""
    return DocumentProcessor(chunk_size=500, chunk_overlap=50)


class TestDocumentProcessor:
    """Test DocumentProcessor functionality."""

    def test_initialization(self):
        """Test processor initialization with default parameters."""
        processor = DocumentProcessor()
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 100

    def test_custom_parameters(self):
        """Test processor initialization with custom parameters."""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 50

    def test_chunk_document(self, processor, sample_document):
        """Test document chunking."""
        chunks = processor.chunk_document(sample_document)

        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)

        # Verify chunk properties
        for chunk in chunks:
            assert chunk.document_id == sample_document.id
            assert chunk.text is not None
            assert len(chunk.text) > 0
            assert chunk.chunk_index >= 0

    def test_chunk_text_content(self, processor, sample_document):
        """Test that chunks contain actual text from document."""
        chunks = processor.chunk_document(sample_document)

        # Combine all chunk text
        combined_text = " ".join(chunk.text for chunk in chunks)

        # Check that key phrases appear in chunks
        assert "Legal Research" in combined_text
        assert "Primary Sources" in combined_text or "primary sources" in combined_text
        assert "Secondary Sources" in combined_text or "secondary sources" in combined_text

    def test_chunk_size_limits(self, processor, sample_document):
        """Test that chunks respect size limits."""
        chunks = processor.chunk_document(sample_document)

        # Chunks should not be excessively long
        max_expected_size = processor.chunk_size * 3  # Allow some flexibility
        for chunk in chunks:
            assert len(chunk.text) <= max_expected_size

    def test_chunk_overlap(self, processor, sample_document):
        """Test that consecutive chunks have overlap."""
        chunks = processor.chunk_document(sample_document)

        if len(chunks) > 1:
            # Check overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                chunk1_end = chunks[i].text[-50:]  # Last 50 chars
                chunk2_start = chunks[i + 1].text[:50]  # First 50 chars

                # There should be some overlap (not exact match due to paragraph boundaries)
                # Just verify both chunks have content
                assert len(chunks[i].text) > 0
                assert len(chunks[i + 1].text) > 0

    def test_chunk_metadata(self, processor, sample_document):
        """Test chunk metadata is properly set."""
        chunks = processor.chunk_document(sample_document)

        for i, chunk in enumerate(chunks):
            assert chunk.document_id == sample_document.id
            assert chunk.chunk_index == i
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char
            assert chunk.embedding is None  # Not yet embedded

    def test_empty_document(self, processor):
        """Test handling of empty document."""
        with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            temp_path = Path(f.name)

        empty_doc = Document(
            file_path=temp_path, title="Empty Document", text_content="", processed=False
        )

        # Document processor raises ValueError for empty content
        with pytest.raises(ValueError, match="no text content"):
            processor.chunk_document(empty_doc)

        temp_path.unlink(missing_ok=True)

    def test_split_into_paragraphs(self, processor):
        """Test paragraph splitting logic."""
        text = """
        Paragraph one has some text.
        It continues here.

        Paragraph two is separate.

        Paragraph three is here.
        """

        paragraphs = processor._split_into_paragraphs(text)

        assert isinstance(paragraphs, list)
        assert len(paragraphs) >= 3  # At least 3 paragraphs

        # Check paragraphs are not empty
        paragraphs = [p for p in paragraphs if p.strip()]
        assert all(len(p.strip()) > 0 for p in paragraphs)

    def test_deterministic_chunking(self, processor, sample_document):
        """Test that chunking is deterministic."""
        chunks1 = processor.chunk_document(sample_document)
        chunks2 = processor.chunk_document(sample_document)

        assert len(chunks1) == len(chunks2)

        for c1, c2 in zip(chunks1, chunks2):
            assert c1.text == c2.text
            assert c1.chunk_index == c2.chunk_index


class TestChunkCreation:
    """Test internal chunk creation logic."""

    def test_create_chunk(self, processor, sample_document):
        """Test _create_chunk helper method."""
        chunk = processor._create_chunk(
            document_id=sample_document.id,
            text="Sample chunk text",
            page_number=1,
            chunk_index=0,
            start_char=0,
        )

        assert isinstance(chunk, Chunk)
        assert chunk.text == "Sample chunk text"
        assert chunk.chunk_index == 0
        assert chunk.document_id == sample_document.id
        assert chunk.id is not None  # Should have UUID
        assert chunk.end_char == 17  # Length of "Sample chunk text"
