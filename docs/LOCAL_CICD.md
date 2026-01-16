# Local CI/CD Pipeline

Comprehensive build, test, and release automation for Hrisa Docs that runs locally or on any CI/CD platform.

## Overview

This local CI/CD pipeline provides a fallback solution when GitHub Actions is not available (private repositories, custom workflows, offline development, etc.). It can run on:

- **Local development machines** (macOS, Linux, Windows)
- **Self-hosted CI/CD platforms** (GitLab CI, Jenkins, Azure Pipelines, CircleCI, etc.)
- **Cloud build servers** (without relying on GitHub)

## Features

✅ **Automated Testing** - Runs full test suite before building
✅ **Code Quality Checks** - Linting and formatting validation
✅ **Multi-Platform Builds** - Builds for macOS, Linux, and Windows (where supported)
✅ **Artifact Verification** - Validates all build outputs
✅ **Checksum Generation** - Creates SHA256 checksums for distribution
✅ **Version Management** - Automated version bumping
✅ **Changelog Generation** - Auto-generates CHANGELOG.md from git commits

## Quick Start

### Run Full Pipeline

```bash
# Run complete CI/CD pipeline (interactive)
./scripts/ci_pipeline.sh

# Run in non-interactive mode (for CI systems)
SKIP_PROMPTS=true ./scripts/ci_pipeline.sh
```

### Configuration

Control the pipeline behavior with environment variables:

```bash
# Disable tests
RUN_TESTS=false ./scripts/ci_pipeline.sh

# Disable linting
RUN_LINTING=false ./scripts/ci_pipeline.sh

# Force specific platform builds
BUILD_MACOS=true BUILD_LINUX=false ./scripts/ci_pipeline.sh

# Full custom configuration
RUN_TESTS=true \
RUN_LINTING=true \
BUILD_MACOS=true \
BUILD_LINUX=true \
BUILD_WINDOWS=false \
SKIP_PROMPTS=true \
./scripts/ci_pipeline.sh
```

## Pipeline Stages

### Stage 1: Pre-build Validation

Checks environment and prerequisites:

- ✅ Python 3.11+ installed
- ✅ Virtual environment exists
- ✅ Docker available (for Linux builds on non-Linux platforms)

### Stage 2: Code Quality Checks

Runs linting and formatting tools:

- **ruff** - Fast Python linter
- **black** - Code formatter

Issues are non-blocking but reported.

### Stage 3: Run Tests

Executes the full test suite:

```bash
pytest tests/ -v
```

**Critical:** Tests must pass for pipeline to continue.

### Stage 4: Build Platforms

Builds installers for available platforms:

- **macOS**: Creates `.dmg` installer (macOS only)
- **Linux**: Creates `.tar.gz` tarball (Linux or Docker)
- **Windows**: Creates `.exe` installer (Windows only)

Automatically detects platform and builds what's possible.

### Stage 5: Verify Artifacts

Validates all expected build outputs exist:

- `dist/HrisaDocs-0.1.0-macOS.dmg`
- `dist/hrisa-docs-0.1.0-linux-x86_64.tar.gz`
- `dist/HrisaDocs-0.1.0-Setup.exe` (Windows)

### Stage 6: Generate Checksums

Creates SHA256 checksums for all installers:

```
dist/SHA256SUMS.txt
```

Users can verify downloads:

```bash
# Verify macOS DMG
sha256sum -c SHA256SUMS.txt | grep macOS

# Verify Linux tarball
sha256sum -c SHA256SUMS.txt | grep linux
```

## Version Management

### Bump Version

```bash
# Bump patch version (0.1.0 -> 0.1.1)
./scripts/version_bump.sh patch

# Bump minor version (0.1.0 -> 0.2.0)
./scripts/version_bump.sh minor

# Bump major version (0.1.0 -> 1.0.0)
./scripts/version_bump.sh major

# Set specific version
./scripts/version_bump.sh 1.2.3
```

**What it does:**
- Updates `pyproject.toml`
- Updates all build scripts (`build_macos.py`, `build_linux.py`, `build_windows.py`)
- Updates Dockerfiles
- Commits changes
- Creates git tag `v<version>`

