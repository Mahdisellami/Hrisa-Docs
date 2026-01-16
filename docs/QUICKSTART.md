# Quick Start Guide

Get started with Hrisa Docs in 5 minutes.

## Prerequisites

1. **Install Ollama**: https://ollama.ai/download
2. **Pull a model**:
   ```bash
   ollama pull llama3.1:latest
   ```

## Installation

```bash
# Clone repository
git clone <repo-url>
cd Document-Processing

# Install
make setup

# Run
make run
```

## Your First Project

### 1. Create Project

- Click **"Manage Projects"**
- Click **"New Project"**
- Enter name: "My First Book"
- Click **"Create"**

### 2. Add Documents

- Go to **"Source Documents"** tab
- Click **"Add"** button
- Select PDF/TXT/DOCX files
- Files appear in list

### 3. Process

- Click **"Process Documents"** button
- Wait for completion (~30s per 100 pages)
- Status shows: "Processing complete: X chunks"

### 4. Discover Themes

- Go to **"Themes"** tab
- Click **"Discover Themes"**
- Wait 1-3 minutes
- Themes appear with labels and keywords

### 5. Generate Book

- Go to **"Synthesis"** tab
- Choose settings:
  - Level: Normal
  - Format: Markdown + DOCX
  - Citations: ✓
- Click **"Start Synthesis"**
- Wait 2-5 minutes per chapter

### 6. View Results

- Go to **"Source Documents"** tab (bottom section)
- Click **"Open Folder"**
- Find your generated book!

## Tips

- **Start small**: Try with 3-5 documents first
- **Review themes**: Rename/merge themes for better results
- **Check citations**: Verify sources in generated text
- **Iterate**: Re-run synthesis with different settings if needed

## Common Commands

```bash
# Run application
make run

# Run tests
make test

# Clean data
make clean

# Reset everything
make reset
```

## Need Help?

- Full guide: `docs/USER_GUIDE.md`
- Troubleshooting: `docs/USER_GUIDE.md#troubleshooting`
- Logs: `~/.docprocessor/logs/`

## Next Steps

1. Explore Settings → Appearance (choose theme/size)
2. Try URL import: File → Import from URL
3. Extract figures: Data Update tab
4. Experiment with different LLM models

---

**Happy Synthesizing! 📚**
