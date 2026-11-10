#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Scaffold a new family diagram module from the template, or list the next free id in each group.

  uv run scripts/new_diagram.py --free                          # next free id per letter
  uv run scripts/new_diagram.py C12 user-consent "A user's consent is ..."
  uv run scripts/new_diagram.py C12 user-consent "..." --dry-run   # print the module, write nothing

The module is written to <family-dir>/src/d_<id>_<slug_with_underscores>.py and builds as it stands, with a
status strip, one band of cards and one table to replace. It refuses an id or a slug already in use.
"""
import argparse
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "diagram_template.py"


def repo_root():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return pathlib.Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return pathlib.Path.cwd()


def used_ids(src):
    ids = {}
    for p in src.glob("d_*.py"):
        m = re.match(r"d_([a-z])(\d+)_", p.name)
        if m:
            ids.setdefault(m.group(1).upper(), set()).add(int(m.group(2)))
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ident", nargs="?", help="diagram id, a capital letter and a number: C12")
    ap.add_argument("slug", nargs="?", help="kebab-case slug: user-consent")
    ap.add_argument("title", nargs="?", default="TITLE: one sentence, the claim the diagram draws")
    ap.add_argument("--family-dir", default="diagrams/topak")
    ap.add_argument("--free", action="store_true", help="list the next free id in each group and exit")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    src = repo_root() / a.family_dir / "src"
    if not src.is_dir():
        sys.exit(f"new_diagram: no {src}")
    ids = used_ids(src)
    if a.free:
        for letter in sorted(ids):
            print(f"{letter}{max(ids[letter]) + 1}   (in use: {', '.join(f'{letter}{n}' for n in sorted(ids[letter]))})")
        return
    if not a.ident or not a.slug:
        ap.error("give an id and a slug, or --free")
    ident = a.ident.upper()
    m = re.fullmatch(r"([A-Z])(\d+)", ident)
    if not m:
        ap.error(f"id must be a capital letter and a number: {a.ident}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        ap.error(f"slug must be kebab-case: {a.slug}")
    if int(m.group(2)) in ids.get(m.group(1), set()):
        sys.exit(f"new_diagram: {ident} is in use; --free lists the next free ids")
    mod = src / f"d_{ident.lower()}_{a.slug.replace('-', '_')}.py"
    if mod.exists():
        sys.exit(f"new_diagram: {mod} exists")

    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("__ID__", ident).replace("__SLUG__", a.slug).replace("__TITLE__", a.title.replace('"', '\\"'))
    if a.dry_run:
        print(text)
        return
    mod.write_text(text, encoding="utf-8")
    print(mod)
    print(f"next: uv run --no-project --python 3.9 python diagrams/gen-topak-family.py {ident}")
    print(f"then: uv run {HERE / 'render.py'} {ident}")


if __name__ == "__main__":
    main()
