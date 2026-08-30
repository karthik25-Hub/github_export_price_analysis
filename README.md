# Battery storage and wholesale electricity prices, nine markets, 2020–2025

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

Currency is local throughout and is never converted: AUD for the Australian regions, EUR
for Great Britain, USD for CAISO and ERCOT. Comparability across markets comes from the
`pct_of_mean_price` and `per_GW_fleet` columns, not from a common currency.

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

| Outcome | What it measures | Region of the curve read |
|---|---|---|
| Mean price | Average price across the year | Whole curve |
| Daily spread | Average within-day high-to-low range | Top quartile, plus the bottom quartile or a bottom share under 10% |
| Peak shaving | Effect on the dearest tenth of hours | Top quartile |
| Valley filling | Effect on the cheapest tenth of hours | Bottom quartile |
| Volatility | Hour-to-hour price variation | Whole curve |

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
silently into the retained set.

`battery_price_impact_near_misses.csv` is the justification for admitting the physical
exception and no others. It gives every rejected year's distance from the band:

| Market | Year | Gross ratio | Distance from band | Admitted |
|---|---|---|---|---|
| CAISO | 2021 | 1.0955 | 0.0545 | no |
| CAISO | 2022 | 0.6348 | 0.5152 | no |
| CAISO | 2023 | 1.0243 | 0.1257 | no |
| ERCOT | 2020 | 1.0491 | 0.1009 | no |
| QLD1 | 2021 | 2.3615 | 0.9115 | no |

The nearest other year is 24.8 times further from the band than the one admitted. No
other year admits the same argument, which is why the distances are published rather
than only the verdicts.

## Reliability

**Intervals are 95 per cent day-block bootstrap, 200 replications, with the curve
refitted inside each replication.** Whole days are resampled rather than hours, because
a battery's schedule is a within-day object and resampling hours would break it. The
interval is the only uncertainty statement made about any cell.

**A cell marked † has an interval covering zero.** 14 of 160 cells carry the mark. They
are shown rather than deleted, because a small effect estimated precisely enough to be
indistinguishable from zero is a finding about that market-year, not a failure to be
hidden.

| Market | Year | Outcome | Effect | 95% interval |
|---|---|---|---|---|
| Great Britain | 2020 | Peak shaving | -0.0001 | [-0.0030, 0.0028] |
| Great Britain | 2021 | Mean price | -0.0048 | [-0.0225, 0.0082] |
| NSW1 | 2022 | Mean price | -0.0197 | [-0.0573, 0.0170] |
| NSW1 | 2023 | Mean price | -0.0241 | [-0.1146, 0.0235] |
| NSW1 | 2024 | Mean price | -0.4387 | [-1.0810, 0.0086] |
| NSW1 | 2025 | Mean price | -1.1952 | [-2.7520, 0.1029] |
| SA1 | 2020 | Volatility | -0.1666 | [-0.4658, 0.3510] |
| SA1 | 2021 | Mean price | -0.0221 | [-0.2591, 0.1892] |
| SA1 | 2022 | Mean price | -0.1853 | [-0.6284, 0.1154] |
| SA1 | 2023 | Mean price | -0.5013 | [-1.0734, 0.0259] |
| VIC1 | 2020 | Mean price | -0.0696 | [-0.2206, 0.0164] |
| VIC1 | 2021 | Mean price | -0.0146 | [-0.0521, 0.0152] |
| VIC1 | 2022 | Mean price | -0.1939 | [-0.5286, 0.0810] |
| VIC1 | 2023 | Mean price | -0.1167 | [-0.2713, 0.0026] |

Twelve of the 14 are mean price. That outcome averages a rise in the cheapest hours
against a fall in the dearest, so the two legs largely cancel and the net is close to
zero in the markets with small fleets.

**There is no placebo test and no multiple-testing correction.** Both were carried by an
earlier specification and both were removed by decision. The within-day shuffle placebo
discriminated almost nothing: 97 of 108 cells sat at its floor of 0.001, nine of the ten
failures already had intervals covering zero, and it is close to guaranteed to pass by
construction, because batteries charge cheap and discharge dear by design and the fitted
curve is forced weakly increasing. The Westfall–Young max-T adjustment went with it, and
its implementation was in any case uncentred and returned exactly 1.000 on 30 cells. The
columns they wrote are not published here. They survive in the thesis's frozen canonical
master as a record of the superseded run, and nothing in the current specification reads
them.

