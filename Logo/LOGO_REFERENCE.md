# Mander / Mander Wines — Logo Authoritative Reference

> **This is the single source of truth for the Mander logo.** Whenever the user references "the Logo", "the logo", "Mander logo", "Mander Wines logo", or "our logo", it means this file and the assets listed here. Never invent, re-imagine, approximate, or ask a generative AI to draw the logo — always composite from the files below.

---

## 1. Authoritative source

| | |
|---|---|
| Master vector | `/Users/jmander/Downloads/Mander logo_adj.pdf` (also `.ai`) |
| **THE source** | `Mander Wines/images/logo-pdf-raw.png` — qlmanage render of the PDF at 3000×1509, white bg made transparent, full alpha preserved. This is the ONE source to use for everything: brand exports AND scene composites. |

**Do NOT use:**
- `images/logo-adj.png` — old poppler-rendered extraction **missing the double horizontal rule lines** that flank the monogram. Legacy only.
- `images/logo-pdf-native.png` — deprecated pre-compensation experiment. The soft-plate compositing recipe (below) makes pre-compensation unnecessary.

---

## 2. Canonical colours (pixel-verified against PDF, 2026-04-23)

| Element | Hex | RGB | Verification |
|---|---|---|---|
| M monogram (royal blue) | `#1C4C8C` | `(28, 76, 140)` | 32,965 core pixels — PDF mode |
| Wordmark + rules (warm dark) | `#433C39` | `(67, 60, 57)` | 193,006 core pixels — PDF mode |

Sampled from the 3000×1509 qlmanage render of `Mander logo_adj.pdf`. Every exported Logo file has been verified as **pixel-identical** (deltaE 0.00) to these values.

### Compositing onto muted / cream backgrounds (THE working recipe)

When placing the logo into a scene with a muted cream bg (e.g. Instagram Coming Soon), the antialiased edges would blend with the cream if placed directly — making strokes read thinner and the blue washed-out. Solution: lay down a **broad soft white plate** before placing the logo. The plate is invisibly diffuse (no boundary artifact) but locally lifts the bg toward white, so the logo's antialiased edges blend with near-white — same as the PDF on its white page.

**Recipe** (scales to SIZE=1080; adjust proportionally for other canvases):

```python
# 1. Broad inner plate — mostly white, heavily blurred
cx, cy = int(SIZE * 0.50), int(SIZE * 0.17)  # or wherever logo centre is
plate = Image.new("RGBA", bg.size, (0, 0, 0, 0))
ImageDraw.Draw(plate).ellipse(
    [cx - 430, cy - 200, cx + 430, cy + 200], fill=(255, 255, 255, 225)
)
plate = plate.filter(ImageFilter.GaussianBlur(radius=130))
bg = Image.alpha_composite(bg, plate)

# 2. Wider soft outer wash to blend plate into the scene
wash = Image.new("RGBA", bg.size, (0, 0, 0, 0))
ImageDraw.Draw(wash).ellipse(
    [cx - 640, cy - 300, cx + 640, cy + 300], fill=(255, 254, 250, 110)
)
wash = wash.filter(ImageFilter.GaussianBlur(radius=200))
bg = Image.alpha_composite(bg, wash)

# 3. Place the raw PDF-native logo on top — NO recolouring, NO compensation
place_logo(bg, width_pct=0.60, cx_pct=0.50, cy_pct=0.17, glow=False)
```

Result on muted cream: CS blue core = `#1C4C8C` (pixel-identical to PDF), deltaE 0.00 on mode, ~2.1 on average (edge of perceptibility). Verified 2026-04-23.

**DO NOT:**
- Apply pixel pre-compensation (the `-8,-8,-7` shift or the `#1A3068` override from earlier experiments). The plate makes it unnecessary and the result no longer pixel-matches the PDF.
- Use a shape-matched "halo" (dilated alpha silhouette). It IS visible and the user rejected it.
- Place the logo directly on the muted bg with no plate. Edges blend with cream and the logo reads washed/thin.

---

## 3. Logo structure (all elements must be present)

The real logo has four parts — any rendering missing one of these is wrong:

