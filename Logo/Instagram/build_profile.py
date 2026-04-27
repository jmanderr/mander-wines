"""
Generate Mander Wines Instagram profile picture from the M monogram.

Why monogram (not full logo):
- IG profile is displayed at ~110×110 px in feed and ~40×40 px in comments
- The full wordmark "MANDER" becomes illegible at those sizes
- The monogram alone is recognisable at any scale — same convention as
  every premium fashion / wine brand on IG (Hermès H, Chanel CC, etc.)

Output:
- Mander-IG-profile.png  — 1080×1080 transparent (for IG upload)
- Mander-IG-profile-white.png — 1080×1080 white-bg
- Mander-IG-profile.jpg  — 1080×1080 white-bg JPG (IG accepts JPG)
- Mander-IG-profile-circle-preview.png — what it looks like cropped to circle
"""
from PIL import Image, ImageDraw, ImageChops
from pathlib import Path

LOGO_DIR = Path("/Users/jmander/Desktop/Claude/Mander Wines/Logo")
OUT_DIR = LOGO_DIR / "Instagram"
SRC = LOGO_DIR / "Mander-monogram.png"

SIZE = 1080  # IG max profile pic resolution

# Open monogram source (PDF-native pixels: #1C4C8C blue)
mono = Image.open(SRC).convert("RGBA")
mw, mh = mono.size

# Scale to fill ~58% of canvas height (leaves comfortable margin inside the
# circular crop, monogram height becomes the limiting dimension)
target_h = int(SIZE * 0.58)
scale = target_h / mh
target_w = int(mw * scale)

# Premultiplied resize keeps edges clean
def premult_resize(img, size):
    r, g, b, a = img.split()
    rp = ImageChops.multiply(r, a)
    gp = ImageChops.multiply(g, a)
    bp = ImageChops.multiply(b, a)
    pre = Image.merge("RGBA", (rp, gp, bp, a)).resize(size, Image.LANCZOS)
    rp2, gp2, bp2, a2 = pre.split()
    def unmul(ch, alpha):
        out = Image.new("L", ch.size, 0)
        cp = ch.load(); ap = alpha.load(); op = out.load()
        for y in range(ch.size[1]):
            for x in range(ch.size[0]):
                av = ap[x, y]
                if av > 0:
                    op[x, y] = min(255, int(cp[x, y] * 255 / av))
        return out
    return Image.merge("RGBA", (unmul(rp2, a2), unmul(gp2, a2), unmul(bp2, a2), a2))

mono_scaled = premult_resize(mono, (target_w, target_h))

# 1. TRANSPARENT 1080×1080
canvas_t = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
px = (SIZE - target_w) // 2
py = (SIZE - target_h) // 2
canvas_t.paste(mono_scaled, (px, py), mono_scaled)
canvas_t.save(OUT_DIR / "Mander-IG-profile.png", "PNG", optimize=True)

# 2. WHITE-BG 1080×1080 (PNG)
canvas_w = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
canvas_w.paste(mono_scaled, (px, py), mono_scaled)
canvas_w.save(OUT_DIR / "Mander-IG-profile-white.png", "PNG", optimize=True)

# 3. WHITE-BG JPG
canvas_w.save(OUT_DIR / "Mander-IG-profile.jpg", "JPEG", quality=100, subsampling=0, optimize=True)

# 4. CIRCLE PREVIEW — shows what it looks like on the IG profile
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).ellipse([0, 0, SIZE, SIZE], fill=255)
preview = Image.new("RGB", (SIZE, SIZE), (220, 220, 220))  # grey backdrop
preview.paste(canvas_w, (0, 0), mask)
# Add a subtle outline ring (1.5%-thick) like IG sometimes shows
ImageDraw.Draw(preview).ellipse([0, 0, SIZE - 1, SIZE - 1], outline=(180, 180, 180), width=4)
preview.save(OUT_DIR / "Mander-IG-profile-circle-preview.png", "PNG", optimize=True)

# Verify pixel colour
from collections import Counter
img = Image.open(OUT_DIR / "Mander-IG-profile.png").convert("RGBA")
w, h = img.size
px_data = img.load()
blues = []
for y in range(h):
    for x in range(w):
        r, g, b, a = px_data[x, y]
        if a < 250: continue
        if b > r + 30 and b > g + 30 and b > 100 and r < 60:
            blues.append((r, g, b))
core = Counter(blues).most_common(1)[0][0]
print(f"Profile pic: {SIZE}×{SIZE}")
print(f"Monogram size: {target_w}×{target_h} (centred, fills {100*target_h/SIZE:.0f}% of height)")
print(f"Core blue pixel: RGB{core} = #{core[0]:02X}{core[1]:02X}{core[2]:02X}  (target: #1C4C8C)")
print(f"\nFiles:")
for f in sorted(OUT_DIR.glob("Mander-IG-profile*")):
    print(f"  {f.name}  ({f.stat().st_size // 1024} KB)")
