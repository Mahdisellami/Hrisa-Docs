# Docker-Based Builds

This document explains how to use Docker for cross-platform builds of Hrisa Docs.

## Overview

Docker allows you to build Linux and Windows executables from any platform (macOS, Windows, or Linux) without needing to set up the target OS.

## Supported Platforms

| Platform | Docker Support | Status | Notes |
|----------|---------------|---------|-------|
| **Linux** | ✅ Full | Production-ready | Ubuntu 22.04 base, native compilation |
| **Windows** | ⚠️ Experimental | Use with caution | Wine-based cross-compilation |
| **macOS** | ❌ Not supported | Use native build | Apple licensing restrictions |

---

## Quick Start

### Build All Platforms

```bash
./scripts/build_all_docker.sh
```

This interactive script will build Linux and optionally Windows.

### Build Linux Only

```bash
./scripts/build_with_docker.sh
```

**Output**: `dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz`

### Build Windows (Experimental)

```bash
./scripts/build_windows_docker.sh
```

**Output**: `dist/HrisaDocs-0.1.0-Windows.zip`

---

## Linux Build (Recommended)

### How It Works

1. Creates Ubuntu 22.04 Docker container
2. Installs Python 3.10, Qt6 runtime libraries, and build tools
3. Installs all Python dependencies (PyQt6 from binary wheels)
4. Runs PyInstaller to create standalone executable
5. Extracts build artifacts to `dist/`

### Build Time

- First build: ~15 minutes (downloads dependencies)
- Subsequent builds: ~2-3 minutes (uses Docker cache)

### Output

```
dist/
├── hrisa-docs/                          # Executable directory
│   ├── hrisa-docs                       # Main executable
│   ├── _internal/                       # Bundled libraries
│   └── hrisa-docs.desktop               # Desktop integration
├── install.sh                           # Installation script
└── hrisa-docs-0.1.0-linux-x86_64.tar.gz # Distribution tarball
```

### Testing

```bash
# Extract and test
cd dist
tar -xzf hrisa-docs-0.1.0-linux-x86_64.tar.gz
cd hrisa-docs
./hrisa-docs

# Or test in Docker
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/dist/hrisa-docs:/app \
    ubuntu:22.04 \
    bash -c "cd /app && ./hrisa-docs"
```

---

## Windows Build (Experimental)

### ⚠️ Important Limitations

The Windows Docker build uses **Wine** for cross-compilation, which has several limitations:

- **Compatibility Issues**: Not all Windows APIs work correctly under Wine
- **Performance**: Slower than native Windows builds
- **Testing**: Harder to test without actual Windows
- **Code Signing**: Cannot sign executables
- **PyQt6 Issues**: GUI may have rendering problems

**Recommendation**: Use native Windows builds or GitHub Actions for production.

### How It Works

1. Creates Ubuntu container with Wine installed
2. Installs Windows Python via Wine
3. Installs dependencies in Wine Python environment
4. Runs PyInstaller via Wine
5. Extracts Windows .exe to `dist/`

### Build Time

- First build: ~30-45 minutes (Wine + Windows Python setup)
- Subsequent builds: ~5-10 minutes

### Output

```
dist/
├── HrisaDocs.exe                        # Windows executable
└── HrisaDocs-0.1.0-Windows.zip          # Distribution archive
```

### When to Use

- **Quick testing** of Windows compatibility
- **Development** on non-Windows platforms
- **CI/CD** environments without Windows runners

### When NOT to Use

- **Production releases** - use native Windows build
- **Code signing required** - Wine cannot sign executables
- **Commercial distribution** - may have compatibility issues

---

## macOS Build

### Why No Docker Support?

Docker cannot be used to build macOS applications due to:

1. **Apple Licensing**: macOS SDK requires Apple hardware
2. **Framework Dependencies**: Need native macOS frameworks (Cocoa, AppKit)
3. **Code Signing**: Requires macOS tools and Apple Developer certificates
4. **Notarization**: Apple's security process requires macOS

### Alternatives

**Option 1: Native Build (Recommended)**
```bash
# On macOS only
python scripts/build_macos.py
```

**Option 2: GitHub Actions (Automated)**
```bash
# Push code and let GitHub Actions build
git tag v0.1.0
git push origin v0.1.0
# Download from GitHub Releases
```

