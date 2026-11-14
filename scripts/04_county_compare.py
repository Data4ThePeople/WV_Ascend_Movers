"""Net domestic migration per 1,000 residents: Ascend WV host counties vs the rest of West Virginia.

Descriptive only. Ascend's arrivals are a few hundred people spread over six areas and five years, so
county migration figures mostly reflect everything else that moves people. The point of this table is
scale and sequence, not cause.

Rate = sum of net domestic migration over the years / average population over the same years / years * 1,000.
Two periods: 2015-2019 (years ending July 1) and 2021-2025. The year ending July 1, 2020 is left out:
it straddles the pandemic start and sits at the seam between the two Census vintages.

ASCEND maps each host community to the county or counties it covers, with the launch date.
Source for each community is in data/ascend_communities.csv.
"""
import collections
import csv

from common import PROC, write_csv

ASCEND = {   # fips: (community, year applications opened there). Counties inferred from the school systems
    # each community page names; the program says areas are "a rough 30-minute drivetime" from the center city.
    "54061": ("Morgantown", 2021),
    "54025": ("Greenbrier Valley", 2022),
    "54037": ("Eastern Panhandle", 2022),
    "54003": ("Eastern Panhandle", 2022),
    "54065": ("Eastern Panhandle", 2022),
    "54083": ("Greater Elkins", 2022),
    "54019": ("New River Gorge", 2023),
    "54081": ("New River Gorge", 2023),
    "54067": ("New River Gorge", 2023),
    "54039": ("Charleston", 2025),
}
PERIODS = {"2015-2019": range(2015, 2020), "2021-2025": range(2021, 2026)}


def main():
    data = collections.defaultdict(dict)
    for r in csv.DictReader(open(PROC / "wv_county_components.csv")):
        data[r["fips"]][int(r["year_ending_july"])] = (int(r["domestic_mig"]), int(r["population"]), r["name"])

    def rate(fipss, years):
        mig = sum(data[f][y][0] for f in fipss for y in years)
        pop = sum(data[f][y][1] for f in fipss for y in years) / len(years)
        return mig, round(1000 * mig / pop / len(years), 2)

    rows = []
    for f, d in sorted(data.items()):
        name = d[2025][2]
        comm, launch = ASCEND.get(f, ("", ""))
        out = [f, name, comm, launch]
        for years in PERIODS.values():
            out += list(rate([f], years))
        rows.append(out)
    panhandle = [f for f in ASCEND if ASCEND[f][0] == "Eastern Panhandle"]
    groups = {"Ascend counties": [f for f in data if f in ASCEND],
              "Eastern Panhandle (Ascend)": panhandle,
              "Other Ascend areas": [f for f in ASCEND if f not in panhandle],
              "Rest of West Virginia": [f for f in data if f not in ASCEND],
              "West Virginia minus Eastern Panhandle": [f for f in data if f not in panhandle],
              "West Virginia, all counties": list(data)}
    for g, fs in groups.items():
        out = ["", g, "", ""]
        for years in PERIODS.values():
            out += list(rate(fs, years))
        rows.append(out)
    write_csv("county_compare.csv", ["fips", "county", "ascend_community", "ascend_launch",
                                     "net_dom_2015_2019", "rate_2015_2019", "net_dom_2021_2025", "rate_2021_2025"],
              rows)
    for r in rows:
        if r[2] or not r[0]:
            print(r)


if __name__ == "__main__":
    main()
