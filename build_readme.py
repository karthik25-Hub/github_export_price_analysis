"""Rebuild README.md and battery_price_impact.xlsx from the verified CSVs.

Every number in the README is generated here. Nothing is hand-typed. The CSVs are
opened read-only and are never written to.

Prose sections that the brief requires kept verbatim are sliced out of the existing
README by heading and reinserted unchanged, rather than retyped, so they cannot drift.

    python build_readme.py
"""
from __future__ import annotations
import re
from pathlib import Path

import pandas as pd

import sys

# ---------------------------------------------------------------------------
# ONE-SHOT SCRIPT. DO NOT RE-RUN.  Disabled 2026-08-18.
#
# SRC is README.md and the output is written back to README.md, so this script
# consumes its own output. The first run stripped the sentences it replaces;
# every later run cannot find them and raises AttributeError at line ~185.
#
# Guarding those regexes does NOT fix it. Tested: with the searches guarded the
# script runs but appends 28 lines / 1,836 bytes on every run, silently growing
# the README. That is worse than the crash.
#
# The real fix needs the pre-run source document, which was never committed
# (git log shows one commit, already carrying the 525-line output). To restore
# re-runnability: strip the generated tables out of the current README by hand,
# save that as README_source.md, point SRC at it, and keep the output separate.
#
# Until then README.md is maintained by hand. Numbers in it must be checked
# against battery_price_impact_master.csv, not assumed.
# ---------------------------------------------------------------------------
sys.exit("build_readme.py is one-shot and disabled; see the note at the top of this file.")


HERE = Path(__file__).resolve().parent
M = pd.read_csv(HERE / "battery_price_impact_master.csv")
J = pd.read_csv(HERE / "battery_price_impact_rejected.csv")
N = pd.read_csv(HERE / "battery_price_impact_near_misses.csv")
DE = pd.read_csv(HERE / "data" / "germany_screening.csv")
IT = pd.read_csv(HERE / "data" / "italy_screening.csv")

ORDER = ["SA1", "VIC1", "NSW1", "QLD1", "Great Britain", "CAISO", "ERCOT"]
OUTC = ["mean", "daily_spread", "peak_shaving", "valley_filling", "volatility"]
LONG = {"mean": "Mean price", "daily_spread": "Daily spread",
        "peak_shaving": "Peak shaving", "valley_filling": "Valley filling",
        "volatility": "Volatility"}
SHORT = {"mean": "Mean", "daily_spread": "Spread", "peak_shaving": "Peak",
         "valley_filling": "Valley", "volatility": "Volatility"}
DASH = "—"
MID = "·"
POSSIBLE = {"SA1": 30, "VIC1": 30, "NSW1": 30, "QLD1": 30, "Great Britain": 30,
            "CAISO": 25, "ERCOT": 30}


# ------------------------------------------------------------------ helpers
def tbl(header, rows):
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def pct(v):
    """Signed to 2 dp; anything under half a hundredth prints as ~0."""
    if pd.isna(v):
        return DASH
    if abs(v) < 0.005:
        return "~0"
    return f"{v:+.2f}"


def pv(v):
    """3 dp, floored at the 999-draw minimum."""
    return "0.001" if v <= 0.001 else f"{v:.3f}"


def verdict(r):
    interval = (r.lo95 * r.hi95) > 0
    per_cell = r.placebo_p <= 0.05
    joint = r.placebo_p_adjusted <= 0.05
    if interval and per_cell and joint:
        return "firm"
    if interval and per_cell:
        return "holds"
    if not interval and per_cell:
        return "covers zero"
    if interval and not per_cell:
        return "fails placebo"
    return "neither"


def physical_cell(mk, y):
    """The physical-gate verdict for a market-year, read off the rejected file."""
    r = J[(J.market == mk) & (J.year == y)]
    exc = r[r.gate_failed == "excluded"]
    if len(exc):
        return "excluded, Winter Storm Uri"
    ph = r[r.gate_failed == "physical"]
    if not len(ph):
        return "pass"
    d = str(ph.detail.iloc[0])
    if "no discharge" in d:
        return "fail, no dispatch"
    m_ = re.search(r"throughput ([\d.]+) GWh", d)
    if m_:
        return f"fail, {m_.group(1)} GWh throughput"
    return "fail, outside band"


