#!/usr/bin/env python3
"""Render public/og.png, the 1200x630 card used for link previews.

Committed output, regenerated on demand:

    py tools/make_og_image.py

Uses the site's own palette (docs/RULEBOOK-adjacent design tokens in
src/layouts/Base.astro) and the same typeface the site serves, so the card
looks like the page it links to. The TTF is fetched to a temp directory
rather than committed: the site itself ships woff2, which Pillow cannot read,
and a 1 MB font has no business in the repository just to redraw one image.

Requires Pillow.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import urllib.request

from PIL import Image, ImageDraw, ImageFont

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / 'public' / 'og.png'

FONT_URL = ('https://raw.githubusercontent.com/googlefonts/literata/main/'
            'fonts/variable/Literata%5Bopsz,wght%5D.ttf')

W, H = 1200, 630
PAPER, SURFACE = '#f7f4ed', '#fffdf8'
INK, INK_SOFT, INK_FAINT = '#17252b', '#4f5f66', '#5e6c72'
RULE, BRAND, ON_BRAND = '#ddd9cd', '#173f4f', '#fffdf8'

SPECIMEN = ['Č', 'Š', 'Ž', 'Ł', 'Ď', 'Ť', 'Ź', 'Ś', 'Ć', 'Ń', 'Ŕ', 'Ï', 'Ḯ']


def font(path: pathlib.Path, size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(path), size)
    try:
        f.set_variation_by_axes([12, weight])   # optical size, weight
    except Exception:
        pass
    return f


def fetch_font() -> pathlib.Path:
    cached = pathlib.Path(tempfile.gettempdir()) / 'literata-var.ttf'
    if not cached.exists() or cached.stat().st_size < 100_000:
        req = urllib.request.Request(FONT_URL, headers={'User-Agent': 'Mozilla/5.0'})
        cached.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return cached


def main() -> int:
    ttf = fetch_font()
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)

    pad = 76

    # brand mark, matching the site header
    d.rounded_rectangle([pad, pad, pad + 68, pad + 68], radius=15, fill=BRAND)
    mark = font(ttf, 44, 600)
    mb = d.textbbox((0, 0), 'E', font=mark)
    d.text((pad + 34 - (mb[2] - mb[0]) / 2 - mb[0],
            pad + 34 - (mb[3] - mb[1]) / 2 - mb[1]), 'E', font=mark, fill=ON_BRAND)

    # eyebrow: both scripts, so the card says "bilingual" at a glance
    eyebrow = font(ttf, 25, 500)
    d.text((pad + 92, pad + 20), 'UKRAÏNŚKA ŁATYNKA  ·  УКРАЇНСЬКА ЛАТИНКА',
           font=eyebrow, fill=INK_FAINT)

    # wordmark
    word = font(ttf, 132, 600)
    d.text((pad, pad + 108), 'Evropéïća', font=word, fill=INK)

    # one line of the actual proposition, in both scripts
    lat = font(ttf, 36, 400)
    cyr = font(ttf, 32, 400)
    d.text((pad, pad + 286), 'Ukraïnśka mova łatynśkymy literamy', font=lat, fill=INK_SOFT)
    d.text((pad, pad + 336), 'Українська мова латинськими літерами', font=cyr, fill=INK_FAINT)

    # specimen strip: the letters this orthography adds
    chip = font(ttf, 40, 500)
    x, y, size = pad, H - pad - 76, 66
    for ch in SPECIMEN:
        d.rounded_rectangle([x, y, x + size, y + size], radius=11,
                            fill=SURFACE, outline=RULE, width=2)
        b = d.textbbox((0, 0), ch, font=chip)
        d.text((x + size / 2 - (b[2] - b[0]) / 2 - b[0],
                y + size / 2 - (b[3] - b[1]) / 2 - b[1]), ch, font=chip, fill=INK)
        x += size + 12

    # url sits on the header row: the specimen strip fills the full width below
    url = font(ttf, 27, 500)
    ub = d.textbbox((0, 0), 'evropeica.github.io', font=url)
    d.text((W - pad - (ub[2] - ub[0]), pad + 22), 'evropeica.github.io',
           font=url, fill=INK_FAINT)

    # brand rule along the bottom
    d.rectangle([0, H - 10, W, H], fill=BRAND)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, 'PNG', optimize=True)
    print(f'wrote {OUT.relative_to(REPO).as_posix()}  {W}x{H}  {OUT.stat().st_size / 1024:.0f} KB')
    return 0


if __name__ == '__main__':
    sys.exit(main())
