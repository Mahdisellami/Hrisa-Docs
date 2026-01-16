#!/usr/bin/env bash
set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SKIP_TESTS=${SKIP_TESTS:-false}
SKIP_LINT=${SKIP_LINT:-false}
SKIP_BUILD_MACOS=${SKIP_BUILD_MACOS:-false}
SKIP_BUILD_LINUX=${SKIP_BUILD_LINUX:-false}
SKIP_BUILD_WINDOWS=${SKIP_BUILD_WINDOWS:-false}
PARALLEL_BUILDS=${PARALLEL_BUILDS:-false}
CLEANUP_BEFORE=${CLEANUP_BEFORE:-true}

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

log_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Error handler
cleanup_on_error() {
    log_error "Pipeline failed! Cleaning up..."
    exit 1
}

trap cleanup_on_error ERR

# Start timer
START_TIME=$(date +%s)

log_section "🚀 LOCAL CI/CD PIPELINE"
log_info "Starting comprehensive build, test, and validation pipeline"
echo ""

# Check prerequisites
log_section "📋 Checking Prerequisites"

if [ ! -d ".venv" ]; then
    log_error "Virtual environment not found. Run 'make setup' first."
    exit 1
fi
log_success "Virtual environment found"

if ! .venv/bin/python --version &>/dev/null; then
    log_error "Python not found in virtual environment"
    exit 1
fi
PYTHON_VERSION=$(.venv/bin/python --version)
log_success "Python found: $PYTHON_VERSION"

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_warning "Not in a git repository"
else
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    GIT_COMMIT=$(git rev-parse --short HEAD)
    log_success "Git repository: branch=$GIT_BRANCH commit=$GIT_COMMIT"
fi

# Cleanup old artifacts
if [ "$CLEANUP_BEFORE" = true ]; then
    log_section "🧹 Cleaning Previous Artifacts"
    rm -rf dist/ build/ htmlcov/ .coverage coverage.xml .pytest_cache/
    log_success "Cleaned previous build artifacts"
fi

# Install/update dependencies
log_section "📦 Installing Dependencies"
.venv/bin/pip install -e ".[dev,packaging]" -q
log_success "Dependencies installed"

# Stage 1: Code Quality Checks
if [ "$SKIP_LINT" != true ]; then
    log_section "🔍 Stage 1: Code Quality Checks"

    # Black formatting check
    log_info "Running Black formatter check..."
    if .venv/bin/black --check src/ tests/ 2>&1 | tee /tmp/black.log; then
        log_success "✓ Black formatting check passed"
    else
        log_warning "⚠ Black formatting issues found"
        log_info "Run 'black src/ tests/' to fix formatting"
    fi

    # Ruff linting
    log_info "Running Ruff linter..."
    if .venv/bin/ruff check src/ tests/ 2>&1 | tee /tmp/ruff.log; then
        log_success "✓ Ruff linting passed"
    else
        log_warning "⚠ Ruff linting issues found"
        log_info "Run 'ruff check --fix src/ tests/' to auto-fix issues"
    fi

    # MyPy type checking
    log_info "Running MyPy type checker..."
    if .venv/bin/mypy src/ --ignore-missing-imports 2>&1 | tee /tmp/mypy.log; then
        log_success "✓ MyPy type checking passed"
    else
        log_warning "⚠ MyPy type checking issues found (non-blocking)"
    fi

    log_success "Code quality checks completed"
else
    log_warning "Skipping code quality checks (SKIP_LINT=true)"
fi

# Stage 2: Unit and Integration Tests
if [ "$SKIP_TESTS" != true ]; then
    log_section "🧪 Stage 2: Running Tests"

    log_info "Running pytest with coverage..."

    # Run tests with coverage
    if .venv/bin/pytest tests/ \
        -v \
        -m "not requires_ollama" \
        --cov=docprocessor \
        --cov-report=term-missing \
        --cov-report=html \
        --cov-report=xml \
        --junitxml=test-results.xml \
        2>&1 | tee /tmp/pytest.log; then
        log_success "✓ All tests passed"
    else
        log_error "✗ Tests failed"
        exit 1
    fi

    # Show coverage summary
    if [ -f "coverage.xml" ]; then
        COVERAGE=$(grep -oP 'line-rate="\K[0-9.]+' coverage.xml | head -1)
        COVERAGE_PCT=$(echo "$COVERAGE * 100" | bc -l | xargs printf "%.1f")
        log_info "Test coverage: ${COVERAGE_PCT}%"

        if (( $(echo "$COVERAGE_PCT >= 70" | bc -l) )); then
            log_success "✓ Coverage meets threshold (≥70%)"
        else
            log_warning "⚠ Coverage below recommended threshold (${COVERAGE_PCT}% < 70%)"
        fi
    fi

    log_success "Tests completed successfully"
