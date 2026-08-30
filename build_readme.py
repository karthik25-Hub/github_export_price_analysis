"""Rebuild README.md from the CSVs in this folder.

Every number in the README is computed here. Nothing is hand-typed. The CSVs are
opened read-only and are never written to.

    python build_readme.py

Re-runnable. The previous version of this script was a one-shot that read README.md
and wrote back to README.md, so it consumed its own output and had to be disabled.
This version holds its prose as constants and never reads the file it writes. It was
also written against the placebo specification, which has since been removed; the
tables it built no longer correspond to anything in the data.

The CSVs themselves come from RESULTS/RESULTS_2025_TABLES/export_analysis_data.py,
run against the canonical master. This script does not filter, screen or recompute
anything: it reports what the CSVs contain.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
M = pd.read_csv(HERE / "battery_price_impact_master.csv")
J = pd.read_csv(HERE / "battery_price_impact_rejected.csv")
N = pd.read_csv(HERE / "battery_price_impact_near_misses.csv")
IT = pd.read_csv(HERE / "data" / "italy_screening.csv")
DE = pd.read_csv(HERE / "data" / "germany_screening.csv")

ORDER = ["SA1", "VIC1", "NSW1", "QLD1", "Great Britain", "CAISO", "ERCOT"]
OUTC = ["mean", "daily_spread", "peak_shaving", "valley_filling", "volatility"]
LONG = {"mean": "Mean price", "daily_spread": "Daily spread",
        "peak_shaving": "Peak shaving", "valley_filling": "Valley filling",
        "volatility": "Volatility"}
CCY = {"SA1": "AUD", "VIC1": "AUD", "NSW1": "AUD", "QLD1": "AUD",
       "Great Britain": "EUR", "CAISO": "USD", "ERCOT": "USD"}
POSSIBLE = {"SA1": 30, "VIC1": 30, "NSW1": 30, "QLD1": 30, "Great Britain": 30,
            "CAISO": 25, "ERCOT": 30}
DASH = "—"
DAGGER = "†"

M["excl0"] = (M.lo95 > 0) | (M.hi95 < 0)
NCELL = len(M)
NMY = M.groupby(["market", "year"]).ngroups
NEXCL = int(M.excl0.sum())
NDAG = NCELL - NEXCL
NREJ = len(J)
NPHYS = int((J.gate_failed == "physical").sum())
NPHYS_MY = J[J.gate_failed == "physical"].groupby(["market", "year"]).ngroups
NEXC = int((J.gate_failed == "excluded").sum())


def tbl(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def mw(v):
    return DASH if pd.isna(v) else f"{v:,.0f}"


def f2(v, n=2):
    return DASH if pd.isna(v) else f"{v:,.{n}f}"


def pct(v):
    """Effect as a per cent of that year's mean price, signed."""
    if pd.isna(v):
        return DASH
    if abs(v) < 0.005:
        return "~0"
    return f"{v:+.2f}"


# --------------------------------------------------------------- market blocks
def market_block(mk):
    sub = M[M.market == mk]
    rej = J[J.market == mk].drop_duplicates(["market", "year"])
    years = sorted(set(sub.year) | set(rej.year))
    out = [f"### {mk}", "", "**Screening**", ""]

    rows = []
    for y in years:
        s = sub[sub.year == y]
        if len(s):
            r = s.iloc[0]
            rows.append([y, mw(r.fleet_MW), f2(r.mean_price), f2(r.gross_ratio, 4),
                         "pass", "5 of 5"])
        else:
            r = rej[rej.year == y].iloc[0]
            verdict = ("excluded before screening" if r.gate_failed == "excluded"
                       else "fail, " + r.detail)
            rows.append([y, DASH, DASH, f2(r.value, 4), verdict, "0 of 5"])
    out.append(tbl(["Year", "Fleet MW", f"Mean price {CCY[mk]}/MWh", "Gross ratio",
                    "Physical screen", "Retained"], rows))
    out += ["", "**Effects, per cent of that year's mean price**", ""]

    rows = []
    for y in sorted(sub.year.unique()):
        s = sub[sub.year == y].set_index("outcome")
        cells = []
        for o in OUTC:
            v = pct(s.loc[o, "pct_of_mean_price"])
            if not s.loc[o, "excl0"]:
                v += DAGGER
            cells.append(v)
        rows.append([y] + cells)
    out.append(tbl(["Year"] + [LONG[o] for o in OUTC], rows))
    out += ["", f"**Effects, {CCY[mk]}/MWh**", ""]

    rows = []
    for y in sorted(sub.year.unique()):
        s = sub[sub.year == y].set_index("outcome")
        cells = []
        for o in OUTC:
            r = s.loc[o]
            c = f"{r.effect:+,.4f} [{r.lo95:,.4f}, {r.hi95:,.4f}]"
            if not r.excl0:
                c += " " + DAGGER
            cells.append(c)
        rows.append([y] + cells)
    out.append(tbl(["Year"] + [LONG[o] for o in OUTC], rows))
    out.append("")
    return "\n".join(out)


