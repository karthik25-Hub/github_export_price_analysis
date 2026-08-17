# Battery storage and wholesale electricity prices, nine markets, 2020–2025

Numerical results supporting the price chapter of an MSc thesis at the University of
Padova. Everything here is output. The panels and the code that produced it are not in
this folder.

Nine markets are covered: South Australia, Victoria, New South Wales, Queensland, Great
Britain, CAISO, ERCOT, Germany and Italy. Seven produce price estimates. Germany and
Italy do not, for reasons given below, and carry their screening evidence instead.

## Method, in one paragraph

For each market-year a merit-order supply curve is fitted relating price to residual
demand, which is load net of wind and solar, and net of interchange in markets that
price it outside their own dispatch. The curve is fitted on 40 quantile bins of residual
demand after removing hour-of-day, weekday and month means from price, so it describes
how price moves with the quantity of dispatchable generation required rather than with
the time of day. The counterfactual asks what the price would have been at the residual
demand that would have prevailed had the fleet not operated: `P_cf(t) = P_obs(t) +
[f(RD_t + b_t) − f(RD_t)]`, where `b_t` is net battery discharge in that hour. Only the
difference between two points on the curve is used, never the curve's level, so fitting
error largely cancels and the observed price remains the anchor. Identification comes
from weather-driven variation in residual demand. Intervals are 95% day-block bootstrap
over 200 replications with the curve refitted inside each replication.

**All effects are observed minus counterfactual, so a negative value means the fleet
pushed the statistic down.**

Currency is local throughout and is never converted: AUD for the Australian regions,
EUR for Great Britain, USD for CAISO and ERCOT. Comparability across markets comes from
the `pct_of_mean_price` and `per_GW_fleet` columns, not from a common currency.

## The five outcomes

| Outcome | What it measures | Region of the curve read | Rank correlation required |
|---|---|---|---|
| Mean price | Average price across the year | Whole curve | 0.60 |
| Daily spread | Average within-day high-to-low range | Top quartile, plus the bottom quartile or a bottom share under 10% | 0.60 |
| Peak shaving | Effect on the dearest tenth of hours | Top quartile | 0.60 |
| Valley filling | Effect on the cheapest tenth of hours | Bottom quartile | 0.60 |
| Volatility | Hour-to-hour price variation | Whole curve | 0.60 |

## The two gates

Every market-year passes two independent screens before any estimate is reported.

**Physical gate.** The gross charge-to-discharge ratio must fall in the band 1.15 to
1.45, on throughput of at least 10 GWh. Batteries lose energy, so charging must exceed
discharging by roughly 11 to 18 per cent; a ratio below 1.00 is not merely unusual but
impossible, and indicates that the series is not measuring what it appears to measure.
The 10 GWh floor exists because a ratio computed on very little energy is noise.

**One documented exception: CAISO 2024, at a gross ratio of 1.1478.** That is 0.0022
short of the band, under two tenths of one per cent, and excluding a year on that margin
is not defensible. The exception is recorded in the `exception` column of all five
affected rows rather than folded silently into the retained set.

`battery_price_impact_near_misses.csv` is the justification for admitting one exception
and no others. It gives every rejected year's distance from the band:

| Market | Year | Gross ratio | Distance from band | Admitted |
|---|---|---|---|---|
| CAISO | 2021 | 1.0955 | 0.0545 | no |
| ERCOT | 2020 | 1.0491 | 0.1009 | no |
| CAISO | 2023 | 1.0243 | 0.1257 | no |
| CAISO | 2022 | 0.6348 | 0.5152 | no |
| QLD1 | 2021 | 2.3615 | 0.9115 | no |

The nearest other year is 24.8 times further from the band than the one admitted. No
other year admits the same argument, which is why the distances are published rather
than only the verdicts.

**Identification gate.** The counterfactual only works if price is actually ordered by
residual demand, so the fitted curve must return a rank correlation of at least 0.60 in
the region each outcome reads. The
governing correlation for each retained cell is in the `rho_governing` column, and the
value that failed is in `battery_price_impact_rejected.csv`.

