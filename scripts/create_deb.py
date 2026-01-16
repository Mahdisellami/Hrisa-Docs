#!/usr/bin/env python3
"""
Create a .deb package for Debian/Ubuntu distributions.

This script packages the built Linux executable into a proper .deb package
that can be installed with dpkg or apt.

Prerequisites:
- Build the Linux executable first: python scripts/build_linux.py
- The dist/hrisa-docs/ directory must exist
"""

import subprocess
import sys
from pathlib import Path
import shutil
from datetime import datetime

# Project paths
ROOT_DIR = Path(__file__).parent.parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build" / "deb"
EXECUTABLE_DIR = DIST_DIR / "hrisa-docs"
ASSETS_DIR = ROOT_DIR / "assets"

# Package info
PACKAGE_NAME = "hrisa-docs"
VERSION = "0.1.0"
ARCHITECTURE = "amd64"  # or "arm64" for ARM builds
MAINTAINER = "Hrisa Docs Team <support@hrisadocs.com>"
DESCRIPTION_SHORT = "Document processing and synthesis with local LLMs"
DESCRIPTION_LONG = """Hrisa Docs is a powerful desktop application for researchers
 to consolidate publications and documents into synthesized books using
 RAG (Retrieval-Augmented Generation) with local LLMs.
 .
 Features:
  - PDF/DOCX document processing
  - Semantic search with vector embeddings
  - Automatic theme discovery
  - Intelligent synthesis with local LLMs
  - Citation tracking
  - Export to PDF, DOCX, Markdown
"""
HOMEPAGE = "https://github.com/yourusername/Document-Processing"
SECTION = "science"  # debian package section: https://packages.debian.org/
PRIORITY = "optional"


def check_prerequisites():
    """Check if the executable exists."""
    if not EXECUTABLE_DIR.exists():
        print("[ERROR] Executable directory not found!")
        print(f"Expected: {EXECUTABLE_DIR}")
        print("\nBuild the Linux executable first:")
        print("  python scripts/build_linux.py")
        return False

    executable = EXECUTABLE_DIR / PACKAGE_NAME
    if not executable.exists():
        print(f"[ERROR] Executable not found: {executable}")
        return False

    print(f"[OK] Found executable: {executable}")
    return True


def clean_build():
    """Clean previous build artifacts."""
    print("\nCleaning previous .deb builds...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  Removed {BUILD_DIR}")


def create_directory_structure():
    """Create the Debian package directory structure."""
    print("\nCreating package directory structure...")

    # Main directories
    pkg_root = BUILD_DIR / f"{PACKAGE_NAME}_{VERSION}_{ARCHITECTURE}"
    pkg_debian = pkg_root / "DEBIAN"
    pkg_opt = pkg_root / "opt" / PACKAGE_NAME
    pkg_bin = pkg_root / "usr" / "local" / "bin"
    pkg_applications = pkg_root / "usr" / "share" / "applications"
    pkg_icons = pkg_root / "usr" / "share" / "icons" / "hicolor" / "512x512" / "apps"
    pkg_doc = pkg_root / "usr" / "share" / "doc" / PACKAGE_NAME

    for directory in [pkg_debian, pkg_opt, pkg_bin, pkg_applications, pkg_icons, pkg_doc]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  Created {directory.relative_to(BUILD_DIR)}")

    return pkg_root


def copy_application_files(pkg_root):
    """Copy application files to package directory."""
    print("\nCopying application files...")

    pkg_opt = pkg_root / "opt" / PACKAGE_NAME

    # Copy all files from executable directory
    for item in EXECUTABLE_DIR.iterdir():
        dest = pkg_opt / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
            print(f"  Copied directory: {item.name}")
        else:
            shutil.copy2(item, dest)
            print(f"  Copied file: {item.name}")

    # Ensure executable is executable
    executable = pkg_opt / PACKAGE_NAME
    executable.chmod(0o755)
    print(f"  Set executable permissions: {PACKAGE_NAME}")


def create_symlink_script(pkg_root):
    """Create symlink in /usr/local/bin."""
    print("\nCreating symlink...")

    pkg_bin = pkg_root / "usr" / "local" / "bin"
    symlink = pkg_bin / PACKAGE_NAME

    # Create relative symlink
    symlink.symlink_to(f"/opt/{PACKAGE_NAME}/{PACKAGE_NAME}")
    print(f"  Created: /usr/local/bin/{PACKAGE_NAME} -> /opt/{PACKAGE_NAME}/{PACKAGE_NAME}")


