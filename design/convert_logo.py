#!/usr/bin/env python3
"""
Convert selected logo to all required formats and sizes for Hrisa Docs
"""

import os
from pathlib import Path
from PIL import Image
import shutil

# Paths
DESIGN_DIR = Path(__file__).parent
PROJECT_ROOT = DESIGN_DIR.parent
SELECTED_LOGO = DESIGN_DIR / "finals" / "hrisa_docs_icon_macos_style.png"
FINALS_DIR = DESIGN_DIR / "finals"
ASSETS_DIR = DESIGN_DIR / "assets"

# macOS icon sizes (for .icns)
MACOS_SIZES = [16, 32, 64, 128, 256, 512, 1024]

# Windows icon sizes (for .ico)
WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]

# All sizes we'll generate
ALL_SIZES = sorted(set(MACOS_SIZES + WINDOWS_SIZES))


def ensure_dirs():
    """Create necessary directories"""
    FINALS_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    print(f"[OK] Created directories")


def load_and_convert_to_png():
    """Load JPEG and convert to PNG with proper alpha channel"""
    print(f"\n[1/4] Loading selected logo: {SELECTED_LOGO.name}")

    if not SELECTED_LOGO.exists():
        raise FileNotFoundError(f"Selected logo not found: {SELECTED_LOGO}")

    img = Image.open(SELECTED_LOGO)

    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        print(f"  Converting from {img.mode} to RGBA")
        img = img.convert('RGBA')

    # Save master PNG
    master_png = FINALS_DIR / "hrisa_docs_icon_master.png"
    img.save(master_png, 'PNG', quality=100)
    print(f"  [OK] Saved master PNG: {master_png.name}")

    return img


def generate_all_sizes(master_img):
    """Generate all required icon sizes"""
    print(f"\n[2/4] Generating {len(ALL_SIZES)} icon sizes")

    generated_files = {}

    for size in ALL_SIZES:
        # High-quality resize
        resized = master_img.resize((size, size), Image.Resampling.LANCZOS)

        # Save PNG
        filename = f"hrisa_docs_icon_{size}x{size}.png"
        filepath = FINALS_DIR / filename
        resized.save(filepath, 'PNG', quality=100)

        generated_files[size] = filepath
        print(f"  [OK] {size}x{size}")

    return generated_files


def create_icns_file(size_files):
    """Create macOS .icns file"""
    print(f"\n[3/4] Creating macOS .icns file")

    # Create iconset directory
    iconset_dir = FINALS_DIR / "hrisa_docs.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Copy files with proper naming for iconutil
    iconset_mapping = {
        16: ("icon_16x16.png", "icon_16x16@2x.png"),
        32: ("icon_32x32.png", "icon_32x32@2x.png"),
        64: (None, None),  # Skip, covered by 32@2x
        128: ("icon_128x128.png", "icon_128x128@2x.png"),
        256: ("icon_256x256.png", "icon_256x256@2x.png"),
        512: ("icon_512x512.png", "icon_512x512@2x.png"),
        1024: (None, None),  # Skip, covered by 512@2x
    }

    for size in MACOS_SIZES:
        if size not in size_files:
            continue

        src_file = size_files[size]

        if size == 16:
            # 16x16 and 16x16@2x (32x32)
            shutil.copy(src_file, iconset_dir / "icon_16x16.png")
            if 32 in size_files:
                shutil.copy(size_files[32], iconset_dir / "icon_16x16@2x.png")
        elif size == 32:
            # 32x32 and 32x32@2x (64x64)
            shutil.copy(src_file, iconset_dir / "icon_32x32.png")
            if 64 in size_files:
                shutil.copy(size_files[64], iconset_dir / "icon_32x32@2x.png")
        elif size == 128:
            # 128x128 and 128x128@2x (256x256)
            shutil.copy(src_file, iconset_dir / "icon_128x128.png")
            if 256 in size_files:
                shutil.copy(size_files[256], iconset_dir / "icon_128x128@2x.png")
        elif size == 256:
            # 256x256 and 256x256@2x (512x512)
            shutil.copy(src_file, iconset_dir / "icon_256x256.png")
            if 512 in size_files:
                shutil.copy(size_files[512], iconset_dir / "icon_256x256@2x.png")
        elif size == 512:
            # 512x512 and 512x512@2x (1024x1024)
            shutil.copy(src_file, iconset_dir / "icon_512x512.png")
            if 1024 in size_files:
                shutil.copy(size_files[1024], iconset_dir / "icon_512x512@2x.png")

    print(f"  [OK] Created iconset directory")

    # Use iconutil to create .icns (macOS only)
    icns_file = ASSETS_DIR / "hrisa_docs.icns"

    try:
        import subprocess
        result = subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  [OK] Created {icns_file.name}")
        return icns_file
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] iconutil failed: {e.stderr}")
        print(f"  [INFO] You can manually run: iconutil -c icns {iconset_dir}")
        return None
    except FileNotFoundError:
        print(f"  [INFO] iconutil not found (only available on macOS)")
        print(f"  [INFO] Iconset created at: {iconset_dir}")
        print(f"  [INFO] On macOS, run: iconutil -c icns {iconset_dir}")
        return None


