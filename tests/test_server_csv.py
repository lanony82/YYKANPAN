"""P1 tests for CSV persistence: _save_stocks_csv / _load_latest_csv round-trip."""

from __future__ import annotations

import pathlib
import sys
from unittest.mock import patch

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import server as stock_app


# ── Helpers ──────────────────────────────────────────────────────────────────

SAMPLE_ROWS = [
    {
        "ticker": "600519.SS",
        "name": "贵州茅台",
        "price": 1580.0,
        "prev_close": 1575.5,
        "change": 4.5,
        "change_pct": 0.29,
        "volume": 12345678,
        "market_cap": 1980000000000,
        "high52": 1800.0,
        "low52": 1300.0,
        "date": "2026-05-08",
        "source": "akshare",
        "error": None,
    },
    {
        "ticker": "000858.SZ",
        "name": "五粮液",
        "price": 150.2,
        "prev_close": 149.0,
        "change": 1.2,
        "change_pct": 0.81,
        "volume": 9876543,
        "market_cap": 583000000000,
        "high52": 180.0,
        "low52": 120.5,
        "date": "2026-05-08",
        "source": "sina",
        "error": None,
    },
]


@pytest.fixture()
def tmp_data_dir(tmp_path, monkeypatch):
    """Redirect cfg.DATA_DIR to a temp directory for each test."""
    monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)
    # Also patch the date string so file names are deterministic
    monkeypatch.setattr(stock_app, "_bj_date_str", lambda: "2026-05-08")
    return tmp_path


# ── Round-trip ───────────────────────────────────────────────────────────────

class TestCSVRoundTrip:
    """_save_stocks_csv → _load_latest_csv should preserve data fidelity."""

    def test_basic_round_trip(self, tmp_data_dir):
        stock_app._save_stocks_csv(SAMPLE_ROWS)
        loaded = stock_app._load_latest_csv()

        assert loaded is not None
        assert len(loaded) == 2

        row0 = loaded[0]
        assert row0["ticker"] == "600519.SS"
        assert row0["name"] == "贵州茅台"
        assert row0["source"] == "akshare"

    def test_float_fields_restored(self, tmp_data_dir):
        stock_app._save_stocks_csv(SAMPLE_ROWS)
        loaded = stock_app._load_latest_csv()

        row = loaded[0]
        for field in ("price", "prev_close", "change", "change_pct", "high52", "low52"):
            assert isinstance(row[field], float), f"{field} should be float, got {type(row[field])}"

        assert row["price"] == 1580.0
        assert row["change_pct"] == 0.29
        assert row["high52"] == 1800.0
        assert row["low52"] == 1300.0

    def test_int_fields_restored(self, tmp_data_dir):
        stock_app._save_stocks_csv(SAMPLE_ROWS)
        loaded = stock_app._load_latest_csv()

        row = loaded[0]
        for field in ("volume", "market_cap"):
            assert isinstance(row[field], int), f"{field} should be int, got {type(row[field])}"

        assert row["volume"] == 12345678
        assert row["market_cap"] == 1980000000000

    def test_none_52w_preserved(self, tmp_data_dir):
        """Rows with None high52/low52 should load back as None."""
        rows = [
            {
                "ticker": "600036.SS",
                "name": "招商银行",
                "price": 35.0,
                "prev_close": 34.5,
                "change": 0.5,
                "change_pct": 1.45,
                "volume": 5000000,
                "market_cap": 900000000000,
                "high52": None,
                "low52": None,
                "date": "2026-05-08",
                "source": "akshare",
                "error": None,
            }
        ]
        stock_app._save_stocks_csv(rows)
        loaded = stock_app._load_latest_csv()

        assert loaded[0]["high52"] is None
        assert loaded[0]["low52"] is None


# ── Edge cases ───────────────────────────────────────────────────────────────

class TestCSVEdgeCases:
    """Error rows, empty data, and cleanup behavior."""

    def test_error_rows_skipped_on_save(self, tmp_data_dir):
        """Rows with error flag should be excluded from the CSV."""
        rows = [
            {**SAMPLE_ROWS[0]},
            {"ticker": "BAD.XX", "name": "bad", "error": "fetch failed"},
        ]
        stock_app._save_stocks_csv(rows)
        loaded = stock_app._load_latest_csv()

        assert loaded is not None
        assert len(loaded) == 1
        assert loaded[0]["ticker"] == "600519.SS"

    def test_all_error_rows_no_file_written(self, tmp_data_dir):
        """If every row has an error, no CSV should be written at all."""
        rows = [{"ticker": "X", "error": "fail"}]
        stock_app._save_stocks_csv(rows)

        csv_files = list(tmp_data_dir.glob("*.csv"))
        assert len(csv_files) == 0

    def test_empty_list_no_file(self, tmp_data_dir):
        stock_app._save_stocks_csv([])
        csv_files = list(tmp_data_dir.glob("*.csv"))
        assert len(csv_files) == 0

    def test_load_returns_none_when_no_data_dir(self, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", pathlib.Path("/nonexistent/dir"))
        assert stock_app._load_latest_csv() is None

    def test_load_returns_none_when_dir_empty(self, tmp_data_dir):
        assert stock_app._load_latest_csv() is None

    def test_error_field_normalized_to_none(self, tmp_data_dir):
        """Empty error string in CSV should become None on load."""
        rows = [{**SAMPLE_ROWS[0], "error": ""}]
        stock_app._save_stocks_csv(rows)
        loaded = stock_app._load_latest_csv()

        assert loaded[0]["error"] is None

    def test_old_csv_cleanup(self, tmp_data_dir, monkeypatch):
        """Only the most recent _CSV_KEEP_DAYS files should survive."""
        # Create 7 fake dated CSV files
        for day in range(1, 8):
            f = tmp_data_dir / f"2026-05-{day:02d}.csv"
            f.write_text("ticker\n600519.SS\n", encoding="utf-8")

        # Now save a new one (date is patched to 2026-05-08)
        stock_app._save_stocks_csv(SAMPLE_ROWS)

        csv_files = sorted(tmp_data_dir.glob("*.csv"))
        # _CSV_KEEP_DAYS is 5, so we should have at most 5 files
        assert len(csv_files) <= stock_app._CSV_KEEP_DAYS
