"""
Five 'Coming Soon' variations on the new wine-glass/bottle backgrounds.
Uses the EXACT Mander logo (logo-adj.png) and a BOLDER font for 'COMING SOON'
(Didot Bold / Optima Bold — a deliberate move away from the thin Baskerville
the user disliked in the earlier wine-pour comp).

Aesthetic: grey-gradient desaturated look the user confirmed — soft veil,
mild desaturation, vertical gradient for that editorial 'coming soon' feel.

Output: 1080x1080 JPEG (Instagram feed native).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
from pathlib import Path

BASE = Path("/Users/jmander/Desktop/Claude/Mander Wines/instagram-posts/coming-soon-launch")
BG_DIR = BASE / "backgrounds"
LOGO_PATH = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/logo-pdf-raw.png")

SIZE = 1080

FONT_DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
FONT_OPTIMA = "/System/Library/Fonts/Supplemental/Optima.ttc"
FONT_BASK = "/System/Library/Fonts/Supplemental/Baskerville.ttc"
FONT_SNELL = "/System/Library/Fonts/Apple Chancery.ttf"


def load(path, size, index=0):
    if Path(path).exists():
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            pass
    return ImageFont.truetype(FONT_BASK, size=size, index=0)


def prep_bg(src_path, desat=0.45, veil_strength=0.32, veil_rgb=(210, 208, 208)):
    """Square-crop the source, then apply the grey-gradient editorial treatment:
    desaturate the wine's warm tones, apply a soft cool-grey veil, and add a
    mild vertical gradient (slightly darker top + bottom) for depth."""
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)

    img = ImageEnhance.Color(img).enhance(desat)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = ImageEnhance.Contrast(img).enhance(0.95)

    img = img.convert("RGBA")

    veil = Image.new("RGBA", img.size, (*veil_rgb, int(255 * veil_strength)))
    img = Image.alpha_composite(img, veil)

    grad = Image.new("L", (1, SIZE), color=0)
    for y in range(SIZE):
        t = abs(y - SIZE / 2) / (SIZE / 2)
        grad.putpixel((0, y), int(60 * (t ** 1.6)))
    grad = grad.resize((SIZE, SIZE))
    grad_layer = Image.new("RGBA", (SIZE, SIZE), (60, 60, 70, 0))
    grad_layer.putalpha(grad)
    img = Image.alpha_composite(img, grad_layer)
    return img


def recolor_logo(logo, text_rgb=None, monogram_rgb=None):
    """Replace RGB of wordmark/lines (grey) and/or monogram (blue). The source
    encodes antialiasing purely in the alpha channel — RGB is constant across
    each element — so we just swap RGB and leave alpha untouched."""
    px = logo.load()
    w, h = logo.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            is_blue = b > r + 25 and b > g + 15
            target = monogram_rgb if is_blue else text_rgb
            if target is None:
                continue
            px[x, y] = (target[0], target[1], target[2], a)
    return logo


def premultiplied_resize(img, size):
    """Resize RGBA with premultiplied alpha so antialiased edges don't bleed
    the logo colour toward the transparent-pixel RGB during LANCZOS filtering."""
    px = img.load()
    w, h = img.size
    pm = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pmx = pm.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            pmx[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    pm = pm.resize(size, Image.LANCZOS)
    rx = pm.load()
    for y in range(size[1]):
        for x in range(size[0]):
            r, g, b, a = rx[x, y]
            if a > 0:
                rx[x, y] = (min(255, r * 255 // a), min(255, g * 255 // a), min(255, b * 255 // a), a)
    return pm


def place_logo(canvas, width_pct, cx_pct, cy_pct, glow=False, text_color=None, monogram_color=None):
    logo = Image.open(LOGO_PATH).convert("RGBA")
    if text_color is not None or monogram_color is not None:
        logo = recolor_logo(logo, text_rgb=text_color, monogram_rgb=monogram_color)
    tw = int(SIZE * width_pct)
    th = int(logo.height * tw / logo.width)
    # Use premultiplied resize only if size differs from source — otherwise skip
    # to preserve the PDF-native pixel values exactly.
    if (tw, th) != logo.size:
        logo = premultiplied_resize(logo, (tw, th))
    x = int(SIZE * cx_pct) - tw // 2
    y = int(SIZE * cy_pct) - th // 2

    if glow:
        # Cream glow that only appears OUTSIDE the logo silhouette — we blur a
        # filled silhouette and then subtract the logo's own alpha so the halo
        # doesn't bleed cream tint into the (antialiased) monogram or wordmark.
        alpha_mask = logo.split()[3]
        pad = 90
        silhouette = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
        fill = Image.new("RGBA", (tw, th), (252, 246, 234, 255))
        fill.putalpha(alpha_mask)
        silhouette.paste(fill, (pad, pad), fill)
        silhouette = silhouette.filter(ImageFilter.GaussianBlur(radius=38))

        # Punch out the logo area + a 3px buffer so halo doesn't bleed into
        # antialiased logo edges (which would otherwise wash out the blue).
        punch = Image.new("L", (tw + pad * 2, th + pad * 2), 0)
        punch.paste(alpha_mask, (pad, pad))
        punch = punch.filter(ImageFilter.MaxFilter(7))  # dilate by ~3px
        halo_alpha = ImageChops.subtract(silhouette.split()[3], punch)
        silhouette.putalpha(halo_alpha)

        canvas.alpha_composite(silhouette, (x - pad, y - pad))

    canvas.paste(logo, (x, y), logo)
    return x, y, tw, th


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


def halo(canvas, text, widths, spacing, x0, y, font, radius=20, alpha=190, colour=(248, 242, 232)):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_spaced(d, text, widths, spacing, x0, y, font, (*colour, alpha))
    return Image.alpha_composite(canvas, layer.filter(ImageFilter.GaussianBlur(radius=radius)))


def save(canvas, name):
    final = Image.new("RGB", canvas.size, (255, 255, 255))
    final.paste(canvas, mask=canvas.split()[3])
    out = BASE / name
    if out.suffix.lower() == ".png":
        final.save(out, "PNG", optimize=True)
    else:
        # subsampling=0 + quality=100 preserves saturated colours (blue monogram)
        final.save(out, "JPEG", quality=100, optimize=True, subsampling=0)
    print(f"  -> {out.name}")


CREAM = (250, 245, 238, 255)
SHADOW = (0, 0, 0, 170)


# ---------------------------------------------------------------
# V1: Logo centred upper, bold Didot 'COMING SOON' beneath
# ---------------------------------------------------------------
def v1():
    bg = prep_bg(BG_DIR / "06-wine-pour-glass.jpeg", desat=0.42, veil_strength=0.34)
    _, ly, _, lh = place_logo(bg, width_pct=0.58, cx_pct=0.50, cy_pct=0.40)

    text = "COMING SOON"
    font = load(FONT_DIDOT, int(SIZE * 0.078), index=1)  # Didot Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.26)
    widths, total, th = measure(draw, text, font, spacing)
    while total > SIZE * 0.78:
        font = load(FONT_DIDOT, font.size - 2, index=1)
        spacing = int(font.size * 0.26)
        widths, total, th = measure(draw, text, font, spacing)
    x0 = (SIZE - total) // 2
    y = ly + lh + int(SIZE * 0.055)
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=18, alpha=180)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, CREAM, shadow=(3, SHADOW))
    save(bg, "mander-coming-soon-wineglass-01-didot-bold.jpg")


# ---------------------------------------------------------------
# V2: Optima Bold — clean, modern, tall letters over bottle+glass
# ---------------------------------------------------------------
def v2():
    bg = prep_bg(BG_DIR / "07-bottle-and-glass.jpeg", desat=0.44, veil_strength=0.30)
    _, ly, _, lh = place_logo(bg, width_pct=0.50, cx_pct=0.50, cy_pct=0.34)

    text = "COMING SOON"
    font = load(FONT_OPTIMA, int(SIZE * 0.085), index=1)  # Optima Bold
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.20)
    widths, total, th = measure(draw, text, font, spacing)
    while total > SIZE * 0.82:
        font = load(FONT_OPTIMA, font.size - 2, index=1)
        spacing = int(font.size * 0.20)
        widths, total, th = measure(draw, text, font, spacing)
    x0 = (SIZE - total) // 2
    y = ly + lh + int(SIZE * 0.07)
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=20, alpha=190)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, CREAM, shadow=(3, SHADOW))
    save(bg, "mander-coming-soon-wineglass-02-optima-bold.jpg")


# ---------------------------------------------------------------
# V3: Script "Coming" + block "SOON" over the dramatic pour
# ---------------------------------------------------------------
def v3():
    bg = prep_bg(BG_DIR / "08-dramatic-pour.jpeg", desat=0.42, veil_strength=0.34)
    place_logo(bg, width_pct=0.42, cx_pct=0.50, cy_pct=0.22)

    script_font = load(FONT_SNELL, int(SIZE * 0.22))
    script = "Coming"
    draw = ImageDraw.Draw(bg)
    sb = draw.textbbox((0, 0), script, font=script_font)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    sx = (SIZE - sw) // 2 - sb[0]
    sy = int(SIZE * 0.48) - sb[1]
    layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((sx, sy), script, font=script_font, fill=(250, 244, 232, 210))
    bg = Image.alpha_composite(bg, layer.filter(ImageFilter.GaussianBlur(radius=24)))
    draw = ImageDraw.Draw(bg)
    draw.text((sx + 3, sy + 3), script, font=script_font, fill=(0, 0, 0, 150))
    draw.text((sx, sy), script, font=script_font, fill=CREAM)

    block_font = load(FONT_DIDOT, int(SIZE * 0.085), index=1)
    block = "SOON"
    bb = draw.textbbox((0, 0), block, font=block_font)
    bw_, bh_ = bb[2] - bb[0], bb[3] - bb[1]
    bx = (SIZE - bw_) // 2 - bb[0]
    by = sy + sh + int(SIZE * 0.05)
    draw.text((bx + 3, by + 3), block, font=block_font, fill=(0, 0, 0, 170))
    draw.text((bx, by), block, font=block_font, fill=CREAM)
    save(bg, "mander-coming-soon-wineglass-03-script-block.jpg")


# ---------------------------------------------------------------
# V4: Didot Bold flanked by rule lines over two-glasses scene
# ---------------------------------------------------------------
def v4():
    bg = prep_bg(BG_DIR / "09-two-glasses.jpeg", desat=0.50, veil_strength=0.22)

    # Broad soft plate: a very wide, heavily-blurred white ellipse lifts
    # the LOCAL bg toward near-white so the logo's antialiased edges blend
    # with white (as they do in the PDF on its white page) — without any
    # visible halo or outline. The radius is deliberately large and the
    # blur heavy so there's no perceivable "plate shape" — just a subtle,
    # diffuse brightening across the upper region of the image.
    cx, cy = int(SIZE * 0.50), int(SIZE * 0.17)
    plate = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.ellipse([cx - 430, cy - 200, cx + 430, cy + 200], fill=(255, 255, 255, 225))
    plate = plate.filter(ImageFilter.GaussianBlur(radius=130))
    bg = Image.alpha_composite(bg, plate)
    wash = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    wd.ellipse([cx - 640, cy - 300, cx + 640, cy + 300], fill=(255, 254, 250, 110))
    wash = wash.filter(ImageFilter.GaussianBlur(radius=200))
    bg = Image.alpha_composite(bg, wash)

    # PDF-native logo (raw source — #1C4C8C core pixel identical to PDF)
    place_logo(bg, width_pct=0.60, cx_pct=0.50, cy_pct=0.17, glow=False)

    text = "COMING SOON"
    font = load(FONT_DIDOT, int(SIZE * 0.058), index=1)
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.32)
    widths, total, th = measure(draw, text, font, spacing)
    x0 = (SIZE - total) // 2
    # Nudged down from 0.58 to sit lower over the glass bowls, matching the earlier placement.
    y = int(SIZE * 0.62) - th // 2
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=16, alpha=170)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, CREAM, shadow=(2, SHADOW))

    line_y = y + th // 2 + 2
    gap = int(SIZE * 0.025)
    line_len = int(SIZE * 0.12)
    lc = (250, 245, 238, 230)
    draw.line([(x0 - gap - line_len, line_y), (x0 - gap, line_y)], fill=lc, width=2)
    draw.line([(x0 + total + gap, line_y), (x0 + total + gap + line_len, line_y)], fill=lc, width=2)
    save(bg, "mander-coming-soon-wineglass-04-ruled.png")


# ---------------------------------------------------------------
# V5: Large Didot Bold across the swirl scene, logo bottom-right
# ---------------------------------------------------------------
def v5():
    bg = prep_bg(BG_DIR / "10-wine-swirl.jpeg", desat=0.42, veil_strength=0.32)

    text = "COMING SOON"
    font = load(FONT_DIDOT, int(SIZE * 0.098), index=1)
    draw = ImageDraw.Draw(bg)
    spacing = int(font.size * 0.22)
    widths, total, th = measure(draw, text, font, spacing)
    while total > SIZE * 0.80:
        font = load(FONT_DIDOT, font.size - 2, index=1)
        spacing = int(font.size * 0.22)
        widths, total, th = measure(draw, text, font, spacing)
    x0 = (SIZE - total) // 2
    y = int(SIZE * 0.46) - th // 2
    bg = halo(bg, text, widths, spacing, x0, y, font, radius=26, alpha=210)
    draw = ImageDraw.Draw(bg)
    draw_spaced(draw, text, widths, spacing, x0, y, font, CREAM, shadow=(4, SHADOW))

    place_logo(bg, width_pct=0.30, cx_pct=0.80, cy_pct=0.86)
    save(bg, "mander-coming-soon-wineglass-05-large-didot.jpg")


if __name__ == "__main__":
    print("Generating 5 wine-glass variations...")
    v1(); v2(); v3(); v4(); v5()
    print("Done.")
