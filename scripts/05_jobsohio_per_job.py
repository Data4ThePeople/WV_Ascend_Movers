"""JobsOhio incentive dollars per committed new job, from the executed-agreements data parsed in the
JobsOhioSmallBiz project (data/commitments_norm.csv, built by that project's scripts 03 and 04).

These are commitments at signing: the jobs a company promised and the incentive JobsOhio agreed to.
They are not jobs verified later or dollars actually paid.

A project that combined two programs (for example a workforce grant and an economic development grant)
appears as one row per program. Jobs are counted once per project (month, company, county); dollars
are summed across its programs.

A company that signs a second agreement for the same project often restates the same job promise
(Intel's 3,000 jobs appear on a July 2022 grant and a December 2022 workforce grant). When the same
company and county show the same job count in more than one month, the jobs count once, in the first month.

Grants only: loans (Growth Fund, Revitalization Loan, Other Loan) are repaid and are left out, and so are
site grants (Spec Development / OSIP), which promise no jobs.
"""
import collections
import csv
import datetime as dt
from pathlib import Path

from common import write_csv

SRC = Path.home() / "PycharmProjects" / "JobsOhioSmallBiz" / "data" / "commitments_norm.csv"
EXCLUDE = {"Growth Fund Loan", "Revitalization Loan", "Other Loan", "Spec Development (OSIP)"}
YEARS = range(2021, 2026)   # the years Ascend WV has run, full calendar years only


def main():
    projects = collections.defaultdict(lambda: {"dollars": 0, "jobs": set(), "programs": set()})
    skipped = collections.Counter()
    for r in csv.DictReader(open(SRC)):
        year = int(r["report_month"][:4])
        if r["program_family"] in EXCLUDE:
            if year in YEARS:
                skipped[r["program_family"]] += 1
            continue
        key = (r["report_month"], r["company_norm"] or r["company"], r["county"])
        p = projects[key]
        p["dollars"] += int(r["value"] or 0)
        p["programs"].add(r["program_family"])
        if r["jobs_created_n"] not in ("", None):
            p["jobs"].add(int(float(r["jobs_created_n"])))
        p["year"] = year

    # restated promises: same company, county and job count in a later month count zero new jobs
    first = {}
    restated = 0
    # promises from 2015 on are checked, so a 2021 agreement restating a 2019 promise is caught
    for key in sorted(projects, key=lambda k: dt.datetime.strptime(k[0], "%Y-%b")):
        p = projects[key]
        jobs = max(p["jobs"]) if p["jobs"] else 0
        tag = (key[1], key[2], jobs)
        if jobs and key[1] and tag in first:
            p["jobs"] = {0}
            p["restated_from"] = first[tag]
            restated += 1
        elif jobs:
            first[tag] = key[0]

    rows, conflicts = [], 0
    by_year = collections.defaultdict(lambda: [0, 0, 0, 0])   # projects, dollars, jobs, projects with 0 jobs
    for key, p in projects.items():
        if p["year"] not in YEARS:
            continue
        if len(p["jobs"]) > 1:
            conflicts += 1          # same project, different job counts on two program lines
        jobs = max(p["jobs"]) if p["jobs"] else 0
        y = by_year[p["year"]]
        y[0] += 1
        y[1] += p["dollars"]
        y[2] += jobs
        y[3] += jobs == 0
        rows.append([p["year"], key[0], key[1], key[2], "; ".join(sorted(p["programs"])), p["dollars"], jobs,
                     p.get("restated_from", "")])

    write_csv("jobsohio_projects_2021_2025.csv",
              ["year", "report_month", "company", "county", "programs", "grant_dollars", "jobs_committed",
               "jobs_restated_from_month"], sorted(rows))
    out = []
    tot = [0, 0, 0, 0]
    for year in YEARS:
        y = by_year[year]
        tot = [a + b for a, b in zip(tot, y)]
        out.append([year, y[0], y[1], y[2], y[3], round(y[1] / y[2]) if y[2] else ""])
    out.append(["2021-2025", tot[0], tot[1], tot[2], tot[3], round(tot[1] / tot[2])])
    write_csv("jobsohio_per_job.csv", ["year", "projects", "grant_dollars", "jobs_committed",
                                       "projects_with_no_new_jobs", "dollars_per_committed_job"], out)
    print("left out:", dict(skipped))
    print("agreements whose job promise repeats an earlier one (jobs set to 0):", restated)
    print("projects whose program lines disagree on jobs (max used):", conflicts)
    for o in out:
        print(o)


if __name__ == "__main__":
    main()
