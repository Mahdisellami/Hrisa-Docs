# Building Hrisa Docs for Linux

This guide explains how to build Hrisa Docs for Linux distributions.

## Table of Contents
- [Quick Start (Docker - Recommended)](#quick-start-docker---recommended)
- [Native Linux Build](#native-linux-build)
- [Distribution Packages](#distribution-packages)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker - Recommended)

Build Linux binaries from any platform using Docker:

```bash
# Build with Docker (works on macOS, Windows, Linux)
./scripts/build_with_docker.sh
```

This will:
1. Build a Docker image with Ubuntu 22.04
2. Compile the application inside the container
3. Extract the build artifacts to `dist/`
4. Create a distributable tarball

**Output**: `dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz`

---

## Native Linux Build

### Prerequisites

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    python3.11-dev \
    build-essential \
    libqt6widgets6 \
    qt6-base-dev \
    upx-ucl
```

**Fedora/RHEL**:
```bash
sudo dnf install -y \
    python3.11 \
    python3-devel \
    gcc \
    gcc-c++ \
    qt6-qtbase-devel \
    upx
```

**Arch Linux**:
```bash
sudo pacman -S \
    python \
    python-pip \
    qt6-base \
    upx
```

### Build Steps

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd Document-Processing
   ```

2. **Create virtual environment**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install pyinstaller
   pip install -e .
   ```

4. **Run build script**:
   ```bash
   python scripts/build_linux.py
   ```

5. **Build output**:
   - Executable directory: `dist/hrisa-docs/`
   - Executable: `dist/hrisa-docs/hrisa-docs`
   - Install script: `dist/install.sh`

---

## Distribution Packages

### .deb Package (Debian/Ubuntu)

Create a `.deb` package for easy installation on Debian-based systems:

```bash
# Coming soon
python scripts/create_deb.py
```

Install the package:
```bash
sudo dpkg -i dist/hrisa-docs_0.1.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed
```

### AppImage (Universal Linux)

Create a portable AppImage that runs on any Linux distribution:

```bash
# Coming soon
./scripts/create_appimage.sh
```

Run the AppImage:
```bash
chmod +x HrisaDocs-0.1.0-x86_64.AppImage
./HrisaDocs-0.1.0-x86_64.AppImage
```

### Manual Tarball Distribution

Create a simple tarball for manual distribution:

```bash
cd dist
tar -czf hrisa-docs-0.1.0-linux-x86_64.tar.gz hrisa-docs install.sh
```

Users can extract and install:
```bash
tar -xzf hrisa-docs-0.1.0-linux-x86_64.tar.gz
cd hrisa-docs-0.1.0-linux-x86_64
sudo ./install.sh
```

---

## Testing

### Test in Docker

Run the built executable in a clean Ubuntu container:

```bash
# Start Ubuntu container with X11 forwarding
docker run -it \
    --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/dist/hrisa-docs:/app \
    ubuntu:22.04 \
    bash

# Inside container
cd /app
./hrisa-docs
```

### Test on Native Linux

```bash
# Run directly
cd dist/hrisa-docs
./hrisa-docs

# Or install system-wide
cd dist
sudo ./install.sh

# Run from anywhere
hrisa-docs
```

### Verify Desktop Integration

After installation, check:

```bash
# Desktop file installed
cat /usr/share/applications/hrisa-docs.desktop

# Icon installed
ls /usr/share/icons/hicolor/512x512/apps/hrisa-docs.png

# Executable symlinked
which hrisa-docs
```

---

## Troubleshooting

### "No module named 'PyQt6'"

PyInstaller may not have bundled PyQt6 correctly.

**Solution**:
```bash
# Add to hiddenimports in spec file
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    # ... existing imports
]
```

### "error while loading shared libraries: libQt6Core.so.6"

Qt6 libraries not found.

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install libqt6core6 libqt6gui6 libqt6widgets6

# Or use --onefile mode (larger but self-contained)
# Edit spec file: change to EXE with all binaries included
```

### "Failed to connect to Ollama"

Ollama is not running.

**Solution**:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
systemctl start ollama

# Or run manually
ollama serve
```

### Build Fails with "Permission denied"

Build script not executable or permission issues.

**Solution**:
```bash
chmod +x scripts/build_linux.py
sudo chown -R $USER:$USER .
```

### Docker Build Fails

Docker daemon not running or insufficient resources.

**Solution**:
```bash
# Check Docker status
docker info

# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker

# Increase Docker resources
# Docker Desktop → Settings → Resources → Memory: 4GB+
```

### Executable Crashes on Startup

Missing libraries or incompatible libc version.

**Solution 1 - Check dependencies**:
```bash
ldd dist/hrisa-docs/hrisa-docs
```

**Solution 2 - Build on older Ubuntu**:
```bash
# Use Ubuntu 20.04 for better compatibility
# Edit Dockerfile.ubuntu: FROM ubuntu:20.04
```

**Solution 3 - Use AppImage**:
AppImages bundle all dependencies and work on most distributions.

---

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/build.yml`:

```yaml
build-linux:
  runs-on: ubuntu-22.04
  steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y qt6-base-dev upx-ucl

    - name: Install Python dependencies
      run: |
        python -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install pyinstaller
        pip install -e .

    - name: Build application
      run: |
        source .venv/bin/activate
        python scripts/build_linux.py

    - name: Create tarball
      run: |
        cd dist
        tar -czf hrisa-docs-${{ github.ref_name }}-linux-x86_64.tar.gz hrisa-docs

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: linux-build
        path: dist/hrisa-docs-*.tar.gz
```

---

## Platform Support

| Distribution | Version | Status | Notes |
|--------------|---------|--------|-------|
| Ubuntu | 22.04+ | ✅ Tested | Primary target |
| Ubuntu | 20.04 | ✅ Should work | Build on 20.04 for better compatibility |
| Debian | 11+ | ✅ Should work | Same as Ubuntu |
| Fedora | 38+ | ⚠️ Untested | Different package manager |
| Arch | Latest | ⚠️ Untested | Rolling release |
| openSUSE | 15.5+ | ⚠️ Untested | Different libraries |

**Recommendation**: Build on Ubuntu 20.04 or 22.04 for maximum compatibility.

---

## Build Artifacts

After a successful build:

```
dist/
├── hrisa-docs/                    # Executable directory
│   ├── hrisa-docs                 # Main executable
│   ├── _internal/                 # Bundled libraries
│   └── hrisa-docs.desktop         # Desktop integration file
├── install.sh                     # Installation script
└── hrisa-docs-0.1.0-linux-x86_64.tar.gz  # Distributable archive
```

---

## Size Optimization

**Current size**: ~350-400 MB (includes ML models and dependencies)

**Optimization options**:
1. **UPX compression**: Already enabled in spec file
2. **Exclude unnecessary files**:
   ```python
   # In spec file
   excludes=['tkinter', 'matplotlib', 'jupyter']
   ```
3. **Strip binaries**:
   ```bash
   strip dist/hrisa-docs/hrisa-docs
   ```
4. **Use --onefile mode**: Single executable (slower startup)

**Note**: Size is mostly from sentence-transformers models (~300MB). Consider:
- Downloading models on first run instead of bundling
- Offering a "lite" version without models

---

## Next Steps

1. ✅ Basic Linux build working
2. 🔄 Test on Ubuntu 22.04 VM
3. ⏳ Create .deb package
4. ⏳ Create AppImage
5. ⏳ Add to CI/CD pipeline
6. ⏳ Test on multiple distributions

---

## Resources

- [PyInstaller Linux Documentation](https://pyinstaller.org/en/stable/usage.html)
- [AppImage Documentation](https://docs.appimage.org/)
- [Debian Packaging Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [Docker Multi-Platform Builds](https://docs.docker.com/build/building/multi-platform/)

---

**Questions or issues?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue.
