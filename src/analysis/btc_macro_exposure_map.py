"""Build the core contemporaneous BTC macro-exposure and regime panel.

This deliberately differs from the project's D+2 UTC predictive panel.  A
dated US market observation is paired here with the BTC return ending at the
New York 17:00 close on that same date.  It is a same-session association
measure for exposure identification, never a predictive or causal design.
"""
from __future__ import annotations

from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import f as f_dist
from statsmodels.stats.diagnostic import breaks_cusumolsresid

ROOT = Path(__file__).resolve().parents[2]
FACTORS_INPUT = ROOT / "data" / "processed" / "market_factor_features.csv"
OUT = ROOT / "data" / "processed" / "btc_macro_regime_panel.csv"
TABLES, FIGURES = ROOT / "reports" / "tables", ROOT / "reports" / "figures"

# The primary six-factor model avoids close substitutes (S&P/Nasdaq, 2Y/10Y/
# real yield) in one short rolling window. Those substitutes remain in the
# univariate exposure map below.
PRIMARY = {
    "real_yield": "us_10y_real_yield_change_1d",
    "nasdaq": "nasdaq_return_1d",
    "gold": "gold_return_1d",
    "oil": "wti_return_1d",
    "usd": "broad_usd_return_1d",
    "vix": "vix_change_1d",
}
UNIVARIATE = {
    "sp500": "sp500_return_1d", "nasdaq": "nasdaq_return_1d",
    "gold": "gold_return_1d", "oil": "wti_return_1d",
    "usd": "broad_usd_return_1d", "vix": "vix_change_1d",
    "us_2y": "us_2y_yield_change_1d", "us_10y": "us_10y_yield_change_1d",
    "real_yield": "us_10y_real_yield_change_1d",
}
LABELS = {
    "sp500": "S&P 500", "nasdaq": "Nasdaq", "gold": "Gold", "oil": "WTI",
    "usd": "Broad USD", "vix": "VIX", "us_2y": "2Y yield", "us_10y": "10Y yield",
    "real_yield": "10Y real yield",
}


def hac_fit(y: pd.Series, X: pd.DataFrame):
    return sm.OLS(y, sm.add_constant(X, has_constant="add")).fit(cov_type="HAC", cov_kwds={"maxlags": 1})


def ny_17_closes() -> pd.Series:
    """BTC prices at the end of the 16:00--17:00 New York hourly candle."""
    hourly = ROOT / "data" / "raw" / "cryptodatadownload_bitstamp_btcusd_hourly.csv"
    raw = pd.read_csv(hourly, skiprows=1)
    timestamp = pd.to_datetime(raw["date"], utc=True).dt.tz_convert("America/New_York")
    close = pd.to_numeric(raw["close"], errors="coerce")
    mask = timestamp.dt.hour.eq(16)
    return pd.Series(close[mask].to_numpy(), index=timestamp[mask].dt.tz_localize(None).dt.normalize(), name="btc_ny_close").sort_index().groupby(level=0).last().dropna()


def rolling_primary(d: pd.DataFrame, window: int) -> pd.DataFrame:
    cols = ["btc_ny_return_1d", *PRIMARY.values()]
    x = d[cols].dropna()
    rows: list[dict] = []
    for end in range(window, len(x) + 1):
        sample = x.iloc[end - window:end]
        fit = hac_fit(sample.btc_ny_return_1d, sample[list(PRIMARY.values())])
        row = {"date": sample.index[-1], f"macro_r2_{window}d": fit.rsquared,
               f"macro_adj_r2_{window}d": fit.rsquared_adj}
        for short, col in PRIMARY.items():
            row[f"beta_{short}_{window}d"] = fit.params[col]
            row[f"beta_{short}_se_{window}d"] = fit.bse[col]
        rows.append(row)
    return pd.DataFrame(rows).set_index("date")


def rolling_univariate(d: pd.DataFrame, short: str, col: str, window: int) -> pd.Series:
    x = d[["btc_ny_return_1d", col]].dropna()
    values, dates = [], []
    for end in range(window, len(x) + 1):
        sample = x.iloc[end - window:end]
        values.append(sm.OLS(sample.btc_ny_return_1d, sm.add_constant(sample[col])).fit().params[col])
        dates.append(sample.index[-1])
    return pd.Series(values, index=dates, name=f"beta_{short}_uni_{window}d")


