#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Render one family diagram to PNG, in the light theme, the dark theme or both, whole or cropped, so it can be
looked at.

Light is rasterized by rsvg-convert, which reads the presentation attributes (the light theme). Dark needs a
browser, because the dark theme is CSS custom properties switched by `svg[data-theme=dark]`, which rsvg ignores:
the script inserts that attribute, wraps the SVG in an HTML page and screenshots it with headless Chrome.

A crop is made by rewriting the SVG's viewBox, not by cropping the PNG, so it is exact and works in both themes.
Crop by a text needle (the first <text> element whose text contains it, tags stripped), or by explicit
coordinates in SVG units.

  uv run scripts/render.py B9                       # both themes, whole, at 1300 px wide
  uv run scripts/render.py B9 --theme dark --needle "Plane b" --h 700 --width 1800
  uv run scripts/render.py diagrams/topak/H8-overlay-verification-2026.10.05.svg --y 2200 --h 900 --x 0 --w 1700

Writes PNGs to --out (default: a directory named after the diagram id under $TMPDIR) and prints their paths.
"""
import argparse
import html
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

DARK_BG = "#12151b"   # BASE["bg"] dark in diagrams/topak/src/lib.py
CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
]


def die(msg):
    print(f"render: {msg}", file=sys.stderr)
    sys.exit(2)


def repo_root():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return pathlib.Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return pathlib.Path.cwd()


def resolve(target, family_dir):
    p = pathlib.Path(target)
    if p.suffix == ".svg" and p.exists():
        return p
    if re.fullmatch(r"[A-Z]\d+", target):
        hits = sorted(family_dir.glob(f"{target}-*.svg"))
        if len(hits) == 1:
            return hits[0]
        die(f"id {target}: {len(hits)} files match {family_dir}/{target}-*.svg")
    die(f"not an SVG file or a diagram id: {target}")


def size(svg):
    m = re.search(r'<svg\b[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', svg)
    if not m:
        die("root <svg> has no width and height")
    return float(m.group(1)), float(m.group(2))


def find_needle(svg, needle):
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
        if needle in text:
            y = re.search(r'\by="([\d.]+)"', m.group(1))
            x = re.search(r'\bx="([\d.]+)"', m.group(1))
            return float(x.group(1)) if x else 0.0, float(y.group(1))
    die(f"needle not found in any <text>: {needle!r}")


def crop(svg, x, y, w, h):
    def fix(tag):
        tag = re.sub(r'\bwidth="[\d.]+"', f'width="{w:.0f}"', tag, count=1)
        tag = re.sub(r'\bheight="[\d.]+"', f'height="{h:.0f}"', tag, count=1)
        return re.sub(r'\bviewBox="[^"]*"', f'viewBox="{x:.0f} {y:.0f} {w:.0f} {h:.0f}"', tag, count=1)
    return re.sub(r"<svg\b[^>]*>", lambda m: fix(m.group(0)), svg, count=1)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if not c:
            continue
        if os.path.isabs(c) and os.path.exists(c):
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def light(svg_path, out_png, out_w):
    if not shutil.which("rsvg-convert"):
        die("rsvg-convert not found (macOS: brew install librsvg; Debian: apt install librsvg2-bin)")
    subprocess.run(["rsvg-convert", "-w", str(out_w), str(svg_path), "-o", str(out_png)], check=True)


def dark(svg_text, work, out_png, w, h, out_w):
    chrome = find_chrome()
    if not chrome:
        die("no Chrome or Chromium found; set CHROME=/path/to/chrome")
    svg_text = re.sub(r"<svg\b", '<svg data-theme="dark"', svg_text, count=1)
    (work / "dark.svg").write_text(svg_text, encoding="utf-8")
    (work / "dark.html").write_text(
        f'<html><body style="margin:0;background:{DARK_BG}">'
        f'<img src="dark.svg" width="{w:.0f}" height="{h:.0f}" style="display:block"></body></html>',
        encoding="utf-8")
    scale = out_w / w
    subprocess.run([chrome, "--headless=new", "--hide-scrollbars", f"--force-device-scale-factor={scale:.4f}",
                    f"--window-size={int(w)},{int(h)}", f"--screenshot={out_png}",
                    (work / "dark.html").resolve().as_uri()],
                   check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="a diagram id (B9) or a path to an SVG")
    ap.add_argument("--theme", choices=["light", "dark", "both"], default="both")
    ap.add_argument("--needle", help="crop around the first <text> containing this string")
    ap.add_argument("--above", type=float, default=120, help="with --needle: SVG units kept above the text")
    ap.add_argument("--x", type=float, help="crop left, SVG units (default 0)")
    ap.add_argument("--y", type=float, help="crop top, SVG units")
    ap.add_argument("--w", type=float, help="crop width, SVG units (default: whole width)")
    ap.add_argument("--h", type=float, help="crop height, SVG units (default 900 when cropping)")
    ap.add_argument("--width", type=int, default=1300, help="output PNG width in pixels (default 1300)")
    ap.add_argument("--family-dir", default="diagrams/topak", help="where diagram SVGs live, relative to the repo")
    ap.add_argument("--out", help="output directory")
    a = ap.parse_args()

    root = repo_root()
    path = resolve(a.target, root / a.family_dir)
    svg = path.read_text(encoding="utf-8")
    W, H = size(svg)
    ident = path.name.split("-", 1)[0]
    tag = "whole"
    if a.needle or a.y is not None:
        if a.needle:
            _, ny = find_needle(svg, a.needle)
            y = max(0.0, ny - a.above)
        else:
            y = a.y
        x = a.x or 0.0
        w = min(a.w or W, W - x)
        h = min(a.h or 900, H - y)
        svg = crop(svg, x, y, w, h)
        W, H = w, h
        tag = f"y{int(y)}"
    out = pathlib.Path(a.out) if a.out else pathlib.Path(tempfile.gettempdir()) / "diagram-render" / ident
    out.mkdir(parents=True, exist_ok=True)
    work = pathlib.Path(tempfile.mkdtemp(prefix=f"{ident}-", dir=out))
    src = work / "light.svg"
    src.write_text(svg, encoding="utf-8")
    width = min(a.width, int(W * 2))
    if a.theme in ("light", "both"):
        png = out / f"{ident}-{tag}-light.png"
        light(src, png, width)
        print(png)
    if a.theme in ("dark", "both"):
        png = out / f"{ident}-{tag}-dark.png"
        dark(svg, work, png, W, H, width)
        print(png)


if __name__ == "__main__":
    main()
