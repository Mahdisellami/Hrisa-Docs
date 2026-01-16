#!/usr/bin/env python3
"""
Remove white/gray background from logo and make it transparent
"""

from PIL import Image
import numpy as np
from pathlib import Path

# Paths
DESIGN_DIR = Path(__file__).parent
SELECTED_LOGO = DESIGN_DIR / "concepts" / "ai_generated" / "_7ab62638-53a2-4822-bb00-91a18002e740.jpeg"
OUTPUT_PNG = DESIGN_DIR / "finals" / "hrisa_docs_icon_transparent.png"


def remove_background(img_path, output_path, threshold=240):
    """
    Remove light background from image and make it transparent.

    Args:
        img_path: Input image path
        output_path: Output path for transparent PNG
        threshold: RGB threshold for background removal (0-255)
    """
    print(f"Loading image: {img_path.name}")

    # Load image
    img = Image.open(img_path)
    img = img.convert('RGBA')

    # Convert to numpy array for processing
    data = np.array(img)

    # Get RGB channels
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

    # Create mask for light pixels (background)
    # Light gray/white pixels where all RGB values are above threshold
    light_mask = (r > threshold) & (g > threshold) & (b > threshold)

    # Also remove light grays (when R, G, B are similar and high)
    # Calculate how similar the RGB values are
    rgb_diff = np.abs(r - g) + np.abs(g - b) + np.abs(r - b)
    similar_and_light = (rgb_diff < 30) & ((r + g + b) / 3 > threshold)

    # Combine masks
    background_mask = light_mask | similar_and_light

    # Set alpha channel to 0 (transparent) for background pixels
    data[:,:,3][background_mask] = 0

    # Create new image from array
    result = Image.fromarray(data, 'RGBA')

    # Save
    result.save(output_path, 'PNG')
    print(f"[OK] Saved transparent version: {output_path.name}")

    return result


def preview_transparency(img, size=512):
    """Show what the transparent image will look like"""
    # Create a preview with checkerboard background
    preview = Image.new('RGBA', (size, size), (255, 255, 255, 0))

    # Create checkerboard pattern
    checker_size = 20
    for i in range(0, size, checker_size * 2):
        for j in range(0, size, checker_size * 2):
            preview.paste((220, 220, 220, 255), (i, j, i + checker_size, j + checker_size))
            preview.paste((220, 220, 220, 255), (i + checker_size, j + checker_size, i + checker_size * 2, j + checker_size * 2))

    # Resize logo to fit
    logo_resized = img.resize((size, size), Image.Resampling.LANCZOS)

    # Composite logo on checkerboard
    preview = Image.alpha_composite(preview, logo_resized)

    return preview


def main():
    """Remove background and create transparent icon"""
    print("=" * 60)
    print("Hrisa Docs - Make Icon Background Transparent")
    print("=" * 60)

    # Try different threshold values to find best one
    print("\nTesting transparency removal...")

    # Default threshold
    transparent_img = remove_background(SELECTED_LOGO, OUTPUT_PNG, threshold=230)

    print(f"\n[OK] Created transparent version!")
    print(f"  Input:  {SELECTED_LOGO}")
    print(f"  Output: {OUTPUT_PNG}")

    print("\nNow re-running conversion script with transparent image...")

    return transparent_img


if __name__ == '__main__':
    main()
