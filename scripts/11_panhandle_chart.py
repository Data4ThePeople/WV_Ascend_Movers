"""Chart 8: net moves from the Washington metro to the Eastern Panhandle (people who moved in minus people who
moved the other way), IRS filing years 2011-12 to 2022-23. Reads data/processed/panhandle_inflows.csv and
panhandle_outflows.csv (script 10)."""
import matplotlib.pyplot as plt
import pandas as pd

from common import CHARTS, PROC
from plot_style import BLUE, GRID, INK, INK_DIM, MUTED, credit, titleblock, use_house_style

PRE, POST = ["2017-18", "2018-19", "2019-20"], ["2020-21", "2021-22", "2022-23"]


def net_by_year():
    i = pd.read_csv(PROC / "panhandle_inflows.csv")
    o = pd.read_csv(PROC / "panhandle_outflows.csv")
    i = i[i.origin == "Washington metro"].set_index("years").people
    o = o[o.destination == "Washington metro"].set_index("years").people
    return i - o, i, o


def main():
    net, i, o = net_by_year()
    years = list(net.index)
    x = range(len(years))
    use_house_style()
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(top=0.68, bottom=0.2, left=0.08, right=0.95)
    ax.axvspan(years.index("2020-21") - 0.5, len(years) - 0.5, color=GRID, lw=0)
    ax.text(years.index("2020-21") - 0.35, 2850, "Moves from 2020\nfilings to 2021\nand later", color=INK_DIM,
            fontsize=9, va="top")
    ax.plot(x, net.values, color=BLUE, lw=2)
    ax.scatter(x, net.values, color=BLUE, s=22, zorder=3)
    for k in years:
        ax.annotate(f"{net[k]:,}", (years.index(k), net[k]), textcoords="offset points",
                    xytext=(0, -15 if k == "2021-22" else 8), ha="center", fontsize=8, color=INK)
    # three-year averages used in the text
    avgs = []
    for ks in (PRE, POST):
        a = round(i[ks].mean() - o[ks].mean())
        avgs.append(a)
        j0, j1 = years.index(ks[0]), years.index(ks[-1])
        ax.plot([j0 - 0.3, j1 + 0.3], [a, a], color=MUTED, lw=1.2, ls=(0, (3, 3)))
    ax.set_xticks(list(x))
    ax.set_xticklabels([y[2:4] + "-" + y[-2:] for y in years], fontsize=9)
    ax.set_ylim(0, 3000)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}")
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    titleblock(fig, "Net moves from the Washington area to the Eastern Panhandle",
               "People who moved from the Washington metro (D.C. and 21 nearby Maryland and Virginia counties and "
               "cities) to\nJefferson, Berkeley and Morgan counties, minus people who moved the other way, by IRS "
               f"filing years.\nDashed lines: three-year averages, {avgs[0]:,} a year (2017-18 to 2019-20) and "
               f"{avgs[1]:,} (2020-21 to 2022-23).\nOnly county pairs with 20 or more returns a year are listed by "
               "the IRS, so these are undercounts.")
    credit(fig, "Source: IRS Statistics of Income, U.S. Population Migration Data, county-to-county, 2011-12 to "
                "2022-23. The IRS notes that processing changes from\n2014-15 on may affect comparisons; 2022-23 uses "
                "an updated matching method. Data 4 The People calculation.")
    fig.savefig(CHARTS / "08-washington-panhandle-net.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
