"""Census Bureau population estimates, components of change, for West Virginia and its counties.

Two vintages, because no single file covers 2010 to 2025:
- Vintage 2020 (co-est2020-alldata.csv): years ending July 1, 2011 to 2020, built on the 2010 Census.
- Vintage 2025 (co-est2025-alldata.csv): years ending July 1, 2021 to 2025, built on the 2020 Census.
The partial first year in each file (April to July of 2010 and of 2020) is dropped.
The two vintages are not revised to match each other; see DATASETS.md.
"""
import csv
import io

from common import RAW, STATE, cached, write_csv

FILES = {
    2020: ("https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv",
           range(2011, 2021)),
    2025: ("https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv",
           range(2021, 2026)),
}
FIELDS = ["POPESTIMATE", "NATURALCHG", "INTERNATIONALMIG", "DOMESTICMIG", "NETMIG", "RESIDUAL"]


def rows():
    for vintage, (url, years) in FILES.items():
        raw = cached(RAW / "popest" / url.rsplit("/", 1)[1], url).decode("latin-1")
        for r in csv.DictReader(io.StringIO(raw)):
            if r["STATE"] != STATE and r["SUMLEV"] != "040":
                continue
            for y in years:
                yield vintage, r, y


def main():
    state, county, us = [], [], []
    seen = set()
    for vintage, r, y in rows():
        # the 2010s file calls natural change NATURALINC; the 2020s file calls it NATURALCHG
        names = [("NATURALINC" if f == "NATURALCHG" and f"NATURALCHG{y}" not in r else f) for f in FIELDS]
        vals = [int(r[f"{n}{y}"]) for n in names]
        key = (r["SUMLEV"], r["STATE"], r["COUNTY"], y)
        if key in seen:
            raise SystemExit(f"duplicate key {key}")
        seen.add(key)
        row = [y, vintage, r["STATE"] + r["COUNTY"], r["CTYNAME"]] + vals
        if r["SUMLEV"] == "040":
            us.append(row)
            if r["STATE"] == STATE:
                state.append(row)
        elif r["SUMLEV"] == "050":
            county.append(row)
    header = ["year_ending_july", "vintage", "fips", "name", "population", "natural_change",
              "international_mig", "domestic_mig", "net_mig", "residual"]
    write_csv("wv_components.csv", header, sorted(state))
    write_csv("state_components.csv", header, sorted(us, key=lambda x: (x[2], x[0])))
    write_csv("wv_county_components.csv", header, sorted(county, key=lambda x: (x[2], x[0])))


if __name__ == "__main__":
    main()
