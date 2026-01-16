#!/usr/bin/env python3
"""
Manual Test Script - Full Workflow Validation

This script demonstrates and validates the complete document processing workflow:
1. Create sample PDFs
2. Process documents (extract, chunk, embed)
3. Discover themes
4. Generate synthesized book
5. Export to multiple formats

Run with: .venv/bin/python scripts/manual_test.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from docprocessor.core.document_processor import DocumentProcessor
from docprocessor.core.embedder import Embedder
from docprocessor.core.vector_store import VectorStore
from docprocessor.core.theme_analyzer import ThemeAnalyzer
from docprocessor.core.synthesis_engine import SynthesisEngine
from docprocessor.core.rag_pipeline import RAGPipeline
from docprocessor.core.output_formatter import OutputFormatter
from docprocessor.llm.ollama_client import OllamaClient
from docprocessor.llm.prompt_manager import PromptManager
from docprocessor.utils.logger import get_logger

logger = get_logger(__name__)

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(step_num, title):
    """Print a formatted step header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(message):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_info(message):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def create_sample_pdfs(output_dir: Path):
    """Create sample PDF files for testing."""
    print_step(1, "Creating Sample PDF Documents")

    try:
        import fitz  # PyMuPDF

        output_dir.mkdir(parents=True, exist_ok=True)

        # Sample 1: Legal Research Paper
        doc1 = fitz.open()
        page1 = doc1.new_page()

        text1 = """
        Legal Research Methodologies

        Introduction

        This paper examines various methodologies employed in legal research, focusing on
        constitutional law and international treaties. Legal scholars have developed
        sophisticated approaches to analyzing legal precedents and statutory interpretation.

        Historical Context

        The evolution of legal research methods can be traced back to the early 20th century.
        Scholars began systematically categorizing legal principles and developing frameworks
        for comparative legal analysis across different jurisdictions.

        Modern Approaches

        Contemporary legal research incorporates digital databases, computational analysis,
        and interdisciplinary approaches. Researchers now have access to vast repositories
        of legal documents and can perform sophisticated textual analysis.

        Conclusion

        The field continues to evolve with technological advancements and changing legal
        landscapes. Future research will likely incorporate artificial intelligence and
        machine learning techniques.
        """

        page1.insert_text((50, 50), text1, fontsize=11)
        doc1.save(output_dir / "sample_legal_research.pdf")
        doc1.close()
        print_success(f"Created: {output_dir / 'sample_legal_research.pdf'}")

        # Sample 2: Constitutional Law
        doc2 = fitz.open()
        page2 = doc2.new_page()

        text2 = """
        Constitutional Principles and Their Application

        Abstract

        This study explores fundamental constitutional principles and their practical
        application in modern legal systems. We examine separation of powers, judicial
        review, and fundamental rights protection.

        Separation of Powers

        The doctrine of separation of powers ensures that governmental authority is
        distributed among executive, legislative, and judicial branches. This prevents
        concentration of power and provides checks and balances.

        Judicial Review

        Courts play a crucial role in interpreting constitutional provisions and ensuring
        that legislation complies with constitutional mandates. The power of judicial
        review has evolved significantly over time.

        Fundamental Rights

        Constitutional protections for fundamental rights vary across jurisdictions but
        generally include freedoms of speech, religion, and due process. These rights
        form the cornerstone of democratic societies.
        """

        page2.insert_text((50, 50), text2, fontsize=11)
        doc2.save(output_dir / "sample_constitutional_law.pdf")
        doc2.close()
        print_success(f"Created: {output_dir / 'sample_constitutional_law.pdf'}")

        # Sample 3: International Treaties
        doc3 = fitz.open()
        page3 = doc3.new_page()

        text3 = """
        International Treaty Law: A Comprehensive Overview

        Introduction to Treaty Law

        International treaties form the backbone of international law, governing relations
        between nations and establishing frameworks for cooperation. The Vienna Convention
        on the Law of Treaties provides the fundamental rules.

        Treaty Formation

        Treaties are formed through negotiation, signature, and ratification. The process
        involves multiple stages and requires consent of participating states. Reservations
        may be made subject to certain conditions.

        Treaty Interpretation

        Interpreting treaty provisions requires consideration of ordinary meaning, context,
        and object and purpose. Supplementary means of interpretation may be used when
        necessary to clarify ambiguous terms.

        Treaty Obligations

        States parties are bound by treaty obligations under the principle pacta sunt
        servanda. Breach of treaty obligations may result in international responsibility
        and potential remedies or sanctions.
        """

        page3.insert_text((50, 50), text3, fontsize=11)
        doc3.save(output_dir / "sample_treaty_law.pdf")
        doc3.close()
        print_success(f"Created: {output_dir / 'sample_treaty_law.pdf'}")

        print_info(f"Created 3 sample PDFs in {output_dir}")
        return list(output_dir.glob("*.pdf"))

    except ImportError:
        print_error("PyMuPDF not installed. Install with: pip install pymupdf")
        return []
    except Exception as e:
        print_error(f"Error creating PDFs: {e}")
        return []


