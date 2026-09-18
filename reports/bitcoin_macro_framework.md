# Bitcoin Macro Exposure Framework

## Executive Summary

This project maps Bitcoin's **changing contemporaneous risk exposures**, rather
than searching for directional return alpha from public macro data. BTC has no
stable one-line identity: it often carries equity and dollar sensitivity, but
the magnitude and even sign of its equity, gold, rate and dollar exposures vary
through time.

The primary 126-observation same-session model has a rolling adjusted R² median
of **0.191** (IQR **0.041–0.282**).
This is explanatory fit, not forecast accuracy. The practical output is a
risk-context layer: strategy signals determine *what* to trade; current factor
exposures help determine *how much* risk to take.

## 1. Research Question

**How do Bitcoin's relationships with equities, rates, gold, oil, the dollar
and market volatility change across market environments?**

The prior D+2-UTC walk-forward study found weak weekly prediction (OLS OOS R²
-0.026; Ridge -0.022). This final project therefore distinguishes prediction
from same-session exposure and does not claim stable directional forecasting.

## 2. Data and Alignment

BTC/USD is Bitstamp hourly data cut at New York 17:00; the hourly archive
supports this final alignment from 2018-05-15 to 2026-09-16. Dated FRED market moves
and LBMA gold fixes are paired with BTC's log return from NY 17:00 on D-1 to NY
17:00 on D. The intervals substantially overlap, so coefficients describe
contemporaneous co-movement, not a causal effect or a forecast. The primary
six-factor model contains real-yield change, Nasdaq, gold, WTI, broad USD and
VIX change. S&P and 2Y/10Y nominal yields are retained as univariate robustness
views rather than entered as close substitutes in each rolling window.

## 3. BTC Cross-Asset Exposure

The 126-day adjusted R² ranges from -0.018 to 0.490; the
252-day median is 0.182. The 126-day multivariate Nasdaq beta
averages 0.71 and ranges from
-1.63 to 1.77. Broad-USD
beta averages -1.16 and ranges from
-6.28 to 1.72. Gold beta averages
0.04; real-yield beta averages
0.005. Their sign variation does not support a
stable “digital gold” or fixed-rate-sensitivity narrative.

See the nine final figures in `reports/figures/`: core rolling betas carry HAC
standard-error bands within each window. Those bands display local estimation
uncertainty; they are not a multiple-testing correction.

## 4. Stability of Macro Relationships

Rolling coefficients are the primary stability evidence. The six-factor CUSUM
test has p=0.534, while pre-specified Chow-style coefficient-break
tests have p=0.000010 at 2020-03-16 and
p=0.015 at 2022-01-03. This supports
episode-specific instability without claiming that coincident historical events
caused those breaks.

## 5. Transparent Regime Analysis

Risk-off means VIX above its expanding 75th percentile or negative Nasdaq
20-day momentum. Monetary state is the sign of 20-day real-yield change. These
are observable, deliberately simple states—not optimized clusters.

| Regime | N | BTC daily vol | Nasdaq beta | Gold beta | Real-yield beta | USD beta | Macro adj. R² |
|---|---:|---:|---:|---:|---:|---:|---:|
| Risk Off | 718 | 4.14% | 0.73 | 0.15 | -0.007 | -1.21 | 0.243 |
| Risk On | 957 | 3.43% | 0.75 | 0.13 | 0.005 | -0.85 | 0.081 |
| Real Yields Falling | 924 | 3.89% | 0.78 | 0.22 | -0.013 | -0.69 | 0.081 |
| Real Yields Rising | 898 | 3.66% | 0.65 | 0.08 | 0.010 | -0.93 | 0.213 |

Risk-off has higher sample macro explanatory power and volatility than risk-on,
while the two sample Nasdaq betas are similar. The controlled Nasdaq×risk-off
interaction is not significant (HAC p=0.553); the real-yield interaction in
the rising-real-yield state is weak (p=0.570). These are
sample descriptions, not robust forecasts or causal rules.

## 6. Economic Interpretation

* **Nasdaq/S&P:** risk appetite and growth/duration-sensitive exposure.
* **2Y / real yields:** policy expectations and real discount-rate/financial
  conditions; a changing beta cautions against a fixed rates narrative.
* **Broad USD:** global dollar/financial-condition exposure; often negative but
  unstable.
* **VIX:** stress/risk aversion and volatility context, not standalone alpha.
* **Gold:** alternative-monetary comparison, not evidence BTC is digital gold.
* **Oil:** combined commodity/inflation/global-growth signal, not a direct BTC
  fundamental driver.

Traditional liquidity and crypto-native factors are excluded from the final
daily core: available public liquidity histories are revised/lag-approximated,
and crypto-native coverage would shorten the long macro sample without adding a
cleaner exposure interpretation.

## 7. Practical Framework

Use rolling beta, rolling macro R² and volatility as a risk-context layer.
Directional signals can require greater confidence and smaller sizing in a
stress/high-exposure state. Funding/basis strategies can reduce leverage and
holding-period tolerance; market makers can reduce inventory limits and hedge
more urgently. The framework informs **how much** and **which type** of risk is
acceptable; a separate strategy determines **what** to trade.

## 8. Limitations

Correlation is not causation; contemporaneous regression is not prediction;
transparent regimes are imperfect; the NY-close exposure sample starts in 2018;
BTC is a single-exchange price series; and
FRED histories are current revisions rather than point-in-time vintages.
Crypto-specific shocks can dominate, especially when macro R² is low.

## Conclusion

BTC is best treated as a **time-varying cross-asset risk exposure**. It often
shares equity and dollar risk, while gold, rates and overall macro explanatory
power shift materially across time. This supports a rolling exposure/risk
framework, not a claim of reliable public-macro directional alpha.