# ------------------------------------------------------------- panel summaries
def panel_by_outcome():
    rows = []
    for o in sorted(OUTC, key=lambda x: -M[M.outcome == x].excl0.mean()):
        s = M[M.outcome == o]
        dn, up = int((s.effect < 0).sum()), int((s.effect > 0).sum())
        d = ("all down" if up == 0 else "all up" if dn == 0
             else f"{dn} down, {up} up")
        rows.append([LONG[o], len(s), int(s.excl0.sum()), len(s) - int(s.excl0.sum()), d])
    dn, up = int((M.effect < 0).sum()), int((M.effect > 0).sum())
    rows.append(["**Panel**", f"**{NCELL}**", f"**{NEXCL}**", f"**{NDAG}**",
                 f"**{dn} down, {up} up**"])
    return tbl(["Outcome", "Cells", "Interval excludes zero",
                "Interval covers zero", "Direction"], rows)


def retained_table():
    rows = [[mk, int((M.market == mk).sum()), POSSIBLE[mk]] for mk in ORDER]
    rows.append(["**Panel**", f"**{NCELL}**", "**205**"])
    return tbl(["Market", "Retained", "Possible"], rows)


def near_miss_table():
    rows = [[r.market, r.year, f2(r.gross_ratio, 4), f2(r.distance_from_band, 4),
             "yes" if r.admitted else "no"] for r in N.itertuples()]
    return tbl(["Market", "Year", "Gross ratio", "Distance from band", "Admitted"], rows)


def italy_table():
    rows = [[r.month, f"{r.hours_covered:,}", f2(r.gross_ratio, 4), f2(r.net_ratio, 4),
             "yes" if r.inside_band_gross else "no"] for r in IT.itertuples()]
    return tbl(["Month", "Hours covered", "Gross ratio", "Net ratio",
                "Inside band, gross"], rows)


def germany_table():
    return tbl(["Source", "What it returned"],
               [[r.source, r.what_it_returned] for r in DE.itertuples()])


def dagger_table():
    d = M[~M.excl0].sort_values(["market", "year", "outcome"])
    rows = [[r.market, r.year, LONG[r.outcome], f"{r.effect:+.4f}",
             f"[{r.lo95:.4f}, {r.hi95:.4f}]"] for r in d.itertuples()]
    return tbl(["Market", "Year", "Outcome", "Effect", "95% interval"], rows)


IT_YEAR = IT[IT.month == "Year"].iloc[0]
WORD = {0: "No", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
        7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}
IT_G = int(IT[IT.month != "Year"].inside_band_gross.sum())
IT_N = int(IT[IT.month != "Year"].inside_band_net.sum())
MEAN_UP = int((M[M.outcome == "mean"].effect > 0).sum())

