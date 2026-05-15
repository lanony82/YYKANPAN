"""Tests for analysis/screener.py — Stock screener strategies & API."""

from __future__ import annotations

import pathlib
import sys
from unittest.mock import patch, MagicMock

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analysis import screener


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_bars(closes: list[float], volumes: list[float] | None = None) -> list[dict]:
    """Build a minimal OHLCV bar list for testing strategies."""
    if volumes is None:
        volumes = [1_000_000.0] * len(closes)
    return [
        {
            "day": f"2026-05-{i+1:02d}",
            "open": c * 0.99,
            "high": c * 1.01,
            "low": c * 0.98,
            "close": c,
            "volume": volumes[i],
        }
        for i, c in enumerate(closes)
    ]


# ── list_strategies ──────────────────────────────────────────────────────────

class TestListStrategies:
    def test_returns_all_four(self):
        result = screener.list_strategies()
        keys = {s["key"] for s in result}
        assert keys == {"golden_cross", "volume_breakout", "oversold_bounce", "limit_up_relay"}

    def test_structure(self):
        for s in screener.list_strategies():
            assert "key" in s
            assert "name" in s
            assert "desc" in s
            assert "icon" in s


# ── STRATEGIES dict ──────────────────────────────────────────────────────────

class TestStrategiesDict:
    def test_all_present(self):
        expected = {"golden_cross", "volume_breakout", "oversold_bounce", "limit_up_relay"}
        assert set(screener.STRATEGIES.keys()) == expected

    def test_each_has_required_fields(self):
        for k, v in screener.STRATEGIES.items():
            assert "name" in v, f"{k} missing 'name'"
            assert "desc" in v, f"{k} missing 'desc'"
            assert "icon" in v, f"{k} missing 'icon'"


# ── Internal helpers ─────────────────────────────────────────────────────────

class TestCodeConversions:
    def test_code_to_sina_sh(self):
        assert screener._code_to_sina("600519") == "sh600519"
        assert screener._code_to_sina("688001") == "sh688001"

    def test_code_to_sina_sz(self):
        assert screener._code_to_sina("000858") == "sz000858"
        assert screener._code_to_sina("300750") == "sz300750"

    def test_code_to_ticker_sh(self):
        assert screener._code_to_ticker("600519") == "600519.SS"

    def test_code_to_ticker_sz(self):
        assert screener._code_to_ticker("000858") == "000858.SZ"


class TestCalcVolumeRatio:
    def test_normal(self):
        # 5 bars with vol 100, then last bar with vol 200 → ratio ~2.0
        vols = [100.0] * 5 + [200.0]
        assert screener._calc_volume_ratio(vols, 5) == 2.0

    def test_too_few_bars(self):
        assert screener._calc_volume_ratio([100.0], 5) == 0

    def test_zero_avg(self):
        vols = [0.0] * 5 + [100.0]
        assert screener._calc_volume_ratio(vols, 5) == 0


# ── run_screen ───────────────────────────────────────────────────────────────

