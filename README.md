# WV_Ascend_Movers

Data 4 The People project, in progress. It looks at Ascend West Virginia, a
program that pays remote workers to move to West Virginia, and compares that
approach with JobsOhio's grants to companies. It also looks at other places
that have paid people to move and what their evaluations found.

No post or visualization is published yet. Links will be added here when they
are.

## What's in the repo

- `DATASETS.md`: every dataset, how it is built, its limits and known conflicts
- `TIEOUT.md`: every charted number recomputed from the raw files
- `scripts/`: numbered build scripts, run in order
- `data/ascend_reported.csv`: each published Ascend WV figure with its source and exact words
- `data/ascend_communities.csv`: Ascend host areas and the counties they cover
- `data/programs.csv`: other pay-to-move programs and what their evaluations found
- `data/processed/`: outputs of the scripts
- `charts/`: static charts
- `SCOPE.md`, `STATUS.md`: project scope and where it stands in the publishing process

## Data sources

- U.S. Census Bureau, Population Estimates, components of change, Vintage 2020
  and Vintage 2025
- IRS Statistics of Income, U.S. Population Migration Data, 2011-12 to 2022-23
- JobsOhio monthly executed grants and loans reports, as parsed in the
  [JobsOhioSmallBiz](https://github.com/Data4ThePeople/JobsOhioSmallBiz) project
- Ascend WV and WVU releases and statistics, and news reports quoting them
- Published evaluations of other programs, listed in `data/programs.csv`

## How to rebuild

Python 3 with pandas and matplotlib. Census and IRS files download on the
first run into `data/raw/` (not committed). Script 05 reads
`../JobsOhioSmallBiz/data/commitments_norm.csv`, so that repo must sit beside
this one.

```
cd scripts
python3 01_fetch_popest.py
python3 02_fetch_irs_migration.py
python3 03_ascend_reported.py
python3 04_county_compare.py
python3 05_jobsohio_per_job.py
python3 06_charts.py
python3 99_tieout.py
```

## Method notes

- Census domestic migration is modeled from tax, Medicare and Social Security
  records, not counted. The 2010s and 2020s files use different Census bases.
- Every Ascend WV figure is reported by the program or by news stories quoting
  it. There is no public participant-level data, so none of it is recomputed.
- JobsOhio figures are jobs promised and dollars agreed at signing, not jobs
  verified or dollars paid.
