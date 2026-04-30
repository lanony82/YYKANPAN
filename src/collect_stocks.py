"""
collect_stocks.py
-----------------
Fetches daily snapshot data for every ticker in watchlist file
and appends a row to data/YYYY-MM-DD.csv.

Usage:
    python src/collect_stocks.py               # prefer watchlist_cn.json, fallback to watchlist.txt
    python src/collect_stocks.py AAPL MSFT     # pass tickers directly

Requirements:
    pip install yfinance pandas
"""

import sys
import datetime
import pathlib
import json
import pandas as pd

from app import fetch_stock
from time_utils import BeijingTime


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


# ── Config ───────────────────────────────────────────────────────────────────
WATCHLIST_FILE = BASE_DIR / "watchlist.txt"
WATCHLIST_CN_FILE = BASE_DIR / "watchlist_cn.json"
DATA_DIR       = BASE_DIR / "data"
KEEP_DAYS      = 5
# ─────────────────────────────────────────────────────────────────────────────


def load_watchlist_txt(path: pathlib.Path) -> list[str]:
    """Read tickers from watchlist file, skipping comments and blanks."""
    tickers = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                tickers.append(line.upper())
    return tickers


def load_watchlist_cn(path: pathlib.Path) -> list[str]:
    """Read tickers from watchlist_cn.json."""
    items = json.loads(path.read_text(encoding="utf-8"))
    tickers = []
    for item in items:
        ticker = str(item.get("ticker", "")).strip().upper()
        if ticker:
            tickers.append(ticker)
    return tickers


def load_default_watchlist() -> list[str]:
    """Prefer the web watchlist; fallback to legacy watchlist.txt."""
    if WATCHLIST_CN_FILE.exists():
        tickers = load_watchlist_cn(WATCHLIST_CN_FILE)
        if tickers:
            return tickers
    if WATCHLIST_FILE.exists():
        return load_watchlist_txt(WATCHLIST_FILE)
    return []


def cleanup_old_files(data_dir: pathlib.Path, keep_days: int) -> None:
    """Keep only the newest N daily CSV files (YYYY-MM-DD.csv)."""
    files = sorted(
        [f for f in data_dir.glob("*.csv") if len(f.stem) == 10],
        key=lambda f: f.stem,
        reverse=True,
    )
    for old_file in files[keep_days:]:
        old_file.unlink(missing_ok=True)


def fetch_snapshot(ticker: str) -> dict:
    """Return a dict of key daily metrics for one ticker using app-level fallback logic."""
    result = fetch_stock(ticker, ticker)
    if result.get("error"):
        return {"ticker": ticker, "error": result["error"]}

    return {
        "date": result.get("date"),
        "ticker": result.get("ticker", ticker),
        "price": result.get("price"),
        "prev_close": result.get("prev_close"),
        "change": result.get("change"),
        "change_pct": result.get("change_pct"),
        "volume": result.get("volume"),
        "market_cap": result.get("market_cap"),
        "52w_high": result.get("high52"),
        "52w_low": result.get("low52"),
        "source": result.get("source"),
    }


def _beijing_today() -> datetime.date:
    return BeijingTime.today()


def run(tickers: list[str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    today_str = _beijing_today().isoformat()
    out_file  = DATA_DIR / f"{today_str}.csv"

    rows = []
    for ticker in tickers:
        print(f"  Fetching {ticker} ...", end=" ")
        try:
            row = fetch_snapshot(ticker)
            rows.append(row)
            if "error" in row:
                print(f"WARNING: {row['error']}")
            else:
                arrow = "▲" if row["change"] >= 0 else "▼"
                print(f"{row['price']:>10.2f}  {arrow} {row['change_pct']:+.2f}%")
        except Exception as exc:
            print(f"ERROR: {exc}")
            rows.append({"ticker": ticker, "error": str(exc)})

    df = pd.DataFrame(rows)

    # Append if file already exists (re-run safety), replace existing tickers
    if out_file.exists():
        existing = pd.read_csv(out_file)
        existing = existing[~existing["ticker"].isin(df["ticker"])]
        df = pd.concat([existing, df], ignore_index=True)

    df.to_csv(out_file, index=False)
    cleanup_old_files(DATA_DIR, KEEP_DAYS)
    print(f"\nSaved → {out_file}  ({len(rows)} tickers)")
    print(f"Retention → kept latest {KEEP_DAYS} daily files")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tickers = [t.upper() for t in sys.argv[1:]]
    else:
        tickers = load_default_watchlist()
        if not tickers:
            print(f"No watchlist found at {WATCHLIST_CN_FILE} or {WATCHLIST_FILE}")
            sys.exit(1)

    if not tickers:
        print("No tickers to fetch.")
        sys.exit(0)

    print(f"\nCollecting {len(tickers)} tickers on {_beijing_today()} (Beijing UTC+8)...\n")
    run(tickers)
