.PHONY: help run run-offline test test-unit test-integration clean clean-all reset install setup format lint build ci ci-fast ci-full ci-test-only ci-build-only release release-force delete-tag

# Version for release management
VERSION ?= v0.1.0

# Default target - show help
help:
	@echo "📚 Hrisa Docs - Available Commands"
	@echo ""
	@echo "🚀 Running the Application:"
	@echo "  make run              - Run the GUI application (normal mode)"
	@echo "  make run-offline      - Run in offline mode (no internet checks)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo ""
	@echo "📦 Building & Distribution:"
	@echo "  make build            - Build macOS .app bundle"
	@echo ""
	@echo "🔄 CI/CD Pipeline (Local):"
	@echo "  make ci               - Run full CI/CD pipeline (test + lint + build)"
	@echo "  make ci-fast          - Fast pipeline (skip builds)"
	@echo "  make ci-test-only     - Only tests and quality checks"
	@echo "  make ci-build-only    - Only build installers"
	@echo "  make ci-full          - Complete pipeline with all platforms"
	@echo ""
	@echo "🏷️  Release Management:"
	@echo "  make release          - Create and push release tag (VERSION=v0.1.0)"
	@echo "  make release-force    - Force push release (overwrites existing tag)"
	@echo "  make delete-tag       - Delete tag locally and remotely (VERSION=v0.1.0)"
	@echo ""
	@echo "🛠️  Setup & Installation:"
	@echo "  make install          - Install dependencies"
	@echo "  make setup            - Full setup (venv + install + directories)"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean            - Clean generated files and cache"
	@echo "  make reset            - 🔄 Reset app to initial state (for testing)"
	@echo "  make clean-projects   - Delete all projects (⚠️  WARNING: destructive)"
	@echo "  make clean-vector-db  - Clear vector database"
	@echo "  make clean-output     - Clear output files"
	@echo "  make clean-all        - Clean everything (projects + db + output)"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make format           - Format code with black"
	@echo "  make lint             - Lint code with ruff"
	@echo ""
	@echo "📖 Documentation:"
	@echo "  make privacy          - Show data privacy documentation"
	@echo ""

# Run the application
run:
	@echo "🚀 Starting Hrisa Docs..."
	.venv/bin/python -m docprocessor.gui

# Run in offline mode
run-offline:
	@echo "🚀 Starting Hrisa Docs (Offline Mode)..."
	OFFLINE_MODE=1 .venv/bin/python -m docprocessor.gui

# Run all tests
test:
	@echo "🧪 Running all tests..."
	.venv/bin/pytest -v

# Run unit tests only
test-unit:
	@echo "🧪 Running unit tests..."
	.venv/bin/pytest tests/unit -v

# Run integration tests only
test-integration:
	@echo "🧪 Running integration tests..."
	.venv/bin/pytest tests/integration -v

# Build macOS application bundle
build:
	@echo "📦 Building macOS application..."
	.venv/bin/python scripts/build_macos.py

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	.venv/bin/pip install -e .

# Full setup
setup:
	@echo "🛠️  Setting up project..."
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@echo "Installing dependencies..."
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e ".[dev]"
	@echo "Creating data directories..."
	mkdir -p data/projects
	mkdir -p data/vector_db
	mkdir -p data/output
	@echo "✅ Setup complete!"

# Clean generated files and cache
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleanup complete!"

