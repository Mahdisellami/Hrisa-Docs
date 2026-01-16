# GUI Manual Testing Guide

Complete manual testing guide for the Hrisa Docs GUI application.

## Prerequisites

1. **Ollama must be running** for full functionality:
   ```bash
   ollama serve
   ollama pull llama3.1:latest
   ```

2. **Sample PDFs**: Use the PDFs in `data/manual_test/` or your own PDF documents

## Launch the GUI

```bash
.venv/bin/python scripts/launch_gui.py
```

The main window should appear with 4 tabs:
- 📄 Documents
- 🏷️ Themes
- 📖 Synthesis
- ⚙️ Settings

---

## Test Scenario 1: Basic Document Import

### Steps:
1. **Click the "Documents" tab**
2. **Click "➕ Add" button**
3. **Select PDF files** from file dialog
   - Use `data/manual_test/*.pdf` or your own PDFs
   - Try selecting 1 PDF, then multiple PDFs
4. **Verify document list updates**

### Expected Results:
✓ File dialog opens
✓ Selected PDFs appear in the document list
✓ Status shows "X document(s) loaded"
✓ Document names are displayed (not full paths)
✓ Tooltips show full file paths on hover
✓ "➖ Remove" button becomes enabled when selecting a document
✓ "🗑️ Clear All" button becomes enabled
✓ "⚡ Process Documents" button becomes enabled

### Test Variations:
- Add 1 document
- Add 3 documents at once
- Try adding same document twice (should not duplicate)
- Remove a document using "➖ Remove"
- Clear all documents using "🗑️ Clear All"

---

## Test Scenario 2: Document List Management

### Steps:
1. **Add multiple documents** (3-5 PDFs)
2. **Click on a document** in the list to select it
3. **Click "➖ Remove"** to remove the selected document
4. **Verify the document is removed**
5. **Click "🗑️ Clear All"**
6. **Verify all documents are removed**

### Expected Results:
✓ Selection highlights the document
✓ Remove button works correctly
✓ List updates immediately
✓ Status label updates document count
✓ Clear All removes everything
✓ Buttons disable appropriately when list is empty

---

## Test Scenario 3: Document Processing

### Steps:
1. **Add 2-3 sample PDFs** from `data/manual_test/`
2. **Click "⚡ Process Documents" button**
3. **Observe progress bar and status messages**
4. **Wait for completion** (should take 10-30 seconds)

### Expected Results:
✓ "Process Documents" button becomes disabled during processing
✓ Progress bar appears and shows progress (0-100%)
✓ Status messages update:
  - "Initializing..."
  - "Processing [filename]..."
  - "Embedding chunk X/Y..."
  - "Completed! Stored X chunks"
✓ Success dialog appears when complete
✓ "🔍 Discover Themes" button becomes enabled
✓ Progress bar disappears after completion
✓ Can process documents again if needed

### Watch For:
⚠️ Processing may take 20-30 seconds for 3 documents
⚠️ Large PDFs (>100 pages) may take several minutes
⚠️ If error occurs, check that PDFs are valid and readable

---

## Test Scenario 4: Theme Discovery

### Prerequisites:
- Documents must be processed first (Test Scenario 3)
- Ollama must be running

### Steps:
1. **Click "🏷️ Themes" tab**
2. **Click "🔍 Discover Themes" button**
3. **Observe progress** (this takes 30-60 seconds with LLM)
4. **Wait for theme discovery to complete**

### Expected Results:
✓ "Discover Themes" button becomes disabled during discovery
✓ Progress bar shows progress
✓ Status updates show:
  - "Retrieving chunks..."
  - "Analyzing X chunks..."
  - "Clustering themes..."
  - "Labeling theme X/Y..."
✓ Discovered themes appear in the list
✓ Each theme shows:
  - Theme label (e.g., "Legal Research Methods")
  - Chunk count (e.g., "5 chunks")
  - Importance score (e.g., "85.0%")
✓ Success dialog shows number of themes discovered
✓ "🚀 Start Synthesis" button becomes enabled (in Synthesis tab)

### Expected Themes (for sample PDFs):
- Should discover 2-3 themes
- Themes should have meaningful labels
- Themes in French if source is French
- Themes in English if source is English

---

## Test Scenario 5: Theme Editing

### Prerequisites:
- Themes must be discovered first (Test Scenario 4)

### Steps:
1. **Stay on "🏷️ Themes" tab**
2. **Select a theme** from the list
3. **Click "✏️ Rename" button**
4. **Enter new theme name** in dialog
5. **Click OK**
6. **Verify theme name updates**

