"""Cache public daily sources used in the first research milestone.

Raw downloads are intentionally retained untouched.  Re-running without
--refresh is offline/reproducible once the cache exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
FRED = {
    "us_2y_yield": "DGS2",
    "us_10y_yield": "DGS10",
    "us_10y_real_yield": "DFII10",
    "effective_fed_funds": "EFFR",
    "sp500": "SP500",
    "nasdaq_composite": "NASDAQCOM",
    "vix": "VIXCLS",
    "broad_usd": "DTWEXBGS",
    "wti": "DCOILWTICO",
}
BTC_HOURLY_URL = "https://www.cryptodatadownload.com/cdd/Bitstamp_BTCUSD_1h.csv"
LBMA_GOLD_URL = "https://prices.lbma.org.uk/json/gold_am.json"


def fetch(url: str) -> bytes:
    # curl is used rather than requests because this research environment
    # routes command-line HTTPS reliably while Python's TLS client can time out.
    result = subprocess.run(
        ["curl", "-L", "--fail", "--silent", "--show-error", "--retry", "2", "--connect-timeout", "15", "--max-time", "120", url],
        check=True, capture_output=True,
    )
    return result.stdout


def cache(name: str, url: str, refresh: bool, metadata: dict) -> None:
    path = RAW / name
    if path.exists() and not refresh:
        content = path.read_bytes()
        metadata[name] = {"url": url, "cached": True, "path": str(path.relative_to(ROOT)),
                          "sha256": hashlib.sha256(content).hexdigest()}
        return
    content = fetch(url)
    path.write_bytes(content)
    metadata[name] = {
        "url": url,
        "cached": False,
        "path": str(path.relative_to(ROOT)),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="replace cached raw files")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    metadata: dict = {}
    for name, series in FRED.items():
        cache(f"fred_{series}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}", args.refresh, metadata)
    cache("lbma_gold_am.json", LBMA_GOLD_URL, args.refresh, metadata)
    cache("cryptodatadownload_bitstamp_btcusd_hourly.csv", BTC_HOURLY_URL, args.refresh, metadata)
    (RAW / "download_manifest.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(f"Cached {len(metadata)} sources in {RAW}")


if __name__ == "__main__":
    main()
