# Book Synthesis Parameters Guide

## Overview

The synthesis engine now supports comprehensive control over output length, depth, and format. This guide explains all available parameters and their effects.

---

## Output Size Controls

### `--chapter-length <words>`
**Target word count per chapter**
- Default: `1500`
- Recommended ranges:
  - Summary: `500-1000` words
  - Standard: `1500-2500` words
  - Comprehensive: `3000-5000` words
  - Exhaustive: `5000+` words

**Example**:
```bash
python scripts/test_synthesis.py --use-existing --chapter-length 3000
```

### `--target-words <total>`
**Target total word count for entire book** (Coming Soon)
- Will auto-adjust chapter lengths to hit target
- Example: `--target-words 50000` for a 50K word book

### `--chunks-per-chapter <number>`
**How many source chunks to use per chapter**
- Default: `100`
- Higher = more comprehensive, longer generation time
- Recommended:
  - Quick summary: `50-75` chunks
  - Standard: `100-150` chunks
  - Comprehensive: `200-300` chunks
  - Exhaustive: `300+` chunks

**Example**:
```bash
python scripts/test_synthesis.py --use-existing --chunks-per-chapter 200
```

---

## Content Depth Controls

### `--depth <level>`
**Overall content depth level** (Coming Soon)
- Choices: `summary`, `moderate`, `comprehensive`, `exhaustive`
- Default: `moderate`
- Affects:
  - Detail level in explanations
  - Number of examples
  - Citation density

**Example**:
```bash
python scripts/test_synthesis.py --use-existing --depth comprehensive
```

---

## Theme/Structure Controls

### `--n-themes <number>`
**Force specific number of themes/chapters**
- If not specified, auto-detects optimal number
- Minimum: 2
- Maximum: From settings (default 10)

**Example**:
```bash
python scripts/test_synthesis.py --use-existing --n-themes 5
```

---

## Output Format Controls

### `--format <type>`
**Output format**
- Choices: `markdown`, `docx`, `text`, `pdf`, `all`
- Default: `all`

**Formats**:
- **Markdown** (.md): Clean, readable, GitHub-compatible
- **DOCX** (.docx): Microsoft Word format, editable
- **Plain Text** (.txt): Simple text format
- **PDF** (.pdf): Professional PDF (requires pandoc)
- **All**: Generates all formats

**Example**:
```bash
python scripts/test_synthesis.py --use-existing --format pdf
```

### `--pdf-template <style>`
**PDF template style** (requires pandoc)
- Choices: `academic`, `professional`, `simple`
- Default: `academic`

**Templates**:
- **Academic**: Report format, 12pt, TOC, colored links
- **Professional**: Article format, 11pt, TOC
- **Simple**: Article format, 12pt, no TOC

**Example**:
```bash
python scripts/test_synthesis.py --use-existing --format pdf --pdf-template professional
```

---

## Complete Examples

### 1. Quick Summary Book (Small Output)
```bash
python scripts/test_synthesis.py \
  --use-existing \
  --n-themes 2 \
  --chapter-length 1000 \
  --chunks-per-chapter 50 \
  --format markdown
```

**Result**: ~2 chapters × 1000 words = ~2000 words total

---

### 2. Standard Book (Medium Output)
```bash
python scripts/test_synthesis.py \
  --use-existing \
  --n-themes 5 \
  --chapter-length 2500 \
  --chunks-per-chapter 150 \
  --format all
```

**Result**: ~5 chapters × 2500 words = ~12,500 words total

---

### 3. Comprehensive Book (Large Output)
```bash
python scripts/test_synthesis.py \
  --use-existing \
  --title "Le Bénéfice Fiscal: A Comprehensive Analysis" \
  --author "Synthesized from Salma AKROUT Thesis" \
  --n-themes 8 \
  --chapter-length 4000 \
  --chunks-per-chapter 250 \
  --format pdf \
  --pdf-template academic
```

**Result**: ~8 chapters × 4000 words = ~32,000 words total (~100 pages)

---

