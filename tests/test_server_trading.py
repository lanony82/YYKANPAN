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
    @patch.object(stock_app, "fetch_stock", return_value=SAMPLE_STOCK)
    @patch.object(stock_app, "_save_stocks_csv")
    def test_off_hours_no_csv_falls_through_to_live(self, mock_save, mock_fetch, mock_wl, mock_csv, mock_session):
        """Outside trading + no CSV → falls through to live fetch."""
        result = stock_app._get_stocks_snapshot()
        assert len(result) == 1
        assert result[0]["price"] == SAMPLE_STOCK["price"]
        mock_fetch.assert_called_once()

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


# ── Advisor save-decision endpoint ──────────────────────────────────────────

class TestAdvisorSaveDecision:
    """Test POST /api/advisor/save-decision."""

    @pytest.fixture(autouse=True)
    def _client_and_tmp(self, tmp_path, monkeypatch):
        from trading import decision as dec_mod
        tmp_file = tmp_path / "decisions.json"
        monkeypatch.setattr(dec_mod, "_DECISIONS_FILE", tmp_file)
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()
        self.dec_mod = dec_mod

    def test_save_basic(self):
        resp = self.client.post("/api/advisor/save-decision", json={
            "ticker": "600519.SS",
            "name": "贵州茅台",
            "action": "sell",
            "reasons": ["浮亏 -12%，触及止损线"],
            "factors": [{"name": "盈亏", "score": -2, "weight": 0.3, "detail": "浮亏"}],
            "risk_pref": "balanced",
            "portfolio_action": "减仓",
        })
        data = resp.get_json()
        assert data["ok"] is True
        dec = data["decision"]
        assert "[AI建议]" in dec["title"]
        assert "600519.SS" in dec["title"]
        assert dec["type"] == "trade"
        assert dec["state"] == "idea"
        assert "ai-advisor" in dec["tags"]

    def test_save_creates_in_journal(self):
        self.client.post("/api/advisor/save-decision", json={
            "ticker": "000001.SZ",
            "name": "平安银行",
            "action": "hold",
            "reasons": [],
        })
        decisions = self.dec_mod.list_decisions()
        assert len(decisions) == 1
        assert "平安银行" in decisions[0]["title"]

    def test_save_includes_factors_in_context(self):
        resp = self.client.post("/api/advisor/save-decision", json={
            "ticker": "600519.SS",
            "name": "贵州茅台",
            "action": "add",
            "reasons": ["接近52周低点"],
            "factors": [
                {"name": "盈亏", "score": 1, "weight": 0.3, "detail": "浮盈 5%"},
                {"name": "趋势", "score": 1, "weight": 0.1, "detail": "偏强"},
            ],
        })
        dec = resp.get_json()["decision"]
        assert "因子分析" in dec["context"]
        assert "盈亏" in dec["context"]

    def test_save_includes_trade_fields(self):
        resp = self.client.post("/api/advisor/save-decision", json={
            "ticker": "600519.SS",
            "name": "贵州茅台",
            "action": "buy",
            "reasons": ["突破"],
            "price": 1700,
            "size": 1000,
            "stop_loss": 1530,
            "take_profit": 2125,
            "strength": 4,
        })
        dec = resp.get_json()["decision"]
        assert dec["symbol"] == "贵州茅台"
        assert dec["price"] == 1700
        assert dec["size"] == 1000
        assert dec["stop_loss"] == 1530
        assert dec["take_profit"] == 2125
        assert dec["confidence"] == 0.8  # strength 4 / 5
        assert dec["source"] == "ai"
        assert dec["action"] == "BUY"


# ── Evaluate endpoint ──────────────────────────────────────────────────────

class TestEvaluateEndpoint:
    """Test POST /api/decisions/evaluate/<id>."""

    @pytest.fixture(autouse=True)
    def _client_and_tmp(self, tmp_path, monkeypatch):
        from trading import decision as dec_mod
        tmp_file = tmp_path / "decisions.json"
        monkeypatch.setattr(dec_mod, "_DECISIONS_FILE", tmp_file)
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()
        self.dec_mod = dec_mod

    def test_evaluate_profit(self):
        d = self.dec_mod.create_decision("buy X", action="BUY", symbol="X", price=10, size=100)
        resp = self.client.post(f"/api/decisions/evaluate/{d['id']}", json={"current_price": 12})
        data = resp.get_json()
        assert data["ok"]
        assert data["pnl"] == 200.0
        assert "盈利" in data["verdict"]

    def test_evaluate_no_price(self):
        resp = self.client.post("/api/decisions/evaluate/abc123", json={})
        assert resp.status_code == 400

    def test_evaluate_not_found(self):
        resp = self.client.post("/api/decisions/evaluate/nonexistent", json={"current_price": 10})
        assert resp.status_code == 400


# ── Analyze endpoint ──────────────────────────────────────────────────────

class TestAnalyzeEndpoint:
    """Test GET /api/decisions/analyze."""

    @pytest.fixture(autouse=True)
    def _client_and_tmp(self, tmp_path, monkeypatch):
        from trading import decision as dec_mod
        tmp_file = tmp_path / "decisions.json"
        monkeypatch.setattr(dec_mod, "_DECISIONS_FILE", tmp_file)
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()
        self.dec_mod = dec_mod

    def test_analyze_empty(self):
        resp = self.client.get("/api/decisions/analyze")
        data = resp.get_json()
        assert data["ok"]
        assert data["total"] == 0

    def test_analyze_with_data(self):
        self.dec_mod.create_decision("b1", action="BUY", symbol="A", price=10)
        self.dec_mod.create_decision("s1", action="SELL", symbol="B", price=20)
        resp = self.client.get("/api/decisions/analyze")
        data = resp.get_json()
        assert data["total"] == 2
        assert data["buys"] == 1
        assert data["sells"] == 1

    def test_analyze_patterns(self):
        self.dec_mod.create_decision("fomo", action="BUY", symbol="X", price=10, confidence=0.2)
        resp = self.client.get("/api/decisions/analyze")
        data = resp.get_json()
        types = [p["type"] for p in data["patterns"]]
        assert "low_confidence" in types
        assert "no_stop_loss" in types

    def test_analyze_filter_type(self):
        self.dec_mod.create_decision("t", dtype="trade", action="BUY", symbol="X", price=10)
        self.dec_mod.create_decision("l", dtype="life")
        resp = self.client.get("/api/decisions/analyze?type=trade")
        data = resp.get_json()
        assert data["total"] == 1