def blocked_cell(mk, y):
    r = J[(J.market == mk) & (J.year == y)]
    if len(r[r.gate_failed == "excluded"]):
        return "not screened"
    ide = set(r[r.gate_failed == "identification"].outcome)
    if not ide:
        return DASH
    if len(ide) == 5:
        return "all five"
    return ", ".join(SHORT[o] for o in OUTC if o in ide)


# ------------------------------------------------------- per-market tables
def market_block(mk):
    m = M[M.market == mk]
    j = J[J.market == mk]
    years = sorted(set(m.year) | set(j.year))
    cur = m.currency.iloc[0] if len(m) else ""
    rows = []
    for y in years:
        my = m[m.year == y]
        ph = physical_cell(mk, y)
        if len(my):
            fleet = f"{my.fleet_MW.iloc[0]:,.0f}"
            mp = f"{my.mean_price.iloc[0]:.2f}"
            gr = f"{my.gross_ratio.iloc[0]:.4f}"
        else:
            fleet = mp = DASH
            jr = j[(j.year == y) & (j.gate_failed == "physical") & j.value.notna()]
            gr = f"{jr.value.iloc[0]:.4f}" if len(jr) else DASH
        rows.append([y, fleet, mp, gr, ph, f"{len(my)} of 5", blocked_cell(mk, y)])
    t1 = tbl(["Year", "Fleet MW", f"Mean price {cur}/MWh", "Gross ratio",
              "Physical gate", "Admitted", "Blocked by identification gate"], rows)

    yrs2 = sorted(set(m.year))
    r2, r3 = [], []
    for y in yrs2:
        my = m[m.year == y].set_index("outcome")
        a, b = [y], [y]
        for o in OUTC:
            if o in my.index:
                r = my.loc[o]
                a.append(pct(r.pct_of_mean_price))
                b.append(f"{pv(r.placebo_p)} / {pv(r.placebo_p_adjusted)} {MID} {verdict(r)}")
            else:
                a.append(DASH)
                b.append(DASH)
        r2.append(a)
        r3.append(b)
    head = ["Year"] + [LONG[o] for o in OUTC]
    return t1, tbl(head, r2), tbl(head, r3), len(m)


# ------------------------------------------------- panel reliability table
def panel_table():
    d = M.copy()
    d["interval"] = (d.lo95 * d.hi95) > 0
    d["placebo"] = d.placebo_p <= 0.05
    d["joint"] = d.placebo_p_adjusted <= 0.05
    d["both"] = d.interval & d.placebo
    rows = []
    for o in OUTC:
        s = d[d.outcome == o]
        dn, up = int((s.effect < 0).sum()), int((s.effect > 0).sum())
        direction = ("all down" if up == 0 else "all up" if dn == 0
                     else f"{dn} down, {up} up")
        rows.append([LONG[o], len(s), int(s.interval.sum()), int(s.placebo.sum()),
                     int(s.joint.sum()), int(s.both.sum()), direction,
                     s.interval.mean()])
    rows.sort(key=lambda r: -r[-1])
    body = [r[:-1] for r in rows]
    dn, up = int((d.effect < 0).sum()), int((d.effect > 0).sum())
    body.append(["**Panel**", f"**{len(d)}**", f"**{int(d.interval.sum())}**",
                 f"**{int(d.placebo.sum())}**", f"**{int(d.joint.sum())}**",
                 f"**{int(d.both.sum())}**", f"**{dn} down, {up} up**"])
    t = tbl(["Outcome", "Cells", "Interval excludes zero", "Beats placebo",
             "Survives joint test", "Interval and placebo", "Direction"], body)
    return t, (len(d), int(d.interval.sum()), int(d.placebo.sum()),
               int(d.joint.sum()), int(d.both.sum()))


# ---------------------------------------------------------------- assembly
SRC = (HERE / "README.md").read_text(encoding="utf-8")
parts = re.split(r"^## ", SRC, flags=re.M)
sec = {}
for p in parts[1:]:
    sec[p.split("\n", 1)[0].strip()] = "## " + p.rstrip() + "\n"
intro = parts[0].rstrip() + "\n"

# method paragraph, minus the five-outcomes sentence that the table replaces
method = sec["Method, in one paragraph"]
five_sentence = re.search(
    r"\*\*All effects are observed minus counterfactual.*?hour-to-hour volatility\.\n",
    method, re.S).group(0)
method = method.replace(five_sentence,
                        "**All effects are observed minus counterfactual, so a negative "
                        "value means the fleet\npushed the statistic down.**\n")

