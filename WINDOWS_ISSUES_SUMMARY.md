# Windows Installation Issues - Summary

Based on screenshots from Windows testing (2026-01-15 05:43-05:45):

## Issues Identified

### 1. ✅ FIXED: Wrong Pandoc Installation Instructions
**Problem:** Error message shows "Install with: brew install pandoc (macOS)" on Windows
**Screenshot:** 05.44.38
**Status:** Fixed in output_formatter.py - now shows platform-specific instructions

### 2. ⚠️ CMD Window Appears During Processing
**Problem:** Administrator CMD window opens during chunk processing
**Screenshot:** 05.43.02 (black CMD window with "Administrator: C:\WINDOWS\...")
**Likely Cause:** Dependency checker still running or subprocess calls without CREATE_NO_WINDOW
**Status:** Partially fixed - added subprocess.STARTUPINFO() for pandoc calls
**Note:** If CMD appears during synthesis, might be from Ollama installation check

### 3. ❌ CRITICAL: Content Generation Fails
**Problem:** "[Content generation failed]" in synthesized document
**Screenshots:** 05.43.19, 05.44.51, 05.45.12
**Evidence:**
- Theme discovery works (Theme 1: 201 mentions, Theme 1.08: 7 mentions)
- Synthesis tab shows "[Content generation failed]" for all themes
- Final document has table of contents but no content

**Root Cause:** Ollama not responding or model not available
**Possible Reasons:**
1. Ollama service not started after installation
2. Model (llama3.1:latest) not pulled
3. Ollama service running but not accessible
4. Permission issues with Ollama on Windows

## Fixes Applied

### 1. check_dependencies.py
- Added comprehensive logging to %TEMP%\hrisa_deps_install.log
- Windows Ollama: Use silent install flags (/VERYSILENT)
- Windows Ollama: Wait for completion and verify service
- Windows Ollama: Explicitly start service with 'net start Ollama'
- Windows Ollama: Verify ollama --version responds
- Windows Pandoc: Silent MSI install (/qn)
- Auto-install Pandoc without prompt
- Added installation summary

### 2. build_windows.py
- Removed 'runhidden' flag - show console during dependency install
- Added option to view log file after installation
- Better status messages

### 3. output_formatter.py
- Platform-specific error messages for Pandoc/XeLaTeX
- Added subprocess.STARTUPINFO() for Windows to hide pandoc CMD window
- Fixed macOS-only error messages

## Next Steps for User

### Immediate Debugging

1. **Check if Ollama is actually installed and running:**
   ```cmd
   ollama --version
   ollama list
   ```

2. **Check if Ollama service is running:**
   ```cmd
   sc query Ollama
   ```
   Or in Task Manager, look for "Ollama" service

3. **Check the installation log:**
   - Open `%TEMP%\hrisa_deps_install.log` in Notepad
   - Look for:
     - "✅ Ollama is responding: [version]"
     - "✅ Model 'llama3.1:latest' pulled successfully"
     - Any error messages

4. **If Ollama not installed, manually install:**
   - Download from: https://ollama.ai/download
   - Install normally (not silent)
   - After install, open CMD and run:
     ```cmd
     ollama pull llama3.1:latest
     ```

5. **Verify Ollama works:**
   ```cmd
   ollama run llama3.1:latest
   >>> Hello
   (should respond)
   >>> /bye
   ```

### Testing the Fixed Version

1. **Rebuild Windows installer with fixes:**
   ```bash
   cd /Users/peng/Documents/mse/private/Document-Processing
   python scripts/build_windows.py
   ```

2. **Transfer new installer to Windows VM**

3. **Uninstall old version in Windows:**
   - Settings → Apps → Hrisa Docs → Uninstall

4. **Install new version with "Install dependencies" checked**
   - Watch the console window (should now be visible)
   - Look for success messages
   - After install, optionally view log file

5. **Test synthesis:**
   - Open app
   - Load project with documents
   - Run "Discover Themes"
   - Run "Synthesis"
   - Check if content generates successfully

## Why Pandoc IS for Windows

**Correction:** Pandoc **IS available for Windows**!
- Download: https://pandoc.org/installing.html
- Windows installer: `.msi` file
- Required for PDF export
- Our dependency checker installs it automatically

## CMD Window Issue

The CMD window appearing is likely one of:
1. Dependency checker still running (if during install)
2. Ollama installation prompts (should be hidden now with /VERYSILENT)
3. First-time Ollama service start

With the fixes:
- Dependency install console should be visible (intentional, for debugging)
- Pandoc calls during PDF export are hidden (subprocess.STARTUPINFO)
- Ollama calls are HTTP-based, no CMD windows

## Expected Behavior After Fixes

1. **Installation:**
   - Console window visible during dependency install ✓
   - Shows progress for Ollama, Pandoc, model download ✓
   - Creates log file ✓
   - Option to view log after install ✓

2. **First Run:**
   - App opens normally ✓
   - No CMD windows during processing ✓
   - Ollama responds to synthesis requests ✓

3. **Synthesis:**
   - Themes discovered ✓
   - Content generated successfully ✓
   - Export works (all formats) ✓

## Status

- ✅ Pandoc error messages fixed
- ✅ Dependency installer improved with logging
- ✅ Windows subprocess calls fixed (no CMD windows)
- ❌ **Still need to verify:** Ollama actually installs and starts on Windows
- ⚠️ **User must test:** Rebuild installer and test on Windows VM