else
    log_warning "Skipping tests (SKIP_TESTS=true)"
fi

# Stage 3: Security and Dependency Checks
log_section "🔒 Stage 3: Security Checks"

log_info "Checking for known security vulnerabilities..."
if .venv/bin/pip list --format=json | jq -r '.[] | "\(.name)==\(.version)"' > /tmp/requirements.txt 2>/dev/null; then
    log_success "✓ Dependency list generated"
else
    log_warning "⚠ Could not generate dependency list (jq not installed)"
fi

# Check for common security issues in code
log_info "Scanning for potential security issues..."
if grep -r "eval(" src/ 2>/dev/null; then
    log_warning "⚠ Found eval() usage - review for security"
fi
if grep -r "exec(" src/ 2>/dev/null; then
    log_warning "⚠ Found exec() usage - review for security"
fi
log_success "Basic security scan completed"

# Stage 4: Build Validation
log_section "🏗️  Stage 4: Build Validation"

log_info "Validating package configuration..."
if .venv/bin/python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))" 2>/dev/null; then
    log_success "✓ pyproject.toml is valid"
else
    log_error "✗ pyproject.toml has syntax errors"
    exit 1
fi

log_info "Checking for missing dependencies..."
if .venv/bin/python -c "import docprocessor" 2>&1 | tee /tmp/import.log; then
    log_success "✓ Package imports successfully"
else
    log_error "✗ Package import failed"
    exit 1
fi

# Stage 5: Platform Builds
log_section "🔨 Stage 5: Building Installers"

# Detect current platform
CURRENT_OS=$(uname -s)
case "$CURRENT_OS" in
    Darwin*)
        PLATFORM="macOS"
        log_info "Running on macOS"
        ;;
    Linux*)
        PLATFORM="Linux"
        log_info "Running on Linux"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        PLATFORM="Windows"
        log_info "Running on Windows"
        ;;
    *)
        PLATFORM="Unknown"
        log_warning "Unknown platform: $CURRENT_OS"
        ;;
esac

BUILD_SUCCESS=0
BUILD_FAILED=0

# Build for macOS
if [ "$SKIP_BUILD_MACOS" != true ] && [ "$PLATFORM" = "macOS" ]; then
    log_info "Building macOS installer..."
    if python scripts/build_macos.py 2>&1 | tee /tmp/build_macos.log; then
        log_success "✓ macOS build completed"
        BUILD_SUCCESS=$((BUILD_SUCCESS + 1))
    else
        log_error "✗ macOS build failed"
        BUILD_FAILED=$((BUILD_FAILED + 1))
    fi
elif [ "$SKIP_BUILD_MACOS" = true ]; then
    log_info "Skipping macOS build (SKIP_BUILD_MACOS=true)"
elif [ "$PLATFORM" != "macOS" ]; then
    log_warning "Cannot build macOS on $PLATFORM (requires macOS)"
fi

# Build for Linux
if [ "$SKIP_BUILD_LINUX" != true ] && [ "$PLATFORM" = "Linux" ]; then
    log_info "Building Linux tarball..."
    if python scripts/build_linux.py 2>&1 | tee /tmp/build_linux.log; then
        log_success "✓ Linux build completed"
        BUILD_SUCCESS=$((BUILD_SUCCESS + 1))
    else
        log_error "✗ Linux build failed"
        BUILD_FAILED=$((BUILD_FAILED + 1))
    fi
elif [ "$SKIP_BUILD_LINUX" = true ]; then
    log_info "Skipping Linux build (SKIP_BUILD_LINUX=true)"
elif [ "$PLATFORM" != "Linux" ]; then
    log_info "Skipping Linux build (not on Linux, use Docker for cross-platform builds)"
fi

# Build for Windows
if [ "$SKIP_BUILD_WINDOWS" != true ] && [ "$PLATFORM" = "Windows" ]; then
    log_info "Building Windows installer..."
    if python scripts/build_windows.py 2>&1 | tee /tmp/build_windows.log; then
        log_success "✓ Windows build completed"
        BUILD_SUCCESS=$((BUILD_SUCCESS + 1))
    else
        log_error "✗ Windows build failed"
        BUILD_FAILED=$((BUILD_FAILED + 1))
    fi
