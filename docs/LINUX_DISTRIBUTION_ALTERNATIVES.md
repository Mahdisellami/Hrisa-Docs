# Linux Distribution Alternatives

Due to the large size of the Linux build (~800MB-1.5GB with PyTorch), we provide multiple distribution methods to accommodate different user preferences and infrastructure limitations.

## Distribution Methods

### 1. GitHub Release (If Under 2GB)

**Primary method** - Used when the tarball is under GitHub's 2GB limit.

**Download:**
```bash
wget https://github.com/MahdiSellami/Hrisa-Docs/releases/download/v0.1.0/hrisa-docs-0.1.0-linux-x86_64.tar.gz
tar -xzf hrisa-docs-0.1.0-linux-x86_64.tar.gz
sudo ./install.sh
```

**Pros:**
- Official release location
- Versioned
- Integrated with GitHub workflow

**Cons:**
- 2GB file size limit

---

### 2. Google Drive

**Alternative hosting** for large files.

**Setup (Maintainer):**
1. Upload tarball to Google Drive
2. Set sharing to "Anyone with the link"
3. Get shareable link
4. Add link to release notes

**Download (User):**
```bash
# Install gdown (Google Drive downloader)
pip install gdown

# Download from Google Drive
gdown "https://drive.google.com/uc?id=YOUR_FILE_ID"

# Or use browser to download manually
```

**Pros:**
- No size limit (up to 15GB free)
- Fast download speeds
- Familiar platform

**Cons:**
- Requires Google account for maintainer
- Not integrated with GitHub releases
- Extra download tool needed for CLI

---

### 3. Docker Hub

**Container-based distribution** - Users run via Docker.

**Setup (Maintainer):**
```bash
# Build Docker image
docker build -f Dockerfile.ubuntu -t mahdisellami/hrisa-docs:0.1.0 .
docker tag mahdisellami/hrisa-docs:0.1.0 mahdisellami/hrisa-docs:latest

# Push to Docker Hub
docker push mahdisellami/hrisa-docs:0.1.0
docker push mahdisellami/hrisa-docs:latest
```

**Usage (User):**
```bash
# Pull and run
docker pull mahdisellami/hrisa-docs:0.1.0
docker run -it --rm \
  -v ~/.docprocessor:/root/.docprocessor \
  -v ~/Documents:/documents \
  mahdisellami/hrisa-docs:0.1.0
```

**Pros:**
- Consistent environment
- No dependency issues
- Easy updates
- Standard container workflow

**Cons:**
- Requires Docker installed
- Larger initial download
- GUI apps need X11 forwarding

---

### 4. PyPI (Python Package Index)

**Install via pip** - For Python users.

**Setup (Maintainer):**
```bash
# Build package
python3 -m build

# Upload to PyPI
python3 -m twine upload dist/*
```

**Usage (User):**
```bash
# Install via pip
pip install hrisa-docs

# Run
hrisa-docs
```

**Pros:**
- Standard Python distribution
- Automatic dependency management
- Easy updates: `pip install --upgrade hrisa-docs`
- No large binary download

**Cons:**
- Users need Python environment
- Not a standalone executable
- Requires all dependencies installed

---

### 5. Snap Store

**Universal Linux package** managed by Canonical.

**Setup (Maintainer):**
1. Create `snap/snapcraft.yaml`
2. Build snap: `snapcraft`
3. Publish: `snapcraft push --release=stable hrisa-docs_0.1.0_amd64.snap`

**Usage (User):**
```bash
# Install from Snap Store
sudo snap install hrisa-docs

# Run
hrisa-docs
```

**Pros:**
- Automatic updates
- Sandboxed security
- Cross-distro compatibility
- No size limits

**Cons:**
- Initial Snap Store setup required
- Review process for new packages
- Some users don't like Snap

---

### 6. Flatpak

**Universal Linux package** - Desktop-focused.

**Setup (Maintainer):**
1. Create `com.mahdisellami.HrisaDocs.yaml`
2. Build: `flatpak-builder build-dir com.mahdisellami.HrisaDocs.yaml`
3. Publish to Flathub

**Usage (User):**
```bash
# Install from Flathub
flatpak install flathub com.mahdisellami.HrisaDocs

# Run
flatpak run com.mahdisellami.HrisaDocs
```

