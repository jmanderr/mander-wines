from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

BASE = Path("/Users/jmander/Desktop/Claude/Mander Wines/instagram-posts/coming-soon-launch")
BG = BASE / "backgrounds" / "01-barrel-head-on.jpeg"
LOGO_PATH = Path("/Users/jmander/Desktop/Claude/Mander Wines/images/logo-adj.png")
OUT = BASE / "mander-coming-soon-01-barrel-head-on.jpg"

SIZE = 1080

BOLD_SERIF_CANDIDATES = [
    ("/System/Library/Fonts/Supplemental/Didot.ttc", 1),   # Didot Bold
    ("/System/Library/Fonts/Supplemental/Didot.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Baskerville.ttc", 2),
    ("/System/Library/Fonts/Supplemental/Baskerville.ttc", 0),
    ("/System/Library/Fonts/Times.ttc", 1),
]

def load_bold(size):
    for path, idx in BOLD_SERIF_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size, index=idx)
            except Exception:
                continue
    return ImageFont.load_default()

def muted_overlay(img, strength=0.30):
    overlay = Image.new("RGBA", img.size, (235, 235, 235, int(255 * strength)))
    return Image.alpha_composite(img.convert("RGBA"), overlay)

# --- background ---
bg = Image.open(BG).convert("RGBA")
w, h = bg.size
side = min(w, h)
bg = bg.crop(((w - side) // 2, (h - side) // 2, (w - side) // 2 + side, (h - side) // 2 + side))
bg = bg.resize((SIZE, SIZE), Image.LANCZOS)
bg = muted_overlay(bg, strength=0.28)

# --- logo ---
# The "MANDER" wordmark sits around y-ratio ~0.58 of the logo PNG (below geometric centre
# because the monogram is taller on top). Offset so the wordmark lands on the barrel centre.
logo = Image.open(LOGO_PATH).convert("RGBA")
target_w = int(SIZE * 0.66)
ratio = target_w / logo.width
target_h = int(logo.height * ratio)
logo = logo.resize((target_w, target_h), Image.LANCZOS)

# Barrel visual centre (from Gemini analysis): x=0.505, y=0.499
BARREL_CX = int(SIZE * 0.505)
BARREL_CY = int(SIZE * 0.499)
BARREL_BOTTOM_Y = int(SIZE * 0.884)

# Position so the MANDER wordmark (~0.58 down the logo) sits on barrel centre
WORDMARK_RATIO = 0.58
logo_x = BARREL_CX - target_w // 2
logo_y = BARREL_CY - int(target_h * WORDMARK_RATIO)
bg.paste(logo, (logo_x, logo_y), logo)

# --- COMING SOON — bolder, with soft light halo, positioned near bottom of barrel ---
text = "COMING SOON"
# Fit the text within the barrel's visible face (~66% of canvas width).
# Iterate font size until the total width fits the target.
MAX_TEXT_W = int(SIZE * 0.62)
font_size = int(SIZE * 0.082)
while font_size > 30:
    font = load_bold(font_size)
    spacing_px = int(font_size * 0.30)
    probe = ImageDraw.Draw(bg)
    widths = [probe.textbbox((0, 0), ch, font=font)[2] - probe.textbbox((0, 0), ch, font=font)[0] for ch in text]
    total = sum(widths) + spacing_px * (len(text) - 1)
    if total <= MAX_TEXT_W:
        break
    font_size -= 2

draw = ImageDraw.Draw(bg)
char_widths = [draw.textbbox((0, 0), ch, font=font)[2] - draw.textbbox((0, 0), ch, font=font)[0] for ch in text]
text_w = sum(char_widths) + spacing_px * (len(text) - 1)
ascent, descent = font.getmetrics()
text_h = ascent + descent

# Baseline sits just above the bottom of the barrel face
text_y = BARREL_BOTTOM_Y - text_h - int(SIZE * 0.015)
cursor_x = BARREL_CX - text_w // 2

# Soft light halo behind the text so it pops off the wood grain without a hard box
halo_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
halo_draw = ImageDraw.Draw(halo_layer)
hx = cursor_x
for ch, cw in zip(text, char_widths):
    halo_draw.text((hx, text_y), ch, font=font, fill=(245, 240, 230, 170))
    hx += cw + spacing_px
halo_layer = halo_layer.filter(ImageFilter.GaussianBlur(radius=14))
bg = Image.alpha_composite(bg, halo_layer)

# Main text — deep charcoal with a tight dark shadow for crispness
draw = ImageDraw.Draw(bg)
cursor_x = BARREL_CX - text_w // 2
for ch, cw in zip(text, char_widths):
    draw.text((cursor_x + 3, text_y + 3), ch, font=font, fill=(0, 0, 0, 150))
    draw.text((cursor_x, text_y), ch, font=font, fill=(38, 30, 26, 255))
    cursor_x += cw + spacing_px

final = Image.new("RGB", bg.size, (255, 255, 255))
final.paste(bg, mask=bg.split()[3])
final.save(OUT, "JPEG", quality=95, optimize=True)
print(f"Saved: {OUT}")
