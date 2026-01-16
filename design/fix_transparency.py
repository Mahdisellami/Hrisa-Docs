#!/usr/bin/env python3
"""
Properly remove ALL background from the icon - make it truly transparent
"""

from PIL import Image
import numpy as np
from pathlib import Path

DESIGN_DIR = Path(__file__).parent
SELECTED_LOGO = DESIGN_DIR / "concepts" / "ai_generated" / "_7ab62638-53a2-4822-bb00-91a18002e740.jpeg"
OUTPUT = DESIGN_DIR / "finals" / "hrisa_docs_icon_transparent_fixed.png"


def remove_background_aggressive(img_path, output_path):
    """
    Aggressively remove ALL light/white/gray background
    Keep only the red chili and dark elements
    """
    print(f"Loading: {img_path.name}")

    # Load and convert to RGBA
    img = Image.open(img_path).convert('RGBA')
    data = np.array(img)

    # Separate channels
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Strategy: Keep only pixels that are:
    # 1. Red (chili) - high R, low G, low B
    # 2. Dark (outlines, shadows) - all RGB low
    # 3. White document fold - but only if surrounded by red

    # Mask 1: Keep red pixels (chili)
    is_red = (r > 150) & (r > g * 1.3) & (r > b * 1.3)

    # Mask 2: Keep dark pixels (outlines, shadows, black elements)
    is_dark = (r < 100) & (g < 100) & (b < 100)

    # Mask 3: Keep medium dark grays (document fold shadows)
    is_medium_gray = (r < 180) & (g < 180) & (b < 180) & (
        (np.abs(r - g) < 20) & (np.abs(g - b) < 20) & (np.abs(r - b) < 20)
    )

    # Combine: Keep red, dark, or medium gray pixels
    keep_mask = is_red | is_dark | is_medium_gray

    # Set alpha to 0 for everything else
    data[:,:,3] = np.where(keep_mask, 255, 0)

    # Create image
    result = Image.fromarray(data, 'RGBA')

    # Save
    result.save(output_path, 'PNG')
    print(f"[OK] Saved: {output_path.name}")

    return result


def main():
    print("=" * 60)
    print("Hrisa Docs - Fix Transparency Properly")
    print("=" * 60)
    print()

    # Remove background aggressively
    result = remove_background_aggressive(SELECTED_LOGO, OUTPUT)

    print()
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nFixed transparent icon: {OUTPUT}")
    print("\nBackground is now TRULY transparent")
    print("Only red chili and dark elements remain")
    print()
    print("Next: Update convert_logo.py to use this file")

    return result


if __name__ == '__main__':
    main()
