# Installation Guide

Complete installation guide for Hrisa Docs on macOS and Windows.

## Table of Contents
- [System Requirements](#system-requirements)
- [Option 1: Packaged Application (Recommended)](#option-1-packaged-application-recommended)
- [Option 2: From Source (Developers)](#option-2-from-source-developers)
- [Required Dependencies](#required-dependencies)
- [First-Time Setup](#first-time-setup)
- [Verification](#verification)

---

## System Requirements

### Minimum Requirements
- **OS**: macOS 12+ or Windows 10+
- **RAM**: 8 GB (16 GB recommended)
- **Disk Space**: 5 GB free space
  - Application: ~1.5 GB
  - Ollama + models: ~2-3 GB
  - Working space: ~1 GB
- **Display**: 1280x720 minimum (1920x1080 recommended)

### Required Software
- **Ollama**: For local LLM processing (required)
- **Pandoc**: For document export (optional, for PDF export)
- **XeLaTeX**: For PDF generation (optional, for PDF export)

---

## Option 1: Packaged Application (Recommended)

### macOS

#### Step 1: Download the Application
Download `Hrisa Docs.app` or `HrisaDocs.dmg` from the releases.

#### Step 2: Install
If you have a DMG file:
```bash
# Open the DMG
open HrisaDocs-0.1.0-macOS.dmg

# Drag "Hrisa Docs.app" to Applications folder
```

If you have the .app directly:
```bash
# Move to Applications
mv "Hrisa Docs.app" /Applications/
```

#### Step 3: First Launch
1. Open Applications folder
2. Right-click "Hrisa Docs.app"
3. Select "Open" (first time only - bypasses Gatekeeper)
4. Click "Open" in the security dialog

> **Note**: macOS may show a security warning for unsigned apps. This is normal for development builds.

#### Alternative: Using Terminal
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine "/Applications/Hrisa Docs.app"

# Open the app
open "/Applications/Hrisa Docs.app"
```

### Windows

#### Step 1: Download the Application
Download `HrisaDocs-Setup.exe` from the releases.

#### Step 2: Install
1. Run `HrisaDocs-Setup.exe`
2. Follow the installation wizard
3. Choose installation directory (default: `C:\Program Files\HrisaDocs`)
4. Create desktop shortcut (recommended)

#### Step 3: First Launch
1. Double-click the desktop shortcut or
2. Start Menu → Hrisa Docs

> **Note**: Windows may show SmartScreen warning. Click "More info" → "Run anyway".

---

## Option 2: From Source (Developers)

### Prerequisites
- Python 3.11 or higher
- Git
- Make (macOS/Linux) or equivalent on Windows

### Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd Document-Processing

# Setup virtual environment and install dependencies
make setup

# Run the application
make run
```

### Manual Setup (Without Make)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .

# Run application
python -m docprocessor.gui
```

---

## Required Dependencies

### 1. Ollama (Required)

Ollama provides the local LLM for document synthesis.

#### macOS

```bash
# Option A: Download installer
# Visit: https://ollama.ai/download
# Download and run the installer

# Option B: Using Homebrew
brew install ollama

# Start Ollama service
ollama serve
```

#### Windows

```bash
# Download installer from: https://ollama.ai/download
# Run the installer
# Ollama will start automatically

# Or using PowerShell
winget install Ollama.Ollama
```

#### Install Required Model

```bash
# Pull the default model (llama3.1, ~4GB)
ollama pull llama3.1:latest

# Verify installation
ollama list
```

#### Verify Ollama is Running

```bash
# Test connection
curl http://localhost:11434/api/version

# Should return: {"version":"0.x.x"}
```

### 2. Pandoc (Optional - for PDF Export)

#### macOS

```bash
# Using Homebrew
brew install pandoc

# Verify installation
pandoc --version
```

#### Windows

**Option A: Installer (Recommended)**
1. Download from: https://pandoc.org/installing.html
2. Run installer: `pandoc-3.x-windows-x86_64.msi`
3. Restart terminal

**Option B: Chocolatey**
```powershell
choco install pandoc
```

### 3. XeLaTeX (Optional - for PDF Export)

XeLaTeX is part of TeX Live (macOS) or MiKTeX (Windows).

#### macOS - Install MacTeX

```bash
# Option A: Using Homebrew (Recommended)
brew install --cask mactex-no-gui

# Wait for installation (~4 GB download)

# Update PATH
eval "$(/usr/libexec/path_helper)"

# Or restart terminal
```

**Option B: Full MacTeX (includes GUI tools)**
```bash
brew install --cask mactex
```

#### Windows - Install MiKTeX

**Option A: Installer (Recommended)**
1. Download from: https://miktex.org/download
2. Run installer: `basic-miktex-x.x-x64.exe`
3. During setup:
   - Choose "Install missing packages on-the-fly: Yes"
   - Select user or system-wide installation
4. Restart terminal

**Option B: Chocolatey**
```powershell
choco install miktex
```

**Configure MiKTeX**
1. Open MiKTeX Console
2. Settings → General → Install missing packages: **Always**
3. Check for updates

#### Verify LaTeX Installation

```bash
# Check XeLaTeX
xelatex --version

# Should show: XeTeX 3.x...
```

---

## First-Time Setup

### 1. Launch Application

```bash
# Packaged app (macOS)
open "/Applications/Hrisa Docs.app"

# Packaged app (Windows)
# Use Start Menu or desktop shortcut

# From source
make run
```

### 2. Initial Configuration

The application will create configuration directories:

**macOS/Linux:**
```
~/.docprocessor/
├── preferences.json    # User preferences
├── data/              # Application data
│   ├── projects/      # Project files
│   ├── vector_db/     # Vector database
│   └── output/        # Generated documents
└── logs/              # Application logs
```

**Windows:**
```
C:\Users\<username>\.docprocessor\
├── preferences.json
├── data\
│   ├── projects\
│   ├── vector_db\
│   └── output\
└── logs\
```

### 3. Select Language

On first launch:
1. Menu → Settings → Appearance
2. Select your language: French, English, or Arabic
3. Application will update immediately

### 4. Configure Settings (Optional)

**Menu → Settings → Model Settings:**
- Ollama Model: `llama3.1:latest` (default)
- Embedding Model: `all-MiniLM-L6-v2` (default)

**Menu → Settings → Chunk Settings:**
- Chunk Size: 1000 tokens (default)
- Chunk Overlap: 100 tokens (default)

---

## Verification

### Test Ollama Connection

```bash
# From terminal
curl http://localhost:11434/api/version

# Should return version information
```

**In the application:**
1. Create a test project
2. Import a PDF document
3. Click "Process Documents"
4. If successful, Ollama is working ✓

### Test PDF Export (Optional)

```bash
# Create test markdown
echo "# Test Document" > test.md
echo "" >> test.md
echo "This is a test paragraph." >> test.md

# Convert to PDF
pandoc test.md -o test.pdf --pdf-engine=xelatex

# If test.pdf is created, PDF export is working ✓
```

**In the application:**
1. Complete a synthesis
2. Select "PDF" as output format
3. If PDF is generated successfully, export is working ✓

### Test Full Workflow

1. **Create Project**: Menu → Project → New Project
2. **Import Document**: Menu → File → Import (select a PDF)
3. **Process**: Documents tab → Process Documents
4. **Discover Themes**: Themes tab → Discover Themes
5. **Synthesize**: Synthesis tab → Start Synthesis
6. **Verify Output**: Files tab → Generated Documents

If all steps complete successfully, installation is complete! ✓

---

## Troubleshooting

### Application Won't Start

**macOS:**
```bash
# Check for quarantine attribute
xattr "/Applications/Hrisa Docs.app"

# Remove quarantine
xattr -d com.apple.quarantine "/Applications/Hrisa Docs.app"
```

**Windows:**
- Run as Administrator
- Check Windows Defender/Antivirus logs
- Reinstall from installer

### Ollama Connection Failed

**Check if Ollama is running:**
```bash
# macOS/Linux
ps aux | grep ollama

# Windows
tasklist | findstr ollama
```

**Start Ollama:**
```bash
# macOS/Linux
ollama serve

# Windows
# Ollama runs as a service, restart from Services
```

**Check firewall:**
- Ensure port 11434 is not blocked
- Allow Ollama through firewall

### PDF Export Fails

**Error: "pandoc not found"**
- Reinstall pandoc
- Add pandoc to PATH
- Restart application

**Error: "xelatex not found"**
```bash
# macOS
eval "$(/usr/libexec/path_helper)"

# Windows
# Add to PATH: C:\Program Files\MiKTeX\miktex\bin\x64\
```

**First PDF takes long time:**
- Normal - LaTeX packages are being installed
- Subsequent exports will be faster

### Application Logs

Check logs for detailed error information:

**macOS/Linux:**
```bash
tail -f ~/.docprocessor/logs/docprocessor.log
```

**Windows:**
```powershell
Get-Content -Tail 50 -Wait "$env:USERPROFILE\.docprocessor\logs\docprocessor.log"
```

---

## Next Steps

After successful installation:

1. **Read the [User Guide](USER_GUIDE.md)** for detailed feature documentation
2. **Follow the [Quick Start](QUICKSTART.md)** for your first project
3. **Check [Troubleshooting Guide](TROUBLESHOOTING.md)** if you encounter issues

---

## Getting Help

- **Documentation**: See `docs/` folder
- **Logs**: `~/.docprocessor/logs/docprocessor.log`
- **Issues**: Check existing issues or create new one
- **Community**: [Link to community/forum if available]

---

## Updating

### Packaged Application

Download and install the new version:
- macOS: Replace old .app with new one
- Windows: Run new installer (will upgrade existing installation)

Your data in `~/.docprocessor/` is preserved across updates.

### From Source

```bash
# Pull latest changes
git pull origin main

# Update dependencies
make setup

# Restart application
make run
```

---

**Installation complete!** 🎉

Ready to synthesize your documents into comprehensive books.
