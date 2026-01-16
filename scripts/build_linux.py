#!/usr/bin/env python3
"""
Build script for Linux application.

Creates a standalone executable that can be distributed to users or packaged as .deb/.AppImage.
"""

import subprocess
import sys
from pathlib import Path
import shutil

# Project paths
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
ICON_PATH = ROOT_DIR / "assets" / "icon.png"  # Linux uses PNG

# Application info
APP_NAME = "Hrisa Docs"
APP_VERSION = "0.1.0"
EXECUTABLE_NAME = "hrisa-docs"  # Linux executable name (lowercase, hyphenated)


def check_requirements():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("[ERROR] PyInstaller not found")
        print("Install with: pip install pyinstaller")
        return False


def clean_build():
    """Clean previous build artifacts."""
    print("\nCleaning previous builds...")

    # Remove BUILD_DIR completely
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  Removed {BUILD_DIR}")

    # For DIST_DIR, only remove Linux-specific files (not the directory itself)
    # This handles the case where dist is a Docker volume mount
    # Preserve files for other platforms (macOS .dmg, Windows .exe, etc.)
    if DIST_DIR.exists():
        linux_files = [
            "hrisa-docs",  # Linux executable file
            "hrisa-docs.desktop",  # Desktop integration file
            "install.sh",  # Linux install script
            "check_dependencies.py",  # Dependency checker
            f"hrisa-docs-{APP_VERSION}-linux-x86_64.tar.gz",  # Linux tarball
        ]
        for item_name in linux_files:
            item = DIST_DIR / item_name
            if item.exists():
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"  Removed {item}")
                else:
                    item.unlink()
                    print(f"  Removed {item}")
        print(f"  Cleaned Linux build artifacts from {DIST_DIR}")


def create_spec_file():
    """Create PyInstaller spec file for Linux."""
    # Convert paths to strings for spec file
    src_dir = str(SRC_DIR)
    root_dir = str(ROOT_DIR)
    icon_path = str(ICON_PATH) if ICON_PATH.exists() else ""
    executable_name = EXECUTABLE_NAME

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Hidden imports needed at runtime
hiddenimports = [
    # ChromaDB - include all submodules
    'chromadb',
    'chromadb.api',
    'chromadb.api.models',
    'chromadb.api.rust',
    'chromadb.api.client',
    'chromadb.api.segment',
    'chromadb.config',
    'chromadb.db',
    'chromadb.db.impl',
    'chromadb.db.impl.sqlite',
    'chromadb.telemetry',
    'chromadb.telemetry.product',
    'chromadb.telemetry.product.posthog',
    'chromadb.utils',
    'chromadb.segment',
    'chromadb.segment.impl',
    'chromadb.segment.impl.vector',
    'chromadb.segment.impl.metadata',
    # Other dependencies
    'sentence_transformers',
    'ollama',
    'langchain',
    'langchain_community',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'pymupdf',
    'numpy',
    'pydantic',
    'yaml',
    # Additional ChromaDB dependencies
    'posthog',
    'hnswlib',
    # Optional ChromaDB dependencies (may not be available, that's ok)
    # 'unqlite',  # Skip - not always available
]

