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
        if r["url"].startswith("provided:"):
            # a document sent to us directly and not published online; kept in data/raw, not committed
            if not (ROOT / r["url"][len("provided:"):]).exists():
                print(f"line {i}: note, {r['url']} is not on this machine")
        elif not r["url"].startswith("https://"):
            raise SystemExit(f"line {i}: url is not https or provided:")
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
    q3_communities(by)


def q3_communities(by):
    """Q3 2026 community pages against the statewide page. Gaps are printed, not fixed."""
    comm = list(csv.DictReader(open(ROOT / "data" / "ascend_q3_2026_communities.csv")))
    state = {r["measure"]: float(r["value"]) for m in by.values() for r in m if r["publish_date"] == "2026-10-16"}
    print("\nQ3 2026: sum of six community pages vs statewide page")
    for col, meas in [("members", "participants"), ("completed_two_years", "completed_two_years"),
                      ("total_incl_household", "new_residents_incl_family"), ("applications", "applications")]:
        tot = sum(int(r[col]) for r in comm)
        print(f"  {col:<22} communities {tot:>7,}   statewide {state[meas]:>9,.0f}   gap {tot - state[meas]:+,.0f}")
    m = sum(int(r["members"]) for r in comm)
    for col in ["wv_born_pct", "home_purchase_pct"]:
        print(f"  {col} weighted by members: {sum(int(r['members']) * int(r[col]) for r in comm) / m:.1f}")


if __name__ == "__main__":
    main()
