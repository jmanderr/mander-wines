"""
Five distinct 'Coming Soon' Instagram variations on the hero-barrels.jpg image.
Each variant uses the EXACT Mander logo (logo-adj.png) — only the layout/typography
of 'Coming Soon' and the logo placement differ.

Output: 1080x1080 JPEG (Instagram feed ready).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

BASE = Path("/Users/jmander/Desktop/Claude/Mander Wines/instagram-posts/coming-soon-launch")
HERO = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/hero-barrels.jpg")
LOGO_PATH = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/logo-adj.png")

SIZE = 1080

# Font catalogue -----------------------------------------------------------
FONT_DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
FONT_BASK = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_SNELL = "/System/Library/Fonts/Apple Chancery.ttf"
FONT_SNELL_ALT = "/System/Library/Fonts/SnellRoundhand.ttc"
FONT_OPTIMA = "/System/Library/Fonts/Supplemental/Optima.ttc"

def load(path, size, index=0):
    if Path(path).exists():
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            pass
    return ImageFont.truetype(FONT_BASK, size=size, index=0)

# Helpers ------------------------------------------------------------------
def square_crop_hero():
    """Square crop of the hero image that excludes the baked-in Mander logo
    on the right edge (which sits at roughly x>=1500 in the 1920-wide source)."""
    img = Image.open(HERO).convert("RGBA")
    w, h = img.size  # 1920x1091
    side = h  # 1091
    # Right edge of crop = 1480 to cut before the existing logo; left shifts accordingly.
    left = max(0, 1480 - side)
    img = img.crop((left, 0, left + side, side))
    return img.resize((SIZE, SIZE), Image.LANCZOS)

def muted_overlay(img, strength=0.22):
    overlay = Image.new("RGBA", img.size, (235, 235, 230, int(255 * strength)))
    return Image.alpha_composite(img.convert("RGBA"), overlay)

def measure(draw, text, font, spacing_px):
    widths = [draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0] for ch in text]
    total = sum(widths) + spacing_px * (len(text) - 1)
    ascent, descent = font.getmetrics()
    return widths, total, ascent + descent

def draw_spaced(draw, text, widths, spacing_px, start_x, y, font, fill, shadow=None):
    x = start_x
    for ch, cw in zip(text, widths):
        if shadow:
            off, sfill = shadow
            draw.text((x + off, y + off), ch, font=font, fill=sfill)
        draw.text((x, y), ch, font=font, fill=fill)
        x += cw + spacing_px

def halo_behind(canvas, text, widths, spacing_px, start_x, y, font, radius=16, alpha=180, colour=(245, 240, 230)):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_spaced(d, text, widths, spacing_px, start_x, y, font, (*colour, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=radius))
    return Image.alpha_composite(canvas, layer)

def place_logo(canvas, width_pct, cx_pct, cy_pct):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    tw = int(SIZE * width_pct)
    th = int(logo.height * tw / logo.width)
    logo = logo.resize((tw, th), Image.LANCZOS)
    x = int(SIZE * cx_pct) - tw // 2
    y = int(SIZE * cy_pct) - th // 2
    canvas.paste(logo, (x, y), logo)
    return x, y, tw, th

def save(canvas, name):
    final = Image.new("RGB", canvas.size, (255, 255, 255))
    final.paste(canvas, mask=canvas.split()[3])
    out = BASE / name
    final.save(out, "JPEG", quality=95, optimize=True)
    print(f"  -> {out.name}")

# ------------------------------------------------------------------
# Variant 1: Logo centred upper, bold Didot "COMING SOON" beneath
# ------------------------------------------------------------------
def variant_1():
    bg = muted_overlay(square_crop_hero(), strength=0.20)
    _, ly, _, lh = place_logo(bg, width_pct=0.60, cx_pct=0.50, cy_pct=0.42)

    text = "COMING SOON"
    font = load(FONT_DIDOT, int(SIZE * 0.072), index=1)  # Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.28)
    widths, total, _ = measure(draw, text, font, spacing)
    y = ly + lh + int(SIZE * 0.05)
    sx = (SIZE - total) // 2
    bg = halo_behind(bg, text, widths, spacing, sx, y, font, radius=18, alpha=180)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, sx, y, font, (38, 30, 26, 255), shadow=(2, (0, 0, 0, 140)))
    save(bg, "mander-coming-soon-hero-01-centered-bold.jpg")

# ------------------------------------------------------------------
# Variant 2: Script "Coming" + block "SOON" (editorial, ref image 1 style)
# ------------------------------------------------------------------
def variant_2():
    bg = muted_overlay(square_crop_hero(), strength=0.22)
    place_logo(bg, width_pct=0.42, cx_pct=0.50, cy_pct=0.25)

    # Script "Coming"
    script_path = FONT_SNELL_ALT if Path(FONT_SNELL_ALT).exists() else FONT_SNELL
    script_font = load(script_path, int(SIZE * 0.24))
    script_text = "Coming"
    draw = ImageDraw.Draw(bg)
    sb = draw.textbbox((0, 0), script_text, font=script_font)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    sx = (SIZE - sw) // 2 - sb[0]
    sy = int(SIZE * 0.50) - sb[1]
    # halo
    halo = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.text((sx, sy), script_text, font=script_font, fill=(250, 245, 235, 200))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=22))
    bg = Image.alpha_composite(bg, halo)
    draw = ImageDraw.Draw(bg)
    draw.text((sx + 3, sy + 3), script_text, font=script_font, fill=(0, 0, 0, 130))
    draw.text((sx, sy), script_text, font=script_font, fill=(245, 240, 232, 255))

    # Block "SOON"
    block_font = load(FONT_DIDOT, int(SIZE * 0.078), index=1)
    block_text = "SOON"
    bd = draw.textbbox((0, 0), block_text, font=block_font)
    bw_, bh_ = bd[2] - bd[0], bd[3] - bd[1]
    bx = (SIZE - bw_) // 2 - bd[0]
    by = sy + sh + int(SIZE * 0.06)
    draw.text((bx + 2, by + 2), block_text, font=block_font, fill=(0, 0, 0, 140))
    draw.text((bx, by), block_text, font=block_font, fill=(40, 32, 28, 255))
    save(bg, "mander-coming-soon-hero-02-script-block.jpg")

# ------------------------------------------------------------------
# Variant 3: Logo small at top, huge minimal "COMING SOON" centred
# ------------------------------------------------------------------
def variant_3():
    bg = muted_overlay(square_crop_hero(), strength=0.24)
    place_logo(bg, width_pct=0.38, cx_pct=0.50, cy_pct=0.20)

    text = "COMING SOON"
    font = load(FONT_OPTIMA, int(SIZE * 0.085), index=1)  # Optima Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.18)
    widths, total, text_h = measure(draw, text, font, spacing)
    # fit within 84% width
    while total > SIZE * 0.84:
        new = max(30, font.size - 2)
        font = load(FONT_OPTIMA, new, index=1)
        spacing = int(font.size * 0.18)
        widths, total, text_h = measure(draw, text, font, spacing)
    y = int(SIZE * 0.56)
    sx = (SIZE - total) // 2
    bg = halo_behind(bg, text, widths, spacing, sx, y, font, radius=20, alpha=200)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, sx, y, font, (35, 28, 24, 255), shadow=(3, (0, 0, 0, 150)))
    save(bg, "mander-coming-soon-hero-03-minimal-bold.jpg")

# ------------------------------------------------------------------
# Variant 4: Logo centred, "COMING SOON" flanked by rule lines (matches logo design)
# ------------------------------------------------------------------
def variant_4():
    bg = muted_overlay(square_crop_hero(), strength=0.22)
    _, ly, _, lh = place_logo(bg, width_pct=0.56, cx_pct=0.50, cy_pct=0.40)

    text = "COMING SOON"
    font = load(FONT_BASK, int(SIZE * 0.055), index=2)  # Baskerville Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.32)
    widths, total, text_h = measure(draw, text, font, spacing)
    y = ly + lh + int(SIZE * 0.06)
    sx = (SIZE - total) // 2

    # Decorative rule lines on either side of the text (echo the logo's horizontal lines)
    bg = halo_behind(bg, text, widths, spacing, sx, y, font, radius=14, alpha=160)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, sx, y, font, (40, 32, 28, 255), shadow=(2, (0, 0, 0, 120)))

    # Rule lines
    line_y = y + text_h // 2 + 2
    gap = int(SIZE * 0.025)
    line_len = int(SIZE * 0.12)
    line_col = (40, 32, 28, 230)
    draw.line([(sx - gap - line_len, line_y), (sx - gap, line_y)], fill=line_col, width=2)
    draw.line([(sx + total + gap, line_y), (sx + total + gap + line_len, line_y)], fill=line_col, width=2)
    save(bg, "mander-coming-soon-hero-04-ruled.jpg")

# ------------------------------------------------------------------
# Variant 5: Logo bottom-right (like original hero), "COMING SOON" large on barrel centre
# ------------------------------------------------------------------
def variant_5():
    bg = muted_overlay(square_crop_hero(), strength=0.20)

    text = "COMING SOON"
    font = load(FONT_DIDOT, int(SIZE * 0.098), index=1)
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.24)
    widths, total, text_h = measure(draw, text, font, spacing)
    while total > SIZE * 0.76:
        new = max(30, font.size - 2)
        font = load(FONT_DIDOT, new, index=1)
        spacing = int(font.size * 0.24)
        widths, total, text_h = measure(draw, text, font, spacing)
    y = int(SIZE * 0.48) - text_h // 2
    sx = (SIZE - total) // 2
    bg = halo_behind(bg, text, widths, spacing, sx, y, font, radius=24, alpha=200)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, sx, y, font, (32, 24, 20, 255), shadow=(3, (0, 0, 0, 160)))

    # Logo small bottom-right
    place_logo(bg, width_pct=0.30, cx_pct=0.80, cy_pct=0.86)
    save(bg, "mander-coming-soon-hero-05-logo-corner.jpg")

if __name__ == "__main__":
    print("Generating 5 hero-barrel variations...")
    variant_1()
    variant_2()
    variant_3()
    variant_4()
    variant_5()
    print("\nAll 5 saved to coming-soon-launch/")
