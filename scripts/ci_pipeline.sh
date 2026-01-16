#!/bin/bash
# Local CI/CD Pipeline for Hrisa Docs
# Fallback solution for when GitHub Actions is not available
# Can be run locally or on any CI/CD platform (GitLab CI, Jenkins, Azure Pipelines, etc.)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Pipeline configuration
RUN_TESTS="${RUN_TESTS:-true}"
RUN_LINTING="${RUN_LINTING:-true}"
BUILD_MACOS="${BUILD_MACOS:-auto}"
BUILD_LINUX="${BUILD_LINUX:-auto}"
BUILD_WINDOWS="${BUILD_WINDOWS:-false}"
SKIP_PROMPTS="${SKIP_PROMPTS:-false}"

# Detect platform
detect_platform() {
    case "$OSTYPE" in
        darwin*)  PLATFORM="macos" ;;
        linux*)   PLATFORM="linux" ;;
        msys*|cygwin*) PLATFORM="windows" ;;
        *)        PLATFORM="unknown" ;;
    esac

    log_info "Detected platform: $PLATFORM"
}

# Auto-configure builds based on platform
auto_configure_builds() {
    if [ "$BUILD_MACOS" == "auto" ]; then
        if [ "$PLATFORM" == "macos" ]; then
            BUILD_MACOS="true"
        else
            BUILD_MACOS="false"
        fi
    fi

    if [ "$BUILD_LINUX" == "auto" ]; then
        if [ "$PLATFORM" == "linux" ]; then
            BUILD_LINUX="true"
        elif command -v docker &> /dev/null; then
            BUILD_LINUX="true"
        else
            BUILD_LINUX="false"
        fi
    fi
}

# Print pipeline configuration
print_config() {
    echo ""
    echo "=========================================="
    echo "CI/CD Pipeline Configuration"
    echo "=========================================="
    echo "Platform: $PLATFORM"
    echo "Run Tests: $RUN_TESTS"
    echo "Run Linting: $RUN_LINTING"
    echo "Build macOS: $BUILD_MACOS"
    echo "Build Linux: $BUILD_LINUX"
    echo "Build Windows: $BUILD_WINDOWS"
    echo "=========================================="
    echo ""
}

# Confirm with user (unless SKIP_PROMPTS=true)
confirm_proceed() {
    if [ "$SKIP_PROMPTS" == "true" ]; then
        return 0
    fi

    read -p "Proceed with this configuration? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Pipeline cancelled by user"
        exit 0
    fi
}

# Stage 1: Pre-build validation
stage_prebuild() {
    echo ""
    echo "=========================================="
    echo "Stage 1: Pre-build Validation"
    echo "=========================================="

    # Check Python
    log_info "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION found"

    # Check virtual environment
    log_info "Checking virtual environment..."
    if [ ! -d ".venv" ]; then
        log_error "Virtual environment not found. Run 'make setup' first"
        exit 1
    fi
    log_success "Virtual environment found"

    # Activate virtual environment
    source .venv/bin/activate

    # Check Docker (if needed for Linux build)
    if [ "$BUILD_LINUX" == "true" ] && [ "$PLATFORM" != "linux" ]; then
        log_info "Checking Docker installation..."
        if ! command -v docker &> /dev/null; then
            log_warning "Docker not found. Linux build will be skipped"
            BUILD_LINUX="false"
        elif ! docker info &> /dev/null; then
            log_warning "Docker daemon not running. Linux build will be skipped"
            BUILD_LINUX="false"
        else
            log_success "Docker is available"
        fi
    fi

    log_success "Pre-build validation completed"
}

# Stage 2: Code quality checks
stage_quality() {
    echo ""
    echo "=========================================="
    echo "Stage 2: Code Quality Checks"
    echo "=========================================="

    if [ "$RUN_LINTING" == "true" ]; then
        log_info "Running code formatters and linters..."

        # Check if ruff and black are installed
        if .venv/bin/python -c "import ruff" 2>/dev/null; then
            log_info "Running ruff..."
            .venv/bin/ruff check src/ || log_warning "Ruff found issues (non-blocking)"
        else
            log_warning "Ruff not installed, skipping..."
        fi

        if .venv/bin/python -c "import black" 2>/dev/null; then
            log_info "Running black..."
            .venv/bin/black --check src/ || log_warning "Black found formatting issues (non-blocking)"
        else
            log_warning "Black not installed, skipping..."
        fi

        log_success "Code quality checks completed"
    else
        log_info "Skipping code quality checks"
    fi
}

