# Building for Windows

Complete guide to building Hrisa Docs for Windows distribution.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Manual Build Process](#manual-build-process)
- [Automated Build (CI/CD)](#automated-build-cicd)
- [Testing the Build](#testing-the-build)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)

---

## Prerequisites

### Required Software

1. **Windows 10 or 11** (64-bit)
2. **Python 3.11+**
   ```powershell
   # Check Python version
   python --version
   # Should show: Python 3.11.x or higher
   ```

3. **Git**
   - Download from: https://git-scm.com/download/win
   - Or: `winget install Git.Git`

4. **Visual C++ Build Tools** (for some dependencies)
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Or: `winget install Microsoft.VisualStudio.2022.BuildTools`

### Optional (for installer)

**Inno Setup** (creates installer .exe):
```powershell
# Using Chocolatey
choco install innosetup -y

# Or download from: https://jrsoftware.org/isdl.php
```

---

## Manual Build Process

### Step 1: Clone Repository

```powershell
# Clone repository
git clone <repository-url>
cd Document-Processing
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies

```powershell
# Install project dependencies
pip install -e .

# Install build tools
pip install pyinstaller
```

### Step 4: Build Application

```powershell
# Run build script
python scripts\build_windows.py
```

**Build process steps**:
1. Cleans previous builds
2. Creates PyInstaller spec file
3. Builds standalone executable
4. Creates installer (if Inno Setup installed)

**Expected output**:
```
============================================================
Building Hrisa Docs for Windows
============================================================
✓ PyInstaller 6.x.x found

Cleaning previous builds...
  Removed build/
  Removed dist/

Creating spec file...
✓ Created spec file: HrisaDocs.spec

Building application...
This may take several minutes...

✓ Build completed successfully!

Creating installer with Inno Setup...
✓ Created installer: dist/HrisaDocs-0.1.0-Setup.exe

============================================================
Build Summary
============================================================
✓ Executable: dist/HrisaDocs.exe
  Size: ~500 MB

✓ Installer: dist/HrisaDocs-0.1.0-Setup.exe
  Size: ~280 MB

Next steps:
1. Test the executable: dist\HrisaDocs.exe
2. Distribute the installer to users
```

### Step 5: Verify Build

```powershell
# Check build artifacts
dir dist\

# Should show:
# - HrisaDocs.exe (standalone executable)
# - HrisaDocs-0.1.0-Setup.exe (installer)
```

---

## Build Script Details

### What the Build Script Does

The `scripts/build_windows.py` script:

1. **Cleans previous builds**:
   - Removes `build/` directory
   - Removes `dist/` directory

2. **Creates PyInstaller spec file**:
   - Configures application metadata
   - Specifies hidden imports for dependencies
   - Bundles data files (config, prompts)
   - Sets up exclusions to reduce size

3. **Builds with PyInstaller**:
   - Creates standalone executable
   - Bundles Python runtime
   - Includes all dependencies
   - Compresses to single directory

4. **Creates installer** (if Inno Setup available):
   - Professional installer with wizard
   - Creates Start Menu shortcuts
   - Adds uninstall entry
   - ~280 MB installer from ~1.5 GB application

### Customizing the Build

Edit `scripts/build_windows.py` to customize:

```python
# Hidden imports (for modules PyInstaller misses)
hiddenimports = [
    'chromadb',
    'chromadb.api.rust',
    # Add your modules here
]

# Exclude unnecessary modules (reduces size)
excludes = [
    'tkinter',
    'matplotlib',
    # Add modules to exclude
]

# Data files to bundle
datas = [
    ('config/', 'config'),
    # Add your data files
]
```

---

## Automated Build (CI/CD)

### Using GitHub Actions

The repository includes GitHub Actions workflow for automated builds.

**Workflow file**: `.github/workflows/build.yml`

### Trigger Builds

**Automatically triggered on**:
- Push to `main` or `develop` branch
- Pull requests to `main`
- Creating version tags (e.g., `v0.1.0`)

**Manual trigger**:
1. Go to GitHub repository
2. Actions tab
3. Select "Build Hrisa Docs" workflow
4. Click "Run workflow"

### Download Build Artifacts

**From workflow run**:
1. Go to Actions tab
2. Click on the workflow run
3. Scroll to "Artifacts" section
4. Download:
   - `HrisaDocs-Windows-exe` (standalone executable)
   - `HrisaDocs-Windows-installer` (setup executable)

**Artifacts retention**: 90 days

### Creating Releases

**To create a release with installers**:

```bash
# Create and push a version tag
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions will:
1. Build for Windows and macOS
2. Run tests
3. Create checksums
4. Create GitHub release
5. Upload installers as release assets

---

## Testing the Build

### Test Standalone Executable

```powershell
# Run the executable
.\dist\HrisaDocs.exe

# Check if it launches correctly
# Test basic functionality:
# 1. Create a project
# 2. Import a PDF
# 3. Verify UI responds
```

### Test Installer

```powershell
# Run installer
.\dist\HrisaDocs-0.1.0-Setup.exe

# Test installation:
# 1. Follow installation wizard
# 2. Check Start Menu shortcut created
# 3. Launch from Start Menu
# 4. Test application functionality
# 5. Uninstall via Control Panel
```

### Test on Clean System

**Virtual machine testing** (recommended):
1. Create Windows 10/11 VM
2. Install only:
   - Windows updates
   - Ollama (required dependency)
3. Run installer
4. Test full workflow

**Test checklist**:
- [ ] Installer runs without errors
- [ ] Application launches
- [ ] Can create project
- [ ] Can import documents
- [ ] Can process documents (with Ollama)
- [ ] Can discover themes
- [ ] Can synthesize document
- [ ] Can export to DOCX/Markdown
- [ ] PDF export (if pandoc/LaTeX installed)
- [ ] Uninstaller removes all files

---

## Troubleshooting

### Build Fails: Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```powershell
# Ensure all dependencies installed
pip install -e .

# Check for hidden import in spec file
# Edit scripts/build_windows.py, add to hiddenimports:
hiddenimports = [
    'missing_module',
]
```

### Build Fails: PyInstaller Error

**Error**: `RecursionError: maximum recursion depth exceeded`

**Solution**:
```powershell
# Increase recursion limit
$env:RECURSION_LIMIT=5000
python scripts\build_windows.py
```

### Executable Won't Run: Missing DLL

**Error**: Application fails to start with DLL error

**Solution**:
1. Ensure Visual C++ Redistributable installed:
   ```powershell
   winget install Microsoft.VCRedist.2015+.x64
   ```
2. Rebuild application

### Executable Flagged by Antivirus

**Problem**: Windows Defender or antivirus blocks executable

**Solution**:
1. **Code signing** (recommended for distribution):
   - Purchase code signing certificate
   - Sign executable with signtool

2. **Temporary**: Add exception in antivirus

3. **Submit to Microsoft**:
   - False positives can be reported to Microsoft

### Inno Setup Not Found

**Error**: `Inno Setup not found, skipping installer creation`

**Solution**:
```powershell
# Install Inno Setup
choco install innosetup -y

# Or download from: https://jrsoftware.org/isdl.php

# Ensure ISCC.exe is in PATH
$env:PATH += ";C:\Program Files (x86)\Inno Setup 6"

# Rebuild
python scripts\build_windows.py
```

### Build Very Slow

**Problem**: Build takes > 20 minutes

**Solutions**:
1. Disable antivirus temporarily
2. Exclude project directory from real-time scanning
3. Use SSD for faster I/O
4. Close other applications

### Executable Size Too Large

**Problem**: Executable is > 1 GB

**Solutions**:
1. Add exclusions in `build_windows.py`:
   ```python
   excludes = [
       'tkinter',
       'matplotlib',
       'test',
       'unittest',
   ]
   ```

2. Remove unused dependencies from `pyproject.toml`

3. Use UPX compression (experimental):
   ```python
   # In spec file
   upx=True,
   upx_exclude=[],
   ```

---

## Distribution

### Distributing the Installer

**Recommended**: Distribute `HrisaDocs-0.1.0-Setup.exe`

**Advantages**:
- Professional installation experience
- Creates Start Menu shortcuts
- Adds uninstall entry
- Smaller download size (~280 MB vs ~1.5 GB)

### Distributing Standalone Executable

**Alternative**: Distribute `HrisaDocs.exe` + dependencies

**Package structure**:
```
HrisaDocs-0.1.0-Windows-Portable/
├── HrisaDocs.exe
├── _internal/           (dependencies)
└── README.txt          (instructions)
```

**Zip for distribution**:
```powershell
# Create portable package
Compress-Archive -Path dist\HrisaDocs.exe, dist\_internal -DestinationPath HrisaDocs-Portable.zip
```

### Creating Checksums

**For installer**:
```powershell
# Create SHA256 checksum
Get-FileHash dist\HrisaDocs-0.1.0-Setup.exe -Algorithm SHA256 | Format-List

# Save to file
Get-FileHash dist\HrisaDocs-0.1.0-Setup.exe -Algorithm SHA256 |
  Select-Object @{Name='Hash';Expression={$_.Hash}}, @{Name='File';Expression={$_.Path | Split-Path -Leaf}} |
  Out-File dist\HrisaDocs-0.1.0-Setup.sha256
```

Users can verify:
```powershell
# Verify checksum
Get-FileHash HrisaDocs-0.1.0-Setup.exe -Algorithm SHA256
# Compare with published checksum
```

### Code Signing (Optional, Recommended)

**Why code sign?**
- Removes SmartScreen warnings
- Increases user trust
- Required for some enterprise deployments

**Process**:
1. Purchase code signing certificate (~$100-500/year)
2. Install certificate on build machine
3. Sign executable:
   ```powershell
   signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 HrisaDocs.exe
   ```
4. Sign installer:
   ```powershell
   signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 HrisaDocs-0.1.0-Setup.exe
   ```

---

## Continuous Integration

### GitHub Actions Workflow

The project includes automated builds via GitHub Actions.

**Configuration**: `.github/workflows/build.yml`

**Features**:
- ✅ Automated builds on push/PR
- ✅ Builds for Windows and macOS
- ✅ Runs tests before building
- ✅ Creates installers
- ✅ Uploads artifacts
- ✅ Creates releases for tags
- ✅ Generates checksums

**Monitoring builds**:
1. GitHub repository → Actions tab
2. View workflow runs
3. Download artifacts
4. Check logs for errors

---

## Build Performance

**Typical build times** (on GitHub Actions runners):

| Step | Duration |
|------|----------|
| Checkout & Setup | 1-2 minutes |
| Install Dependencies | 3-5 minutes |
| PyInstaller Build | 10-15 minutes |
| Create Installer | 1-2 minutes |
| **Total** | **15-25 minutes** |

**Local builds** (varies by hardware):
- Fast machine (SSD, 16GB RAM): 10-15 minutes
- Slow machine (HDD, 8GB RAM): 20-30 minutes

---

## Next Steps

After successful build:

1. **Test thoroughly**: Follow [Testing the Build](#testing-the-build)
2. **Create release**: Tag version and push to trigger release
3. **Update documentation**: Update version numbers in docs
4. **Distribute**: Upload to GitHub releases or distribution platform

---

## Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Windows Code Signing](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)

---

## Questions?

- **Build issues**: Check [Troubleshooting](#troubleshooting)
- **CI/CD issues**: Check GitHub Actions logs
- **Distribution**: See [Distribution](#distribution)
- **Code signing**: Consult certificate provider documentation

---

**Happy building!** 🏗️
