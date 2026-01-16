#!/bin/bash
# Build Hrisa Docs for Linux using Docker
# This allows building Linux binaries from any platform (macOS, Windows, Linux)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Building Hrisa Docs for Linux with Docker"
echo "=========================================="
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
docker build -t hrisa-docs-ubuntu-builder -f "$ROOT_DIR/Dockerfile.ubuntu" "$ROOT_DIR"

echo ""
echo "[2/4] Creating build container..."
# Create container and run build
docker run --rm \
    --name hrisa-docs-build \
    -v "$ROOT_DIR/dist:/app/dist" \
    hrisa-docs-ubuntu-builder

echo ""
echo "[3/4] Fixing file permissions..."
# Fix permissions on macOS (files created in Docker are owned by root)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo chown -R $(whoami) "$ROOT_DIR/dist" 2>/dev/null || true
fi

echo ""
echo "[4/4] Creating tarball..."
cd "$ROOT_DIR/dist"
if [ -d "hrisa-docs" ]; then
    tar -czf hrisa-docs-0.1.0-linux-x86_64.tar.gz hrisa-docs
    echo ""
    echo "=========================================="
    echo "Build Complete!"
    echo "=========================================="
    echo ""
    echo "Output files:"
    echo "  - Executable directory: $ROOT_DIR/dist/hrisa-docs/"
    echo "  - Tarball: $ROOT_DIR/dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz"
    echo ""
    echo "To test on Linux:"
    echo "  1. Transfer tarball to Linux machine"
    echo "  2. tar -xzf hrisa-docs-0.1.0-linux-x86_64.tar.gz"
    echo "  3. cd hrisa-docs"
    echo "  4. sudo ../install.sh"
    echo ""
else
    echo "ERROR: Build directory not found"
    exit 1
fi
