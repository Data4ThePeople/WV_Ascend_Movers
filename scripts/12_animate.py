"""Animated GIF of chart 1 (West Virginia's net domestic migration) for social posts.

The bars rise one year at a time over about eight seconds, then the finished chart holds for
about five. Each bar's label appears only once the bar is at its full, published value. Same
data, colors, text and layout as chart_wv_domestic() in 06_charts.py.

    python scripts/12_animate.py [seconds] [hold_seconds]
"""
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

from common import PROC, ROOT  # noqa: E402
from plot_style import BLUE, INK, INK_DIM, MUTED, YELLOW, credit, titleblock, use_house_style  # noqa: E402

OUT = ROOT / "posts" / "west-virginia-ascend" / "social"
SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
HOLD = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
FRAME_MS = 80
WIDTH_PX = 1200


def main():
    use_house_style()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(PROC / "wv_components.csv")))
    years = [int(r["year_ending_july"]) for r in rows]
    vals = [int(r["domestic_mig"]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.set_dpi(WIDTH_PX / fig.get_figwidth())
    fig.subplots_adjust(top=0.78, bottom=0.17, left=0.09, right=0.97)
    bars = ax.bar(years, vals, color=[YELLOW if v < 0 else BLUE for v in vals], width=0.7)
    labels = [ax.text(x, v + (250 if v >= 0 else -250), f"{v:,}", ha="center", va="bottom" if v >= 0 else "top",
                      fontsize=8.5, color=INK_DIM, visible=False) for x, v in zip(years, vals)]
    ax.axhline(0, color=INK_DIM, lw=0.8)
    vline = ax.axvline(2021.5, color=MUTED, lw=1, ls=(0, (3, 3)), visible=False)
    note = ax.text(2021.62, max(vals) * 1.05 + 1500, "First Ascend class of 53\nannounced Sept. 2021", color=INK,
                   fontsize=9.5, va="top", visible=False)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], fontsize=9)
    ax.set_ylim(min(vals) * 1.18, max(vals) * 1.05 + 2000)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.set_major_formatter(lambda v, _: f"{int(v):,}")
    ax.set_xlim(ax.get_xlim())   # fix the limits from the full bars before they start at zero
    titleblock(fig, "West Virginia's net domestic migration, 2011 to 2025",
               "People moving in from other states minus people moving out, years ending July 1. "
               "Losses in yellow, gains in blue.\nThe line marks Ascend WV's first class; it does not mean "
               "the program caused any change.")
    credit(fig, "Source: U.S. Census Bureau, Population Estimates, Vintage 2020 (2011-2020) and Vintage 2025 "
                "(2021-2025). The two vintages use\ndifferent Census bases and are not revised to match.")

    def draw(t):
        """t runs from 0 to len(years); bar i is full once t >= i + 1."""
        for i, (b, lab, v) in enumerate(zip(bars, labels, vals)):
            frac = min(max(t - i, 0.0), 1.0)
            b.set_height(v * frac)
            lab.set_visible(frac >= 1.0)
        shown = t >= years.index(2022)
        vline.set_visible(shown)
        note.set_visible(shown)
        fig.canvas.draw()
        return Image.frombuffer("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB").copy()

    n = int(round(SECONDS * 1000 / FRAME_MS))
    step = len(years) / (n - 1)
    frames = [draw(min(i * step, len(years))) for i in range(n)]
    last = draw(len(years))
    plt.close(fig)

    pal = last.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames] + [pal]
    path = OUT / "01-wv-net-domestic-migration.gif"
    q[0].save(path, save_all=True, append_images=q[1:], duration=[FRAME_MS] * n + [int(HOLD * 1000)], loop=0,
              optimize=False, disposal=1)
    last.save(OUT / "01-wv-net-domestic-migration-final-frame.png")
    print(f"{path.name}: {len(q)} frames, {last.size[0]}x{last.size[1]}, {n * FRAME_MS / 1000:.1f}s + "
          f"{HOLD:.0f}s hold, {path.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