## Reliability

**Placebo: within-day shuffle, 999 draws.** Each day's charging and discharging volumes
and its daily balance are held exactly, and only the assignment to hours within the day
is randomised. If a random schedule reproduces the effect, the estimate reflects moving
energy rather than timing it. p is reported as `(1 + #{at least as extreme}) / (R + 1)`,
which floors at 0.0010 on 999 draws.

Two p-values are given for every cell. `placebo_p` is the per-cell value and is the
headline. `placebo_p_adjusted` is a Westfall–Young max-T adjustment applied jointly
across all of a market's cells, so the statement is one joint claim rather than a set of
marginal tests. The joint version is strictly more conservative by construction.

Cells that fail the placebo are marked, never deleted. The p-value is a direct function
of the estimate's magnitude, so removing failures would select on the dependent
variable.

## How to read the market tables

Each market that produces estimates gets three tables. The first records what the
screening did, year by year, including years where nothing survived. The second gives
the effects as a percentage of that year's own mean price, which is how markets on
different currencies and price levels are compared. The third gives the reliability of
each estimate.

In the reliability table each cell reads `per-cell p / joint p · verdict`. The
per-cell p is the within-day shuffle placebo for that cell alone. The joint p is the
Westfall-Young max-T adjustment across all of that market's cells together, so it is a
single claim about the market rather than a set of separate tests, and it is strictly
the more conservative of the two.

**Placebo p floors at 0.001**, because 999 draws cannot resolve anything finer. A cell
printed as 0.001 means no draw out of 999 matched the observed estimate, not that the
p-value is precisely one in a thousand.

The verdict combines three tests: whether the 95% interval excludes zero, whether the
cell beats its own placebo, and whether it survives the joint test.

| Verdict | Meaning |
|---|---|
| firm | Interval excludes zero, beats the placebo, and survives the joint test |
| holds | Interval excludes zero and beats the placebo, but not the joint test |
| covers zero | Beats the placebo, but the interval spans zero |
| fails placebo | Interval excludes zero, but a random reshuffle matches it |
| neither | Interval spans zero and the placebo is not beaten |

An effect printed as `~0` is smaller than half a hundredth of one per cent of that
year's mean price. A dash means the cell was not estimated.

Fleet MW, mean price and gross ratio are carried only on retained rows in the source
data. Where a market-year clears the physical gate but loses all five outcomes to the
identification gate, those three columns are therefore blank: NSW1 2025, QLD1 2025 and
ERCOT 2023. That is a gap in the source data rather than a missing value invented here,
and the rows are kept rather than dropped so the screening remains visible.

## Results by market

### SA1

**Gates**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2020 | 205 | 43.49 | 1.2296 | pass | 3 of 5 | Spread, Peak |
| 2021 | 216 | 50.71 | 1.2533 | pass | 5 of 5 | — |
| 2022 | 223 | 155.89 | 1.2699 | pass | 5 of 5 | — |
| 2023 | 523 | 80.07 | 1.3404 | pass | 4 of 5 | Valley |
| 2024 | 804 | 100.11 | 1.3413 | pass | 3 of 5 | Spread, Valley |
| 2025 | 1,301 | 86.73 | 1.2474 | pass | 4 of 5 | Valley |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | +0.19 | — | — | +1.46 | -0.23 |
| 2021 | -0.02 | -9.85 | -4.70 | +2.17 | -1.23 |
| 2022 | +0.05 | -5.81 | -1.11 | +1.12 | -0.63 |
| 2023 | -0.84 | -10.45 | -5.76 | — | -1.54 |
| 2024 | -3.23 | — | -25.89 | — | -7.60 |
| 2025 | -7.87 | -63.95 | -48.40 | — | -10.45 |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | 0.328 / 0.999 · neither | — | — | 0.001 / 0.001 · firm | 0.001 / 1.000 · covers zero |
| 2021 | 1.000 / 1.000 · neither | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.775 · holds |
| 2022 | 1.000 / 1.000 · neither | 0.001 / 0.001 · firm | 0.001 / 0.998 · holds | 0.001 / 0.001 · firm | 0.001 / 0.033 · firm |
| 2023 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | — | 0.001 / 0.999 · holds |
| 2024 | 0.001 / 0.001 · firm | — | 0.001 / 0.001 · firm | — | 0.001 / 0.850 · holds |
| 2025 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | — | 0.001 / 0.125 · holds |

