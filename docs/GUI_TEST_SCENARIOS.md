# GUI Test Scenarios - Step by Step

## Scenario 1: Complete Workflow (No Ollama Required - 3 minutes)

**Goal**: Test document import and processing without needing Ollama

### Setup
✓ GUI should already be running
✓ You should see the main window with 4 tabs

### Steps

**1. Import Two Documents**
   - Click the **"📄 Documents"** tab (should already be selected)
   - You should see:
     - Empty document list
     - "No documents loaded" status
     - Gray "⚡ Process Documents" button (disabled)

   - Click **"➕ Add"** button
   - Navigate to: `data/manual_test/`
   - Select **TWO** files:
     - `sample_legal_research.pdf`
     - `sample_constitutional_law.pdf`
   - Click **"Open"**

   **✓ Expected Result:**
   - Both documents appear in the list
   - Status shows "2 document(s) loaded"
   - "⚡ Process Documents" button turns blue (enabled)
   - "🗑️ Clear All" button is enabled
   - Each document shows only filename (not full path)
   - Hover over a document → tooltip shows full path

**2. Test Document List Controls**
   - Click on the first document to select it

   **✓ Expected:**
   - Document highlights in blue
   - "➖ Remove" button becomes enabled

   - Click **"➖ Remove"** button

   **✓ Expected:**
   - Document is removed from list
   - Status shows "1 document(s) loaded"

   - Click **"➕ Add"** again
   - Add the same document back
   - Click **"Add"** again and try to add it once more

   **✓ Expected:**
   - Document appears in list
   - Adding same document twice doesn't create duplicate
   - Still shows "2 document(s) loaded"

**3. Process Documents**
   - Click **"⚡ Process Documents"** button

   **✓ Immediately You Should See:**
   - Button becomes gray (disabled)
   - Progress bar appears at bottom
   - Status changes to "Initializing..."
   - "➕ Add" button becomes gray (disabled)

   **✓ After 5-10 seconds:**
   - Status shows "Processing sample_legal_research.pdf..."
   - Progress bar shows ~25%

   **✓ After 15-20 seconds:**
   - Status shows "Embedding chunk 1/1..." (or similar)
   - Progress bar shows ~50%

   **✓ After 20-30 seconds:**
   - Status shows "✓ Processed successfully: 2 chunks stored"
   - Progress bar reaches 100% then disappears
   - Success dialog pops up:
     ```
     Processing Complete
     Successfully processed documents!
     Total chunks: 2
     You can now discover themes.
     ```
   - Click **"OK"**

   **✓ Final State:**
   - "⚡ Process Documents" button is enabled again (can reprocess)
   - "➕ Add" button is enabled
   - Status bar at bottom shows "Processing complete: 2 chunks"

**4. Check Themes Tab**
   - Click the **"🏷️ Themes"** tab

   **✓ Expected:**
   - "🔍 Discover Themes" button is now enabled (blue)
   - Theme list is empty
   - Status shows "No themes discovered yet"

**5. Check Synthesis Tab**
   - Click the **"📖 Synthesis"** tab

   **✓ Expected:**
   - Configuration options are visible
   - "🚀 Start Synthesis" button is gray (disabled - no themes yet)
   - Status shows "Configure settings and process documents to begin"

**🎉 SCENARIO 1 COMPLETE!**
You've successfully tested:
- ✓ Document import
- ✓ Document list management
- ✓ Document processing with progress tracking
- ✓ Tab navigation
- ✓ Button state management

---

## Scenario 2: Full Workflow with Theme Discovery & Synthesis (5 minutes)

**Goal**: Complete end-to-end workflow from PDFs to synthesized book

**Prerequisites**:
- ⚠️ **OLLAMA MUST BE RUNNING**
- Run in terminal: `ollama serve`
- In another terminal: `ollama pull llama3.1:latest`

### Steps

**1. Start Fresh**
   - If documents are already loaded, click **"🗑️ Clear All"**
   - Click **"📄 Documents"** tab

**2. Import Three Documents**
   - Click **"➕ Add"**
   - Navigate to `data/manual_test/`
   - Select **ALL THREE** files (Cmd+A or Shift+Click):
     - `sample_legal_research.pdf`
     - `sample_constitutional_law.pdf`
     - `sample_treaty_law.pdf`
   - Click **"Open"**

   **✓ Expected:**
   - All 3 documents in list
   - Status: "3 document(s) loaded"

**3. Process Documents**
   - Click **"⚡ Process Documents"**
   - Wait for completion (~30-40 seconds)
   - Click **"OK"** on success dialog

   **✓ Expected:**
   - Success message: "Total chunks: 3"
   - Status: "Processing complete: 3 chunks"