**After bumping:**

```bash
# Push the tag to trigger releases
git push origin v<version>
```

## Changelog Generation

### Generate Changelog

```bash
./scripts/generate_changelog.sh
```

**What it does:**
- Parses git commit history
- Categorizes commits by type (features, fixes, docs, etc.)
- Generates `CHANGELOG.md` in Keep a Changelog format
- Supports conventional commits (feat:, fix:, docs:, etc.)

**Commit Categories:**

| Pattern | Category | Icon |
|---------|----------|------|
| `feat:`, `Add ...` | Features | ✨ |
| `fix:`, `Fix ...` | Bug Fixes | 🐛 |
| `Update ...` | Changes | 🔄 |
| `docs:` | Documentation | 📚 |
| `refactor:` | Refactoring | ♻️ |
| `Remove ...` | Removals | 🗑️ |
| `test:` | Tests | ✅ |
| `chore:` | Chores | 🔧 |

**Example CHANGELOG.md:**

```markdown
# Changelog

## [0.1.0] - 2026-01-11

### ✨ Features
- Document processing with RAG (`a1b2c3d`)
- Theme discovery and analysis (`e4f5g6h`)

### 🐛 Bug Fixes
- Fix PDF extraction for scanned documents (`i7j8k9l`)

### 📚 Documentation
- Add installation instructions (`m0n1o2p`)
```

## Integration with CI/CD Platforms

### GitLab CI

`.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build

build:
  stage: build
  script:
    - make setup
    - SKIP_PROMPTS=true RUN_TESTS=true ./scripts/ci_pipeline.sh
  artifacts:
    paths:
      - dist/*.dmg
      - dist/*.tar.gz
      - dist/*.exe
      - dist/SHA256SUMS.txt
    expire_in: 30 days
```

### Jenkins

`Jenkinsfile`:

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'make setup'
            }
        }
        stage('Build') {
            steps {
                sh '''
                    export SKIP_PROMPTS=true
                    export RUN_TESTS=true
                    ./scripts/ci_pipeline.sh
                '''
            }
        }
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }
    }
}
```

### Azure Pipelines

`azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'

  - script: make setup
    displayName: 'Setup Environment'

  - script: |
      export SKIP_PROMPTS=true
      export RUN_TESTS=true
      ./scripts/ci_pipeline.sh
    displayName: 'Run CI/CD Pipeline'

  - task: PublishBuildArtifacts@1
    inputs:
      PathtoPublish: 'dist'
      ArtifactName: 'installers'
```

### CircleCI

`.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  build:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Setup
          command: make setup
      - run:
          name: Build
          command: |
            export SKIP_PROMPTS=true
            export RUN_TESTS=true
            ./scripts/ci_pipeline.sh
      - store_artifacts:
          path: dist/
          destination: installers

workflows:
  version: 2
  build-and-test:
    jobs:
      - build
```

## Release Workflow

### Complete Release Process

```bash
# 1. Ensure all changes are committed
git status

# 2. Run full CI/CD pipeline
./scripts/ci_pipeline.sh

# 3. Generate changelog
./scripts/generate_changelog.sh
git add CHANGELOG.md
git commit -m "Update changelog for v0.2.0"

# 4. Bump version and create tag
./scripts/version_bump.sh minor

# 5. Push everything
git push origin main
git push origin v0.2.0

