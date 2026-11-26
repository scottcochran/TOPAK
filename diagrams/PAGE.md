# The page behind the cards

In the light theme, the page of every TOPAK family diagram is `#eaeaea` (91.7% white), not white. This document
says why, how the number was measured, and how to measure it again. The method is gov-tla's (its `diagrams/PAGE.md`
at commit 25b82ae, which chose `#ececec` for its seven diagrams), and gov-tla's is riemann-diagrams' (which chose
`#eeeeee` for its posters). The measurement here was made on 2026.11.26 with [`measure-page.py`](measure-page.py),
gov-tla's script with only its paths changed. If the diagrams change enough to move the measurement, the `page`
token in [`topak/src/lib.py`](topak/src/lib.py) and this document change together.

## Why not white

A diagram is cards on a page. On a white page, a card's white interior and the page are the same colour, and only
the card's border shows where it ends. The rule riemann-diagrams adopted, and gov-tla and this family follow, is
that the page should match the average luminance of what sits on it. Then the page is neither lighter nor darker
than the diagram as a whole, and the cards stand off it by their borders and tints at the smallest contrast that
still separates them.

## The measurement

For each diagram, `measure-page.py` does four things:

1. It renders the diagram as it is, in the light theme, 1700 pixels wide.
2. It renders the diagram again with its full-page rectangle painted magenta. A magenta pixel in that render is
   page; every other pixel is content.
3. Over the content pixels of the first render, it averages relative luminance (sRGB linearised, Rec. 709
   weights) and converts the mean back to an sRGB grey.
4. For comparison, it also reports the plain mean of the sRGB values.

The choice was made on the diagrams as they were on `main` at ffd02f1, on white, where the content of all 58
diagrams pooled to a relative luminance of 0.8206, sRGB 233.7, 91.7% white: **`#eaeaea`**. gov-tla's `#ececec` is
a little lighter; this family has more tinted panels and tables per diagram. As measured on the committed diagrams,
on their new page, with the figure on white beside it:

