# Sample Documents for Testing

This document provides sources for obtaining sample PDF documents to test the document processing system.

## Option 1: Create a Simple Test PDF

Use the included script to generate a simple test PDF:

```bash
python scripts/create_sample_pdf.py
```

This will create a sample PDF in `data/sample_documents/test_document.pdf`

## Option 2: Public Legal/Academic Papers

### ArXiv (Scientific Papers)
- **URL**: https://arxiv.org
- **How to**: Search for papers and click "PDF" button
- **Good for**: Testing with academic papers
- **Example topics**: "artificial intelligence law", "legal theory"

### SSRN (Social Science Research Network)
- **URL**: https://www.ssrn.com
- **How to**: Search for legal papers and download PDFs
- **Good for**: Law research papers
- **Focus**: Legal scholarship, social science

### Google Scholar
- **URL**: https://scholar.google.com
- **How to**: Search for papers, many have free PDF links
- **Good for**: Academic and legal research
- **Tip**: Add "filetype:pdf" to your search

### Supreme Court Opinions (US)
- **URL**: https://www.supremecourt.gov/opinions/opinions.aspx
- **How to**: Download recent opinions as PDFs
- **Good for**: Legal documents, court opinions
- **Format**: Well-structured legal documents

### European Court of Human Rights
- **URL**: https://hudoc.echr.coe.int
- **How to**: Search cases and download judgments
- **Good for**: International law documents

## Option 3: Download Examples

Here are some direct examples of freely available legal PDFs:

### Sample URLs (copy and paste in browser):

1. **UN Documents**:
   - Universal Declaration of Human Rights
   - https://www.un.org/en/about-us/universal-declaration-of-human-rights (look for PDF)

2. **Public Domain Books**:
   - Project Gutenberg legal texts
   - https://www.gutenberg.org/ebooks/search/?query=law

3. **Creative Commons Papers**:
   - Many academic journals offer CC-licensed papers

## Recommended Test Set

For comprehensive testing, we recommend:

1. **Short document** (5-10 pages): Test basic functionality
2. **Medium document** (20-50 pages): Test chunking and theme discovery
3. **Long document** (100+ pages): Test performance and memory
4. **Multiple documents** (3-5 papers): Test synthesis across documents

## Storage Location

Place your test PDFs in:
```
data/sample_documents/
```

This directory is gitignored and won't be committed to version control.

## Quick Test Command

Once you have a PDF:

```bash
# Test PDF processing only
python scripts/test_pdf_processing.py data/sample_documents/your_paper.pdf -v

# Test full pipeline (processing + embedding + vector storage)
python scripts/test_vector_store.py data/sample_documents/your_paper.pdf

# Test with search query
python scripts/test_vector_store.py data/sample_documents/your_paper.pdf -q "legal theory"
```

## Notes

- Ensure PDFs are text-based (not scanned images)
- Check licensing before using for anything beyond testing
- For legal research, focus on public domain or openly licensed materials
