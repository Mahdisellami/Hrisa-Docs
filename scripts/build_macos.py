#!/usr/bin/env python3
"""
Build script for macOS application bundle.

Creates a standalone .app bundle that can be distributed to users.
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
ICON_PATH = ROOT_DIR / "assets" / "icon.icns"

# Application info
APP_NAME = "Hrisa Docs"
APP_VERSION = "0.1.0"
BUNDLE_ID = "com.hrisadocs.app"


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

    # For DIST_DIR, only remove macOS-specific files
    # Preserve files for other platforms (Linux .tar.gz, Windows .exe, etc.)
    if DIST_DIR.exists():
        macos_files = [
            f"{APP_NAME}.app",  # macOS application bundle
            f"HrisaDocs-{APP_VERSION}-macOS.dmg",  # macOS DMG installer
        ]
        for item_name in macos_files:
            item = DIST_DIR / item_name
            if item.exists():
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"  Removed {item}")
                else:
                    item.unlink()
                    print(f"  Removed {item}")
        print(f"  Cleaned macOS build artifacts from {DIST_DIR}")


def create_spec_file():
    """Create PyInstaller spec file."""
    # Convert paths to strings for spec file
    src_dir = str(SRC_DIR)
    root_dir = str(ROOT_DIR)
    icon_path = str(ICON_PATH)
    app_name = APP_NAME
    bundle_id = BUNDLE_ID
    app_version = APP_VERSION

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
    'chromadb.telemetry',
    'chromadb.telemetry.product',
    'chromadb.telemetry.product.posthog',
    'chromadb.utils',
    'chromadb.segment',
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
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DocumentProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DocumentProcessor',
)

app = BUNDLE(
    coll,
    name='{app_name}.app',
    icon='{icon_path}',
    bundle_identifier='{bundle_id}',
    version='{app_version}',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',
        'CFBundleShortVersionString': '{app_version}',
        'CFBundleVersion': '{app_version}',
    }},
)
"""

    spec_file = ROOT_DIR / "DocumentProcessor.spec"
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


def create_dmg():
    """Create a DMG installer (requires create-dmg tool)."""
    print("\nCreating DMG installer...")

    app_bundle = DIST_DIR / f"{APP_NAME}.app"
    if not app_bundle.exists():
        print(f"[ERROR] App bundle not found: {app_bundle}")
        return False

    # Check if create-dmg is available
    try:
        subprocess.run(["which", "create-dmg"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("  create-dmg not found, skipping DMG creation")
        print("  Install with: brew install create-dmg")
        return False

    dmg_name = f"HrisaDocs-{APP_VERSION}-macOS.dmg"
    dmg_path = DIST_DIR / dmg_name

    cmd = [
        "create-dmg",
        "--volname", APP_NAME,
        "--window-pos", "200", "120",
        "--window-size", "600", "400",
        "--icon-size", "100",
        "--app-drop-link", "400", "200",
        str(dmg_path),
        str(app_bundle)
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] Created DMG: {dmg_path}")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] DMG creation failed")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print(f"Building {APP_NAME} for macOS")
    print("=" * 60)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Clean previous builds
    clean_build()

    # Create spec file
    spec_file = create_spec_file()

    # Build application
    if not build_app(spec_file):
        sys.exit(1)

    # Create DMG (optional)
    create_dmg()

    # Summary
    print("\n" + "=" * 60)
    print("Build Summary")
    print("=" * 60)

    app_bundle = DIST_DIR / f"{APP_NAME}.app"
    if app_bundle.exists():
        size_mb = sum(f.stat().st_size for f in app_bundle.rglob('*') if f.is_file()) / (1024 * 1024)
        print(f"[OK] Application: {app_bundle}")
        print(f"  Size: {size_mb:.1f} MB")

    dmg_file = list(DIST_DIR.glob("*.dmg"))
    if dmg_file:
        dmg_size_mb = dmg_file[0].stat().st_size / (1024 * 1024)
        print(f"[OK] Installer: {dmg_file[0]}")
        print(f"  Size: {dmg_size_mb:.1f} MB")

    print("\nNext steps:")
    print("1. Test the application:")
    print(f"   open '{app_bundle}'")
    print("2. Distribute the DMG file to users")
    print("3. (Optional) Code sign for distribution")


if __name__ == "__main__":
    main()
