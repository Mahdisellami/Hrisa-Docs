#!/bin/bash
# Build Hrisa Docs for Windows using Docker with Wine
# This allows building Windows binaries from any platform (macOS, Windows, Linux)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Building Hrisa Docs for Windows with Docker"
echo "=========================================="
echo ""
echo "NOTE: This uses Wine for cross-compilation."
echo "For best results, build natively on Windows or use GitHub Actions."
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

echo "[1/4] Building Docker image..."
echo "This will take a while (Wine + Windows Python installation)..."
docker build -t hrisa-docs-windows-builder -f "$ROOT_DIR/Dockerfile.windows" "$ROOT_DIR"

echo ""
echo "[2/4] Creating build container..."
# Create container and run build
docker run --rm \
    --name hrisa-docs-windows-build \
    -v "$ROOT_DIR/dist:/app/dist" \
    hrisa-docs-windows-builder

echo ""
echo "[3/4] Fixing file permissions..."
# Fix permissions on macOS (files created in Docker are owned by root)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo chown -R $(whoami) "$ROOT_DIR/dist" 2>/dev/null || true
fi

echo ""
echo "[4/4] Creating zip archive..."
cd "$ROOT_DIR/dist"
if [ -f "HrisaDocs.exe" ]; then
    zip -r HrisaDocs-0.1.0-Windows.zip HrisaDocs.exe
    echo ""
    echo "=========================================="
    echo "Build Complete!"
    echo "=========================================="
    echo ""
    echo "Output files:"
    echo "  - Executable: $ROOT_DIR/dist/HrisaDocs.exe"
    echo "  - Archive: $ROOT_DIR/dist/HrisaDocs-0.1.0-Windows.zip"
    echo ""
    echo "NOTE: Wine-built executables may have compatibility issues."
    echo "For production, use native Windows build or GitHub Actions."
    echo ""
else
    echo "ERROR: Build executable not found"
    exit 1
fi
