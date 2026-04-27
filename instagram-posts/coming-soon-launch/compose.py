from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path

BASE = Path("/Users/jmander/Desktop/Claude/Mander Wines/instagram-posts/coming-soon-launch")
BG_DIR = BASE / "backgrounds"
LOGO_PATH = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/logo-adj.png")
OUT_DIR = BASE

SIZE = 1080  # Instagram native square

# Elegant serif fonts available on macOS — Baskerville pairs beautifully with the
# Mander wordmark's classical serif feel.
SERIF_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Baskerville.ttc",
    "/Library/Fonts/Baskerville.ttc",
    "/System/Library/Fonts/Supplemental/Didot.ttc",
    "/System/Library/Fonts/Supplemental/Optima.ttc",
    "/System/Library/Fonts/Times.ttc",
]

def load_font(size, italic=False):
    for path in SERIF_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size, index=1 if italic else 0)
            except Exception:
                continue
    return ImageFont.load_default()

def muted_overlay(img, strength=0.32):
    """Subtle light-grey veil like the reference image — mutes the scene but keeps it visible."""
    overlay = Image.new("RGBA", img.size, (235, 235, 235, int(255 * strength)))
    out = img.convert("RGBA")
    out = Image.alpha_composite(out, overlay)
    return out

def compose(bg_path, out_path, variant=1):
    bg = Image.open(bg_path).convert("RGBA")
    # Center-crop to square then resize to Instagram 1080
    w, h = bg.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    bg = bg.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)

    # Apply subtle muted overlay (variants tweak strength slightly)
    strength = {1: 0.30, 2: 0.55, 3: 0.34, 4: 0.32, 5: 0.30}.get(variant, 0.30)
    bg = muted_overlay(bg, strength=strength)

    # Load exact logo (RGBA with transparency preserved)
    logo = Image.open(LOGO_PATH).convert("RGBA")
    # Scale logo to ~62% of canvas width
    target_w = int(SIZE * 0.62)
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    # Position logo centered, slightly above center
    logo_x = (SIZE - target_w) // 2
    logo_y = int(SIZE * 0.34) - target_h // 2
    bg.paste(logo, (logo_x, logo_y), logo)

    # "COMING SOON" text — classical serif, letter-spaced, centered below logo
    draw = ImageDraw.Draw(bg)
    text = "COMING SOON"
    font_size = int(SIZE * 0.055)
    font = load_font(font_size)

    # Apply letter spacing manually
    spacing_px = int(font_size * 0.35)
    total_w = sum(draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0] for ch in text) + spacing_px * (len(text) - 1)

    text_y = logo_y + target_h + int(SIZE * 0.06)
    cursor_x = (SIZE - total_w) // 2

    # Subtle shadow for readability over any background
    shadow_offset = 2
    for ch in text:
        ch_w = draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0]
        # shadow
        draw.text((cursor_x + shadow_offset, text_y + shadow_offset), ch, font=font, fill=(0, 0, 0, 90))
        # main — deep charcoal to match the Mander wordmark colour
        draw.text((cursor_x, text_y), ch, font=font, fill=(58, 52, 48, 255))
        cursor_x += ch_w + spacing_px

    # Flatten to RGB and save as high-quality JPEG for Instagram
    final = Image.new("RGB", bg.size, (255, 255, 255))
    final.paste(bg, mask=bg.split()[3])
    final.save(out_path, "JPEG", quality=95, optimize=True)
    print(f"  -> {out_path.name}")

def main():
    bgs = sorted(BG_DIR.glob("*.jpeg"))
    for i, bg_path in enumerate(bgs, start=1):
        name = bg_path.stem.split("-", 1)[1]
        out = OUT_DIR / f"mander-coming-soon-{i:02d}-{name}.jpg"
        print(f"Composing variant {i}: {bg_path.name}")
        compose(bg_path, out, variant=i)

    print("\nDone. Files ready for Instagram (1080x1080, JPEG):")
    for f in sorted(OUT_DIR.glob("mander-coming-soon-*.jpg")):
        print(f"  {f}")

if __name__ == "__main__":
    main()