| Diagram | Pixels | Page | Content luminance | As a grey | On white |
|---|---|---|---|---|---|
| A1 | 1700 × 1510 | 30.2% | 0.839 | 92.6%, `#ececec` | 92.7% |
| A2 | 1700 × 1436 | 48.0% | 0.783 | 89.8%, `#e5e5e5` | 90.0% |
| A3 | 1700 × 1919 | 39.5% | 0.800 | 90.7%, `#e7e7e7` | 90.9% |
| A4 | 1700 × 1228 | 38.3% | 0.821 | 91.7%, `#eaeaea` | 91.9% |
| A5 | 1700 × 2445 | 49.0% | 0.759 | 88.6%, `#e2e2e2` | 88.9% |
| A6 | 1700 × 5482 | 33.7% | 0.813 | 91.3%, `#e9e9e9` | 91.5% |
| B1 | 1700 × 2120 | 54.9% | 0.780 | 89.6%, `#e5e5e5` | 89.9% |
| B10 | 1700 × 2348 | 46.9% | 0.805 | 90.9%, `#e8e8e8` | 91.2% |
| B11 | 1700 × 6153 | 25.9% | 0.836 | 92.5%, `#ececec` | 92.6% |
| B2 | 1700 × 1699 | 25.0% | 0.838 | 92.5%, `#ececec` | 92.7% |
| B3 | 1700 × 2824 | 41.5% | 0.811 | 91.2%, `#e9e9e9` | 91.4% |
| B4 | 1700 × 2142 | 38.0% | 0.801 | 90.7%, `#e7e7e7` | 90.9% |
| B5 | 1700 × 1412 | 47.0% | 0.778 | 89.6%, `#e4e4e4` | 89.8% |
| B6 | 1700 × 1560 | 42.8% | 0.783 | 89.8%, `#e5e5e5` | 90.0% |
| B7 | 1700 × 1972 | 36.7% | 0.781 | 89.7%, `#e5e5e5` | 90.0% |
| B8 | 1700 × 2565 | 33.8% | 0.836 | 92.4%, `#ececec` | 92.6% |
| B9 | 1700 × 3369 | 46.5% | 0.791 | 90.2%, `#e6e6e6` | 90.4% |
| C1 | 1700 × 1725 | 40.4% | 0.796 | 90.4%, `#e7e7e7` | 90.7% |
| C10 | 1700 × 2608 | 57.9% | 0.776 | 89.5%, `#e4e4e4` | 89.7% |
| C11 | 1700 × 2520 | 47.4% | 0.814 | 91.4%, `#e9e9e9` | 91.6% |
| C2 | 1700 × 2318 | 28.0% | 0.856 | 93.4%, `#eeeeee` | 93.6% |
| C3 | 1700 × 1510 | 38.5% | 0.823 | 91.8%, `#eaeaea` | 92.0% |
| C4 | 1700 × 3092 | 30.9% | 0.836 | 92.5%, `#ececec` | 92.6% |
| C5 | 1700 × 2320 | 52.6% | 0.794 | 90.3%, `#e6e6e6` | 90.6% |
| C6 | 1700 × 2537 | 37.0% | 0.808 | 91.0%, `#e8e8e8` | 91.3% |
| C7 | 1700 × 2086 | 35.2% | 0.804 | 90.8%, `#e8e8e8` | 91.1% |
| C8 | 1700 × 2598 | 38.4% | 0.819 | 91.6%, `#eaeaea` | 91.8% |
| C9 | 1700 × 3694 | 42.7% | 0.800 | 90.6%, `#e7e7e7` | 90.9% |
| D1 | 1700 × 2323 | 44.2% | 0.820 | 91.6%, `#eaeaea` | 91.9% |
| D2 | 1700 × 2747 | 41.2% | 0.818 | 91.6%, `#e9e9e9` | 91.7% |
| D3 | 1700 × 1768 | 44.8% | 0.821 | 91.7%, `#eaeaea` | 91.9% |
| D4 | 1700 × 1950 | 48.4% | 0.800 | 90.6%, `#e7e7e7` | 91.0% |
| D5 | 1700 × 2615 | 43.7% | 0.786 | 90.0%, `#e5e5e5` | 90.2% |
| D6 | 1700 × 4061 | 41.1% | 0.822 | 91.8%, `#eaeaea` | 92.0% |
| D7 | 1700 × 3411 | 41.0% | 0.805 | 90.9%, `#e8e8e8` | 91.2% |
| D8 | 1700 × 2795 | 50.0% | 0.786 | 89.9%, `#e5e5e5` | 90.2% |
| D9 | 1700 × 7093 | 32.6% | 0.812 | 91.3%, `#e9e9e9` | 91.4% |
| E1 | 1700 × 1735 | 48.7% | 0.762 | 88.7%, `#e2e2e2` | 89.0% |
| E2 | 1700 × 2487 | 39.8% | 0.771 | 89.2%, `#e3e3e3` | 89.7% |
| E3 | 1700 × 2836 | 42.7% | 0.800 | 90.7%, `#e7e7e7` | 90.9% |
| E4 | 1700 × 4550 | 26.5% | 0.828 | 92.1%, `#ebebeb` | 92.2% |
| E5 | 1700 × 3587 | 43.2% | 0.793 | 90.3%, `#e6e6e6` | 90.5% |
| F1 | 1700 × 2218 | 38.2% | 0.793 | 90.3%, `#e6e6e6` | 90.5% |
| G1 | 1700 × 3305 | 19.9% | 0.808 | 91.1%, `#e8e8e8` | 91.2% |
| G2 | 1700 × 2250 | 58.2% | 0.771 | 89.2%, `#e3e3e3` | 89.5% |
| G3 | 1700 × 6401 | 29.6% | 0.845 | 92.9%, `#ededed` | 93.1% |
| G4 | 1700 × 3723 | 44.4% | 0.789 | 90.1%, `#e6e6e6` | 90.3% |
| H1 | 1700 × 2577 | 33.8% | 0.828 | 92.1%, `#ebebeb` | 92.3% |
| H10 | 1700 × 7449 | 29.3% | 0.844 | 92.8%, `#ededed` | 92.9% |
| H11 | 1700 × 2356 | 33.3% | 0.792 | 90.2%, `#e6e6e6` | 90.4% |
| H2 | 1700 × 2515 | 60.8% | 0.784 | 89.8%, `#e5e5e5` | 90.2% |
| H3 | 1700 × 5475 | 18.0% | 0.874 | 94.2%, `#f0f0f0` | 94.4% |
| H4 | 1700 × 3228 | 33.2% | 0.838 | 92.5%, `#ececec` | 92.7% |
| H5 | 1700 × 1759 | 40.3% | 0.800 | 90.7%, `#e7e7e7` | 90.9% |
| H6 | 1700 × 3576 | 27.9% | 0.833 | 92.3%, `#ebebeb` | 92.4% |
| H7 | 1700 × 2944 | 28.8% | 0.793 | 90.3%, `#e6e6e6` | 90.5% |
| H8 | 1700 × 5075 | 38.4% | 0.827 | 92.0%, `#ebebeb` | 92.2% |
| H9 | 1700 × 4556 | 37.5% | 0.841 | 92.7%, `#ececec` | 92.9% |
| **All 58, pooled** | 183,112,638 content px | | **0.817** | **91.5%, `#e9e9e9`** | **91.7%, `#eaeaea`** |

