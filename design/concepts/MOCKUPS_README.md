# Hrisa Docs - Initial Icon Mockups

## Overview

These are programmatically generated mockups to visualize the minimalist icon concepts from `DESIGN_BRIEFS.md`. They serve as starting points for refinement with AI tools (DALL-E, Midjourney) or vector software (Figma, Inkscape).

## Generated Mockups

### 1. Concept E - Single Chili Mark
**File**: `concept_e_single_chili_*.png`

**Description**: Ultra minimalist - just a bold red chili pepper silhouette with green stem on white background.

**Pros**:
- Maximum simplicity
- Instantly recognizable at small sizes
- Strong brand mark
- Works well as standalone icon

**Cons**:
- Doesn't directly reference "documents"
- May be too simple/generic

**Best Use**: App icon, favicon, loading indicator

---

### 2. Concept F - Document + Chili Corner
**File**: `concept_f_document_chili_*.png`

**Description**: Clean white document page with folded corner, small red chili accent in bottom-right corner.

**Pros**:
- Clearly communicates "document processing"
- Professional appearance
- Chili adds cultural identity without overwhelming
- Good balance of elements

**Cons**:
- Chili might be too small at 16x16 or 32x32 sizes
- Less bold than other concepts

**Best Use**: Document file icons, toolbar icons, professional contexts

---

### 3. Concept A1 - Diagonal Chili
**File**: `concept_a1_diagonal_chili_*.png`

**Description**: White document with bold red chili pepper crossing diagonally from bottom-left to top-right.

**Pros**:
- Strong visual impact
- Dynamic diagonal composition
- Both elements equally prominent
- Memorable design

**Cons**:
- May feel busy at small sizes
- Diagonal line can blur at low resolution

**Best Use**: Main app icon, marketing materials, large sizes

---

### 4. Circular Badge
**File**: `concept_circular_badge_*.png`

**Description**: Red circular badge with white inner circle containing centered chili silhouette.

**Pros**:
- Classic badge/seal aesthetic
- Works well at all sizes (circular is universal)
- Strong brand identity
- Could add text around border if needed

**Cons**:
- Less directly communicates "documents"
- Red border might be too bold for some contexts

**Best Use**: Logo mark, social media profile, stamps/seals

---

## Color Palette Used

All mockups use the official Hrisa Docs color palette:

| Color | Hex | Usage |
|-------|-----|-------|
| Chili Red | #C62828 | Primary chili pepper body |
| Chili Highlight | #D32F2F | Chili pepper highlights |
| Chili Shadow | #B71C1C | Chili pepper shadows |
| Document White | #FAFAFA | Paper/document background |
| Document Shadow | #E0E0E0 | Paper fold/shadow |
| Outline | #212121 | Borders and outlines |
| Stem Green | #4CAF50 | Chili pepper stem |

---

## Sizes Generated

Each concept has been generated at:
- **1024x1024**: Source/master size
- **512x512**: Retina display
- **256x256**: Standard icon size

Additional sizes needed for final production:
- 128x128 (Dock)
- 64x64 (toolbar)
- 32x32 (list view)
- 16x16 (smallest)

---

## Next Steps

### Option 1: Refine These Mockups
Take these into vector software (Figma/Inkscape) and:
1. Make shapes more organic and polished
2. Add subtle gradients or shadows
3. Perfect the proportions
4. Export at all required sizes

### Option 2: Use AI Tools for New Variations
Use the prompts in `../AI_PROMPTS.txt` to generate:
1. More realistic/detailed versions
2. Alternative styles (hand-drawn, geometric, 3D)
3. Variations on these concepts
4. Completely new directions (Chechia, Harissa label, etc.)

### Option 3: Hybrid Approach
1. Use these mockups as references
2. Generate AI variations based on the style you like
3. Take the best AI output and refine in vector software

---

## Recommendations

**For Main App Icon**:
- **Concept A1 (Diagonal Chili)** or **Circular Badge** - Both are bold and memorable

**For Document File Icons**:
- **Concept F (Document + Corner Chili)** - Clearly shows document while adding brand identity

**For Branding/Marketing**:
- **Circular Badge** - Works well as a logo mark and can scale

**Most Versatile**:
- **Concept E (Single Chili)** - Can be used anywhere, simplest to reproduce

---

## Testing at Small Sizes

Before finalizing, test each concept at:
- 16x16 pixels (must still be recognizable)
- 32x32 pixels (toolbar icons)
- 64x64 pixels (standard icons)

**Critical Test**: Place icon next to other app icons on macOS Dock and Windows taskbar - does it stand out? Is it distinguishable?

---

## Files Generated

```
design/concepts/mockups/
├── concept_e_single_chili_1024x1024.png
├── concept_e_single_chili_512x512.png
├── concept_e_single_chili_256x256.png
├── concept_f_document_chili_1024x1024.png
├── concept_f_document_chili_512x512.png
├── concept_f_document_chili_256x256.png
├── concept_a1_diagonal_chili_1024x1024.png
├── concept_a1_diagonal_chili_512x512.png
├── concept_a1_diagonal_chili_256x256.png
├── concept_circular_badge_1024x1024.png
├── concept_circular_badge_512x512.png
└── concept_circular_badge_256x256.png
```

---

## Generation Script

The mockups were generated using `../generate_icon_mockups.py` which uses Python PIL/Pillow to create basic geometric shapes. The script can be modified to experiment with different:
- Colors
- Proportions
- Shapes
- Layouts

To regenerate or modify:
```bash
python3 design/generate_icon_mockups.py
```
