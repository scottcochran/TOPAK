#!/usr/bin/env python3
"""Every heading a diagram links to is an anchor GitHub's rendered page has.

A link to a Markdown heading opens the rendered file at the heading's anchor, which topak/src/sources.py works out
from the heading's source as GitHub does. A wrong anchor fails silently: GitHub opens the top of the file. This reads
every such link from the committed SVGs, fetches each file's rendered page at its pinned commit from github.com, and
checks the linked anchors against the page's own, and the generator's list of the file's anchors against the page's
order. It needs the network and the repository to be readable without a login, so it is run by hand, after a pin
moves or the anchor rule changes, and is in no workflow. Standard library and curl only.
  python3 diagrams/check-heading-anchors.py
"""
import collections
import html
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent / "topak"
sys.path.insert(0, str(HERE / "src"))

import sources  # noqa: E402

LINK = re.compile(rf"{re.escape(sources.GITHUB)}/blob/([0-9a-f]{{40}})/([^?#]+\.md)#(?!L\d+$)(.+)")


def main():
    want = collections.defaultdict(set)
    for f in sorted(HERE.glob("*.svg")):
        for h in re.findall(r' href="([^"]*)"', f.read_text(encoding="utf-8")):
            m = LINK.fullmatch(html.unescape(h))
            if m:
                want[(m.group(1), m.group(2))].add(urllib.parse.unquote(m.group(3)))
    bad = links = 0
    for (commit, rel), frags in sorted(want.items()):
        url = f"{sources.GITHUB}/blob/{commit}/{rel}"
        for attempt in range(4):
            r = subprocess.run(["curl", "-fsSL", url], capture_output=True)
            if r.returncode == 0:
                break
            time.sleep(5 * (attempt + 1))
        else:
            print(f"ERROR {rel} at {commit[:7]}: not fetched")
            bad += 1
            continue
        # the page carries the rendered file as a JSON string: id=\"user-content-<anchor>\"
        live = re.findall(r'id=\\"user-content-([^\\"]*)\\"', r.stdout.decode("utf-8", "replace"))
        mine = list(sources.at(commit).heading_anchors(rel).values())
        links += len(frags)
        missing = sorted(frags - set(live))
        if not live:
            print(f"ERROR {rel} at {commit[:7]}: the page shows no anchors (is the repository readable?)")
            bad += 1
        elif missing:
            print(f"ERROR {rel} at {commit[:7]}: linked, and not an anchor of the page: {missing}")
            bad += 1
        elif mine != [a for a in live if a in set(mine)]:
            print(f"ERROR {rel} at {commit[:7]}: the generator's anchors are not the page's, in order")
            bad += 1
        time.sleep(0.4)
    print(f"check-heading-anchors: {len(want)} files, {links} headings linked, {bad} files failing")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
