"""Where people moving into the Eastern Panhandle (Jefferson, Berkeley, Morgan) came from, before and after
COVID, from IRS county-to-county inflows, 2011-12 to 2022-23. Writes data/processed/panhandle_inflows.csv
(one row per filing-year pair and origin group) and data/processed/panhandle_inflow_counties.csv (top origins).
"""
import io

import pandas as pd

from common import PROC, RAW, cached

PANHANDLE = {"037": "Jefferson", "003": "Berkeley", "065": "Morgan"}
PANHANDLE_FIPS = {54037, 54003, 54065}
# Washington metro core: D.C. and the inner Maryland and Virginia counties and cities (OMB Washington-Arlington-
# Alexandria metro, central counties). Kept as a fixed list so every year is grouped the same way.
DC_METRO = {11001,                                      # District of Columbia
            24031, 24033, 24021, 24017, 24009,          # Montgomery, Prince George's, Frederick, Charles, Calvert MD
            51013, 51059, 51107, 51153, 51179, 51061, 51043, 51047, 51177, 51187,  # Arlington, Fairfax, Loudoun,
            # Prince William, Stafford, Fauquier, Clarke, Culpeper, Spotsylvania, Warren VA
            51510, 51600, 51610, 51683, 51685, 51630}   # Alexandria, Fairfax city, Falls Church, Manassas,
            # Manassas Park, Fredericksburg
BALTIMORE = {24510, 24005, 24003, 24027, 24013, 24025, 24035}  # Baltimore city/county, Anne Arundel, Howard,
            # Carroll, Harford, Queen Anne's
NEARBY = {24043, 24001, 51069, 51840, 42055, 42057, 42001}  # Washington Co MD, Allegany MD, Frederick VA,
            # Winchester VA, Franklin PA, Fulton PA, Adams PA
YEARS = [f"{y % 100:02d}{(y + 1) % 100:02d}" for y in range(2011, 2023)]


def group(fips):
    if fips in DC_METRO:
        return "Washington metro"
    if fips in BALTIMORE:
        return "Baltimore metro"
    if fips in NEARBY:
        return "Nearby MD, VA, PA counties"
    if 54000 < fips < 55000:
        return "Elsewhere in West Virginia"
    return "Everywhere else"


