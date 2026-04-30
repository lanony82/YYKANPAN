"""
summary.py
----------
Print a quick summary table from all collected CSV files in data/.

Usage:
    python src/summary.py           # show today's data
    python src/summary.py all       # show all historical data
    python src/summary.py 2026-04-28  # show a specific date
"""

import sys
import pathlib
import datetime
import pandas as pd
from time_utils import BeijingTime

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"


def _beijing_today() -> datetime.date:
    return BeijingTime.today()


def load(date_str: str | None = None) -> pd.DataFrame:
    if not DATA_DIR.exists() or not list(DATA_DIR.glob("*.csv")):
        print("No data yet. Run collect_stocks.py first.")
        sys.exit(0)

    if date_str == "all":
        frames = [pd.read_csv(f) for f in sorted(DATA_DIR.glob("*.csv"))]
        return pd.concat(frames, ignore_index=True)

    if date_str:
        f = DATA_DIR / f"{date_str}.csv"
    else:
        f = DATA_DIR / f"{_beijing_today().isoformat()}.csv"

    if not f.exists():
        available = sorted(p.stem for p in DATA_DIR.glob("*.csv"))
        print(f"No file for {date_str or 'today'}. Available: {available}")
        sys.exit(1)

    return pd.read_csv(f)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    df = load(arg)

    # Keep only rows without errors
    df = df[df.get("error", pd.Series(dtype=str)).isna()] if "error" in df.columns else df

    if df.empty:
        print("No successful quote rows to display yet.")
        print("Data file exists, but all rows currently contain fetch errors.")
        return

    # Older/partial files might miss some columns; fill minimal defaults so sorting works.
    if "date" not in df.columns:
        df["date"] = _beijing_today().isoformat()
    if "change_pct" not in df.columns:
        df["change_pct"] = 0.0

    cols = ["date", "ticker", "price", "change_pct", "volume", "market_cap", "pe_ratio", "52w_high", "52w_low"]
    cols = [c for c in cols if c in df.columns]
    df = df[cols].sort_values(["date", "change_pct"], ascending=[True, False])

    pd.set_option("display.max_rows", 200)
    pd.set_option("display.float_format", "{:,.2f}".format)
    pd.set_option("display.width", 120)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
