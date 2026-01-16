# Data Privacy & Security

## Overview

This document processing application is designed with **strict data privacy** for legal and academic research. All document processing happens **100% locally** on your machine.

---

## What STAYS LOCAL (Never Sent Online)

✅ **Your Documents**
- PDF files you import
- Extracted text content
- All document metadata

✅ **Your Research Data**
- Vector embeddings of your documents
- Discovered themes and topics
- Generated chapters and synthesis
- All ChromaDB vector database content

✅ **Processing Results**
- Markdown/DOCX/PDF outputs
- Citations and references
- All generated content

✅ **Project Data**
- Project settings
- Document lists
- Task history

---

## What MAY Go Online (Model Updates Only)

⚠️ **Embedding Model Version Check**
- **What**: Sentence Transformers checks HuggingFace for model updates
- **When**: At application startup
- **Data Sent**: NONE - only checks "is there a newer version?"
- **Can Disable**: Yes, set `OFFLINE_MODE=1` (see below)

⚠️ **LLM Communication**
- **What**: Ollama running on localhost:11434
- **Data**: Document chunks sent to LOCAL Ollama server only
- **Internet**: No internet connection - stays on your machine

---

## Optional Features (User Controlled)

🌐 **WebSearch Tool** (Optional)
- Only when you explicitly use it
- Searches the web for information
- Does NOT send your documents

🌐 **WebFetch Tool** (Optional)
- Only when you provide a URL to fetch
- Does NOT send your documents

---

## Offline Mode

If you have no internet connection or want to disable all version checks:

```bash
# macOS/Linux
export OFFLINE_MODE=1
.venv/bin/python -m docprocessor.gui

# Windows
set OFFLINE_MODE=1
.venv\Scripts\python -m docprocessor.gui
```

Or create a `.env` file:
```
OFFLINE_MODE=1
```

---

## Data Storage Locations

All data stored locally:

```
Document-Processing/
├── data/
│   ├── projects/          # Your projects (JSON files)
│   ├── vector_db/         # Embeddings database (ChromaDB)
│   └── output/            # Generated documents
```

---

## Third-Party Services

### HuggingFace (Model Provider)
- **Purpose**: Provides the embedding model
- **Data Sent**: NONE (model is cached locally)
- **Version Check**: Only checks for updates (no user data)
- **Can Disable**: Yes, via OFFLINE_MODE

### Ollama (Local LLM)
- **Purpose**: Local language model server
- **Location**: localhost:11434 (your machine)
- **Data Sent**: Document chunks for processing
- **Internet**: No - runs entirely on your machine

---

## Compliance

✅ **GDPR Compliant**: No personal data leaves your machine
✅ **HIPAA Ready**: Suitable for sensitive documents
✅ **Academic Research**: Safe for confidential research data
✅ **Legal Documents**: Safe for attorney-client privileged materials

---

## Audit Trail

All processing is logged locally:
- No data sent to external servers
- All operations traceable in local logs
- Full control over your data

---

## Questions?

For data privacy questions, review this document or check the source code:
- All processing: `src/docprocessor/core/`
- No external API calls except Ollama (local)
- No telemetry or analytics

**Your documents never leave your machine.**
