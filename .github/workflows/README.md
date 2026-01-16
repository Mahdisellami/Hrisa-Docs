# CI/CD Workflows

This directory contains GitHub Actions workflows for automated building, testing, and releasing.

## Workflows

### build.yml - Build & Test

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main`
- Version tags (`v*`)
- Manual workflow dispatch

**Jobs**:

1. **test** - Runs on Ubuntu, macOS, and Windows
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage to Codecov

2. **lint** - Code quality checks
   - Black formatting check
   - Ruff linting
   - MyPy type checking (non-blocking)

3. **build-macos** - Build macOS application
   - Creates `.app` bundle
   - Generates DMG installer
   - Uploads artifacts
   - On tags: uploads to GitHub Releases

4. **build-linux** - Build Linux application
   - Creates standalone executable
   - Generates tarball with install script
   - Uploads artifacts
   - On tags: uploads to GitHub Releases

5. **build-windows** - Build Windows application
   - Creates `.exe` executable
   - Generates Inno Setup installer
   - Uploads artifacts
   - On tags: uploads to GitHub Releases

6. **create-release** - Create GitHub Release
   - Only runs on version tags
   - Uses `RELEASE_NOTES_<version>.md` if available
   - Otherwise generates changelog from commits
   - Creates draft or pre-release based on version

## Using the CI/CD Pipeline

### Running Tests on Every Push

Tests run automatically on every push to `main` or `develop`:

```bash
git push origin main
```

### Creating a Release

1. Ensure `RELEASE_NOTES_v0.1.0.md` exists (optional)
2. Create and push a tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

3. GitHub Actions will:
   - Run tests on all platforms
   - Build installers for macOS, Linux, Windows
   - Create GitHub Release with artifacts
   - Upload checksums

### Manual Workflow Trigger

Go to Actions → Build & Test → Run workflow

Useful for:
- Testing workflow changes
- Building without creating a release
- Re-running failed builds

## Artifacts

Build artifacts are available for 90 days:
- macOS: DMG installer + SHA256
- Linux: tarball + SHA256
- Windows: Setup.exe + SHA256

## Badges

Add to README.md:

```markdown
![Build Status](https://github.com/USER/REPO/actions/workflows/build.yml/badge.svg)
![Tests](https://github.com/USER/REPO/actions/workflows/build.yml/badge.svg?event=push)
[![codecov](https://codecov.io/gh/USER/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USER/REPO)
```

## Secrets Required

None! The workflow uses:
- `GITHUB_TOKEN` (automatically provided)
- Codecov token uploaded via actions (optional)

## Customization

### Changing Python Version

Edit in `build.yml`:
```yaml
env:
  PYTHON_VERSION: '3.11'  # Change here
```

### Skipping CI

Add to commit message:
```
fix: Some change

[skip ci]
```

### Platform-Specific Builds

The workflow can be triggered for specific platforms by modifying the `needs` dependencies.

## Troubleshooting

**macOS build fails**: Check create-dmg installation
**Windows build fails**: Verify Inno Setup installation
**Linux build fails**: Check system dependencies

View logs: Actions tab → Select workflow run → Click on failed job
