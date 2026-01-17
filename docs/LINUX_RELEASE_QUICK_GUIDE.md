# Linux Release Quick Guide

Quick reference for distributing Linux builds via multiple channels.

## Before You Start

Build the Linux tarball on your Ubuntu VM:
```bash
cd ~/Documents/Hrisa-Docs
source .venv/bin/activate
python3 scripts/build_linux.py
```

Files created in `dist/`:
- `hrisa-docs-0.1.0-linux-x86_64.tar.gz` (~800MB-1.5GB)
- `hrisa-docs-linux.sha256`

---

## Method 1: Google Drive (For Large Files >2GB)

### Upload
1. Go to https://drive.google.com
2. Click **"New"** → **"File upload"**
3. Upload `hrisa-docs-0.1.0-linux-x86_64.tar.gz`
4. Right-click file → **"Get link"** → **"Anyone with the link"**
5. Copy link

### Get Direct Download Link
```bash
# From sharing link: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
# Direct download: https://drive.google.com/uc?id=FILE_ID&export=download
```

### Add to Release Notes
Update GitHub release with:
```markdown
## Linux Download

Due to file size, Linux build is hosted on Google Drive:
- [Download hrisa-docs-0.1.0-linux-x86_64.tar.gz](https://drive.google.com/uc?id=FILE_ID&export=download) (~800 MB)
- SHA256: [paste checksum from hrisa-docs-linux.sha256]

Installation:
\`\`\`bash
# Download manually or use gdown
pip install gdown
gdown "https://drive.google.com/uc?id=FILE_ID"

# Extract and install
tar -xzf hrisa-docs-0.1.0-linux-x86_64.tar.gz
sudo ./install.sh
\`\`\`
```

---

## Method 2: Docker Hub

### One-Time Setup
```bash
# Login to Docker Hub
docker login
# Username: mahdisellami (or your Docker Hub username)
```

### Build and Push
```bash
cd ~/Documents/Hrisa-Docs

# Build Docker image
docker build -f Dockerfile.ubuntu -t mahdisellami/hrisa-docs:0.1.0 .

# Tag as latest
docker tag mahdisellami/hrisa-docs:0.1.0 mahdisellami/hrisa-docs:latest

# Push to Docker Hub
docker push mahdisellami/hrisa-docs:0.1.0
docker push mahdisellami/hrisa-docs:latest
```

### Add to Release Notes
```markdown
## Docker Installation (Recommended)

\`\`\`bash
# Pull and run
docker pull mahdisellami/hrisa-docs:0.1.0

# Run with data persistence
docker run -it --rm \\
  -e DISPLAY=$DISPLAY \\
  -v /tmp/.X11-unix:/tmp/.X11-unix \\
  -v ~/.docprocessor:/root/.docprocessor \\
  -v ~/Documents:/documents \\
  mahdisellami/hrisa-docs:0.1.0
\`\`\`

Prerequisites:
- Docker installed: `sudo apt install docker.io`
- X11 access: `xhost +local:docker`
```

---

## Method 3: PyPI (Python Package)

### One-Time Setup
```bash
# Install build tools
pip install build twine

# Create PyPI account at https://pypi.org/account/register/
# Create API token at https://pypi.org/manage/account/token/
```

### Build and Upload
```bash
cd ~/Documents/Hrisa-Docs

# Build distribution packages
python3 -m build

# Upload to PyPI (test server first)
python3 -m twine upload --repository testpypi dist/*

# If test works, upload to real PyPI
python3 -m twine upload dist/*
```

### Add to Release Notes
```markdown
## Install via pip

\`\`\`bash
# Install from PyPI
pip install hrisa-docs

# Run
hrisa-docs
\`\`\`

Requirements:
- Python 3.11+
- Ollama installed separately
```

---

## Method 4: GitHub Release (If <2GB)

```bash
# On Ubuntu VM
cd ~/Documents/Hrisa-Docs/dist

# Upload to GitHub
gh release upload v0.1.0 \\
  hrisa-docs-0.1.0-linux-x86_64.tar.gz \\
  hrisa-docs-linux.sha256 \\
  --repo MahdiSellami/Hrisa-Docs
```

---

## Release Checklist

For each Linux release:

- [ ] **Build** tarball on Ubuntu VM
- [ ] **Test** installation: `sudo ./install.sh`
- [ ] **Test** app launch: `hrisa-docs`
- [ ] **Check size**: If <2GB → GitHub, else → Google Drive
- [ ] **Upload** to chosen platform(s)
- [ ] **Update** release notes with download links
- [ ] **Verify** download links work
- [ ] **Post** announcement with all install options

---

## Multi-Platform Release Example

```markdown
# Hrisa Docs v0.1.0

## Downloads

### Windows
- [HrisaDocs-0.1.0-Setup.exe](link) (339 MB)

### macOS
- [HrisaDocs-0.1.0-macOS.dmg](link) (281 MB)

### Linux

**Option 1: Docker (Recommended)**
\`\`\`bash
docker pull mahdisellami/hrisa-docs:0.1.0
\`\`\`

**Option 2: Python Package**
\`\`\`bash
pip install hrisa-docs
\`\`\`

**Option 3: Direct Download**
- [Google Drive](link) (850 MB) - Extract and run `sudo ./install.sh`

**Option 4: Build from Source**
See [BUILD_LINUX_LOCALLY.md](link)

## Checksums

- Windows: `[sha256]`
- macOS: `[sha256]`
- Linux: `[sha256]`
```

---

## Troubleshooting

### "File too large for GitHub"
→ Use Google Drive (Method 1)

### "Docker build fails"
→ Check Dockerfile.ubuntu exists
→ Ensure dependencies installed

### "PyPI upload rejected"
→ Check version number is unique
→ Verify package structure with `twine check dist/*`

### "Google Drive download slow"
→ Normal for large files
→ Provide torrent as alternative

---

## Quick Commands Reference

```bash
# Build
python3 scripts/build_linux.py

# Test locally
cd dist && ./hrisa-docs

# Upload to Google Drive
# (Manual via web UI)

# Push to Docker Hub
docker push mahdisellami/hrisa-docs:0.1.0

# Upload to PyPI
python3 -m twine upload dist/*

# GitHub release
gh release upload v0.1.0 hrisa-docs-*.tar.gz
```