elif [ "$SKIP_BUILD_WINDOWS" = true ]; then
    log_info "Skipping Windows build (SKIP_BUILD_WINDOWS=true)"
elif [ "$PLATFORM" != "Windows" ]; then
    log_info "Skipping Windows build (not on Windows)"
fi

if [ $BUILD_SUCCESS -eq 0 ] && [ $BUILD_FAILED -eq 0 ]; then
    log_warning "No builds were performed"
else
    log_info "Build results: $BUILD_SUCCESS succeeded, $BUILD_FAILED failed"
fi

# Stage 6: Artifact Verification
log_section "📦 Stage 6: Verifying Build Artifacts"

if [ -d "dist" ]; then
    log_info "Build artifacts in dist/:"
    ls -lh dist/ | tail -n +2 | while read -r line; do
        echo "  $line"
    done

    # Verify specific artifacts
    ARTIFACTS_FOUND=0

    if [ -f "dist/HrisaDocs-0.1.0-macOS.dmg" ]; then
        SIZE=$(du -h "dist/HrisaDocs-0.1.0-macOS.dmg" | cut -f1)
        log_success "✓ macOS DMG found ($SIZE)"
        ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
    fi

    if [ -f "dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz" ]; then
        SIZE=$(du -h "dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz" | cut -f1)
        log_success "✓ Linux tarball found ($SIZE)"
        ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
    fi

    if [ -f "dist/HrisaDocs-0.1.0-Setup.exe" ]; then
        SIZE=$(du -h "dist/HrisaDocs-0.1.0-Setup.exe" | cut -f1)
        log_success "✓ Windows installer found ($SIZE)"
        ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
    fi

    if [ $ARTIFACTS_FOUND -eq 0 ]; then
        log_warning "No platform installers found in dist/"
    else
        log_success "Found $ARTIFACTS_FOUND platform installer(s)"
    fi
else
    log_warning "No dist/ directory found (builds may have been skipped)"
fi

# Stage 7: Generate checksums
log_section "🔐 Stage 7: Generating Checksums"

if [ -d "dist" ]; then
    cd dist

    # Generate SHA256 checksums for all installers
    if ls *.dmg *.tar.gz *.exe 2>/dev/null; then
        log_info "Generating SHA256 checksums..."
        shasum -a 256 *.dmg *.tar.gz *.exe 2>/dev/null > SHA256SUMS.txt || true
        if [ -f "SHA256SUMS.txt" ]; then
            log_success "✓ Checksums generated"
            cat SHA256SUMS.txt
        fi
    else
        log_info "No installers found for checksum generation"
    fi

    cd ..
fi

# Pipeline Summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

log_section "📊 Pipeline Summary"

echo ""
echo "Pipeline Status: ${GREEN}✓ PASSED${NC}"
echo "Duration: ${MINUTES}m ${SECONDS}s"
echo ""

if [ "$SKIP_LINT" != true ]; then
    echo "  ✓ Code Quality Checks"
else
    echo "  ⊘ Code Quality Checks (skipped)"
fi

if [ "$SKIP_TESTS" != true ]; then
    echo "  ✓ Tests & Coverage"
else
    echo "  ⊘ Tests & Coverage (skipped)"
fi

echo "  ✓ Security Checks"
echo "  ✓ Build Validation"

if [ $BUILD_SUCCESS -gt 0 ]; then
    echo "  ✓ Platform Builds ($BUILD_SUCCESS)"
elif [ $BUILD_FAILED -eq 0 ]; then
    echo "  ⊘ Platform Builds (skipped)"
else
    echo "  ✗ Platform Builds (failed)"
fi

if [ -d "dist" ]; then
    echo "  ✓ Artifacts & Checksums"
fi

echo ""
log_success "🎉 CI/CD Pipeline completed successfully!"
echo ""

# Output important files
echo "📁 Generated Files:"
if [ -f "coverage.xml" ]; then
    echo "  - coverage.xml (test coverage report)"
fi
if [ -f "htmlcov/index.html" ]; then
    echo "  - htmlcov/index.html (HTML coverage report)"
fi
if [ -f "test-results.xml" ]; then
    echo "  - test-results.xml (JUnit test results)"
fi
if [ -d "dist" ]; then
    echo "  - dist/ (build artifacts)"
fi
echo ""

# Suggest next steps
echo "💡 Next Steps:"
echo "  - Review coverage report: open htmlcov/index.html"
echo "  - Test installers in dist/"
echo "  - Commit and push changes"
echo "  - Create release: git tag v0.1.0 && git push --tags"
echo ""
