"""Static charts for Step 1, house dark palette. Every number is read from data/processed at render time."""
import collections
import csv

import matplotlib.pyplot as plt

from common import CHARTS, PROC
from plot_style import BLUE, GRID, INK, INK_DIM, MAGENTA, MUTED, YELLOW, credit, titleblock, use_house_style

use_house_style()
CHARTS.mkdir(exist_ok=True)


def read(name):
    return list(csv.DictReader(open(PROC / name)))


def fmt(n):
    return f"{n:+,}" if n else "0"


def chart_wv_domestic():
    rows = read("wv_components.csv")
    years = [int(r["year_ending_july"]) for r in rows]
    vals = [int(r["domestic_mig"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(top=0.78, bottom=0.17, left=0.09, right=0.97)
    ax.bar(years, vals, color=[YELLOW if v < 0 else BLUE for v in vals], width=0.7)
    for x, v in zip(years, vals):
        ax.text(x, v + (250 if v >= 0 else -250), f"{v:,}", ha="center", va="bottom" if v >= 0 else "top",
                fontsize=8.5, color=INK_DIM)
    ax.axhline(0, color=INK_DIM, lw=0.8)
    ax.axvline(2020.5, color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.text(2020.62, max(vals) * 1.05 + 1500, "Ascend WV opens\nApril 2021", color=INK, fontsize=9.5, va="top")
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], fontsize=9)
    ax.set_ylim(min(vals) * 1.18, max(vals) * 1.05 + 2000)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.set_major_formatter(lambda v, _: f"{int(v):,}")
    titleblock(fig, "West Virginia's net domestic migration, 2011 to 2025",
               "People moving in from other states minus people moving out, years ending July 1. "
               "Losses in yellow, gains in blue.\nThe line marks Ascend WV's launch; it does not mean the "
               "program caused the change.")
    credit(fig, "Source: U.S. Census Bureau, Population Estimates, Vintage 2020 (2011-2020) and Vintage 2025 "
                "(2021-2025). The two vintages use\ndifferent Census bases and are not revised to match.")
    fig.savefig(CHARTS / "01-wv-net-domestic-migration.png")
    plt.close(fig)


def chart_irs_flows():
    rows = [r for r in read("wv_irs_flows.csv") if r["scope"] == "us"]
    d = collections.defaultdict(dict)
    for r in rows:
        d[r["years"]][r["direction"]] = int(r["individuals"])
    labels = list(d)
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(top=0.78, bottom=0.17, left=0.09, right=0.88)
    for key, color in [("inflow", BLUE), ("outflow", YELLOW)]:
        ys = [d[l][key] for l in labels]
        ax.plot(x, ys, color=color, lw=2.4, marker="o", ms=4)
        ax.text(len(labels) - 0.8, ys[-1], "Moved in" if key == "inflow" else "Moved out", color=color,
                fontsize=11, fontweight="bold", va="center")
        ax.text(len(labels) - 1, ys[-1] + (900 if key == "inflow" else -900), f"{ys[-1]:,}", color=color,
                fontsize=9, ha="center", va="center")
    ax.set_xticks(list(x))
    ax.set_xticklabels([l.replace("20", "", 1).replace("-", "-\n") for l in labels], fontsize=8.5)
    ax.yaxis.set_major_formatter(lambda v, _: f"{int(v):,}")
    ax.set_ylim(20000, 52000)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    titleblock(fig, "People moving into and out of West Virginia, from tax returns",
               "People on federal tax returns whose address moved between West Virginia and another state, "
               "by pair of filing years.\nThe IRS warns that processing changes may affect 2014-15. 2022-23 starts a new "
               "series that matches about 5% more returns.")
    credit(fig, "Source: IRS Statistics of Income, U.S. Population Migration Data, state-to-state inflows and "
                "outflows, 2011-12 to 2022-23.\nCovers people on returns only (n2). Latest year published: 2022-23.")
    fig.savefig(CHARTS / "02-wv-irs-in-out.png")
    plt.close(fig)


def state_rates():
    d = collections.defaultdict(dict)
    for r in read("state_components.csv"):
        d[r["name"]][int(r["year_ending_july"])] = (int(r["domestic_mig"]), int(r["population"]))

    def rate(n, ys):
        return 1000 * sum(d[n][y][0] for y in ys) / (sum(d[n][y][1] for y in ys) / len(ys)) / len(ys)
    return {n: (rate(n, range(2015, 2020)), rate(n, range(2021, 2026))) for n in d}


def chart_state_change():
    rates = state_rates()
    order = sorted(rates, key=lambda n: rates[n][1] - rates[n][0], reverse=True)
    show = order[:10] + [n for n in ["Ohio", "Pennsylvania", "Kentucky", "Virginia", "Maryland"] if n not in order[:10]]
    show = sorted(show, key=lambda n: rates[n][1] - rates[n][0])
    fig, ax = plt.subplots(figsize=(10, 7.4))
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.2, right=0.95)
    for i, n in enumerate(show):
        ch = rates[n][1] - rates[n][0]
        color = MAGENTA if n == "West Virginia" else (BLUE if n == "Ohio" else MUTED)
        ax.barh(i, ch, color=color, height=0.68)
        ax.text(ch + 0.12, i, f"{ch:+.2f}", va="center", fontsize=9, color=INK)
        rank = order.index(n) + 1
        ax.text(-0.15, i, f"{n}  ({rank})", va="center", ha="right", fontsize=10,
                color=INK if n in ("West Virginia", "Ohio") else INK_DIM,
                fontweight="bold" if n in ("West Virginia", "Ohio") else "normal")
    ax.axhline(9.5 - (15 - len(show)), color=GRID, lw=0)
    ax.set_yticks([])
    ax.axvline(0, color=INK_DIM, lw=0.8)
    ax.set_xlim(-0.2, max(rates[n][1] - rates[n][0] for n in show) * 1.15)
    ax.tick_params(axis="x", labelsize=9)
    ax.spines["left"].set_visible(False)
    titleblock(fig, "Ten states with the largest turn in domestic migration, plus West Virginia's neighbors",
               "Change in net domestic migration per 1,000 residents per year, 2021-2025 average minus "
               "2015-2019 average.\nRank among 50 states and D.C. in parentheses. West Virginia in magenta, "
               "Ohio in blue.")
    credit(fig, "Source: U.S. Census Bureau, Population Estimates, Vintage 2020 and Vintage 2025, components of "
                "change. Years end July 1;\nthe year ending July 1, 2020 is left out. Data 4 The People "
                "calculation.")
    fig.savefig(CHARTS / "03-state-migration-turn.png")
    plt.close(fig)


def chart_counties():
    rows = {r["county"]: r for r in read("county_compare.csv")}
    groups = ["Ascend counties", "Rest of West Virginia"]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.subplots_adjust(top=0.72, bottom=0.2, left=0.24, right=0.95)
    for i, g in enumerate(groups):
        for j, (col, color) in enumerate([("rate_2015_2019", YELLOW), ("rate_2021_2025", BLUE)]):
            v = float(rows[g][col])
            y = i + (-0.18 if j == 0 else 0.18)
            ax.barh(y, v, height=0.32, color=color)
            ax.text(v + (0.12 if v >= 0 else -0.12), y, f"{v:+.2f}", va="center",
                    ha="left" if v >= 0 else "right", fontsize=9.5, color=INK)
        ax.text(-6.4, i, g, ha="right", va="center", fontsize=11, color=INK)
    ax.set_yticks([])
    ax.invert_yaxis()
    ax.axvline(0, color=INK_DIM, lw=0.8)
    ax.set_xlim(-6.2, 3.4)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)
    fig.text(0.03, 0.765, "2015-2019", color=YELLOW, fontsize=11, fontweight="bold")
    fig.text(0.14, 0.765, "2021-2025", color=BLUE, fontsize=11, fontweight="bold")
    titleblock(fig, "Ascend host counties and the rest of West Virginia",
               "Net domestic migration per 1,000 residents per year. Ascend counties: Monongalia, Greenbrier, "
               "Jefferson, Randolph,\nFayette and Kanawha, counted for the whole period whatever their launch "
               "year.")
    credit(fig, "Source: U.S. Census Bureau, Population Estimates, Vintage 2020 and Vintage 2025. "
                "County list from Ascend WV and WVU releases.\nData 4 The People calculation.")
    fig.savefig(CHARTS / "04-ascend-counties-vs-rest.png")
    plt.close(fig)


if __name__ == "__main__":
    chart_wv_domestic()
    chart_irs_flows()
    chart_state_change()
    chart_counties()
    print("charts written to", CHARTS)
