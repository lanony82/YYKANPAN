"""Tests for v2.0 features: macro, risk-events, bazi/wuyunliuqi, providers API."""

from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
TOOLS_DIR = SRC_DIR / "tools"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import server as stock_app
from tools.bazi_core import calc_wuyun_liuqi


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def client(tmp_path, monkeypatch):
    wl_path = tmp_path / "watchlist_cn.json"
    wl_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(stock_app, "WATCHLIST", wl_path)
    stock_app.app.config["TESTING"] = True
    with stock_app.app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_macro_cache():
    """Reset macro cache between tests."""
    stock_app._MACRO_CACHE = None
    stock_app._MACRO_CACHE_TS = 0
    yield


@pytest.fixture(autouse=True)
def _reset_risk_history():
    """Clear risk event history between tests."""
    stock_app._RISK_EVENT_HISTORY.clear()
    yield


@pytest.fixture(autouse=True)
def _reset_provider_order():
    """Restore default provider order between tests."""
    original = list(stock_app._A_SHARE_DEFAULT_ORDER)
    yield
    stock_app._preferred_provider_order = original


# ══════════════════════════════════════════════════════════════════════════════
# calc_wuyun_liuqi — pure function tests
# ══════════════════════════════════════════════════════════════════════════════

class TestCalcWuyunLiuqi:
    """Test 五运六气 calculation for known dates."""

    def test_2026_basic_fields(self):
        """2026 is 丙午年: 水运太过, 少阴君火司天, 阳明燥金在泉."""
        dt = datetime(2026, 5, 11, 10, 0, 0)
        r = calc_wuyun_liuqi(dt)
        assert r["sui_yun"] == "水运太过"
        assert r["sitian"] == "少阴君火"
        assert r["zaiquan"] == "阳明燥金"

    def test_2026_has_all_keys(self):
        dt = datetime(2026, 5, 11)
        r = calc_wuyun_liuqi(dt)
        expected_keys = {
            "sui_yun", "sitian", "zaiquan", "period_name",
            "period_index", "host_qi", "guest_qi", "comment",
            "health_tip", "trading_tip",
        }
        assert expected_keys == set(r.keys())

    def test_comment_contains_year_info(self):
        dt = datetime(2026, 3, 15)
        r = calc_wuyun_liuqi(dt)
        assert "丙午" in r["comment"]
        assert "水运太过" in r["comment"]

    def test_period_index_in_range(self):
        for month in range(1, 13):
            dt = datetime(2026, month, 15)
            r = calc_wuyun_liuqi(dt)
            assert 1 <= r["period_index"] <= 6

    def test_health_tip_not_empty(self):
        dt = datetime(2026, 7, 1)
        r = calc_wuyun_liuqi(dt)
        assert r["health_tip"], "health_tip should not be empty"

    def test_trading_tip_not_empty(self):
        dt = datetime(2026, 7, 1)
        r = calc_wuyun_liuqi(dt)
        assert r["trading_tip"], "trading_tip should not be empty"

    def test_different_year_gives_different_suiyun(self):
        """2025 乙巳年 should have a different sui_yun than 2026 丙午年."""
        r25 = calc_wuyun_liuqi(datetime(2025, 6, 1))
        r26 = calc_wuyun_liuqi(datetime(2026, 6, 1))
        assert r25["sui_yun"] != r26["sui_yun"]

    def test_host_qi_is_valid_six_qi(self):
        from tools.bazi_core import SIX_QI
        dt = datetime(2026, 8, 1)
        r = calc_wuyun_liuqi(dt)
        assert r["host_qi"] in SIX_QI

    def test_guest_qi_is_valid_six_qi(self):
        from tools.bazi_core import SIX_QI
        dt = datetime(2026, 8, 1)
        r = calc_wuyun_liuqi(dt)
        assert r["guest_qi"] in SIX_QI


# ══════════════════════════════════════════════════════════════════════════════
# /api/macro endpoint
# ══════════════════════════════════════════════════════════════════════════════

FAKE_SINA_MACRO_RAW = (
    'var hq_str_sh000001="上证指数,3350.00,3300.00,3360.00,3370.00,3340.00,'
    '3350.00,3360.00,200000000,180000000000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'
    '0,0,0,0,0,2026-05-11,15:00:00,00";\n'
    'var hq_str_fx_susdcny="15:00:00,7.2000,7.2200,7.1800,7.2300,7.1700,'
    '7.2100,0,0,0,0,0,0,0";\n'
    'var hq_str_hf_GC="2650.50,2660.00,2640.00,2655.00,0,0,0,2645.00,'
    '0,0,0,0,0,2026-05-11";\n'
    'var hq_str_hf_CL="72.30,73.00,71.50,72.80,0,0,0,71.00,'
    '0,0,0,0,0,2026-05-11";\n'
)


