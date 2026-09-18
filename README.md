# Bitcoin Macro Exposure Framework

## Research question

**How do Bitcoin's cross-asset risk exposures change across market
environments?** This is an explanatory risk-framework project—not a claim
that public macro variables generate stable directional BTC alpha.

## Approach

The project aligns Bitstamp BTC/USD hourly data (2018-05-15 onward) to the New York 17:00 close and
pairs each BTC return with same-date changes/returns in Nasdaq, S&P 500, 2Y and
10Y Treasury yields, 10Y real yields, gold, WTI, broad USD and VIX. A rolling,
six-factor 126-observation regression maps contemporaneous BTC betas and
adjusted R²; a 252-observation version is a robustness check. Transparent
risk-on/off and real-yields-rising/falling states summarize how exposures and
risk differ across environments.

The archived prediction study uses a different D+2 UTC availability convention
and found weak weekly OOS performance (OLS R² -0.026; Ridge -0.022). It is not
part of the final inference and is not mixed with the same-session exposure
panel.

## Key findings

* BTC's 126-observation rolling macro adjusted R² has a median of **0.191**
  (IQR 0.041–0.282), indicating material but time-varying same-session macro
  co-movement.
* The rolling multivariate Nasdaq beta averages **0.71**, but ranges from
  **-1.63 to 1.77**. Dollar, gold and real-yield betas also change sign.
* In the transparent sample, risk-off macro adjusted R² is 0.243 versus 0.081
  in risk-on; volatility is higher, but Nasdaq beta is similar (0.73 versus
  0.75). The controlled interaction has p=0.553, so this is not a robust rule.
* BTC therefore has no stable “tech,” “digital gold,” or purely idiosyncratic
  identity. The useful product is a rolling risk-context layer.

## Repository structure

```text
data/raw/                         cached source inputs
data/processed/btc_macro_regime_panel.csv
src/data/download_milestone1.py   cache public market data
src/features/build_market_features.py  build stationary dated market factors
src/analysis/btc_macro_exposure_map.py
reports/bitcoin_macro_framework.md
reports/figures/                  final publication figures
reports/tables/                   final numerical outputs
data_dictionary.csv               sources, transformations and timing
```

## Reproduction

From the repository root, install the packages in `requirements.txt`, then run:

```bash
python -m src.data.download_milestone1
python -m src.features.build_market_features
MPLCONFIGDIR=/tmp/btc_macro_mpl python -m src.analysis.btc_macro_exposure_map
python -m src.analysis.render_final_report
```

The first command uses cached raw files unless `--refresh` is deliberately
provided. The exposure command writes the processed panel, all final tables and
all final figures; the report command renders the markdown report from those
outputs.

## Limitations

Same-session regressions are associations, not causal estimates or forecasts.
BTC is represented by a single-exchange series; FRED histories are current
revisions rather than point-in-time vintages; and transparent regime rules are
imperfect. Crypto-specific shocks may dominate when rolling macro R² is low.
