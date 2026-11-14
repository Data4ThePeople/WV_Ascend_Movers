# Scope and requirements (initial)

Project: WV_Ascend_Movers
Opened: November 14, 2026
Process: `~/.claude/d4tp-process/PROCESS.md` (this project is in Step 1, not yet opened with `/step 1`)
Series: Data 4 Thought, written as a contrast to the JobsOhio work in `~/PycharmProjects/JobsOhioSmallBiz`

---

## The idea

JobsOhio pays large companies to expand or locate in Ohio. Ascend West Virginia
pays individual remote workers to move to West Virginia. The post compares the
two approaches: what each one costs, what each one promises, what each one can
show it delivered, and how good that evidence is. It also looks at other places
that have paid people to move, and whether any of them can show more people
moved in because of it.

## The program

**Ascend West Virginia** (ascendwv.com), launched April 12, 2021. Run by the
WVU Brad and Alys Smith Outdoor Economic Development Collaborative, with the
state Department of Tourism. Funded mainly by a $25 million gift from Brad and
Alys Smith. The original offer was $10,000 over the first 12 months plus $2,000
for staying a second year, plus outdoor recreation perks. The Charleston offer
(2025) is reported at more than $20,000 in total incentives.

Communities, in order of launch (county mapping still to confirm):

| Community | Likely county or counties | Launched |
|---|---|---|
| Morgantown | Monongalia | 2021 |
| Greenbrier Valley (Lewisburg) | Greenbrier | 2021 |
| Eastern Panhandle (Shepherdstown) | Jefferson, maybe Berkeley | 2021 |
| Greater Elkins | Randolph | November 2022 |
| New River Gorge | Fayette, maybe Raleigh | 2023 |
| Charleston | Kanawha | September 2025 |

A sister program, First Ascent, targets graduates and partners with Huntington.
Some reported totals combine the two programs.

## What the program itself reports (not independently checked)

These numbers come from the program, WVU, or press coverage quoting them. They
conflict with each other, and the post has to say so.

| Measure | Reported values | Sources |
|---|---|---|
| Participants (workers) | 509 (2023), 300+ (2024), 704 (July 2026), "more than 700" (NPR, July 2026) | WV MetroNews 7/19/2026; NPR 7/24/2026 |
| New residents incl. family | 951 (2023), 1,400+ (WVU, May 2026), 1,500+ (Michigan Public, July 2026) | WVU Today 5/5/2026; Michigan Public 7/24/2026 |
| Applications | 65,000 (2023), about 88,000 (2026) | NPR 7/24/2026 |
| Retention | 98% (early), 96%, 96.2%, 96.4% | WVU, WCHS, MetroNews |
| Economic impact | $500 million; $580 million (2023 WVU study) | WV Press Association; Michigan Public |
| Bought or built a home | 41% of participants | WV MetroNews 7/19/2026 |

Open questions on these: how "retention" is defined (still in the state at the
end of the two-year commitment, or completed the program), what the economic
impact study counts, and whether "participants" means workers or households.

## Comparison programs found so far

| Program | Type | Best evaluation found | What it found |
|---|---|---|---|
| Tulsa Remote (Tulsa, OK, 2018) | $10,000 to remote workers, city level, privately funded | Bartik, Upjohn Institute (2025); EIG (2021, 2023) | Bartik: 58% to 70% of movers would not have come without the grant; about $36,000 per job versus about $218,000 for typical business incentives; benefits about 4.3 times costs, under Tulsa's housing conditions. Retention 76% (Tulsa Remote's own 2023 report, end of 2022) to 80% (program, 2025) |
| Vermont remote and new worker grants (2018, 2019) | State grants to new workers | Vermont DFR report to the legislature (January 2022) | Very high returns per dollar ($93.88 and $66.26), based on participant surveys; the consultant called this the high end. Most recipients said the grant was not the deciding factor |
| Kansas Rural Opportunity Zones (2011/2012) | State income tax waiver and student loan repayment, rural counties | Kansas Legislative Post Audit (August 2023); Kansas Commerce evaluation (2020) | Did little to slow rural population loss despite $27.1 million spent; most participants would have moved anyway |
| Choose Topeka, Remote Shoals (AL) | City or regional relocation grants | CGR comparative evaluation; CRS Insight IN12472 (2024) | Positive returns mainly at scale; incentive is not the only factor. CRS calls the value of relocation incentives questionable |

Still to check: Northwest Arkansas "Life Works Here," Opportunity Maine
student loan tax credit, Alaska and other state-level programs, Make My Move
listings, and whether any state (not city) program has an evaluation that
compares movers to a control group.