# the two gates, minus the region-of-curve sentences the outcomes table absorbs
gates = sec["The two gates"]
region_sentence = re.search(
    r"Peak shaving reads the top quartile.*?bottom share under 10 per cent\. ",
    gates, re.S).group(0)
gates = gates.replace(region_sentence, "")
old_nm = re.search(r"\| Market \| Year \| Gross ratio \|.*?\| QLD1 \| 2021 \|[^\n]*\n",
                   gates, re.S).group(0)
n = N.sort_values("distance_from_band")
new_nm = tbl(["Market", "Year", "Gross ratio", "Distance from band", "Admitted"],
             [[r.market, r.year, f"{r.gross_ratio:.4f}", f"{r.distance_from_band:.4f}",
               "no"] for r in n.itertuples()]) + "\n"
gates = gates.replace(old_nm, new_nm)

# reliability prose, minus the totals sentence the panel table now carries
rel = sec["Reliability"]
tot_sentence = re.search(r"Of the 108 retained cells.*?per-cell placebo\.\n", rel, re.S).group(0)
rel = rel.replace(tot_sentence, "")

FIVE = tbl(["Outcome", "What it measures", "Region of the curve read",
            "Rank correlation required"],
           [["Mean price", "Average price across the year", "Whole curve", "0.60"],
            ["Daily spread", "Average within-day high-to-low range", "Top quartile, plus the bottom quartile or a bottom share under 10%", "0.60"],
            ["Peak shaving", "Effect on the dearest tenth of hours", "Top quartile", "0.60"],
            ["Valley filling", "Effect on the cheapest tenth of hours", "Bottom quartile", "0.60"],
            ["Volatility", "Hour-to-hour price variation", "Whole curve", "0.60"]])

HOWTO = """## How to read the market tables

Each market that produces estimates gets three tables. The first records what the
screening did, year by year, including years where nothing survived. The second gives
the effects as a percentage of that year's own mean price, which is how markets on
different currencies and price levels are compared. The third gives the reliability of
each estimate.

In the reliability table each cell reads `per-cell p / joint p """ + MID + """ verdict`. The
per-cell p is the within-day shuffle placebo for that cell alone. The joint p is the
Westfall-Young max-T adjustment across all of that market's cells together, so it is a
single claim about the market rather than a set of separate tests, and it is strictly
the more conservative of the two.

**Placebo p floors at 0.001**, because 999 draws cannot resolve anything finer. A cell
printed as 0.001 means no draw out of 999 matched the observed estimate, not that the
p-value is precisely one in a thousand.

The verdict combines three tests: whether the 95% interval excludes zero, whether the
cell beats its own placebo, and whether it survives the joint test.

""" + tbl(["Verdict", "Meaning"],
          [["firm", "Interval excludes zero, beats the placebo, and survives the joint test"],
           ["holds", "Interval excludes zero and beats the placebo, but not the joint test"],
           ["covers zero", "Beats the placebo, but the interval spans zero"],
           ["fails placebo", "Interval excludes zero, but a random reshuffle matches it"],
           ["neither", "Interval spans zero and the placebo is not beaten"]]) + """

An effect printed as `~0` is smaller than half a hundredth of one per cent of that
year's mean price. A dash means the cell was not estimated.

Fleet MW, mean price and gross ratio are carried only on retained rows in the source
data. Where a market-year clears the physical gate but loses all five outcomes to the
identification gate, those three columns are therefore blank: NSW1 2025, QLD1 2025 and
ERCOT 2023. That is a gap in the source data rather than a missing value invented here,
and the rows are kept rather than dropped so the screening remains visible.
"""

blocks, counts = [], {}
for mk in ORDER:
    t1, t2, t3, k = market_block(mk)
    counts[mk] = k
    blocks.append(f"### {mk}\n\n**Gates**\n\n{t1}\n\n**Effects, per cent of mean "
                  f"price**\n\n{t2}\n\n**Reliability**, per-cell p / joint p "
                  f"{MID} verdict\n\n{t3}\n")
markets_md = "## Results by market\n\n" + "\n".join(blocks)

panel_md, totals = panel_table()
de_md = tbl(["Source", "What it returned"],
            [[r.source, r.what_it_returned] for r in DE.itertuples()])
it = IT.copy()
it_md = tbl(["Month", "Hours covered", "Gross ratio", "Net ratio", "Inside band, gross"],
            [[r.month, f"{r.hours_covered:,}", f"{r.gross_ratio:.4f}",
              f"{r.net_ratio:.4f}", "yes" if r.inside_band_gross else "no"]
             for r in it.itertuples()])