# Stage 3: Run tests
stage_test() {
    echo ""
    echo "=========================================="
    echo "Stage 3: Run Tests"
    echo "=========================================="

    if [ "$RUN_TESTS" == "true" ]; then
        log_info "Running test suite..."

        if [ -d "tests" ]; then
            .venv/bin/pytest tests/ -v || {
                log_error "Tests failed!"
                exit 1
            }
            log_success "All tests passed"
        else
            log_warning "No tests directory found, skipping tests"
        fi
    else
        log_info "Skipping tests"
    fi
}

# Stage 4: Build platforms
stage_build() {
    echo ""
    echo "=========================================="
    echo "Stage 4: Build Platforms"
    echo "=========================================="

    BUILD_SUCCESS=()
    BUILD_FAILED=()

    # Build macOS
    if [ "$BUILD_MACOS" == "true" ]; then
        log_info "Building macOS installer..."
        if .venv/bin/python scripts/build_macos.py; then
            log_success "macOS build completed"
            BUILD_SUCCESS+=("macOS")
        else
            log_error "macOS build failed"
            BUILD_FAILED+=("macOS")
        fi
    fi

    # Build Linux
    if [ "$BUILD_LINUX" == "true" ]; then
        log_info "Building Linux installer..."
        if [ "$PLATFORM" == "linux" ]; then
            if .venv/bin/python scripts/build_linux.py; then
                log_success "Linux build completed"
                BUILD_SUCCESS+=("Linux")
            else
                log_error "Linux build failed"
                BUILD_FAILED+=("Linux")
            fi
        else
            if ./scripts/build_with_docker.sh; then
                log_success "Linux build completed (Docker)"
                BUILD_SUCCESS+=("Linux")
            else
                log_error "Linux build failed (Docker)"
                BUILD_FAILED+=("Linux")
            fi
        fi
    fi

    # Build Windows
    if [ "$BUILD_WINDOWS" == "true" ]; then
        log_info "Building Windows installer..."
        if [ "$PLATFORM" == "windows" ]; then
            if python scripts/build_windows.py; then
                log_success "Windows build completed"
                BUILD_SUCCESS+=("Windows")
            else
                log_error "Windows build failed"
                BUILD_FAILED+=("Windows")
            fi
        else
            log_warning "Windows build requires Windows platform or Docker (experimental)"
            BUILD_FAILED+=("Windows")
        fi
    fi

    # Build summary
    echo ""
    log_info "Build Summary:"
    if [ ${#BUILD_SUCCESS[@]} -gt 0 ]; then
        log_success "Successful builds: ${BUILD_SUCCESS[*]}"
    fi
    if [ ${#BUILD_FAILED[@]} -gt 0 ]; then
        log_error "Failed builds: ${BUILD_FAILED[*]}"
        exit 1
    fi
}

# Stage 5: Verify artifacts
stage_verify() {
    echo ""
    echo "=========================================="
    echo "Stage 5: Verify Build Artifacts"
    echo "=========================================="

    log_info "Checking build artifacts..."

    ARTIFACTS=()

    if [ "$BUILD_MACOS" == "true" ]; then
        if [ -f "dist/HrisaDocs-0.1.0-macOS.dmg" ]; then
            SIZE=$(du -h "dist/HrisaDocs-0.1.0-macOS.dmg" | cut -f1)
            log_success "macOS DMG: $SIZE"
            ARTIFACTS+=("dist/HrisaDocs-0.1.0-macOS.dmg")
        else
            log_error "macOS DMG not found"
        fi
    fi

    if [ "$BUILD_LINUX" == "true" ]; then
        if [ -f "dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz" ]; then
            SIZE=$(du -h "dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz" | cut -f1)
            log_success "Linux tarball: $SIZE"
            ARTIFACTS+=("dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz")
        else
            log_error "Linux tarball not found"
        fi
    fi

    if [ "$BUILD_WINDOWS" == "true" ]; then
        if [ -f "dist/HrisaDocs-0.1.0-Setup.exe" ]; then
            SIZE=$(du -h "dist/HrisaDocs-0.1.0-Setup.exe" | cut -f1)
            log_success "Windows installer: $SIZE"
            ARTIFACTS+=("dist/HrisaDocs-0.1.0-Setup.exe")
        elif [ -f "dist/HrisaDocs.exe" ]; then
            SIZE=$(du -h "dist/HrisaDocs.exe" | cut -f1)
            log_success "Windows executable: $SIZE"
            ARTIFACTS+=("dist/HrisaDocs.exe")
        else
            log_error "Windows executable not found"
        fi
    fi

    # Check if any builds were enabled
    if [ "$BUILD_MACOS" == "false" ] && [ "$BUILD_LINUX" == "false" ] && [ "$BUILD_WINDOWS" == "false" ]; then
        log_info "No builds were configured, skipping artifact verification"
        return 0
    fi

    if [ ${#ARTIFACTS[@]} -eq 0 ]; then
        log_error "No build artifacts found!"
        exit 1
    fi

    log_success "All expected artifacts verified"
}

# Stage 6: Generate checksums
stage_checksums() {
    echo ""
    echo "=========================================="
    echo "Stage 6: Generate Checksums"
    echo "=========================================="

    # Check if any builds were enabled
    if [ "$BUILD_MACOS" == "false" ] && [ "$BUILD_LINUX" == "false" ] && [ "$BUILD_WINDOWS" == "false" ]; then
        log_info "No builds were configured, skipping checksum generation"
        return 0
    fi

    log_info "Generating SHA256 checksums..."

    cd dist

    # Remove old checksums file
    rm -f SHA256SUMS.txt

    # Generate checksums for all installers
    if [ "$PLATFORM" == "macos" ] || [ "$PLATFORM" == "linux" ]; then
        sha256sum *.dmg *.tar.gz *.exe 2>/dev/null > SHA256SUMS.txt || true
    else
        # Windows
        certutil -hashfile *.dmg SHA256 >> SHA256SUMS.txt 2>/dev/null || true
        certutil -hashfile *.tar.gz SHA256 >> SHA256SUMS.txt 2>/dev/null || true
        certutil -hashfile *.exe SHA256 >> SHA256SUMS.txt 2>/dev/null || true
    fi

    cd "$ROOT_DIR"

    if [ -f "dist/SHA256SUMS.txt" ] && [ -s "dist/SHA256SUMS.txt" ]; then
        log_success "Checksums generated: dist/SHA256SUMS.txt"
        cat dist/SHA256SUMS.txt
    else
        log_warning "No checksums generated"
    fi
}

# Final summary
print_summary() {
    echo ""
    echo "=========================================="
    echo "Pipeline Summary"
    echo "=========================================="
    echo ""

    log_success "All pipeline stages completed successfully!"

    echo ""
    echo "Build Artifacts:"
    ls -lh dist/*.{dmg,tar.gz,exe} 2>/dev/null || echo "  (check dist/ directory)"

    echo ""
    echo "Next Steps:"
    echo "  1. Test installers on clean systems"
    echo "  2. Create git tag: git tag v0.1.0"
    echo "  3. Push tag: git push origin v0.1.0"
    echo "  4. Upload artifacts to GitHub Releases"
    echo ""
}

# Main pipeline execution
main() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║  Hrisa Docs - Local CI/CD Pipeline    ║"
    echo "╚════════════════════════════════════════╝"
    echo ""

    detect_platform
    auto_configure_builds
    print_config
    confirm_proceed

    # Execute pipeline stages
    stage_prebuild
    stage_quality
    stage_test
    stage_build
    stage_verify
    stage_checksums

    print_summary

    log_success "Pipeline completed successfully! 🎉"
}

# Run main pipeline
main "$@"