## Results by market

Effects are given twice: as a per cent of that year's own mean price, which is how
markets on different currencies and price levels are compared, and in local currency
with the 95 per cent interval. An effect printed as `~0` is smaller than half a
hundredth of one per cent of that year's mean price. † marks an interval covering zero.
A dash means the market-year produced no estimate.

Every market-year that clears the physical screen retains all five outcomes, so the
screening table's last column reads 5 of 5 throughout.

### SA1

**Screening**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2020 | 205 | 43.49 | 1.2296 | pass | 5 of 5 |
| 2021 | 216 | 50.71 | 1.2533 | pass | 5 of 5 |
| 2022 | 223 | 155.89 | 1.2699 | pass | 5 of 5 |
| 2023 | 523 | 80.07 | 1.3404 | pass | 5 of 5 |
| 2024 | 804 | 100.11 | 1.3413 | pass | 5 of 5 |
| 2025 | 1,392 | 86.73 | 1.2474 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | +0.26 | -5.04 | -1.02 | +2.21 | -0.38† |
| 2021 | -0.04† | -14.60 | -6.44 | +2.85 | -1.65 |
| 2022 | -0.12† | -8.35 | -1.95 | +0.86 | -0.98 |
| 2023 | -0.63† | -17.97 | -7.62 | +2.58 | -2.30 |
| 2024 | -3.51 | -52.74 | -30.78 | +4.61 | -9.11 |
| 2025 | -9.10 | -95.89 | -60.09 | +5.57 | -13.74 |

**Effects, AUD/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | +0.1144 [0.0030, 0.1800] | -2.1916 [-3.4400, -1.5673] | -0.4438 [-1.1854, -0.0678] | +0.9626 [0.6395, 1.1961] | -0.1666 [-0.4658, 0.3510] † |
| 2021 | -0.0221 [-0.2591, 0.1892] † | -7.4035 [-12.0835, -5.2610] | -3.2657 [-5.3563, -1.5943] | +1.4424 [1.1233, 1.8159] | -0.8376 [-1.5811, -0.5433] |
| 2022 | -0.1853 [-0.6284, 0.1154] † | -13.0090 [-17.6211, -10.5526] | -3.0454 [-5.7964, -1.1814] | +1.3342 [0.9511, 1.9417] | -1.5216 [-2.8292, -0.8963] |
| 2023 | -0.5013 [-1.0734, 0.0259] † | -14.3920 [-21.0122, -10.0483] | -6.0984 [-10.1344, -2.5033] | +2.0652 [1.5825, 2.5980] | -1.8395 [-3.1246, -1.0681] |
| 2024 | -3.5117 [-6.5501, -1.2918] | -52.7989 [-88.7569, -34.6565] | -30.8103 [-51.9765, -14.7788] | +4.6179 [3.7126, 5.5851] | -9.1217 [-17.4532, -3.6101] |
| 2025 | -7.8885 [-15.5828, -2.6749] | -83.1669 [-165.5698, -38.3026] | -52.1174 [-112.1016, -15.7580] | +4.8275 [3.9202, 5.6221] | -11.9212 [-27.8603, -3.8818] |

### VIC1

**Screening**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2020 | 60 | 51.89 | 1.2197 | pass | 5 of 5 |
| 2021 | 444 | 44.91 | 1.2691 | pass | 5 of 5 |
| 2022 | 444 | 134.06 | 1.2096 | pass | 5 of 5 |
| 2023 | 651 | 54.78 | 1.2208 | pass | 5 of 5 |
| 2024 | 911 | 82.13 | 1.2472 | pass | 5 of 5 |
| 2025 | 1,885 | 77.89 | 1.2108 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | -0.13† | -1.89 | -1.57 | +0.27 | -0.19 |
| 2021 | -0.03† | -2.61 | -1.31 | +0.62 | -0.33 |
| 2022 | -0.14† | -9.98 | -2.95 | +1.55 | -1.44 |
| 2023 | -0.21† | -12.40 | -5.20 | +2.08 | -2.11 |
| 2024 | -1.03 | -25.51 | -11.67 | +2.01 | -2.07 |
| 2025 | -5.85 | -76.79 | -55.27 | +3.11 | -9.48 |