### VIC1

**Gates**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2020 | 60 | 51.89 | 1.2197 | pass | 3 of 5 | Spread, Peak |
| 2021 | 444 | 44.91 | 1.2691 | pass | 5 of 5 | — |
| 2022 | 444 | 134.06 | 1.2096 | pass | 5 of 5 | — |
| 2023 | 651 | 54.78 | 1.2208 | pass | 5 of 5 | — |
| 2024 | 911 | 82.13 | 1.2472 | pass | 3 of 5 | Spread, Valley |
| 2025 | 1,883 | 77.89 | 1.2108 | pass | 2 of 5 | Spread, Peak, Valley |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | -0.14 | — | — | +0.10 | -0.16 |
| 2021 | -0.03 | -1.58 | -0.92 | +0.34 | -0.22 |
| 2022 | -0.02 | -5.43 | -1.97 | +0.91 | -0.87 |
| 2023 | -0.09 | -8.40 | -3.72 | +1.78 | -1.52 |
| 2024 | -1.15 | — | -9.36 | — | -1.50 |
| 2025 | -4.98 | — | — | — | -7.27 |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | 0.001 / 0.001 · covers zero | — | — | 0.001 / 0.001 · covers zero | 0.001 / 1.000 · holds |
| 2021 | 1.000 / 1.000 · neither | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2022 | 1.000 / 1.000 · neither | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2023 | 1.000 / 1.000 · neither | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2024 | 0.001 / 0.001 · firm | — | 0.001 / 0.001 · firm | — | 0.001 / 0.711 · holds |
| 2025 | 0.001 / 0.001 · firm | — | — | — | 0.001 / 0.001 · firm |

### NSW1

**Gates**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2020 | — | — | — | fail, no dispatch | 0 of 5 | — |
| 2021 | — | — | 1.1833 | fail, 0.8 GWh throughput | 0 of 5 | — |
| 2022 | 60 | 182.71 | 1.2117 | pass | 5 of 5 | — |
| 2023 | 421 | 95.94 | 1.2503 | pass | 5 of 5 | — |
| 2024 | 1,517 | 131.02 | 1.2617 | pass | 3 of 5 | Spread, Valley |
| 2025 | — | — | — | pass | 0 of 5 | all five |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.01 | -0.29 | -0.13 | +0.06 | -0.05 |
| 2023 | -0.04 | -1.08 | -0.58 | +0.27 | -0.13 |
| 2024 | -0.23 | — | -2.21 | — | -0.30 |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | 0.044 / 0.144 · covers zero | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2023 | 0.001 / 0.001 · covers zero | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2024 | 0.001 / 0.001 · covers zero | — | 0.001 / 0.001 · firm | — | 0.001 / 0.001 · firm |

### QLD1

**Gates**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2020 | — | — | — | fail, no dispatch | 0 of 5 | — |
| 2021 | — | — | 2.3615 | fail, 0.2 GWh throughput | 0 of 5 | — |
| 2022 | 127 | 205.14 | 1.2711 | pass | 1 of 5 | Mean, Spread, Peak, Volatility |
| 2023 | 328 | 90.67 | 1.1934 | pass | 1 of 5 | Mean, Spread, Peak, Volatility |
| 2024 | 1,130 | 111.48 | 1.2270 | pass | 1 of 5 | Mean, Spread, Peak, Volatility |
| 2025 | — | — | — | pass | 0 of 5 | all five |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | — | — | — | +0.01 | — |
| 2023 | — | — | — | +0.13 | — |
| 2024 | — | — | — | +1.16 | — |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | — | — | — | 0.001 / 0.033 · firm | — |
| 2023 | — | — | — | 0.001 / 0.001 · firm | — |
| 2024 | — | — | — | 0.001 / 0.001 · firm | — |

