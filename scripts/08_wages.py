"""State wage benchmarks from BLS Occupational Employment and Wage Statistics (OEWS), all occupations,
West Virginia and Ohio: annual mean and annual median wage, latest May estimate available.

Ascend publishes average (mean) salaries and JobsOhio's committed payroll per committed job is also an
average, so the mean is the like-for-like benchmark; the median is kept for context.
Series IDs: OEU + S + area (state FIPS + 00000) + industry 000000 + occupation 000000 + datatype
(04 annual mean, 13 annual median).
"""
import json

from common import RAW, cached, get_key, write_csv

SERIES = {(st, dtype): f"OEUS{fips}00000000000000000{code}"
          for st, fips in [("West Virginia", "54"), ("Ohio", "39")]
          for dtype, code in [("annual_mean", "04"), ("annual_median", "13")]}


def main():
    body = json.dumps({"seriesid": list(SERIES.values()), "latest": "true",
                       "registrationkey": get_key("BLS_API_KEY")}).encode()
    raw = json.loads(cached(RAW / "bls" / "oews_state_wages.json", "https://api.bls.gov/publicAPI/v2/timeseries/data/",
                            data=body, headers={"Content-Type": "application/json"}))
    if raw.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS: {raw.get('status')} {raw.get('message')}")
    by_id = {s["seriesID"]: s["data"] for s in raw["Results"]["series"]}
    rows = []
    for (st, dtype), sid in SERIES.items():
        d = by_id.get(sid) or []
        if len(d) != 1:
            raise SystemExit(f"{sid}: expected one latest value, got {len(d)}")
        rows.append([st, dtype, d[0]["year"], d[0]["periodName"], int(float(d[0]["value"])), sid])
    write_csv("state_wages_oews.csv", ["state", "measure", "year", "period", "usd", "series_id"], rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