**Effects, AUD/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | -0.0696 [-0.2206, 0.0164] † | -0.9827 [-2.2472, -0.3489] | -0.8129 [-2.1150, -0.1325] | +0.1421 [0.1119, 0.1711] | -0.0994 [-0.3189, -0.0448] |
| 2021 | -0.0146 [-0.0521, 0.0152] † | -1.1708 [-1.5543, -0.9122] | -0.5864 [-0.9322, -0.3982] | +0.2776 [0.2068, 0.3636] | -0.1462 [-0.1883, -0.1272] |
| 2022 | -0.1939 [-0.5286, 0.0810] † | -13.3773 [-17.6344, -10.7371] | -3.9561 [-5.8190, -2.2918] | +2.0750 [1.5225, 2.4976] | -1.9337 [-2.5927, -1.4880] |
| 2023 | -0.1167 [-0.2713, 0.0026] † | -6.7903 [-8.4094, -5.9425] | -2.8473 [-4.0943, -1.9707] | +1.1406 [0.9203, 1.4317] | -1.1568 [-1.4302, -0.9955] |
| 2024 | -0.8439 [-2.2462, -0.0657] | -20.9495 [-42.3377, -11.2158] | -9.5819 [-21.0081, -2.8488] | +1.6503 [1.2115, 1.8628] | -1.7003 [-5.5256, -0.7180] |
| 2025 | -4.5576 [-8.8634, -0.9281] | -59.8061 [-104.3060, -23.9764] | -43.0481 [-79.6727, -11.4022] | +2.4247 [1.7977, 3.0377] | -7.3816 [-15.1861, -4.1178] |

### NSW1

**Screening**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2020 | — | — | — | fail, no discharge recorded | 0 of 5 |
| 2021 | — | — | 1.1833 | fail, throughput 0.8 GWh below the 10 GWh floor | 0 of 5 |
| 2022 | 60 | 182.71 | 1.2117 | pass | 5 of 5 |
| 2023 | 421 | 95.94 | 1.2503 | pass | 5 of 5 |
| 2024 | 1,517 | 131.02 | 1.2617 | pass | 5 of 5 |
| 2025 | 3,536 | 103.32 | 1.4006 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.01† | -0.79 | -0.24 | +0.14 | -0.10 |
| 2023 | -0.03† | -2.39 | -1.01 | +0.73 | -0.25 |
| 2024 | -0.34† | -10.15 | -3.99 | +0.87 | -0.57 |
| 2025 | -1.16† | -20.01 | -11.83 | +1.12 | -2.12 |

**Effects, AUD/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.0197 [-0.0573, 0.0170] † | -1.4369 [-1.9881, -1.2335] | -0.4332 [-0.8079, -0.2520] | +0.2633 [0.2346, 0.3483] | -0.1826 [-0.3213, -0.1247] |
| 2023 | -0.0241 [-0.1146, 0.0235] † | -2.2918 [-3.4361, -1.7537] | -0.9660 [-1.6608, -0.5794] | +0.7017 [0.5950, 0.8216] | -0.2391 [-0.3619, -0.1694] |
| 2024 | -0.4387 [-1.0810, 0.0086] † | -13.3040 [-24.0295, -8.1131] | -5.2236 [-10.4556, -2.1189] | +1.1374 [0.9882, 1.2896] | -0.7475 [-2.0295, -0.3766] |
| 2025 | -1.1952 [-2.7520, 0.1029] † | -20.6738 [-38.2583, -9.1775] | -12.2260 [-24.1126, -2.4539] | +1.1555 [0.8311, 1.5508] | -2.1938 [-4.7549, -0.7841] |

### QLD1

**Screening**

| Year | Fleet MW | Mean price AUD/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2020 | — | — | — | fail, no discharge recorded | 0 of 5 |
| 2021 | — | — | 2.3615 | fail, throughput 0.2 GWh below the 10 GWh floor | 0 of 5 |
| 2022 | 127 | 205.14 | 1.2711 | pass | 5 of 5 |
| 2023 | 328 | 90.67 | 1.1934 | pass | 5 of 5 |
| 2024 | 1,130 | 111.48 | 1.2270 | pass | 5 of 5 |
| 2025 | 2,603 | 84.89 | 1.2051 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.23 | -4.19 | -1.26 | +0.47 | -0.34 |
| 2023 | -0.28 | -5.12 | -2.54 | +0.77 | -0.57 |
| 2024 | -1.47 | -23.33 | -11.75 | +1.56 | -2.67 |
| 2025 | -5.39 | -73.24 | -31.46 | +2.31 | -5.59 |

