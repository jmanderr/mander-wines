"""
Export Mander brand logo assets from the authoritative PDF source
(/Users/jmander/Downloads/Mander logo_adj.pdf) using a PDF-native render
that includes ALL logo elements — M monogram, the DOUBLE rule lines
flanking the monogram, the MANDER wordmark, and the bottom horizontal
rule. Source: images/logo-pdf-raw.png (qlmanage render of the PDF at
3000×1509, converted to transparent bg with full alpha for coloured
pixels).

Produces, for both the FULL logo and the M-MONOGRAM alone:
  - PNG transparent background
  - PNG white background
  - JPG white background
  - PDF (raster-embedded, print-ready)
  - SVG (wraps the PNG — scalable in web/docs)
  - WebP (modern web)
  - TIFF (high-end print)
  - @4x hi-res PNG / JPG for print

Colours carried through from the PDF render — no recolouring:
  - Monogram: #1C4C8C (28, 76, 140) — PDF-native royal blue
  - Wordmark + rules: #433C39 (67, 60, 57)
"""
import base64
from pathlib import Path
from PIL import Image

SRC = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/logo-pdf-raw.png")
OUT_DIR = Path("/Users/jmander/Desktop/Claude/Mander Wines/Logo")
OUT_DIR.mkdir(parents=True, exist_ok=True)

src = Image.open(SRC).convert("RGBA")
W, H = src.size
print(f"Source size: {W}×{H}")

def tight_crop(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

def monogram_bbox(img):
    """Find the bounding box of just the blue-monogram pixels."""
    px = img.load()
    w, h = img.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 100:
                continue
            if b > r + 30 and b > g + 30 and b > 100:
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)

def add_white_bg(rgba):
    white = Image.new("RGB", rgba.size, (255, 255, 255))
    white.paste(rgba, mask=rgba.split()[3])
    return white

def save_all(rgba, base_name, hires_scale=4):
    outputs = []
    png_path = OUT_DIR / f"{base_name}.png"
    rgba.save(png_path, "PNG", optimize=True)
    outputs.append(png_path)

    png_white_path = OUT_DIR / f"{base_name}-white-bg.png"
    add_white_bg(rgba).save(png_white_path, "PNG", optimize=True)
    outputs.append(png_white_path)

    jpg_path = OUT_DIR / f"{base_name}.jpg"
    add_white_bg(rgba).save(jpg_path, "JPEG", quality=100, subsampling=0, optimize=True)
    outputs.append(jpg_path)

    pdf_path = OUT_DIR / f"{base_name}.pdf"
    add_white_bg(rgba).save(pdf_path, "PDF", resolution=300.0)
    outputs.append(pdf_path)

    webp_path = OUT_DIR / f"{base_name}.webp"
    rgba.save(webp_path, "WEBP", lossless=True)
    outputs.append(webp_path)

    tiff_path = OUT_DIR / f"{base_name}.tiff"
    rgba.save(tiff_path, "TIFF", compression="tiff_lzw")
    outputs.append(tiff_path)

    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    w_, h_ = rgba.size
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w_}" height="{h_}" viewBox="0 0 {w_} {h_}">
  <image width="{w_}" height="{h_}" xlink:href="data:image/png;base64,{b64}"/>
</svg>'''
    svg_path = OUT_DIR / f"{base_name}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    outputs.append(svg_path)

    hires = rgba.resize((w_ * hires_scale, h_ * hires_scale), Image.LANCZOS)
    hires_png = OUT_DIR / f"{base_name}@{hires_scale}x.png"
    hires.save(hires_png, "PNG", optimize=True)
    outputs.append(hires_png)
    hires_jpg = OUT_DIR / f"{base_name}@{hires_scale}x.jpg"
    add_white_bg(hires).save(hires_jpg, "JPEG", quality=100, subsampling=0, optimize=True)
    outputs.append(hires_jpg)

    return outputs

# Full logo — use the entire PDF-native source as-is
full_logo = tight_crop(src)
print(f"Full logo: {full_logo.size}")
for p in save_all(full_logo, "Mander-logo-full"):
    print(f"  {p.name}")

# M-monogram alone — crop to the blue pixels' bounding box
mb = monogram_bbox(src)
if mb is None:
    raise RuntimeError("Could not find monogram pixels in source")
# Add a small breathing margin around the monogram
pad = 20
mb = (max(0, mb[0]-pad), max(0, mb[1]-pad),
      min(W, mb[2]+pad), min(H, mb[3]+pad))
monogram = tight_crop(src.crop(mb))
print(f"\nMonogram: {monogram.size}")
for p in save_all(monogram, "Mander-monogram"):
    print(f"  {p.name}")

# Colour verification
print("\nColour verification (core pixels):")
from collections import Counter

def verify(img, label):
    w, h = img.size
    px = img.load()
    blues, darks = [], []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 250:
                continue
            if b > r + 30 and b > g + 30 and b > 100:
                blues.append((r, g, b))
            elif max(r, g, b) < 90:
                darks.append((r, g, b))
    if blues:
        core = Counter(blues).most_common(1)[0][0]
        print(f"  {label} blue core: RGB{core} #{core[0]:02X}{core[1]:02X}{core[2]:02X}")
    if darks:
        core = Counter(darks).most_common(1)[0][0]
        print(f"  {label} dark core: RGB{core} #{core[0]:02X}{core[1]:02X}{core[2]:02X}")

verify(full_logo, "Full")
verify(monogram, "Mono")
