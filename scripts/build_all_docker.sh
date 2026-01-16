#!/bin/bash
# Build Hrisa Docs for all platforms using Docker
# This script orchestrates builds for Linux and Windows via Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Building Hrisa Docs for All Platforms"
echo "=========================================="
echo ""
echo "Platforms:"
echo "  - Linux: Docker (Ubuntu 22.04)"
echo "  - Windows: Docker with Wine (experimental)"
echo "  - macOS: Not supported via Docker (requires native macOS)"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    echo "Install Docker from: https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Build for Linux
echo ""
echo "=========================================="
echo "Building for Linux..."
echo "=========================================="
"$SCRIPT_DIR/build_with_docker.sh"

# Build for Windows (optional, with confirmation)
echo ""
echo "=========================================="
echo "Build for Windows?"
echo "=========================================="
echo ""
echo "NOTE: Windows build uses Wine for cross-compilation."
echo "This is experimental and may have compatibility issues."
echo "For production, use native Windows build or GitHub Actions."
echo ""
read -p "Build Windows version? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    "$SCRIPT_DIR/build_windows_docker.sh"
else
    echo "Skipping Windows build."
fi

# macOS note
echo ""
echo "=========================================="
echo "macOS Build"
echo "=========================================="
echo ""
echo "macOS builds cannot be created via Docker due to:"
echo "  - Apple licensing restrictions"
echo "  - Need for macOS-specific frameworks and SDK"
echo "  - Code signing requirements"
echo ""
echo "To build for macOS:"
echo "  1. On macOS: python scripts/build_macos.py"
echo "  2. Or use GitHub Actions (already configured)"
echo ""

echo ""
echo "=========================================="
echo "Build Summary"
echo "=========================================="
echo ""
echo "Completed builds:"
ls -lh "$ROOT_DIR/dist/"/*.{tar.gz,zip,dmg,exe} 2>/dev/null || echo "  (check dist/ directory)"
echo ""
echo "For distribution packages:"
echo "  - Linux .deb: python scripts/create_deb.py"
echo "  - Linux AppImage: ./scripts/create_appimage.sh"
echo "  - macOS .dmg: (created by scripts/build_macos.py)"
echo "  - Windows installer: (created by scripts/build_windows.py on Windows)"
echo ""