### Great Britain

**Gates**

| Year | Fleet MW | Mean price EUR/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2020 | 274 | 39.59 | 1.2980 | pass | 5 of 5 | — |
| 2021 | 306 | 137.64 | 1.3167 | pass | 1 of 5 | Mean, Spread, Peak, Volatility |
| 2022 | 905 | 240.53 | 1.2818 | pass | 3 of 5 | Spread, Peak |
| 2023 | 2,235 | 108.00 | 1.2165 | pass | 5 of 5 | — |
| 2024 | 2,550 | 85.81 | 1.1995 | pass | 5 of 5 | — |
| 2025 | 3,931 | 94.36 | 1.1925 | pass | 5 of 5 | — |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | ~0 | -0.01 | ~0 | ~0 | ~0 |
| 2021 | — | — | — | +0.01 | — |
| 2022 | ~0 | — | — | +0.02 | -0.02 |
| 2023 | +0.06 | -0.76 | -0.13 | +0.36 | -0.13 |
| 2024 | +0.20 | -1.61 | -0.26 | +0.85 | -0.32 |
| 2025 | +0.26 | -2.59 | -0.60 | +1.26 | -0.50 |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | 0.863 / 1.000 · fails placebo | 0.002 / 1.000 · holds | 0.998 / 1.000 · neither | 0.515 / 1.000 · neither | 0.001 / 1.000 · holds |
| 2021 | — | — | — | 0.001 / 1.000 · holds | — |
| 2022 | 1.000 / 1.000 · neither | — | — | 0.001 / 0.994 · holds | 0.001 / 0.002 · firm |
| 2023 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2024 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2025 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |

### CAISO

**Gates**

| Year | Fleet MW | Mean price USD/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2021 | — | — | 1.0955 | fail, outside band | 0 of 5 | — |
| 2022 | — | — | 0.6348 | fail, outside band | 0 of 5 | — |
| 2023 | — | — | 1.0243 | fail, outside band | 0 of 5 | — |
| 2024 | 11,676 | 29.34 | 1.1478 | pass | 5 of 5 | — |
| 2025 | 15,689 | 31.18 | 1.1539 | pass | 3 of 5 | Spread, Peak |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2024 | +4.02 | -26.58 | -3.60 | +15.37 | -6.05 |
| 2025 | +3.85 | — | — | +12.75 | -4.55 |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2024 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 1.000 · holds | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |
| 2025 | 0.001 / 0.001 · firm | — | — | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |

### ERCOT

**Gates**

| Year | Fleet MW | Mean price USD/MWh | Gross ratio | Physical gate | Admitted | Blocked by identification gate |
|---|---|---|---|---|---|---|
| 2020 | — | — | 1.0491 | fail, outside band | 0 of 5 | — |
| 2021 | — | — | — | excluded, Winter Storm Uri | 0 of 5 | not screened |
| 2022 | 2,138 | 64.32 | 1.2294 | pass | 4 of 5 | Valley |
| 2023 | — | — | — | pass | 0 of 5 | all five |
| 2024 | 8,294 | 28.10 | 1.2274 | pass | 4 of 5 | Valley |
| 2025 | 13,909 | 33.50 | 1.2188 | pass | 5 of 5 | — |

**Effects, per cent of mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.16 | -0.91 | -1.48 | — | -0.33 |
| 2024 | -0.99 | -15.43 | -9.83 | — | -1.97 |
| 2025 | -1.26 | -27.71 | -16.84 | +3.20 | -5.55 |

**Reliability**, per-cell p / joint p · verdict

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | 0.001 / 0.001 · firm | 0.001 / 0.029 · firm | 0.001 / 0.001 · firm | — | 0.001 / 0.001 · firm |
| 2024 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | — | 0.001 / 0.001 · firm |
| 2025 | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm | 0.001 / 0.001 · firm |

