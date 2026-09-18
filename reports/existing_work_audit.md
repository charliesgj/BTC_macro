# Existing-work audit — BTC macro-regime project

Audit date: 2026-09-17. This review inspected the repository tree, README, all
analysis/data/feature modules, reports, figures, tables, cached datasets and
the prior research discussion. There are no notebooks and no separate TODO or
project-log file. This document is the baseline for the reframed project: it
does not rerun valid analyses.

## 1. Work already completed

### Questions investigated

1. Do public macro and cross-asset variables explain or forecast BTC returns?
   This was tested at daily and weekly frequencies with strict chronological
   designs.
2. Are factor exposures stable? Rolling correlations/betas, CUSUM and two
   pre-specified Chow tests were run.
3. Do simple risk and real-yield states alter BTC behaviour? A first,
   intentionally small regime screen was completed.
4. Does post-New-York-close public information forecast BTC's subsequent
   24-hour/5-day return or volatility? It was tested separately using hourly
   BTC data.
5. Do M2, Fed assets and reverse repo variables contain timing-aware signal?
   Preliminary release-event tests were completed.
6. What do public on-chain/cycle variables, halving timing, BTC--gold residual
   co-movement, weekend volatility, and ETH/SOL beta asymmetry show? These are
   documented side investigations, not all part of the core macro framework.

### Cached sources and coverage

| Block | Cached source | Main coverage / caveat |
|---|---|---|
| BTC price/volume | CryptoDataDownload Bitstamp daily and hourly BTC/USD | Daily 2014-11-28--2026-09-17; single-exchange fallback, not a composite index. |
| Traditional markets | FRED: DGS2, DGS10, DFII10, EFFR, SP500, NASDAQCOM, VIXCLS, DTWEXBGS, DCOILWTICO | Current revised histories, not ALFRED vintages. |
| Gold | Official LBMA AM fixing | Business-day fixing; used with documented pragmatic alignment. |
| Traditional liquidity | FRED: M2SL, WALCL, RRPONTSYD | M2 availability is conservatively approximated by +35 days; revised-history caveat remains. |
| BTC network | Coin Metrics Community archive | Supply, issuance, active addresses, transactions, hash rate, MVRV and fees; cache ends 2026-05-24. |
| Crypto derivatives | Binance BTCUSDT funding archive | Monthly raw files through 2026-08. |
| Side assets | Binance ETH/USDT and SOL/USDT daily; CFTC gold COT; GPR; FRED CPI/industrial production/high-yield spread/breakevens | Used only in documented side/gold work. |

`data_dictionary.csv` documents the original Milestone-1 block, but has not
yet been extended to every later on-chain, funding, liquidity and side-series
field. No stablecoin (total, USDT, or USDC) history is cached.

### Variables constructed

The main `milestone1_daily_aligned.csv` has BTC close and volume; 1/5/20-day
log returns; 1/5/20/60-day forward returns; 20-day annualised realized
volatility; 20-day momentum; and 252-day drawdown. It also has levels and
1/5/20-day changes for 2Y, 10Y, 10Y real yields, EFFR and 2s10s; 1/5/20-day
returns/volatility for S&P 500, Nasdaq, broad USD, gold and WTI; and VIX
levels/changes.

The liquidity panel has post-availability M2 growth, Fed-assets growth and
RRP changes. The public chain panel has supply, daily issuance proxies, active
addresses, transactions, MVRV/realized-price proxies, hash-ribbon state,
miner-revenue/Puell-like proxy, and halving-age/epoch. Daily on-chain states
are shifted one day. Funding is a separate, one-day-lagged extension.

### Alignment and reproducibility already in place

For the original daily **predictive** panel, a US observation dated D is made
effective at D+2 UTC. Friday information therefore appears once on Sunday; no
weekend TradFi return is fabricated or silently forward-filled. Assertions
check that a source observation never enters before D+2. Low-frequency states
are carried forward only after their effective date, while event regressions
use real update dates. Raw downloads are cached and scripts are modular.

This is a strong conservative design for prediction. It is **not** the best
primary timestamp convention for the reframed question of *contemporaneous
market exposure*: it deliberately pairs a dated market move with BTC returns
starting two days later. The repository already has a NY-17:00 BTC-close helper
for a better exposure-oriented alignment, but no full macro exposure panel
based on it. This is a methodological gap, not evidence that prior prediction
results are invalid.

### Regressions, models and diagnostics already run

* HAC univariate contemporaneous/predictive screens for every core factor and
  1/5/20/60-day BTC horizon (`milestone1_univariate_hac_regressions.csv`).
  ADF and KPSS diagnostics accompany these; price/yield levels were not used
  blindly as regression factors.
* Six-factor OLS/HAC benchmark: real-yield change, Nasdaq, gold, WTI, broad
  USD and VIX. VIF, condition number, Breusch--Pagan and Ljung--Box diagnostics
  were produced for horizons 1/5/20/60.
