# Windows Testing Checklist

## Current Status

✅ **Fixed:** Pandoc error messages now platform-specific
✅ **Fixed:** CMD windows hidden during subprocess calls
✅ **Fixed:** Dependency installer has comprehensive logging
⚠️  **Partial:** Ollama installed but synthesis still failing
❌ **Issue:** Theme names showing as "Theme 1", "Theme 2" instead of descriptive labels
❌ **Issue:** Content generation failing - "[Content generation failed]"

---

## Critical Issues to Debug

### Issue 1: Ollama Not Generating Content

**Evidence:**
- Theme discovery works (Theme 2: 203 mentions, Theme 1: 247 mentions)
- Synthesis runs but produces "[Content generation failed]"
- This means Ollama is not responding to generation requests

**Debug Steps:**

1. **Verify Ollama is running:**
   ```cmd
   ollama --version
   ```
   Expected: Shows version number (e.g., "ollama version 0.1.17")

2. **Check if Ollama service is running:**
   ```cmd
   sc query Ollama
   ```
   Expected: STATE = "RUNNING"

3. **List available models:**
   ```cmd
   ollama list
   ```
   Expected: Should show "llama3.1:latest" or similar

4. **Test Ollama directly:**
   ```cmd
   ollama run llama3.1:latest
   ```
   Type: "Hello"
   Expected: Should respond with generated text
   Exit with: `/bye`

5. **Check Ollama is accessible on default port:**
   ```cmd
   curl http://localhost:11434/api/tags
   ```
   Expected: JSON response with model list

**If Ollama not running:**

Option A: Start manually
```cmd
ollama serve
```
(Leave this CMD window open)

Option B: Install as service (recommended)
- Download and install from: https://ollama.ai/download
- Installer should auto-start service

**If model not available:**
```cmd
ollama pull llama3.1:latest
```
Wait for download (4-5 GB)

---

### Issue 2: Theme Names Generic Instead of Descriptive

**Evidence:**
- Themes show as "Theme 1", "Theme 2"
- Should show descriptive names like "Budget Analysis", "Tax Regulations", etc.

**Possible Causes:**

1. **Theme labeling disabled in settings**
   - Check: Parameters tab → "Auto-label themes" checkbox
   - Should be: ✅ Checked

2. **Ollama not responding during theme discovery**
   - If Ollama was down during theme discovery
   - Labels couldn't be generated
   - Themes got default names

**Solution:**
1. Ensure Ollama is running (see Issue 1)
2. Re-run theme discovery:
   - Go to Themes tab
   - Click "Clear" to remove old themes
   - Click "Discover Themes" again
   - Wait for completion
   - Check if themes now have descriptive names

---

## Testing Workflow

### Step 1: Verify Ollama Installation

1. Open CMD
2. Run: `ollama --version`
3. Run: `ollama list`
4. Run: `ollama run llama3.1:latest`
5. Type "Hello" and press Enter
6. Verify it responds
7. Type `/bye` to exit

### Step 2: Re-run Theme Discovery (with Ollama running)

1. Open Hrisa Docs
2. Go to Themes tab
3. Click "Clear" button
4. Click "Discover Themes"
5. Wait for completion
6. **Check theme names** - should be descriptive, not "Theme 1"

### Step 3: Run Synthesis

1. Go to Synthesis tab
2. Click "Start Synthesis"
3. Wait for completion
4. **Check generated document** - should have actual content, not "[Content generation failed]"

### Step 4: Test PDF Export

1. After synthesis succeeds
2. Check "Include PDF" checkbox
3. Click "Export"
4. **Expected error** (if Pandoc not installed):
   - "Pandoc not installed. Install from: https://pandoc.org/installing.html"
   - NOT "brew install pandoc"

---

## Expected Results After Fixes

### Theme Discovery
```
Découverte de thèmes:

Budget Analysis (203 mentions, 94.3%)
Financial Regulations (247 mentions, 48.2%)
Tax Compliance (156 mentions, 32.1%)
```

### Synthesis Output
```markdown
# Synthesized Document

**Generated**: 2026-01-15 07:21

---

## Table of Contents

1. [Budget Analysis](#chapter-1)
2. [Financial Regulations](#chapter-2)

---

## Chapter 1: Budget Analysis {#chapter-1}

### Overview

The budget analysis framework encompasses several key components...

[Actual generated content here, multiple paragraphs]

### Key Findings

...

---

## Chapter 2: Financial Regulations {#chapter-2}

### Introduction

Financial regulations in Tunisia have evolved...

[Actual generated content]
```

---

## Diagnostic Log Locations

### Dependency Installation Log
```
%TEMP%\hrisa_deps_install.log
```
Open with: `notepad %TEMP%\hrisa_deps_install.log`

### Application Logs
```
%USERPROFILE%\.docprocessor\logs\
```

Look for:
- Ollama connection errors
- Theme labeling errors
- Synthesis failures

---

## Quick Fix Commands

### If Ollama not installed:
```cmd
# Download from browser: https://ollama.ai/download
# Or use PowerShell:
irm https://ollama.ai/install.sh | iex
```

### If Ollama installed but not running:
```cmd
# Start service
net start Ollama

# Or run manually
ollama serve
```

### If model not pulled:
```cmd
ollama pull llama3.1:latest
```

### If Pandoc needed for PDF:
```cmd
# Download from browser: https://pandoc.org/installing.html
# Or check dependency log
notepad %TEMP%\hrisa_deps_install.log
```

---

## Known Good State

When everything works correctly:

1. ✅ `ollama --version` shows version
2. ✅ `ollama list` shows llama3.1:latest
3. ✅ `sc query Ollama` shows STATE = RUNNING
4. ✅ Theme discovery produces descriptive names
5. ✅ Synthesis generates actual content
6. ✅ PDF export shows Windows-specific error if Pandoc missing

---

## Next Rebuild

When you rebuild the installer again, verify dependency checker:

1. Install with "Install dependencies" checkbox checked
2. Watch console window (should be visible now)
3. Look for:
   - "✅ Ollama is responding: [version]"
   - "✅ Model 'llama3.1:latest' pulled successfully"
   - "✅ Pandoc installed successfully"
4. After install, check log:
   ```cmd
   notepad %TEMP%\hrisa_deps_install.log
   ```

---

## Transfer New Installer to Windows

The new installer with all fixes is ready:
```
/Users/peng/Documents/mse/private/Document-Processing/dist/HrisaDocs.exe
```

Copy to Windows VM and test!