def create_ico_file(size_files):
    """Create Windows .ico file"""
    print(f"\n[4/4] Creating Windows .ico file")

    ico_file = ASSETS_DIR / "hrisa_docs.ico"

    # Collect images for .ico (use multiple sizes)
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_images = []

    for size in ico_sizes:
        if size in size_files:
            img = Image.open(size_files[size])
            ico_images.append(img)

    if not ico_images:
        print(f"  [ERROR] No images available for .ico creation")
        return None

    # Save as .ico with multiple sizes
    try:
        ico_images[0].save(
            ico_file,
            format='ICO',
            sizes=[(img.width, img.height) for img in ico_images]
        )
        print(f"  [OK] Created {ico_file.name} with {len(ico_images)} sizes")
        return ico_file
    except Exception as e:
        print(f"  [ERROR] Failed to create .ico: {e}")
        return None


def copy_to_build_locations(icns_file, ico_file):
    """Copy icons to build script locations"""
    print(f"\n[5/5] Copying icons to build locations")

    # macOS build location
    if icns_file and icns_file.exists():
        macos_icon_dest = PROJECT_ROOT / "assets" / "icon.icns"
        macos_icon_dest.parent.mkdir(exist_ok=True)
        shutil.copy(icns_file, macos_icon_dest)
        print(f"  [OK] Copied to {macos_icon_dest}")

    # Windows build location
    if ico_file and ico_file.exists():
        windows_icon_dest = PROJECT_ROOT / "assets" / "icon.ico"
        windows_icon_dest.parent.mkdir(exist_ok=True)
        shutil.copy(ico_file, windows_icon_dest)
        print(f"  [OK] Copied to {windows_icon_dest}")

    # Also copy a PNG for general use
    master_png = FINALS_DIR / "hrisa_docs_icon_master.png"
    if master_png.exists():
        general_icon_dest = PROJECT_ROOT / "assets" / "icon.png"
        shutil.copy(master_png, general_icon_dest)
        print(f"  [OK] Copied master PNG to {general_icon_dest}")


def main():
    """Main conversion process"""
    print("=" * 60)
    print("Hrisa Docs - Logo Conversion")
    print("=" * 60)
    print(f"\nSelected logo: _7ab62638 (Chili on Document with Fold)")

    ensure_dirs()

    # Step 1: Load and convert
    master_img = load_and_convert_to_png()

    # Step 2: Generate all sizes
    size_files = generate_all_sizes(master_img)

    # Step 3: Create macOS .icns
    icns_file = create_icns_file(size_files)

    # Step 4: Create Windows .ico
    ico_file = create_ico_file(size_files)

    # Step 5: Copy to build locations
    copy_to_build_locations(icns_file, ico_file)

    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  Master PNG: design/finals/hrisa_docs_icon_master.png")
    print(f"  All sizes:  design/finals/hrisa_docs_icon_*x*.png")
    print(f"  macOS icon: design/assets/hrisa_docs.icns")
    print(f"  Windows icon: design/assets/hrisa_docs.ico")
    print(f"\nBuild assets:")
    print(f"  assets/icon.icns (for macOS builds)")
    print(f"  assets/icon.ico (for Windows builds)")
    print(f"  assets/icon.png (general use)")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
