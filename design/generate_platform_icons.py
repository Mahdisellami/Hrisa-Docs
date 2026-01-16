#!/usr/bin/env python3
"""
Generate platform-specific icons from a master image.

Usage:
    python generate_platform_icons.py <master_image.png>

Requirements:
    pip install Pillow

Input:
    - Master image (PNG, 1024x1024 or larger, transparent background)

Output:
    - macOS .icns file (all required sizes)
    - Windows .ico file (all required sizes)
    - Linux PNG files (multiple sizes)
    - Updated assets/icon.* files
"""

import os
import sys
import subprocess
from pathlib import Path
from PIL import Image

# Required sizes for each platform
MACOS_SIZES = [
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]

WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]
LINUX_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]


def resize_image(input_path: Path, output_path: Path, size: int) -> None:
    """Resize image to specified size with high-quality resampling."""
    img = Image.open(input_path)

    # Ensure image is RGBA for transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Resize with high-quality Lanczos filter
    img_resized = img.resize((size, size), Image.Resampling.LANCZOS)

    # Save
    img_resized.save(output_path, 'PNG')
    print(f"  ✓ Created {size}x{size}: {output_path.name}")


def generate_macos_iconset(master_image: Path, output_dir: Path) -> Path:
    """Generate macOS .iconset folder with all required sizes."""
    print("\n📦 Generating macOS icon set...")

    iconset_dir = output_dir / "HrisaDocs.iconset"
    iconset_dir.mkdir(exist_ok=True)

    for size, filename in MACOS_SIZES:
        output_path = iconset_dir / filename
        resize_image(master_image, output_path, size)

    return iconset_dir


def convert_to_icns(iconset_dir: Path, output_path: Path) -> bool:
    """Convert .iconset folder to .icns file using iconutil."""
    print(f"\n🔨 Converting to .icns...")

    try:
        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ Created {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("  ✗ iconutil not found (only available on macOS)")
        return False


def generate_windows_ico(master_image: Path, output_path: Path) -> bool:
    """Generate Windows .ico file with all required sizes."""
    print("\n📦 Generating Windows .ico...")

    # Check if ImageMagick is available
    try:
        subprocess.run(["convert", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ⚠️  ImageMagick not found. Trying PIL method...")
        return generate_windows_ico_pil(master_image, output_path)

    # Create temporary PNGs for each size
    temp_dir = output_path.parent / "temp_ico"
    temp_dir.mkdir(exist_ok=True)

    temp_files = []
    for size in WINDOWS_SIZES:
        temp_file = temp_dir / f"icon_{size}.png"
        resize_image(master_image, temp_file, size)
        temp_files.append(str(temp_file))

    # Use ImageMagick to create .ico
    try:
        subprocess.run(
            ["convert"] + temp_files + [str(output_path)],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ Created {output_path}")
        success = True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr.decode()}")
        success = False

    # Clean up temp files
    for temp_file in temp_files:
        Path(temp_file).unlink()
    temp_dir.rmdir()

    return success


def generate_windows_ico_pil(master_image: Path, output_path: Path) -> bool:
    """Generate Windows .ico using PIL (fallback method)."""
    try:
        img = Image.open(master_image)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create resized versions
        icon_sizes = [(size, size) for size in WINDOWS_SIZES]
        img.save(output_path, format='ICO', sizes=icon_sizes)

        print(f"  ✓ Created {output_path} (PIL method)")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def generate_linux_pngs(master_image: Path, output_dir: Path) -> None:
    """Generate Linux PNG files at various sizes."""
    print("\n📦 Generating Linux PNG icons...")

    for size in LINUX_SIZES:
        output_path = output_dir / f"hrisa_docs_icon_{size}x{size}.png"
        resize_image(master_image, output_path, size)


def copy_to_assets(source_files: dict, assets_dir: Path) -> None:
    """Copy generated files to assets/ directory."""
    print("\n📁 Copying to assets directory...")

    assets_dir.mkdir(exist_ok=True)

    for name, source in source_files.items():
        if source.exists():
            dest = assets_dir / name
            import shutil
            shutil.copy2(source, dest)
            print(f"  ✓ Copied {name}")
        else:
            print(f"  ⚠️  Skipped {name} (not found)")


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_platform_icons.py <master_image.png>")
        print("\nMaster image should be:")
        print("  - PNG format")
        print("  - 1024x1024 or larger")
        print("  - Transparent background")
        print("  - High quality (will be scaled down)")
        sys.exit(1)

    master_image = Path(sys.argv[1])

    if not master_image.exists():
        print(f"Error: {master_image} not found")
        sys.exit(1)

    if master_image.suffix.lower() not in ['.png', '.jpg', '.jpeg']:
        print("Error: Master image must be PNG, JPG, or JPEG")
        sys.exit(1)

    # Check image size
    with Image.open(master_image) as img:
        width, height = img.size
        if width < 512 or height < 512:
            print(f"Warning: Image is {width}x{height}. Recommended: 1024x1024 or larger")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                sys.exit(0)

    # Setup directories
    project_root = Path(__file__).parent.parent
    design_dir = project_root / "design"
    finals_dir = design_dir / "finals"
    assets_dir = project_root / "assets"

    finals_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"🎨 Hrisa Docs Icon Generator")
    print(f"{'='*60}")
    print(f"Master image: {master_image}")
    print(f"Output directory: {finals_dir}")
    print(f"{'='*60}")

    # Generate platform-specific icons
    iconset_dir = generate_macos_iconset(master_image, finals_dir)

    icns_path = finals_dir / "hrisa_docs.icns"
    convert_to_icns(iconset_dir, icns_path)

    ico_path = finals_dir / "hrisa_docs.ico"
    generate_windows_ico(master_image, ico_path)

    generate_linux_pngs(master_image, finals_dir)

    # Copy main icon for Linux
    main_icon = finals_dir / "hrisa_docs_icon_512x512.png"
    if main_icon.exists():
        import shutil
        shutil.copy2(main_icon, finals_dir / "hrisa_docs_icon_master.png")

    # Copy to assets directory
    copy_to_assets(
        {
            "icon.icns": icns_path,
            "icon.ico": ico_path,
            "icon.png": main_icon,
        },
        assets_dir,
    )

    print(f"\n{'='*60}")
    print("✅ Icon generation complete!")
    print(f"{'='*60}")
    print("\nGenerated files:")
    print(f"  • macOS:   {icns_path}")
    print(f"  • Windows: {ico_path}")
    print(f"  • Linux:   {finals_dir}/hrisa_docs_icon_*.png")
    print(f"  • Assets:  {assets_dir}/icon.*")
    print("\nNext steps:")
    print("  1. Test icons on each platform")
    print("  2. Rebuild installers with new icons")
    print("  3. Verify icons appear correctly in:")
    print("     - macOS: Dock, Finder, Applications folder")
    print("     - Windows: Taskbar, Start Menu, Desktop")
    print("     - Linux: Application menu, desktop launcher")
    print()


if __name__ == "__main__":
    main()
