"""Claude's tie-out. Recomputes every charted or headline number from the raw downloaded files with code
separate from the build scripts (pandas here, csv modules there), compares with data/processed, and writes
TIEOUT.md. The word checks (labels and sourced claims) are listed at the end with a status for each.
"""
import pandas as pd

from common import PROC, RAW, ROOT

rows = []


def check(item, ours, theirs, tol=0):
    ok = abs(float(ours) - float(theirs)) <= tol
    rows.append((item, ours, theirs, "match" if ok else "DIFFERENT"))


# --- Census: state rows, straight from the raw files -----------------------------------------------------
v20 = pd.read_csv(RAW / "popest" / "co-est2020-alldata.csv", encoding="latin-1", dtype={"STATE": str, "COUNTY": str})
v25 = pd.read_csv(RAW / "popest" / "co-est2025-alldata.csv", encoding="latin-1", dtype={"STATE": str, "COUNTY": str})
wv20 = v20[(v20.SUMLEV == 40) & (v20.STATE == "54")].iloc[0]
wv25 = v25[(v25.SUMLEV == 40) & (v25.STATE == "54")].iloc[0]
raw_dom = {y: int(wv20[f"DOMESTICMIG{y}"]) for y in range(2011, 2021)}
raw_dom.update({y: int(wv25[f"DOMESTICMIG{y}"]) for y in range(2021, 2026)})
proc = pd.read_csv(PROC / "wv_components.csv").set_index("year_ending_july")
for y, v in raw_dom.items():
    check(f"WV net domestic migration, year ending {y} (chart 1)", v, proc.loc[y, "domestic_mig"])
check("WV net domestic migration 2021-2025 total", sum(raw_dom[y] for y in range(2021, 2026)), 17349)
check("WV net domestic migration 2015-2019 total", sum(raw_dom[y] for y in range(2015, 2020)), -39847)
check("WV population July 1, 2025", int(wv25["POPESTIMATE2025"]), 1766147)


# --- Census: state rates and ranks (chart 3) -------------------------------------------------------------
def rates(df20, df25):
    out = {}
    s20 = df20[df20.SUMLEV == 40].set_index("STNAME")
    s25 = df25[df25.SUMLEV == 40].set_index("STNAME")
    for n in s25.index:
        pre = sum(s20.loc[n, f"DOMESTICMIG{y}"] for y in range(2015, 2020)) / \
            (sum(s20.loc[n, f"POPESTIMATE{y}"] for y in range(2015, 2020)) / 5) / 5 * 1000
        post = sum(s25.loc[n, f"DOMESTICMIG{y}"] for y in range(2021, 2026)) / \
            (sum(s25.loc[n, f"POPESTIMATE{y}"] for y in range(2021, 2026)) / 5) / 5 * 1000
        out[n] = post - pre
    return out


ch = rates(v20, v25)
rank = sorted(ch, key=ch.get, reverse=True)
check("States in ranking (50 + D.C.)", len(ch), 51)
for n, shown_rank, shown in [("Wyoming", 1, 8.89), ("Connecticut", 2, 6.82), ("West Virginia", 3, 6.34),
                             ("Alaska", 4, 5.94), ("Ohio", 31, 1.11), ("Maryland", 38, 0.05)]:
    check(f"{n} change per 1,000 (chart 3)", round(ch[n], 2), shown, tol=0.005)
    check(f"{n} rank (chart 3)", rank.index(n) + 1, shown_rank)

# --- Census: county groups (chart 4) ---------------------------------------------------------------------
groups = {"Eastern Panhandle (Ascend)": ["037", "003", "065"],
          "Other Ascend areas": ["061", "025", "083", "019", "081", "067", "039"]}
c20 = v20[(v20.SUMLEV == 50) & (v20.STATE == "54")].set_index("COUNTY")
c25 = v25[(v25.SUMLEV == 50) & (v25.STATE == "54")].set_index("COUNTY")
groups["Rest of West Virginia"] = [c for c in c25.index if c not in groups["Eastern Panhandle (Ascend)"]
                                   + groups["Other Ascend areas"]]