def main():
    rows, counties = [], []
    for yy in YEARS:
        raw = cached(RAW / "irs" / f"countyinflow{yy}.csv", f"https://www.irs.gov/pub/irs-soi/countyinflow{yy}.csv")
        d = pd.read_csv(io.BytesIO(raw), encoding="latin-1", dtype=str)
        d.columns = [c.lower() for c in d.columns]
        for c, w in [("y2_statefips", 2), ("y2_countyfips", 3), ("y1_statefips", 2), ("y1_countyfips", 3)]:
            d[c] = d[c].str.strip().str.zfill(w)   # 2020-21 and 2021-22 drop leading zeros
        d = d[(d.y2_statefips == "54") & (d.y2_countyfips.isin(PANHANDLE))].copy()
        for c in ("n1", "n2", "agi"):
            d[c] = pd.to_numeric(d[c])
        d["y1"] = pd.to_numeric(d.y1_statefips) * 1000 + pd.to_numeric(d.y1_countyfips)
        # county-to-county rows only: real state codes (1-56) and not the destination itself (non-movers)
        cc = d[(pd.to_numeric(d.y1_statefips) <= 56) & (d.y1 != d.y2_statefips.astype(int) * 1000 + d.y2_countyfips.astype(int))]
        cc = cc[~cc.y1.isin(PANHANDLE_FIPS)]           # moves between the three Panhandle counties do not count
        # totals: code 96000 "Total Migration-US and Foreign", 97000 US; 'other flows' (suppressed small cells)
        tot = d[d.y1_statefips == "97"]
        tot = tot[tot.y1_countyfips == "000"]
        us_total = tot.groupby("y2_countyfips")[["n1", "n2", "agi"]].sum().sum()
        within = cc.copy()
        within["grp"] = within.y1.map(group)
        g = within.groupby("grp")[["n1", "n2", "agi"]].sum()
        # US total minus moves from the other two Panhandle counties
        intra = d[(pd.to_numeric(d.y1_statefips) <= 56) & d.y1.isin(PANHANDLE_FIPS) &
                  (d.y1 != d.y2_statefips.astype(int) * 1000 + d.y2_countyfips.astype(int))][["n1", "n2", "agi"]].sum()
        us = us_total - intra
        for grp, r in g.iterrows():
            rows.append([f"20{yy[:2]}-{yy[2:]}", grp, int(r.n1), int(r.n2), int(r.agi)])
        rest = us - g.drop(index="Everywhere else", errors="ignore").sum()
        rows = [r for r in rows if not (r[0] == f"20{yy[:2]}-{yy[2:]}" and r[1] == "Everywhere else")]
        rows.append([f"20{yy[:2]}-{yy[2:]}", "Everywhere else", int(rest.n1), int(rest.n2), int(rest.agi)])
        rows.append([f"20{yy[:2]}-{yy[2:]}", "All U.S. arrivals", int(us.n1), int(us.n2), int(us.agi)])
        top = within.groupby(["y1", "y1_state", "y1_countyname"])[["n1", "n2", "agi"]].sum().reset_index()
        top.insert(0, "years", f"20{yy[:2]}-{yy[2:]}")
        counties.append(top)
    out = pd.DataFrame(rows, columns=["years", "origin", "returns", "people", "agi_thousands"])
    out.to_csv(PROC / "panhandle_inflows.csv", index=False)
    pd.concat(counties).to_csv(PROC / "panhandle_inflow_counties.csv", index=False)
    p = out.pivot(index="years", columns="origin", values="people")
    print(p.to_string())
    a = out.pivot(index="years", columns="origin", values="agi_thousands") * 1000 / out.pivot(
        index="years", columns="origin", values="returns")
    print((a.round(-2)).to_string())


if __name__ == "__main__":
    main()


def outflows():
    """Moves out of the Panhandle to each origin group (IRS county outflows), for net figures."""
    rows = []
    for yy in YEARS:
        raw = cached(RAW / "irs" / f"countyoutflow{yy}.csv", f"https://www.irs.gov/pub/irs-soi/countyoutflow{yy}.csv")
        d = pd.read_csv(io.BytesIO(raw), encoding="latin-1", dtype=str)
        d.columns = [c.lower() for c in d.columns]
        for c, w in [("y1_statefips", 2), ("y1_countyfips", 3), ("y2_statefips", 2), ("y2_countyfips", 3)]:
            d[c] = d[c].str.strip().str.zfill(w)
        d = d[(d.y1_statefips == "54") & (d.y1_countyfips.isin(PANHANDLE))].copy()
        for c in ("n1", "n2", "agi"):
            d[c] = pd.to_numeric(d[c])
        d["y2"] = pd.to_numeric(d.y2_statefips) * 1000 + pd.to_numeric(d.y2_countyfips)
        own = d.y1_statefips.astype(int) * 1000 + d.y1_countyfips.astype(int)
        cc = d[(pd.to_numeric(d.y2_statefips) <= 56) & (d.y2 != own) & ~d.y2.isin(PANHANDLE_FIPS)].copy()
        cc["grp"] = cc.y2.map(group)
        g = cc.groupby("grp")[["n1", "n2"]].sum()
        for grp, r in g.iterrows():
            if grp != "Everywhere else":
                rows.append([f"20{yy[:2]}-{yy[2:]}", grp, int(r.n1), int(r.n2)])
    out = pd.DataFrame(rows, columns=["years", "destination", "returns", "people"])
    out.to_csv(PROC / "panhandle_outflows.csv", index=False)
    print(out.pivot(index="years", columns="destination", values="people").to_string())


if __name__ == "__main__":
    outflows()
