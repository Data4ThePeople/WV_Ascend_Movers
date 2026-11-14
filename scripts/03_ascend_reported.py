"""Checks the hand-built table of Ascend WV figures (data/ascend_reported.csv) and prints each measure over time.

Every row is a figure the program, WVU or a news story quoting them published. None of it is recomputed;
there is no public participant-level data. Conflicts are kept, not resolved.
"""
import collections
import csv

from common import ROOT

REQUIRED = ["publish_date", "measure", "unit", "source_name", "url", "exact_quote"]


def main():
    rows = list(csv.DictReader(open(ROOT / "data" / "ascend_reported.csv")))
    seen = set()
    for i, r in enumerate(rows, 2):
        for k in REQUIRED:
            if not r[k]:
                raise SystemExit(f"line {i}: {k} is empty")
        if not r["url"].startswith("https://"):
            raise SystemExit(f"line {i}: url is not https")
        key = (r["publish_date"], r["measure"], r["value"], r["url"])
        if key in seen:
            raise SystemExit(f"line {i}: duplicate row {key}")
        seen.add(key)
    by = collections.defaultdict(list)
    for r in rows:
        by[r["measure"]].append(r)
    for m in ["participants", "new_residents_incl_family", "retention_pct", "economic_impact_usd",
              "funding_usd", "completed_two_years"]:
        print(f"\n{m}")
        for r in sorted(by[m], key=lambda r: r["publish_date"]):
            print(f"  {r['publish_date']}  {r['value'] or '-':>11}  {r['unit']:<22} {r['source_name']}")
    print(f"\n{len(rows)} rows, {len(by)} measures, all with source and quote")


if __name__ == "__main__":
    main()
