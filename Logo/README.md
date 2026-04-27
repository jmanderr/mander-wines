# Mander Wines — Logo Brand Assets

Canonical logo export files, generated from the authoritative source
`/Users/jmander/Downloads/Mander logo_adj.pdf` (via `images/logo-adj.png`).

## Colours (match the PDF as rendered by macOS Preview)

| Element | Hex | RGB |
|---|---|---|
| M monogram (royal blue) | `#294B88` | `(41, 75, 136)` |
| Wordmark + rules (warm dark) | `#423C39` | `(66, 60, 57)` |

These are the **PDF-native values**, sampled directly from the authoritative
`Mander logo_adj.pdf` via macOS `sips` (same colour engine Preview uses). What
you see here is exactly what you'd see if you opened the PDF in Preview.

> **Note on muted / cream backgrounds:** if compositing onto a muted editorial
> background and the blue reads washed-out due to simultaneous contrast,
> apply a broad soft white wash + override the monogram to `#1A3068` *at
> composite time only* — see `memory/reference_mander_logo.md`. Don't modify
> the brand asset files themselves.

## Files

Each logo exists in **two variants**:

1. **`Mander-logo-full.*`** — full lockup (M monogram above, MANDER wordmark, flanking rules, bottom rule). 822×341 px at 1×.
2. **`Mander-monogram.*`** — just the M monogram. 122×170 px at 1×.

### Format catalogue

| Extension | Background | Use case |
|---|---|---|
| `.png` | Transparent | Web overlays, compositing on photos, any layout |
| `-white-bg.png` | White | When transparent would blend into a coloured layout |
| `.jpg` | White | Legacy systems / email that require JPG |
| `.pdf` | White | Print, invoices, decks, letterheads |
| `.svg` | Transparent (embedded PNG) | Web — scales without loss at target size |
| `.webp` | Transparent | Modern web — smaller file than PNG |
| `.tiff` | Transparent | High-end print workflows |
| `@4x.png` / `@4x.jpg` | Transparent / White | Print-ready hi-res (4× the base size) |

## How to use in future designs

**Always composite from these files** — do NOT ask an AI image tool to
"draw the Mander logo". Use the PNG for transparent overlays, the SVG for
the web, the PDF for print. The M-monogram files are for tight spaces where
the full wordmark won't fit (favicons, social media profile pictures, wax
seals, cork stamps, bottle capsules, etc.).

## Regenerate

If source artwork changes, update `images/logo-adj.png` (from the PDF via
macOS Preview / `sips`, NOT poppler — poppler gives a brighter blue) and
re-run `export_logo.py`.
