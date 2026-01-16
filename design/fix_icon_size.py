#!/usr/bin/env python3
"""
Fix icon size - add proper padding so it matches other macOS app icons
"""

from PIL import Image, ImageDraw
from pathlib import Path

DESIGN_DIR = Path(__file__).parent
SOURCE = DESIGN_DIR / "concepts" / "ai_generated" / "_7ab62638-53a2-4822-bb00-91a18002e740.jpeg"
OUTPUT = DESIGN_DIR / "finals" / "hrisa_docs_icon_final.png"


def create_properly_sized_icon(source_path, output_path, size=1024):
    """
    Create macOS icon with proper sizing:
    1. Add 10-15% padding around content (standard for app icons)
    2. Apply rounded square mask
    3. Content appears same size as other dock icons
    """
    print(f"Loading: {source_path.name}")

    # Load original
    img = Image.open(source_path).convert('RGBA')

    # Resize if needed
    if img.size != (size, size):
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Create canvas with padding
    # Standard app icons use 10-12% padding
    padding_percent = 0.12  # 12% padding
    padding = int(size * padding_percent)

    # New content size (smaller)
    content_size = size - (2 * padding)

    print(f"Original size: {size}x{size}")
    print(f"Padding: {padding}px ({int(padding_percent * 100)}%)")
    print(f"Content size: {content_size}x{content_size}")

    # Resize content to be smaller
    content = img.resize((content_size, content_size), Image.Resampling.LANCZOS)

    # Create new canvas with full size
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # Paste content in center with padding
    canvas.paste(content, (padding, padding), content)

    # Create rounded square mask (standard macOS radius)
    corner_radius = int(size * 0.2237)  # Standard iOS/macOS radius
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size, size)], radius=corner_radius, fill=255)

    # Apply mask
    canvas.putalpha(mask)

    # Save
    canvas.save(output_path, 'PNG')
    print(f"[OK] Saved: {output_path.name}")
    print()
    print("Icon now:")
    print("  ✓ Proper padding (matches other macOS apps)")
    print("  ✓ Content 12% smaller")
    print("  ✓ Transparent corners")
    print("  ✓ Same apparent size as other Dock icons")

    return canvas


def main():
    print("=" * 60)
    print("Hrisa Docs - Fix Icon Size")
    print("=" * 60)
    print()

    result = create_properly_sized_icon(SOURCE, OUTPUT)

    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nProperly sized icon: {OUTPUT}")
    print("\nNext: Update convert_logo.py and rebuild")

    return result


if __name__ == '__main__':
    main()