* OLS, standardized OLS and fixed-alpha Ridge expanding-window weekly return
  forecasts, plus univariate and historical-mean benchmarks. Scaling occurs
  inside each training window.
* Post-NY-close univariate HAC mean-return/absolute-return tests and
  expanding-median high-VIX interactions.
* Timing-aware univariate liquidity event tests; chronological on-chain and
  on-chain-plus-funding drawdown-state screens.
* BTC--gold weekly factor-residual correlation/diversification exercise.

No random time-series split was used. No regularized macro model was tuned for
best OOS performance. Lasso/Elastic Net, PCA, VAR, Granger, local projections,
HMM/GMM, autoencoders and neural networks have not been run.

### Stability and regime work already run

* Rolling **univariate** 126/252/504-observation BTC betas for real yields,
  Nasdaq, gold, USD, VIX and WTI, with figures and summary table.
* CUSUM of the six-factor 1-day model (p=0.046) and pre-specified Chow-style
  tests at 2020-03-16 (p=0.000053) and 2022-01-03 (p=0.00569).
* Transparent two-state screens: risk-off when VIX is above its full-sample
  median or Nasdaq 20-day momentum is negative; and real-yields
  rising/falling by 20-day real-yield change. Regime performance and two
  factor-interaction tests were saved.

Those results motivate time variation, but the existing states use the
predictive D+2 panel and use a full-sample VIX median in one screen. They are
an exploratory predecessor, not the final real-time/identity regime map.

## 2. Main empirical findings to retain

1. **Return prediction is weak.** The 1-day six-factor adjusted R² is 0.0032;
   5-day is 0.0021; 20-day is -0.0010; 60-day is -0.0003. Weekly OOS R² versus
   the expanding historical mean is -0.026 for OLS macro and -0.022 for Ridge;
   the best listed univariate (gold) is only 0.001. This is useful negative
   evidence, not an invitation to search more transformations.
2. **This weak fit is not a multicollinearity artefact.** The daily six-factor
   maximum VIF is 2.44 and standardized condition number is 2.89. Standardizing
   OLS leaves its forecasts unchanged, as it should.
3. **The exposure relationship appears unstable.** CUSUM and the two
   pre-specified break tests reject stable coefficients at conventional levels;
   rolling univariate betas also change sign/magnitude over windows. This is a
   hypothesis for a disciplined regime framework, not proof of named causes.
4. **Initial simple states are suggestive, not conclusive.** For example, the
   Nasdaq beta is 0.108 in the existing risk-off screen and -0.158 in risk-on,
   but the controlled Nasdaq interaction has HAC p=0.109. The real-yield
   interaction has p=0.329. Descriptive state differences need a cleaner,
   exposure-specific implementation and uncertainty bands.
5. **Post-close public macro variables do not forecast mean BTC returns.**
   However, VIX level explains about 2.1% of next-24-hour absolute BTC-return
   variation (HAC p<0.001), and VIX change about 0.7% (p=0.007). This is a
   volatility/risk-budget result, not directional alpha.
6. **Liquidity/on-chain predictive results are also weak or preliminary.** M2
   and RRP screens are near zero; Fed-assets 4-week growth has a 20-day
   adjusted R² of 0.0072 (p=0.0006), but this is one result in a small,
   revised-vintage multiple-test screen. On-chain 90-day drawdown OOS AUC is
   0.509 (core) and 0.538 (with funding), with negative Brier skill.
7. **BTC and gold are not interchangeable directional assets in this sample.**
   Weekly raw correlation is 0.126 and factor-residual correlation is 0.004;
   this can support diversification, but BTC's much larger volatility rules
   out treating it as a conventional safe haven. It does not establish an
   alternative-monetary regime.
8. **The four-year/halving study cannot validate a cycle law.** Only two
   completed halving-to-halving intervals are observable from the reliable
   price history. Halving is a protocol event, not identified macro causality.

## 3. Classification against the reframed proposed work

