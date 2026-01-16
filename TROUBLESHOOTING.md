# Hrisa Docs - Troubleshooting Guide

## Issue: App Won't Open on macOS

### Symptoms
- Downloaded .dmg file
- Installed app to /Applications
- App icon appears but won't launch
- No error message or window appears

### Most Common Causes

#### 1. Gatekeeper / Code Signing Issue (Most Likely)

**Problem**: macOS blocks unsigned apps from unknown developers.

**Solution A - Right-Click to Open** (Easiest):
```bash
1. Go to /Applications
2. Right-click (or Ctrl+Click) on "Hrisa Docs.app"
3. Select "Open" from context menu
4. Click "Open" in the security dialog
```

This permanently allows the app to run.

**Solution B - System Settings**:
```bash
1. Try to open the app (it will fail)
2. Go to System Settings → Privacy & Security
3. Scroll down to "Security" section
4. You should see: "Hrisa Docs was blocked..."
5. Click "Open Anyway"
6. Try opening the app again
```

**Solution C - Terminal Command** (Advanced):
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine "/Applications/Hrisa Docs.app"

# Then try opening normally
open "/Applications/Hrisa Docs.app"
```

---

#### 2. Missing Dependencies

**Problem**: App can't find required Python libraries or system frameworks.

**Check Logs**:
```bash
# Open Console.app
# Filter for "Hrisa" or "HrisaDocs"
# Look for errors mentioning missing libraries
```

**Common Missing Dependencies**:
- PyQt6
- ChromaDB
- Sentence Transformers
- Ollama (if required at runtime)

**Solution**: These should be bundled in the .app, but if not:
```bash
# Rebuild with all dependencies
python3 scripts/build_macos.py
```

---

#### 3. Corrupted Download

**Problem**: .dmg or .app file was corrupted during download or build.

**Check File Integrity**:
```bash
# Check if .app bundle is valid
spctl -a -vvv "/Applications/Hrisa Docs.app"

# Check bundle structure
ls -la "/Applications/Hrisa Docs.app/Contents/"
ls -la "/Applications/Hrisa Docs.app/Contents/MacOS/"
```

**Expected Output**:
```
/Applications/Hrisa Docs.app/Contents/
├── MacOS/
│   └── DocumentProcessor  (executable)
├── Resources/
├── Info.plist
└── ...
```

**Solution**: Re-download or rebuild the app.

---

#### 4. Python Runtime Issues

**Problem**: PyInstaller executable can't initialize Python runtime.

**Check Crash Logs**:
```bash
# macOS Ventura+
log show --predicate 'processImagePath contains "Hrisa"' --last 1h

# Older macOS
open ~/Library/Logs/DiagnosticReports/
# Look for HrisaDocs or DocumentProcessor crash reports
```

**Common Errors**:
- `dyld: Library not loaded`
- `Fatal Python error: init_fs_encoding`
- `ImportError: No module named...`

**Solution**: Rebuild with proper hidden imports in build script.

---

### Quick Debug Commands

```bash
# Try running from Terminal to see error messages
cd "/Applications/Hrisa Docs.app/Contents/MacOS"
./DocumentProcessor

# Check if executable exists and is executable
ls -l "/Applications/Hrisa Docs.app/Contents/MacOS/DocumentProcessor"

# Check code signature
codesign -dv "/Applications/Hrisa Docs.app"

# Remove app from quarantine
xattr -dr com.apple.quarantine "/Applications/Hrisa Docs.app"
```

---

## Issue: White Background on Icon (FIXED)

**Status**: ✅ Fixed in commit 73108ed

**Problem**: Icon had white/gray background instead of transparent.

**Solution**:
- Removed background using `design/make_transparent.py`
- Regenerated all icon sizes with transparency
- New builds will have transparent icon

**To Get Fix**:
```bash
git pull
# Rebuild app
python3 scripts/build_macos.py
```

---

## General Debugging

### Enable Verbose Logging

Edit build script to add console mode for debugging:

```python
# In scripts/build_macos.py
exe = EXE(
    ...
    console=True,  # Change to True for debugging
    ...
)
```

Rebuild and run - you'll see console output with errors.

### Check System Requirements

**Minimum macOS Version**: 10.13 (High Sierra)
**Recommended**: macOS 12.0+ (Monterey)

**Required**:
- 64-bit Intel or Apple Silicon
- 4GB RAM minimum
- 500MB disk space

---

## Still Not Working?

### Collect Debug Info

```bash
# 1. System info
sw_vers

