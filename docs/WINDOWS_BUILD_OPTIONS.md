# Windows Build Options

Building Windows executables for Hrisa Docs requires a Windows environment or x86_64 architecture. Docker builds on ARM64 (Apple Silicon) are **not supported** due to Wine limitations.

## Why Docker on ARM64 Doesn't Work

Wine on ARM64 Linux can only execute ARM64 Windows binaries (which are rare). It cannot run x86/x64 Windows executables, including:
- Python installers (amd64.exe)
- PyInstaller
- Most Windows applications

**Technical Reason**: Wine translates Windows API calls to Linux but doesn't emulate CPU architecture. ARM64 cannot natively execute x86/x64 instructions without complex emulation layers (box86/box64, QEMU) that are unreliable for production builds.

## Recommended Build Options

### Option 1: Native Windows Build (Recommended)

Build on an actual Windows machine for best results.

**Requirements**:
- Windows 10 or later
- Python 3.11+
- Git

**Steps**:
```cmd
# Clone repository
git clone <repo-url>
cd Document-Processing

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -e .
pip install pyinstaller

# Build executable
python scripts\build_windows.py

# Output: dist\HrisaDocs.exe
```

**Optional: Create Installer**
Install [Inno Setup](https://jrsoftware.org/isinfo.php) to create a professional installer:
```cmd
# After running build_windows.py
# Output: dist\HrisaDocs-0.1.0-Setup.exe
```

### Option 2: GitHub Actions (Automated)

Use GitHub's Windows runners to build automatically on push/release.

**Setup**:
1. Enable GitHub Actions in repository settings
2. Rename `.github/workflows/build.yml.disabled` → `build.yml`
3. Push code or create release tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. Download artifacts from:
   - **GitHub Actions**: Repository → Actions → Workflow run
   - **Releases**: Repository → Releases (for tagged versions)

**Pros**:
- Fully automated
- Builds for all platforms (Windows, macOS, Linux)
- Free for public repositories
- Professional CI/CD workflow

**Cons**:
- Requires GitHub account
- Slower than local builds (~15-20 minutes)

### Option 3: Cloud Windows VM

Use a cloud Windows instance for building.

#### Free Tier Options

**Oracle Cloud Always Free**:
- 2 Windows instances (1/8 OCPU, 1 GB RAM)
- Windows Server 2019/2022
- Free forever (not trial)
- [Sign up](https://www.oracle.com/cloud/free/)

**Azure Free Trial**:
- $200 credit for 30 days
- Windows Server VMs
- [Sign up](https://azure.microsoft.com/free/)

**AWS Free Tier**:
- 750 hours/month of t2.micro Windows (12 months)
- Windows Server 2016/2019/2022
- [Sign up](https://aws.amazon.com/free/)

**Google Cloud Free Trial**:
- $300 credit for 90 days
- Windows Server VMs
- [Sign up](https://cloud.google.com/free/)

#### Setup Cloud VM

1. **Create Windows VM** (Windows Server 2019/2022)
2. **Connect via RDP** (Remote Desktop)
3. **Install Build Tools**:
   ```powershell
   # Install Chocolatey
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

   # Install Git and Python
   choco install git python311 -y
   ```
4. **Clone and Build**:
   ```powershell
   git clone <repo-url>
   cd Document-Processing
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   pip install pyinstaller
   python scripts\build_windows.py
   ```
5. **Download Executable** via RDP or upload to cloud storage

#### Cost Comparison

| Provider     | Free Tier      | Cost After Free | Best For         |
|--------------|----------------|-----------------|------------------|
| Oracle Cloud | Forever free   | $0              | Long-term builds |
| Azure        | 30 days trial  | ~$50/month      | Short-term       |
| AWS          | 12 months      | ~$30/month      | Medium-term      |
| GCP          | 90 days trial  | ~$40/month      | Medium-term      |

### Option 4: Docker on x86_64 Linux (Advanced)

If you have access to an x86_64 Linux machine (not ARM64), the Docker build will work:

```bash
# On x86_64 Linux only
./scripts/build_windows_docker.sh
```

This uses Wine on x86_64, which can execute Windows x86/x64 binaries.

## Comparison Matrix

| Method              | Platform      | Cost  | Build Time | Reliability   | Best For           |
|---------------------|---------------|-------|------------|---------------|--------------------|
| **Native Windows**  | Windows       | Free  | ~5 min     | ⭐⭐⭐⭐⭐     | Development        |
| **GitHub Actions**  | Any           | Free* | ~20 min    | ⭐⭐⭐⭐⭐     | CI/CD, Releases    |
| **Oracle Cloud**    | Any           | Free  | ~5 min     | ⭐⭐⭐⭐       | No Windows machine |
| **Docker (x86_64)** | x86_64 Linux  | Free  | ~30 min    | ⭐⭐⭐         | Linux workflows    |
| **Docker (ARM64)**  | Apple Silicon | Free  | ❌ Fails    | ❌             | Not supported      |

*Free for public repositories, paid for private

## Recommendations

1. **For Development**: Use native Windows build (Option 1)
2. **For CI/CD**: Use GitHub Actions (Option 2)
3. **No Windows Machine**: Use Oracle Cloud Always Free (Option 3)
4. **Advanced Users**: Docker on x86_64 Linux (Option 4)

## Future Work

- [ ] Implement proper CI/CD pipeline with:
  - Automated testing before builds
  - Code signing for Windows executables
  - Notarization for macOS apps
  - Artifact versioning and publishing
  - Release notes generation
- [ ] Cross-compilation support improvements
- [ ] Native ARM64 Windows builds (when ecosystem matures)

## Getting Help

- **Build Issues**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **GitHub Actions**: See [.github/workflows/build.yml.disabled](.github/workflows/build.yml.disabled)
- **Windows Build Script**: See [scripts/build_windows.py](../scripts/build_windows.py)
