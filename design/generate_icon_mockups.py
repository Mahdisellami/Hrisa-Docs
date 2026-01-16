#!/usr/bin/env python3
"""
Generate basic icon mockups for Hrisa Docs
Creates simple programmatic versions of minimalist concepts
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Color Palette
COLORS = {
    'chili_red': '#C62828',
    'chili_highlight': '#D32F2F',
    'chili_shadow': '#B71C1C',
    'document_white': '#FAFAFA',
    'document_shadow': '#E0E0E0',
    'outline': '#212121',
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_concept_e_single_chili(size=1024):
    """
    Concept E: Single Chili Mark
    Ultra minimalist - just a red chili pepper silhouette
    """
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Calculate proportions
    center_x = size // 2
    center_y = size // 2

    # Chili pepper shape using bezier approximation with ellipses
    # Body (elongated ellipse)
    chili_width = size * 0.15
    chili_height = size * 0.6

    chili_left = center_x - chili_width
    chili_right = center_x + chili_width
    chili_top = center_y - chili_height // 2
    chili_bottom = center_y + chili_height // 2

    # Draw main chili body (elongated ellipse, slightly curved)
    chili_color = hex_to_rgb(COLORS['chili_red'])

    # Draw as polygon to create curved chili shape
    points = []
    # Left side curve
    for i in range(20):
        t = i / 20
        x = chili_left - size * 0.02 * (1 - abs(2*t - 1))  # Slight left bulge
        y = chili_top + t * chili_height
        points.append((x, y))

    # Right side curve
    for i in range(20, 0, -1):
        t = i / 20
        x = chili_right + size * 0.02 * (1 - abs(2*t - 1))  # Slight right bulge
        y = chili_top + t * chili_height
        points.append((x, y))

    draw.polygon(points, fill=chili_color)

    # Draw stem (small green rectangle at top)
    stem_color = (76, 175, 80)  # Green
    stem_width = size * 0.08
    stem_height = size * 0.08
    stem_left = center_x - stem_width / 2
    stem_top = chili_top - stem_height
    draw.rectangle(
        [stem_left, stem_top, stem_left + stem_width, chili_top],
        fill=stem_color
    )

    return img

def create_concept_f_document_chili(size=1024):
    """
    Concept F: Document + Corner Chili
    White document with folded corner and small red chili accent
    """
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Document rectangle (80% of canvas)
    margin = size * 0.1
    doc_left = margin
    doc_top = margin
    doc_right = size - margin
    doc_bottom = size - margin

    # Draw document base
    doc_color = hex_to_rgb(COLORS['document_white'])
    draw.rectangle(
        [doc_left, doc_top, doc_right, doc_bottom],
        fill=doc_color,
        outline=hex_to_rgb(COLORS['outline']),
        width=max(2, size // 256)
    )

    # Folded corner (top-right)
    fold_size = size * 0.15
    fold_points = [
        (doc_right - fold_size, doc_top),
        (doc_right, doc_top + fold_size),
        (doc_right - fold_size, doc_top + fold_size),
    ]
    shadow_color = hex_to_rgb(COLORS['document_shadow'])
    draw.polygon(fold_points, fill=shadow_color)

    # Draw fold line
    draw.line(
        [(doc_right - fold_size, doc_top), (doc_right - fold_size, doc_top + fold_size)],
        fill=hex_to_rgb(COLORS['outline']),
        width=max(1, size // 512)
    )
    draw.line(
        [(doc_right - fold_size, doc_top + fold_size), (doc_right, doc_top + fold_size)],
        fill=hex_to_rgb(COLORS['outline']),
        width=max(1, size // 512)
    )

    # Small chili in bottom-right corner
    chili_size = size * 0.25
    chili_center_x = doc_right - chili_size * 0.6
    chili_center_y = doc_bottom - chili_size * 0.6

    # Chili body
    chili_color = hex_to_rgb(COLORS['chili_red'])
    chili_width = chili_size * 0.2
    chili_height = chili_size * 0.8

    # Draw as ellipse (simplified for corner accent)
    chili_bbox = [
        chili_center_x - chili_width,
        chili_center_y - chili_height / 2,
        chili_center_x + chili_width,
        chili_center_y + chili_height / 2
    ]
    draw.ellipse(chili_bbox, fill=chili_color)

    # Small stem
    stem_width = chili_size * 0.08
    stem_height = chili_size * 0.12
    stem_color = (76, 175, 80)
    stem_bbox = [
        chili_center_x - stem_width / 2,
        chili_bbox[1] - stem_height,
        chili_center_x + stem_width / 2,
        chili_bbox[1]
    ]
    draw.ellipse(stem_bbox, fill=stem_color)

    return img

def create_concept_a1_diagonal_chili(size=1024):
    """
    Concept A1: Single Chili Diagonal
    Document with red chili crossing diagonally
    """
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Document rectangle (70% of canvas)
    margin = size * 0.15
    doc_left = margin
    doc_top = margin
    doc_right = size - margin
    doc_bottom = size - margin

    # Draw document with folded corner
    doc_color = hex_to_rgb(COLORS['document_white'])
    draw.rectangle(
        [doc_left, doc_top, doc_right, doc_bottom],
        fill=doc_color,
        outline=hex_to_rgb(COLORS['outline']),
        width=max(2, size // 256)
    )

    # Folded corner (top-right)
    fold_size = size * 0.12
    fold_points = [
        (doc_right - fold_size, doc_top),
        (doc_right, doc_top + fold_size),
        (doc_right - fold_size, doc_top + fold_size),
    ]
    shadow_color = hex_to_rgb(COLORS['document_shadow'])
    draw.polygon(fold_points, fill=shadow_color)

    # Diagonal chili from bottom-left to top-right
    chili_color = hex_to_rgb(COLORS['chili_red'])

    # Calculate diagonal line
    start_x = doc_left + size * 0.05
    start_y = doc_bottom - size * 0.05
    end_x = doc_right - size * 0.05
    end_y = doc_top + size * 0.05

    # Create chili shape as thick curved line
    chili_width = size * 0.08

    # Draw as polygon (elongated shape along diagonal)
    import math
    angle = math.atan2(end_y - start_y, end_x - start_x)
    perp_angle = angle + math.pi / 2

    offset_x = math.cos(perp_angle) * chili_width
    offset_y = math.sin(perp_angle) * chili_width

    points = [
        (start_x + offset_x, start_y + offset_y),
        (end_x + offset_x, end_y + offset_y),
        (end_x - offset_x, end_y - offset_y),
        (start_x - offset_x, start_y - offset_y),
    ]
    draw.polygon(points, fill=chili_color)

    # Add rounded ends
    draw.ellipse(
        [start_x - chili_width, start_y - chili_width,
         start_x + chili_width, start_y + chili_width],
        fill=chili_color
    )

    # Stem at top end (smaller circle)
    stem_color = (76, 175, 80)
    stem_size = chili_width * 0.6
    draw.ellipse(
        [end_x - stem_size, end_y - stem_size,
         end_x + stem_size, end_y + stem_size],
        fill=stem_color
    )

    return img

def create_concept_circular_badge(size=1024):
    """
    Circular badge concept with chili and document elements
    """
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2
    radius = size * 0.45

    # Draw circular background
    circle_bbox = [center - radius, center - radius, center + radius, center + radius]
    draw.ellipse(circle_bbox, fill=hex_to_rgb(COLORS['chili_red']))

    # Inner white circle for document
    inner_radius = radius * 0.7
    inner_bbox = [
        center - inner_radius, center - inner_radius,
        center + inner_radius, center + inner_radius
    ]
    draw.ellipse(inner_bbox, fill=hex_to_rgb(COLORS['document_white']))

    # Central chili silhouette
    chili_width = size * 0.08
    chili_height = size * 0.35
    chili_bbox = [
        center - chili_width, center - chili_height / 2,
        center + chili_width, center + chili_height / 2
    ]
    draw.ellipse(chili_bbox, fill=hex_to_rgb(COLORS['chili_red']))

    # Stem
    stem_width = chili_width * 0.5
    stem_height = size * 0.06
    stem_bbox = [
        center - stem_width, center - chili_height / 2 - stem_height,
        center + stem_width, center - chili_height / 2
    ]
    draw.ellipse(stem_bbox, fill=(76, 175, 80))

    return img

def main():
    """Generate all icon mockups"""
    output_dir = os.path.join(os.path.dirname(__file__), 'concepts', 'mockups')
    os.makedirs(output_dir, exist_ok=True)

    print("Generating icon mockups...")
    print(f"Output directory: {output_dir}")

    concepts = [
        ('concept_e_single_chili', create_concept_e_single_chili),
        ('concept_f_document_chili', create_concept_f_document_chili),
        ('concept_a1_diagonal_chili', create_concept_a1_diagonal_chili),
        ('concept_circular_badge', create_concept_circular_badge),
    ]

    sizes = [1024, 512, 256]

    for name, func in concepts:
        print(f"\n  Creating {name}...")
        for size in sizes:
            img = func(size)
            filename = f"{name}_{size}x{size}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)
            print(f"    [OK] {filename}")

    print(f"\n[OK] Generated {len(concepts) * len(sizes)} mockup files")
    print(f"\nView mockups in: design/concepts/mockups/")
    print("\nThese are basic programmatic mockups. For final designs,")
    print("you can use these as references with AI tools (DALL-E, Midjourney)")
    print("or refine them in vector software (Figma, Inkscape).")

if __name__ == '__main__':
    main()