Against the grey page, the anti-aliased edges of cards count a little darker, which moves each figure by a few
tenths of a percent (the pooled figure from `#eaeaea` to `#e9e9e9`) and the choice not at all, as gov-tla found.

## One number for every diagram

The diagrams share one library and one palette. A page that changed shade from one diagram to the next would make
the family look like 58 designs. The diagrams measure from 88.6% (A5) to 94.2% (H3) on the new page. Following
riemann-diagrams and gov-tla, a diagram that measures more than a few percent away from the page is a reason to
look at that diagram, not to change the page.

## What changed in the generator

The canvas rectangle used the `bg` token, which card interiors, label tabs, arrow-label chips and table rows also
use. It now has a token of its own, `page`:

| Token | Light | Dark |
|---|---|---|
| `bg` | `#ffffff` | `#12151b` |
| `page` | `#eaeaea` | `#12151b` |

The dark theme is unchanged: its page and its cards were already different shades (`#12151b` against the panels'
`#1a1e26`). In each SVG, only the first rectangle, the style's variable lists and one new `.f-page` rule changed,
the same five lines in all 58. No diagram's content or footer moved.

All 58 were regenerated. Two of them, B11 and H9, read corpus files at build time (the CI workflows, and
`spec/specification-graph.json` with its results file) that had changed on `main` since they were drawn on
2026.11.17. Regenerated from the working tree, they would have redrawn their content, with dated statements that no
longer held. They now read those files with git at `PIN_G12` in `topak/src/lib.py`, the commit they were drawn at
(the merge of PR #86), and regenerate as drawn. Moving that pin is an amendment of the two diagrams.

## Measuring again

```bash
uv run --no-project --python 3.9 --with pillow python diagrams/measure-page.py diagrams/topak/*.svg
```

It prints each diagram, then the pooled figure; it takes about a minute and a half for the family. Given one
diagram, it prints that diagram alone.

The script needs `rsvg-convert` on the path. It measures the content against whatever page the diagram has now,
because the mask repaints the page rectangle, and only the as-is render's content pixels count. `rsvg-convert`
ignores `prefers-color-scheme`, so it always renders the light theme.