# 6. Create GitHub Release
#    - Go to GitHub → Releases → Draft a new release
#    - Tag: v0.2.0
#    - Upload files from dist/:
#      - HrisaDocs-0.2.0-macOS.dmg
#      - hrisa-docs-0.2.0-linux-x86_64.tar.gz
#      - SHA256SUMS.txt
#    - Copy changelog from CHANGELOG.md
#    - Publish release
```

### Quick Release (Automated)

```bash
# Run everything in one go
./scripts/generate_changelog.sh && \
git add CHANGELOG.md && \
git commit -m "Update changelog" && \
./scripts/version_bump.sh patch && \
SKIP_PROMPTS=true ./scripts/ci_pipeline.sh
```

## Troubleshooting

### Pipeline Fails at Pre-build

**Error**: `Virtual environment not found`

**Solution**:
```bash
make setup
```

### Pipeline Fails at Tests

**Error**: `Tests failed!`

**Solution**: Fix failing tests before building:
```bash
pytest tests/ -v
```

### Docker Build Fails (Linux)

**Error**: `Docker daemon not running`

**Solution**:
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### No Artifacts Generated

**Error**: `No build artifacts found!`

**Solution**: Check build logs for errors. Common issues:
- Missing dependencies: `pip install -e .`
- PyInstaller not installed: `pip install pyinstaller`
- Insufficient disk space

### Checksum Generation Fails

**Issue**: Works on macOS/Linux but fails on Windows

**Reason**: Windows uses `certutil` instead of `sha256sum`

**Workaround**: Generate manually:
```powershell
# Windows
certutil -hashfile dist\HrisaDocs.exe SHA256
```

## Advanced Usage

### Custom Build Matrix

Build specific combinations:

```bash
# Build only macOS (on macOS)
BUILD_MACOS=true BUILD_LINUX=false ./scripts/ci_pipeline.sh

# Build only Linux (with Docker)
BUILD_MACOS=false BUILD_LINUX=true ./scripts/ci_pipeline.sh

# Build all available platforms
BUILD_MACOS=auto BUILD_LINUX=auto ./scripts/ci_pipeline.sh
```

### Parallel Builds (Advanced)

For faster builds, run platform builds in parallel:

```bash
# Build macOS and Linux simultaneously (requires tmux or separate terminals)
BUILD_MACOS=true BUILD_LINUX=false SKIP_PROMPTS=true ./scripts/ci_pipeline.sh &
BUILD_MACOS=false BUILD_LINUX=true SKIP_PROMPTS=true ./scripts/ci_pipeline.sh &
wait
```

### Skip Specific Stages

```bash
# Skip tests (not recommended for releases)
RUN_TESTS=false ./scripts/ci_pipeline.sh

# Skip linting
RUN_LINTING=false ./scripts/ci_pipeline.sh

# Skip everything except builds
RUN_TESTS=false RUN_LINTING=false ./scripts/ci_pipeline.sh
```

## Comparison: Local CI/CD vs GitHub Actions

| Feature | Local CI/CD | GitHub Actions |
|---------|-------------|----------------|
| **Cost** | Free | Free (public), paid (private) |
| **Availability** | Always | Requires GitHub |
| **Platform Support** | All | All (better Windows support) |
| **Speed** | Fast (local) | Slower (cloud) |
| **Customization** | Full control | YAML configuration |
| **Automation** | Manual trigger | Auto on push/tag |
| **Build Matrix** | Sequential | Parallel |
| **Best For** | Development, private repos | Production, public repos |

## Best Practices

1. **Always run tests** before building (`RUN_TESTS=true`)
2. **Generate changelog** before each release
3. **Bump version** only when ready to release
4. **Create git tags** for all releases
5. **Verify checksums** after generating installers
6. **Test installers** on clean systems before distributing
7. **Document changes** in CHANGELOG.md
8. **Keep builds reproducible** by pinning dependencies

## Future Enhancements

- [ ] Automated code signing (macOS, Windows)
- [ ] Automated notarization (macOS)
- [ ] Docker image builds
- [ ] Multi-architecture builds (ARM64, x86_64)
- [ ] Automated release notes from changelog
- [ ] Integration with package managers (Homebrew, apt, winget)
- [ ] Performance benchmarking
- [ ] Security scanning

## Resources

- **Pipeline Script**: [scripts/ci_pipeline.sh](../scripts/ci_pipeline.sh)
- **Version Management**: [scripts/version_bump.sh](../scripts/version_bump.sh)
- **Changelog Generator**: [scripts/generate_changelog.sh](../scripts/generate_changelog.sh)
- **GitHub Actions** (disabled): [.github/workflows/build.yml.disabled](../.github/workflows/build.yml.disabled)

---

**Questions or Issues?** Open an issue or check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
