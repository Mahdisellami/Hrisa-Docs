# Building Linux Release Locally

Due to GitHub's 2GB release asset limit, the Linux build must be created locally and uploaded manually.

## Prerequisites

**On your Ubuntu VM:**

1. Python 3.11+ installed
2. Git installed
3. At least 10GB free disk space

## Build Steps

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/MahdiSellami/Hrisa-Docs.git
cd Hrisa-Docs
git checkout v0.1.0  # Or your target release tag
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (this will take a while - ~500MB-1GB download)
pip install -e ".[packaging]"
```

### 3. Run the Build Script

```bash
# This will create dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz
python3 scripts/build_linux.py
```

**Expected build time:** 15-25 minutes

**Expected output:**
- `dist/hrisa-docs` - Single executable file (~1.5-2GB)
- `dist/hrisa-docs.desktop` - Desktop integration file
- `dist/install.sh` - Installation script
- `dist/check_dependencies.py` - Dependency checker
- `dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz` - Final tarball (may exceed 2GB)

### 4. Verify the Build

```bash
# Check file sizes
ls -lh dist/

# Test the executable
cd dist
./hrisa-docs --version  # Should not crash

# Test tarball contents
tar -tzf hrisa-docs-0.1.0-linux-x86_64.tar.gz
```

### 5. Create SHA256 Checksum

```bash
cd dist
sha256sum hrisa-docs-0.1.0-linux-x86_64.tar.gz > hrisa-docs-linux.sha256
cat hrisa-docs-linux.sha256
```

## Upload to GitHub Release

### Option A: Via Web UI (Easiest)

1. Go to: https://github.com/MahdiSellami/Hrisa-Docs/releases/tag/v0.1.0
2. Click "Edit release"
3. Drag and drop from your VM:
   - `hrisa-docs-0.1.0-linux-x86_64.tar.gz`
   - `hrisa-docs-linux.sha256`
4. Click "Update release"

### Option B: Via `gh` CLI

```bash
# Install GitHub CLI (if not already installed)
sudo apt install gh -y

# Authenticate
gh auth login

# Upload to release
gh release upload v0.1.0 \
  dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz \
  dist/hrisa-docs-linux.sha256 \
  --repo MahdiSellami/Hrisa-Docs \
  --clobber  # Overwrites if already exists
```

### Option C: Transfer to macOS, then Upload

If VM doesn't have direct GitHub access:

```bash
# On VM: Copy to shared folder
cp dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz ~/Downloads/
cp dist/hrisa-docs-linux.sha256 ~/Downloads/

# On macOS: Upload using gh CLI
cd ~/Downloads
gh release upload v0.1.0 \
  hrisa-docs-0.1.0-linux-x86_64.tar.gz \
  hrisa-docs-linux.sha256 \
  --repo MahdiSellami/Hrisa-Docs
```

## Troubleshooting

### Build Fails with "No module named 'PyInstaller'"

```bash
source .venv/bin/activate
pip install pyinstaller
```

### Build Fails with "Cannot import chromadb"

```bash
pip install -e ".[packaging]"  # Reinstall all dependencies
```

### Tarball Still Too Large

The tarball may exceed 2GB even with optimizations. Solutions:

1. **Split upload**: Use external hosting (Google Drive, Dropbox) and link from release notes
2. **Docker image**: Build and push to Docker Hub instead
3. **Keep as-is**: GitHub CLI might handle >2GB files differently than web UI

### VM Runs Out of Disk Space

```bash
# Clean up build artifacts
rm -rf build/ dist/

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Clean pip cache
pip cache purge
```

## Automation (Optional)

Create a script `build_and_upload.sh`:

```bash
#!/bin/bash
set -e

VERSION="v0.1.0"

echo "Building Linux release..."
source .venv/bin/activate
python3 scripts/build_linux.py

echo "Creating checksum..."
cd dist
sha256sum hrisa-docs-${VERSION#v}-linux-x86_64.tar.gz > hrisa-docs-linux.sha256

echo "Uploading to GitHub..."
gh release upload $VERSION \
  hrisa-docs-${VERSION#v}-linux-x86_64.tar.gz \
  hrisa-docs-linux.sha256 \
  --repo MahdiSellami/Hrisa-Docs \
  --clobber

echo "Done! Release updated at:"
echo "https://github.com/MahdiSellami/Hrisa-Docs/releases/tag/$VERSION"
```

Make it executable:
```bash
chmod +x build_and_upload.sh
./build_and_upload.sh
```

## Notes

- The Linux build is excluded from GitHub Actions CI due to size limitations
- macOS and Windows builds still happen automatically
- You need to manually build and upload Linux artifacts for each release
- Consider adding this step to your release checklist
