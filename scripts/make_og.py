#!/usr/bin/env python3
"""Generate 1200x630 OG images into assets/og/.

Style matches the site palette (style.css tokens): dark navy background,
teal primary, pink accent, IBM-style typography via system fonts.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1200, 630
BG_TOP = (11, 2, 16)
BG_MID = (10, 16, 32)
BG_BOT = (5, 1, 8)
PRIMARY = (104, 240, 211)
ACCENT = (255, 122, 143)
TEXT = (238, 243, 255)
MUTED = (167, 183, 219)

BOLD_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
MONO_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]


def load_font(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise SystemExit("No usable truetype font found")


def wrap(draw, text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def render(filename, kicker, title):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        if y < H // 2:
            t = y / (H / 2)
            c = tuple(int(BG_TOP[i] + (BG_MID[i] - BG_TOP[i]) * t) for i in range(3))
        else:
            t = (y - H / 2) / (H / 2)
            c = tuple(int(BG_MID[i] + (BG_BOT[i] - BG_MID[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c

    d = ImageDraw.Draw(img, "RGBA")

    # subtle grid
    for gx in range(0, W, 64):
        d.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 10), width=1)
    for gy in range(0, H, 64):
        d.line([(0, gy), (W, gy)], fill=(255, 255, 255, 10), width=1)

    # spectral trace curve
    points = []
    for x in range(0, W + 10, 10):
        import math
        y = H * 0.78 + math.sin(x / 90.0) * 26 + math.sin(x / 37.0) * 12
        points.append((x, y))
    d.line(points, fill=(255, 122, 143, 90), width=2)
    d.ellipse([W - 40, H * 0.78 - 34, W + 40, H * 0.78 + 46], fill=(255, 122, 143, 0))
    d.ellipse([W - 34, H * 0.78 - 6, W - 14, H * 0.78 + 14], fill=(255, 122, 143, 160))

    kicker_font = load_font(MONO_CANDIDATES, 30)
    title_font = load_font(BOLD_CANDIDATES, 72)
    footer_font = load_font(MONO_CANDIDATES, 26)

    d.text((80, 92), kicker.upper(), font=kicker_font, fill=PRIMARY)

    lines = wrap(d, title, title_font, W - 160)
    ty = 170
    for line in lines[:3]:
        d.text((80, ty), line, font=title_font, fill=TEXT)
        ty += 84

    d.rectangle([80, H - 120, 200, H - 114], fill=ACCENT)
    d.text((80, H - 92), "genefold.ai", font=footer_font, fill=MUTED)

    img.save(OUT / filename, "PNG")
    print(f"assets/og/{filename}")


JOBS = [
    ("genefold-default.png", "Genefold AI",
     "Spectral intelligence for embedding search and monitoring"),
    ("engineering-001.png", "Engineering / 001",
     "Designing ArrowSpace and graph wiring"),
    ("engineering-002.png", "Engineering / 002",
     "Genefold First Principles: Depletion of Uncertainty"),
    ("engineering-003.png", "Engineering / 003",
     "Genefold First Principles: From Entropy to Epiplexity"),
    ("engineering-004.png", "Engineering / 004",
     "Genefold First Principles: The Curriculum Engine"),
    ("engineering-005.png", "Engineering / 005",
     "Synthetic Data That Teaches: A Feedback Loop for Training Beyond Static Corpora"),
    ("docs-spectral-intelligence.png", "Genefold Docs",
     "Spectral intelligence for embeddings"),
    ("docs-spectral-vector-search.png", "Genefold Docs",
     "Spectral vector search"),
    ("docs-graph-laplacian-retrieval.png", "Genefold Docs",
     "Graph Laplacian retrieval"),
    ("docs-embedding-drift.png", "Genefold Docs",
     "Embedding drift detection"),
    ("docs-ood-vector-retrieval.png", "Genefold Docs",
     "Out-of-distribution vector retrieval"),
    ("docs-spectral-search-vs-hnsw.png", "Genefold Docs",
     "Spectral search vs HNSW"),
    ("docs-glossary.png", "Genefold Docs",
     "Spectral retrieval glossary"),
    ("research-arrowspace.png", "Genefold Research",
     "ArrowSpace: Spectral Search for Embeddings and Graph Analysis"),
    ("research-energy-dispersion.png", "Genefold Research",
     "From Embedding Geometry to Spectral Search"),
    ("products-arrowspace.png", "Genefold Products",
     "ArrowSpace: spectral retrieval in Python and Rust"),
]

if __name__ == "__main__":
    for name, kicker, title in JOBS:
        render(name, kicker, title)