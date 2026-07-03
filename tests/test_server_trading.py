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

    def test_analyze_filter_type(self):
        self.dec_mod.create_decision("t", dtype="trade", action="BUY", symbol="X", price=10)
        self.dec_mod.create_decision("l", dtype="life")
        resp = self.client.get("/api/decisions/analyze?type=trade")
        data = resp.get_json()
        assert data["total"] == 1


# ── Daily article content endpoint ────────────────────────────────────────

class TestDailyArticleEndpoint:
    """Test POST /api/content/daily-article."""

    @pytest.fixture(autouse=True)
    def _client(self):
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()

    @patch.object(stock_app, "_build_auto_brief", return_value={
        "snapshot": {"regime": "偏强", "avg_change_pct": 1.23}
    })
    @patch.object(stock_app, "_build_ai_edge_report", return_value={
        "summary": {"confidence": 72.6},
        "playbook": ["关注强势股回踩", "不追高"],
    })
    @patch.object(stock_app, "_load_sentiment_history", return_value=[{"stage": "上升"}])
    @patch.object(stock_app, "_get_limit_stats", return_value={"limit_up": 45, "limit_down": 3})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 10, "patterns": [{"type": "no_review"}]})
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    def test_generate_article_no_file(self, *_mocks):
        resp = self.client.post("/api/content/daily-article", json={
            "trade_date": "2026-05-21",
            "save_to_file": False,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert "article" in data
        assert data["article"]["date"] == "2026-05-21"
        assert "content_markdown" in data["article"]
        assert "免责声明" in data["article"]["content_markdown"]
        assert "原创说明" in data["article"]["content_markdown"]
        assert "saved" not in data

    @patch.object(stock_app, "_build_auto_brief", return_value={"snapshot": {"regime": "震荡"}})
    @patch.object(stock_app, "_build_ai_edge_report", return_value={"summary": {"confidence": 55.0}, "playbook": []})
    @patch.object(stock_app, "_load_sentiment_history", return_value=[])
    @patch.object(stock_app, "_get_limit_stats", return_value={})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 0, "patterns": []})
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    @patch.object(stock_app, "_fetch_pd_image", return_value=False)
    @patch.object(stock_app, "_collect_closing_news", return_value={"risk_events": [], "cctv": []})
    def test_generate_article_save_to_data_wxfile(self, _news, _img, _loss, _analyze, _limit, _sent, _ai, _brief, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)
        resp = self.client.post("/api/content/daily-article", json={
            "trade_date": "2026-05-21",
            "save_to_file": True,
        })
        data = resp.get_json()
        assert data["ok"] is True
        assert data["saved"]["ok"] is True
        assert data["saved"]["mode"] == "3-files-per-day"
        files = data["saved"]["files"]
        assert len(files) == 3

        rels = {f["relative"] for f in files}
        assert "data/wxfile/2026-05-21_opening.md" in rels
        assert "data/wxfile/2026-05-21_intraday.md" in rels
        assert "data/wxfile/2026-05-21_closing.md" in rels

        for name in ("opening", "intraday", "closing"):
            saved_path = tmp_path / "wxfile" / f"2026-05-21_{name}.md"
            assert saved_path.exists()
            text = saved_path.read_text(encoding="utf-8")
            assert "风险提示与免责声明" in text
            assert "原创说明" in text