### Expected Results:
✓ Theme can be selected
✓ "✏️ Rename" button becomes enabled
✓ Dialog appears with current name pre-filled
✓ New name is saved and displayed
✓ Theme list refreshes with new name

### Additional Tests:
- **Select 2+ themes**: "🔗 Merge" button should enable (not implemented yet)
- **Click "🗑️ Delete"**: Selected theme should be removed
- **Verify status label**: Shows correct theme count

---

## Test Scenario 6: Synthesis Configuration

### Steps:
1. **Click "📖 Synthesis" tab**
2. **Review default configuration**:
   - Synthesis level: Normal (30%)
   - Auto-detect themes: Checked
   - Chunks per chapter: 150
   - Output format: Both
   - Include citations: Checked

### Change Configuration:
1. **Synthesis level dropdown**:
   - Try: Short (15%), Normal (30%), Comprehensive (50%)
2. **Uncheck "Auto-detect optimal number"**:
   - Number of themes spinbox should become enabled
   - Adjust to 3, 5, 7
3. **Change chunks per chapter**: Try 100, 150, 200
4. **Change output format**: Try Markdown, DOCX, Both
5. **Toggle "Include source citations"**

### Expected Results:
✓ All controls are responsive
✓ Number of themes spinbox enables/disables correctly
✓ Changes are reflected immediately
✓ Status shows "Configure settings and process documents to begin"
✓ "🚀 Start Synthesis" button is disabled until themes are discovered

---

## Test Scenario 7: Book Synthesis

### Prerequisites:
- Documents processed (Test Scenario 3)
- Themes discovered (Test Scenario 4)
- Ollama running

### Steps:
1. **Stay on "📖 Synthesis" tab**
2. **Configure synthesis** (or use defaults)
3. **Click "🚀 Start Synthesis" button**
4. **Wait for synthesis** (2-5 minutes depending on settings)

### Expected Results:
✓ "🚀 Start Synthesis" button becomes disabled
✓ Progress bar appears
✓ Status messages update:
  - "Initializing..."
  - "Loading themes..."
  - "Synthesizing X chapters..."
  - "Writing chapter Y/X: [Theme Name]..."
  - "Formatting output..."
  - "Generating Markdown..."
  - "Generating DOCX..."
✓ Progress bar reaches 100%
✓ Success dialog appears with file paths
✓ Files are created in `data/output/`

### Verify Output Files:
```bash
ls -lh data/output/
```

Expected files:
- `synthesized_book_YYYYMMDD_HHMMSS.md`
- `synthesized_book_YYYYMMDD_HHMMSS.docx`

**Open and verify**:
```bash
open data/output/synthesized_book_*.md
open data/output/synthesized_book_*.docx
```

**Check content**:
✓ Title and author present
✓ Table of contents
✓ All chapters present
✓ Chapter titles match theme labels
✓ Content is coherent and well-structured
✓ Citations included (if enabled)
✓ Language matches source documents (French → French, English → English)
✓ No mixed languages (e.g., English headers in French content)

---

## Test Scenario 8: Error Handling

### Test 8A: Process Without Documents
1. **Clear all documents**
2. **Try to click "⚡ Process Documents"**
3. **Expected**: Button should be disabled

### Test 8B: Discover Themes Without Processing
1. **Go to Themes tab**
2. **Try to click "🔍 Discover Themes"**
3. **Expected**: Button should be disabled until documents are processed

### Test 8C: Synthesize Without Themes
1. **Go to Synthesis tab**
2. **Try to click "🚀 Start Synthesis"**
3. **Expected**: Button should be disabled until themes exist

### Test 8D: Ollama Not Running
1. **Stop Ollama**: `killall ollama` (or quit Ollama app)
2. **Try to discover themes**
3. **Expected**:
   - Operation should fail gracefully
   - Error dialog should appear
   - Helpful error message about Ollama

### Test 8E: Invalid PDF
1. **Add a non-PDF file** (rename .txt to .pdf)
2. **Try to process**
3. **Expected**:
   - Error dialog appears
   - Helpful error message
   - Processing stops gracefully

---

## Test Scenario 9: Long Running Operations

### Test Cancellation (Not Implemented Yet):
1. **Start a long operation** (e.g., processing 10+ PDFs)
2. **Try to interact with UI**
3. **Verify**: UI should remain responsive (not frozen)
4. **Note**: Cancellation is not yet implemented

### Test Multiple Operations:
1. **Process documents**
2. **Immediately try to process again**
3. **Expected**: Second process should not start while first is running

---

## Test Scenario 10: UI State Persistence

### Test Window State:
1. **Resize the window**
2. **Switch between tabs**
3. **Verify**: Window size persists as you switch tabs