def expanding_quantile(s: pd.Series, q: float, min_periods: int = 252) -> pd.Series:
    # State at t uses only observations through t, appropriate for an observable
    # contemporaneous state and conservative enough for later deployment.
    return s.expanding(min_periods=min_periods).quantile(q)


def max_drawdown(returns: pd.Series) -> float:
    wealth = np.exp(returns.cumsum())
    return float((wealth / wealth.cummax() - 1).min())


def regime_summary(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, interactions = [], []
    factor_cols = list(PRIMARY.values())
    for dim in ("risk_regime", "monetary_regime"):
        for state, g in d.dropna(subset=["btc_ny_return_1d"]).groupby(dim, dropna=True):
            g = g.dropna(subset=[*factor_cols])
            if len(g) < 126:
                continue
            fit = hac_fit(g.btc_ny_return_1d, g[factor_cols])
            row = {
                "dimension": dim, "regime": state, "n": len(g),
                "mean_return": g.btc_ny_return_1d.mean(),
                "median_return": g.btc_ny_return_1d.median(),
                "volatility": g.btc_ny_return_1d.std(),
                "downside_volatility": g.loc[g.btc_ny_return_1d < 0, "btc_ny_return_1d"].std(),
                "annualized_sharpe_like": g.btc_ny_return_1d.mean() / g.btc_ny_return_1d.std() * np.sqrt(252),
                "max_drawdown": max_drawdown(g.btc_ny_return_1d),
                "macro_adj_r2": fit.rsquared_adj,
            }
            for short, col in PRIMARY.items():
                row[f"beta_{short}"] = fit.params[col]
            rows.append(row)

        # Pre-specified tests: equity loading in risk state, real-yield loading
        # in monetary state. They quantify a conditional association only.
        spec = {
            "risk_regime": ("nasdaq", "risk_off"),
            "monetary_regime": ("real_yield", "real_yields_rising"),
        }[dim]
        short, active_state = spec
        col = PRIMARY[short]
        z = d[["btc_ny_return_1d", *factor_cols, dim]].dropna().copy()
        z["interaction"] = z[col] * (z[dim] == active_state).astype(float)
        if len(z) >= 252:
            fit = hac_fit(z.btc_ny_return_1d, z[[*factor_cols, "interaction"]])
            interactions.append({"dimension": dim, "interaction": f"{LABELS.get(short, short)} × {active_state}",
                                 "coefficient": fit.params["interaction"], "hac_t": fit.tvalues["interaction"],
                                 "hac_p": fit.pvalues["interaction"], "n": int(fit.nobs)})
    return pd.DataFrame(rows), pd.DataFrame(interactions)


def stability_summary(d: pd.DataFrame) -> pd.DataFrame:
    """Compact stability diagnostics for the same-session six-factor model."""
    cols = ["btc_ny_return_1d", *PRIMARY.values()]
    x = d[cols].dropna()
    rows = []
    for window in (126, 252):
        for short in PRIMARY:
            beta = d[f"beta_{short}_{window}d"].dropna()
            rows.append({"test": "rolling_beta", "factor": short, "window": window,
                         "n_windows": len(beta), "mean": beta.mean(), "std": beta.std(),
                         "min": beta.min(), "max": beta.max(), "last": beta.iloc[-1]})
        r2 = d[f"macro_adj_r2_{window}d"].dropna()
        rows.append({"test": "rolling_adjusted_r2", "factor": "six_factor_model", "window": window,
                     "n_windows": len(r2), "mean": r2.mean(), "std": r2.std(),
                     "min": r2.min(), "max": r2.max(), "last": r2.iloc[-1]})

    full = sm.OLS(x.btc_ny_return_1d, sm.add_constant(x[list(PRIMARY.values())])).fit()
    stat, pvalue, _ = breaks_cusumolsresid(full.resid, ddof=len(PRIMARY) + 1)
    rows.append({"test": "cusum", "factor": "six_factor_model", "window": np.nan,
                 "n_windows": len(x), "statistic": stat, "p_value": pvalue})
    for break_date in ("2020-03-16", "2022-01-03"):
        pre = x.loc[:break_date]
        post = x.loc[pd.Timestamp(break_date) + pd.Timedelta(days=1):]
        k = len(PRIMARY) + 1
        if min(len(pre), len(post)) > k:
            pooled = full
            left = sm.OLS(pre.btc_ny_return_1d, sm.add_constant(pre[list(PRIMARY.values())])).fit()
            right = sm.OLS(post.btc_ny_return_1d, sm.add_constant(post[list(PRIMARY.values())])).fit()
            fstat = ((pooled.ssr - left.ssr - right.ssr) / k) / ((left.ssr + right.ssr) / (len(x) - 2 * k))
            rows.append({"test": "pre_specified_chow", "factor": "six_factor_model", "window": np.nan,
                         "break_date": break_date, "n_windows": len(x), "statistic": fstat,
                         "p_value": f_dist.sf(fstat, k, len(x) - 2 * k)})
    return pd.DataFrame(rows)


def make_figures(panel: pd.DataFrame, summaries: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for short in ("nasdaq", "gold", "real_yield", "usd"):
        c = f"beta_{short}_126d"
        plt.figure(figsize=(10, 3.6)); plt.plot(panel.index, panel[c], lw=.8, color="#1f77b4")
        plt.fill_between(panel.index, panel[c] - 1.96 * panel[f"beta_{short}_se_126d"], panel[c] + 1.96 * panel[f"beta_{short}_se_126d"], color="#1f77b4", alpha=.15)
        plt.axhline(0, color="black", lw=.6); plt.title(f"BTC rolling multivariate beta: {LABELS[short]} (126 observations)")
        plt.tight_layout(); plt.savefig(FIGURES / f"exposure_map_beta_{short}.png", dpi=150); plt.close()
    plt.figure(figsize=(10, 3.6)); plt.plot(panel.index, panel["macro_adj_r2_126d"], lw=.8, color="#6a4c93")
    plt.axhline(0, color="black", lw=.6); plt.title("BTC rolling six-factor macro adjusted R² (126 observations)")
    plt.tight_layout(); plt.savefig(FIGURES / "exposure_map_rolling_macro_r2.png", dpi=150); plt.close()

    heat = summaries.pivot(index=["dimension", "regime"], columns=None, values=None) if False else None
    beta_cols = ["beta_nasdaq", "beta_gold", "beta_real_yield", "beta_usd", "beta_vix"]
    h = summaries.set_index(["dimension", "regime"])[beta_cols]
    plt.figure(figsize=(8, max(3, .55 * len(h))))
    image = plt.imshow(h.values, aspect="auto", cmap="coolwarm", vmin=-np.nanmax(np.abs(h.values)), vmax=np.nanmax(np.abs(h.values)))
    plt.colorbar(image, label="multivariate beta")
    plt.xticks(range(len(beta_cols)), [x.replace("beta_", "") for x in beta_cols], rotation=25, ha="right")
    plt.yticks(range(len(h)), [f"{a}: {b}" for a, b in h.index])
    plt.title("BTC factor beta by transparent macro regime", pad=10)
    plt.tight_layout(rect=[0, 0, 1, .96]); plt.savefig(FIGURES / "exposure_map_regime_beta_heatmap.png", dpi=150); plt.close()

    # Price is deliberately on a log scale. Orange dots mark a risk state,
    # rather than suggesting that the state caused the price move.
    plt.figure(figsize=(10, 3.8)); plt.semilogy(panel.index, panel.btc_ny_close, color="black", lw=.8, label="BTC NY 17:00 close")
    stress = panel.risk_regime.eq("risk_off")
    plt.scatter(panel.index[stress], panel.loc[stress, "btc_ny_close"], s=3, color="#e76f51", alpha=.45, label="risk-off observation")
    plt.title("BTC price with transparent risk-regime observations"); plt.legend(loc="upper left", frameon=False)
    plt.tight_layout(); plt.savefig(FIGURES / "exposure_map_btc_price_risk_regime.png", dpi=150); plt.close()

    vol = summaries[summaries.dimension.isin(["risk_regime", "monetary_regime"])].copy()
    labels = [f"{d.replace('_regime','')}:\n{r.replace('_',' ')}" for d, r in zip(vol.dimension, vol.regime)]
    plt.figure(figsize=(9, 3.8)); bars = plt.bar(range(len(vol)), vol.volatility * np.sqrt(252), color=["#e76f51", "#2a9d8f", "#6a4c93", "#457b9d"])
    plt.xticks(range(len(vol)), labels); plt.ylabel("annualised BTC volatility")
    plt.title("BTC volatility across transparent regimes")
    for bar, value in zip(bars, vol.volatility * np.sqrt(252)): plt.text(bar.get_x() + bar.get_width()/2, value, f"{value:.0%}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout(); plt.savefig(FIGURES / "exposure_map_regime_volatility.png", dpi=150); plt.close()

    # One compact supplemental figure covers the retained 2Y, oil and VIX
    # exposures without turning the final figure set into a chart catalog.
    fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)
    supplemental = [
        ("beta_us_2y_uni_126d", "BTC rolling univariate beta: 2Y yield change"),
        ("beta_oil_126d", "BTC rolling multivariate beta: WTI"),
        ("beta_vix_126d", "BTC rolling multivariate beta: VIX change"),
    ]
    for ax, (col, title) in zip(axes, supplemental):
        ax.plot(panel.index, panel[col], lw=.8, color="#457b9d")
        ax.axhline(0, color="black", lw=.6); ax.set_title(title, fontsize=10)
    fig.tight_layout(); fig.savefig(FIGURES / "exposure_map_supplemental_betas.png", dpi=150); plt.close(fig)


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True); FIGURES.mkdir(parents=True, exist_ok=True)
    market = pd.read_csv(FACTORS_INPUT, parse_dates=["date"]).set_index("date").sort_index()
    closes = ny_17_closes()
    market["btc_ny_close"] = closes.reindex(market.index)
    # FRED begins long before BTC. The final panel is BTC's available history,
    # not the union of all source calendars.
    market = market.loc[market.btc_ny_close.notna()].copy()
    market["btc_ny_return_1d"] = np.log(market.btc_ny_close / market.btc_ny_close.shift(1))
    market["btc_ny_vol_20d"] = market.btc_ny_return_1d.rolling(20).std() * np.sqrt(252)
    market["btc_ny_drawdown_252d"] = market.btc_ny_close / market.btc_ny_close.rolling(252, min_periods=1).max() - 1

    # Transparent observable states. Neither state is a return forecast.
    market["vix_expanding_p75"] = expanding_quantile(market.vix, .75)
    market["risk_regime"] = pd.Series(
        np.where((market.vix >= market.vix_expanding_p75) | (market.nasdaq_return_20d < 0), "risk_off", "risk_on"),
        index=market.index, dtype="object",
    ).where(market.vix_expanding_p75.notna())
    market["monetary_regime"] = pd.Series(
        np.where(market.us_10y_real_yield_change_20d >= 0, "real_yields_rising", "real_yields_falling"),
        index=market.index, dtype="object",
    ).where(market.us_10y_real_yield_change_20d.notna())

    # Univariate raw exposure map: all retained factors, 126d primary and 252d robustness.
    for short, col in UNIVARIATE.items():
        for window in (126, 252):
            market = market.join(rolling_univariate(market, short, col, window), how="left")
    for window in (126, 252):
        market = market.join(rolling_primary(market, window), how="left")

    summary, interactions = regime_summary(market)
    stability = stability_summary(market)
    summary.to_csv(TABLES / "btc_macro_exposure_regime_summary.csv", index=False)
    interactions.to_csv(TABLES / "btc_macro_exposure_regime_interactions.csv", index=False)
    stability.to_csv(TABLES / "btc_macro_exposure_stability.csv", index=False)

    keep = ["btc_ny_close", "btc_ny_return_1d", "btc_ny_vol_20d", "btc_ny_drawdown_252d",
            *UNIVARIATE.values(), "vix", "risk_regime", "monetary_regime",
            "vix_expanding_p75"]
    rolling = [c for c in market if c.startswith(("beta_", "macro_r2_", "macro_adj_r2_"))]
    panel = market[[*keep, *rolling]].copy(); panel.index.name = "date"
    panel.to_csv(OUT)
    current_cols = ["macro_adj_r2_126d", "beta_nasdaq_126d", "beta_gold_126d", "beta_oil_126d",
                    "beta_usd_126d", "beta_vix_126d", "beta_real_yield_126d", "beta_us_2y_uni_126d",
                    "risk_regime", "monetary_regime"]
    latest = panel.dropna(subset=["macro_adj_r2_126d"]).iloc[[-1]][current_cols].copy()
    latest.insert(0, "date", latest.index)
    latest.to_csv(TABLES / "btc_macro_exposure_latest_snapshot.csv", index=False)
    make_figures(panel, summary)

    r126 = panel.macro_adj_r2_126d.dropna()
    print(f"Wrote {OUT.name}: {len(panel):,} dated market observations; 126d median adjusted R2={r126.median():.3f}")


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()