class TestDailyFileRouting:
    """Test GET routes for daily wx files by date and section."""

    @pytest.fixture(autouse=True)
    def _client(self):
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()

    @pytest.fixture(autouse=True)
    def _stub_network(self):
        # Prevent daily-article file generation from hitting the real network
        # (Wikimedia image fetch + CLS/CCTV news collection).
        with patch.object(stock_app, "_fetch_pd_image", return_value=False), \
             patch.object(stock_app, "_collect_closing_news", return_value={"risk_events": [], "cctv": []}):
            yield

    @patch.object(stock_app, "_build_auto_brief", return_value={"snapshot": {"regime": "震荡"}})
    @patch.object(stock_app, "_build_ai_edge_report", return_value={"summary": {"confidence": 50.0}, "playbook": []})
    @patch.object(stock_app, "_load_sentiment_history", return_value=[])
    @patch.object(stock_app, "_get_limit_stats", return_value={"limit_up": 10, "limit_down": 2})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 0, "patterns": []})
    @patch.object(stock_app, "_fetch_macro_indicators", return_value=[])
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    def test_list_daily_files_by_date(self, _loss, _macro, _analyze, _limit, _sent, _ai, _brief, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)
        self.client.post("/api/content/daily-article", json={
            "trade_date": "2026-05-21",
            "save_to_file": True,
        })

        resp = self.client.get("/api/content/daily-files/2026-05-21")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["trade_date"] == "2026-05-21"
        assert len(data["files"]) == 3
        assert all(f["exists"] for f in data["files"])

    @patch.object(stock_app, "_build_auto_brief", return_value={"snapshot": {"regime": "震荡"}})
    @patch.object(stock_app, "_build_ai_edge_report", return_value={"summary": {"confidence": 50.0}, "playbook": []})
    @patch.object(stock_app, "_load_sentiment_history", return_value=[])
    @patch.object(stock_app, "_get_limit_stats", return_value={"limit_up": 10, "limit_down": 2})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 0, "patterns": []})
    @patch.object(stock_app, "_fetch_macro_indicators", return_value=[])
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    def test_get_single_section_by_date(self, _loss, _macro, _analyze, _limit, _sent, _ai, _brief, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)
        self.client.post("/api/content/daily-article", json={
            "trade_date": "2026-05-21",
            "save_to_file": True,
        })

        resp = self.client.get("/api/content/daily-files/2026-05-21/intraday")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["section"] == "intraday"
        assert "content_markdown" in data

    def test_get_single_section_invalid(self):
        resp = self.client.get("/api/content/daily-files/2026-05-21/nope")
        assert resp.status_code == 400

    @patch.object(stock_app, "_build_auto_brief", return_value={"snapshot": {"regime": "震荡"}})
    @patch.object(stock_app, "_build_ai_edge_report", return_value={"summary": {"confidence": 50.0}, "playbook": []})
    @patch.object(stock_app, "_load_sentiment_history", return_value=[])
    @patch.object(stock_app, "_get_limit_stats", return_value={})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 0, "patterns": []})
    @patch.object(stock_app, "_fetch_macro_indicators", return_value=[])
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    def test_list_daily_files_create_if_missing_with_content(self, _loss, _macro, _analyze, _limit, _sent, _ai, _brief, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)

        resp = self.client.get(
            "/api/content/daily-files/2026-06-01?create_if_missing=1&include_content=true"
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert len(data["files"]) == 3
        for f in data["files"]:
            assert f["exists"]
            assert "content_markdown" in f
            assert "2026-06-01" in f["content_markdown"]

    def test_list_daily_files_missing_without_create(self, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)

        resp = self.client.get("/api/content/daily-files/2099-01-01")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert len(data["files"]) == 3
        # No files were created and content was not requested
        assert all(f["exists"] is False for f in data["files"])
        assert all("content_markdown" not in f for f in data["files"])

    def test_get_single_section_missing_returns_404(self, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)

        resp = self.client.get("/api/content/daily-files/2099-01-01/opening")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False
        assert data["section"] == "opening"

    @patch.object(stock_app, "_build_auto_brief", return_value={"snapshot": {"regime": "震荡"}})
    @patch.object(stock_app, "_build_ai_edge_report", return_value={"summary": {"confidence": 50.0}, "playbook": []})
    @patch.object(stock_app, "_load_sentiment_history", return_value=[])
    @patch.object(stock_app, "_get_limit_stats", return_value={})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 0, "patterns": []})
    @patch.object(stock_app, "_fetch_macro_indicators", return_value=[])
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    def test_get_single_section_create_if_missing(self, _loss, _macro, _analyze, _limit, _sent, _ai, _brief, tmp_path, monkeypatch):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)

        resp = self.client.get(
            "/api/content/daily-files/2026-06-02/closing?create_if_missing=true"
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["ok"] is True
        assert data["section"] == "closing"
        assert "content_markdown" in data
        # File should now exist on disk
        assert (tmp_path / "wxfile" / "2026-06-02_closing.md").exists()


class TestDailyArticleCustomization:
    """Test custom title and disclaimer toggles."""

    @pytest.fixture(autouse=True)
    def _client(self):
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()

    @patch.object(stock_app, "_build_auto_brief", return_value={"snapshot": {"regime": "震荡"}})
    @patch.object(stock_app, "_build_ai_edge_report", return_value={"summary": {"confidence": 50.0}, "playbook": []})
    @patch.object(stock_app, "_load_sentiment_history", return_value=[])
    @patch.object(stock_app, "_get_limit_stats", return_value={})
    @patch.object(stock_app.dec, "analyze", return_value={"total": 0, "patterns": []})
    @patch.object(stock_app, "_fetch_macro_indicators", return_value=[])
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={"top_pattern": None, "next_day_rule": "先执行计划"})
    def test_custom_title_and_no_disclaimer(self, *_mocks):
        resp = self.client.post("/api/content/daily-article", json={
            "trade_date": "2026-05-21",
            "title": "我的复盘标题",
            "include_disclaimer": False,
            "include_original_note": False,
            "save_to_file": False,
        })
        data = resp.get_json()
        assert data["ok"] is True
        article = data["article"]
        assert article["title"] == "我的复盘标题"
        assert article["disclaimer"] == ""
        assert article["original_note"] == ""
        md = article["content_markdown"]
        assert "免责声明" not in md
        assert "原创说明" not in md
        assert "我的复盘标题" in md

    @patch.object(stock_app, "_build_auto_brief", return_value={
        "snapshot": {
            "regime": "震荡", "valid": 90, "total": 100, "avg_change_pct": 0.5
        }
    })
    @patch.object(stock_app, "_build_ai_edge_report", return_value={
        "summary": {
            "confidence": 60.0, "market_bias": "neutral",
            "up_count": 50, "down_count": 50, "coverage": 100,
        },
        "playbook": ["保持纪律"],
    })
    @patch.object(stock_app, "_load_sentiment_history", return_value=[
        {"stage": "上升", "score": 70, "up_ratio": 0.6}
    ])
    @patch.object(stock_app, "_get_limit_stats", return_value={
        "limit_up": 20, "limit_down": 5,
        "yesterday_limit_up_performance": {
            "profit_rate": 60.0, "avg_change_pct": 1.5, "verdict": "偏强",
        },
    })
    @patch.object(stock_app.dec, "analyze", return_value={
        "total": 5, "patterns": [], "by_source": {"manual": 3, "ai": 2},
    })
    @patch.object(stock_app, "_fetch_macro_indicators", return_value=[
        {"symbol": "vol_total", "price": 9000},
        {"symbol": "northbound", "price": 50},
        {"symbol": "sh000001", "price": 3200, "change_pct": 0.4},
        {"symbol": "sz399001", "price": 11000, "change_pct": -0.2},
    ])
    @patch.object(stock_app.dec, "detect_loss_patterns", return_value={
        "top_pattern": {"label": "示例模式"},
        "next_day_rule": "明日硬约束：示例规则",
    })
    def test_full_card_collections(self, *_mocks):
        resp = self.client.post("/api/content/daily-article", json={
            "trade_date": "2026-05-21",
            "save_to_file": False,
            "include_card_collections": True,
        })
        data = resp.get_json()
        article = data["article"]
        md = article["content_markdown"]
        # Sections must surface enriched cards and the carry-forward rule
        assert "明日硬约束：示例规则" in md
        assert "示例模式" in md
        assert "上证 3200" in md
        assert "成功率 60.0%" in md
        assert "决策来源卡片：manual:3, ai:2" in md
        assert "情绪分值：70" in md
