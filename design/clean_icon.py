#!/usr/bin/env python3
"""
Clean up the icon - remove decorative elements and simplify
"""

from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

# Paths
DESIGN_DIR = Path(__file__).parent

def create_simple_version_from_b27cf160():
    """Use the cleaner _b27cf160 icon (simple chili with shadow)"""
    source = DESIGN_DIR / "concepts" / "ai_generated" / "_b27cf160-dc4d-4bda-9cc7-10931b76cd6f.jpeg"
    output = DESIGN_DIR / "finals" / "hrisa_docs_icon_transparent_v2.png"

    print(f"Loading cleaner icon: _b27cf160")

    # Load image
    img = Image.open(source)
    img = img.convert('RGBA')

    # Convert to numpy for processing
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Remove white/light background
    threshold = 230
    light_mask = (r > threshold) & (g > threshold) & (b > threshold)

    # Also remove light grays
    rgb_diff = np.abs(r - g) + np.abs(g - b) + np.abs(r - b)
    similar_and_light = (rgb_diff < 30) & ((r + g + b) / 3 > threshold)

    # Combine masks
    background_mask = light_mask | similar_and_light

    # Set alpha to 0 for background
    data[:,:,3][background_mask] = 0

    # Create new image
    result = Image.fromarray(data)
    result.save(output, 'PNG')

    print(f"[OK] Saved cleaner version: {output.name}")
    print(f"\nThis icon is:")
    print(f"  - Much simpler (just red chili with modern shadow)")
    print(f"  - No decorative elements")
    print(f"  - Clean and professional")

    return output

def crop_and_clean_current():
    """Clean up current icon by removing decorative side elements"""
    source = DESIGN_DIR / "concepts" / "ai_generated" / "_7ab62638-53a2-4822-bb00-91a18002e740.jpeg"
    output = DESIGN_DIR / "finals" / "hrisa_docs_icon_transparent_v2.png"

    print(f"Cleaning up current icon: _7ab62638")

    # Load image
    img = Image.open(source)
    img = img.convert('RGBA')

    # Crop to remove side decorations (keep center 80%)
    width, height = img.size
    crop_margin = int(width * 0.1)

    # Crop
    cropped = img.crop((crop_margin, 0, width - crop_margin, height))

    # Resize back to original size
    resized = cropped.resize((width, height), Image.Resampling.LANCZOS)

    # Convert to numpy for background removal
    data = np.array(resized)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Remove white/light background
    threshold = 230
    light_mask = (r > threshold) & (g > threshold) & (b > threshold)

    # Also remove light grays
    rgb_diff = np.abs(r - g) + np.abs(g - b) + np.abs(r - b)
    similar_and_light = (rgb_diff < 30) & ((r + g + b) / 3 > threshold)

    # Combine masks
    background_mask = light_mask | similar_and_light

    # Set alpha to 0 for background
    data[:,:,3][background_mask] = 0

    # Create new image
    result = Image.fromarray(data)
    result.save(output, 'PNG')

    print(f"[OK] Saved cleaned version: {output.name}")
    print(f"\nThis icon:")
    print(f"  - Removed side decorative elements")
    print(f"  - Cleaner composition")
    print(f"  - Still shows document + chili")

    return output


if __name__ == '__main__':
    print("=" * 60)
    print("Hrisa Docs - Icon Cleanup Options")
    print("=" * 60)
    print()

    # Option 1: Switch to simpler icon
    print("Creating CLEANER version (using _b27cf160)...")
    print("This is the simple red chili with long shadow you preferred earlier.\n")

    output = create_simple_version_from_b27cf160()

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"\nNew icon saved to: {output}")
    print("\nNext step: Run conversion script to regenerate all sizes")
    print("  python3 design/convert_logo.py")