class TestMacroEndpoint:

    def test_macro_returns_list(self, client):
        """GET /api/macro should return a JSON list."""
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = FAKE_SINA_MACRO_RAW.encode("gbk")
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            rv = client.get("/api/macro")
            assert rv.status_code == 200
            data = rv.get_json()
            assert isinstance(data, list)
            assert len(data) >= 1

    def test_macro_shanghai_parsed(self, client):
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = FAKE_SINA_MACRO_RAW.encode("gbk")
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            rv = client.get("/api/macro")
            data = rv.get_json()
            sh = [d for d in data if d.get("symbol") == "sh000001"]
            assert len(sh) == 1
            assert sh[0]["name"] == "上证指数"
            assert sh[0]["price"] == 3360.0
            assert sh[0]["prev"] == 3300.0

    def test_macro_cache_hit(self, client):
        """Second call within TTL should not fetch again."""
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = FAKE_SINA_MACRO_RAW.encode("gbk")
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            client.get("/api/macro")
            client.get("/api/macro")
            assert mock_open.call_count == 1

    def test_macro_network_error(self, client):
        """Network failure should return error entry."""
        with patch.object(stock_app.urlrequest, "urlopen", side_effect=Exception("timeout")):
            rv = client.get("/api/macro")
            data = rv.get_json()
            assert isinstance(data, list)
            assert any("error" in d for d in data)


# ══════════════════════════════════════════════════════════════════════════════
# /api/macro-history endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestMacroHistoryEndpoint:

    @pytest.fixture(autouse=True)
    def _reset_macro_history_cache(self):
        stock_app._MACRO_HISTORY_CACHE.clear()
        yield

    def test_unknown_symbol_returns_400(self, client):
        rv = client.get("/api/macro-history/INVALID")
        assert rv.status_code == 400

    def test_sh000001_returns_closes(self, client):
        fake_kline = json.dumps([
            {"day": "2026-05-01", "close": "3350.00"},
            {"day": "2026-05-02", "close": "3360.00"},
            {"day": "2026-05-03", "close": "3370.00"},
        ]).encode("utf-8")
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = fake_kline
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            rv = client.get("/api/macro-history/sh000001")
            data = rv.get_json()
            assert data["ok"] is True
            assert data["symbol"] == "sh000001"
            assert len(data["closes"]) == 3
            assert data["closes"] == [3350.0, 3360.0, 3370.0]

    def test_hf_GC_returns_closes(self, client):
        # Sina futures JSONP response format
        fake_raw = 'data([{"date":"2026-05-01","close":"2350.00"},{"date":"2026-05-02","close":"2360.00"}])'
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = fake_raw.encode("utf-8")
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            rv = client.get("/api/macro-history/hf_GC")
            data = rv.get_json()
            assert data["ok"] is True
            assert len(data["closes"]) == 2

    def test_fx_susdcny_returns_closes(self, client):
        # Sina forex returns pipe-delimited CSV: date,open,low,high,close
        fake_raw = 'data("2026-05-01,7.2100,7.2000,7.2200,7.2150,|2026-05-02,7.2150,7.2050,7.2300,7.2200,");'
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = fake_raw.encode("utf-8")
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            rv = client.get("/api/macro-history/fx_susdcny")
            data = rv.get_json()
            assert data["ok"] is True
            assert len(data["closes"]) == 2
            assert data["closes"] == [7.215, 7.22]

    def test_network_error_returns_empty(self, client):
        with patch.object(stock_app.urlrequest, "urlopen", side_effect=Exception("timeout")):
            rv = client.get("/api/macro-history/sh000001")
            data = rv.get_json()
            assert data["ok"] is False
            assert data["closes"] == []

    def test_cache_hit(self, client):
        fake_kline = json.dumps([
            {"day": "2026-05-01", "close": "3350.00"},
        ]).encode("utf-8")
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = fake_kline
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_open.return_value = mock_resp

            client.get("/api/macro-history/sh000001")
            client.get("/api/macro-history/sh000001")
            assert mock_open.call_count == 1


