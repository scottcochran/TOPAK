#!/usr/bin/env python3
"""Generate the TOPAK diagram family (SVG, adaptive light/dark).

Each diagram is a module diagrams/topak/src/d_<id>_<slug>.py exposing ID, SLUG and build() -> Canvas.
Output: diagrams/topak/<ID>-<slug>-<DATE>.svg. Run with no arguments for all, or with ids (e.g. A1 D3).
No dependencies beyond the standard library.
"""
import importlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent / "topak"
sys.path.insert(0, str(HERE / "src"))

from lib import DATE  # noqa: E402


def main(argv):
    want = {a.upper() for a in argv}
    mods = sorted(p.stem for p in (HERE / "src").glob("d_*.py"))
    failed = 0
    for name in mods:
        if want and name.split("_")[1].upper() not in want:
            continue
        try:
            m = importlib.import_module(name)
        except Exception as e:  # report and carry on, so one broken module cannot block the rest
            print(f"ERROR {name}: {e!r}")
            failed += 1
            continue
        out = HERE / f"{m.ID}-{m.SLUG}-{DATE}.svg"
        canvas = m.build()
        out.write_text(canvas.svg(), encoding="utf-8")
        print(out.relative_to(HERE.parent.parent))
        for w in canvas.warnings:
            print("  WARNING", w)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
