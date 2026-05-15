"""
collect_stocks.py
-----------------
Fetches daily snapshot data for every ticker in watchlist file
and saves to data/YYYY-MM-DD.csv.

Usage:
    python src/collect_stocks.py               # prefer watchlist_cn.json, fallback to watchlist.txt
    python src/collect_stocks.py AAPL MSFT     # pass tickers directly
"""

import sys
import csv
import pathlib

# Allow running as standalone script: python src/data/collect_stocks.py
_SRC_DIR = str(pathlib.Path(__file__).resolve().parent.parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from config import cfg, load_watchlist
from data.providers import fetch_stock
from time_utils import BeijingTime


CSV_FIELDS = [
    "ticker", "name", "price", "prev_close", "change", "change_pct",
    "volume", "market_cap", "high52", "low52", "date", "source", "error",
]
KEEP_DAYS = 5


def cleanup_old_files(data_dir: pathlib.Path, keep_days: int) -> None:
    """Keep only the newest N daily CSV files (YYYY-MM-DD.csv)."""
    files = sorted(
        [f for f in data_dir.glob("*.csv") if len(f.stem) == 10],
        key=lambda f: f.stem,
        reverse=True,
    )
    for old_file in files[keep_days:]:
        old_file.unlink(missing_ok=True)


def run(tickers: list[str]) -> None:
    data_dir = cfg.DATA_DIR
    data_dir.mkdir(exist_ok=True)

    rows = []
    for ticker in tickers:
        print(f"  Fetching {ticker} ...", end=" ")
        try:
            row = fetch_stock(ticker, ticker)
            rows.append(row)
            if row.get("error"):
                print(f"WARNING: {row['error']}")
            else:
                change = row.get("change") or 0
                arrow = "▲" if change >= 0 else "▼"
                print(f"{row.get('price', 0):>10.2f}  {arrow} {(row.get('change_pct') or 0):+.2f}%")
        except Exception as exc:
            print(f"ERROR: {exc}")
            rows.append({"ticker": ticker, "error": str(exc)})

    # Use the date from the fetched data (= last trading day)
    dates = [r.get("date") for r in rows if r.get("date")]
    save_date = max(dates) if dates else BeijingTime.date_str()
    out_file = data_dir / f"{save_date}.csv"

    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    cleanup_old_files(data_dir, KEEP_DAYS)
    valid = [r for r in rows if not r.get("error")]
    print(f"\nSaved → {out_file}  ({len(valid)}/{len(rows)} valid)")
    print(f"Retention → kept latest {KEEP_DAYS} daily files")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tickers = [t.upper() for t in sys.argv[1:]]
    else:
        wl = load_watchlist()
        tickers = [s["ticker"] for s in wl]
        if not tickers:
            print(f"No watchlist found at {cfg.WATCHLIST_PATH}")
            sys.exit(1)

    if not tickers:
        print("No tickers to fetch.")
        sys.exit(0)

    print(f"\nCollecting {len(tickers)} tickers on {BeijingTime.date_str()} (Beijing UTC+8)...\n")
    run(tickers)
