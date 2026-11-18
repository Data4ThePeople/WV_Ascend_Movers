"""Chart 8: people moving between the Washington metro and the Eastern Panhandle, IRS filing years 2011-12
to 2022-23. Reads data/processed/panhandle_inflows.csv and panhandle_outflows.csv (script 10)."""
import matplotlib.pyplot as plt
import pandas as pd

from common import CHARTS, PROC
from plot_style import BLUE, GRID, INK, INK_DIM, MUTED, YELLOW, credit, titleblock, use_house_style


def main():
    i = pd.read_csv(PROC / "panhandle_inflows.csv")
    o = pd.read_csv(PROC / "panhandle_outflows.csv")
    i = i[i.origin == "Washington metro"].set_index("years").people
    o = o[o.destination == "Washington metro"].set_index("years").people
    years = list(i.index)
    x = range(len(years))
    use_house_style()
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(top=0.72, bottom=0.2, left=0.08, right=0.86)
    ax.axvspan(years.index("2020-21") - 0.5, len(years) - 0.5, color=GRID, lw=0)
    ax.text(years.index("2020-21") - 0.35, 120, "Moves from 2020\nfilings to 2021\nand later", color=INK_DIM, fontsize=9,
            va="bottom")
    for s, color, label in [(i, BLUE, "Moved to the\nPanhandle"), (o, YELLOW, "Moved to the\nWashington metro")]:
        ax.plot(x, s.values, color=color, lw=2)
        ax.scatter(x, s.values, color=color, s=22, zorder=3)
        ax.text(len(years) - 0.7, s.values[-1], label, color=color, fontsize=10.5, fontweight="bold", va="center")
    for k in ("2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23"):
        j = years.index(k)
        ax.annotate(f"{i[k]:,}", (j, i[k]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8,
                    color=BLUE)
    ax.set_xticks(list(x))
    ax.set_xticklabels([y[2:4] + "-" + y[-2:] for y in years], fontsize=9)
    ax.set_ylim(0, 3500)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    titleblock(fig, "Moves between the Washington area and the Eastern Panhandle",
               "People on tax returns that moved between the Washington metro (D.C. and 21 nearby Maryland and "
               "Virginia\ncounties and cities) and Jefferson, Berkeley and Morgan counties, by IRS filing years. "
               "Only county pairs\nwith 20 or more returns a year are listed by the IRS, so these are undercounts.")
    credit(fig, "Source: IRS Statistics of Income, U.S. Population Migration Data, county-to-county, 2011-12 to "
                "2022-23. The IRS notes that processing changes from\n2014-15 on may affect comparisons; 2022-23 uses an updated "
                "matching method. Data 4 The People calculation.")
    fig.savefig(CHARTS / "08-washington-panhandle-moves.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