## Reliability by outcome, whole panel

| Outcome | Cells | Interval excludes zero | Beats placebo | Survives joint test | Interval and placebo | Direction |
|---|---|---|---|---|---|---|
| Daily spread | 17 | 17 | 17 | 16 | 17 | all down |
| Volatility | 25 | 24 | 25 | 17 | 24 | all down |
| Peak shaving | 20 | 19 | 19 | 17 | 19 | all down |
| Valley filling | 21 | 19 | 20 | 18 | 19 | all up |
| Mean price | 25 | 14 | 17 | 16 | 13 | 16 down, 9 up |
| **Panel** | **108** | **93** | **98** | **84** | **92** | **78 down, 30 up** |

Sorted by the share of cells whose interval excludes zero.

## Which cells are retained, and why the rest are not

**108 of 205 possible market-year-outcome cells are retained.** The remaining 97 are in
`battery_price_impact_rejected.csv`, each with the gate it failed and the value that
failed it.

| Reason | Cells |
|---|---|
| Identification gate: price not ordered by residual demand in the region the outcome reads | 52 |
| Physical gate: ratio outside the band, throughput below 10 GWh, or no dispatch recorded | 40 |
| Excluded before estimation: ERCOT 2021 | 5 |
| **Total rejected** | **97** |

| Market | Retained | Possible |
|---|---|---|
| SA1 | 24 | 30 |
| VIC1 | 23 | 30 |
| NSW1 | 13 | 30 |
| QLD1 | 3 | 30 |
| Great Britain | 24 | 30 |
| CAISO | 8 | 25 |
| ERCOT | 13 | 30 |
| **Panel** | **108** | **205** |

CAISO has 25 possible rather than 30 because 2020 has no dispatch series at all.

ERCOT 2021 is recorded as an exclusion rather than a gate failure, because it clears
both gates and is removed on separate evidence. February 2021 carries 78.1 per cent of
that year's price mass at a monthly mean of 1,483 USD/MWh against 20 to 51 in every
other month. Prices at an administrative cap during Winter Storm Uri are not set by a
merit order. The reason is stated in the `detail` column rather than being disguised as
a screening outcome.

The rejections are a result in their own right. They identify where a merit-order method
stops working: where metering hides the charging leg, and where price stops tracking
residual demand.

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
covers 7,825 of 8,760 hours and returns an annual gross charge-to-discharge ratio of
**0.9090**, below the physical floor of 1.00 and therefore impossible. Monthly detail is
in `data/italy_screening.csv`. Three months sit inside the 1.15–1.45 band on the gross
basis the gate uses, and four on the net basis, so the count depends on which is read
and neither is enough to support an annual estimate. From September the series stops
reporting on both legs, with the discharge leg falling from 92 to 100 per cent of
intervals through August to 31 to 54 per cent afterwards. No simulated dispatch is
substituted for either market.

**Germany: the four sources checked**

| Source | What it returned |
|---|---|
| SMARD (Bundesnetzagentur) | The only storage category in either set is Pumpspeicher, pumped hydro, filter 4070 on the generation side and 4387 on the consumption side. Five further live series were found among the probed IDs, each returning a constant value across a full week (14808, 4056, 9402, 15308 and 9226 MW) |
| ENTSO-E Transparency | Absent at all ten dates. DE_LU returns 16 production types and storage appears only as B10 Hydro Pumped Storage. The identical query against the IT bidding zone returns B25 from 2025-01-01 onwards |
| MaStR via battery-charts.de (Fraunhofer ISE / RWTH) | Installed capacity and unit counts only. No operational feed is published or downloadable |
| v1 panel series Germany_storage_dispatch_hourly_2020-2025 | 59.7 TWh discharged and 75.2 TWh charged over 2020-2025 at 15-minute resolution; as carried into the hourly panel, 43.0 TWh of discharge and 58.5 TWh of charging. Mean installed capacity on the same row was 9,417 MW |

**Italy: ENTSO-E B25 by month, 2025**