### Test Data Persistence:
1. **Add documents**
2. **Switch to another tab**
3. **Return to Documents tab**
4. **Verify**: Document list is still there

**Note**: Closing and reopening the app will lose state (persistence not implemented)

---

## Test Scenario 11: Multi-Language Support

### Test French Documents:
1. **Add French PDFs** (create or use existing)
2. **Process → Discover Themes → Synthesize**
3. **Verify output**:
   - Theme labels in French
   - Chapter content in French
   - Headers: "Par", "Généré le", "Chapitre"
   - No English mixed in

### Test English Documents:
1. **Clear and add English PDFs**
2. **Process → Discover Themes → Synthesize**
3. **Verify output**:
   - Theme labels in English
   - Chapter content in English
   - Headers: "By", "Generated", "Chapter"
   - No French mixed in

---

## Test Scenario 12: Settings Tab

### Current State:
The Settings tab currently shows placeholder information:
- Ollama Model: llama3.1:latest
- Vector Store: ChromaDB
- Output Directory: data/output
- Language: Auto-detect

### Test:
1. **Click "⚙️ Settings" tab**
2. **Verify information is displayed**

**Note**: Settings are currently read-only (editing not implemented)

---

## Test Scenario 13: Menu Bar

### File Menu:
1. **Click "File" → "Import PDFs"**
2. **Verify**: Same as clicking "➕ Add" button
3. **Click "File" → "Exit"**
4. **Verify**: Application closes

### Help Menu:
1. **Click "Help" → "About"**
2. **Verify**: About dialog appears with:
   - Application name
   - Description
   - Features list
   - Tech stack
   - Phase information

---

## Performance Expectations

| Operation | Documents | Expected Time |
|-----------|-----------|---------------|
| Import PDFs | Any | Instant |
| Process Documents | 3 PDFs (~10 pages each) | 20-30 seconds |
| Process Documents | 10 PDFs | 1-2 minutes |
| Discover Themes | 3 documents | 30-60 seconds |
| Synthesize Book | 3 chapters, Normal | 2-3 minutes |
| Synthesize Book | 3 chapters, Comprehensive | 4-6 minutes |

---

## Known Issues / Limitations

### Not Yet Implemented:
- [ ] Operation cancellation
- [ ] Settings editing (read-only)
- [ ] Theme merging
- [ ] Undo/Redo
- [ ] Keyboard shortcuts (except standard ones)
- [ ] Drag and drop for documents
- [ ] Save/Load project
- [ ] Export to PDF directly

### Expected Behavior:
- GUI may briefly freeze during LLM operations (this is normal)
- Very large PDFs (500+ pages) may cause memory issues
- Synthesis with many themes (10+) will take considerable time

---

## Checklist Summary

Use this checklist to verify all major functionality:

### Documents Tab:
- [ ] Add single document
- [ ] Add multiple documents
- [ ] Remove document
- [ ] Clear all documents
- [ ] Process documents successfully
- [ ] Progress updates correctly
- [ ] Error handling works

### Themes Tab:
- [ ] Discover themes button enables after processing
- [ ] Theme discovery works
- [ ] Themes display correctly
- [ ] Rename theme works
- [ ] Delete theme works
- [ ] Theme count updates

### Synthesis Tab:
- [ ] Configuration controls work
- [ ] Auto-detect themes checkbox works
- [ ] Synthesis level changes
- [ ] Output format changes
- [ ] Synthesis button enables after themes discovered
- [ ] Synthesis completes successfully
- [ ] Output files created
- [ ] Content quality is good
- [ ] Language consistency maintained

### Settings Tab:
- [ ] Information displays correctly

### General:
- [ ] All tabs accessible
- [ ] Status bar updates
- [ ] Menu items work
- [ ] About dialog works
- [ ] Window resizes properly
- [ ] No crashes during normal operation

---

## Reporting Issues

If you find issues during testing, note:
1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Error messages** (if any)
5. **Screenshots** (if helpful)
6. **System info**: macOS version, Python version

---

## Quick Test (5 minutes)

For a quick validation:

```bash
# 1. Launch GUI
.venv/bin/python scripts/launch_gui.py

# 2. Add sample PDFs
#    Click "Add" → Select data/manual_test/*.pdf

# 3. Process
#    Click "Process Documents" → Wait for completion

# 4. Discover Themes (requires Ollama)
#    Go to Themes tab → Click "Discover Themes"

# 5. Synthesize (requires Ollama)
#    Go to Synthesis tab → Click "Start Synthesis"

# 6. Verify output files exist
ls -lh data/output/
```

Expected: All steps complete without errors, output files created.

---

## Full Test (30-45 minutes)

Work through all 13 test scenarios above for comprehensive validation.