**Effects, AUD/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.4678 [-0.8195, -0.1480] | -8.6038 [-12.4842, -5.0058] | -2.5910 [-4.2092, -0.9999] | +0.9581 [0.7696, 1.1880] | -0.7080 [-1.0981, -0.2629] |
| 2023 | -0.2555 [-0.4869, -0.1136] | -4.6445 [-7.1834, -3.3868] | -2.3026 [-3.4188, -1.4286] | +0.7000 [0.5874, 0.8380] | -0.5183 [-0.8470, -0.3912] |
| 2024 | -1.6394 [-2.7352, -0.8889] | -26.0100 [-41.0078, -16.6859] | -13.1010 [-19.9993, -7.9382] | +1.7383 [1.5074, 2.0891] | -2.9713 [-5.7370, -1.4637] |
| 2025 | -4.5797 [-9.4810, -0.5570] | -62.1751 [-128.2804, -15.9283] | -26.7108 [-51.8036, -6.2254] | +1.9589 [1.4088, 2.8351] | -4.7435 [-10.6369, -1.8420] |

### Great Britain

**Screening**

| Year | Fleet MW | Mean price EUR/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2020 | 274 | 39.59 | 1.2980 | pass | 5 of 5 |
| 2021 | 306 | 137.64 | 1.3167 | pass | 5 of 5 |
| 2022 | 905 | 240.53 | 1.2818 | pass | 5 of 5 |
| 2023 | 2,235 | 108.00 | 1.2165 | pass | 5 of 5 |
| 2024 | 2,550 | 85.81 | 1.1995 | pass | 5 of 5 |
| 2025 | 3,931 | 94.36 | 1.1925 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | +0.01 | -0.04 | ~0† | +0.01 | ~0 |
| 2021 | ~0† | -0.35 | -0.15 | +0.01 | -0.09 |
| 2022 | +0.02 | -0.61 | -0.09 | +0.13 | -0.07 |
| 2023 | +0.09 | -2.35 | -0.41 | +0.56 | -0.28 |
| 2024 | +0.45 | -4.97 | -0.81 | +1.90 | -0.81 |
| 2025 | +0.68 | -8.69 | -1.98 | +3.46 | -1.53 |

**Effects, EUR/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2020 | +0.0033 [0.0022, 0.0042] | -0.0147 [-0.0270, -0.0085] | -0.0001 [-0.0030, 0.0028] † | +0.0055 [0.0008, 0.0105] | -0.0015 [-0.0033, -0.0003] |
| 2021 | -0.0048 [-0.0225, 0.0082] † | -0.4831 [-0.8099, -0.2574] | -0.2109 [-0.3861, -0.1136] | +0.0204 [0.0075, 0.0428] | -0.1191 [-0.2316, -0.0480] |
| 2022 | +0.0530 [0.0103, 0.1075] | -1.4782 [-2.0689, -1.0687] | -0.2106 [-0.4684, -0.0033] | +0.3028 [0.1435, 0.5162] | -0.1662 [-0.3053, -0.0834] |
| 2023 | +0.0988 [0.0346, 0.1983] | -2.5384 [-3.2852, -2.0649] | -0.4392 [-0.5375, -0.2943] | +0.6075 [0.3098, 1.1593] | -0.3078 [-0.4501, -0.2321] |
| 2024 | +0.3852 [0.2227, 0.5099] | -4.2640 [-5.4624, -3.4317] | -0.6980 [-1.0434, -0.4282] | +1.6341 [0.8354, 2.3061] | -0.6924 [-0.8841, -0.4922] |
| 2025 | +0.6392 [0.4795, 0.8152] | -8.1969 [-10.0617, -6.9311] | -1.8653 [-2.7598, -0.9908] | +3.2633 [2.5354, 4.0680] | -1.4434 [-1.7344, -1.1965] |

### CAISO

**Screening**