| Proposed task | Status | Audit judgement / minimum action |
|---|---|---|
| Preserve rates, equities, VIX, USD, gold and WTI factor set in stationary transformations | **DONE** | Reuse cached series and feature construction. Add no duplicate downloader. |
| Preserve traditional liquidity variables with publication discipline | **PARTIALLY DONE** | Timing-aware M2/WALCL/RRP panel exists; release lags/vintages are approximations/current revisions. Use as descriptive state only until ALFRED/release-calendar work is added. |
| Preserve crypto-native block | **PARTIALLY DONE** | BTC network, halving and funding exist; stablecoin total/USDT/USDC do not. Extend documentation and obtain stablecoins only for an explanatory state extension. |
| Rolling correlations/betas for all requested exposures | **PARTIALLY DONE** | Correlations broadly exist; beta figures are univariate and cover six factors, not full 2Y/10Y/S&P set nor a multivariate rolling beta/R² map. Build one primary, correctly aligned exposure panel plus limited robustness windows. |
| Full rolling multivariate exposure map (`beta_t`, rolling R²) | **NOT DONE** | This is the highest-value new core analysis. It requires NY-close/contemporaneous exposure alignment, separate from predictive data. |
| Macro-identity labels (risk, monetary/gold-like, crypto-idiosyncratic, stress) | **NOT DONE** | Infer from the new exposure map and transparent state summaries; do not pre-impose four labels. |
| Simple monetary, liquidity and risk regimes | **PARTIALLY DONE** | Two exploratory dimensions exist. Rebuild with expanding/available thresholds and adequate cell counts on the exposure panel; avoid a large cross-product. |
| Regime conditional risk/return/beta/R² and HAC interaction tests | **PARTIALLY DONE** | Partial tables and two interactions exist. Extend only to the core exposures and final regimes. |
| Expanding coefficients, confidence bands, multiple-break/change-point testing | **PARTIALLY DONE** | Rolling, CUSUM and two Chow tests exist. Add confidence intervals/expanding estimates; use a parsimonious change-point test only if it clarifies the plot. Do not add Bai--Perron merely as a checklist item. |
| Transparent cross-asset identity score | **NOT DONE** | Implement only if the exposure map yields stable, interpretable dimensions; otherwise report states rather than a synthetic score. |
| PCA for interpretation and rolling BTC factor exposure | **NOT DONE** | Worth a compact, training-window/expanding implementation after the primary panel; it may reduce redundant factor monitoring. It is not a forecasting exercise. |
| HMM/GMM clustering | **NOT USEFUL** | Skip initially. The sample already shows instability, and opaque state fitting would add more labels before transparent regimes are validated. |
| VAR, Granger and local projections | **NOT USEFUL** | Skip in this reframing: weak OOS return evidence and non-causal interpretation mean they do not answer the practical exposure-map question better than rolling/regime regressions. |
| Stablecoin/on-chain incremental explanatory-power extension | **PARTIALLY DONE** | On-chain/funding state data exist but are not integrated with macro exposure; stablecoins missing. Build only after the traditional exposure map, on its shorter overlap. |
| Repeat/tune return-prediction ML, XGBoost, NN, autoencoder | **NOT USEFUL** | Existing daily/weekly OOS and gold-XGBoost evidence is weak; further tuning would be data mining under the new objective. |
| Practical strategy/risk application layer | **NOT DONE** | Add after empirical regimes: risk budget, leverage/inventory/hedge urgency and volatility limits, explicitly not a trading rule. |
| `btc_macro_regime_panel.csv` dashboard dataset | **NOT DONE** | Create as the durable output of the new exposure/regime stage. |
| Core figures and unified research report | **PARTIALLY DONE** | Several precursor figures/reports exist; no consolidated dashboard figures or `bitcoin_macro_regime_research.md`. Reuse rather than duplicate. |
| Four-year cycle as a timing/explanatory framework | **NOT USEFUL** | Keep the existing limitation/report; do not deepen price-cycle claims with two independent completed cycles. |
| Further gold return forecasting | **NOT USEFUL** | Explicitly closed after poor OOS results; retain only the BTC--gold co-movement/diversification result. |

## 4. Remaining gaps and smallest justified plan

The smallest credible increment is not a larger predictor search. It is:

1. **Build a separate contemporaneous exposure panel.** Use the existing
   Bitstamp hourly NY-17:00 BTC close and dated market returns so a factor move
   is paired with BTC movement over the same market session. Retain the D+2
   panel unchanged for the already-completed prediction work. Document exactly
   which intervals overlap and do not call it causal.
2. **Create a parsimonious rolling multivariate map.** Primary 126-day window,
   with 252-day robustness; track core individual univariate betas, selected
   multivariate betas, HAC/OLS uncertainty approximation, and rolling R².
   Include S&P/2Y/10Y as sensitivity views, not collinear duplicates in every
   multivariate specification.
3. **Rebuild transparent risk/monetary/liquidity states on this panel.** Use
   expanding historical thresholds or simple sign/trend states; report sample
   sizes, return/volatility/downside/drawdown, factor loads, R² and HAC
   interactions. Liquidity will initially be a flagged, revised-history
   descriptive extension rather than a real-time claim.
4. **Only then assess PCA.** Fit it expanding-window for interpretation,
   inspect loadings and retain it only if it provides a clearer, lower-
   dimensional exposure view than the raw map.
5. **Deliver the panel, figures and unified report.** Add a concise practical
   risk application layer. Stablecoins are the next separate short-sample
   extension, not a precondition for completing the long macro framework.

The planned work directly answers how BTC's *risk exposure* changes while
preserving the negative result on stable directional predictability.