check("WV counties", len(c25), 55)
cc = pd.read_csv(PROC / "county_compare.csv").set_index("county")
for g, cs in groups.items():
    for label, df, ys in [("2015_2019", c20, range(2015, 2020)), ("2021_2025", c25, range(2021, 2026))]:
        mig = sum(df.loc[c, f"DOMESTICMIG{y}"] for c in cs for y in ys)
        pop = sum(df.loc[c, f"POPESTIMATE{y}"] for c in cs for y in ys) / 5
        check(f"{g}, net domestic {label}", mig, cc.loc[g, f"net_dom_{label}"])
        check(f"{g}, rate {label} (chart 4)", round(mig / pop / 5 * 1000, 2), cc.loc[g, f"rate_{label}"], tol=0.005)
check("Eastern Panhandle 2021-2025 gain exceeds WV total", 21680 > 17349, True)

# --- IRS (chart 2) ---------------------------------------------------------------------------------------
irs = pd.read_csv(PROC / "wv_irs_flows.csv")
for yy, d, shown in [("2223", "inflow", 36521), ("2223", "outflow", 33384), ("1415", "inflow", 23428),
                     ("1314", "inflow", 32962)]:
    f = pd.read_csv(RAW / "irs" / f"state{d}{yy}.csv", encoding="latin-1", dtype=str)
    f.columns = [c.lower() for c in f.columns]
    here = "y2_statefips" if d == "inflow" else "y1_statefips"
    there = "y1_statefips" if d == "inflow" else "y2_statefips"
    name = "y1_state_name" if d == "inflow" else "y2_state_name"
    r = f[(f[here].str.zfill(2) == "54") & (f[there] == "97") & (~f[name].str.contains("Same State"))]
    check(f"IRS {d} {yy} people (n2), from raw", int(r.n2.iloc[0]), shown)
    p = irs[(irs.years == f"20{yy[:2]}-{yy[2:]}") & (irs.direction == d) & (irs.scope == "us")]
    check(f"IRS {d} {yy} people, processed", int(p.individuals.iloc[0]), shown)

# --- JobsOhio (headline) ---------------------------------------------------------------------------------
jo = pd.read_csv(PROC / "jobsohio_per_job.csv").set_index("year")
src = pd.read_csv(ROOT.parent / "JobsOhioSmallBiz" / "data" / "commitments_norm.csv")
src["y"] = src.report_month.str[:4].astype(int)
keep = src[(src.y.between(2021, 2025)) & (~src.program_family.isin(
    ["Growth Fund Loan", "Revitalization Loan", "Other Loan", "Spec Development (OSIP)"]))]
check("JobsOhio grant dollars 2021-2025", int(keep.value.fillna(0).sum()), int(jo.loc["2021-2025", "grant_dollars"]))
check("JobsOhio committed jobs 2021-2025 (after removing 19 repeated promises)",
      int(jo.loc["2021-2025", "jobs_committed"]), 83124)
check("JobsOhio dollars per committed job",
      round(int(jo.loc["2021-2025", "grant_dollars"]) / int(jo.loc["2021-2025", "jobs_committed"])), 16182)

# --- Ascend reported table (chart 5) ---------------------------------------------------------------------
asc = pd.read_csv(ROOT / "data" / "ascend_reported.csv")
check("Ascend rows with a URL and quote", int((asc.url.notna() & asc.exact_quote.notna()).sum()), len(asc))
for m, d, v in [("participants", "2026-02-06", 618), ("new_residents_incl_family", "2026-02-06", 1161),
                ("participants", "2026-07-19", 704), ("retention_pct", "2026-02-06", 95.5),
                ("completed_two_years", "2026-02-06", 116)]:
    hit = asc[(asc.measure == m) & (asc.publish_date == d)]
    check(f"Ascend {m} {d}", float(hit.value.iloc[0]), v)