# 2. App bundle info
plutil -p "/Applications/Hrisa Docs.app/Contents/Info.plist"

# 3. File permissions
ls -la "/Applications/Hrisa Docs.app/Contents/MacOS/"

# 4. Extended attributes
xattr -l "/Applications/Hrisa Docs.app"

# 5. Recent crash logs
open ~/Library/Logs/DiagnosticReports/
```

### Report Issue

If still not working, create GitHub issue with:
1. macOS version (from `sw_vers`)
2. How you installed (downloaded .dmg vs built locally)
3. Error messages from Console.app
4. Output from debug commands above

---

## Building Locally (Most Reliable)

If downloaded builds don't work, build locally:

```bash
# 1. Clone repository
git clone <repo-url>
cd Hrisa-Docs

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -e ".[packaging]"

# 4. Build app
python3 scripts/build_macos.py

# 5. App will be in dist/
open dist/
```

The locally-built version will be unsigned but should work with right-click → Open.

---

## Code Signing (For Distribution)

To properly sign the app (prevents Gatekeeper issues):

```bash
# 1. Get Apple Developer certificate
# Sign up at developer.apple.com

# 2. Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "/Applications/Hrisa Docs.app"

# 3. Verify signature
codesign --verify --deep --strict --verbose=2 \
  "/Applications/Hrisa Docs.app"

# 4. Notarize with Apple (optional but recommended)
# Follow Apple's notarization guide
```

---

## Windows-Specific Issues

### Issue: "Failed to clear database [WinError 32]" When Reinitializing Vector Database

**Symptoms:**
- Error appears when clicking "Tout effacer" (Clear All) or "Ouvrir le dossier" (Open Folder) in Documents tab
- Error message: `[WinError 32] The process cannot access the file because it is being used by another process`
- File path mentions: `chroma.sqlite3-shm` or `leveldb.ldb`

**Root Cause:**
ChromaDB's SQLite and LevelDB files remain locked by the Windows process even after the database client is closed. This is a known Windows file locking issue with ChromaDB.

**Solutions:**

**Solution A - Restart the Application** (Easiest):
1. Close Hrisa Docs completely
2. Reopen the application
3. The vector database will be cleared on restart
4. This releases all file locks

**Solution B - Manual File Deletion**:
1. Close Hrisa Docs
2. Open File Explorer
3. Navigate to: `C:\Users\<YourUsername>\.docprocessor\data\vector_db\`
4. Delete the entire `vector_db` folder
5. Restart Hrisa Docs (folder will be recreated)

**Solution C - Use Task Manager** (If app won't close):
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find "HrisaDocs.exe" or "python.exe" processes
3. End all related processes
4. Wait 10 seconds
5. Try deleting the vector_db folder manually
6. Restart the application

**Prevention:**
- Avoid rapidly clearing/reinitializing the database
- Always restart the app after major database operations
- This issue will be addressed in a future update

---

## Quick Fix Checklist

- [ ] Right-click → Open (bypass Gatekeeper)
- [ ] Check System Settings → Security for block message
- [ ] Remove quarantine: `xattr -d com.apple.quarantine "/Applications/Hrisa Docs.app"`
- [ ] Run from Terminal to see errors: `"/Applications/Hrisa Docs.app/Contents/MacOS/DocumentProcessor"`
- [ ] Check Console.app for crash logs
- [ ] Try rebuilding locally with `python3 scripts/build_macos.py`

---

## Contact

If none of these solutions work, please file an issue at:
https://github.com/<username>/Hrisa-Docs/issues

Include your macOS version and error messages!
