"""Chart 6 (pay per job) and the comparison table image for the heart of the post.
Every number is tied out in 99_tieout.py: Ascend member-weighted salary (Q3 2026 community pages),
JobsOhio committed payroll per committed job 2021-2025 (script 05), BLS OEWS May 2025 means (script 08).
"""
import csv

import matplotlib.pyplot as plt
import pandas as pd

from common import PROC, ROOT
from plot_style import BLUE, GRID, INK, INK_DIM, MUTED, SURFACE, YELLOW, credit, titleblock, use_house_style

CHARTS = ROOT / "charts"


def values():
    q3 = pd.read_csv(ROOT / "data" / "ascend_q3_2026_communities.csv")
    ascend = round((q3.avg_salary_usd * q3.members).sum() / q3.members.sum())
    jo = {r["year"]: r for r in csv.DictReader(open(PROC / "jobsohio_per_job.csv"))}["2021-2025"]
    jobsohio = round(int(jo["committed_new_payroll"]) / int(jo["jobs_with_payroll"]))
    w = pd.read_csv(PROC / "state_wages_oews.csv")
    mean = {r.state: r.usd for r in w[w.measure == "annual_mean"].itertuples()}
    return ascend, jobsohio, mean["West Virginia"], mean["Ohio"]


def chart_pay():
    ascend, jobsohio, wv, oh = values()
    rows = [("Ascend members, average salary", "Pay of jobs members already have", ascend, "solid", BLUE),
            ("JobsOhio grants, payroll per job", "Pay promised for jobs not yet created", jobsohio, "hatch", YELLOW),
            ("Ohio, average wage", "All jobs in the state", oh, "bench", MUTED),
            ("West Virginia, average wage", "All jobs in the state", wv, "bench", MUTED)]
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(top=0.74, bottom=0.17, left=0.33, right=0.93)
    for i, (name, note, v, kind, color) in enumerate(rows):
        if kind == "hatch":
            ax.barh(i, v, height=0.55, facecolor=SURFACE, edgecolor=color, hatch="///", linewidth=1.6)
        else:
            ax.barh(i, v, height=0.55 if kind == "solid" else 0.35, color=color)
        ax.text(v + 1200, i, f"${v:,}", va="center", ha="left", fontsize=11, color=INK)
        ax.text(-3000, i - 0.11, name, ha="right", va="center", fontsize=11, color=INK)
        ax.text(-3000, i + 0.2, note, ha="right", va="center", fontsize=9.5, color=INK_DIM)
    ax.set_yticks([])
    ax.invert_yaxis()
    ax.set_xlim(0, 112000)
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_formatter(lambda x, _: f"${x/1000:.0f}k")
    ax.tick_params(axis="x", labelsize=9)
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    titleblock(fig, "Pay Ascend members have, and pay JobsOhio was promised",
               "Annual pay per job. Ascend's figure is the average salary of its members, checked with pay records "
               "when\nthey apply. JobsOhio's is the new payroll companies committed to, divided by the jobs they "
               "committed to\ncreate in 2021 to 2025. State averages are for all jobs, May 2025.")
    credit(fig, "Sources: WVU Smith OEDC, Ascend WV Q3 2026 statistics (six community pages, weighted by members); "
                "JobsOhio monthly\nexecuted grant reports; U.S. Bureau of Labor Statistics, OEWS May 2025. "
                "Data 4 The People calculation.")
    fig.savefig(CHARTS / "06-pay-per-job.png")
    plt.close(fig)


def table_compare():
    rows = [("What the state pays",
             "$12,000 in cash to the worker, paid\nmonthly over 24 months",
             "$16,182 in grants per committed\nnew job (2021 to 2025)"),
            ("Does the job exist when\nthe deal is made?",
             "Yes. Members show proof of\nemployment and income first.",
             "Not yet. The company commits\nto create it."),
            ("What pay is published?",
             "Members' average salary,\nby community",
             "The payroll the company\npromised"),
            ("What can the public\ncheck later?",
             "Members, completions and\nretention, in WVU's reports",
             "Only signs of failure: layoff\nnotices, bankruptcies, lawsuits")]
    fig = plt.figure(figsize=(10, 6.2))
    titleblock(fig, "Two ways to pay for jobs", "Ascend WV pays workers to move. JobsOhio pays companies to "
               "create jobs.")
    x = [0.03, 0.33, 0.66]
    top = 0.78
    fig.text(x[1], top, "Ascend WV", color=BLUE, fontsize=13, fontweight="bold", va="top")
    fig.text(x[2], top, "JobsOhio grants", color=YELLOW, fontsize=13, fontweight="bold", va="top")
    h = 0.135
    for i, (q, a, j) in enumerate(rows):
        y = top - 0.07 - i * h
        fig.add_artist(plt.Line2D([0.03, 0.97], [y + 0.012, y + 0.012], color=GRID, lw=1))
        fig.text(x[0], y, q, color=INK, fontsize=11, fontweight="bold", va="top", linespacing=1.35)
        fig.text(x[1], y, a, color=INK, fontsize=11, va="top", linespacing=1.35)
        fig.text(x[2], y, j, color=INK, fontsize=11, va="top", linespacing=1.35)
    credit(fig, "Ascend's $12,000 is its cash incentive only; total program cost per member is not published. "
                "Sources: ascendwv.com terms\nand FAQ; WVU Smith OEDC Ascend WV statistics; JobsOhio monthly executed "
                "grant reports; Data 4 The People JobsOhio grants tool.")
    fig.savefig(CHARTS / "07-two-ways-table.png")
    plt.close(fig)


if __name__ == "__main__":
    use_house_style()
    chart_pay()
    table_compare()
    print("wrote 06-pay-per-job.png, 07-two-ways-table.png")