| Year | Fleet MW | Mean price USD/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2021 | — | — | 1.0955 | fail, gross ratio 1.0955 below the 1.15-1.45 band by 0.0545 | 0 of 5 |
| 2022 | — | — | 0.6348 | fail, gross ratio 0.6348 below the 1.15-1.45 band by 0.5152 | 0 of 5 |
| 2023 | — | — | 1.0243 | fail, gross ratio 1.0243 below the 1.15-1.45 band by 0.1257 | 0 of 5 |
| 2024 | 11,676 | 32.68 | 1.1478 | pass | 5 of 5 |
| 2025 | 15,689 | 32.19 | 1.1539 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2024 | +3.73 | -106.57 | -31.29 | +30.38 | -20.07 |
| 2025 | +7.04 | -60.48 | -10.79 | +28.12 | -15.76 |

**Effects, USD/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2024 | +1.2200 [0.1785, 2.0784] | -34.8220 [-43.2284, -28.8874] | -10.2247 [-15.5550, -6.1403] | +9.9264 [6.8536, 12.9456] | -6.5582 [-8.3665, -5.0841] |
| 2025 | +2.2657 [1.5482, 3.1281] | -19.4689 [-24.5174, -16.5783] | -3.4736 [-4.5293, -2.5745] | +9.0523 [6.6071, 12.5225] | -5.0746 [-6.4122, -4.1369] |

### ERCOT

**Screening**

| Year | Fleet MW | Mean price USD/MWh | Gross ratio | Physical screen | Retained |
|---|---|---|---|---|---|
| 2020 | — | — | 1.0491 | fail, gross ratio 1.0491 below the 1.15-1.45 band by 0.1009 | 0 of 5 |
| 2021 | — | — | — | excluded before screening | 0 of 5 |
| 2022 | 2,138 | 64.32 | 1.2294 | pass | 5 of 5 |
| 2023 | 4,178 | 55.95 | 1.2530 | pass | 5 of 5 |
| 2024 | 8,294 | 28.10 | 1.2274 | pass | 5 of 5 |
| 2025 | 13,909 | 33.50 | 1.2188 | pass | 5 of 5 |

**Effects, per cent of that year's mean price**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.14 | -1.47 | -1.76 | +0.09 | -0.40 |
| 2023 | -1.32 | -14.18 | -13.88 | +0.12 | -4.95 |
| 2024 | -0.97 | -21.46 | -12.52 | +1.19 | -2.65 |
| 2025 | -1.44 | -40.55 | -22.97 | +5.76 | -7.78 |

**Effects, USD/MWh**

| Year | Mean price | Daily spread | Peak shaving | Valley filling | Volatility |
|---|---|---|---|---|---|
| 2022 | -0.0899 [-0.1508, -0.0407] | -0.9422 [-1.2981, -0.6523] | -1.1314 [-1.6920, -0.7045] | +0.0545 [0.0422, 0.0696] | -0.2582 [-0.4203, -0.1614] |
| 2023 | -0.7410 [-1.1642, -0.3754] | -7.9344 [-12.4867, -3.8390] | -7.7643 [-11.9545, -4.1281] | +0.0645 [0.0499, 0.0747] | -2.7674 [-4.5299, -1.3181] |
| 2024 | -0.2733 [-0.6322, -0.0532] | -6.0305 [-10.5828, -3.1260] | -3.5181 [-6.2231, -1.6408] | +0.3351 [0.2835, 0.3877] | -0.7458 [-1.4122, -0.3573] |
| 2025 | -0.4835 [-0.8223, -0.2370] | -13.5824 [-17.7886, -10.4039] | -7.6937 [-10.4710, -5.4770] | +1.9311 [1.6212, 2.2778] | -2.6071 [-3.5664, -1.9852] |

## Reliability by outcome, whole panel

| Outcome | Cells | Interval excludes zero | Interval covers zero | Direction |
|---|---|---|---|---|
| Daily spread | 32 | 32 | 0 | all down |
| Valley filling | 32 | 32 | 0 | all up |
| Peak shaving | 32 | 31 | 1 | all down |
| Volatility | 32 | 31 | 1 | all down |
| Mean price | 32 | 20 | 12 | 24 down, 8 up |
| **Panel** | **160** | **146** | **14** | **120 down, 40 up** |