def test_document_processing(pdf_files):
    """Test PDF processing and embedding."""
    print_step(2, "Processing Documents")

    try:
        # Initialize components
        doc_processor = DocumentProcessor()
        embedder = Embedder()
        vector_store = VectorStore(collection_name="manual_test")

        all_chunks = []

        for pdf_path in pdf_files:
            print_info(f"Processing: {pdf_path.name}")

            # Process document (extract and chunk in one step)
            document, chunks = doc_processor.process_document(pdf_path)
            print_success(f"  Extracted {len(document.text_content)} characters")
            print_success(f"  Created {len(chunks)} chunks")

            # Embed and store chunks
            for i, chunk in enumerate(chunks):
                if i % 5 == 0:
                    print(f"    Embedding chunk {i+1}/{len(chunks)}...", end='\r')
                # Generate embedding and attach to chunk (convert numpy array to list)
                embedding = embedder.embed_text(chunk.text)
                chunk.embedding = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
                # Add chunk to vector store
                vector_store.add_chunk(chunk)

            print_success(f"  Stored {len(chunks)} chunks in vector store")
            all_chunks.extend(chunks)

        print_info(f"\nTotal: {len(all_chunks)} chunks processed and stored")
        return vector_store, all_chunks

    except Exception as e:
        print_error(f"Error in document processing: {e}")
        import traceback
        traceback.print_exc()
        return None, []


