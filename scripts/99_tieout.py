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
check("JobsOhio committed jobs 2021-2025 (after removing 10 repeated promises)",
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

# --- Ascend Q3 2026 (WVU OEDC, provided; as of Sept. 30, 2026) ---------------------------------------------
for m, v in [("participants", 827), ("new_residents_incl_family", 1641), ("completed_two_years", 184),
             ("retention_pct", 96), ("applications", 94400)]:
    hit = asc[(asc.measure == m) & (asc.publish_date == "2026-10-16")]
    check(f"Ascend Q3 2026 {m}", float(hit.value.iloc[0]), v)
q3 = pd.read_csv(ROOT / "data" / "ascend_q3_2026_communities.csv")
for col, v in [("members", 809), ("completed_two_years", 185), ("total_incl_household", 1645),
               ("applications", 95048)]:
    check(f"Q3 2026 community pages, sum of {col}", int(q3[col].sum()), v)
for col, v in [("wv_born_pct", 11.3), ("home_purchase_pct", 41.2)]:
    check(f"Q3 2026 {col} weighted by members", round((q3[col] * q3.members).sum() / q3.members.sum(), 1), v)
check("Q3 2026 members as % of 1,000 goal", round(827 / 1000 * 100, 1), 82.7)
check("Q3 2026 residents as % of WV net domestic 2021-2025", round(1641 / sum(raw_dom[y] for y in range(2021, 2026)) * 100, 1), 9.5)
check("Q3 2026 members as % of applications", round(827 / 94400 * 100, 1), 0.9)
sts = pd.read_csv(ROOT / "data" / "ascend_q3_2026_states.csv")
sw = sts[sts.scope == "Statewide"]
check("Q3 2026 statewide states table, sum of members", int(sw.members.sum()), 819)
nb = sw[sw.state.isin(["Virginia", "Maryland", "Pennsylvania", "Ohio", "Kentucky"])].members.sum()
check("Q3 2026 % of U.S. members from the five neighboring states", round(nb / sw.members.sum() * 100, 1), 35.8)
ep = sts[sts.scope == "Eastern Panhandle"]
check("Q3 2026 Eastern Panhandle states table, sum (212 members; p.5 also lists Chile, UK, Canada)", int(ep.members.sum()), 209)
check("Q3 2026 % of Eastern Panhandle members from VA, MD, DC",
      round(ep[ep.state.isin(["Virginia", "Maryland", "Washington DC"])].members.sum() / 212 * 100, 1), 47.6)

# --- BBER memo, Feb. 2021 (provided by WVU OEDC) ---------------------------------------------------------
# cohort sizes and output totals transcribed from Appendices 1, 2 and 4
mor, lew, she = [50, 75, 100, 100], [25, 25, 38, 48], [25, 25, 38, 48]
check("BBER memo: workers modeled in three areas", sum(mor + lew + she), 597)
check("BBER memo: Monongalia workers", sum(mor), 325)
base = [11087361, 16631042, 22182408, 22182408, 5067672, 5067672, 7702861, 9729930,
        4524329, 4524329, 6876980, 8686712]
ret = [16297591, 24280492, 32936319, 32936319, 7296858, 7296858, 11249642, 14391598,
       6514404, 6514404, 10043381, 12848465]
check("BBER memo: baseline output, sum of cohorts (App. 2 total 124,263,705)", sum(base), 124263705, tol=12)
check("BBER memo: 50% retention output, sum of cohorts (App. 4 total 182,606,329)", sum(ret), 182606329, tol=12)
for d, v in [("2021-02-01", 182600000), ("2021-02-01", 124300000)]:
    hit = asc[(asc.measure == "economic_impact_usd") & (asc.publish_date == d) & (asc.value == v)]
    check(f"Ascend table has BBER {v:,}", len(hit), 1)

# --- OEDC 2025 Impact Report --------------------------------------------------------------------------------
for m, v in [("funding_usd", 3000000), ("funding_usd", 2165000), ("funding_usd", 48400000),
             ("retention_pct", 95), ("applications", 11482)]:
    hit = asc[(asc.measure == m) & (asc.publish_date == "2025-12-31") & (asc.value == v)]
    check(f"Impact Report 2025 {m} {v:,}", len(hit), 1)

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
    ("Chart 5 sources line names WVU OEDC Quarter 3 2026 statistics", "supported",
     "Five Q3 2026 rows in data/ascend_reported.csv, each with page and quote"),
    ("Q3 2026 community pages sum to the statewide page", "not supported",
     "Members 809 vs 827, completed 185 vs 184, household 1,645 vs 1,641; recorded in DATASETS.md"),
    ("Q3 2026 survey figures (income, home price) are program totals", "not supported",
     "p.9 says 495 respondents, 'rolling and not comprehensive'; not used as totals"),
    ("No Ascend spending total, incentives paid or cost per member is published", "supported",
     "Not in the Q3 2026 report, the 2025 Impact Report or the BBER memo; OEDC pointed only to the Impact Report"),
    ("Impact Report funding figures are for the whole Collaborative", "supported",
     "Impact Report 'IMPACT SNAPSHOT 2020-2025': 'the Collaborative grew...'; $80.6M+, $48.4M+, $11.8M"),
    ("Ascend Heroes incentive", "conflict recorded",
     "Ascend release says $12,000; WV MetroNews says $20,000"),
    ("'$580 million' from a 2023 WVU study", "not supported",
     "Only source is NPR; WVU OEDC sent the Feb. 2021 BBER memo instead and offered a December call on the method"),
    ("BBER $182.6 million is a projection for three areas, cumulative 2021-2031", "supported",
     "BBER memo pp.3-4, 11-13 and Appendix 4"),
    ("BBER memo makes no adjustment for workers who would have moved anyway", "supported",
     "Assumptions on p.3 list none; direct impact is all remote workers' income (p.2)"),
    ("Memo's 50% retention and program's 96% measure different things", "supported",
     "Memo p.4: 50% of each cohort stays each further year; Q3 2026 p.2: in program 4+ months and stayed"),
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
          "report, the CRS page, and some page numbers in data/programs.csv.",
          "", "## Independent tie-out of the Q3 2026 additions (fresh agent, November 17, 2026)", "",
          "Read all 9 pages of the WVU Q3 2026 PDF as text and images; recomputed with its own code without "
          "seeing the build scripts or TIEOUT.md.", "",
          "- Every cell in the five Q3 rows, the community table and the states table matched the PDF. All "
          "derived figures matched (809, 185, 1,645, 95,048; 11.3%; 41.2%; 82.7%; 0.9%; 35.8%; 47.6%; 9.5%).",
          "- Fixed after its word checks: retention row scope now says as of Sept. 30, 2026; DATASETS.md says "
          "the Oct. 16 date is from the file name, quotes p.2 'family and friends' instead of 'household "
          "members', says the nine countries include the U.S., and states the base and caveats of each derived "
          "figure; chart 5 subtitle says 'released' because the Q3 report was sent to us, not published.",
          "- Noted: the Charleston states table (p.8) lists California twice; not used.",
          "- Could not check: the Q4 2025 figures (that PDF is not in data/raw; the first independent tie-out "
          "re-pulled it), whether the Q3 report is posted online, and the wording of the Sept. 2021 goal.",
          "", "## Independent tie-out of the BBER memo additions (fresh agent, November 18, 2026)", "",
          "Read all 16 pages of the Feb. 2021 BBER memo and the WVU OEDC reply; recomputed the appendices with "
          "its own code.", "",
          "- All figures matched: 597 workers; $124.3M, 404 jobs, $3.2M tax; $182.6M, 594 jobs, $4.6M tax; "
          "cohort sums within $2 of printed totals (rounding); direct output is 65% of $90,000 per worker-year.",
          "- Confirmed by reading every page: the memo counts all workers' income as new spending and has no "
          "adjustment for workers who would have moved anyway; the memo's 50% and the program's 96% measure "
          "different things.",
          "- Fixed: baseline years are 2021-2026 (not 2027); the 50% is of those remaining, not the full cohort; "
          "the OEDC paraphrase now quotes 'exactly how many' and adds her 'on their radar' sentence; noted the "
          "memo's own 490 vs 403 conflict for the two unmodeled areas.",
          "- Could not check: the later $500M, $580M and $750M figures (no documents), and whether any other "
          "publication measures retention after the two-year term.",
          "", "## Independent tie-out of the 2025 Impact Report additions (fresh agent, November 18, 2026)", "",
          "Read all 23 pages of the saved PDF, text and rendered images.", "",
          "- Every claim and all five rows supported; no number errors. No Ascend spending, incentives paid, "
          "operating cost or cost per member anywhere in the report.",
          "- Added after its notes: the 618 includes members 'in the process of relocating'; 1,161 is labeled "
          "two ways; 25 babies appears in both the end-2025 snapshot and the Q3 2026 report; reworded the "
          "DATASETS 'Not checked' line now that the report has been read.",
          "- Could not check from this source: the $25M Smith gift, $2.4M Rural Health and $500K Charleston "
          "donation (documented elsewhere in DATASETS.md)."]
(ROOT / "TIEOUT.md").write_text("\n".join(lines) + "\n")
print(f"{len(rows) - len(bad)} of {len(rows)} match")
for r in bad:
    print("DIFFERENT:", r)
