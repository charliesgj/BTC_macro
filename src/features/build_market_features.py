"""Build stationary same-session market factors for the final exposure map."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "market_factor_features.csv"
FRED = {
    "us_2y_yield": "DGS2", "us_10y_yield": "DGS10", "us_10y_real_yield": "DFII10",
    "effective_fed_funds": "EFFR", "sp500": "SP500", "nasdaq": "NASDAQCOM",
    "vix": "VIXCLS", "broad_usd": "DTWEXBGS", "wti": "DCOILWTICO",
}


def fred_series(name: str, code: str) -> pd.Series:
    raw = pd.read_csv(RAW / f"fred_{code}.csv")
    dates = pd.to_datetime(raw.iloc[:, 0])
    values = pd.to_numeric(raw.iloc[:, 1], errors="coerce")
    return pd.Series(values.to_numpy(), index=dates, name=name).sort_index()


def gold_series() -> pd.Series:
    raw = pd.DataFrame(json.loads((RAW / "lbma_gold_am.json").read_text()))
    return pd.Series(pd.to_numeric(raw.v.str[0], errors="coerce").to_numpy(), index=pd.to_datetime(raw.d), name="gold").sort_index()


def log_return(s: pd.Series, periods: int) -> pd.Series:
    # WTI's April-2020 negative settlement is left missing instead of being
    # transformed into an artificial log return.
    return np.log(s.where(s > 0)).diff(periods)


def main() -> None:
    factors = pd.concat([*[fred_series(name, code) for name, code in FRED.items()], gold_series()], axis=1)
    factors["curve_2s10s"] = factors.us_10y_yield - factors.us_2y_yield
    for col in ("us_2y_yield", "us_10y_yield", "us_10y_real_yield", "effective_fed_funds", "curve_2s10s"):
        factors[f"{col}_change_1d"] = factors[col].diff()
        factors[f"{col}_change_20d"] = factors[col].diff(20)
    for col in ("sp500", "nasdaq", "broad_usd", "gold", "wti"):
        factors[f"{col}_return_1d"] = log_return(factors[col], 1)
        factors[f"{col}_return_20d"] = log_return(factors[col], 20)
    factors["vix_change_1d"] = factors.vix.diff()
    # The NY-close BTC archive starts here; retaining older macro-only rows
    # would add no usable observations to the final panel.
    factors = factors.loc["2018-05-15":].copy()
    factors.index.name = "date"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    factors.to_csv(OUT)
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(factors):,} dated market observations")


if __name__ == "__main__":
    main()