**Option 3: OSXCross (Advanced, Not Recommended)**

Technically possible but:
- Legally questionable (requires macOS SDK)
- Complex setup
- No code signing capability
- Not officially supported

---

## Prerequisites

### System Requirements

- **Docker Desktop**: 20.10 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 20GB free (for Docker images and builds)
- **Internet**: Required for first build (downloads dependencies)

### Install Docker

**macOS**:
```bash
brew install --cask docker
# Or download from https://docker.com
```

**Windows**:
Download from https://docker.com and install Docker Desktop

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER

# Fedora
sudo dnf install docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

---

## Troubleshooting

### Docker Build Fails

**Error**: `Cannot connect to Docker daemon`

**Solution**:
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

**Error**: `Permission denied while trying to connect to Docker`

**Solution**:
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and log back in
```

### Build is Very Slow

**Solution**:
```bash
# Increase Docker resources
# Docker Desktop → Settings → Resources
# - CPUs: 4+
# - Memory: 8GB+
# - Disk: 20GB+
```

### Linux Build: PyQt6 Fails to Install

**Solution**: Already fixed with `--only-binary` flag. If you see issues:
```bash
# Rebuild Docker image from scratch
docker build --no-cache -t hrisa-docs-ubuntu-builder -f Dockerfile.ubuntu .
```

### Windows Build: Wine Crashes

**Solution**:
```bash
# Clean Wine prefix and rebuild
docker rmi hrisa-docs-windows-builder
./scripts/build_windows_docker.sh
```

### Out of Disk Space

**Solution**:
```bash
# Clean up Docker
docker system prune -a --volumes
```

---

## Comparison: Docker vs Native vs GitHub Actions

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Docker (Linux)** | Works anywhere, reproducible, fast | Large image size | Development, CI/CD |
| **Docker (Windows)** | Cross-platform | Wine limitations, slow | Testing only |
| **Native Build** | Best compatibility, fastest | Requires target OS | Production releases |
| **GitHub Actions** | Automated, all platforms | Requires GitHub, slower | CI/CD, releases |

---

## Advanced Usage

### Custom Docker Images

```bash
# Build with custom tag
docker build -t my-hrisa-builder:v1.0 -f Dockerfile.ubuntu .

# Use custom image
docker run --rm -v $(pwd)/dist:/app/dist my-hrisa-builder:v1.0
```

### Build for Different Architectures

```bash
# Build for ARM64 (Apple Silicon, ARM servers)
docker buildx build --platform linux/arm64 -t hrisa-docs-ubuntu-builder:arm64 -f Dockerfile.ubuntu .

# Build for AMD64 (Intel/AMD processors)
docker buildx build --platform linux/amd64 -t hrisa-docs-ubuntu-builder:amd64 -f Dockerfile.ubuntu .
```

### Mount Custom Config

```bash
# Use custom config during build
docker run --rm \
    -v $(pwd)/dist:/app/dist \
    -v $(pwd)/my-config:/app/config \
    hrisa-docs-ubuntu-builder
```

---

## CI/CD Integration

### GitLab CI

```yaml
build-linux:
  image: docker:latest
  services:
    - docker:dind
  script:
    - ./scripts/build_with_docker.sh
  artifacts:
    paths:
      - dist/hrisa-docs-*.tar.gz
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Build Linux') {
            steps {
                sh './scripts/build_with_docker.sh'
            }
        }
    }
}
```

### Azure Pipelines

```yaml
- task: Bash@3
  inputs:
    targetType: 'inline'
    script: './scripts/build_with_docker.sh'
```

---

## Best Practices

1. **Use Docker for Linux builds** - Most reliable and reproducible
2. **Use native builds for production** - Best compatibility and performance
3. **Use GitHub Actions for releases** - Automated, all platforms
4. **Test Docker builds** before distributing to users
5. **Document dependencies** in Dockerfile for transparency
6. **Cache Docker layers** to speed up subsequent builds
7. **Clean old images** regularly to save disk space

---

## Additional Resources

- [Linux Build Guide](LINUX_BUILD.md)
- [Building for Windows](BUILDING_WINDOWS.md)
- [Packaging Guide](PACKAGING.md)
- [Docker Documentation](https://docs.docker.com/)
- [PyInstaller Documentation](https://pyinstaller.org/)