# Clean projects (WARNING: destructive)
clean-projects:
	@echo "⚠️  WARNING: This will delete ALL projects!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	@echo "🗑️  Deleting all projects..."
	rm -rf data/projects/*
	@echo "✅ Projects deleted!"

# Clean vector database
clean-vector-db:
	@echo "🗑️  Clearing vector database..."
	rm -rf data/vector_db/*
	@echo "✅ Vector database cleared!"

# Clean output files
clean-output:
	@echo "🗑️  Clearing output files..."
	rm -rf data/output/*
	@echo "✅ Output files cleared!"

# Clean everything
clean-all: clean clean-projects clean-vector-db clean-output
	@echo "✅ Everything cleaned!"

# Reset app to initial state (for testing) - NO CONFIRMATION REQUIRED
reset:
	@echo "🔄 Resetting application to initial state..."
	@echo ""
	@echo "This will:"
	@echo "  • Delete all projects and their documents"
	@echo "  • Clear all vector databases"
	@echo "  • Remove all output files"
	@echo "  • Clean Python cache and system files"
	@echo ""
	@echo "⏳ Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "⏳ Deleting all projects..."
	@rm -rf data/projects/* 2>/dev/null || true
	@echo "⏳ Clearing vector database..."
	@rm -rf data/vector_db/* 2>/dev/null || true
	@echo "⏳ Clearing output files..."
	@rm -rf data/output/* 2>/dev/null || true
	@echo "⏳ Recreating directory structure..."
	@mkdir -p data/projects
	@mkdir -p data/vector_db
	@mkdir -p data/output
	@echo ""
	@echo "✅ Application reset to initial state!"
	@echo "   You can now run 'make run' for a fresh start."

# Format code with black
format:
	@echo "🎨 Formatting code..."
	.venv/bin/black src/ tests/

# Lint code with ruff
lint:
	@echo "🔍 Linting code..."
	.venv/bin/ruff check src/ tests/

# Show privacy documentation
privacy:
	@cat DATA_PRIVACY.md

# Quick start guide
quickstart:
	@echo "🚀 Quick Start Guide"
	@echo ""
	@echo "1. Setup (first time only):"
	@echo "   make setup"
	@echo ""
	@echo "2. Run the application:"
	@echo "   make run"
	@echo ""
	@echo "3. For offline mode:"
	@echo "   make run-offline"
	@echo ""
	@echo "4. Run tests:"
	@echo "   make test"
	@echo ""
	@echo "5. Need help?"
	@echo "   make help"
	@echo ""

# ============================================================
# CI/CD Pipeline Targets
# ============================================================

# Full CI/CD pipeline (default)
ci:
	@echo "🚀 Running CI/CD Pipeline..."
	@./scripts/ci_local.sh

# Fast pipeline (skip builds)
ci-fast:
	@echo "🚀 Running Fast CI/CD Pipeline (no builds)..."
	@SKIP_BUILD_MACOS=true SKIP_BUILD_LINUX=true SKIP_BUILD_WINDOWS=true ./scripts/ci_local.sh

# Only run tests and quality checks
ci-test-only:
	@echo "🧪 Running Tests & Quality Checks Only..."
	@SKIP_BUILD_MACOS=true SKIP_BUILD_LINUX=true SKIP_BUILD_WINDOWS=true ./scripts/ci_local.sh

# Only build installers
ci-build-only:
	@echo "🔨 Building Installers Only..."
	@SKIP_TESTS=true SKIP_LINT=true ./scripts/ci_local.sh

# Complete pipeline with all platforms (may require Docker)
ci-full:
	@echo "🚀 Running Full CI/CD Pipeline (all platforms)..."
	@SKIP_BUILD_MACOS=false SKIP_BUILD_LINUX=false SKIP_BUILD_WINDOWS=false ./scripts/ci_local.sh

# ============================================================
# Release Management
# ============================================================

# Delete tag locally and remotely
delete-tag:
	@echo "🗑️  Deleting tag $(VERSION)..."
	@echo "  Deleting local tag..."
	@git tag -d $(VERSION) 2>/dev/null || echo "  ⚠️  Local tag $(VERSION) not found"
	@echo "  Deleting remote tag..."
	@git push origin :refs/tags/$(VERSION) 2>/dev/null || echo "  ⚠️  Remote tag $(VERSION) not found"
	@echo "✅ Tag $(VERSION) deleted!"

# Create and push release tag
release:
	@echo "🚀 Creating release $(VERSION)..."
	@echo ""
	@echo "This will:"
	@echo "  1. Push current commits to remote"
	@echo "  2. Create tag $(VERSION)"
	@echo "  3. Push tag to trigger CI/CD release workflow"
	@echo ""
	@echo "⏳ Pushing commits..."
	@git push
	@echo "⏳ Creating tag $(VERSION)..."
	@git tag $(VERSION)
	@echo "⏳ Pushing tag..."
	@git push origin $(VERSION)
	@echo ""
	@echo "✅ Release $(VERSION) created and pushed!"
	@echo "   Check GitHub Actions: https://github.com/$$(git config --get remote.origin.url | sed 's/.*://;s/.git//')/actions"

# Force push release (overwrites existing tag)
release-force:
	@echo "🚀 Force pushing release $(VERSION)..."
	@echo ""
	@echo "⚠️  WARNING: This will overwrite existing tag $(VERSION) on remote!"
	@echo ""
	@echo "This will:"
	@echo "  1. Force push current commits to remote"
	@echo "  2. Delete remote tag $(VERSION)"
	@echo "  3. Push new tag $(VERSION) to trigger CI/CD"
	@echo ""
	@echo "⏳ Force pushing commits..."
	@git push --force-with-lease origin main
	@echo "⏳ Deleting remote tag $(VERSION)..."
	@git push origin :refs/tags/$(VERSION) 2>/dev/null || echo "  (Tag doesn't exist on remote yet)"
	@echo "⏳ Pushing new tag $(VERSION)..."
	@git push origin $(VERSION)
	@echo ""
	@echo "✅ Release $(VERSION) force-pushed!"
	@echo "   Check GitHub Actions: https://github.com/$$(git config --get remote.origin.url | sed 's/.*://;s/.git//')/actions"
	@echo ""
	@echo "📦 Expected build artifacts:"
	@echo "   - HrisaDocs-0.1.0-macOS.dmg"
	@echo "   - hrisa-docs-0.1.0-linux-x86_64.tar.gz"
	@echo "   - HrisaDocs-0.1.0-Setup.exe"
