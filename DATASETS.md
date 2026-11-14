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
domestic migration summed over the period, divided by average population over
the period, divided by the number of years.

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
- **2022-23 is a new series.** A new matching method added about 5% more
  returns. 2022-23 is not directly comparable with earlier years.
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
  (checked back to 2015), the later agreement counts zero new jobs. 19
  agreements in 2021-2025 are treated this way, including Intel's December
  2022 workforce grant, which repeats the 3,000 jobs on its July 2022 grant.
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

## Comparison programs and Ascend WV figures

Sections to come once the primary documents are read: Ascend WV
program-reported figures and communities; Tulsa Remote (Bartik 2025, EIG);
Vermont worker grants (DFR 2022); Kansas Rural Opportunity Zones (LPA 2023,
Commerce 2020); Choose Topeka and Remote Shoals (CGR); CRS IN12472.