def install_desktop_file(pkg_root):
    """Create and install .desktop file."""
    print("\nCreating desktop integration...")

    pkg_applications = pkg_root / "usr" / "share" / "applications"
    desktop_file = pkg_applications / f"{PACKAGE_NAME}.desktop"

    desktop_content = f"""[Desktop Entry]
Version=1.1
Type=Application
Name=Hrisa Docs
GenericName=Document Processor
Comment={DESCRIPTION_SHORT}
Exec=/opt/{PACKAGE_NAME}/{PACKAGE_NAME}
Icon={PACKAGE_NAME}
Terminal=false
Categories=Office;Education;Science;
Keywords=document;pdf;synthesis;llm;research;rag;
StartupNotify=true
StartupWMClass=hrisa-docs
"""

    desktop_file.write_text(desktop_content)
    desktop_file.chmod(0o644)
    print(f"  Created: {desktop_file.name}")


def install_icon(pkg_root):
    """Install application icon."""
    print("\nInstalling icon...")

    pkg_icons = pkg_root / "usr" / "share" / "icons" / "hicolor" / "512x512" / "apps"
    icon_source = ASSETS_DIR / "icon.png"

    if not icon_source.exists():
        print(f"  [WARNING] Icon not found: {icon_source}")
        return

    icon_dest = pkg_icons / f"{PACKAGE_NAME}.png"
    shutil.copy2(icon_source, icon_dest)
    print(f"  Installed: {icon_dest.name}")


def create_copyright_file(pkg_root):
    """Create copyright file."""
    print("\nCreating copyright file...")

    pkg_doc = pkg_root / "usr" / "share" / "doc" / PACKAGE_NAME
    copyright_file = pkg_doc / "copyright"

    copyright_content = f"""Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {PACKAGE_NAME}
Upstream-Contact: {MAINTAINER}
Source: {HOMEPAGE}

Files: *
Copyright: {datetime.now().year} Hrisa Docs Team
License: [Your License]
 [License text here]
"""

    copyright_file.write_text(copyright_content)
    print(f"  Created: {copyright_file.name}")


def create_changelog(pkg_root):
    """Create changelog file."""
    print("\nCreating changelog...")

    pkg_doc = pkg_root / "usr" / "share" / "doc" / PACKAGE_NAME
    changelog_file = pkg_doc / "changelog.gz"

    changelog_content = f"""{PACKAGE_NAME} ({VERSION}) stable; urgency=medium

  * Initial release
  * Document processing with PDF/DOCX support
  * Semantic search with vector embeddings
  * Theme discovery and synthesis
  * Local LLM integration with Ollama

 -- {MAINTAINER}  {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}
"""

    # Compress changelog
    import gzip
    with gzip.open(changelog_file, 'wt') as f:
        f.write(changelog_content)

    print(f"  Created: {changelog_file.name}")


def create_control_file(pkg_root):
    """Create DEBIAN/control file."""
    print("\nCreating control file...")

    pkg_debian = pkg_root / "DEBIAN"
    control_file = pkg_debian / "control"

    # Calculate installed size (in KB)
    total_size = sum(f.stat().st_size for f in pkg_root.rglob('*') if f.is_file())
    installed_size = total_size // 1024

    control_content = f"""Package: {PACKAGE_NAME}
Version: {VERSION}
Architecture: {ARCHITECTURE}
Maintainer: {MAINTAINER}
Installed-Size: {installed_size}
Depends: libqt6core6 (>= 6.2), libqt6gui6 (>= 6.2), libqt6widgets6 (>= 6.2), libxcb-xinerama0, libxcb-cursor0, libxkbcommon-x11-0, libdbus-1-3, libgl1, libglib2.0-0
Recommends: ollama, pandoc, texlive-xetex
Section: {SECTION}
Priority: {PRIORITY}
Homepage: {HOMEPAGE}
Description: {DESCRIPTION_SHORT}
{DESCRIPTION_LONG}
"""

    control_file.write_text(control_content)
    control_file.chmod(0o644)
    print(f"  Created: {control_file.name}")


