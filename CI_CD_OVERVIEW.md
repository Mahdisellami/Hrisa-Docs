# CI/CD System Overview

Hrisa Docs has **dual CI/CD pipelines**: one local, one cloud-based. Use both for maximum efficiency!

## 🚀 Quick Reference

### Local Pipeline (Immediate Feedback)

```bash
make ci              # Full pipeline (~5-10 min)
make ci-fast         # Skip builds (~2-3 min)
make ci-test-only    # Only tests (~2 min)
make ci-build-only   # Only builds (~5 min)
```

### Cloud Pipeline (Multi-Platform)

```bash
git push            # Triggers GitHub Actions
git tag v0.1.0      # Builds + creates release
git push --tags     # Uploads installers
```

---

## Two Pipelines, One Goal

### 🏠 Local CI/CD (`make ci`)

**When**: During development, before commits/pushes

**What it does**:
1. ✅ Code quality checks (Black, Ruff, MyPy)
2. ✅ Run tests with coverage
3. ✅ Security scans
4. ✅ Build validation
5. ✅ Create installer for **current platform**
6. ✅ Generate checksums

**Speed**: ⚡ Fast (2-10 minutes)
**Platforms**: Current OS only
**Cost**: 💰 Free (uses your CPU)
**Privacy**: 🔒 Everything stays local

**Perfect for**:
- Pre-commit validation
- Fast feedback during development
- Testing changes locally
- Building installers for testing
- Working offline

### ☁️ GitHub Actions

**When**: On push, PR, or release tags

**What it does**:
1. ✅ Test on Ubuntu, macOS, Windows (parallel)
2. ✅ Code quality checks
3. ✅ Build installers for **all platforms**
4. ✅ Upload artifacts (90-day retention)
5. ✅ Create GitHub Releases (on tags)
6. ✅ Generate checksums

**Speed**: 🐢 Slower (15-30 minutes)
**Platforms**: ✅ All three (macOS, Linux, Windows)
**Cost**: 💳 Free tier (2,000 min/month)
**Privacy**: ☁️ Runs in GitHub cloud

**Perfect for**:
- Multi-platform releases
- Automated testing on all OSes
- Distribution to users
- Release automation
- Team collaboration

---

## Recommended Workflow

### 1. Development Phase (Local)

```bash
# Make changes
vim src/docprocessor/core/synthesis_engine.py

# Quick validation (2-3 min)
make ci-fast

# If tests pass, commit
git add -A
git commit -m "feat: Improve synthesis"
```

### 2. Pre-Push Phase (Local)

```bash
# Full validation (5-10 min)
make ci

# If everything passes, push
git push origin main
```

### 3. Push Phase (GitHub Actions)

GitHub Actions automatically:
- ✅ Tests on all platforms
- ✅ Builds all installers
- ✅ Uploads artifacts

Check status: Repository → Actions tab

### 4. Release Phase (Both)

```bash
# Create release notes
vim RELEASE_NOTES_v0.1.0.md

# Local validation
make ci-full

# Tag and push
git tag v0.1.0
git push --tags
```

GitHub Actions automatically:
- ✅ Builds all installers
- ✅ Creates GitHub Release
- ✅ Uploads installers + checksums

---

## Comparison Matrix

| Feature | Local CI/CD | GitHub Actions |
|---------|-------------|----------------|
| **Trigger** | Manual (`make ci`) | Automatic (on push) |
| **Speed** | ⚡ 2-10 min | 🐢 15-30 min |
| **Platforms** | Current OS | All 3 platforms |
| **Cost** | Free (your machine) | Free tier limits |
| **Privacy** | 100% local | Cloud-based |
| **Artifacts** | Local `dist/` | 90-day retention |
| **Feedback** | Immediate terminal | Email/web UI |
| **Network** | Works offline | Requires internet |
| **Parallelization** | Single machine | Parallel matrix |

---

## Configuration Options

### Local Pipeline

Controlled by environment variables:

```bash
# Skip stages
SKIP_TESTS=true make ci
SKIP_LINT=true make ci
SKIP_BUILD_MACOS=true make ci

# Fast modes
make ci-fast         # SKIP_BUILD_*=true
make ci-test-only    # Only tests
make ci-build-only   # Only builds
```

### GitHub Actions

Configured in `.github/workflows/build.yml`:

```yaml
on:
  push:               # On every push
  pull_request:       # On PRs
  tags: ['v*']        # On release tags
  workflow_dispatch:  # Manual trigger
```

Skip with commit message:
```bash
git commit -m "docs: Update README [skip ci]"
```

---

## Pipeline Stages Comparison

### Both Pipelines Run:

| Stage | Local | GitHub Actions |
|-------|-------|----------------|
| **Code Quality** | Black, Ruff, MyPy | ✓ Same |
| **Tests** | Pytest + coverage | ✓ All platforms |
| **Security** | Basic scans | ✓ Same |
| **Validation** | Package checks | ✓ Same |