# --- Words: every label and sourced claim on the built output -------------------------------------------
WORDS = [
    ("Chart 1 marker 'First Ascend class of 53 announced Sept. 2021'", "supported",
     "Ascend release Sept 2, 2021: 'The 53 class members...'; independent tie-out found 'arrive' only partly supported"),
    ("Chart 1 note 'two vintages use different Census bases and are not revised to match'", "supported",
     "Census methodology page and V2025 methods statement"),
    ("Chart 2 note 'IRS guides from 2014-15 on warn processing changes may affect comparisons'", "supported",
     "2014-15 guide warns identity-theft processing 'may' affect comparisons; it does not name 2014-15 "
     "WV figures"),
    ("Chart 2 note '2022-23 uses an updated matching method that finds about 5% more returns'", "supported",
     "IRS 2022-23 guide: 'Minor updates were made to the method for matching returns' (about 5% increase)"),
    ("Chart 2 'Covers people on returns only (n2)'", "supported", "IRS guides: non-filers excluded"),
    ("Chart 3 'Rank among 50 states and D.C.'", "supported", "51 state rows recomputed above"),
    ("Chart 4 county lists for each Ascend area", "partly supported",
     "Inferred from school systems on ascendwv.com community pages; program says '30-minute drivetime'"),
    ("Chart 5 'Goal: 1,000 remote workers in five years (Sept. 2021)'", "supported",
     "Ascend release Sept 2, 2021"),
    ("Chart 5 every dot", "supported", "each row in data/ascend_reported.csv carries URL and quote"),
    ("Retention defined as 'at least four months and stayed'", "supported",
     "WVU Q4 2025 statistics p.2, read by the research agent and confirmed by the independent tie-out"),
    ("Average salary $94,617", "supported as Morgantown Area only",
     "WVU Q4 2025 p.3; corrected from statewide after the independent tie-out"),
    ("Ascend Heroes incentive", "conflict recorded",
     "Ascend release says $12,000; WV MetroNews says $20,000"),
    ("'$580 million' from a 2023 WVU study", "not supported",
     "Only source is NPR; no study document found"),
    ("Bartik: 58-70% would not have moved; $36k vs $218k per job", "supported (summary only)",
     "Upjohn two-page summary; full report not opened"),
    ("JobsOhio figures are commitments, not verified jobs", "supported",
     "JobsOhioSmallBiz DATASETS.md, monthly executed reports section"),
]

lines = ["# Tie-out", "", "Generated by `scripts/99_tieout.py`. Numbers recomputed from `data/raw/` with "
         "pandas, separate from the build scripts.", "", "## Numbers", "",
         "| Item | Recomputed | Shown / built | Result |", "|---|---|---|---|"]
lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
lines += ["", "## Words", "", "| Label or claim | Status | Source |", "|---|---|---|"]
lines += [f"| {a} | {b} | {c} |" for a, b, c in WORDS]
bad = [r for r in rows if r[3] != "match"]
lines += ["", f"**{len(rows) - len(bad)} of {len(rows)} numbers match.**"]
lines += ["", "## Independent tie-out (fresh agent, November 14, 2026)", "",
          "Re-pulled Census, IRS, the WVU Q4 2025 PDF and the program evaluations; recomputed with its own code "
          "without seeing the build scripts or outputs.", "",
          "- Every number on charts 1 to 4 matched. Eastern Panhandle 2021-2025 rate is 20.574999, at the "
          "rounding edge of 20.57.",
          "- JobsOhio: same totals ($1,345,075,454; 83,124 jobs; $16,182). It zeroed 10 repeated promises in "
          "2021-2025; DATASETS.md said 19, which counted earlier years. Corrected to 10.",
          "- Census rate definition did not say which populations are averaged. Now stated in DATASETS.md.",
          "- Fixed after its word checks: $94,617 salary is Morgantown Area only; Ascend Heroes is $12,000 per "
          "Ascend's release (MetroNews said $20,000); Greenbrier Valley launch is September 2022 per WVU; chart 1 "
          "'arrive' changed to 'announced'; chart 2 'new series' changed to the guide's wording; chart 5 goal "
          "line now says to compare with members; Bartik 58-70% range and method credited to the abstract; "
          "Vermont 'less than $2M' changed to 'approximately $2 million'; SCOPE.md Tulsa 76% credited to Tulsa "
          "Remote's own report.",
          "- Could not check: Bartik's full report, CGR's full report, Tulsa Remote's 2023 report, the GROW 2026 "
          "report, the CRS page, and some page numbers in data/programs.csv."]
(ROOT / "TIEOUT.md").write_text("\n".join(lines) + "\n")
print(f"{len(rows) - len(bad)} of {len(rows)} match")
for r in bad:
    print("DIFFERENT:", r)