Sorted by the share of cells whose interval excludes zero. Daily spread and valley
filling are unanimous in sign and unanimous in excluding zero. Mean price is the outcome
that does not settle: eight of its 32 cells are positive, and twelve have intervals
covering zero.

## Which cells are retained, and why the rest are not

**160 of 205 possible market-year-outcome cells are retained**, across 32 market-years
and seven markets. The remaining 45 are in `battery_price_impact_rejected.csv`, each
with the screen it failed and the value that failed it.

| Reason | Market-years | Cells |
|---|---|---|
| Physical dispatch screen: ratio outside the band, throughput below 10 GWh, or no dispatch recorded | 8 | 40 |
| Excluded before estimation: ERCOT 2021 | 1 | 5 |
| Price-ordering screen | 0 | 0 |
| **Total rejected** | **9** | **45** |

| Market | Retained | Possible |
|---|---|---|
| SA1 | 30 | 30 |
| VIC1 | 30 | 30 |
| NSW1 | 20 | 30 |
| QLD1 | 20 | 30 |
| Great Britain | 30 | 30 |
| CAISO | 10 | 25 |
| ERCOT | 20 | 30 |
| **Panel** | **160** | **205** |

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

| Outcome | Real-time, superseded | Day-ahead, published here |
|---|---|---|
| Mean price | +1.1787 | +1.2200 |
| Daily spread | -7.7971 | -34.8220 |
| Peak shaving | -1.0553 | -10.2247 |
| Valley filling | +4.5102 | +9.9264 |
| Volatility | -1.7747 | -6.5582 |

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
basis the screen uses, and four on the net basis, so the count depends on which is read
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

## Files

| File | Contents | Supports |
|---|---|---|
| `battery_price_impact_master.csv` | 160 retained cells, one row per market-year-outcome, with effect, 95 per cent interval, per cent of mean price, per GW of fleet, currency, fleet MW, mean price, gross ratio, governing rank correlation, and the exception text | Chapters 4 and 5 |
| `battery_price_impact_rejected.csv` | 45 rejected cells with the screen failed, the failing value, and the reason | Chapters 3 and 5 |
| `battery_price_impact_near_misses.csv` | every rejected year's distance from the physical band, the justification for the single physical exception | Chapter 3 |
| `data/<market>_price_effects.csv` | each market's slice of the master, for the seven that produce estimates | Chapter 5 |
| `data/germany_screening.csv` | the four sources checked for a German dispatch series and what each returned | Chapter 3 |
| `data/italy_screening.csv` | Italian B25 by month for 2025: hours covered, gross and net ratio, and whether each month falls inside the band | Chapter 3 |
| `battery_price_impact.xlsx` | all of the above as one workbook, a sheet per market plus an About sheet | all of the above |
| `build_readme.py` | the script that generates every table in this README; the CSVs are read-only inputs | — |

Germany and Italy are named `_screening` rather than `_price_effects` because they carry
screening evidence and no estimates. Naming them for effects they do not contain would
be misleading.

**Four columns carried by the thesis's canonical master are not published here:**
`placebo_p`, `placebo_p_adjusted`, `placebo_p_adjusted_centred` and `n_draws`. They are
vestigial output from the placebo test described above, which was removed by decision,
and `placebo_p_adjusted` is the known-broken uncentred implementation. The canonical
file keeps them as a frozen record of the superseded run; this export does not carry a
broken column. Nothing in the current specification reads any of the four.

The export applies **no screen filter**. Every cell in the canonical master appears
here, the two documented exceptions included. An earlier by-market split filtered on the
price-ordering screen and silently dropped the two Great Britain 2022 exception cells,
leaving that file at 28 rows against 30. It now reads 30.

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
bid identically without the fleet. No result in this repository is described as causal
or as conservative.

The supply curve is fitted on prices that already contain the fleet's own effect, which
biases every estimate towards zero, and the bias grows as the fleet grows.

Dispatch series cover registered capacity only. For Great Britain the `fleet_MW` column
is balancing-mechanism registered capacity, 273.8 to 3,931.0 MW, not total installed
capacity of 1,100 to 6,000 MW, because the B1610 series sees only BM-registered units
and the numerator and denominator must refer to the same fleet. The per-GW figure must
not be scaled up to a whole-fleet effect. Coverage is reported and never scaled by.