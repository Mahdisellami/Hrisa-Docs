#!/usr/bin/env python3
"""
Create proper macOS-style icon:
- Keep the white rounded square (document shape)
- Keep the red chili and all details
- Make only the CORNERS transparent (outside the rounded square)
"""

from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

DESIGN_DIR = Path(__file__).parent
SOURCE = DESIGN_DIR / "concepts" / "ai_generated" / "_7ab62638-53a2-4822-bb00-91a18002e740.jpeg"
OUTPUT = DESIGN_DIR / "finals" / "hrisa_docs_icon_macos_style.png"


def create_rounded_square_mask(size, corner_radius):
    """Create a mask for rounded square (iOS/macOS icon style)"""
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)

    # Draw rounded rectangle (will be white/255)
    draw.rounded_rectangle(
        [(0, 0), (size, size)],
        radius=corner_radius,
        fill=255
    )

    return mask


def make_macos_style_icon(source_path, output_path, size=1024):
    """
    Create macOS-style icon:
    1. Load original image
    2. Create rounded square mask
    3. Apply mask so only rounded square area is visible
    4. Corners are transparent
    """
    print(f"Loading: {source_path.name}")

    # Load original
    img = Image.open(source_path).convert('RGBA')

    # Resize if needed
    if img.size != (size, size):
        img = img.resize((size, size), Image.Resampling.LANCZOS)

    # Create rounded square mask
    # macOS/iOS uses approximately 22% corner radius
    corner_radius = int(size * 0.2237)  # Standard iOS radius
    print(f"Creating rounded square mask (radius: {corner_radius}px)")

    mask = create_rounded_square_mask(size, corner_radius)

    # Apply mask to image
    # The mask determines transparency: 255 = opaque, 0 = transparent
    img.putalpha(mask)

    # Save
    img.save(output_path, 'PNG')
    print(f"[OK] Saved: {output_path.name}")
    print()
    print("Icon now has:")
    print("  ✓ White rounded square shape (like macOS apps)")
    print("  ✓ Transparent corners")
    print("  ✓ Red chili and all details preserved")

    return img


def main():
    print("=" * 60)
    print("Hrisa Docs - Create Proper macOS Icon")
    print("=" * 60)
    print()

    result = make_macos_style_icon(SOURCE, OUTPUT)

    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nProper macOS icon: {OUTPUT}")
    print("\nNext: Update convert_logo.py and rebuild")

    return result


if __name__ == '__main__':
    main()
