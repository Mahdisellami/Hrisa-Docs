# PDF Export Setup Guide

PDF export requires **pandoc** and a **LaTeX distribution** to convert Markdown to professionally formatted PDF documents.

## macOS Setup

### 1. Install Pandoc
```bash
brew install pandoc
```

### 2. Install MacTeX (LaTeX distribution)
```bash
brew install --cask mactex-no-gui
```

After installation, restart your terminal or run:
```bash
eval "$(/usr/libexec/path_helper)"
```

### 3. Verify Installation
```bash
pandoc --version
xelatex --version
```

## Windows Setup

### 1. Install Pandoc

**Option A: Using Installer (Recommended)**
1. Download from: https://pandoc.org/installing.html
2. Run the installer (pandoc-3.x-windows-x86_64.msi)
3. Restart your terminal

**Option B: Using Chocolatey**
```powershell
choco install pandoc
```

### 2. Install MiKTeX (LaTeX distribution)

**Option A: Using Installer (Recommended)**
1. Download from: https://miktex.org/download
2. Run the installer (basic-miktex-x.x-x64.exe)
3. During setup, choose "Install missing packages on-the-fly: Yes"
4. Restart your terminal

**Option B: Using Chocolatey**
```powershell
choco install miktex
```

### 3. Configure MiKTeX
After installation, open MiKTeX Console and:
- Settings → General → "Install missing packages on-the-fly" → **Always**
- Check for updates

### 4. Verify Installation
```powershell
pandoc --version
xelatex --version
```

## Testing PDF Export

Run this test command:
```bash
# Create test markdown
echo "# Test Document\n\nThis is a test." > test.md

# Convert to PDF
pandoc test.md -o test.pdf --pdf-engine=xelatex

# Open the PDF
open test.pdf  # macOS
start test.pdf # Windows
```

If the PDF is generated successfully, your system is ready!

## Troubleshooting

### macOS

**Issue**: `xelatex: command not found`
```bash
eval "$(/usr/libexec/path_helper)"
# Or restart your terminal
```

**Issue**: Permission denied
```bash
sudo chown -R $(whoami) /usr/local/texlive
```

### Windows

**Issue**: `pandoc: xelatex not found`
- Add MiKTeX bin folder to PATH:
  - `C:\Program Files\MiKTeX\miktex\bin\x64\`
- Restart terminal

**Issue**: "pdflatex: The memory dump file could not be found"
- Open MiKTeX Console
- Click "Refresh file name database"
- Update packages

**Issue**: Font issues in PDF
- XeLaTeX handles Unicode better than pdflatex
- Ensure you're using `--pdf-engine=xelatex`

### Both Platforms

**Issue**: PDF generation is slow
- First run installs LaTeX packages (can take several minutes)
- Subsequent runs will be much faster

**Issue**: Missing packages
- macOS: Reinstall MacTeX
- Windows: MiKTeX should auto-install packages

## PDF Templates

The application supports three PDF templates:

- **Academic**: Report class, 12pt, table of contents, colored links
- **Professional**: Article class, 11pt, table of contents
- **Simple**: Article class, 12pt, minimal formatting

Templates can be customized by editing `output_formatter.py`.

## Performance Notes

- **First PDF generation**: 30-60 seconds (installs LaTeX packages)
- **Subsequent generations**: 10-20 seconds
- **Large documents (50+ pages)**: 30-60 seconds

## Alternative: Use Online Converter

If you cannot install LaTeX:
1. Export to **Markdown** format
2. Use an online converter like:
   - https://www.markdowntopdf.com/
   - https://dillinger.io/ (export as PDF)
