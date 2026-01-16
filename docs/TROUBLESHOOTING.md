# Troubleshooting Guide

Common issues and solutions for Hrisa Docs.

## Table of Contents
- [Installation Issues](#installation-issues)
- [Application Launch Issues](#application-launch-issues)
- [Ollama Connection Issues](#ollama-connection-issues)
- [Document Processing Issues](#document-processing-issues)
- [Theme Discovery Issues](#theme-discovery-issues)
- [Synthesis Issues](#synthesis-issues)
- [PDF Export Issues](#pdf-export-issues)
- [Performance Issues](#performance-issues)
- [GUI Issues](#gui-issues)
- [Data and Storage Issues](#data-and-storage-issues)
- [Getting More Help](#getting-more-help)

---

## Installation Issues

### macOS: "Cannot open app from unidentified developer"

**Problem**: Security warning when opening the app.

**Solution**:
```bash
# Option 1: Right-click → Open (first time only)
# Right-click the app → Open → Click "Open" in dialog

# Option 2: Remove quarantine attribute
xattr -d com.apple.quarantine "/Applications/Hrisa Docs.app"
```

**Alternative**:
System Preferences → Security & Privacy → Click "Open Anyway"

### Windows: SmartScreen Warning

**Problem**: "Windows protected your PC" warning.

**Solution**:
1. Click "More info"
2. Click "Run anyway"

**For repeated warnings**:
- Right-click installer → Properties → Unblock → Apply

### Dependencies Installation Fails

**Problem**: `pip install` or `make setup` fails.

**Solution**:
```bash
# Ensure Python 3.11+ is installed
python --version

# Try upgrading pip
pip install --upgrade pip

# Install dependencies one at a time to identify issue
pip install PyQt6
pip install chromadb
pip install sentence-transformers
```

---

## Application Launch Issues

### Application Doesn't Start

**macOS**:
```bash
# Check if quarantine attribute is present
xattr -l "/Applications/Hrisa Docs.app"

# Remove all extended attributes
xattr -cr "/Applications/Hrisa Docs.app"

# Try launching from terminal
open "/Applications/Hrisa Docs.app"
```

**Windows**:
- Run as Administrator
- Check Task Manager for existing instances
- Check Windows Event Viewer for errors

### Application Crashes on Startup

**Check logs**:
```bash
# macOS/Linux
cat ~/.docprocessor/logs/docprocessor.log

# Windows
type %USERPROFILE%\.docprocessor\logs\docprocessor.log
```

**Common causes**:
1. Corrupted preferences file
2. Missing dependencies
3. Conflicting Python installations

**Solution**:
```bash
# Reset preferences
rm ~/.docprocessor/preferences.json

# macOS/Linux
rm -rf ~/.docprocessor/data/vector_db/*

# Windows
rmdir /s /q %USERPROFILE%\.docprocessor\data\vector_db
```

### "No module named 'docprocessor'" Error

**Problem**: Running from source, module not found.

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install in editable mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

---

## Ollama Connection Issues

### "Failed to connect to Ollama" Error

**Check if Ollama is running**:
```bash
# Test connection
curl http://localhost:11434/api/version

# Should return: {"version":"0.x.x"}
```

**If not running**:
```bash
# macOS/Linux
ollama serve

# Windows
# Check Services → Ollama → Start
# Or restart Ollama from system tray
```

**Check firewall**:
- Ensure port 11434 is not blocked
- Add Ollama to firewall exceptions

### Model Not Found

**Problem**: "Model 'llama3.1:latest' not found".

**Solution**:
```bash
# List installed models
ollama list

# Pull required model
ollama pull llama3.1:latest

# Verify model is available
ollama list | grep llama3.1
```

### Ollama Connection Timeout

**Problem**: Connection times out or very slow.

**Solutions**:
1. **Check system resources**:
   - Close other applications
   - Ensure 8GB+ RAM available
   - Check CPU usage

2. **Restart Ollama**:
   ```bash
   # macOS/Linux
   pkill ollama
   ollama serve

   # Windows
   # Restart from Services or system tray
   ```

3. **Check Ollama logs**:
   ```bash
   # macOS
   cat ~/.ollama/logs/server.log

   # Linux
   journalctl -u ollama

   # Windows
   # Check: C:\Users\<username>\.ollama\logs\
   ```

---

## Document Processing Issues

### PDF Import Fails

**Problem**: "Failed to import document" error.

**Common causes**:
1. **Corrupted PDF**: Try opening PDF in another viewer
2. **Password protected**: Remove password first
3. **Scanned PDF without OCR**: Use OCR tool first (not yet supported)

**Solution**:
```bash
# Test PDF with PyMuPDF
python -c "import fitz; doc=fitz.open('your_file.pdf'); print(doc.page_count)"
```

**Workarounds**:
- Export PDF to new PDF from Adobe Reader
- Convert to text file first
- Use PDF repair tool

### Processing Stuck at 0%

**Problem**: Document processing doesn't progress.

**Check**:
1. Look at application logs
2. Check if Ollama is responding
3. Verify disk space available

**Solution**:
```bash
# Check disk space
df -h  # macOS/Linux
dir    # Windows

# Restart application
# Try processing single document first
```

### "No chunks found" After Processing

**Problem**: Documents processed but chunk count is 0.

**Causes**:
- PDF contains only images (no text)
- Text extraction failed
- Document is empty

**Solution**:
1. Verify PDF contains text:
   - Try copying text from PDF
   - Check if it's a scanned document
2. Use OCR if needed (external tool)
3. Try different PDF format

### Processing Very Slow

**Problem**: Processing takes much longer than expected.

**Expected times** (per 100 pages):
- Text extraction: 10-30 seconds
- Chunking: < 1 second
- Embedding: 30-60 seconds
- Storage: 10-20 seconds

**Solutions**:
1. **Close other applications**
2. **Process smaller batches**: 5-10 documents at a time
3. **Check RAM usage**: Ensure 4GB+ available
4. **Disable antivirus temporarily**: May scan files during processing

---

## Theme Discovery Issues

### Themes Are Too Generic

**Problem**: Themes like "General Content", "Miscellaneous Topics".

**Causes**:
- Not enough documents processed
- Documents are too similar
- Number of themes too high

**Solutions**:
1. **Process more documents**: At least 5-10 documents recommended
2. **Reduce number of themes**: Try 3-5 themes instead of 10+
3. **Review chunk settings**: Increase chunk size for better context

### Theme Discovery Fails

**Problem**: "Error discovering themes" message.

**Check**:
```bash
# Verify documents are processed
# Check: Documents tab shows N chunks

# Check Ollama is responding
curl http://localhost:11434/api/tags
```

**Solution**:
```bash
# Clear vector database and reprocess
# Menu → Documents → Clear Database
# Process documents again
```

### Themes Show Full LLM Responses

**Problem**: Themes show long text instead of clean labels.

**This should be fixed in packaged app**. If still occurring:
1. Verify you're using latest version
2. Check `config/prompts.yaml` exists
3. Review application logs

---

## Synthesis Issues

### Synthesis Stuck at 0%

**Problem**: Synthesis doesn't progress beyond initialization.

**Common causes**:
1. Ollama not responding
2. Not enough memory
3. Theme discovery not completed

**Solution**:
```bash
# Check Ollama
curl http://localhost:11434/api/version

# Check system resources
# Close other applications

# Verify themes are discovered
# Go to Themes tab, should show themes
```

### Synthesis Produces Poor Quality Output

**Problem**: Generated text is incoherent or repetitive.

**Solutions**:
1. **Adjust synthesis level**:
   - Try "Comprehensive" for more detailed output
   - Try "Short" if output is too verbose

2. **Increase chunks per chapter**:
   - Default: 150 chunks
   - Try: 200-300 for more comprehensive

3. **Improve source material**:
   - Ensure documents are high quality
   - Process more related documents
   - Remove low-quality documents

4. **Use better LLM model**:
   ```bash
   # Install larger model
   ollama pull llama3:70b

   # Change in: Settings → Model Settings
   ```

### Synthesis Crashes or Fails

**Check logs**:
```bash
tail -f ~/.docprocessor/logs/docprocessor.log
```

**Common issues**:
1. **Out of memory**: Close other apps, reduce batch size
2. **Ollama timeout**: Increase timeout in settings
3. **Storage full**: Check disk space

---

## PDF Export Issues

### "Pandoc not found" Error

**Solution**:
```bash
# macOS
brew install pandoc

# Windows
# Download from: https://pandoc.org/installing.html

# Verify installation
pandoc --version
```

### "XeLaTeX not found" Error

**macOS**:
```bash
# Install MacTeX
brew install --cask mactex-no-gui

# Update PATH
eval "$(/usr/libexec/path_helper)"

# Or restart terminal

# Verify
xelatex --version
```

**Windows**:
```bash
# Install MiKTeX from: https://miktex.org/download

# Add to PATH:
# C:\Program Files\MiKTeX\miktex\bin\x64\

# Restart terminal
# Verify
xelatex --version
```

### PDF Generation Very Slow

**First PDF generation**:
- Takes 30-60 seconds (normal)
- LaTeX packages are being installed
- Subsequent PDFs will be faster (10-20 seconds)

**Always slow**:
1. Check if antivirus is scanning files
2. Verify disk is not full
3. Try generating smaller document first

### PDF Has Formatting Issues

**Common issues**:
1. **Missing fonts**: XeLaTeX should handle most fonts
2. **Unicode issues**: XeLaTeX handles Unicode better than pdflatex
3. **Images not displaying**: Check source markdown

**Workarounds**:
- Export to DOCX instead and convert manually
- Export to Markdown and use online converter
- Edit LaTeX template in `output_formatter.py`

### PDF Export Leaves Temp Files

**Problem**: `.md` temp files left in output directory.

**This should be fixed**. If still occurring:
```bash
# Manual cleanup
rm ~/.docprocessor/data/output/*.md

# Or use GUI: Files tab → Delete temp files
```

---

## Performance Issues

### High Memory Usage

**Problem**: Application uses > 4GB RAM.

**Normal usage**:
- Idle: 200-500 MB
- Processing: 1-2 GB
- Synthesis: 2-4 GB

**Solutions**:
1. **Process smaller batches**: 5-10 documents at a time
2. **Reduce chunk size**: Settings → Chunk Settings → 800 tokens
3. **Close other applications**
4. **Restart application** after heavy operations

### Slow GUI Response

**Problem**: Interface is sluggish or unresponsive.

**Solutions**:
1. **Check for background operations**: Look at status bar
2. **Reduce size profile**: Settings → Appearance → Small profile
3. **Clear old projects**: Remove unused projects
4. **Restart application**

### Vector Search Slow

**Problem**: Theme discovery or synthesis is very slow.

**Solutions**:
1. **Rebuild vector database**:
   ```bash
   # Clear database
   rm -rf ~/.docprocessor/data/vector_db/*

   # Reprocess documents
   ```

2. **Reduce embedding batch size** (edit settings.py):
   ```python
   EMBEDDING_BATCH_SIZE = 16  # Default: 32
   ```

---

## GUI Issues

### Display Issues (macOS Dark Mode)

**Problem**: Text not visible, colors wrong.

**Solution**:
```bash
# Force theme in application
# Settings → Appearance → Select theme manually
# Dark or Light
```

### Window Size Issues

**Problem**: Window too large or too small.

**Solutions**:
1. **Change size profile**: Settings → Appearance → Size Profile
   - Large: For accessibility
   - Medium: Balanced (default)
   - Small: Compact

2. **Reset window preferences**:
   ```bash
   rm ~/.docprocessor/preferences.json
   # Restart application
   ```

### Arabic Text Not Displaying Correctly

**Problem**: Arabic text appears as boxes or reversed.

**Solution**:
1. Ensure system has Arabic fonts installed
2. Application should handle RTL automatically
3. Try restarting application

### Menus Not in Selected Language

**Problem**: Changed language but menus still in old language.

**Solution**:
- Restart application (some translations require restart)
- Check: Settings → Appearance → Language

---

## Data and Storage Issues

### Project Files Corrupted

**Problem**: "Failed to load project" error.

**Solution**:
```bash
# Check project file
cat ~/.docprocessor/data/projects/project_name.json

# If corrupted, restore from backup (if available)
# Or create new project and re-import documents
```

### Vector Database Corrupted

**Problem**: "Database error" or crashes during search.

**Solution**:
```bash
# Backup project metadata
cp ~/.docprocessor/data/projects/*.json ~/backup/

# Clear vector database
rm -rf ~/.docprocessor/data/vector_db/*

# Reprocess all documents in project
```

### Running Out of Disk Space

**Problem**: "No space left on device".

**Check usage**:
```bash
# macOS/Linux
du -sh ~/.docprocessor/data/*

# Windows
dir /s %USERPROFILE%\.docprocessor\data
```

**Cleanup**:
```bash
# Delete old project outputs
rm ~/.docprocessor/data/output/*.pdf
rm ~/.docprocessor/data/output/*.docx

# Or use GUI: Files tab → Delete all outputs

# Remove old projects
# Project dashboard → Delete unused projects
```

### Cannot Find Generated Files

**Problem**: Files generated but not showing in GUI.

**Location**:
```bash
# macOS/Linux
ls -la ~/.docprocessor/data/output/

# Windows
dir %USERPROFILE%\.docprocessor\data\output\
```

**Solution**:
1. Click "Refresh" button in Files tab
2. Verify output directory exists
3. Check file permissions

### Project Management Issues

**Problem**: Cannot duplicate project.

**Solution**:
1. Ensure only ONE project is selected
2. Check disk space is available
3. Try renaming the duplicate to avoid name conflicts

**Problem**: Bulk delete not working.

**Solution**:
1. Select multiple projects with Cmd/Ctrl+Click or Shift+Click
2. Delete button should show count: "Supprimer (3)"
3. If button stays disabled, try clicking projects again
4. Check logs for permission errors

**Problem**: Context menu doesn't appear on right-click.

**Solution**:
- **macOS**: Use two-finger tap or Control+Click
- **Windows**: Ensure right mouse button is working
- Try clicking the project first, then right-clicking
- If still not working, use the buttons at the bottom instead

**Problem**: Archived projects disappeared.

**Solution**:
1. Open project dashboard (Cmd/Ctrl+Shift+P)
2. Change filter dropdown to "Archivés"
3. Archived projects will appear
4. Right-click → "♻️ Restore" to unarchive

---

## Getting More Help

### Check Application Logs

**macOS/Linux**:
```bash
# View logs in real-time
tail -f ~/.docprocessor/logs/docprocessor.log

# View full log
less ~/.docprocessor/logs/docprocessor.log

# Search logs
grep -i error ~/.docprocessor/logs/docprocessor.log
```

**Windows**:
```powershell
# View logs
Get-Content -Tail 50 -Wait "$env:USERPROFILE\.docprocessor\logs\docprocessor.log"

# Full log
notepad "$env:USERPROFILE\.docprocessor\logs\docprocessor.log"
```

### Enable Debug Logging

Edit `config/settings.py`:
```python
LOG_LEVEL = "DEBUG"  # Change from "INFO"
```

Restart application - logs will be much more detailed.

### Reset Application to Defaults

**Complete reset** (will lose all data):
```bash
# macOS/Linux
rm -rf ~/.docprocessor/

# Windows
rmdir /s /q %USERPROFILE%\.docprocessor
```

**Restart application** - will recreate default configuration.

### Collect Diagnostic Information

Before reporting issues, collect:

1. **Application logs**:
   ```bash
   cp ~/.docprocessor/logs/docprocessor.log ~/diagnostic_info.log
   ```

2. **System information**:
   ```bash
   # macOS
   system_profiler SPSoftwareDataType > ~/system_info.txt

   # Windows
   systeminfo > %USERPROFILE%\system_info.txt
   ```

3. **Installed packages** (from source):
   ```bash
   pip list > ~/installed_packages.txt
   ```

4. **Ollama status**:
   ```bash
   curl http://localhost:11434/api/version > ~/ollama_status.txt
   ollama list >> ~/ollama_status.txt
   ```

### Report Issues

When reporting issues, include:
- Description of the problem
- Steps to reproduce
- Application logs
- System information
- Screenshots (if GUI issue)

---

## Common Error Messages

### "ChromaDB error: Collection not found"

**Solution**:
```bash
# Recreate collection - clear database and reprocess
# Menu → Documents → Clear Database
```

### "Embedding model download failed"

**Problem**: No internet or model not available.

**Solution**:
1. Check internet connection
2. Model will download on first use (500MB-1GB)
3. Wait for download to complete
4. Restart application if stuck

### "Failed to generate chapter"

**Problem**: LLM generation error.

**Solution**:
1. Check Ollama is running
2. Verify model is loaded: `ollama list`
3. Check Ollama logs for errors
4. Try regenerating specific chapter

### "Permission denied" Errors

**macOS/Linux**:
```bash
# Fix permissions
chmod -R u+w ~/.docprocessor/
```

**Windows**:
- Run application as Administrator
- Check folder permissions
- Move data folder to user directory

---

## Still Having Issues?

1. **Read the docs**: Check [User Guide](USER_GUIDE.md) and [Installation Guide](INSTALLATION.md)
2. **Search existing issues**: Someone may have had the same problem
3. **Check logs**: Most errors are explained in logs
4. **Ask for help**: Provide logs and system information

---

**Remember**: Most issues can be resolved by:
1. Restarting the application
2. Checking Ollama is running
3. Clearing caches and rebuilding
4. Reviewing application logs

Good luck! 🍀
