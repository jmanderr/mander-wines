"""
Five 'Coming Soon' variations on the FULL hero-barrels.jpg landscape image.
The existing Mander logo on the right side is preserved — 'Coming Soon' is
placed on the barrel face in 5 different layouts/styles.

Output: 1920x1091 JPEG (Instagram landscape, accepted up to 1.91:1 — this is 1.76:1).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path

BASE = Path("/Users/jmander/Desktop/Claude/Mander Wines/instagram-posts/coming-soon-launch")
HERO = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/hero-barrels.jpg")

# Native resolution keeps every pixel of the original photo
W, H = 1920, 1091

# Fonts
FONT_DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
FONT_BASK = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_OPTIMA = "/System/Library/Fonts/Supplemental/Optima.ttc"
FONT_SNELL = "/System/Library/Fonts/Apple Chancery.ttf"

def load(path, size, index=0):
    if Path(path).exists():
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            pass
    return ImageFont.truetype(FONT_BASK, size=size, index=0)

def full_bg(overlay_strength=0.40):
    """Muted grey-gradient background in the style of editorial coming-soon posts:
    desaturate the warm wood tones, apply a cool-grey veil, then add a soft vertical
    gradient (slightly darker top + bottom) for a dreamy, low-contrast feel."""
    img = Image.open(HERO).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)

    # 1. Desaturate the warm wood tones to neutral greys
    img = ImageEnhance.Color(img).enhance(0.38)   # strong desaturation
    img = ImageEnhance.Brightness(img).enhance(1.04)
    img = ImageEnhance.Contrast(img).enhance(0.92)

    img = img.convert("RGBA")

    # 2. Flat cool-grey veil
    veil = Image.new("RGBA", img.size, (205, 205, 208, int(255 * overlay_strength)))
    img = Image.alpha_composite(img, veil)

    # 3. Subtle vertical gradient — slightly darker top and bottom, lighter in middle
    grad = Image.new("L", (1, H), color=0)
    for y in range(H):
        # quadratic curve: 0 at middle, max at edges
        t = abs(y - H / 2) / (H / 2)
        grad.putpixel((0, y), int(55 * (t ** 1.6)))
    grad = grad.resize((W, H))
    grad_layer = Image.new("RGBA", (W, H), (70, 70, 75, 0))
    grad_layer.putalpha(grad)
    img = Image.alpha_composite(img, grad_layer)

    return img

def measure(draw, text, font, spacing):
    widths = [draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0] for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    a, d = font.getmetrics()
    return widths, total, a + d

def draw_spaced(draw, text, widths, spacing, x0, y, font, fill, shadow=None):
    x = x0
    for ch, cw in zip(text, widths):
        if shadow:
            off, sc = shadow
            draw.text((x + off, y + off), ch, font=font, fill=sc)
        draw.text((x, y), ch, font=font, fill=fill)
        x += cw + spacing

def halo(canvas, text, widths, spacing, x0, y, font, radius=22, alpha=180, colour=(248, 242, 232)):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_spaced(d, text, widths, spacing, x0, y, font, (*colour, alpha))
    return Image.alpha_composite(canvas, layer.filter(ImageFilter.GaussianBlur(radius=radius)))

def save(canvas, name):
    final = Image.new("RGB", canvas.size, (255, 255, 255))
    final.paste(canvas, mask=canvas.split()[3])
    out = BASE / name
    final.save(out, "JPEG", quality=95, optimize=True)
    print(f"  -> {out.name}")

# Layout reference points (original 1920x1091):
# Existing Mander logo bounding box: roughly x=1540 to x=1900, y=470 to y=620
# So the usable "open" area of the barrel face is x=0 to x=1500.
# Centre of that usable area:
LOGO_LEFT = 1540  # existing logo starts here
USABLE_CX = LOGO_LEFT // 2  # ~770 — centre of the open barrel area
BARREL_CY = 545
# Fallback focal point on the main barrel (slightly left of geometric centre)
BARREL_CX = USABLE_CX

# ------------------------------------------------------------------
# V1: "COMING SOON" large, centered on main barrel face (to the left of existing logo)
# ------------------------------------------------------------------
def v1():
    bg = full_bg(0.18)
    text = "COMING SOON"
    font = load(FONT_DIDOT, 150, index=1)  # Didot Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.22)
    widths, total, th = measure(draw, text, font, spacing)
    # Fit within the usable area to the left of the existing logo (max ~1380px wide)
    while total > 1240:
        font = load(FONT_DIDOT, font.size - 4, index=1)
        spacing = int(font.size * 0.22)
        widths, total, th = measure(draw, text, font, spacing)
    x0 = USABLE_CX - total // 2
    y = BARREL_CY - th // 2
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=26, alpha=200)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, (250, 245, 238, 255), shadow=(3, (0, 0, 0, 180)))
    save(bg, "mander-coming-soon-full-01-centered.jpg")

# ------------------------------------------------------------------
# V2: "COMING SOON" beneath the existing logo on the right
# ------------------------------------------------------------------
def v2():
    bg = full_bg(0.18)
    text = "COMING SOON"
    # Fit the text within the width of the existing logo (~360px) so it sits cleanly under it
    font = load(FONT_BASK, 42, index=2)  # Baskerville Bold, smaller
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.32)
    widths, total, th = measure(draw, text, font, spacing)
    # Right-align so text fits within the image, flush under the logo's right edge (~x=1880)
    right_edge = 1880
    x0 = right_edge - total
    y = 680
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=16, alpha=170)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, (250, 245, 238, 255), shadow=(2, (0, 0, 0, 160)))
    save(bg, "mander-coming-soon-full-02-under-logo.jpg")

# ------------------------------------------------------------------
# V3: Script "Coming" + block "SOON" on the main barrel face
# ------------------------------------------------------------------
def v3():
    bg = full_bg(0.20)
    # Script "Coming" — sized to fit within the usable open area (left of existing logo)
    script_font = load(FONT_SNELL, 240)
    script = "Coming"
    draw = ImageDraw.Draw(bg)
    sb = draw.textbbox((0, 0), script, font=script_font)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    sx = USABLE_CX - sw // 2 - sb[0]
    sy = BARREL_CY - sh - 20 - sb[1]
    # halo
    layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((sx, sy), script, font=script_font, fill=(250, 244, 232, 210))
    bg = Image.alpha_composite(bg, layer.filter(ImageFilter.GaussianBlur(radius=28)))
    draw = ImageDraw.Draw(bg)
    draw.text((sx + 4, sy + 4), script, font=script_font, fill=(0, 0, 0, 140))
    draw.text((sx, sy), script, font=script_font, fill=(245, 238, 228, 255))

    # Block "SOON"
    block_font = load(FONT_DIDOT, 130, index=1)
    block = "SOON"
    bb = draw.textbbox((0, 0), block, font=block_font)
    bw_, bh_ = bb[2] - bb[0], bb[3] - bb[1]
    bx = USABLE_CX - bw_ // 2 - bb[0]
    by = sy + sh + 40
    draw.text((bx + 3, by + 3), block, font=block_font, fill=(0, 0, 0, 170))
    draw.text((bx, by), block, font=block_font, fill=(250, 245, 238, 255))
    save(bg, "mander-coming-soon-full-03-script-block.jpg")

# ------------------------------------------------------------------
# V4: "COMING SOON" flanked by rule lines, centered on barrel face
# ------------------------------------------------------------------
def v4():
    bg = full_bg(0.18)
    text = "COMING SOON"
    font = load(FONT_BASK, 95, index=2)
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.32)
    widths, total, th = measure(draw, text, font, spacing)
    # Ensure total + decorative lines fit in usable area (left of existing logo)
    max_w = 1380
    while total + 2 * 180 + 2 * 36 > max_w:
        font = load(FONT_BASK, font.size - 4, index=2)
        spacing = int(font.size * 0.32)
        widths, total, th = measure(draw, text, font, spacing)
    x0 = USABLE_CX - total // 2
    y = BARREL_CY - th // 2
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=20, alpha=170)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, (250, 245, 238, 255), shadow=(3, (0, 0, 0, 170)))
    line_y = y + th // 2 + 4
    gap, line_len = 36, 180
    lc = (250, 245, 238, 230)
    draw.line([(x0 - gap - line_len, line_y), (x0 - gap, line_y)], fill=lc, width=3)
    draw.line([(x0 + total + gap, line_y), (x0 + total + gap + line_len, line_y)], fill=lc, width=3)
    save(bg, "mander-coming-soon-full-04-ruled.jpg")

# ------------------------------------------------------------------
# V5: Large "COMING SOON" across the lower portion of the barrel
# ------------------------------------------------------------------
def v5():
    bg = full_bg(0.16)
    text = "COMING SOON"
    font = load(FONT_OPTIMA, 160, index=1)  # Optima Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.18)
    widths, total, th = measure(draw, text, font, spacing)
    while total > 1380:
        font = load(FONT_OPTIMA, font.size - 4, index=1)
        spacing = int(font.size * 0.18)
        widths, total, th = measure(draw, text, font, spacing)
    x0 = USABLE_CX - total // 2
    y = 820  # lower on the barrel face
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=28, alpha=200)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, (250, 245, 238, 255), shadow=(4, (0, 0, 0, 180)))
    save(bg, "mander-coming-soon-full-05-lower-bold.jpg")

if __name__ == "__main__":
    print("Generating 5 full-image variations...")
    v1(); v2(); v3(); v4(); v5()
    print("Done.")