def create_postinst_script(pkg_root):
    """Create post-installation script."""
    print("\nCreating post-install script...")

    pkg_debian = pkg_root / "DEBIAN"
    postinst_file = pkg_debian / "postinst"

    postinst_content = """#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

exit 0
"""

    postinst_file.write_text(postinst_content)
    postinst_file.chmod(0o755)
    print(f"  Created: {postinst_file.name}")


def create_prerm_script(pkg_root):
    """Create pre-removal script."""
    print("\nCreating pre-removal script...")

    pkg_debian = pkg_root / "DEBIAN"
    prerm_file = pkg_debian / "prerm"

    prerm_content = """#!/bin/bash
set -e

# Clean up any running instances
pkill -f hrisa-docs || true

exit 0
"""

    prerm_file.write_text(prerm_content)
    prerm_file.chmod(0o755)
    print(f"  Created: {prerm_file.name}")


def build_package(pkg_root):
    """Build the .deb package using dpkg-deb."""
    print("\nBuilding .deb package...")

    package_name = f"{PACKAGE_NAME}_{VERSION}_{ARCHITECTURE}.deb"
    output_path = DIST_DIR / package_name

    cmd = [
        "dpkg-deb",
        "--build",
        "--root-owner-group",  # Set ownership to root
        str(pkg_root),
        str(output_path)
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"\n[OK] Package created: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Package build failed:")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print("\n[ERROR] dpkg-deb not found!")
        print("This script must be run on a Debian/Ubuntu system.")
        print("Or run it inside a Docker container:")
        print("  docker run --rm -v $(pwd):/app -w /app ubuntu:22.04 bash -c 'apt-get update && apt-get install -y dpkg-dev && python3 scripts/create_deb.py'")
        return None


def verify_package(package_path):
    """Verify the package contents."""
    print("\nVerifying package...")

    # Show package info
    cmd_info = ["dpkg-deb", "--info", str(package_path)]
    try:
        result = subprocess.run(cmd_info, check=True, capture_output=True, text=True)
        print("\nPackage Information:")
        print(result.stdout)
    except:
        print("  [WARNING] Could not verify package info")

    # Show package contents
    cmd_contents = ["dpkg-deb", "--contents", str(package_path)]
    try:
        result = subprocess.run(cmd_contents, check=True, capture_output=True, text=True)
        print("\nPackage Contents:")
        print(result.stdout[:1000])  # First 1000 chars
        if len(result.stdout) > 1000:
            print("  ... (truncated)")
    except:
        print("  [WARNING] Could not list package contents")


def main():
    """Main packaging process."""
    print("=" * 60)
    print(f"Creating .deb package for {PACKAGE_NAME}")
    print("=" * 60)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Clean previous builds
    clean_build()

    # Create directory structure
    pkg_root = create_directory_structure()

    # Copy files
    copy_application_files(pkg_root)
    create_symlink_script(pkg_root)
    install_desktop_file(pkg_root)
    install_icon(pkg_root)

    # Create package metadata
    create_copyright_file(pkg_root)
    create_changelog(pkg_root)
    create_control_file(pkg_root)
    create_postinst_script(pkg_root)
    create_prerm_script(pkg_root)

    # Build package
    package_path = build_package(pkg_root)

    if not package_path:
        sys.exit(1)

    # Verify package
    verify_package(package_path)

    # Summary
    print("\n" + "=" * 60)
    print("Build Summary")
    print("=" * 60)

    package_size_mb = package_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Package: {package_path}")
    print(f"  Size: {package_size_mb:.1f} MB")

    print("\nNext steps:")
    print("1. Install the package:")
    print(f"   sudo dpkg -i {package_path}")
    print("   sudo apt-get install -f  # Fix dependencies if needed")
    print("\n2. Run the application:")
    print(f"   {PACKAGE_NAME}")
    print("\n3. Or find 'Hrisa Docs' in your applications menu")
    print("\n4. Uninstall:")
    print(f"   sudo apt-get remove {PACKAGE_NAME}")
    print("\n5. Test on clean Ubuntu:")
    print(f"   docker run -it --rm ubuntu:22.04 bash")
    print(f"   # Inside container: dpkg -i /path/to/{package_path.name}")


if __name__ == "__main__":
    main()