1. **M monogram** (centred top, blue `#1C4C8C`)
2. **Double rule lines** flanking the monogram horizontally (left and right of M, dark `#433C39`)
3. **MANDER wordmark** beneath the monogram (serif, dark `#433C39`)
4. **Single bottom rule line** underneath the wordmark (dark `#433C39`)

The earlier `logo-adj.png` was missing #2 (the double rules) — this caused visible structural mismatch with the PDF in all prior outputs. Always verify the rendered logo includes all four elements before finalising.

---

## 4. Brand asset file inventory

Location: `/Users/jmander/Desktop/Claude/Mander Wines/Logo/`

### Full logo (`Mander-logo-full.*`)

| File | Background | Use case |
|---|---|---|
| `.png` | Transparent | Web overlays, compositing on photos |
| `-white-bg.png` | White | Placements on coloured surfaces |
| `.jpg` | White | Systems that require JPG (email, legacy) |
| `.pdf` | White | Print, decks, letterheads |
| `.svg` | Transparent (embedded PNG) | Web — scales at target size |
| `.webp` | Transparent | Modern web, smaller file |
| `.tiff` | Transparent | High-end print |
| `@4x.png` / `@4x.jpg` | Transparent / White | Print-ready hi-res (4×) |

### M monogram alone (`Mander-monogram.*`)

Same format catalogue — use where the full wordmark won't fit (favicons, profile pictures, wax seals, cork stamps, bottle capsules).

---

## 5. Usage rules

**DO:**
- Composite directly from the PNG (transparent), SVG, or PDF files in this directory
- Use the @4x variants for print (magazines, posters, packaging)
- Use the monogram-only files when space is tight (favicons, social profile)
- Pre-compensate the source blue with `(-8, -8, -7)` shift only when compositing onto muted/cream backgrounds where bg bleed lightens the blue

**DO NOT:**
- Ask Gemini / Claude / any generative AI to "draw the Mander logo" or "add a Mander engraving" — always composite from these real files
- Use `logo-adj.png` — it is missing the double rule lines
- Re-render the PDF via poppler (`pdftoppm`) — uses a different colour profile and gives a brighter, wrong blue
- Use JPG when PNG is available — JPG's YCbCr encoding drifts saturated blues upward
- Add cream-coloured halos/glows around the logo — creates visible rectangular outline artifacts
- Modify brand asset files for bg-specific compensation — compensation happens in the compositing script at paste time, not in the source files
- Assume pixel-perfect source = pixel-perfect output on every bg — simultaneous contrast and antialiased edges bias the rendered pixel toward the bg's colour. Pre-compensation handles this.

---

## 6. Regeneration

If the PDF source artwork changes:

```bash
# 1. Render the PDF via macOS native (qlmanage) for authoritative colours
qlmanage -t -s 3000 -o /tmp "/Users/jmander/Downloads/Mander logo_adj.pdf"

# 2. Convert to transparent-bg PNG with proper alpha (see export_logo.py header)
#    — save to images/logo-pdf-raw.png

# 3. Regenerate all brand exports
cd "/Users/jmander/Desktop/Claude/Mander Wines/Logo"
python3 export_logo.py
```

Always use `qlmanage` (or `sips`) — not poppler — to render the PDF. macOS Core Graphics gives the correct colour profile; poppler does not.

---

## 7. Verification checklist before shipping any logo-containing asset

1. Core blue pixel is `#1C4C8C` ±2 per channel (or pre-compensated `(20, 68, 133)` for muted bg)
2. Dark pixel is `#433C39` ±2 per channel
3. All four logo elements present (monogram + double rules + wordmark + bottom rule)
4. Edge antialiasing is clean (no rectangular outlines, no cream halo artifacts)
5. CIE Lab deltaE to the PDF < 2.0 (imperceptible)

---

## 8. Related files

- `README.md` — short-form summary of the Logo directory
- `export_logo.py` — regenerator script
- Canonical memory note: `~/.claude/projects/-Users-jmander/memory/reference_mander_logo.md`
- Hard-rule memory: `~/.claude/projects/-Users-jmander/memory/feedback_the_logo_means_pdf.md`
