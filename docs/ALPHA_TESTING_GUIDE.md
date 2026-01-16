# Hrisa Docs - Alpha Testing Guide

Welcome! Thank you for helping test Hrisa Docs. This guide will help you test the application effectively and provide valuable feedback.

## 📥 Installation

### macOS
1. Download `HrisaDocs-0.1.0-macOS.dmg`
2. Open the DMG file
3. Drag "Hrisa Docs" to Applications folder
4. **First launch**: Right-click app → "Open" (to bypass Gatekeeper)
   - Alternative: System Settings → Privacy & Security → "Open Anyway"

### Windows
1. Download `HrisaDocs-0.1.0-Setup.exe`
2. Run the installer
3. Follow installation wizard
4. Launch from Start Menu or Desktop shortcut

## ⚙️ Prerequisites

### Required: Ollama (Local LLM)
```bash
# Download from: https://ollama.ai/download
# After installation, pull the model:
ollama pull llama3.1:latest
```

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/version
# Should return version info
```

### Optional: PDF Export
For PDF export functionality:
- **macOS**: `brew install pandoc` + `brew install --cask mactex-no-gui`
- **Windows**: Download from pandoc.org + MiKTeX

## 🧪 Test Scenarios

### Scenario 1: First Project (15 min)
**Goal**: Test the complete workflow from start to finish.

1. **Launch app**
   - Does it open without errors?
   - Does the main window look correct?

2. **Create project** (Cmd/Ctrl+N)
   - Click "Manage Projects" → "New Project"
   - Name: "Alpha Test 1"
   - Description: "Testing basic workflow"
   - Template: "Standard"
   - ✅ **Expected**: Project created, dashboard closes

3. **Import documents** (Cmd/Ctrl+O)
   - Go to "Files" tab
   - Click "Import" or press Cmd/Ctrl+O
   - Select 2-3 PDF files (ideally research papers or reports)
   - ✅ **Expected**: Files tab shows "Files (3)", documents appear in list

4. **Process documents**
   - Click "Process" button
   - ✅ **Expected**:
     - Progress bar shows detailed messages
     - Green ✓ checkmark when done
     - Dialog shows: "✓ Processing complete! 150 chunks stored"

5. **Discover themes**
   - Go to "Themes" tab
   - Click "Discover Themes"
   - ✅ **Expected**:
     - Progress shows "Clustering...", "Analyzing..."
     - Dialog shows: "✓ Discovered 5 themes"
     - Themes tab shows "Themes (5)"
     - Themes appear with labels and descriptions

6. **Generate synthesis**
   - Go to "Synthesis" tab
   - Select "Normal" level
   - Format: "DOCX"
   - Title: "Alpha Test Synthesis"
   - Click "Generate Synthesis"
   - ✅ **Expected**:
     - Progress shows detailed steps
     - Dialog shows: "✨ Synthesis complete! 📘 DOCX: [path], 📊 Summary: X words, Y citations"
     - Output files tab shows generated DOCX

7. **Open output**
   - In "Output Files", click the DOCX file
   - ✅ **Expected**: Opens in Word/LibreOffice with formatted chapters and citations

**📝 Report**:
- Did everything work smoothly?
- Were the progress messages clear?
- Was the generated content coherent?
- Any confusing steps?

---

### Scenario 2: Keyboard Shortcuts (5 min)
**Goal**: Test keyboard navigation.

1. **File operations**:
   - Press **Cmd/Ctrl+O** → Should open import dialog
   - Press **Cmd/Ctrl+N** → Should open new project dialog
   - Press **Cmd/Ctrl+Shift+P** → Should open project dashboard

2. **Menu tooltips**:
   - Hover over File menu items
   - ✅ **Expected**: Tooltips show descriptions and keyboard shortcuts

**📝 Report**:
- Which shortcuts worked?
- Which didn't?
- Were tooltips helpful?

---

### Scenario 3: Project Management (10 min)
**Goal**: Test multi-project features.

1. **Create multiple projects**
   - Press Cmd/Ctrl+Shift+P to open dashboard
   - Create 3 projects with different names

2. **Duplicate project**
   - Select one project
   - Click "Duplicate" button
   - Enter new name: "Copy of Alpha Test 1"
   - ✅ **Expected**: New project appears with same settings

3. **Rename project**
   - Select a project
   - Click "Rename" button
   - Change name to "Renamed Project"
   - ✅ **Expected**: Project name updates in list

4. **Multi-select and bulk delete**
   - Hold Cmd/Ctrl and click 2 projects
   - ✅ **Expected**: Delete button shows "Supprimer (2)"
   - Click "Supprimer (2)"
   - Choose "Archive All"
   - ✅ **Expected**: Both projects archived, success message shows count

5. **Context menu**
   - Right-click on a project
   - ✅ **Expected**: Menu shows 📂 Open, 📋 Duplicate, ✏️ Rename, ⭐ Favorite, 📦 Archive

6. **Filter and search**
   - Change filter to "Actifs" (Active)
   - ✅ **Expected**: Archived projects disappear
   - Change filter to "Archivés" (Archived)
   - ✅ **Expected**: Only archived projects show
   - Search for a project name
   - ✅ **Expected**: List filters to matching projects

**📝 Report**:
- Did multi-select work smoothly?
- Were bulk operations clear?
- Did context menu work on right-click?
- Any bugs with filters/search?

---

### Scenario 4: Error Handling (5 min)
**Goal**: Test how app handles problems.

1. **Process without documents**
   - Create new project
   - Try to click "Process" without importing any PDFs
   - ✅ **Expected**: Clear error message

2. **Ollama not running**
   - Stop Ollama: `pkill ollama`
   - Try to discover themes or generate synthesis
   - ✅ **Expected**: Error mentions Ollama connection failed with instructions

3. **Invalid file**
   - Try to import a non-PDF file (e.g., .txt, .jpg)
   - ✅ **Expected**: Either rejected with message or imported with warning

**📝 Report**:
- Were error messages clear?
- Did you know how to fix the problem?
- Any crashes?

---

### Scenario 5: Visual Polish (5 min)
**Goal**: Check UI quality.

1. **Success notifications**
   - After processing, check if:
     - Green ✓ checkmark appears
     - Dialog has icons (✓, ✨, 📄, 📘, 📊)
     - Summary stats are shown

2. **Tab badges**
   - Check if "Files" tab shows count: "Files (3)"
   - Check if "Themes" tab shows count: "Themes (5)"

3. **Tooltips**
   - Hover over various buttons
   - ✅ **Expected**: Helpful tooltips appear

**📝 Report**:
- Does the app look professional?
- Are icons/emojis helpful or distracting?
- Any visual bugs?

---

## 🐛 Reporting Issues

### What to Include

1. **Environment**:
   - OS: macOS 15.x / Windows 11 / etc.
   - Hrisa Docs version: 0.1.0
   - Ollama version: `ollama --version`

2. **Steps to Reproduce**:
   - What did you do? (step by step)
   - What did you expect?
   - What actually happened?

3. **Logs** (if app crashed or behaved strangely):
   - **macOS**: `~/.docprocessor/logs/docprocessor.log`
   - **Windows**: `C:\Users\[YourName]\.docprocessor\logs\docprocessor.log`
   - Copy the last 50-100 lines

4. **Screenshots/Video** (very helpful!):
   - Screenshot of the error
   - Screen recording of the bug happening

### How to Report

**Email/Message format:**
```
Subject: [Alpha] Brief description of issue

