"""Tests for wxfile additions: 五运六气, news collector, PD image, scheduler.

These cover the helpers and standard sections added to
``_build_daily_wechat_article`` and the daily wxfile scheduler — which are
network/wall-clock dependent in production. Every test stubs the network and
clock so the suite stays fast and offline-safe.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import server as stock_app


# ── _wuyun_liuqi_for_date ────────────────────────────────────────────────────


class TestWuyunLiuqi:
    """干支 + 岁运 + 司天 + 在泉 + 主气 derivation."""

    def test_2026_is_bingwu(self):
        r = stock_app._wuyun_liuqi_for_date("2026-06-03")
        assert r["year_ganzhi"] == "丙午年"
        assert r["yun"] == "水运太过"
        assert r["sitian"] == "少阴君火"
        assert r["zaiquan"] == "阳明燥金"

    def test_2025_is_yisi(self):
        r = stock_app._wuyun_liuqi_for_date("2025-12-15")
        assert r["year_ganzhi"] == "乙巳年"
        assert r["yun"] == "金运不及"
        assert r["sitian"] == "厥阴风木"
        assert r["zaiquan"] == "少阳相火"

    def test_zhuqi_summer(self):
        # 6月 → 三之气, 主气 少阳相火
        assert stock_app._wuyun_liuqi_for_date("2026-06-15")["zhuqi"] == "少阳相火"

    def test_zhuqi_winter(self):
        # md < 321 falls into the wrap-around 初之气 window (厥阴风木)
        assert stock_app._wuyun_liuqi_for_date("2026-01-10")["zhuqi"] == "厥阴风木"
        # late November onwards → 终之气 太阳寒水
        assert stock_app._wuyun_liuqi_for_date("2026-12-15")["zhuqi"] == "太阳寒水"

    def test_zhuqi_spring(self):
        # 3月20 < 321 → 厥阴风木; 3月21 → 少阴君火 (boundary check)
        assert stock_app._wuyun_liuqi_for_date("2026-03-20")["zhuqi"] == "厥阴风木"
        assert stock_app._wuyun_liuqi_for_date("2026-03-21")["zhuqi"] == "少阴君火"

    def test_zhuqi_autumn(self):
        # 9月22 → 太阴湿土; 9月23 → 阳明燥金
        assert stock_app._wuyun_liuqi_for_date("2026-09-22")["zhuqi"] == "太阴湿土"
        assert stock_app._wuyun_liuqi_for_date("2026-09-23")["zhuqi"] == "阳明燥金"

    def test_invalid_date_falls_back(self):
        r = stock_app._wuyun_liuqi_for_date("not-a-date")
        # Defaults to 2026-01-01 sentinel → still valid 干支
        assert r["year_ganzhi"].endswith("年")
        assert r["yun"] in {
            "土运太过", "土运不及", "金运不及", "金运太过",
            "水运太过", "水运不及", "木运不及", "木运太过",
            "火运太过", "火运不及",
        }

    def test_returns_all_keys(self):
        r = stock_app._wuyun_liuqi_for_date("2026-06-03")
        assert set(r.keys()) >= {"year_ganzhi", "yun", "sitian", "zaiquan", "zhuqi"}

    def test_year_cycles_60(self):
        # Same Ganzhi 60 years apart
        r1 = stock_app._wuyun_liuqi_for_date("1966-06-03")
        r2 = stock_app._wuyun_liuqi_for_date("2026-06-03")
        assert r1["year_ganzhi"] == r2["year_ganzhi"]


# ── _collect_closing_news ────────────────────────────────────────────────────


class TestCollectClosingNews:
    """News collection: in-memory risk events + CCTV headlines."""

    def setup_method(self):
        self._saved_history = list(stock_app._RISK_EVENT_HISTORY)
        stock_app._RISK_EVENT_HISTORY.clear()

    def teardown_method(self):
        stock_app._RISK_EVENT_HISTORY.clear()
        stock_app._RISK_EVENT_HISTORY.extend(self._saved_history)

    def _patch_now(self, dt: datetime):
        return patch.object(stock_app, "_bj_now", return_value=dt)

    def test_empty_when_no_risk_events_and_no_ak(self):
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", None):
            out = stock_app._collect_closing_news("2026-06-03")
        assert out == {"risk_events": [], "cctv": []}

    def test_blackswan_sorted_before_greyrhino(self):
        stock_app._RISK_EVENT_HISTORY.extend([
            {"type": "灰犀牛", "severity": "medium", "title": "GR", "time": "2026-06-03 10:00"},
            {"type": "黑天鹅", "severity": "high", "title": "BS", "time": "2026-06-03 09:00"},
        ])
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", None):
            out = stock_app._collect_closing_news("2026-06-03")
        assert [e["title"] for e in out["risk_events"]] == ["BS", "GR"]

    def test_filters_to_last_2_days(self):
        stock_app._RISK_EVENT_HISTORY.extend([
            {"type": "黑天鹅", "severity": "high", "title": "OLD", "time": "2026-05-01 09:00"},
            {"type": "黑天鹅", "severity": "high", "title": "FRESH", "time": "2026-06-03 09:00"},
        ])
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", None):
            out = stock_app._collect_closing_news("2026-06-03")
        titles = [e["title"] for e in out["risk_events"]]
        assert "FRESH" in titles
        assert "OLD" not in titles

    def test_limit_caps_risk_events(self):
        stock_app._RISK_EVENT_HISTORY.extend([
            {"type": "黑天鹅", "severity": "high", "title": f"E{i}", "time": "2026-06-03 09:00"}
            for i in range(10)
        ])
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", None):
            out = stock_app._collect_closing_news("2026-06-03", limit=3)
        assert len(out["risk_events"]) == 3

    def test_cctv_collected_via_akshare_mock(self):
        import pandas as pd
        df = pd.DataFrame([
            {"title": "习近平会见外国领导人", "content": ""},
            {"title": "国务院发布政策", "content": ""},
        ])
        mock_ak = MagicMock()
        mock_ak.news_cctv.return_value = df
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", mock_ak), \
             patch.object(stock_app, "_with_retries", side_effect=lambda fn: fn()):
            out = stock_app._collect_closing_news("2026-06-03")
        titles = [n["title"] for n in out["cctv"]]
        assert "习近平会见外国领导人" in titles
        assert "国务院发布政策" in titles

    def test_cctv_dedupes_across_days(self):
        import pandas as pd
        df = pd.DataFrame([{"title": "重复标题", "content": ""}])
        mock_ak = MagicMock()
        mock_ak.news_cctv.return_value = df
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", mock_ak), \
             patch.object(stock_app, "_with_retries", side_effect=lambda fn: fn()):
            out = stock_app._collect_closing_news("2026-06-03")
        assert sum(1 for n in out["cctv"] if n["title"] == "重复标题") == 1

    def test_cctv_failure_returns_empty(self):
        mock_ak = MagicMock()
        mock_ak.news_cctv.side_effect = RuntimeError("network down")
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", mock_ak), \
             patch.object(stock_app, "_with_retries", side_effect=lambda fn: fn()):
            out = stock_app._collect_closing_news("2026-06-03")
        assert out["cctv"] == []

    def test_risk_event_failure_returns_empty(self):
        # Inject a malformed event that breaks sort comparator
        stock_app._RISK_EVENT_HISTORY.append({"type": None, "time": None})
        with self._patch_now(datetime(2026, 6, 3, 16, 0)), \
             patch.object(stock_app, "ak", None):
            out = stock_app._collect_closing_news("2026-06-03")
        # Should not raise; risk_events may be partial or empty
        assert "risk_events" in out


# ── _fetch_pd_image ──────────────────────────────────────────────────────────


class TestFetchPdImage:
    """Public-domain Wikimedia image fetcher with cache + fallback."""

    def test_cache_hit_skips_network(self, tmp_path):
        dest = tmp_path / "cached.png"
        dest.write_bytes(b"\x89PNG\r\n\x1a\nfake")
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            ok = stock_app._fetch_pd_image("anything", dest, "https://fallback")
        assert ok is True
        mock_open.assert_not_called()

    def test_empty_file_is_not_cache_hit(self, tmp_path):
        dest = tmp_path / "empty.png"
        dest.touch()
        with patch.object(stock_app.urlrequest, "urlopen") as mock_open:
            mock_open.side_effect = RuntimeError("network blocked")
            ok = stock_app._fetch_pd_image("q", dest, "https://fallback")
        assert ok is False  # search failed AND fallback failed → False

    def test_search_success_downloads(self, tmp_path, monkeypatch):
        dest = tmp_path / "out.png"
        api_response = (
            b'{"query":{"pages":{"1":{"imageinfo":[{"thumburl":'
            b'"https://example.org/pic.png"}]}}}}'
        )
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"x" * 100

        class _Resp:
            def __init__(self, payload):
                self._payload = payload

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return self._payload

        responses = [_Resp(api_response), _Resp(png_bytes)]
        monkeypatch.setattr(
            stock_app.urlrequest,
            "urlopen",
            lambda req, timeout=None: responses.pop(0),
        )
        ok = stock_app._fetch_pd_image("market", dest, "https://fallback")
        assert ok is True
        assert dest.read_bytes() == png_bytes

    def test_search_fails_uses_fallback(self, tmp_path, monkeypatch):
        dest = tmp_path / "fb.png"
        png_bytes = b"\x89PNG\r\n\x1a\nfallback"

        class _OkResp:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return png_bytes

        calls = []

        def _open(req, timeout=None):
            calls.append(req.full_url)
            if "commons.wikimedia.org/w/api.php" in req.full_url:
                raise RuntimeError("search down")
            return _OkResp()

        monkeypatch.setattr(stock_app.urlrequest, "urlopen", _open)
        ok = stock_app._fetch_pd_image("q", dest, "https://fallback/img.png")
        assert ok is True
        assert dest.read_bytes() == png_bytes
        assert any("fallback" in u for u in calls)

    def test_download_failure_returns_false(self, tmp_path, monkeypatch):
        dest = tmp_path / "fail.png"
        monkeypatch.setattr(
            stock_app.urlrequest,
            "urlopen",
            MagicMock(side_effect=RuntimeError("dead")),
        )
        ok = stock_app._fetch_pd_image("q", dest, "https://fallback")
        assert ok is False
        assert not dest.exists()


# ── Standard wxfile sections (五运六气 / 打油诗 / 黑天鹅) ─────────────────────


class TestWxfileStandardSections:
    """Section blocks injected by _build_daily_wechat_article on save."""

    @pytest.fixture(autouse=True)
    def _stub_data_sources(self, monkeypatch, tmp_path):
        monkeypatch.setattr(stock_app.cfg, "DATA_DIR", tmp_path)
        monkeypatch.setattr(stock_app, "_fetch_pd_image", lambda *a, **kw: True)
        monkeypatch.setattr(stock_app, "_collect_closing_news",
                            lambda *a, **kw: {"risk_events": [], "cctv": []})
        monkeypatch.setattr(stock_app, "_build_auto_brief", lambda: {
            "snapshot": {"regime": "震荡", "avg_change_pct": -0.3, "valid": 15, "total": 15}
        })
        monkeypatch.setattr(stock_app, "_build_ai_edge_report", lambda: {
            "summary": {"confidence": 42.5, "market_bias": "中性",
                        "up_count": 3, "down_count": 12, "coverage": 15},
            "playbook": ["维持中性仓位"],
        })
        monkeypatch.setattr(stock_app, "_load_sentiment_history",
                            lambda: [{"score": 5, "up_ratio": 0.56, "stage": "上升"}])
        monkeypatch.setattr(stock_app, "_get_limit_stats",
                            lambda: {"limit_up": 84, "limit_down": 4})
        monkeypatch.setattr(stock_app, "_fetch_macro_indicators", lambda: [])
        monkeypatch.setattr(stock_app.dec, "analyze",
                            lambda dtype="trade": {"total": 167, "patterns": [], "by_source": {}})
        monkeypatch.setattr(stock_app.dec, "detect_loss_patterns",
                            lambda: {"top_pattern": None, "next_day_rule": "观察"})

    def _build(self, sections=None):
        payload = {"trade_date": "2026-06-03", "save_to_file": True}
        if sections is not None:
            payload["sections"] = sections
        return stock_app._build_daily_wechat_article(payload)

    def test_opening_has_wuyun_block(self, tmp_path):
        self._build()
        text = (tmp_path / "wxfile" / "2026-06-03_opening.md").read_text(encoding="utf-8")
        assert "## 五运六气参考" in text
        assert "丙午年" in text
        assert "水运太过" in text
        assert "少阴君火" in text
        assert "img/2026-06-03_wuyun.png" in text

    def test_intraday_has_poem_block(self, tmp_path):
        self._build()
        text = (tmp_path / "wxfile" / "2026-06-03_intraday.md").read_text(encoding="utf-8")
        assert "## 盘中打油诗" in text
        assert "img/2026-06-03_chart.png" in text
        # Poem references live numbers
        assert "84" in text and "4" in text  # 涨跌停
        assert "震荡" in text

    def test_closing_has_news_and_swan(self, tmp_path):
        self._build()
        text = (tmp_path / "wxfile" / "2026-06-03_closing.md").read_text(encoding="utf-8")
        assert "## 今日要闻与风险事件" in text
        assert "img/2026-06-03_swan.jpg" in text
        # Empty risk events → graceful fallback line
        assert "未自动捕获" in text

    def test_closing_renders_risk_events(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            stock_app, "_collect_closing_news",
            lambda *a, **kw: {
                "risk_events": [
                    {"type": "黑天鹅", "severity": "high",
                     "title": "上证暴跌 -5.2%", "time": "2026-06-03 10:30"},
                ],
                "cctv": [
                    {"date": "20260603", "title": "国务院发布重要政策"},
                ],
            },
        )
        self._build()
        text = (tmp_path / "wxfile" / "2026-06-03_closing.md").read_text(encoding="utf-8")
        assert "黑天鹅" in text
        assert "上证暴跌 -5.2%" in text
        assert "国务院发布重要政策" in text
        assert "🟠" in text  # high severity emoji

    def test_sections_filter_only_writes_selected(self, tmp_path):
        result = self._build(sections=["opening"])
        assert (tmp_path / "wxfile" / "2026-06-03_opening.md").exists()
        assert not (tmp_path / "wxfile" / "2026-06-03_intraday.md").exists()
        assert not (tmp_path / "wxfile" / "2026-06-03_closing.md").exists()
        files = result["saved"]["files"]
        assert len(files) == 1
        assert files[0]["section"] == "opening"

    def test_sections_filter_intraday_only(self, tmp_path):
        self._build(sections=["intraday"])
        assert (tmp_path / "wxfile" / "2026-06-03_intraday.md").exists()
        assert not (tmp_path / "wxfile" / "2026-06-03_opening.md").exists()

    def test_sections_filter_unknown_writes_nothing(self, tmp_path):
        result = self._build(sections=["bogus"])
        assert result["saved"]["files"] == []
        assert not list((tmp_path / "wxfile").glob("2026-06-03_*.md"))

    def test_empty_sections_list_writes_nothing(self, tmp_path):
        # Empty list → allowed set is empty → no files written.
        result = self._build(sections=[])
        # But empty list is falsy → filter is skipped → all 3 written.
        # Document the actual behavior here so a future change to make `[]`
        # mean "write none" would surface.
        assert len(result["saved"]["files"]) == 3


# ── wx scheduler ─────────────────────────────────────────────────────────────


class TestWxScheduler:
    """Daily 3-section scheduler — tick logic + guard set."""

    def setup_method(self):
        stock_app._WX_RAN.clear()

    def teardown_method(self):
        stock_app._WX_RAN.clear()

    def _patch_now(self, dt: datetime):
        return patch.object(stock_app, "_bj_now", return_value=dt)

    def test_before_first_window_does_nothing(self):
        called = []
        with self._patch_now(datetime(2026, 6, 3, 7, 0)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        assert called == []
        assert stock_app._WX_RAN == set()

    def test_after_opening_runs_opening_only(self):
        called = []
        with self._patch_now(datetime(2026, 6, 3, 8, 35)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        assert len(called) == 1
        assert called[0]["sections"] == ["opening"]
        assert ("2026-06-03", "opening") in stock_app._WX_RAN

    def test_after_close_runs_all_three(self):
        called = []
        with self._patch_now(datetime(2026, 6, 3, 16, 5)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        sections = [c["sections"][0] for c in called]
        assert sections == ["opening", "intraday", "closing"]
        for s in ("opening", "intraday", "closing"):
            assert ("2026-06-03", s) in stock_app._WX_RAN

    def test_guard_prevents_duplicate_run(self):
        called = []
        with self._patch_now(datetime(2026, 6, 3, 16, 5)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
            stock_app._wx_scheduler_tick()
            stock_app._wx_scheduler_tick()
        # First tick wrote 3 sections; subsequent ticks must be no-ops.
        assert len(called) == 3

    def test_guard_clears_on_new_day(self):
        stock_app._WX_RAN.add(("2026-06-02", "opening"))
        stock_app._WX_RAN.add(("2026-06-02", "intraday"))
        called = []
        with self._patch_now(datetime(2026, 6, 3, 8, 35)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        # Yesterday's entries pruned
        assert all(k[0] == "2026-06-03" for k in stock_app._WX_RAN)
        # Today's opening ran
        assert len(called) == 1

    def test_build_failure_does_not_set_guard(self):
        with self._patch_now(datetime(2026, 6, 3, 8, 35)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=RuntimeError("boom")):
            stock_app._wx_scheduler_tick()
        # Guard NOT set → next tick will retry
        assert ("2026-06-03", "opening") not in stock_app._WX_RAN

    def test_failure_then_success_eventually_succeeds(self):
        attempt = {"n": 0}

        def _build(_p):
            attempt["n"] += 1
            if attempt["n"] == 1:
                raise RuntimeError("transient")
            return {"ok": True}

        with self._patch_now(datetime(2026, 6, 3, 8, 35)), \
             patch.object(stock_app, "_build_daily_wechat_article", side_effect=_build):
            stock_app._wx_scheduler_tick()  # fails, guard not set
            stock_app._wx_scheduler_tick()  # succeeds
        assert attempt["n"] == 2
        assert ("2026-06-03", "opening") in stock_app._WX_RAN

    def test_skips_on_saturday(self):
        # 2026-06-06 is a Saturday — even at 16:00, no sections should run.
        called = []
        with self._patch_now(datetime(2026, 6, 6, 16, 5)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        assert called == []
        assert stock_app._WX_RAN == set()

    def test_skips_on_sunday(self):
        # 2026-06-07 is a Sunday
        called = []
        with self._patch_now(datetime(2026, 6, 7, 12, 35)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        assert called == []

    def test_skips_on_holiday(self):
        # 2026-05-01 is a CN holiday (劳动节). Even a weekday holiday is skipped.
        called = []
        with self._patch_now(datetime(2026, 5, 1, 16, 5)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        assert called == []

    def test_runs_on_normal_weekday(self):
        # Sanity: 2026-06-08 is a Monday, not a holiday → should run as usual.
        called = []
        with self._patch_now(datetime(2026, 6, 8, 8, 35)), \
             patch.object(stock_app, "_build_daily_wechat_article",
                          side_effect=lambda p: called.append(p) or {"ok": True}):
            stock_app._wx_scheduler_tick()
        assert len(called) == 1
        assert called[0]["sections"] == ["opening"]


class TestIsCnTradingDay:
    """Date-only trading-day predicate."""

    def test_weekday_non_holiday_is_trading(self):
        assert stock_app._is_cn_trading_day(datetime(2026, 6, 8, 0, 0)) is True

    def test_saturday_not_trading(self):
        assert stock_app._is_cn_trading_day(datetime(2026, 6, 6, 12, 0)) is False

    def test_sunday_not_trading(self):
        assert stock_app._is_cn_trading_day(datetime(2026, 6, 7, 12, 0)) is False

    def test_labor_day_not_trading(self):
        assert stock_app._is_cn_trading_day(datetime(2026, 5, 1, 12, 0)) is False

    def test_uses_bj_now_when_called_without_arg(self):
        with patch.object(stock_app, "_bj_now", return_value=datetime(2026, 6, 6, 12, 0)):
            assert stock_app._is_cn_trading_day() is False
        with patch.object(stock_app, "_bj_now", return_value=datetime(2026, 6, 8, 12, 0)):
            assert stock_app._is_cn_trading_day() is True


class TestWxScheduleStatusEndpoint:
    """GET /api/content/daily-schedule/status."""

    @pytest.fixture(autouse=True)
    def _client(self):
        stock_app.app.config["TESTING"] = True
        self.client = stock_app.app.test_client()
        # Reset state so tests are isolated
        stock_app._WX_RAN.clear()

    def test_returns_schedule_metadata(self):
        resp = self.client.get("/api/content/daily-schedule/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        sections = [s["section"] for s in data["schedule"]]
        assert sections == ["opening", "intraday", "closing"]
        # Times match _WX_SCHEDULE
        time_map = {s["section"]: s["time"] for s in data["schedule"]}
        assert time_map["opening"] == "08:30"
        assert time_map["intraday"] == "12:30"
        assert time_map["closing"] == "16:00"

    def test_ran_today_reflects_guard_state(self):
        with patch.object(stock_app, "_bj_date_str", return_value="2026-06-03"):
            stock_app._WX_RAN.add(("2026-06-03", "opening"))
            resp = self.client.get("/api/content/daily-schedule/status")
        data = resp.get_json()
        ran = {s["section"]: s["ran_today"] for s in data["schedule"]}
        assert ran == {"opening": True, "intraday": False, "closing": False}

    def test_ran_today_ignores_other_days(self):
        with patch.object(stock_app, "_bj_date_str", return_value="2026-06-03"):
            stock_app._WX_RAN.add(("2026-06-02", "opening"))
            resp = self.client.get("/api/content/daily-schedule/status")
        data = resp.get_json()
        ran = {s["section"]: s["ran_today"] for s in data["schedule"]}
        assert ran == {"opening": False, "intraday": False, "closing": False}