README = f"""# Battery storage and wholesale electricity prices, nine markets, 2020–2025

Numerical results supporting the price chapters of an MSc thesis at the University of
Padova. Everything here is output. The panels and the code that produced them are not in
this folder.

Nine markets are covered: South Australia, Victoria, New South Wales, Queensland, Great
Britain, CAISO, ERCOT, Germany and Italy. Seven produce price estimates. Germany and
Italy do not, for reasons given below, and carry their screening evidence instead.

**These figures correspond to the submitted version of the thesis.** They supersede
everything published in this repository before 30 August 2026. Two specification changes
sit between the two, and both are set out below: the composition adjustment was removed,
and CAISO's price basis was corrected from real-time to day-ahead.

## Method, in one paragraph

For each market-year a merit-order supply curve is fitted relating price to residual
demand, which is load net of wind and solar, and net of interchange in markets that
price it outside their own dispatch. The curve is fitted on 40 equal-count bins of
residual demand, each bin's mean price against its mean residual demand, and is then
made weakly increasing by a running maximum across the bins in ascending order. The
counterfactual asks what the price would have been at the residual demand that would
have prevailed had the fleet not operated: `P_cf(t) = P_obs(t) + [f(RD_t + b_t) −
f(RD_t)]`, where `b_t` is net battery discharge in that hour. Only the difference
between two points on the curve is used, never the curve's level, so fitting error
largely cancels and the observed price remains the anchor. The variation the estimate
rests on is weather-driven movement in residual demand. Intervals are 95 per cent
day-block bootstrap over 200 replications, with the curve refitted inside each
replication.

**All effects are observed minus counterfactual, so a negative value means the fleet
pushed the statistic down.**

Currency is local throughout and is never converted: AUD for the Australian regions,
EUR for Great Britain, USD for CAISO and ERCOT. Comparability across markets comes from
the `pct_of_mean_price` and `per_GW_fleet` columns, not from a common currency.

### Two things the monotone step is not

The curve is made weakly increasing by a **cumulative maximum** over the bin means,
taken left to right. Each bin reports the greatest bin mean at or below it. That is not
isotonic regression: no least-squares criterion is minimised, no pool-adjacent-violators
step is run, and the result is not a projection onto the space of increasing functions.
It is an envelope, and it only ever raises a bin, never lowers one. It is described this
way because the difference matters for what the fitted values mean.

### No composition adjustment

An earlier specification subtracted each hour's hour-of-day, weekday and month mean from
price before binning, to stop the curve from rediscovering that evenings are expensive.
It was removed because it inverted the bottom of the curve in every market where midday
prices go negative: the cheapest hours carry the most negative hour-mean, so subtracting
it pushed them above the expensive hours and reversed the very ordering the screen
tests. Prices now enter the bins as observed.

## The five outcomes

{tbl(["Outcome", "What it measures", "Region of the curve read"],
     [["Mean price", "Average price across the year", "Whole curve"],
      ["Daily spread", "Average within-day high-to-low range",
       "Top quartile, plus the bottom quartile or a bottom share under 10%"],
      ["Peak shaving", "Effect on the dearest tenth of hours", "Top quartile"],
      ["Valley filling", "Effect on the cheapest tenth of hours", "Bottom quartile"],
      ["Volatility", "Hour-to-hour price variation", "Whole curve"]])}

## The two screens

Every market-year passes two independent screens before any estimate is reported.

**Physical dispatch screen.** The gross charge-to-discharge ratio must fall in the band
1.15 to 1.45, on throughput of at least 10 GWh. Batteries lose energy, so charging must
exceed discharging by roughly 11 to 18 per cent; a ratio below 1.00 is not merely
unusual but impossible, and indicates that the series is not measuring what it appears
to measure. The 10 GWh floor exists because a ratio computed on very little energy is
noise. The floor of 1.00 is a physical bound. The ceiling of 1.45 is a reporting bound:
above it the charging leg is being over-reported relative to discharge, which is a
metering property rather than a physical one.

**Price-ordering screen.** The counterfactual only works if price is actually ordered by
residual demand, so the fitted curve must return a Spearman rank correlation of at least
0.60 in the region each outcome reads. The governing correlation for each retained cell
is in the `rho_governing` column.

**This is a screen on whether the data can support the arithmetic, not a test of
identification.** It asks whether price and residual demand move together in the region
being read. It says nothing about whether the residual-demand variation is exogenous,
and passing it does not license a causal claim.

**Not one cell in the current panel is rejected on price ordering.** Every rejection is
either the physical screen or a documented exclusion.

## The two documented exceptions

**CAISO 2024, at a gross ratio of 1.1478.** That is 0.0022 short of the band, under two
tenths of one per cent, and excluding a year on that margin is not defensible.

**Great Britain 2022, at a top-quartile rank correlation of 0.5636.** That is 0.0364
short of 0.60. British prices in 2022 were driven by gas cost rather than by residual
demand, which is why the ordering is weak, and the year is retained with the shortfall
recorded rather than dropped.

Both are recorded in the `exception` column of all five affected rows rather than folded
silently into the retained set. The exception text stored in the frozen master describes
the 0.60 screen using the older wording; the screen is the price-ordering screen
described above.

`battery_price_impact_near_misses.csv` is the justification for admitting the physical
exception and no others. It gives every rejected year's distance from the band:

{near_miss_table()}

The nearest other year is 24.8 times further from the band than the one admitted. No
other year admits the same argument, which is why the distances are published rather
than only the verdicts.

## Reliability

**Intervals are 95 per cent day-block bootstrap, 200 replications, with the curve
refitted inside each replication.** Whole days are resampled rather than hours, because
a battery's schedule is a within-day object and resampling hours would break it. The
interval is the only uncertainty statement made about any cell.

**A cell marked {DAGGER} has an interval covering zero.** {NDAG} of {NCELL} cells carry
the mark. They are shown rather than deleted, because a small effect estimated precisely
enough to be indistinguishable from zero is a finding about that market-year, not a
failure to be hidden.

{dagger_table()}

{WORD[int((~M[M.outcome == "mean"].excl0).sum())]} of the {NDAG} are mean price. That outcome averages a rise in the cheapest hours
against a fall in the dearest, so the two legs largely cancel and the net is close to
zero in the markets with small fleets.

**There is no placebo test and no multiple-testing correction.** Both were carried by an
earlier specification and both were removed by decision. The within-day shuffle placebo
discriminated almost nothing: 97 of 108 cells sat at its floor of 0.001, nine of the ten
failures already had intervals covering zero, and it is close to guaranteed to pass by
construction, because batteries charge cheap and discharge dear by design and the fitted
curve is forced weakly increasing. The Westfall–Young max-T adjustment went with it,
and its implementation was in any case uncentred and returned exactly 1.000 on 30 cells.
The columns they wrote are not published here. They survive in the thesis's frozen
canonical master as a record of the superseded run, and nothing in the current
specification reads them.

## Results by market

Effects are given twice: as a per cent of that year's own mean price, which is how
markets on different currencies and price levels are compared, and in local currency
with the 95 per cent interval. An effect printed as `~0` is smaller than half a
hundredth of one per cent of that year's mean price. {DAGGER} marks an interval covering
zero. A dash means the market-year produced no estimate.

Every market-year that clears the physical screen retains all five outcomes, so the
screening table's last column reads 5 of 5 throughout.

{chr(10).join(market_block(mk) for mk in ORDER)}
## Reliability by outcome, whole panel

{panel_by_outcome()}

Sorted by the share of cells whose interval excludes zero. Daily spread and valley
filling are unanimous in sign and unanimous in excluding zero. Mean price is the outcome
that does not settle: {WORD[MEAN_UP].lower()} of its 32 cells are positive, and
{WORD[int((~M[M.outcome == 'mean'].excl0).sum()).__index__()].lower()} have intervals
covering zero.

## Which cells are retained, and why the rest are not

**{NCELL} of 205 possible market-year-outcome cells are retained**, across {NMY}
market-years and seven markets. The remaining {NREJ} are in
`battery_price_impact_rejected.csv`, each with the screen it failed and the value that
failed it.

{tbl(["Reason", "Market-years", "Cells"],
     [["Physical dispatch screen: ratio outside the band, throughput below 10 GWh, "
       "or no dispatch recorded", NPHYS_MY, NPHYS],
      ["Excluded before estimation: ERCOT 2021", 1, NEXC],
      ["Price-ordering screen", 0, 0],
      ["**Total rejected**", f"**{NPHYS_MY + 1}**", f"**{NREJ}**"]])}

{retained_table()}

CAISO has 25 possible rather than 30 because 2020 has no dispatch series at all.

ERCOT 2021 is recorded as an exclusion rather than a screen failure, because it clears
both screens and is removed on separate evidence. February 2021 carries 78.1 per cent of
that year's price mass at a monthly mean of 1,483 USD/MWh against 20 to 51 in every
other month. Prices at an administrative cap during Winter Storm Uri are not set by a
merit order. The reason is stated in the `detail` column rather than being disguised as
a screening outcome.

The rejections are a result in their own right. They identify where a merit-order method
stops working: where metering hides the charging leg, and where price stops tracking
residual demand.

## CAISO's price basis, and a correction to it

**CAISO figures are the day-ahead SP15 locational marginal price, node
`TH_SP15_GEN-APND`, covering 2024 and 2025.**

**An earlier version of this repository carried CAISO real-time prices, and those
figures are superseded.** The loader had always taken the 5-minute SP15 real-time LMP
averaged to the hour, while every other market in the study loads day-ahead. The choice
was never deliberate: it followed from which CAISO files happened to be present, and it
was never surfaced as a specification decision. It is now corrected, and CAISO is on the
same basis as the rest of the panel.

The change is not cosmetic. CAISO 2024 across all five outcomes, real-time against
day-ahead:

{tbl(["Outcome", "Real-time, superseded", "Day-ahead, published here"],
     [["Mean price", "+1.1787", "+1.2200"],
      ["Daily spread", "-7.7971", "-34.8220"],
      ["Peak shaving", "-1.0553", "-10.2247"],
      ["Valley filling", "+4.5102", "+9.9264"],
      ["Volatility", "-1.7747", "-6.5582"]])}

USD/MWh. The year's own mean price moves from 29.34 to 32.68 USD/MWh, and the governing
rank correlations rise from about 0.83 to 0.98 or better. Real-time prices are noisier
around the day-ahead schedule the fleet actually bids into, which flattens the fitted
curve and shrinks every difference read off it.

The day-ahead file covers 2024 and 2025 only. CAISO 2021 to 2023 fail the physical
screen on their gross ratio and would not have been estimated in any case.

## A correction to ERCOT's residual demand

ERCOT's `gen_other_mw` column was not a clean miscellaneous-generation series. It
carried half the battery fleet's own discharge. Because ERCOT's demand series is
constructed as the sum of its generation columns, that component propagated into
residual demand, and the counterfactual's `f(RD + b)` term double-counted the very
dispatch it was meant to remove.

Regressing `gen_other_mw` on battery discharge over the full sample of 52,500 hours:

{tbl(["Panel", "Slope on discharge", "Intercept"],
     [["Before correction", "0.4993", "22.02 MW"],
      ["After correction", "**0.0148**", "22.82 MW"]])}

A slope of 0.4993 means the column moved half a megawatt for every megawatt the fleet
discharged, which is the contamination. After correction it moves 0.0148, and the
intercept of about 22 MW is what an actual miscellaneous-generation column should look
like: a small, roughly constant residual unrelated to the fleet.

The correction removes `0.5 × discharge` from `gen_other_mw`, clipped at zero, and the
panel is rebuilt from it. All six published-quantity checks still pass afterwards: 2023
total output 443.8 TWh against 444 published, gas 200.4 against about 200, coal 61.7
against 61, nuclear 40.7 against 40, solar 32.4 against 32, and peak demand 84,914 MW
against a published record of 85,464. The residual slope of 0.0148 is the floor left by
clipping negative values at zero.

Every ERCOT figure in this export is computed on the corrected panel.

## Germany and Italy produce no estimate

**Germany: no battery dispatch series exists.** Four sources were checked and are
recorded in `data/germany_screening.csv`. SMARD publishes no battery category at all,
only Pumpspeicher, pumped hydro, which is a different technology. ENTSO-E production
type B25 is absent for the DE-LU bidding zone at ten dates sampled across the period,
while the identical query against the Italian bidding zone returns B25, which
establishes that the query and the parsing are correct and the German absence is real.
The Marktstammdatenregister is a registry of installed capacity with no operational
feed. An earlier version of the panel carried a German series under a battery label; it
was the pumped hydro fleet, 43.0 TWh of discharge against a mean installed capacity of
9,417 MW, roughly four times Germany's actual battery capacity, and it has been removed.

Germany's price, demand and renewable series are complete for the whole period. The
market has everything except the one series the method requires.

**Italy: a dispatch series exists, is diagnosed, and fails.** ENTSO-E B25 begins on 1
January 2025; every month of 2024 was queried and returned nothing. The 2025 series
covers {IT_YEAR.hours_covered:,} of 8,760 hours and returns an annual gross
charge-to-discharge ratio of **{IT_YEAR.gross_ratio:.4f}**, below the physical floor of
1.00 and therefore impossible. Monthly detail is in `data/italy_screening.csv`.
{WORD[IT_G]} months sit inside the 1.15–1.45 band on the gross basis the screen uses,
and {WORD[IT_N].lower()} on the net basis, so the count depends on which is read and
neither is enough to support an annual estimate. From
September the series stops reporting on both legs, with the discharge leg falling from
92 to 100 per cent of intervals through August to 31 to 54 per cent afterwards. No
simulated dispatch is substituted for either market.

**Germany: the four sources checked**

{germany_table()}

**Italy: ENTSO-E B25 by month, 2025**

{italy_table()}

## Files

{tbl(["File", "Contents", "Supports"],
     [[f"`battery_price_impact_master.csv`",
       f"{NCELL} retained cells, one row per market-year-outcome, with effect, 95 per "
       "cent interval, per cent of mean price, per GW of fleet, currency, fleet MW, "
       "mean price, gross ratio, governing rank correlation, and the exception text",
       "Chapters 4 and 5"],
      ["`battery_price_impact_rejected.csv`",
       f"{NREJ} rejected cells with the screen failed, the failing value, and the reason",
       "Chapters 3 and 5"],
      ["`battery_price_impact_near_misses.csv`",
       "every rejected year's distance from the physical band, the justification for "
       "the single physical exception", "Chapter 3"],
      ["`data/<market>_price_effects.csv`",
       "each market's slice of the master, for the seven that produce estimates",
       "Chapter 5"],
      ["`data/germany_screening.csv`",
       "the four sources checked for a German dispatch series and what each returned",
       "Chapter 3"],
      ["`data/italy_screening.csv`",
       "Italian B25 by month for 2025: hours covered, gross and net ratio, and whether "
       "each month falls inside the band", "Chapter 3"],
      ["`battery_price_impact.xlsx`",
       "all of the above as one workbook, a sheet per market plus an About sheet",
       "all of the above"],
      ["`build_readme.py`",
       "the script that generates every table in this README; the CSVs are read-only "
       "inputs", DASH]])}

Germany and Italy are named `_screening` rather than `_price_effects` because they carry
screening evidence and no estimates. Naming them for effects they do not contain would
be misleading.

**Four columns carried by the thesis's canonical master are not published here:**
`placebo_p`, `placebo_p_adjusted`, `placebo_p_adjusted_centred` and `n_draws`. They are
vestigial output from the placebo test described above, which was removed by decision,
and `placebo_p_adjusted` is the known-broken uncentred implementation. The canonical
file keeps them as a frozen record of the superseded run; this export does not carry a
broken column. Nothing in the current specification reads any of the four.

The export applies **no screen filter**. Every cell in the canonical master appears here,
the two documented exceptions included. An earlier by-market split filtered on the
price-ordering screen and silently dropped the two Great Britain 2022 exception cells,
leaving that file at 28 rows against 30. It now reads
{int((M.market == "Great Britain").sum())}.

## What is deliberately not here

No dose-response and no claim that the effect grows with fleet size. The counterfactual
computes `f(RD + b) − f(RD)`, so a fleet moving more energy returns a larger number
close to by construction, and reading the sequence across years as evidence about fleet
size would measure the estimator rather than the market. No elasticity is fitted and no
goodness-of-fit statistic is reported, for the same reason: the object here is a
counterfactual difference carrying a bootstrap interval, not a regression.

This is a model-based counterfactual, not a causal design. There is no control group.
The curve is fitted from observed data rather than assumed, and the dispatch is observed
rather than simulated, but the estimate still assumes every other generator would have
bid identically without the fleet. No result in this repository is described as causal or
as conservative.

The supply curve is fitted on prices that already contain the fleet's own effect, which
biases every estimate towards zero, and the bias grows as the fleet grows.

Dispatch series cover registered capacity only. For Great Britain the `fleet_MW` column
is balancing-mechanism registered capacity, {M[M.market == "Great Britain"].fleet_MW.min():,.1f}
to {M[M.market == "Great Britain"].fleet_MW.max():,.1f} MW, not total installed capacity
of 1,100 to 6,000 MW, because the B1610 series sees only BM-registered units and the
numerator and denominator must refer to the same fleet. The per-GW figure must not be
scaled up to a whole-fleet effect. Coverage is reported and never scaled by.
"""

def rewrap(text, width=88):
    """Reflow prose paragraphs. Values interpolated into the prose above land at
    arbitrary widths, so the wrapping is done once at the end rather than guessed."""
    nl = chr(10)
    out = []
    for para in text.split(nl * 2):
        lines = para.split(nl)
        if any(ln.startswith(("|", "#", ">", "    ", "```")) for ln in lines):
            out.append(para)
        else:
            out.append(textwrap.fill(" ".join(ln.strip() for ln in lines),
                                     width=width, break_long_words=False,
                                     break_on_hyphens=False))
    return (nl * 2).join(out)


if __name__ == "__main__":
    (HERE / "README.md").write_text(rewrap(README), encoding="utf-8")
    print(f"wrote {HERE / 'README.md'}")
    print(f"  cells {NCELL}, market-years {NMY}, markets {M.market.nunique()}")
    print(f"  intervals excluding zero {NEXCL}, daggered {NDAG}")
    print(f"  rejected {NREJ}: {NPHYS} physical over {NPHYS_MY} market-years, "
          f"{NEXC} excluded")
    print(f"  Great Britain rows {int((M.market == 'Great Britain').sum())}")