**4. Discover Themes**
   - Click **"🏷️ Themes"** tab
   - Click **"🔍 Discover Themes"** button

   **✓ Immediately:**
   - Button becomes gray (disabled)
   - Progress bar appears
   - Status shows "Initializing..."

   **✓ After 10 seconds:**
   - Status shows "Retrieving chunks..."
   - Progress bar ~20%

   **✓ After 20 seconds:**
   - Status shows "Analyzing 3 chunks..."
   - Progress bar ~40%

   **✓ After 30 seconds:**
   - Status shows "Clustering themes..."
   - Progress bar ~60%

   **✓ After 40-60 seconds:**
   - Status shows "Labeling theme 1/2..." or "Labeling theme 1/3..."
   - Progress bar ~80-100%

   **✓ After 60-90 seconds:**
   - Success dialog appears:
     ```
     Theme Discovery Complete
     Discovered 2 themes!
     You can now review and edit themes, then generate your book.
     ```
   - Click **"OK"**

   **✓ Theme List:**
   - Should show 2-3 themes
   - Each theme shows:
     - Label (e.g., "Legal Research Methods")
     - Chunk count (e.g., "1 chunks, 33.3%")
   - Status shows "2 theme(s) discovered" or "3 theme(s) discovered"

**5. Edit a Theme (Optional)**
   - Click on first theme to select it
   - Click **"✏️ Rename"** button
   - Dialog appears with current name
   - Change to: "Legal Research Methodology"
   - Click **"OK"**

   **✓ Expected:**
   - Theme name updates in list immediately
   - List refreshes

**6. Configure Synthesis**
   - Click **"📖 Synthesis"** tab

   **✓ Expected:**
   - "🚀 Start Synthesis" button is now enabled (green)
   - Status shows "Ready to synthesize"

   - In **"Synthesis Settings"** section:
     - Change "Synthesis level" to **"Comprehensive (50%)"**
   - In **"Output Settings"**:
     - Keep "Output format" as **"Both"**
     - Keep "Include source citations" **checked**

**7. Generate Book**
   - Click **"🚀 Start Synthesis"** button

   **✓ Immediately:**
   - Button becomes gray (disabled)
   - Progress bar appears
   - Status shows "Initializing..."

   **✓ After 10 seconds:**
   - Status shows "Loading themes..."
   - Progress bar ~10%

   **✓ After 20 seconds:**
   - Status shows "Synthesizing 2 chapters..."
   - Progress bar ~20%

   **✓ After 30-60 seconds:**
   - Status shows "Writing chapter 1/2: Legal Research Methods..."
   - Progress bar ~40-50%
   - ⏳ **This is the longest step - LLM is generating text**

   **✓ After 1-2 minutes:**
   - Status shows "Writing chapter 2/2: [Theme Name]..."
   - Progress bar ~60-70%

   **✓ After 2-3 minutes:**
   - Status shows "Formatting output..."
   - Progress bar ~80%

   **✓ After 2.5-3 minutes:**
   - Status shows "Generating Markdown..."
   - Progress bar ~85%

   **✓ After 2.8-3.5 minutes:**
   - Status shows "Generating DOCX..."
   - Progress bar ~90%

   **✓ After 3-4 minutes:**
   - Progress bar reaches 100%
   - Success dialog appears:
     ```
     Synthesis Complete
     Book generated successfully!

     Markdown: data/output/synthesized_book_20260105_123456.md
     DOCX: data/output/synthesized_book_20260105_123456.docx
     ```
   - Click **"OK"**

   **✓ Final State:**
   - Status shows "✓ Book generation complete!"
   - Button is enabled again

**8. Verify Output**
   - Open terminal or Finder
   - Navigate to `data/output/`
   - You should see two files:
     - `.md` file (10-30 KB)
     - `.docx` file (15-40 KB)

   **In Terminal:**
   ```bash
   cd data/output
   ls -lh
   open synthesized_book*.md
   open synthesized_book*.docx
   ```

   **✓ Markdown File Should Contain:**
   - Title: "Synthesized Document"
   - Author: "Synthèse par [name]" or "By [name]"
   - Date generated
   - Table of contents
   - 2-3 chapters with theme names as titles
   - Chapter content (several paragraphs)
   - All in same language as source (English for these samples)

   **✓ DOCX File Should Contain:**
   - Same content as Markdown
   - Professional formatting
   - Proper heading styles

**🎉 SCENARIO 2 COMPLETE!**
You've successfully tested the complete workflow:
- ✓ Import → Process → Discover → Synthesize → Export
- ✓ Full LLM integration
- ✓ Progress tracking for long operations
- ✓ Output file generation

---

## Scenario 3: Error Testing (2 minutes)

**Goal**: Verify error handling and edge cases

### Steps

**1. Test "No Documents" Protection**
   - Click **"📄 Documents"** tab
   - If documents are loaded, click **"🗑️ Clear All"**
   - Try to click **"⚡ Process Documents"**

   **✓ Expected:**
   - Button should be gray (disabled)
   - Cannot click it
   - Status shows "No documents loaded"