a = Analysis(
    ['{src_dir}/docprocessor/gui/__main__.py'],
    pathex=['{src_dir}', '{root_dir}'],
    binaries=[],
    datas=[
        ('{root_dir}/config/prompts.yaml', 'config'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # GUI frameworks we don't use
        'tkinter', 'tk', '_tkinter',
        # Testing frameworks
        'pytest', 'unittest', 'nose', 'doctest', 'coverage',
        # Development tools
        'IPython', 'jupyter', 'notebook', 'nbconvert', 'ipykernel',
        # Documentation
        'sphinx', 'docutils',
        # Large scientific packages (exclude if not critical)
        'matplotlib', 'scipy', 'pandas',
        # Other unused
        'sqlite3',  # ChromaDB uses its own SQLite
        # Compiler/build tools
        'setuptools', 'pip', 'wheel',
        # Large ML frameworks we don't directly import
        'tensorflow', 'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Use --onefile mode to create a single executable
# This significantly reduces package size vs. COLLECT mode
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{executable_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    icon=None,  # Linux doesn't need icon in executable (uses .desktop file)
)
"""

    spec_file = ROOT_DIR / "HrisaDocs-Linux.spec"
    spec_file.write_text(spec_content)
    print(f"[OK] Created spec file: {spec_file}")
    return spec_file


def build_app(spec_file):
    """Build the application using PyInstaller."""
    print("\nBuilding application...")
    print("This may take several minutes...\n")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]

    try:
        subprocess.run(cmd, check=True, cwd=ROOT_DIR)
        print("\n[OK] Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed: {e}")
        return False


def create_desktop_file():
    """Create a .desktop file for Linux desktop integration."""
    # In --onefile mode, PyInstaller creates a single executable file
    executable_file = DIST_DIR / EXECUTABLE_NAME
    if not executable_file.exists():
        print(f"[ERROR] Executable not found: {executable_file}")
        return False

    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment=Document processing and synthesis with local LLMs
Exec={EXECUTABLE_NAME}
Icon=hrisa-docs
Terminal=false
Categories=Office;Education;Science;
Keywords=document;pdf;synthesis;llm;research;
"""

    # Desktop file goes in dist/ alongside the executable
    desktop_file = DIST_DIR / "hrisa-docs.desktop"
    desktop_file.write_text(desktop_content)
    print(f"[OK] Created desktop file: {desktop_file}")
    return True


def create_install_script():
    """Create install.sh script with dependency checking."""
    # Copy dependency checker script
    dep_checker_src = ROOT_DIR / "scripts" / "check_dependencies.py"
    if dep_checker_src.exists():
        dep_checker_dst = DIST_DIR / "check_dependencies.py"
        shutil.copy2(dep_checker_src, dep_checker_dst)
        dep_checker_dst.chmod(0o755)
        print(f"[OK] Copied dependency checker: {dep_checker_dst}")
    else:
        print("[WARNING] check_dependencies.py not found")

    # Use the template from scripts/
    template_path = ROOT_DIR / "scripts" / "install_linux_template.sh"

    if template_path.exists():
        # Copy the template which has full dependency checking
        install_script = DIST_DIR / "install.sh"
        shutil.copy2(template_path, install_script)
        install_script.chmod(0o755)
        print(f"[OK] Created install script from template: {install_script}")
        return True
    else:
        # Fallback: create basic install script
        print("[WARNING] install_linux_template.sh not found, creating basic script")
        install_script = DIST_DIR / "install.sh"

        script_content = f"""#!/bin/bash
# Install script for {APP_NAME}

set -e

APP_NAME="{EXECUTABLE_NAME}"
INSTALL_DIR="/opt/hrisa-docs"
BIN_LINK="/usr/local/bin/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/hrisa-docs.desktop"

echo "Installing {APP_NAME}..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files..."
cp -r "$APP_NAME"/* "$INSTALL_DIR/"

# Make executable
chmod +x "$INSTALL_DIR/$APP_NAME"

# Create symlink
echo "Creating symlink: $BIN_LINK"
ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"

# Install desktop file
if [ -f "$APP_NAME/hrisa-docs.desktop" ]; then
    echo "Installing desktop file..."
    cp "$APP_NAME/hrisa-docs.desktop" "$DESKTOP_FILE"
    chmod 644 "$DESKTOP_FILE"

    # Update desktop file to use absolute path
    sed -i "s|Exec=$APP_NAME|Exec=$INSTALL_DIR/$APP_NAME|g" "$DESKTOP_FILE"
fi

# Copy icon if available
if [ -f "../assets/icon.png" ]; then
    echo "Installing icon..."
    mkdir -p /usr/share/icons/hicolor/512x512/apps
    cp ../assets/icon.png /usr/share/icons/hicolor/512x512/apps/hrisa-docs.png
fi

echo ""
echo "Installation complete!"
echo "Run '{EXECUTABLE_NAME}' from terminal or find '{APP_NAME}' in your applications menu."
"""

        install_script.write_text(script_content)
        install_script.chmod(0o755)
        print(f"[OK] Created basic install script: {install_script}")
        return True


def create_tarball():
    """Create tarball for distribution."""
    print("\nCreating distribution tarball...")

    # In --onefile mode, PyInstaller creates a single executable file
    executable_file = DIST_DIR / EXECUTABLE_NAME
    if not executable_file.exists():
        print(f"[ERROR] Executable not found: {executable_file}")
        return False

    # Check executable file size
    size_mb = executable_file.stat().st_size / (1024 * 1024)
    print(f"  Executable size: {size_mb:.1f} MB")

    # GitHub release asset limit is 2GB (2048 MB)
    # Tarball will be ~5-15% smaller with compression
    # Warn if approaching limit
    if size_mb > 1900:
        print(f"[WARNING] Executable is large ({size_mb:.1f} MB)")
        print(f"  Compressed tarball may approach GitHub's 2GB limit")

    tarball_name = f"hrisa-docs-{APP_VERSION}-linux-x86_64.tar.gz"
    tarball_path = DIST_DIR / tarball_name

    # Files to include in tarball
    files_to_include = [EXECUTABLE_NAME]  # Main executable

    # Add desktop file if it exists
    if (DIST_DIR / "hrisa-docs.desktop").exists():
        files_to_include.append("hrisa-docs.desktop")

    # Add install script if it exists
    if (DIST_DIR / "install.sh").exists():
        files_to_include.append("install.sh")

    # Add dependency checker if it exists
    if (DIST_DIR / "check_dependencies.py").exists():
        files_to_include.append("check_dependencies.py")

    # Create tarball with all files, excluding unnecessary bloat
    # Use maximum compression (-9) and exclude cache files
    cmd = [
        "tar",
        "--exclude=__pycache__",
        "--exclude=*.pyc",
        "--exclude=*.pyo",
        "--exclude=.DS_Store",
        "--exclude=*.so.debug",
        "-czf",
        str(tarball_path),
        "-C", str(DIST_DIR),
    ] + files_to_include

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[OK] Created tarball: {tarball_path}")
        print(f"  Included files: {', '.join(files_to_include)}")

        # Verify tarball was actually created
        if not tarball_path.exists():
            print(f"[ERROR] Tarball file does not exist after creation!")
            return False

        # Show tarball size
        tarball_size_mb = tarball_path.stat().st_size / (1024 * 1024)
        print(f"  Tarball size: {tarball_size_mb:.1f} MB")

        # Warn if approaching or exceeding GitHub's 2GB limit
        if tarball_size_mb > 2048:
            print(f"  [ERROR] Tarball exceeds GitHub's 2GB release asset limit!")
            print(f"  Cannot upload to GitHub releases. Consider alternative distribution.")
            return False
        elif tarball_size_mb > 1800:
            print(f"  [WARNING] Tarball is close to GitHub's 2GB release asset limit!")

        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Tarball creation failed with exit code {e.returncode}")
        if e.stdout:
            print(f"  stdout: {e.stdout}")
        if e.stderr:
            print(f"  stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during tarball creation: {e}")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print(f"Building {APP_NAME} for Linux")
    print("=" * 60)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Warn if not on Linux
    if sys.platform != "linux":
        print("\n[WARNING] You are not running on Linux!")
        print(f"Current platform: {sys.platform}")
        print("The build may succeed, but the executable will only work on Linux.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Build cancelled.")
            sys.exit(0)

    # Clean previous builds
    clean_build()

    # Create spec file
    spec_file = create_spec_file()

    # Build application
    if not build_app(spec_file):
        sys.exit(1)

    # Clean up build directory to free disk space before tarball creation
    print("\nCleaning up build directory to free disk space...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  Removed {BUILD_DIR}")

    # Remove spec file (no longer needed)
    if spec_file.exists():
        spec_file.unlink()
        print(f"  Removed {spec_file}")

    # Create desktop integration files
    create_desktop_file()
    create_install_script()

    # Create distribution tarball
    create_tarball()

    # Summary
    print("\n" + "=" * 60)
    print("Build Summary")
    print("=" * 60)

    # In --onefile mode, check for single executable file
    executable_file = DIST_DIR / EXECUTABLE_NAME
    if executable_file.exists():
        size_mb = executable_file.stat().st_size / (1024 * 1024)
        print(f"[OK] Executable: {executable_file}")
        print(f"  Size: {size_mb:.1f} MB")

    tarball_file = list(DIST_DIR.glob("*.tar.gz"))
    if tarball_file:
        tarball_size_mb = tarball_file[0].stat().st_size / (1024 * 1024)
        print(f"[OK] Tarball: {tarball_file[0]}")
        print(f"  Size: {tarball_size_mb:.1f} MB")

    print("\nNext steps:")
    print("1. Test the executable (on Linux):")
    print(f"   cd {DIST_DIR}")
    print(f"   ./{EXECUTABLE_NAME}")
    print("\n2. Manual installation (on target Linux system):")
    print(f"   cd {DIST_DIR}")
    print(f"   sudo ./install.sh")
    print("\n3. Create distribution packages:")
    print("   - .deb package: Run scripts/create_deb.py")
    print("   - AppImage: Run scripts/create_appimage.sh")


if __name__ == "__main__":
    main()
