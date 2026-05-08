"""P1 tests for server.py — trading session logic & _get_stocks_snapshot."""

from __future__ import annotations

import pathlib
import sys
import threading
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import server as stock_app


# ── _is_cn_trading_session ───────────────────────────────────────────────────

class TestIsCnTradingSession:
    """Verify trading-session detection based on Beijing time."""

    def _patch_bj_now(self, dt: datetime):
        return patch.object(stock_app, "_bj_now", return_value=dt)

    def test_weekend_saturday(self):
        # 2026-01-03 is a Saturday
        with self._patch_bj_now(datetime(2026, 1, 3, 10, 0)):
            assert stock_app._is_cn_trading_session() is False

    def test_weekend_sunday(self):
        # 2026-01-04 is a Sunday
        with self._patch_bj_now(datetime(2026, 1, 4, 10, 0)):
            assert stock_app._is_cn_trading_session() is False

    def test_holiday(self):
        # 2026-01-01 is a holiday (Thursday)
        with self._patch_bj_now(datetime(2026, 1, 1, 10, 0)):
            assert stock_app._is_cn_trading_session() is False

    def test_within_trading_hours(self):
        # 2026-01-05 is a Monday, 10:00 is within 09:15–15:30
        with self._patch_bj_now(datetime(2026, 1, 5, 10, 0)):
            assert stock_app._is_cn_trading_session() is True

    def test_at_open_boundary(self):
        # 09:15 exactly → True
        with self._patch_bj_now(datetime(2026, 1, 5, 9, 15)):
            assert stock_app._is_cn_trading_session() is True

    def test_at_close_boundary(self):
        # 15:30 exactly → True (boundary inclusive)
        with self._patch_bj_now(datetime(2026, 1, 5, 15, 30)):
            assert stock_app._is_cn_trading_session() is True

    def test_before_open(self):
        # 08:00 → False
        with self._patch_bj_now(datetime(2026, 1, 5, 8, 0)):
            assert stock_app._is_cn_trading_session() is False

    def test_after_close(self):
        # 15:31 → False
        with self._patch_bj_now(datetime(2026, 1, 5, 15, 31)):
            assert stock_app._is_cn_trading_session() is False

    def test_labor_day_holiday(self):
        # 2026-05-01 is a holiday
        with self._patch_bj_now(datetime(2026, 5, 1, 10, 0)):
            assert stock_app._is_cn_trading_session() is False

    def test_national_day_holiday(self):
        # 2026-10-01 is a holiday
        with self._patch_bj_now(datetime(2026, 10, 1, 10, 0)):
            assert stock_app._is_cn_trading_session() is False


# ── _get_stocks_snapshot ─────────────────────────────────────────────────────

SAMPLE_STOCK = {
    "ticker": "600519.SS", "name": "贵州茅台", "price": 1800.0,
    "prev_close": 1780.0, "change": 20.0, "change_pct": 1.12,
    "volume": 100000, "high52": 2000.0, "low52": 1500.0,
    "market_cap": 2e12, "date": "2026-01-05", "source": "akshare",
    "error": None,
}


class TestGetStocksSnapshot:
    """Verify cache, off-hours CSV fallback, and live-fetch branches."""

    def setup_method(self):
        """Reset module-level cache before each test."""
        stock_app.STOCKS_CACHE_DATA = None
        stock_app.STOCKS_CACHE_TS = 0.0

    def test_cache_hit_returns_immediately(self):
        """If cache is fresh, return cached data without locking."""
        stock_app.STOCKS_CACHE_DATA = [SAMPLE_STOCK]
        stock_app.STOCKS_CACHE_TS = time.time()

        result = stock_app._get_stocks_snapshot()
        assert result == [SAMPLE_STOCK]

    @patch.object(stock_app, "_is_cn_trading_session", return_value=False)
    @patch.object(stock_app, "_load_latest_csv", return_value=[SAMPLE_STOCK])
    def test_off_hours_with_csv(self, mock_csv, mock_session):
        """Outside trading → load CSV data."""
        result = stock_app._get_stocks_snapshot()
        assert result == [SAMPLE_STOCK]
        mock_csv.assert_called_once()

    @patch.object(stock_app, "_is_cn_trading_session", return_value=False)
    @patch.object(stock_app, "_load_latest_csv", return_value=None)
    @patch.object(stock_app, "load_watchlist", return_value=[
        {"ticker": "600519.SS", "name": "贵州茅台"},
    ])
    def test_off_hours_no_csv_returns_placeholders(self, mock_wl, mock_csv, mock_session):
        """Outside trading + no CSV → offline placeholders."""
        result = stock_app._get_stocks_snapshot()
        assert len(result) == 1
        assert result[0]["source"] == "offline"
        assert result[0]["price"] is None

    @patch.object(stock_app, "_is_cn_trading_session", return_value=True)
    @patch.object(stock_app, "load_watchlist", return_value=[
        {"ticker": "600519.SS", "name": "贵州茅台"},
    ])
    @patch.object(stock_app, "fetch_stock", return_value=SAMPLE_STOCK)
    @patch.object(stock_app, "_save_stocks_csv")
    def test_trading_hours_calls_fetch(self, mock_save, mock_fetch, mock_wl, mock_session):
        """During trading → fetch live data and save CSV."""
        result = stock_app._get_stocks_snapshot()
        assert result == [SAMPLE_STOCK]
        mock_fetch.assert_called_once_with("600519.SS", "贵州茅台")
        mock_save.assert_called_once()

    @patch.object(stock_app, "_is_cn_trading_session", return_value=False)
    @patch.object(stock_app, "_load_latest_csv", return_value=[SAMPLE_STOCK])
    def test_force_refresh_bypasses_cache(self, mock_csv, mock_session):
        """force_refresh=True ignores in-memory cache."""
        stock_app.STOCKS_CACHE_DATA = [{"old": True}]
        stock_app.STOCKS_CACHE_TS = time.time()

        result = stock_app._get_stocks_snapshot(force_refresh=True)
        assert result == [SAMPLE_STOCK]


class TestDoubleCheckedLocking:
    """Verify that concurrent requests only trigger one scan."""

    @patch.object(stock_app, "_is_cn_trading_session", return_value=False)
    @patch.object(stock_app, "_load_latest_csv", return_value=[SAMPLE_STOCK])
    def test_concurrent_requests_single_scan(self, mock_csv, mock_session):
        """Multiple threads should not all call _load_latest_csv independently."""
        stock_app.STOCKS_CACHE_DATA = None
        stock_app.STOCKS_CACHE_TS = 0.0
        results = []
        barrier = threading.Barrier(4)

        def worker():
            barrier.wait()
            r = stock_app._get_stocks_snapshot()
            results.append(r)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert len(results) == 4
        # All got the same data
        for r in results:
            assert r == [SAMPLE_STOCK]
        # CSV loaded at most twice (first call + possible race before lock)
        assert mock_csv.call_count <= 2
