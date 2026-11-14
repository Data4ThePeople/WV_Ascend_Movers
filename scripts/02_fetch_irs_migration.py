"""IRS Statistics of Income state-to-state migration, West Virginia, 2011-12 to 2022-23.

Each file pairs tax returns filed in two consecutive years and compares the address on each.
n1 = returns (roughly households), n2 = exemptions or individuals (roughly people), AGI in thousands of dollars.
We keep three rows per year and direction:
  96 = total migration, U.S. and foreign; 97 = total migration, U.S. only; 98 = foreign.
"Inflow" rows are people who filed outside WV in year 1 and inside WV in year 2; "outflow" the reverse.
"""
import csv
import io

from common import RAW, STATE, cached, write_csv

YEARS = [f"{y % 100:02d}{(y + 1) % 100:02d}" for y in range(2011, 2023)]   # 1112 ... 2223
KEEP = {"96": "us_and_foreign", "97": "us", "98": "foreign"}


def main():
    out, seen = [], set()
    for yy in YEARS:
        for direction, here, there in [("inflow", "y2_statefips", "y1_statefips"),
                                       ("outflow", "y1_statefips", "y2_statefips")]:
            url = f"https://www.irs.gov/pub/irs-soi/state{direction}{yy}.csv"
            raw = cached(RAW / "irs" / url.rsplit("/", 1)[1], url).decode("latin-1")
            for r in csv.DictReader(io.StringIO(raw)):
                r = {k.lower(): v for k, v in r.items()}   # some years use capitalized headers
                name = r["y1_state_name" if direction == "inflow" else "y2_state_name"]
                # some years also code the non-movers row ("Same State") as 97; it is not migration
                if r[here].zfill(2) != STATE or r[there] not in KEEP or "Same State" in name:
                    continue
                key = (yy, direction, r[there])
                if key in seen:
                    raise SystemExit(f"duplicate key {key}")
                seen.add(key)
                year2 = 2000 + int(yy[2:])
                out.append([year2, f"20{yy[:2]}-{yy[2:]}", direction, KEEP[r[there]],
                            int(r["n1"]), int(r["n2"]), int(r["agi"])])
    write_csv("wv_irs_flows.csv", ["year2", "years", "direction", "scope", "returns", "individuals",
                                   "agi_thousands"], out)


if __name__ == "__main__":
    main()
