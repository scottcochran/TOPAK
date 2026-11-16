#!/usr/bin/env python3
"""Lay out a new use case under derived/, with the kernel vendored so the run stays replayable.

    new_usecase.py <slug> [--shape commanded|autonomous] [--date yyyy.mm.dd]

Creates derived/<slug>-<date>/ for the configuration and derived/<slug>-simulation-<date>/ for the
simulation. The kernel and engine are copied, not referenced: a derived directory is frozen, and the
kernel in this skill will change. Refuses to touch a directory that exists.
"""
import argparse
import datetime
import os
import pathlib
import re
import shutil
import subprocess

SKILL = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--shape", choices=["commanded", "autonomous"], default="commanded")
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y.%m.%d"))
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.slug):
        raise SystemExit("a slug is lowercase words joined by hyphens")
    root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True, cwd=SKILL).stdout.strip())
    cfg = root / "derived" / f"{a.slug}-{a.date}"
    sim = root / "derived" / f"{a.slug}-simulation-{a.date}"
    for d in (cfg, sim):
        if d.exists():
            raise SystemExit(f"{d} exists, and a derived directory is not rewritten: pick another slug or date")
    for sub in ("1-bundles", "2-workflows", "3-planes", "4-mission", "5-deployment", "tools"):
        (cfg / sub).mkdir(parents=True)
    shutil.copy(SKILL / "assets/config-README.md", cfg / "README.md")
    if a.shape == "commanded":  # a small deployment that runs as it stands, to replace piece by piece
        shutil.copytree(SKILL / "assets/starter-commanded", cfg, dirs_exist_ok=True)
    (sim / "out").mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "target")
    shutil.copytree(SKILL / "scripts/topak_sim", sim / "topak_sim", ignore=ignore)
    shutil.copytree(SKILL / "scripts/engine", sim / "engine", ignore=ignore)
    mech = os.path.relpath(root / "mechanism/crates", sim / "engine")
    toml = (sim / "engine/Cargo.toml").read_text()
    (sim / "engine/Cargo.toml").write_text(re.sub(r'path = "[^"]*/mechanism/crates/', f'path = "{mech}/', toml))
    shutil.copy(SKILL / f"assets/world_{a.shape}.py", sim / "world.py")
    shutil.copy(SKILL / f"assets/scenario_{a.shape}.json", sim / "scenario.json")
    shutil.copy(SKILL / "assets/simulation-README.md", sim / "README.md")
    s = (sim / "scenario.json").read_text().replace("@NAME@", a.slug).replace("@CONFIG@", f"../{cfg.name}")
    (sim / "scenario.json").write_text(s)
    print(f"configuration: {cfg.relative_to(root)}\nsimulation:    {sim.relative_to(root)}")


if __name__ == "__main__":
    main()
