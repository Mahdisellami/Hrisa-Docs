# Hrisa Docs - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Core Workflow](#core-workflow)
5. [Features](#features)
6. [Settings](#settings)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Introduction

**Hrisa Docs** is a desktop application designed to help researchers consolidate multiple PDF documents (publications, papers, articles) into a synthesized book or manuscript using AI-powered analysis.

### Key Features

- **Local Processing**: All operations run locally using Ollama (no cloud dependencies)
- **Multi-format Support**: PDF, TXT, DOCX
- **Automatic Theme Discovery**: AI identifies key themes across documents
- **Intelligent Synthesis**: Generate coherent chapters with citations
- **Multilingual**: French, English, and Arabic support
- **Accessible**: Multiple size profiles for different needs

### Use Cases

- Legal researchers compiling case law into books
- Academics synthesizing literature reviews
- Writers consolidating research materials
- Anyone needing to organize and synthesize large document collections

---

## Installation

### Prerequisites

1. **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
2. **Ollama** - [Install Ollama](https://ollama.ai/download)
   ```bash
   # After installing Ollama, pull a model:
   ollama pull llama3.1:latest
   ```

### Installation Steps

#### Option 1: From Source

```bash
# Clone the repository
git clone <repository-url>
cd Document-Processing

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the application
docprocessor
```

#### Option 2: Using Make (macOS/Linux)

```bash
make setup    # Install dependencies
make run      # Run the application
```

#### Option 3: Pre-built Installer (Coming Soon)

- **macOS**: Download `.dmg` file
- **Windows**: Download `.exe` installer

---

## Getting Started

### First Launch

1. **Start the application**:
   ```bash
   docprocessor
   # or
   make run
   ```

2. **Create your first project**:
   - Click "Manage Projects"
   - Click "New Project"
   - Enter project name and description
   - Click "Create"

3. **Configure settings** (optional):
   - Go to Settings tab
   - Set UI language (French/English/Arabic)
   - Choose appearance (Settings → Appearance)

### Quick Start Workflow

```
Import Documents → Process → Discover Themes → Generate Synthesis → Export
```

---

## Core Workflow

### Step 1: Import Documents

#### From Files

1. Go to **Source Documents** tab
2. Click **Add** button
3. Select PDF/TXT/DOCX files
4. Documents appear in the list with file size and page count

#### From URLs

1. Go to **File** menu → **Import from URL**
2. Enter URLs (one per line or comma-separated)
3. Configure download settings:
   - Content type filter
   - OCR for scanned PDFs (optional)
4. Click **Import**

**Tip**: You can import multiple documents at once.

---

### Step 2: Process Documents

1. Ensure documents are loaded (check "Source Documents" tab)
2. Click **Process Documents** button
3. Wait for processing to complete:
   - Text extraction from PDFs
   - Text chunking (semantic paragraphs)
   - Embedding generation (vector representations)
   - Storage in vector database

**Processing Time**: ~30 seconds per 100-page document

**Status Messages**:
- "Processing..." - In progress
- "Processing complete: X chunks" - Success
- "Processing failed" - Error (check logs)

---

### Step 3: Discover Themes

1. Go to **Themes** tab
2. Click **Discover Themes** button
3. Configure discovery:
   - **Number of themes**: 2-20 (or auto-detect)
   - Theme discovery uses AI to cluster related content
4. Wait for discovery to complete (1-3 minutes)

**Results**:
- Each theme shows:
  - Theme label (AI-generated)
  - Number of chunks
  - Importance score (%)
  - Keywords

**Theme Management**:
- **Rename**: Click theme → Rename button
- **Merge**: Select 2+ themes → Merge button
- **Delete**: Select theme → Delete button
- **Reorder**: Drag and drop themes to change chapter order

---

### Step 4: Generate Synthesis

1. Go to **Synthesis** tab
2. Review theme configuration
3. Configure synthesis settings:
   - **Synthesis level**: Short / Normal / Comprehensive
   - **Chunks per chapter**: 50-300 (controls chapter length)
   - **Output format**: Markdown / DOCX / PDF / All
   - **Include citations**: ✓ (recommended)
4. Click **Start Synthesis**

**Generation Time**: ~2-5 minutes per chapter (depends on Ollama model)

**Output**:
- Chapters generated from each theme
- Citations to source documents
- Coherent narrative connecting ideas
- Available in configured formats

---

### Step 5: Export Results

**Generated files location**: `data/output/`

**Output Formats**:

1. **Markdown (.md)**:
   - Plain text with formatting
   - Easy to edit
   - Compatible with any text editor

2. **DOCX (.docx)**:
   - Microsoft Word format
   - Preserves formatting
   - Ready for further editing

3. **PDF (.pdf)** (if enabled):
   - Final publication format
   - Professional appearance

**Accessing Files**:
- Go to **Source Documents** tab (bottom section)
- Click **Refresh** to see new files
- Click **Open** to view file
- Click **Open Folder** to browse all outputs

---

## Features

### Project Management

**Create Project**:
- Organize work into separate projects
- Each project has its own documents, themes, and outputs

**Project Settings**:
- Name and description
- LLM model selection
- Processing parameters
- Output preferences

**Switch Projects**:
- Click dropdown at top: "Current Project"
- Select from list
- Last used project loads automatically on restart

---

### Document Management

**Supported Formats**:
- **PDF**: Native and scanned (with OCR)
- **TXT**: Plain text files
- **DOCX**: Microsoft Word documents

**Document Information**:
- Filename
- File size
- Page count (for PDFs)
- Processing status

**Remove Documents**:
- Select document(s)
- Click "Remove" button
- Note: Removes from project, doesn't delete file

---

### Theme Analysis

**How It Works**:
1. Chunks embedded using sentence transformers
2. Clustering algorithm groups similar content
3. LLM generates meaningful labels
4. Themes ranked by importance

**Best Practices**:
- Use 5-10 themes for most projects
- Enable auto-detect for optimal number
- Rename themes for clarity
- Merge overly similar themes
- Delete irrelevant themes

**Theme Quality**:
- Good themes = coherent, distinct topics
- Poor themes = mixed content, unclear labels
- Solution: Adjust theme count or re-run discovery

---

### Synthesis Engine

**Synthesis Levels**:

1. **Short** (2-3 pages/chapter):
   - Quick summaries
   - Key points only
   - Good for overviews

2. **Normal** (5-7 pages/chapter):
   - Balanced coverage
   - Main ideas + details
   - Recommended default

3. **Comprehensive** (10-15 pages/chapter):
   - In-depth analysis
   - All relevant information
   - Academic/publication quality

**Citations**:
- Automatically tracks source documents
- Footnotes or inline citations
- Page numbers when available

**Caching**:
- Generated synthesis cached for reuse
- Cache cleared when:
  - Documents added/removed
  - Themes modified
  - Settings changed

---

### Figure & Data Extraction

1. Go to **Data Update** tab
2. Click **Extract Figures from Document**
3. System extracts:
   - Numbers (currency, percentages, dates)
   - Tables (basic extraction)
   - Statistics

**Use Case**: Extract data points for analysis before synthesis

---

## Settings

### Appearance Settings

**Access**: Settings → Appearance

**Theme**:
- **Dark**: Reduces eye strain, saves battery (OLED)
- **Light**: High contrast, traditional appearance

**Size Profile**:
- **Small**: Compact interface, maximizes space
- **Medium**: Balanced, comfortable for most users
- **Large**: Improved readability, accessibility focus

**Note**: Restart application for full effect

---

### Language Settings

**Access**: Settings tab

**UI Language**:
- French (Français)
- English
- Arabic (العربية)

**Pipeline Language**:
- Controls theme labels and synthesis output language
- "Auto-detect" uses document language

**Note**: UI language requires restart

---

### System Settings

**Ollama Model**:
- Default: `llama3.1:latest`
- Change in project settings or config file
- Supported models: Any Ollama-compatible LLM

**Vector Store**:
- ChromaDB (embedded)
- Location: `~/.docprocessor/vector_db/`

**Output Directory**:
- Default: `data/output/`
- Configurable in project settings

---

## Troubleshooting

### Common Issues

#### "Ollama not found" or Connection Error

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not installed, install Ollama from https://ollama.ai
# Then pull a model:
ollama pull llama3.1:latest

# Start Ollama service (usually automatic)
```

---

#### Processing Hangs or Fails

**Causes**:
- Corrupted PDF
- Very large file (>100MB)
- Insufficient memory

**Solutions**:
1. Try processing fewer documents at once
2. Check PDF can be opened normally
3. Restart application
4. Check logs: `~/.docprocessor/logs/`

---

#### Theme Discovery Returns No Results

**Causes**:
- Too few documents (need 3+)
- Documents too short
- All documents on same topic

**Solutions**:
1. Add more documents
2. Reduce number of themes requested
3. Enable auto-detect

---

#### Synthesis Takes Too Long

**Causes**:
- Large number of chunks per chapter
- Slow LLM model
- CPU-only processing

**Solutions**:
1. Reduce synthesis level (use "Short")
2. Reduce chunks per chapter
3. Use faster Ollama model
4. Enable GPU acceleration (if available)

---

#### Language Settings Don't Apply

**Solution**:
1. Settings tab → Choose language
2. Click "Apply Settings"
3. **Restart application**
4. Check `~/.docprocessor/preferences.json` saved correctly

---

### Log Files

**Location**: `~/.docprocessor/logs/`

**View logs**:
```bash
# Latest log
tail -f ~/.docprocessor/logs/docprocessor.log

# Search for errors
grep ERROR ~/.docprocessor/logs/docprocessor.log
```

---

## FAQ

### How much disk space do I need?

- **Application**: ~500MB (with dependencies)
- **Per project**: 10MB-500MB (depends on documents)
- **Vector database**: ~1MB per 100 pages processed

### Can I use cloud LLMs instead of Ollama?

Currently, the application is designed for local Ollama models. Cloud API support (OpenAI, Anthropic) could be added as a feature request.

### How accurate is the synthesis?

Accuracy depends on:
- Quality of source documents
- Appropriate theme discovery
- LLM model quality (larger models = better)
- Synthesis level chosen

Always review and edit generated content.

### Can I edit themes manually?

Yes! After discovery:
- Rename themes for clarity
- Merge similar themes
- Delete irrelevant themes
- Reorder for logical flow

### Does it work offline?

Yes, completely offline once Ollama models are downloaded. No internet connection needed for processing or synthesis.

### What about privacy?

All processing is local. No data sent to cloud services. Documents and generated content stay on your machine.

### Can I export just one chapter?

Currently, export generates all chapters. You can:
1. Open output file
2. Extract desired chapter manually
3. Or generate synthesis with only desired themes selected

### How do I update the application?

```bash
# From source
git pull origin main
pip install -e . --upgrade

# Pre-built installer: Download new version
```

### How do I cite this tool in my work?

```
Hrisa Docs v0.1.0. Open-source document synthesis tool.
Available at: [repository URL]
```

---

## Support

### Getting Help

- **Issues**: Create an issue in the repository
- **Documentation**: Check `docs/` folder
- **Logs**: See `~/.docprocessor/logs/` for debugging

### Contributing

Contributions welcome! See `CONTRIBUTING.md` for guidelines.

---

## Appendix

### Keyboard Shortcuts

- **Ctrl+N**: New Project
- **Ctrl+O**: Open Project
- **Ctrl+D**: Process Documents
- **Ctrl+T**: Discover Themes
- **Ctrl+S**: Start Synthesis
- **Ctrl+Q**: Quit

### File Structure

```
~/.docprocessor/
├── preferences.json       # User settings
├── logs/                  # Application logs
└── vector_db/            # ChromaDB storage

<project>/
├── metadata.json         # Project settings
├── documents/           # Source documents
└── output/             # Generated files
```

### Performance Tips

1. **Use SSD**: Faster than HDD for vector operations
2. **More RAM**: 8GB minimum, 16GB+ recommended
3. **GPU**: Enable for faster embeddings (if supported)
4. **Batch processing**: Process multiple docs together
5. **Model selection**: Smaller models = faster but less accurate

---

**Version**: 0.1.0
**Last Updated**: January 2026
**License**: MIT