### 4. Maximum Detail Book (Very Large Output)
```bash
python scripts/test_synthesis.py \
  "data/customer_documents/*.pdf" \
  --title "Exhaustive Analysis" \
  --chapter-length 6000 \
  --chunks-per-chapter 400 \
  --format all
```

**Result**: Auto-detected themes, ~6000 words per chapter

---

## Cross-Platform Setup

### PDF Generation (Optional)

**macOS**:
```bash
brew install pandoc
```

**Windows**:
```powershell
# Option 1: Chocolatey
choco install pandoc

# Option 2: Winget
winget install --id JohnMacFarlane.Pandoc

# Option 3: Manual
# Download from https://pandoc.org/installing.html
```

**Linux**:
```bash
sudo apt-get install pandoc texlive-xelatex  # Ubuntu/Debian
sudo dnf install pandoc texlive-xelatex      # Fedora
```

### Alternative: DOCX → PDF (No Pandoc Required)
1. Generate DOCX: `--format docx`
2. Open in Microsoft Word
3. File → Save As → PDF

---

## Performance Considerations

### Synthesis Time Estimates

| Configuration | Themes | Words/Ch | Chunks/Ch | Est. Time |
|--------------|--------|----------|-----------|-----------|
| Quick        | 2      | 1000     | 50        | ~5 min    |
| Standard     | 3-5    | 2500     | 150       | ~15 min   |
| Comprehensive| 5-8    | 4000     | 250       | ~30 min   |
| Exhaustive   | 8-10   | 6000     | 400       | ~60 min   |

**Factors affecting time**:
- Number of themes (clustering + LLM labeling)
- Chapter length (LLM generation time)
- Number of chunks (context processing)
- Ollama model speed (llama3.1:latest is relatively fast)

---

## Why Was The Original Output Short?

**Original command**:
```bash
--chapter-length 1000 --use-existing
```

**Why it was short** (~765 words total):
1. ✗ Only 2 themes auto-detected
2. ✗ Chapter length target not enforced by LLM
3. ✗ Only 50 chunks used per chapter (hardcoded)
4. ✗ LLM generated ~400 words instead of 1000

**Better command for substantial output**:
```bash
--n-themes 5 \
--chapter-length 3000 \
--chunks-per-chapter 200
```

**Result**: ~5 chapters × 3000 words = ~15,000 words (~50 pages)

---

## Tips for Best Results

### 1. Match Chunks to Length
- **Short chapters** (500-1500 words): 50-100 chunks
- **Medium chapters** (1500-3000 words): 100-200 chunks
- **Long chapters** (3000+ words): 200-400 chunks

### 2. Theme Count
- **Small corpus** (< 50 pages): 2-3 themes
- **Medium corpus** (50-200 pages): 3-5 themes
- **Large corpus** (200+ pages): 5-10 themes

### 3. Quality vs. Speed
- **Fast**: Lower chunks, shorter chapters, fewer themes
- **Balanced**: Default settings
- **Quality**: More chunks, longer chapters, more themes

### 4. PDF Issues?
- Ensure pandoc is installed: `pandoc --version`
- Check XeLaTeX is available: `xelatex --version`
- Fall back to DOCX if PDF fails

---

## Future Parameters (Planned)

- `--include-intro` - Add introduction chapter
- `--include-conclusion` - Add conclusion chapter
- `--sections-per-chapter` - Subsection depth
- `--examples-per-section` - Example density
- `--min-themes` / `--max-themes` - Theme range
- `--target-pages` - Target page count (auto-calculate words)

---

## Current Test: Running Now

```bash
# 3 themes, 3000 words/chapter, 200 chunks/chapter, PDF output
DOCPROCESSOR_OLLAMA_MODEL=llama3.1:latest python scripts/test_synthesis.py \
  --use-existing \
  --title "Le Bénéfice Fiscal" \
  --author "From Salma AKROUT" \
  --chapter-length 3000 \
  --chunks-per-chapter 200 \
  --n-themes 3 \
  --format pdf \
  --pdf-template academic
```

**Expected**: ~3 chapters × 3000 words = ~9000 words (~30 pages)