**Pros:**
- Popular desktop app distribution
- Sandboxed
- Automatic updates
- Flathub has good visibility

**Cons:**
- Requires Flatpak installed
- Initial Flathub submission process
- Sandbox can complicate file access

---

### 7. AppImage

**Portable single-file executable** - No installation needed.

**Setup (Maintainer):**
```bash
# Already have script
./scripts/create_appimage.sh
```

**Usage (User):**
```bash
# Download AppImage
wget https://github.com/MahdiSellami/Hrisa-Docs/releases/download/v0.1.0/HrisaDocs-0.1.0-x86_64.AppImage

# Make executable
chmod +x HrisaDocs-0.1.0-x86_64.AppImage

# Run directly
./HrisaDocs-0.1.0-x86_64.AppImage
```

**Pros:**
- No installation required
- Portable
- Self-contained
- Works on any distro

**Cons:**
- Large file size (includes all deps)
- Still subject to 2GB limit on GitHub

---

### 8. Self-Hosted Server

**Host on your own infrastructure** - Full control.

**Setup (Maintainer):**
```bash
# Upload to your server
scp hrisa-docs-0.1.0-linux-x86_64.tar.gz user@yourserver.com:/var/www/downloads/

# Generate download link
echo "https://yourserver.com/downloads/hrisa-docs-0.1.0-linux-x86_64.tar.gz"
```

**Usage (User):**
```bash
wget https://yourserver.com/downloads/hrisa-docs-0.1.0-linux-x86_64.tar.gz
```

**Pros:**
- Full control
- No size limits
- No third-party dependencies
- Can track downloads

**Cons:**
- Requires server infrastructure
- Bandwidth costs
- Maintenance overhead

---

### 9. SourceForge

**Traditional open-source hosting** - Good for large files.

**Setup (Maintainer):**
1. Create SourceForge project
2. Upload via web or FTP

**Usage (User):**
```bash
wget https://sourceforge.net/projects/hrisa-docs/files/v0.1.0/hrisa-docs-0.1.0-linux-x86_64.tar.gz
```

**Pros:**
- Designed for large files
- Free for open source
- Established platform
- No size limits

**Cons:**
- Dated interface
- Additional platform to manage
- Not as popular anymore

---

### 10. Torrent / IPFS

**Decentralized distribution** - For very large files.

**Setup (Maintainer):**
```bash
# Create torrent
transmission-create hrisa-docs-0.1.0-linux-x86_64.tar.gz

# Or add to IPFS
ipfs add hrisa-docs-0.1.0-linux-x86_64.tar.gz
```

**Pros:**
- No hosting costs
- Scales with demand
- Decentralized
- No size limits

**Cons:**
- Users need torrent/IPFS client
- Less mainstream
- Slower initial availability

---

## Recommended Approach

**Multi-channel strategy:**

1. **Primary: Docker Hub** - Best for consistent environment
2. **Secondary: PyPI** - For Python users
3. **Tertiary: Google Drive** - Fallback for direct download
4. **Bonus: GitHub Release** - If file size permits

**In Release Notes:**
```markdown
## Linux Installation

### Option 1: Docker (Recommended)
docker pull mahdisellami/hrisa-docs:0.1.0

### Option 2: Python Package
pip install hrisa-docs

### Option 3: Direct Download
Download from: [Google Drive Link]

### Option 4: GitHub Release (if available)
[Standard installation instructions]
```

---

## Implementation Priority

**Phase 1 (Immediate):**
1. ✅ Local build and test
2. ⏳ Google Drive upload
3. ⏳ Update release notes with link

**Phase 2 (Next Release):**
4. Docker Hub publishing
5. PyPI package creation
6. Automated upload script

**Phase 3 (Future):**
7. Snap/Flatpak packages
8. Self-hosted mirror

---

## Maintainer Checklist

For each release:

- [ ] Build Linux tarball locally
- [ ] Test installation on Ubuntu VM
- [ ] Upload to Google Drive (if >2GB)
- [ ] Upload to GitHub Releases (if <2GB)
- [ ] Build and push Docker image
- [ ] Update PyPI package
- [ ] Update release notes with all download links
- [ ] Update documentation with installation instructions
- [ ] Announce release with all options listed