**2. Test "Can't Discover Without Processing"**
   - Click **"🏷️ Themes"** tab
   - Look at **"🔍 Discover Themes"** button

   **✓ Expected:**
   - Button should be gray (disabled)
   - Cannot click it
   - Status shows "No themes discovered yet"

**3. Test "Can't Synthesize Without Themes"**
   - Click **"📖 Synthesis"** tab
   - Look at **"🚀 Start Synthesis"** button

   **✓ Expected:**
   - Button should be gray (disabled)
   - Cannot click it
   - Status shows "Configure settings and process documents to begin"

**4. Test Adding Same Document Twice**
   - Click **"📄 Documents"** tab
   - Click **"➕ Add"**
   - Select `sample_legal_research.pdf`
   - Click **"Open"**
   - Immediately click **"➕ Add"** again
   - Select the SAME file again
   - Click **"Open"**

   **✓ Expected:**
   - Document appears only once in list
   - Status shows "1 document(s) loaded" (not 2)

**5. Test Menu Bar**
   - Click **"File"** menu at top
   - Click **"Import PDFs"**

   **✓ Expected:**
   - Same file dialog as clicking "➕ Add"

   - Click **"Help"** menu
   - Click **"About"**

   **✓ Expected:**
   - About dialog appears with:
     - "Hrisa Docs"
     - Description
     - Features list
     - Tech stack info
   - Click **"OK"**

**6. Test Window Resize**
   - Drag window corner to make it smaller
   - Drag to make it larger

   **✓ Expected:**
   - Window resizes smoothly
   - All controls remain visible
   - No layout issues

**🎉 SCENARIO 3 COMPLETE!**
You've verified:
- ✓ Button state management prevents invalid operations
- ✓ Duplicate detection works
- ✓ Menu bar functions correctly
- ✓ UI is responsive to window changes

---

## Scenario 4: Theme Management (1 minute)

**Prerequisites**: Must have completed Scenario 2 (themes discovered)

### Steps

**1. Select and Rename**
   - Click **"🏷️ Themes"** tab
   - Click on the **first theme**

   **✓ Expected:**
   - Theme highlights
   - "✏️ Rename" button becomes enabled
   - "🗑️ Delete" button becomes enabled
   - "🔗 Merge" button stays disabled (need 2+ selected)

   - Click **"✏️ Rename"**
   - In dialog, change name to: "Test Theme Name"
   - Click **"OK"**

   **✓ Expected:**
   - Theme list refreshes
   - First theme now shows "Test Theme Name"

**2. Delete a Theme**
   - Click on the **last theme** in list
   - Click **"🗑️ Delete"**

   **✓ Expected:**
   - Theme is removed from list
   - Theme count decreases by 1
   - Status updates: "X theme(s) discovered"
   - If you go to Synthesis tab, button may become disabled if no themes left

**3. Try Multiple Selection**
   - Hold **Cmd** (Mac) or **Ctrl** (Windows)
   - Click on **two themes**

   **✓ Expected:**
   - Both themes highlight
   - "🔗 Merge" button becomes enabled
   - Note: Merge functionality not implemented yet

**🎉 SCENARIO 4 COMPLETE!**
You've tested:
- ✓ Theme selection
- ✓ Theme renaming
- ✓ Theme deletion
- ✓ Button state management

---

## Quick Checklist

Use this for rapid testing:

```
□ Launch GUI
□ Add 2 PDFs
□ Remove 1 PDF
□ Add it back
□ Process documents (~30s)
□ Switch to Themes tab
□ Discover themes (~60s, needs Ollama)
□ Rename a theme
□ Switch to Synthesis tab
□ Change synthesis level
□ Start synthesis (~3-4 min, needs Ollama)
□ Open output files
□ Verify content quality
```

---

## Troubleshooting

**GUI doesn't appear:**
```bash
.venv/bin/python scripts/launch_gui.py
```

**Processing hangs:**
- Check if progress bar is moving
- Wait at least 60 seconds
- Check terminal for errors

**Theme discovery fails:**
```bash
# Check Ollama is running:
curl http://localhost:11434/api/tags

# If not running:
ollama serve

# In another terminal:
ollama pull llama3.1:latest
```

**Synthesis takes forever:**
- Comprehensive mode with many themes can take 5-10 minutes
- This is normal - LLM is generating substantial text
- Progress bar should still be moving

**Output files empty:**
- Check `data/output/` directory exists
- Check file timestamps (should be recent)
- Open files to verify content

---

## Expected Timings

| Operation | Duration |
|-----------|----------|
| Import documents | Instant |
| Process 3 documents | 30-40 seconds |
| Discover themes (3 docs) | 60-90 seconds |
| Synthesize 2 chapters (Normal) | 2-3 minutes |
| Synthesize 2 chapters (Comprehensive) | 4-6 minutes |
| Synthesize 5 chapters (Comprehensive) | 8-12 minutes |

---

**Start with Scenario 1 if Ollama is not running**
**Start with Scenario 2 if Ollama is running**
**Use Quick Checklist for rapid validation**