# ══════════════════════════════════════════════════════════════════════════════
# /api/risk-events endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestRiskEventsEndpoint:

    def test_risk_events_empty(self, client):
        """No events when macro is flat, no stocks loaded, and history cleared."""
        with patch.object(stock_app, "_fetch_macro_indicators", return_value=[
            {"name": "上证指数", "change_pct": 0.5, "price": 3360, "prev": 3340},
        ]), patch.object(stock_app, "_scan_news_events", return_value=[]):
            saved = stock_app.STOCKS_CACHE_DATA
            saved_history = stock_app._RISK_EVENT_HISTORY[:]
            stock_app.STOCKS_CACHE_DATA = []
            stock_app._RISK_EVENT_HISTORY.clear()
            try:
                rv = client.get("/api/risk-events")
                assert rv.status_code == 200
                data = rv.get_json()
                assert data["ok"] is True
                assert data["count"] == 0
            finally:
                stock_app.STOCKS_CACHE_DATA = saved
                stock_app._RISK_EVENT_HISTORY[:] = saved_history

    def test_risk_event_shanghai_crash(self, client):
        """Shanghai index drop >=3% should trigger event."""
        with patch.object(stock_app, "_fetch_macro_indicators", return_value=[
            {"name": "上证指数", "change_pct": -3.5, "price": 3200, "prev": 3316},
        ]):
            rv = client.get("/api/risk-events")
            data = rv.get_json()
            assert data["count"] >= 1
            assert any("上证" in e["title"] for e in data["events"])

    def test_risk_event_dedup_same_hour(self, client):
        """Same event within same hour should not duplicate."""
        with patch.object(stock_app, "_fetch_macro_indicators", return_value=[
            {"name": "上证指数", "change_pct": -5.0, "price": 3100, "prev": 3263},
        ]):
            client.get("/api/risk-events")
            client.get("/api/risk-events")
            rv = client.get("/api/risk-events?period=30d")
            data = rv.get_json()
            titles = [e["title"] for e in data["events"]]
            # Should have at most one occurrence per title
            assert len(titles) == len(set(titles))

    def test_risk_events_period_filter(self, client):
        """Period parameter should be returned in response."""
        with patch.object(stock_app, "_fetch_macro_indicators", return_value=[]):
            rv = client.get("/api/risk-events?period=7d")
            data = rv.get_json()
            assert data["period"] == "7d"

    def test_stock_limit_down_triggers_event(self, client):
        """A stock dropping >=9.8% should trigger a black swan event."""
        with patch.object(stock_app, "_fetch_macro_indicators", return_value=[]):
            stock_app.STOCKS_CACHE_DATA = [
                {"ticker": "600001.SS", "name": "测试股", "change_pct": -10.0, "price": 9.0},
            ]
            try:
                rv = client.get("/api/risk-events")
                data = rv.get_json()
                assert data["count"] >= 1
                assert any("跌停" in e["title"] for e in data["events"])
            finally:
                stock_app.STOCKS_CACHE_DATA = []


# ══════════════════════════════════════════════════════════════════════════════
# /api/bazi endpoint
# ══════════════════════════════════════════════════════════════════════════════

class TestBaziEndpoint:

    def test_bazi_returns_ok(self, client):
        rv = client.get("/api/bazi")
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["ok"] is True

    def test_bazi_has_pillars(self, client):
        rv = client.get("/api/bazi")
        data = rv.get_json()
        assert "pillars" in data
        assert len(data["pillars"]) == 4
        labels = [p["label"] for p in data["pillars"]]
        assert labels == ["年柱", "月柱", "日柱", "时柱"]

    def test_bazi_has_wuyun(self, client):
        rv = client.get("/api/bazi")
        data = rv.get_json()
        assert "wuyun" in data
        wuyun = data["wuyun"]
        assert "sui_yun" in wuyun
        assert "sitian" in wuyun
        assert "zaiquan" in wuyun

    def test_bazi_has_lunar_and_solar(self, client):
        rv = client.get("/api/bazi")
        data = rv.get_json()
        assert "lunar" in data
        assert "solar" in data


# ══════════════════════════════════════════════════════════════════════════════
# /api/providers/* endpoints
# ══════════════════════════════════════════════════════════════════════════════

class TestProvidersEndpoint:

    def test_get_provider_order(self, client):
        rv = client.get("/api/providers/order")
        assert rv.status_code == 200
        data = rv.get_json()
        assert "order" in data
        assert isinstance(data["order"], list)
        assert "sina" in data["order"]

    def test_set_provider_order(self, client):
        rv = client.post(
            "/api/providers/order",
            data=json.dumps({"order": ["yahoo", "sina", "akshare"]}),
            content_type="application/json",
        )
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["ok"] is True
        assert data["order"][0] == "yahoo"

    def test_set_provider_order_invalid_ignored(self, client):
        """Invalid provider names should be dropped, missing ones appended."""
        rv = client.post(
            "/api/providers/order",
            data=json.dumps({"order": ["bogus", "sina"]}),
            content_type="application/json",
        )
        data = rv.get_json()
        assert data["ok"] is True
        assert data["order"][0] == "sina"
        # All valid providers should still be present
        assert len(data["order"]) == len(stock_app._A_SHARE_DEFAULT_ORDER)

    def test_providers_test_endpoint(self, client):
        """POST /api/providers/test should return results list."""
        with patch.object(stock_app, "_test_providers", return_value=[
            {"provider": "sina", "ok": True, "time_s": 0.1},
            {"provider": "akshare", "ok": False, "time_s": 3.0},
            {"provider": "yahoo", "ok": True, "time_s": 0.5},
        ]):
            rv = client.post("/api/providers/test")
            assert rv.status_code == 200
            data = rv.get_json()
            assert "results" in data
            assert data["best"] == "sina"

    def test_providers_auto_endpoint(self, client):
        """POST /api/providers/auto should reorder by speed."""
        with patch.object(stock_app, "_test_providers", return_value=[
            {"provider": "sina", "ok": True, "time_s": 0.5},
            {"provider": "akshare", "ok": True, "time_s": 0.1},
            {"provider": "yahoo", "ok": True, "time_s": 1.0},
        ]):
            rv = client.post("/api/providers/auto")
            data = rv.get_json()
            assert data["ok"] is True
            assert data["order"][0] == "akshare"
            assert data["order"][1] == "sina"
