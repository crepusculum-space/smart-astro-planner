#!/usr/bin/env python3
"""Generates icon-192.png and icon-512.png from geometric primitives only
(a ring, four crosshair bars, a disc and a few seeded random star dots).
No external artwork is used. Run from the project root: python3 tools/make_icons.py
"""
import math, random
from PIL import Image, ImageDraw

BG, RING, WHITE = (10, 10, 26, 255), (74, 158, 255, 255), (255, 255, 255, 255)
SS = 4  # supersampling factor


def render(size):
    n = size * SS
    k = n / 512.0
    img = Image.new("RGBA", (n, n), BG)
    d = ImageDraw.Draw(img)
    c = n / 2

    rnd = random.Random(7)
    placed = 0
    while placed < 16:
        x, y = rnd.uniform(18, 494), rnd.uniform(18, 494)
        if math.hypot(x - 256, y - 256) < 212:
            continue
        r = rnd.choice([1.6, 2.2, 3.0]) * k
        shade = rnd.choice([150, 190, 230])
        d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], fill=(shade, shade, 255, 255))
        placed += 1

    R, W = 190 * k, 18 * k
    d.ellipse([c - R, c - R, c + R, c + R], outline=RING, width=int(W))

    bar = 12 * k
    inner, outer = 58 * k, 112 * k
    d.rectangle([c - bar / 2, c - outer, c + bar / 2, c - inner], fill=WHITE)
    d.rectangle([c - bar / 2, c + inner, c + bar / 2, c + outer], fill=WHITE)
    d.rectangle([c - outer, c - bar / 2, c - inner, c + bar / 2], fill=WHITE)
    d.rectangle([c + inner, c - bar / 2, c + outer, c + bar / 2], fill=WHITE)

    r = 40 * k
    d.ellipse([c - r, c - r, c + r, c + r], fill=WHITE)
    return img.resize((size, size), Image.LANCZOS)


for s in (192, 512):
    render(s).save(f"icon-{s}.png")
    print("wrote", f"icon-{s}.png")