| Month | Hours covered | Gross ratio | Net ratio | Inside band, gross |
|---|---|---|---|---|
| Jan | 744 | 1.1547 | 1.1656 | yes |
| Feb | 672 | 1.1275 | 1.1326 | no |
| Mar | 744 | 1.0082 | 1.0086 | no |
| Apr | 720 | 1.1222 | 1.1309 | no |
| May | 744 | 1.1265 | 1.1358 | no |
| Jun | 670 | 1.1468 | 1.1595 | no |
| Jul | 722 | 1.1531 | 1.1723 | yes |
| Aug | 744 | 1.1785 | 1.1926 | yes |
| Sep | 558 | 0.7770 | 0.7720 | no |
| Oct | 481 | 0.4578 | 0.4577 | no |
| Nov | 504 | 0.6972 | 0.6968 | no |
| Dec | 522 | 0.7246 | 0.7241 | no |
| Year | 7,825 | 0.9090 | 0.9051 | no |

## A correction to ERCOT's residual demand

ERCOT's `gen_other_mw` column was not a clean miscellaneous-generation series. It
carried half the battery fleet's own discharge. Because ERCOT's demand series is
constructed as the sum of its generation columns, that component propagated into
residual demand, and the counterfactual's `f(RD + b)` term double-counted the very
dispatch it was meant to remove.

Regressing `gen_other_mw` on battery discharge over the full sample of 52,500 hours:

| Panel | Slope on discharge | Intercept |
|---|---|---|
| Before correction | 0.4993 | 22.02 MW |
| After correction | **0.0148** | 22.82 MW |

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

## Files

| File | Contents |
|---|---|
| `battery_price_impact_master.csv` | 108 retained cells, one row per market-year-outcome, with effect, 95 per cent interval, per cent of mean price, per GW of fleet, currency, fleet MW, mean price, gross ratio, governing rank correlation, both placebo p-values, and the exception text |
| `battery_price_impact_rejected.csv` | 97 rejected cells with the gate failed, the failing value, and the reason |
| `battery_price_impact_near_misses.csv` | every rejected year's distance from the physical band, the justification for the single exception |
| `data/<market>_price_effects.csv` | each market's slice of the master, for the seven that produce estimates |
| `data/germany_screening.csv` | the four sources checked for a German dispatch series and what each returned |
| `data/italy_screening.csv` | Italian B25 by month for 2025: hours covered, gross and net ratio, and whether each month falls inside the band |
| `build_readme.py` | the script that generates every table in this README and rebuilds the workbook; the CSVs are read-only inputs |
| `battery_price_impact.xlsx` | all of the above as one workbook, a sheet per market plus an About sheet |

Germany and Italy are named `_screening` rather than `_price_effects` because they carry
screening evidence and no estimates. Naming them for effects they do not contain would
be misleading.

## What is deliberately not here

No dose-response and no claim that the effect grows with fleet size. The counterfactual
computes `f(RD + b) − f(RD)`, so a fleet moving more energy returns a larger number close
to by construction, and reading the sequence across years as evidence about fleet size
would measure the estimator rather than the market. No elasticity is fitted and no
goodness-of-fit statistic is reported, for the same reason: the object here is a
counterfactual difference carrying a bootstrap interval, not a regression.

This is a model-based counterfactual, not a causal design. There is no control group.
The curve is fitted from observed data rather than assumed, and the dispatch is observed
rather than simulated, but the estimate still assumes every other generator would have
bid identically without the fleet.

The supply curve is fitted on prices that already contain the fleet's own effect, which
biases every estimate towards zero, and the bias grows as the fleet grows.

Dispatch series cover registered capacity only. For Great Britain the `fleet_MW` column
is balancing-mechanism registered capacity, 273.8 to 3,931.0 MW, not total installed
capacity of 1,100 to 6,000 MW, because the B1610 series sees only BM-registered units and
the numerator and denominator must refer to the same fleet. The per-GW figure must not be
scaled up to a whole-fleet effect. Coverage is reported and never scaled by.
