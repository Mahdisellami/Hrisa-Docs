#!/usr/bin/env python3
"""Create a sample PDF document for testing purposes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
except ImportError:
    print("Error: reportlab is not installed")
    print("Install it with: pip install reportlab")
    sys.exit(1)

from config.settings import settings


def create_sample_legal_paper():
    """Create a sample legal research paper PDF."""
    output_dir = settings.data_dir / "sample_documents"
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = output_dir / "sample_legal_paper.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor="darkblue",
        spaceAfter=30,
        alignment=1,
    )

    story.append(Paragraph("Artificial Intelligence and Legal Ethics", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Author
    author_style = ParagraphStyle(
        "Author", parent=styles["Normal"], fontSize=12, alignment=1
    )
    story.append(Paragraph("John Doe, J.D., Ph.D.", author_style))
    story.append(Paragraph("University of Law Studies", author_style))
    story.append(Spacer(1, 0.5 * inch))

    # Abstract
    story.append(Paragraph("Abstract", styles["Heading2"]))
    abstract = """
    This paper examines the intersection of artificial intelligence and legal ethics,
    exploring how emerging AI technologies challenge traditional legal frameworks and
    ethical considerations. We analyze the implications of AI-driven decision-making
    in legal contexts, including algorithmic bias, accountability, and the role of
    human judgment in automated legal systems.
    """
    story.append(Paragraph(abstract, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Introduction
    story.append(Paragraph("1. Introduction", styles["Heading2"]))
    intro = """
    The rapid advancement of artificial intelligence (AI) has profound implications
    for the legal profession. From predictive analytics in litigation to automated
    contract review, AI systems are increasingly integrated into legal practice.
    This integration raises critical questions about professional responsibility,
    client confidentiality, and the fundamental nature of legal judgment.
    """
    story.append(Paragraph(intro, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    intro2 = """
    As legal practitioners adopt AI tools, they must navigate complex ethical terrain.
    Traditional ethical rules were developed for human actors, not algorithmic systems.
    This paper explores how established legal ethics principles apply—or fail to apply—
    in the age of artificial intelligence.
    """
    story.append(Paragraph(intro2, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 2
    story.append(Paragraph("2. AI in Legal Practice", styles["Heading2"]))
    section2 = """
    Artificial intelligence applications in law span multiple domains. Legal research
    platforms use natural language processing to analyze case law and statutes. Predictive
    analytics tools assess litigation outcomes and settlement values. Document review
    systems employ machine learning to identify relevant materials in discovery.
    """
    story.append(Paragraph(section2, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    section2b = """
    Each application presents unique ethical challenges. For example, when an AI system
    recommends a legal strategy, who bears responsibility if that strategy proves flawed?
    How should lawyers verify AI-generated research? What duty of disclosure exists when
    AI tools make errors?
    """
    story.append(Paragraph(section2b, styles["Normal"]))

    story.append(PageBreak())

    # Section 3
    story.append(Paragraph("3. Ethical Frameworks", styles["Heading2"]))
    section3 = """
    Traditional legal ethics rest on principles including competence, diligence,
    confidentiality, and zealous advocacy within legal bounds. These principles assume
    human agency and judgment. AI systems challenge these assumptions in several ways.
    """
    story.append(Paragraph(section3, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    subsection = """
    3.1 Competence: Lawyers must understand the tools they employ. With AI, this requires
    technical literacy about algorithmic decision-making, training data, and potential
    biases. Many practitioners lack this expertise, creating a competence gap.
    """
    story.append(Paragraph(subsection, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    subsection2 = """
    3.2 Accountability: When AI systems make mistakes, establishing responsibility is
    complex. Is the lawyer liable? The AI developer? The organization deploying the system?
    Traditional negligence frameworks may prove inadequate for distributed, algorithmic
    decision-making.
    """
    story.append(Paragraph(subsection2, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 4
    story.append(Paragraph("4. Algorithmic Bias and Fairness", styles["Heading2"]))
    section4 = """
    A critical concern involves algorithmic bias. AI systems learn from historical data,
    which may encode societal biases. When these systems inform legal decisions, they risk
    perpetuating discrimination. For instance, risk assessment tools in criminal justice
    have shown racial disparities, raising equal protection concerns.
    """
    story.append(Paragraph(section4, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    section4b = """
    Legal professionals have ethical duties to avoid discrimination and ensure fair
    treatment. These duties extend to the tools they employ. Lawyers must scrutinize
    AI systems for bias and understand their limitations. Blind reliance on algorithmic
    outputs violates professional obligations.
    """
    story.append(Paragraph(section4b, styles["Normal"]))

    story.append(PageBreak())

    # Section 5
    story.append(Paragraph("5. Transparency and Explainability", styles["Heading2"]))
    section5 = """
    Many AI systems operate as "black boxes," making decisions through complex,
    inscrutable processes. This opacity conflicts with legal principles of transparency
    and due process. Parties have rights to understand the basis of decisions affecting
    them, yet AI systems may resist explanation.
    """
    story.append(Paragraph(section5, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    section5b = """
    The legal profession must demand explainable AI. Systems that cannot articulate
    their reasoning should not drive legal decisions. Researchers are developing
    interpretable machine learning methods, but adoption remains limited. Legal ethics
    should prioritize transparency over efficiency.
    """
    story.append(Paragraph(section5b, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Conclusion
    story.append(Paragraph("6. Conclusion", styles["Heading2"]))
    conclusion = """
    Artificial intelligence presents both opportunities and challenges for legal ethics.
    While AI can enhance efficiency and access to justice, it also raises profound
    questions about responsibility, bias, and the nature of legal judgment. The legal
    profession must develop new ethical frameworks that account for algorithmic
    decision-making while preserving core values of justice and fairness.
    """
    story.append(Paragraph(conclusion, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    conclusion2 = """
    As AI becomes more prevalent in legal practice, ongoing dialogue among practitioners,
    ethicists, and technologists is essential. Professional rules must evolve to address
    AI-specific concerns. Education must equip lawyers with technical literacy. Only
    through proactive engagement can the legal profession harness AI's benefits while
    safeguarding ethical principles.
    """
    story.append(Paragraph(conclusion2, styles["Normal"]))

    # Build PDF
    doc.build(story)

    print(f"✓ Sample PDF created: {pdf_path}")
    print(f"  Pages: ~3")
    print(f"  Size: {pdf_path.stat().st_size:,} bytes")
    print(f"\nYou can now test with:")
    print(f"  python scripts/test_pdf_processing.py {pdf_path} -v")
    print(f"  python scripts/test_vector_store.py {pdf_path}")


if __name__ == "__main__":
    try:
        create_sample_legal_paper()
    except Exception as e:
        print(f"Error creating sample PDF: {e}")
        sys.exit(1)
