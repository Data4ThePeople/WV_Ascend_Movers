"""Chart 4 as a map: net domestic migration per 1,000 residents per year, by county, 2015-2019 and
2021-2025, with Ascend counties outlined. Reads data/processed/county_compare.csv (built by script 04,
tied out) and the Census cartographic county boundaries (downloaded into data/raw/census/ if missing).
"""
import urllib.request

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from common import PROC, RAW, ROOT
from plot_style import INK, INK_DIM, MUTED, SURFACE, credit, titleblock, use_house_style

SHP_URL = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip"
SHP = RAW / "census" / "cb_2024_us_county_500k.zip"

# Diverging scale: yellow = losses, blue = gains (house convention), gray midpoint. Lightness checked
# symmetric on the dark surface (OKLab L .76/.59/.46 | .34 | .48/.62/.76).
BINS = [(-99, -10, "#eda100", "Loss of 10 or more"), (-10, -5, "#a87210", "Loss of 5 to 10"),
        (-5, -1, "#6e5420", "Loss of 1 to 5"), (-1, 1, "#383835", "Within 1 of zero"),
        (1, 5, "#1c5cab", "Gain of 1 to 5"), (5, 10, "#3987e5", "Gain of 5 to 10"),
        (10, 99, "#86b6ef", "Gain of 10 or more")]


def color(v):
    for lo, hi, c, _ in BINS:
        if lo <= v < hi:
            return c
    raise ValueError(v)


def main():
    if not SHP.exists():
        SHP.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(SHP_URL, headers={"User-Agent": "Mozilla/5.0 (Data 4 The People)"})
        SHP.write_bytes(urllib.request.urlopen(req).read())
    geo = gpd.read_file(f"zip://{SHP}")
    geo = geo[geo.STATEFP == "54"].copy()
    geo["fips"] = (geo.STATEFP + geo.COUNTYFP).astype(int)

    cc = pd.read_csv(PROC / "county_compare.csv")
    cc = cc[cc.fips.notna()].copy()
    cc["fips"] = cc.fips.astype(int)
    if cc.fips.duplicated().any():
        raise SystemExit("duplicate county fips")
    if len(cc) != 55 or set(cc.fips) != set(geo.fips):
        raise SystemExit("county list does not match the 55 WV counties in the boundary file")
    geo = geo.merge(cc, on="fips").to_crs(26917)   # UTM 17N

    comm = pd.read_csv(ROOT / "data" / "ascend_communities.csv")
    asc_fips = {int(f) for fs in comm.fips for f in str(fs).split(";")}
    ascend = geo[geo.fips.isin(asc_fips)]

    use_house_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 6.75))
    fig.subplots_adjust(top=0.80, bottom=0.17, left=0.02, right=0.98, wspace=0.02)
    for ax, col, label in [(axes[0], "rate_2015_2019", "2015 to 2019"), (axes[1], "rate_2021_2025", "2021 to 2025")]:
        geo.plot(ax=ax, color=[color(v) for v in geo[col]], edgecolor=SURFACE, linewidth=0.6)
        ascend.dissolve().boundary.plot(ax=ax, color=INK, linewidth=1.6)
        ax.set_title(label, color=INK, fontsize=13, loc="left", pad=4)
        ax.set_axis_off()
        ax.set_aspect("equal")
    handles = [Patch(facecolor=c, edgecolor="none", label=t) for _, _, c, t in BINS]
    handles.append(Patch(facecolor="none", edgecolor=INK, linewidth=1.6, label="Ascend counties"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9.5,
               labelcolor=INK_DIM, bbox_to_anchor=(0.5, 0.075), handlelength=1.4, columnspacing=1.4)
    titleblock(fig, "Where West Virginia gained and lost people to other states",
               "Net domestic migration per 1,000 residents per year, by county. Yellow is a net loss, blue a "
               "net gain.\nAscend counties outlined, for the whole period whatever their launch year.")
    credit(fig, "Source: U.S. Census Bureau, Population Estimates, Vintage 2020 and Vintage 2025; county "
                "boundaries, Census cartographic files 2024.\nAscend county list from Ascend WV and WVU. "
                "Data 4 The People calculation.")
    out = ROOT / "charts" / "04-county-migration-map.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
