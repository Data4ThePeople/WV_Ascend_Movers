# Datasets

One section per dataset. Written before the post, updated whenever we learn
something new. Sources for every statement are linked in the section.

---

## Census Population Estimates, components of change, states and counties (U.S. Census Bureau)

**What it is.** One row per state or county, with yearly columns for July 1
population and the parts of each year's change: births, deaths, natural change,
net international migration, net domestic migration, net migration and a
residual. Each year runs July 1 to June 30 and is labeled by the year it ends.

**Where it comes from.**
`co-est2020-alldata.csv` (Vintage 2020, years ending 2011 to 2020) and
`co-est2025-alldata.csv` (Vintage 2025, years ending 2021 to 2025), both under
`https://www2.census.gov/programs-surveys/popest/datasets/`. Pulled by
`scripts/01_fetch_popest.py`, cached in `data/raw/popest/`.

**Version and vintage.** Vintage 2020 county file released May 2021. Vintage
2025 released March 2026; its release notes were updated May 14, 2026. Each new
vintage revises every year back to the last census and replaces the one before.
We use the latest vintage for each decade.

**How domestic migration is estimated.** It is a model, not a count. The
Bureau computes migration rates from IRS tax returns (ages 0 to 64), Medicare
enrollment (65 and older), Social Security records (for age) and changes in
group quarters. It uses rates rather than the raw flows because not everyone
files taxes, then applies the rates to the estimated population and forces the
national total to zero.
([V2025 methods](https://www2.census.gov/programs-surveys/popest/technical-documentation/methodology/2020-2025/methods-statement-v2025.pdf),
[V2020 methods](https://www2.census.gov/programs-surveys/popest/technical-documentation/methodology/2010-2020/methods-statement-v2020-final.pdf))

**Coverage.** All 50 states, D.C., and all 55 West Virginia counties. Every
value is modeled; no year is a direct count.

**Changes over time.**
- The two vintages are not one series. Vintage 2020 starts from the 2010
  Census; Vintage 2025 starts from the 2020 Census. They are not revised to
  match each other, and the Bureau publishes no intercensal components for
  2010 to 2020. Charts that span 2011 to 2025 say so.
- The year ending July 1, 2020 straddles the start of the pandemic and is the
  last year of the older vintage. Period averages leave it out.
- Vintage 2025, year ending 2025 only: Medicare data for 2024-25 was not
  received, so migration rates for people 65 and older reuse 2023-24. For ages
  0 to 64, only a partial (26-week) IRS file came in and was combined with the
  prior year's full file.
  ([2025 release notes](https://www2.census.gov/programs-surveys/popest/technical-documentation/methodology/2020-2025/2025-est-relnotes.pdf))
- Vintage 2024 and 2025 raised net international migration for 2021 to 2024.
  This does not change domestic migration but does change net migration.
- Column names: the 2010s file calls natural change `NATURALINC`, the 2020s
  file `NATURALCHG`. The script handles both.

**Suppressed, censored or masked values.** None.

**Missing data.** None in the rows we use.

**Revisions.** Every new vintage revises the whole decade. We pin Vintage 2020
and Vintage 2025 and record the pull date in `data/raw/popest/pulled.txt`.

**Units and rounding.** People. Rates per 1,000 are our calculation: net
domestic migration summed over the period, divided by the average of the July 1
populations of the years in the period (for 2015-2019, July 1 of 2015 through
2019; the July 1, 2014 starting population is not included), divided by the
number of years. Adding the starting population moves West Virginia's change
from +6.34 to +6.32.

**Known quirks.** The `RESIDUAL` column is the part of the change the
components do not explain, created when county and state estimates are forced
to add up. National estimates have none. Both files repeat a state's code on
its state row, so the duplicate-key check uses state and county together.

**Uncertainty.** The Bureau publishes no error measure for the components. The
only accuracy figure found: 2010-2020 county totals were off from the 2020
Census by a mean absolute 2.9%.

**License and attribution.** No license statement found. The Bureau asks
users to cite it. Cite as "U.S. Census Bureau, Population Estimates Program,
Vintage 2020 and Vintage 2025."

---

## IRS Statistics of Income, U.S. Population Migration Data, state-to-state (IRS)

**What it is.** Federal tax returns matched across two filing years by
taxpayer ID, comparing mailing addresses. Inflow rows count returns that moved
into a state; outflow rows count returns that moved out. `n1` = returns
(roughly households), `n2` = people on those returns, `AGI` = adjusted gross
income in thousands of dollars, from the year-2 return.

**Where it comes from.** `https://www.irs.gov/pub/irs-soi/stateinflowYYZZ.csv`
and `stateoutflowYYZZ.csv`, 2011-12 to 2022-23. Pulled by
`scripts/02_fetch_irs_migration.py`, cached in `data/raw/irs/`. Rows used: code
97 (U.S. total), 96 (U.S. and foreign), 98 (foreign).
([2022-23 guide](https://www.irs.gov/pub/irs-soi/2223inpublicmigdoc.pdf))

**Version and vintage.** Latest year 2022-23, released March 19, 2026. No date
announced for 2023-24.

**Coverage.** Tax filers only. People who do not file, file late, switch
between ITIN and SSN, or are claimed as dependents in year 2 are left out. The
IRS publishes no share of the population covered. Since 2011-12 the full
calendar year of filings is used.

**Changes over time.**
- `n2` meant "exemptions" through 2018-19 and "individuals" from 2019-20, when
  exemptions were phased out. The column name did not change.
  ([2019-20 guide](https://www.irs.gov/pub/irs-soi/1920inpublicmigdoc.pdf))
- 2019-20 added returns filed only to get Economic Impact Payments.
- **2022-23 uses an updated matching method.** The guide says "minor
  updates" to matching gave about a 5% increase in matched returns. Compare
  2022-23 with earlier years with that in mind.
- Some years use capitalized headers; the script lowercases them.

**Suppressed, censored or masked values.** State cells under 10 returns are
suppressed (`-1`). None of the West Virginia total rows we use are suppressed.

**Missing data.** None in the rows used.

**Revisions.** 2013-14 was reissued in March 2016 for geocoding errors. 2020-21
was revised in June 2023 for a programming error. We use the files as posted
on the pull date.

**Units and rounding.** Returns and people as integers; AGI in thousands of
dollars.

**Known quirks.**
- Code 97 is used both for "Total Migration-US" and "Total Migration-Same
  State" (people who did not move between states). The two rows differ only by
  name. The script drops the "Same State" row.
- **2014-15**: West Virginia arrivals fall to 23,428 from 32,962, and
  departures to 26,574 from 36,684, then rebound. The IRS gives no reason
  specific to the state. Its 2014-15 guide warns that identity-theft
  processing changes "may" affect comparisons across years
  ([2014-15 guide](https://www.irs.gov/pub/irs-soi/1415inpublicmigdoc.pdf)).
  We treat 2014-15 and the 2016-17 spike as possible processing effects, not
  real swings.

**Uncertainty.** None published.

**License and attribution.** IRS public data. Cite as "IRS Statistics of
Income, U.S. Population Migration Data."

---

## JobsOhio executed grant agreements, 2021-2025 (JobsOhio, parsed in the JobsOhioSmallBiz project)

**What it is.** One row per executed incentive agreement and program, from
JobsOhio's monthly executed grants and loans reports: company, county, jobs
promised, payroll, investment, program and dollar value. These are promises
at signing, not jobs verified later or dollars actually paid.

**Where it comes from.** `~/PycharmProjects/JobsOhioSmallBiz/data/commitments_norm.csv`,
built by that project's scripts 03 and 04. The full description, layout
changes and parse checks are in that project's `DATASETS.md`, section
"JobsOhio Monthly Executed Grants and Loans Reports."

**How we use it.** `scripts/05_jobsohio_per_job.py`:
- Calendar years 2021 to 2025, the years Ascend WV has run.
- Grants only. Loans (Growth Fund, Revitalization Loan, Other Loan) are left
  out because they are repaid. Site grants (Spec Development / OSIP) are left
  out because they promise no jobs.
- A project with two programs in one month has one row per program; jobs count
  once per project (month, company, county) and dollars are summed.
- A company that signs a second agreement often repeats the same job promise.
  When the same company and county show the same job count in a later month
  (checked back to 2015), the later agreement counts zero new jobs. Only
  agreements with a nonzero job count and a company name are matched, and only
  against earlier grant rows (not loans or site grants). 10 agreements in
  2021-2025 are treated this way, including Intel's December 2022 workforce
  grant, which repeats the 3,000 jobs on its July 2022 grant.
- Rows with an empty company name (a known parse defect) share a blank key, so
  empty-name rows in the same month and county merge into one project. Their
  dollars count; their jobs count once.
- Result for 2021-2025: $1,345,075,454 in grants for 83,124 committed new
  jobs, $16,182 per committed job. Rows the parser labels "Unknown" (29) are
  included as grants; leaving them out gives $16,172.
- Result: grant dollars divided by committed new jobs. Retained jobs are not
  counted.

**Known quirks that touch these years.** That project's `DATASETS.md` lists
three parse defects found November 13, 2026. Two touch 2021 to 2025: about 24
company names truncated or empty (one empty-name $10,125,000 workforce grant
in January 2023 with zero jobs is in our total), and a one-row shift on the
June 2023 page. The November 2016 gap is outside our years but affects the
restated-promise check for that month.

**What this is not.** Dollars per committed job is a gross figure. It does not
say how many of those jobs would have come to Ohio without the grant.

---

## Relocation program evaluations (various publishers), `data/programs.csv`

**What it is.** A hand-built table: one row per program and evaluation, with
level, funder, incentive, years, spending, movers, evaluator, whether the
evaluation tried to estimate how many people would have moved anyway (and
how), its headline finding, retention as defined by that source, and the URL
and page of the primary document. Built from the documents themselves, not
press coverage, except where a row says "per CRS."

**Sources.**
- Tulsa Remote: Bartik, Upjohn Institute Technical Report 25-050, May 2025
  (summary PDF read; the full report blocks automated download, so page
  numbers refer to the two-page summary); Economic Innovation Group, November
  2021; Tulsa Remote's own 2023 report, which repeats the EIG method and is not
  independent.
- Vermont: Department of Financial Regulation / PFM Group study, December 15,
  2021; Vermont GROW report, July 6, 2026, for the running total.
- Kansas Rural Opportunity Zones: Legislative Division of Post Audit,
  R-23-011, August 2023; Department of Commerce evaluation, 2020.
- Choose Topeka and Remote Shoals: CGR comparative evaluation, January 2021
  (public slides only; the full report is behind a form asking for personal
  details, which we did not fill in).
- Congressional Research Service Insight IN12472, December 19, 2024, for
  program counts where no evaluation exists.

**How the evaluations measure "would have moved anyway."** Only Bartik
compares approved with not-approved applicants. Vermont and Kansas rely on
participant surveys. EIG, CGR and the programs' own reports make no estimate.
A finding from a survey is labeled as one.

**Known conflicts.**
- Vermont 2018 program: $499,940 to 140 grants (PFM) vs $320,834 to 84
  families (GROW 2026, which matches a September 2019 count) vs about $400,000
  to 110 workers (State Auditor 2019, seen in press only).
- Kansas tax-credit totals differ across the 2020 Commerce report, the 2023
  audit and the 2024 Commerce annual report.
- Tulsa retention: 88% and 87.5% (EIG 2021), 76% (Tulsa Remote 2023), 80%
  (Tulsa Remote 2025, survey), each with a different definition. They are
  shown with their definitions, never averaged.

**Not checked.** Bartik's full report (page numbers, retention definition);
CGR's full report; the Vermont State Auditor's 2019 report.

---

## Ascend WV program-reported figures, `data/ascend_reported.csv` and `data/ascend_communities.csv`

**What it is.** One row per figure the program, WVU, or a news story quoting
them published: date, measure, value, unit, scope, source, URL and the exact
words. Checked by `scripts/03_ascend_reported.py` (every row has a source and
quote; no duplicates). Nothing here is recomputed: there is no public
participant-level data.

**The primary statistical sources.** Two WVU OEDC quarterly reports.

- "Ascend WV Program Statistics, Quarterly Report Q3 2026," counts as of
  September 30, 2026. The October 16, 2026 date we use for it comes from the
  file name; the document itself shows only the quarter and the as-of date. WVU OEDC sent it to Data 4 The People
  in November 2026; we did not find it published online, so it is kept in
  `data/raw/wvu/` and not committed. Its URL in `data/ascend_reported.csv` is
  written `provided:<path>`. Statewide (p.2): 827 members since April 2021,
  1,641 new residents ("Many brought family and friends, increasing the total
  to 1641 new West Virginians including 25 babies born during program"), 184 members who completed the two-year program, 96% retention,
  more than 94,400 applications. Pages 3 to 8 give each community's
  applications, members, completions, total with household, average salary,
  share born in West Virginia, and share who bought a home; these are in
  `data/ascend_q3_2026_communities.csv`. Page 9 gives survey results (average
  household income, individual income, home price, rent, demographics) from
  495 respondents; the report calls the survey "rolling and not
  comprehensive." We do not use page 9 figures as program totals.
- "Ascend WV Quarter 4 Statistics," dated February 6, 2026: 618 members,
  1,161 people including households, 116 completed, 95.5% retention, more
  than 79,780 applications, Morgantown Area salary $94,617.

Launch dates (both reports): Morgantown April 2021, Eastern Panhandle June
2022, Greenbrier Valley September 2022, Greater Elkins November 2022, New River
Gorge June 2023, Charleston September 2025.

**Q3 2026 community pages do not add up to the statewide page.** Members: 809
across the six pages, 827 statewide. Completed: 185 vs 184. With household:
1,645 vs 1,641. Applications: 95,048 vs "94,400+", so some applicants are
likely counted in more than one community. The states table on p.2 sums to 819
members; the other 8 may be members who moved from outside the U.S. (the
report lists nine countries), but the report does not say. Its list of nine countries includes the United
States, so eight are other countries. The Eastern Panhandle states table (p.5) sums
to 209 of its 212 members, and that page lists Chile, the United Kingdom and
Canada among the countries members moved from. The Charleston states table (p.8) lists California
twice, at 2 each; we do not use that table. We use the statewide page for
statewide figures and the community pages only for
comparisons between communities. Shares across communities (born in West
Virginia 11.3%, bought a home 41.2%) are our averages of the community
percentages weighted by community members; the report gives no statewide value
for either.

**Derived Q3 2026 figures and their bases.**
- Members as a share of the goal: 827 of the 1,000 remote workers the program
  set as its five-year goal in September 2021 (82.7%).
- Neighboring states: Virginia, Maryland, Pennsylvania, Ohio and Kentucky are
  293 of the 819 members in the p.2 states table (35.8%). That base includes
  Washington, D.C. (11) and leaves out the 8 not in any state row.
- Eastern Panhandle: Virginia, Maryland and D.C. are 101 of its 212 members
  (47.6%); of the 209 in its states table it would be 48.3%.
- Scale: 1,641 new residents equal 9.5% of West Virginia's net domestic
  migration summed over the years ending July 2021 through July 2025 (17,349).
  This is a size comparison only. Ascend's count is gross arrivals and the
  Census figure is net (arrivals minus departures); the periods differ (Ascend
  April 2021 to September 2026, Census July 2020 to July 2025); and the 1,641
  includes 25 babies born in the state (without them, 9.3%). It says nothing
  about how many members would have moved anyway.

**Definitions and conflicts.**
- **Retention.** Both quarterly reports define it as members in the program at
  least four months who stayed. No other source defines it. NPR describes 96%
  as remaining "after the program's two-year commitment ends"; a 2023 release
  says "in first two years"; a 2026 release says "since its launch." Values
  published: 98%, 97%, 96%, 96.2%, 96.4%, 95.5%, "more than 95%".
- **The 2024 figures.** 295 members and 272 family are "as of May 2024" in an
  August 2024 magazine issue.
- **Members vs residents.** "Members" or "participants" are the remote
  workers; "new residents" adds family. Some stories use "individuals" for the
  residents figure.
- **Residents counts do not always rise.** August 2024: 295 members plus 272
  family (567); September 2024: "over 400." September 2025: "nearly 1,000" in
  a subheadline and "more than 900" in the body of the same release. Q4 2025:
  1,161; May 2026: 1,412, with members rising only from 618 to 668. Q3 2026:
  827 members, 1,641 residents.
- **Economic impact.** The only document is a pre-launch projection: WVU
  Bureau of Business and Economic Research, "Memorandum for The Economic Impact
  of Remote Workers in West Virginia," February 2021 (Christiadi and John
  Deskins). WVU OEDC sent it in November 2026; it is kept in `data/raw/wvu/`
  and not committed. (A January 2022 WV Explorer story reported its $182.6
  million figure.) What it is:
  - A projection, not a measurement. It covers 597 planned workers in three
    areas only (Monongalia 325, Greenbrier 136, Jefferson 136), out of a goal
    of 1,000 "in the span of seven years"; the other two planned areas were
    not modeled. (Its text says the other two areas get 490 workers; its own
    Appendix 1 gives them 403, which is what 1,000 minus 597 leaves.)
  - It assumes each worker earns $90,000, spends like a household earning
    $70,000 to $100,000, spends 65% of income, and pays no West Virginia
    income tax.
  - Its figures are "output," cumulative over all years, in 2021 dollars.
    Baseline, every cohort leaves after two years: $124.3 million output, 404
    jobs, $3.2 million state and local tax (2021-2026). With half of those
    remaining staying each additional year after year two: $182.6 million, 594 jobs, $4.6
    million state and local tax (2021-2031). The jobs are all indirect and
    induced; the remote workers themselves count as zero.
  - It counts every worker's spending as new to West Virginia. It makes no
    adjustment for workers who would have moved without the program.
  - WVU OEDC (Emily Huguenin, November 17, 2026) says the memo's retention
    assumption is more conservative than what the program sees. The two are
    measured differently: the memo's 50% is the share of those remaining in
    a cohort who stay each additional year after the two-year term; the program's 96% is the share in the
    program at least four months who stayed. No published figure measures
    retention after the two-year term.
  Later figures: in January 2023 the director said it was too early for a
  dollar figure. Then "$500 million" (2025, 2026), "$580 million" from a "2023
  WVU study" (NPR, July 2026), and "closer to $750 million" (program
  officials, July 2026). No document or method is published for any of these.
  WVU OEDC offered to explain the $580 million method on a call in December
  2026, after our publication date.
- **What the program knows about members who would have moved anyway.** Per
  WVU OEDC (November 17, 2026): it can't track "exactly how many applicants who
  were not selected still moved" to West Virginia, but "we have learned anecdotally that many people
  who applied to Ascend WV ended up making the move regardless of whether they
  were accepted." It adds: "Some have reported that this
  incentive got WV on their radar and caused them to consider moving here."
  This is the program's account, not a count.
- **Money.** WVU OEDC pointed to its 2025 Impact Report for funding
  sources (a web page that blocks automated reading; Eric saved it as a PDF,
  kept in `data/raw/wvu/`). It gives no Ascend spending total, incentives
  paid, operating cost or cost per member. Its funding figures are for the
  whole Collaborative, 2020-2025: more than $80.6 million "in total funding
  initiated," more than $48.4 million "in funding secured," and $11.8 million
  "in match funding generated." The only Ascend-specific amounts: a $3 million
  award for "a five-year partnership supporting the development, launch and
  operation" of Ascend in the Charleston region, and $2.165 million requested
  for Ascend Heroes, pending at the end of 2025. It also describes retention as
  "more than 95% ... staying for the long haul," without a definition; the
  quarterly reports define the rate as at least four months. The $25 million Smith gift went to the Outdoor Economic
  Development Collaborative as a whole, not to Ascend alone. Also found:
  $2.4 million in federal Rural Health Transformation funds for a healthcare
  expansion (September 2026) and a $500,000 private donation for Charleston
  (September 2026). No total program spending, state appropriation, or cost per
  member is published.
- **Incentive.** $12,000 cash paid over 24 months (members who leave early
  keep what they received), with a package the program values at more than
  $20,000 including recreation. Ascend Heroes (veterans, 2026): Ascend's own
  release says $12,000; WV MetroNews reported $20,000. We use the release.

**Communities.** Six areas. Counties are inferred from the school systems each
community page names; the program says each area is "a rough 30-minute
drivetime" from its center city, so county lines are an approximation:
Morgantown (Monongalia), Greenbrier Valley (Greenbrier), Eastern Panhandle
(Jefferson, Berkeley, Morgan), Greater Elkins (Randolph), New River Gorge
(Fayette, Raleigh, Nicholas), Charleston (Kanawha). Dates and URLs in
`data/ascend_communities.csv`.

**Not checked.** WVU Today pages and the OEDC five-year impact report block
automated reading; the same releases were read from ascendwv.com copies. The
NPR story was read from Michigan Public's copy.
