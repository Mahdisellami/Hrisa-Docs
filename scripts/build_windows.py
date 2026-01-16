#!/usr/bin/env python3
"""
Build script for Windows executable and installer.

Creates a standalone .exe and optionally an installer using Inno Setup.
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
ICON_PATH = ROOT_DIR / "assets" / "icon.ico"

# Application info
APP_NAME = "Hrisa Docs"
APP_VERSION = "0.1.0"


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
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"  Removed {directory}")


def create_spec_file():
    """Create PyInstaller spec file for Windows."""
    # Use forward slashes - works on Windows and avoids Unicode escape issues
    src_dir = str(SRC_DIR).replace('\\', '/')
    root_dir = str(ROOT_DIR).replace('\\', '/')
    icon_path = str(ICON_PATH).replace('\\', '/')

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
    'unqlite',
    'sqlite3',
    # Keyring dependencies for Windows
    'keyring',
    'keyring.backends',
    'keyring.backends.Windows',
    # Search handlers
    'requests',
    'beautifulsoup4',
    'googleapiclient',
]

a = Analysis(
    ['{src_dir}/docprocessor/gui/__main__.py'],
    pathex=['{src_dir}', '{root_dir}'],
    binaries=[],
    datas=[
        # Include config data file (YAML)
        ('{root_dir}/config/prompts.yaml', 'config'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'tk', '_tkinter'],  # Exclude tkinter completely
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HrisaDocs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',  # Optional: create version info file
    icon='{icon_path}',
)
"""

    spec_file = ROOT_DIR / "HrisaDocs_win.spec"
    spec_file.write_text(spec_content)
    print(f"[OK] Created spec file: {spec_file}")
    return spec_file


def create_version_info():
    """Create version info file for Windows executable."""
    version_info = f"""# UTF-8
#
# Version information for Hrisa Docs

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 1, 0, 0),
    prodvers=(0, 1, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Hrisa Docs'),
        StringStruct(u'FileDescription', u'Document Synthesis Application'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'HrisaDocs'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2026 Hrisa Docs'),
        StringStruct(u'OriginalFilename', u'HrisaDocs.exe'),
        StringStruct(u'ProductName', u'{APP_NAME}'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    version_file = ROOT_DIR / "file_version_info.txt"
    version_file.write_text(version_info, encoding='utf-8')
    print(f"[OK] Created version info: {version_file}")
    return version_file


def build_exe(spec_file):
    """Build the executable using PyInstaller."""
    print("\nBuilding executable...")
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


def create_installer_script():
    """Create Inno Setup script for Windows installer."""
    iss_content = f"""[Setup]
AppName={APP_NAME}
AppVersion={APP_VERSION}
AppPublisher=Hrisa Docs
DefaultDirName={{autopf}}\\HrisaDocs
DefaultGroupName={APP_NAME}
OutputBaseFilename=HrisaDocs-{APP_VERSION}-Setup
Compression=lzma2
SolidCompression=yes
OutputDir=dist
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "installdeps"; Description: "Install required dependencies (Ollama, Pandoc)"; GroupDescription: "Dependencies"; Flags: checkedonce

[Files]
Source: "dist\\HrisaDocs.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "scripts\\check_dependencies.py"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\HrisaDocs.exe"
Name: "{{autodesktop}}\\{APP_NAME}"; Filename: "{{app}}\\HrisaDocs.exe"; Tasks: desktopicon

[Run]
Filename: "python"; Parameters: "{{app}}\\check_dependencies.py --auto"; StatusMsg: "Installing dependencies (Ollama, Pandoc)..."; Tasks: installdeps; Flags: waituntilterminated
Filename: "notepad"; Parameters: "{{%TEMP}}\\hrisa_deps_install.log"; Description: "View dependency installation log"; Flags: postinstall skipifsilent nowait unchecked
Filename: "{{app}}\\HrisaDocs.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent
"""

    iss_file = ROOT_DIR / "installer.iss"
    iss_file.write_text(iss_content)
    print(f"[OK] Created Inno Setup script: {iss_file}")
    return iss_file


def create_installer(iss_file):
    """Create Windows installer using Inno Setup."""
    print("\nCreating Windows installer...")

    # Check if Inno Setup is available
    inno_paths = [
        Path(r"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"),
        Path(r"C:\\Program Files\\Inno Setup 6\\ISCC.exe"),
    ]

    iscc = None
    for path in inno_paths:
        if path.exists():
            iscc = path
            break

    if not iscc:
        print("  Inno Setup not found, skipping installer creation")
        print("  Download from: https://jrsoftware.org/isdl.php")
        return False

    try:
        subprocess.run([str(iscc), str(iss_file)], check=True)
        print("[OK] Installer created successfully!")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Installer creation failed")
        return False


def main():
    """Main build process."""
    print("=" * 60)
    print(f"Building {APP_NAME} for Windows")
    print("=" * 60)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Clean previous builds
    clean_build()

    # Create version info
    create_version_info()

    # Create spec file
    spec_file = create_spec_file()

    # Build executable
    if not build_exe(spec_file):
        sys.exit(1)

    # Create installer script
    iss_file = create_installer_script()

    # Create installer (optional)
    create_installer(iss_file)

    # Summary
    print("\n" + "=" * 60)
    print("Build Summary")
    print("=" * 60)

    exe_file = DIST_DIR / "HrisaDocs.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"[OK] Executable: {exe_file}")
        print(f"  Size: {size_mb:.1f} MB")

    installer_files = list(DIST_DIR.glob("*Setup.exe"))
    if installer_files:
        installer = installer_files[0]
        installer_size_mb = installer.stat().st_size / (1024 * 1024)
        print(f"[OK] Installer: {installer}")
        print(f"  Size: {installer_size_mb:.1f} MB")

    print("\nNext steps:")
    print("1. Test the executable:")
    print(f"   {exe_file}")
    print("2. Test the installer (if created)")
    print("3. Distribute to users")
    print("\nNote: First run may be slow as Windows Defender scans the file")


if __name__ == "__main__":
    main()