ger = sec["Germany and Italy produce no estimate"].rstrip()
ger += ("\n\n**Germany: the four sources checked**\n\n" + de_md +
        "\n\n**Italy: ENTSO-E B25 by month, 2025**\n\n" + it_md + "\n")

files = sec["Files"].replace(
    "| `battery_price_impact.xlsx` |",
    "| `build_readme.py` | the script that generates every table in this README and "
    "rebuilds the workbook; the CSVs are read-only inputs |\n| `battery_price_impact.xlsx` |")

README = "\n".join([
    intro, method,
    "## The five outcomes\n\n" + FIVE + "\n",
    gates, rel, HOWTO, markets_md,
    "## Reliability by outcome, whole panel\n\n" + panel_md +
    "\n\nSorted by the share of cells whose interval excludes zero.\n",
    sec["Which cells are retained, and why the rest are not"],
    ger, sec["A correction to ERCOT's residual demand"], files,
    sec["What is deliberately not here"],
])
README = re.sub(r"\n{3,}", "\n\n", README)
(HERE / "README.md").write_text(README, encoding="utf-8")

# ------------------------------------------------------------------- xlsx
NOTE = {**{mk: f"{mk}. Three tables: gates, effects as per cent of mean price, and "
               f"reliability. {counts[mk]} retained cells." for mk in ORDER},
        "Germany": "No price estimate. Four sources checked; none publishes a battery "
                   "dispatch series.",
        "Italy": "No price estimate. ENTSO-E B25 exists from 1 Jan 2025 but fails the "
                 "physical gate at 0.9090 for the year."}


def md_to_df(md):
    rows = [r.strip().strip("|").split("|") for r in md.split("\n")]
    head = [c.strip() for c in rows[0]]
    return pd.DataFrame([[c.strip() for c in r] for r in rows[2:]], columns=head)


with pd.ExcelWriter(HERE / "battery_price_impact.xlsx", engine="openpyxl") as w:
    about = pd.DataFrame({"About": [
        "Battery storage and wholesale electricity prices, nine markets, 2020-2025.",
        "",
        "SIGN CONVENTION: effects are observed minus counterfactual, so a NEGATIVE",
        "value means the fleet pushed the statistic down. Currency is local and is",
        "never converted; compare markets on per cent of mean price or per GW.",
        "",
        "Each market sheet carries three tables: gates, effects as per cent of that",
        "year's mean price, and reliability.",
        "",
        "RELIABILITY CELLS read: per-cell placebo p / joint max-T p, then a verdict.",
        "Placebo p floors at 0.001 on 999 draws, so 0.001 means no draw matched.",
        "",
        "VERDICTS",
        "  firm          interval excludes zero, beats placebo, survives joint test",
        "  holds         interval and placebo pass, joint test does not",
        "  covers zero   beats the placebo but the interval spans zero",
        "  fails placebo interval excludes zero but a reshuffle matches it",
        "  neither       interval spans zero and the placebo is not beaten",
        "",
        f"PANEL: {totals[0]} cells, {totals[1]} intervals exclude zero, "
        f"{totals[2]} beat the placebo,",
        f"{totals[3]} survive the joint test, {totals[4]} satisfy interval and placebo.",
        "",
        "Germany and Italy produce no estimate; their sheets carry screening evidence.",
        "Generated by build_readme.py from the verified CSVs. See README.md."]})
    about.to_excel(w, sheet_name="About", index=False)
    for mk in ORDER:
        t1, t2, t3, _ = market_block(mk)
        r = 0
        pd.DataFrame({"note": [NOTE[mk]]}).to_excel(w, sheet_name=mk, index=False, startrow=r)
        r += 3
        for title, md in (("Gates", t1), ("Effects, per cent of mean price", t2),
                          ("Reliability", t3)):
            pd.DataFrame({title: []}).to_excel(w, sheet_name=mk, index=False, startrow=r)
            r += 1
            d = md_to_df(md)
            d.to_excel(w, sheet_name=mk, index=False, startrow=r)
            r += len(d) + 3
    for mk, d in (("Germany", DE), ("Italy", IT)):
        pd.DataFrame({"note": [NOTE[mk]]}).to_excel(w, sheet_name=mk, index=False, startrow=0)
        d.to_excel(w, sheet_name=mk, index=False, startrow=3)

print("retained cells per market:", counts, "total", sum(counts.values()))
print("panel totals (cells, interval, placebo, joint, both):", totals)