### Platform Builds:

| Platform | Local | GitHub Actions |
|----------|-------|----------------|
| **macOS** | ✓ (if on Mac) | ✓ Always |
| **Linux** | ✓ (if on Linux) | ✓ Always |
| **Windows** | ✓ (if on Windows) | ✓ Always |

### Artifacts:

| Artifact | Local | GitHub Actions |
|----------|-------|----------------|
| **Installers** | `dist/` folder | Download from Actions |
| **Checksums** | `dist/SHA256SUMS.txt` | Included in release |
| **Coverage** | `htmlcov/index.html` | Codecov integration |
| **Logs** | `/tmp/*.log` | Workflow logs |

---

## Common Scenarios

### Scenario 1: Quick Feature Development

```bash
# Fast iteration loop
while coding; do
    make ci-test-only  # 2 min
done
```

### Scenario 2: Pre-Commit Validation

```bash
# Before every commit
make ci-fast  # 3 min

git add -A
git commit -m "..."
```

### Scenario 3: Pre-Push Check

```bash
# Full local validation
make ci  # 10 min

# If passes, push
git push
```

### Scenario 4: Release Preparation

```bash
# 1. Local full build
make ci-full

# 2. Test installers manually
open dist/HrisaDocs-0.1.0-macOS.dmg

# 3. Tag and let GitHub Actions build all platforms
git tag v0.1.0
git push --tags
```

### Scenario 5: Debugging CI Failure

```bash
# Reproduce locally
make ci

# Check specific logs
cat /tmp/pytest.log
cat /tmp/build_macos.log
```

---

## Best Practices

### ✅ DO:

1. **Run `make ci-fast` before every commit** (catches issues early)
2. **Run `make ci` before every push** (full validation)
3. **Let GitHub Actions handle multi-platform builds** (it's automatic)
4. **Use local CI for rapid iteration** (much faster)
5. **Check GitHub Actions status before releasing** (ensures all platforms work)

### ❌ DON'T:

1. **Don't skip local CI and rely only on GitHub** (wastes time waiting)
2. **Don't build all platforms locally** (use GitHub Actions for that)
3. **Don't commit without running tests** (breaks the build)
4. **Don't push if local CI fails** (will fail remotely too)

---

## Troubleshooting

### Local Pipeline Fails

```bash
# Check logs
ls -l /tmp/*.log

# View specific log
cat /tmp/pytest.log

# Clean and retry
make clean
make ci
```

### GitHub Actions Fails

1. Go to: Repository → Actions → Failed workflow
2. Click on failed job
3. Read error logs
4. Reproduce locally: `make ci`
5. Fix and push

### Both Pass Locally but Fail on GitHub

- Check platform differences (macOS vs Linux vs Windows)
- Check environment variables
- Check external dependencies (Ollama, etc.)

---

## Advanced Usage

### Git Hooks Integration

`.git/hooks/pre-push`:
```bash
#!/bin/bash
make ci-fast
[ $? -eq 0 ] || exit 1
```

### IDE Integration

**VS Code** `.vscode/tasks.json`:
```json
{
  "label": "Run CI Pipeline",
  "type": "shell",
  "command": "make ci-fast"
}
```

### Parallel Local Testing

```bash
# Terminal 1: Watch tests
fswatch -o src/ tests/ | xargs -n1 make ci-test-only

# Terminal 2: Development
vim src/...
```

---

## Cost Analysis

### Local CI/CD
- **Hardware**: Your existing machine
- **Time**: Your development time
- **Cost**: $0

### GitHub Actions
- **Free Tier**: 2,000 minutes/month
- **Average Job**: ~15 minutes × 3 platforms = 45 min/push
- **Monthly Allowance**: ~44 pushes/month
- **Cost**: $0 (within free tier)

**Recommendation**: Use local CI for development (saves GitHub Actions minutes), use GitHub Actions for releases and multi-platform testing.

---

## Future Enhancements

- [ ] Parallel test execution in local CI
- [ ] Docker-based cross-compilation
- [ ] Artifact caching for faster builds
- [ ] Performance benchmarking in pipeline
- [ ] Automatic dependency updates
- [ ] Integration with other CI platforms (GitLab, CircleCI)

---

## Summary

**Use Local CI/CD** (`make ci`) for:
- ⚡ Fast feedback during development
- 🔒 Privacy-sensitive work
- 💰 Saving GitHub Actions minutes
- 🏠 Offline development

**Use GitHub Actions** for:
- 🌍 Multi-platform releases
- 🤖 Automated testing on all OSes
- 📦 Distribution to users
- 👥 Team collaboration

**Best of Both Worlds**: Develop locally with fast feedback, release with GitHub Actions for multi-platform support!

---

📚 **Documentation**:
- Local CI/CD: `docs/LOCAL_CICD.md`
- GitHub Actions: `.github/workflows/README.md`
- Build Scripts: `docs/PACKAGING.md`

🚀 **Get Started**: `make help`