Environment:
- OS: macOS 15.1
- Hrisa Docs: 0.1.0
- Ollama: 0.1.22

Issue:
[Describe what happened]

Steps to Reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected:
[What should happen]

Actual:
[What actually happened]

Logs:
[Paste relevant logs if available]

Screenshots:
[Attach screenshots]
```

## 💡 Feedback We're Looking For

### Usability
- Is the workflow clear and intuitive?
- Are there confusing steps?
- What took longer than expected?
- What was surprisingly easy?

### Features
- What features do you wish existed?
- What features do you never use?
- What would make your workflow faster?

### Performance
- How long did processing take? (Note: depends on document size)
- Did the app feel slow anywhere?
- Any freezing or hanging?

### Quality
- Was the generated content coherent?
- Were citations accurate?
- Did themes make sense?
- Quality of output formatting?

### Documentation
- Was this guide clear?
- What was missing?
- What was confusing?

## 📞 Getting Help

### Common Issues

**App won't open (macOS)**:
```bash
xattr -d com.apple.quarantine "/Applications/Hrisa Docs.app"
```

**Ollama connection failed**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve
```

**Processing takes forever**:
- Normal: ~30 seconds per 100 pages
- Check CPU usage (should be high during processing)
- Check Ollama is responding: `ollama list`

**PDF export not working**:
- Install pandoc: `brew install pandoc` (macOS)
- Install LaTeX: `brew install --cask mactex-no-gui` (macOS)

### Full Documentation
- **User Guide**: `docs/USER_GUIDE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **README**: `README.md`

## 🎯 Testing Priorities

### Critical (Must Work)
1. ✅ Create project
2. ✅ Import documents
3. ✅ Process documents
4. ✅ Discover themes
5. ✅ Generate synthesis
6. ✅ Export output

### Important (Should Work)
7. ✅ Keyboard shortcuts
8. ✅ Project management (duplicate, rename)
9. ✅ Multi-select and bulk operations
10. ✅ Error messages

### Nice to Have (Test if Time)
11. ✅ Visual polish (icons, badges, tooltips)
12. ✅ Context menus
13. ✅ Search and filters
14. ✅ Different synthesis levels

## 🙏 Thank You!

Your feedback is invaluable for making Hrisa Docs better. Even small comments like "this button was confusing" or "I loved this feature" help immensely.

Happy testing! 🚀

---

**Contact**: [Your email/contact]
**Version**: 0.1.0 Alpha
**Date**: January 2026