## Statewide context

Census Vintage 2025 estimates put West Virginia's net domestic migration at
about +6,408 for July 2024 to July 2025, up from about +3,348 (2022 to 2023)
and +4,312 (2023 to 2024). The state still lost population because deaths
outnumbered births. These are third-party reproductions of Census tables and
must be pulled from Census directly before use.

## What the data can and cannot support (initial read)

- **No public participant-level data.** Every Ascend outcome number is
  program-reported. We cannot recompute retention, cost per mover, or impact
  without data from WVU.
- **Ascend is small next to statewide flows.** Even 1,500 residents over five
  years is small against net domestic migration of several thousand a year,
  and net migration is not the same as gross arrivals. The post cannot say
  Ascend drove West Virginia's migration gains, and should not imply it.
- **The strongest evidence on the approach is Tulsa**, where Bartik compared
  approved and unapproved applicants. There is no similar study for Ascend
  that we have found.
- **The JobsOhio side is well documented** in the JobsOhioSmallBiz project
  (Form 990 Schedule I grants, monthly executed grants and loans reports,
  commitments). That gives a cost per committed job we can compute ourselves.

## Research questions

1. What does Ascend cost per participant and per household, all in? (Needs
   total program spending, which is not public yet.)
2. How many people has Ascend moved, by year and by community?
3. What does "96% retention" measure, and how does it compare with Tulsa's
   76% to 80%?
4. What did net domestic migration do in Ascend counties before and after
   2021, compared with similar non-Ascend counties? Descriptive only.
5. What does JobsOhio pay per committed job, and how many committed jobs
   showed up? (From the JobsOhioSmallBiz data.)
6. Across all programs found, which ones have an evaluation that asks whether
   people would have moved anyway, and what did it find?

## Candidate data sources

| Source | Use | Access |
|---|---|---|
| Census Population Estimates, components of change, state and county, Vintage 2025 (and 2010s vintages) | Net domestic migration, WV and counties | Public API / CSV |
| IRS SOI state-to-state and county-to-county migration files | Gross inflows and outflows, incomes of movers | Public CSV |
| ACS 1-year state-to-state migration flows | Where movers come from | Public |
| Ascend WV / WVU OEDC releases and press coverage | Program-reported counts, retention, impact | Public, conflicting |
| WVU 2023 Ascend economic impact study | Method behind the $580 million claim | Need to obtain |
| WV state budget, Tourism and WVU appropriations | Any public money in Ascend | Public, to search |
| Bartik (Upjohn 2025), EIG Tulsa reports, Tulsa Remote 2025 impact report | Tulsa evidence | Public PDFs |
| Vermont DFR 2022 report | Vermont evidence | Public PDF |
| Kansas LPA 2023 audit; Kansas Commerce 2020 ROZ evaluation | Kansas evidence | Public PDFs |
| CGR comparative evaluation; CRS IN12472 | Cross-program evidence | Public |
| JobsOhioSmallBiz project data (Form 990 Schedule I, executed grants reports, JobsOhio annual reports) | JobsOhio cost per committed job | Already pulled in that project |

## Recommended first move on data

Ask WVU for the numbers we cannot compute: participants and households by
year and community, the retention definition, total program spending by
year, and a copy of the 2023 impact study. The contact is the WVU Outdoor
Economic Development Collaborative (Danny Twilley is the official quoted in
the July 2026 coverage). Without that, the post rests on program-reported
figures, and it has to say so plainly.

## Requirements

- Follow `PROCESS.md`. Run `/step 1` to create `STATUS.md` before work starts.
- Write `DATASETS.md` before any analysis, one section per dataset.
- Every program-reported figure is labeled as program-reported in charts and
  text. Conflicting figures are shown, not averaged or picked.
- No causal claims about Ascend and migration. Describe sequence and size.
- Cost comparisons use the same unit on both sides (per committed job, per
  participant, per household) and say what each unit counts.
- Comparison programs are described from their evaluations, not their
  marketing.
- Charts follow the house conventions: titled, dark palette for static PNGs,
  vanilla JS for any interactive, "Built by Data 4 The People."
- Claude's tie-out and the independent fresh-agent tie-out before Step 1
  closes, checking words as well as numbers.
- No political commentary. The comparison is between two economic development
  approaches, not between parties, governors, or donors.
- Repo, when created, goes under `Data4ThePeople` with a `README.md`.

## Timeline

Eric plans to write the week of November 16, 2026. Step 1 needs: Census and
IRS migration pulls, the comparison table sourced from primary documents, the
JobsOhio cost per committed job from the existing project, and whatever WVU
sends back.