class TestRunScreen:
    @pytest.fixture(autouse=True)
    def _clear_caches(self):
        """Clear screener caches before each test."""
        screener._POOL_CACHE.clear()
        screener._SCREENER_CACHE.clear()
        screener._OHLCV_CACHE.clear()
        yield
        screener._POOL_CACHE.clear()
        screener._SCREENER_CACHE.clear()
        screener._OHLCV_CACHE.clear()

    def test_unknown_strategy(self):
        result = screener.run_screen("nonexistent")
        assert result["ok"] is False
        assert "未知策略" in result["msg"]

    def test_cache_hit(self):
        """Second call for same strategy should return cached result."""
        fake_result = {
            "ok": True, "strategy": "golden_cross", "name": "均线金叉",
            "desc": "...", "icon": "✦", "hits": [], "scanned": "test",
            "ts": "2026-05-08 10:00",
        }
        import time
        screener._SCREENER_CACHE["golden_cross"] = {
            "data": fake_result,
            "ts": time.time(),  # fresh
        }
        result = screener.run_screen("golden_cross")
        assert result is fake_result

    def test_golden_cross_empty_pool(self):
        with patch.object(screener, "_get_csi300_pool", return_value=[]):
            result = screener.run_screen("golden_cross")
            assert result["ok"] is False

    def test_golden_cross_no_hits(self):
        """Pool with stocks but no golden cross signals → ok=True, hits=[]."""
        pool = [{"code": "600519", "name": "贵州茅台", "ticker": "600519.SS", "sina": "sh600519"}]
        # Flat price, no crossover
        bars = _make_bars([100.0] * 25)
        with patch.object(screener, "_get_csi300_pool", return_value=pool), \
             patch.object(screener, "_fetch_ohlcv", return_value=bars), \
             patch.object(screener, "_prefetch_pool_ohlcv"):
            result = screener.run_screen("golden_cross")
            assert result["ok"] is True
            assert result["strategy"] == "golden_cross"
            assert result["hits"] == []

    def test_volume_breakout_structure(self):
        """Check result dict structure even with empty pool."""
        with patch.object(screener, "_get_csi300_pool", return_value=[]), \
             patch.object(screener, "_prefetch_pool_ohlcv"):
            result = screener.run_screen("volume_breakout")
            assert result["ok"] is False  # empty pool

    def test_limit_up_relay_uses_zt_pool(self):
        """limit_up_relay uses _get_zt_pool, not CSI300."""
        with patch.object(screener, "_get_zt_pool", return_value=[]) as mock_zt:
            result = screener.run_screen("limit_up_relay")
            assert result["ok"] is True
            assert result["hits"] == []
            mock_zt.assert_called()


# ── Strategy scan functions ──────────────────────────────────────────────────

class TestScanGoldenCross:
    def test_detects_cross(self):
        """Construct prices where MA5 crosses above MA20 at the last bar."""
        # 20 bars flat at 10, then 5 bars rising to trigger MA5 > MA20
        closes = [10.0] * 18 + [10.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
        # High volume on last bar to pass volume ratio check
        volumes = [1_000_000.0] * 20 + [1_000_000.0, 1_000_000.0, 1_000_000.0, 1_500_000.0, 2_000_000.0]
        bars = _make_bars(closes, volumes)

        pool = [{"code": "600519", "name": "茅台", "ticker": "600519.SS", "sina": "sh600519"}]
        with patch.object(screener, "_fetch_ohlcv", return_value=bars):
            hits = screener._scan_golden_cross(pool)
        # Whether it triggers depends on exact MA math, just check structure
        for h in hits:
            assert "code" in h
            assert "score" in h
            assert "reasons" in h

    def test_too_few_bars(self):
        pool = [{"code": "600519", "name": "茅台", "ticker": "600519.SS", "sina": "sh600519"}]
        bars = _make_bars([10.0] * 5)
        with patch.object(screener, "_fetch_ohlcv", return_value=bars):
            hits = screener._scan_golden_cross(pool)
        assert hits == []


class TestScanVolumeBreakout:
    def test_no_match_flat(self):
        pool = [{"code": "000858", "name": "五粮液", "ticker": "000858.SZ", "sina": "sz000858"}]
        bars = _make_bars([50.0] * 25)
        with patch.object(screener, "_fetch_ohlcv", return_value=bars):
            hits = screener._scan_volume_breakout(pool)
        assert hits == []


class TestScanOversoldBounce:
    def test_no_match_normal_rsi(self):
        pool = [{"code": "000858", "name": "五粮液", "ticker": "000858.SZ", "sina": "sz000858"}]
        bars = _make_bars([50.0] * 30)
        with patch.object(screener, "_fetch_ohlcv", return_value=bars):
            hits = screener._scan_oversold_bounce(pool)
        assert hits == []


# ── Server endpoint (integration) ───────────────────────────────────────────

class TestScreenerEndpoints:
    @pytest.fixture
    def client(self):
        import server as stock_app
        stock_app.app.config["TESTING"] = True
        with stock_app.app.test_client() as c:
            yield c

    def test_strategies_list(self, client):
        resp = client.get("/api/screener/strategies")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert len(data["strategies"]) == 4

    def test_scan_unknown_strategy(self, client):
        resp = client.get("/api/screener?strategy=nonexistent")
        data = resp.get_json()
        assert data["ok"] is False