def test_theme_discovery(vector_store, chunks):
    """Test theme discovery."""
    print_step(3, "Discovering Themes")

    try:
        # Check Ollama availability
        try:
            ollama_client = OllamaClient()
            # Try a simple test to see if Ollama is available
            print_success("Ollama client initialized")
        except Exception as e:
            print_warning(f"Ollama initialization issue: {e}")
            print_info("Note: Theme discovery and synthesis require Ollama")
            print_info("  1. Start Ollama: ollama serve")
            print_info("  2. Pull model: ollama pull llama3.1:latest")
            return []

        # Initialize theme analyzer
        prompt_manager = PromptManager()
        theme_analyzer = ThemeAnalyzer()

        print_info("Running clustering algorithm...")
        themes = theme_analyzer.discover_themes(
            vector_store=vector_store,
            num_themes=3
        )

        print_success(f"Discovered {len(themes)} themes")

        # Display discovered themes
        print("\n" + Colors.BOLD + "Discovered Themes:" + Colors.ENDC)
        for i, theme in enumerate(themes, 1):
            print(f"\n{Colors.OKCYAN}Theme {i}: {theme.label}{Colors.ENDC}")
            print(f"  Description: {theme.description[:100]}...")
            print(f"  Chunks: {len(theme.chunk_ids)}")
            print(f"  Size: {theme.size}")

        return themes

    except Exception as e:
        print_error(f"Error in theme discovery: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_synthesis(vector_store, themes):
    """Test book synthesis."""
    print_step(4, "Synthesizing Book")

    try:
        # Initialize synthesis components
        embedder = Embedder()
        ollama_client = OllamaClient()
        prompt_manager = PromptManager()

        rag_pipeline = RAGPipeline(
            vector_store=vector_store,
            embedder=embedder,
            ollama_client=ollama_client,
            prompt_manager=prompt_manager
        )

        synthesis_engine = SynthesisEngine(
            vector_store=vector_store,
            rag_pipeline=rag_pipeline
        )

        print_info("Generating chapters...")
        chapters = []

        for i, theme in enumerate(themes, 1):
            print(f"\n{Colors.OKCYAN}Generating Chapter {i}: {theme.label}{Colors.ENDC}")

            chapter = synthesis_engine.synthesize_chapter(
                theme=theme,
                chapter_number=i,
                target_length=800
            )

            chapters.append(chapter)
            word_count = len(chapter.content.split())
            print_success(f"  Generated {word_count} words")

        print_info(f"\nTotal: {len(chapters)} chapters generated")
        return chapters

    except Exception as e:
        print_error(f"Error in synthesis: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_export(chapters):
    """Test export to multiple formats."""
    print_step(5, "Exporting Book")

    try:
        output_formatter = OutputFormatter()

        # Export to Markdown
        print_info("Exporting to Markdown...")
        md_path = output_formatter.export_markdown(
            chapters=chapters,
            title="Legal Research Synthesis",
            author="Document Processor (Test)"
        )
        print_success(f"Markdown: {md_path}")

        # Export to DOCX
        print_info("Exporting to DOCX...")
        docx_path = output_formatter.export_docx(
            chapters=chapters,
            title="Legal Research Synthesis",
            author="Document Processor (Test)"
        )
        print_success(f"DOCX: {docx_path}")

        # Print file sizes
        md_size = md_path.stat().st_size / 1024
        docx_size = docx_path.stat().st_size / 1024

        print(f"\n{Colors.BOLD}Output Files:{Colors.ENDC}")
        print(f"  Markdown: {md_path.name} ({md_size:.1f} KB)")
        print(f"  DOCX: {docx_path.name} ({docx_size:.1f} KB)")

        # Show preview
        print(f"\n{Colors.BOLD}Content Preview:{Colors.ENDC}")
        with open(md_path, 'r') as f:
            preview = f.read()[:500]
            print(preview + "...\n")

        return md_path, docx_path

    except Exception as e:
        print_error(f"Error in export: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    """Run manual test workflow."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                   DOCUMENT PROCESSOR MANUAL TEST                   ║")
    print("║                     Full Workflow Validation                       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    # Setup
    test_dir = Path("data/manual_test")
    test_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Create sample PDFs
        pdf_files = create_sample_pdfs(test_dir)
        if not pdf_files:
            print_error("Failed to create sample PDFs. Exiting.")
            return

        # Step 2: Process documents
        vector_store, chunks = test_document_processing(pdf_files)
        if not vector_store or not chunks:
            print_error("Failed to process documents. Exiting.")
            return

        # Step 3: Discover themes
        themes = test_theme_discovery(vector_store, chunks)
        if not themes:
            print_warning("Theme discovery skipped or failed.")
            print_info("To complete full test, ensure Ollama is running:")
            print_info("  1. ollama serve")
            print_info("  2. ollama pull llama3.1:latest")
            print_info("  3. Re-run this script")
            return

        # Step 4: Synthesize book
        chapters = test_synthesis(vector_store, themes)
        if not chapters:
            print_error("Failed to synthesize book. Exiting.")
            return

        # Step 5: Export
        md_path, docx_path = test_export(chapters)

        # Summary
        print_step(6, "Test Summary")
        print_success("All steps completed successfully!")
        print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
        print(f"  ✓ Processed {len(pdf_files)} PDF documents")
        print(f"  ✓ Created {len(chunks)} text chunks")
        print(f"  ✓ Discovered {len(themes)} themes")
        print(f"  ✓ Generated {len(chapters)} chapters")
        print(f"  ✓ Exported to 2 formats")

        if md_path and docx_path:
            print(f"\n{Colors.OKGREEN}📖 Open your synthesized book:{Colors.ENDC}")
            print(f"  Markdown: open {md_path}")
            print(f"  DOCX: open {docx_path}")

        print(f"\n{Colors.OKCYAN}Test data saved in: {test_dir}{Colors.ENDC}")

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
