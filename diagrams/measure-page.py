#!/usr/bin/env python3
"""Measure the mean luminance of a diagram's content, page background excluded, and say what grey matches it.

This is how the light theme's page background (the `page` token in diagrams/topak/src/lib.py) was chosen;
diagrams/PAGE.md records the process and the result. Taken from gov-tla's diagrams/measure-page.py (the same
author, at gov-tla commit 25b82ae), itself riemann-diagrams' tools/measure-page.py (Apache-2.0, at commit 37fecad)
extended to pool several diagrams; unchanged here but for these paths. Each is rendered twice at the same width,
once as it is and once with its page rectangle painted a sentinel colour; the sentinel render is the mask. Over the
pixels that are not page, the script averages the relative luminance (sRGB linearised, Rec. 709 weights) and
converts the mean back to an sRGB grey, and also reports the plain mean of the sRGB values for comparison.

Needs rsvg-convert on the path and Pillow in the interpreter:

    uv run --no-project --with pillow python diagrams/measure-page.py diagrams/topak/*.svg [--width 1700]

With several diagrams it prints each, then their content pooled: the mean over every content pixel of all of them,
which is how this family's page was chosen (riemann-diagrams measured one poster).
"""
import argparse
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image

SENTINEL = "#ff00ff"


def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb(y):
    return 255 * (12.92 * y if y <= 0.0031308 else 1.055 * y ** (1 / 2.4) - 0.055)


def render(svg_text, width, out):
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False, encoding="utf-8") as f:
        f.write(svg_text)
    subprocess.run(["rsvg-convert", "-w", str(width), f.name, "-o", str(out)], check=True)
    pathlib.Path(f.name).unlink()


def grey_line(y):
    grey = srgb(y)
    return (f"content mean relative luminance Y = {y:.4f} -> sRGB {grey:.1f} = {100 * grey / 255:.1f}% white = "
            f"#{round(grey):02x}{round(grey):02x}{round(grey):02x}")


def measure(path, width):
    """(content pixels, sum of their relative luminance, sum of their mean sRGB value), printing the diagram's line."""
    s = path.read_text(encoding="utf-8")
    m = re.search(r'<rect width="(\d+)" height="(\d+)" fill="#[0-9a-f]{6}" class="f-(?:bg|page)"/>', s)
    if not m:
        sys.exit(f"measure-page: {path.name}: no full-page background rect found in the SVG head")
    masked = s[:m.start()] + f'<rect width="{m.group(1)}" height="{m.group(2)}" fill="{SENTINEL}"/>' + s[m.end():]
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        render(s, width, d / "as-is.png")
        render(masked, width, d / "mask.png")
        w = Image.open(d / "as-is.png").convert("RGB")
        k = Image.open(d / "mask.png").convert("RGB")
    wp, kp = w.load(), k.load()
    W, H = w.size
    lut = [lin(i) for i in range(256)]
    sent = tuple(int(SENTINEL[i:i + 2], 16) for i in (1, 3, 5))
    n = nbg = 0
    ysum = vsum = 0.0
    for yy in range(H):
        for xx in range(W):
            if kp[xx, yy] == sent:
                nbg += 1
                continue
            r, g, b = wp[xx, yy]
            ysum += 0.2126 * lut[r] + 0.7152 * lut[g] + 0.0722 * lut[b]
            vsum += (r + g + b) / 3
            n += 1
    if not n:
        sys.exit(f"measure-page: {path.name}: no content pixels")
    print(f"{path.name}: {W}x{H} px, page background {100 * nbg / (W * H):.1f}%, content {100 * n / (W * H):.1f}%")
    print("  " + grey_line(ysum / n))
    print(f"  content mean sRGB value = {vsum / n:.1f} = {100 * vsum / n / 255:.1f}% white")
    return n, ysum, vsum


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("svg", type=pathlib.Path, nargs="+",
                    help="one diagram, or several: then also their content pooled, each pixel counted once")
    ap.add_argument("--width", type=int, default=1700, help="render width in pixels (default 1700)")
    a = ap.parse_args()
    totals = [measure(p, a.width) for p in a.svg]
    if len(totals) > 1:
        n = sum(t[0] for t in totals)
        print(f"pooled over {len(totals)} diagrams, {n} content px:")
        print("  " + grey_line(sum(t[1] for t in totals) / n))
        print(f"  content mean sRGB value = {sum(t[2] for t in totals) / n:.1f} = "
              f"{100 * sum(t[2] for t in totals) / n / 255:.1f}% white")


if __name__ == "__main__":
    main()
