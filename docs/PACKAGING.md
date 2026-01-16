# Packaging Guide

This guide explains how to create distributable packages for macOS and Windows.

## Overview

The application can be packaged as:
- **macOS**: `.app` bundle and `.dmg` installer
- **Windows**: `.exe` executable and installer

**Build Methods**:
- **Automated (CI/CD)**: GitHub Actions builds for both platforms automatically
- **Manual**: Run build scripts on native platform
- **Hybrid**: Use CI/CD for Windows, manual for macOS (or vice versa)

📚 **Detailed guides**:
- **Windows builds**: See [Building for Windows](BUILDING_WINDOWS.md)
- **CI/CD setup**: See [Automated Builds](#automated-builds-cicd) below

## Prerequisites

### Common Requirements

```bash
# Install packaging dependencies
pip install pyinstaller

# Or with dev dependencies
pip install -e ".[packaging]"
```

### macOS-Specific

```bash
# Optional: For DMG creation
brew install create-dmg
```

### Windows-Specific

- **Inno Setup** (for installer): https://jrsoftware.org/isdl.php
- Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

---

## Building for macOS

### Quick Build

```bash
# From project root
python scripts/build_macos.py
```

### What Gets Created

1. **Application Bundle**: `dist/Hrisa Docs.app`
   - Self-contained application
   - Can be run directly
   - Can be dragged to Applications folder

2. **DMG Installer**: `dist/HrisaDocs-0.1.0-macOS.dmg` (if create-dmg installed)
   - Distributable installer
   - Professional appearance
   - Easy for users to install

### Build Process

The build script:
1. Cleans previous builds
2. Creates PyInstaller spec file
3. Bundles Python interpreter and dependencies
4. Creates .app bundle with proper structure
5. Optionally creates DMG installer

### Testing

```bash
# Test the app bundle
open "dist/Hrisa Docs.app"

# Check logs
tail -f ~/.docprocessor/logs/docprocessor.log
```

### Size Expectations

- **App bundle**: ~200-300 MB (includes Python, PyQt6, ML models)
- **DMG**: ~150-250 MB (compressed)

---

## Building for Windows

### Quick Build

```bash
# From project root
python scripts/build_windows.py
```

### What Gets Created

1. **Executable**: `dist/HrisaDocs.exe`
   - Single-file executable
   - Self-contained
   - No installation needed

2. **Installer**: `dist/HrisaDocs-0.1.0-Setup.exe` (if Inno Setup installed)
   - Professional Windows installer
   - Creates start menu shortcuts
   - Uninstaller included

### Build Process

The build script:
1. Cleans previous builds
2. Creates version info for executable
3. Creates PyInstaller spec file
4. Bundles everything into single .exe
5. Optionally creates installer with Inno Setup

### Testing

```cmd
# Test the executable
dist\HrisaDocs.exe

# Check for issues
# First run may trigger Windows Defender scan
```

### Size Expectations

- **Executable**: ~150-250 MB (single-file includes everything)
- **Installer**: ~100-200 MB (compressed)

---

## Customization

### Adding an Icon

#### macOS

1. Create `icon.icns` file (macOS format)
2. Update `build_macos.py`:
   ```python
   icon='path/to/icon.icns',
   ```

#### Windows

1. Create `icon.ico` file (Windows format)
2. Update `build_windows.py`:
   ```python
   icon='path/to/icon.ico',
   ```

### Changing Version

Update in build scripts:
```python
APP_VERSION = "0.2.0"  # Change this
```

### Adding Files to Package

Edit the `datas` section in spec file:
```python
datas=[
    ('README.md', '.'),
    ('docs/*.md', 'docs'),
],
```

---

## Distribution

### macOS Distribution

#### Option 1: Direct Distribution

1. Build DMG: `python scripts/build_macos.py`
2. Upload DMG to hosting (GitHub Releases, website, etc.)
3. Users download and install

**Note**: Users may see "unidentified developer" warning. They can:
- Right-click → Open (first time only)
- Or: System Preferences → Security → "Open Anyway"

#### Option 2: Code Signing (Recommended for Production)

Requires Apple Developer account ($99/year):

```bash
# Sign the application
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/Hrisa Docs.app"

# Notarize with Apple
xcrun notarytool submit "dist/HrisaDocs-0.1.0-macOS.dmg" \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID"

# Staple the notarization
xcrun stapler staple "dist/Hrisa Docs.app"
```

Benefits:
- No security warnings
- Users trust the app immediately
- Approved for Mac App Store

---

### Windows Distribution

#### Option 1: Direct Distribution

1. Build installer: `python scripts/build_windows.py`
2. Upload to hosting
3. Users download and install

**Note**: Windows Defender SmartScreen may show warning for unsigned apps.

#### Option 2: Code Signing (Recommended for Production)

Requires code signing certificate (~$200-400/year):

```cmd
# Sign the executable
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com dist\HrisaDocs.exe

# Sign the installer
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com dist\HrisaDocs-Setup.exe
```

Benefits:
- No SmartScreen warnings
- Users trust the software
- Professional appearance

---

## Troubleshooting

### "Module not found" Errors

**Cause**: Missing hidden imports

**Solution**: Add to `hiddenimports` in build script:
```python
hiddenimports = [
    'missing_module',
    # ...
]
```

### Large File Size

**Solutions**:
1. Exclude unnecessary modules:
   ```python
   excludes=['tkinter', 'matplotlib', 'scipy'],
   ```

2. Use UPX compression (automatic in scripts)

3. Consider one-folder instead of one-file (Windows only)

### Application Crashes on Startup

**Debug**:
1. Run with console mode temporarily:
   ```python
   console=True,  # See error messages
   ```

2. Check logs: `~/.docprocessor/logs/`

3. Test dependencies:
   ```bash
   # Test imports
   python -c "import chromadb; import sentence_transformers; import PyQt6"
   ```

### Slow Startup

**Normal**: First launch may be slow (10-20 seconds)
- PyInstaller unpacks to temp directory
- Windows Defender scans executable

**If consistently slow**:
- Check antivirus isn't scanning repeatedly
- Consider --onedir build instead of --onefile

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Releases

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -e ".[packaging]"
      - run: python scripts/build_macos.py
      - uses: actions/upload-artifact@v2
        with:
          name: macos-dmg
          path: dist/*.dmg

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -e ".[packaging]"
      - run: python scripts/build_windows.py
      - uses: actions/upload-artifact@v2
        with:
          name: windows-installer
          path: dist/*Setup.exe
```

---

## Release Checklist

Before releasing:

- [ ] Update version number in:
  - [ ] `build_macos.py`
  - [ ] `build_windows.py`
  - [ ] `pyproject.toml`
  - [ ] `docs/USER_GUIDE.md`
- [ ] Test on clean machines
- [ ] Verify all features work
- [ ] Check file sizes reasonable
- [ ] Test installation process
- [ ] Prepare release notes
- [ ] Create GitHub release
- [ ] Upload installers
- [ ] Update download links

---

## Advanced Topics

### Optimizing Bundle Size

1. **Exclude unnecessary packages**:
   ```python
   excludes=['jupyter', 'notebook', 'IPython']
   ```

2. **Strip binaries** (Linux/macOS):
   ```python
   strip=True,
   ```

3. **Use lighter dependencies**:
   - Smaller embedding models
   - Minimal PyQt6 components

### Multiple Architecture Support

#### macOS Universal Binary

```bash
# Build for both Intel and Apple Silicon
pyinstaller --target-arch universal2 ...
```

#### Windows ARM

```bash
# Build on ARM64 Windows
pyinstaller --target-arch arm64 ...
```

### Adding Auto-Updates

Consider integrating:
- **PyUpdater**: Auto-update framework
- **Sparkle** (macOS): Native update system
- **Squirrel** (Windows): Modern update framework

---

## Automated Builds (CI/CD)

### GitHub Actions Workflow

The repository includes automated builds via GitHub Actions.

**File**: `.github/workflows/build.yml`

### Features

✅ **Automated building** on push/PR
✅ **Multi-platform**: Windows and macOS
✅ **Testing**: Runs tests before building
✅ **Artifacts**: Uploads build outputs
✅ **Releases**: Creates GitHub releases for tags
✅ **Checksums**: Generates SHA256 hashes

### Triggering Builds

**Automatic triggers**:
- Push to `main` or `develop` branch
- Pull requests to `main`
- Creating version tags (e.g., `v0.1.0`)

**Manual trigger**:
1. Go to GitHub repository → Actions tab
2. Select "Build Hrisa Docs" workflow
3. Click "Run workflow" button
4. Select branch
5. Click "Run workflow"

### Downloading Artifacts

**From workflow run**:
1. GitHub repository → Actions tab
2. Click on the workflow run
3. Scroll to "Artifacts" section at bottom
4. Download:
   - `HrisaDocs-macOS-dmg` (macOS installer)
   - `HrisaDocs-Windows-installer` (Windows installer)

**Artifact retention**: 90 days

### Creating Releases

**To create a new release**:

```bash
# 1. Update version in build scripts
# Edit scripts/build_macos.py and scripts/build_windows.py:
APP_VERSION = "0.2.0"

# 2. Commit changes
git add scripts/
git commit -m "chore: Bump version to 0.2.0"

# 3. Create and push tag
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

**GitHub Actions will automatically**:
1. Build for Windows and macOS
2. Run all tests
3. Create installers
4. Generate checksums
5. Create GitHub release with:
   - Release notes (from git commits)
   - macOS DMG installer
   - Windows installer
   - SHA256 checksums
   - Installation instructions

### Viewing Build Status

**Badge** (add to README.md):
```markdown
![Build Status](https://github.com/YOUR_USERNAME/Document-Processing/actions/workflows/build.yml/badge.svg)
```

**Monitoring**:
- GitHub repository → Actions tab
- View workflow runs
- Check build logs
- See test results

### Build Times

Typical CI build times:

| Platform | Duration |
|----------|----------|
| macOS | 15-20 minutes |
| Windows | 15-25 minutes |
| Tests | 3-5 minutes |
| **Total** | **~20-30 minutes** |

### Troubleshooting CI Builds

**Build fails on Windows**:
- Check Windows-specific paths
- Verify all dependencies in `pyproject.toml`
- Review Windows build logs

**Build fails on macOS**:
- Check for macOS-specific issues
- Verify `create-dmg` installation step
- Review macOS build logs

**Tests fail**:
- Check test logs in "test" job
- Fix failing tests locally first
- Push fixes to trigger rebuild

**Artifact upload fails**:
- Check artifact paths in workflow
- Verify files exist after build
- Check GitHub Actions storage limits

### Local Testing of CI Workflow

Test workflow locally with [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS

# Run workflow locally
act push

# Run specific job
act -j build-macos
```

**Note**: Full local testing is limited due to platform constraints.

### Advanced Configuration

**Edit `.github/workflows/build.yml` to**:
- Change Python version
- Add more platforms (Linux)
- Modify test configuration
- Customize release notes
- Add deployment steps

**Example - Add Linux build**:
```yaml
build-linux:
  runs-on: ubuntu-latest
  steps:
    # ... similar to other builds
```

### Security Notes

- **Code signing**: Not included in CI (requires certificates)
- **Secrets**: Don't commit certificates or passwords
- **GITHUB_TOKEN**: Automatically provided by GitHub Actions
- **Dependencies**: Pinned versions recommended for reproducibility

### Cost Considerations

GitHub Actions free tier:
- **Public repos**: Unlimited minutes
- **Private repos**: 2,000 minutes/month

Our builds use ~30 minutes per run:
- Approximately 60-70 builds per month on free tier
- Usually sufficient for small teams

---

## Support

### Issues During Build

1. Check PyInstaller docs: https://pyinstaller.org/
2. Search for error messages
3. Create issue with:
   - Build script output
   - System information
   - PyInstaller version

### Testing Builds

Test on:
- **macOS**: Latest 2 major versions
- **Windows**: Windows 10 and 11
- Clean VMs (no dev tools installed)
- Different user accounts

---

## Summary

```bash
# Quick build commands

# macOS
python scripts/build_macos.py

# Windows
python scripts/build_windows.py

# Outputs in dist/ folder
```

**Next steps**: See `docs/DISTRIBUTION.md` for release process.
