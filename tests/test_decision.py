"""Tests for Decision Journal (src/decision.py)."""

import json
import sys
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from trading import decision as dec


@pytest.fixture(autouse=True)
def _tmp_decisions(tmp_path, monkeypatch):
    """Redirect decisions file to a temp directory."""
    tmp_file = tmp_path / "decisions.json"
    monkeypatch.setattr(dec, "_DECISIONS_FILE", tmp_file)
    yield tmp_file


class TestCreateDecision:
    def test_basic_create(self):
        d = dec.create_decision("Buy AAPL on dip")
        assert d["title"] == "Buy AAPL on dip"
        assert d["type"] == "trade"
        assert d["state"] == "idea"
        assert d["id"]
        assert d["created_at"]
        assert d["tags"] == []

    def test_create_with_all_fields(self):
        d = dec.create_decision(
            title="Switch jobs",
            dtype="work",
            context="Market downturn, good offers",
            action="Accepted offer B",
            outcome="Salary +30%",
            tags=["career", "risk"],
            state="reviewed",
        )
        assert d["type"] == "work"
        assert d["state"] == "reviewed"
        assert d["tags"] == ["career", "risk"]
        assert d["outcome"] == "Salary +30%"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="type must be"):
            dec.create_decision("test", dtype="invalid")

    def test_invalid_state_raises(self):
        with pytest.raises(ValueError, match="state must be"):
            dec.create_decision("test", state="invalid")

    def test_whitespace_stripped(self):
        d = dec.create_decision("  spaced title  ", context="  ctx  ")
        assert d["title"] == "spaced title"
        assert d["context"] == "ctx"

    def test_tags_cleaned(self):
        d = dec.create_decision("t", tags=["  a ", "", "  b  ", ""])
        assert d["tags"] == ["a", "b"]


class TestListDecisions:
    def test_list_empty(self):
        assert dec.list_decisions() == []

    def test_list_all(self):
        dec.create_decision("A", dtype="trade")
        dec.create_decision("B", dtype="life")
        dec.create_decision("C", dtype="work")
        assert len(dec.list_decisions()) == 3

    def test_filter_by_type(self):
        dec.create_decision("A", dtype="trade")
        dec.create_decision("B", dtype="life")
        result = dec.list_decisions(dtype="trade")
        assert len(result) == 1
        assert result[0]["title"] == "A"

    def test_filter_by_state(self):
        dec.create_decision("A", state="idea")
        dec.create_decision("B", state="acted")
        result = dec.list_decisions(state="acted")
        assert len(result) == 1
        assert result[0]["title"] == "B"

    def test_filter_by_type_and_state(self):
        dec.create_decision("A", dtype="trade", state="idea")
        dec.create_decision("B", dtype="trade", state="acted")
        dec.create_decision("C", dtype="life", state="idea")
        result = dec.list_decisions(dtype="trade", state="idea")
        assert len(result) == 1
        assert result[0]["title"] == "A"


class TestGetDecision:
    def test_get_existing(self):
        d = dec.create_decision("Find me")
        found = dec.get_decision(d["id"])
        assert found["title"] == "Find me"

    def test_get_missing(self):
        assert dec.get_decision("nonexistent") is None


class TestUpdateDecision:
    def test_update_title_and_state(self):
        d = dec.create_decision("Original")
        updated = dec.update_decision(d["id"], {"title": "Changed", "state": "acted"})
        assert updated["title"] == "Changed"
        assert updated["state"] == "acted"
        assert updated["updated_at"] >= d["created_at"]

    def test_update_tags(self):
        d = dec.create_decision("T", tags=["a"])
        updated = dec.update_decision(d["id"], {"tags": ["b", "c"]})
        assert updated["tags"] == ["b", "c"]

    def test_update_invalid_type(self):
        d = dec.create_decision("T")
        with pytest.raises(ValueError):
            dec.update_decision(d["id"], {"type": "bad"})

    def test_update_invalid_state(self):
        d = dec.create_decision("T")
        with pytest.raises(ValueError):
            dec.update_decision(d["id"], {"state": "bad"})

    def test_update_nonexistent(self):
        assert dec.update_decision("nope", {"title": "x"}) is None

    def test_ignores_unknown_fields(self):
        d = dec.create_decision("T")
        updated = dec.update_decision(d["id"], {"title": "New", "hacker": "drop table"})
        assert updated["title"] == "New"
        assert "hacker" not in updated


class TestDeleteDecision:
    def test_delete_existing(self):
        d = dec.create_decision("Delete me")
        assert dec.delete_decision(d["id"]) is True
        assert dec.list_decisions() == []

    def test_delete_nonexistent(self):
        assert dec.delete_decision("nope") is False


class TestPersistence:
    def test_survives_reload(self, _tmp_decisions):
        dec.create_decision("Persistent")
        # Re-read from file
        data = json.loads(_tmp_decisions.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["title"] == "Persistent"

    def test_max_cap(self, monkeypatch):
        monkeypatch.setattr(dec, "MAX_DECISIONS", 3)
        for i in range(5):
            dec.create_decision(f"D{i}")
        result = dec.list_decisions()
        assert len(result) == 3
        assert result[0]["title"] == "D2"  # oldest kept


class TestKanbanFlow:
    """Test a realistic kanban workflow: idea → decided → acted → reviewed."""

    def test_full_flow(self):
        d = dec.create_decision("Buy 600519 breakout", dtype="trade", tags=["breakout"])
        assert d["state"] == "idea"

        d = dec.update_decision(d["id"], {"state": "decided", "action": "Set limit order at 1700"})
        assert d["state"] == "decided"
        assert d["action"] == "Set limit order at 1700"

        d = dec.update_decision(d["id"], {"state": "acted"})
        assert d["state"] == "acted"

        d = dec.update_decision(d["id"], {"state": "reviewed", "outcome": "+5% in 3 days"})
        assert d["state"] == "reviewed"
        assert d["outcome"] == "+5% in 3 days"


# ── Trade-specific fields ────────────────────────────────────────────────────

class TestTradeFields:
    """Test the extended Decision model with trading fields."""

    def test_create_with_trade_fields(self):
        d = dec.create_decision(
            "买入晶合集成",
            dtype="trade",
            action="BUY",
            symbol="晶合集成",
            price=33.7,
            size=1000,
            confidence=0.6,
            stop_loss=31.5,
            take_profit=37.0,
            source="manual",
        )
        assert d["symbol"] == "晶合集成"
        assert d["price"] == 33.7
        assert d["size"] == 1000
        assert d["confidence"] == 0.6
        assert d["stop_loss"] == 31.5
        assert d["take_profit"] == 37.0
        assert d["source"] == "manual"

    def test_trade_fields_only_for_trade_type(self):
        d = dec.create_decision(
            "Switch jobs",
            dtype="work",
            symbol="AAPL",
            price=100,
        )
        # Non-trade types should NOT get trade fields
        assert "symbol" not in d
        assert "price" not in d

    def test_confidence_clamped(self):
        d = dec.create_decision("test", symbol="X", confidence=1.5)
        assert d["confidence"] == 1.0
        d2 = dec.create_decision("test2", symbol="X", confidence=-0.5)
        assert d2["confidence"] == 0.0  # clamped to 0

    def test_max_drawdown_clamped(self):
        d = dec.create_decision("test", symbol="X", max_drawdown=0.15)
        assert d["max_drawdown"] == 0.15

    def test_trade_context_dict(self):
        ctx = {"type": "breakout", "volume": "high", "emotion": "fomo"}
        d = dec.create_decision("test", symbol="X", price=10, trade_context=ctx)
        assert d["trade_context"] == ctx

    def test_invalid_source_ignored(self):
        d = dec.create_decision("test", symbol="X", price=10, source="hacker")
        assert "source" not in d or d.get("source") != "hacker"

    def test_ai_source(self):
        d = dec.create_decision("test", symbol="X", price=10, source="ai")
        assert d["source"] == "ai"

    def test_update_trade_fields(self):
        d = dec.create_decision("test", symbol="X", price=10)
        updated = dec.update_decision(d["id"], {"price": 15, "stop_loss": 12})
        assert updated["price"] == 15
        assert updated["stop_loss"] == 12

    def test_full_decision_example(self):
        """The real example from the spec."""
        d = dec.create_decision(
            "突破压力位追涨",
            dtype="trade",
            action="BUY",
            symbol="晶合集成",
            price=33.7,
            size=1000,
            confidence=0.6,
            stop_loss=31.5,
            take_profit=37.0,
            trade_context={"type": "breakout", "volume": "high"},
            source="manual",
        )
        assert d["action"] == "BUY"
        assert d["symbol"] == "晶合集成"
        assert d["price"] == 33.7
        assert d["size"] == 1000
        assert d["trade_context"]["type"] == "breakout"


# ── Evaluate ──────────────────────────────────────────────────────────────────

class TestEvaluate:
    """Test post-trade decision evaluation."""

    def test_evaluate_profit(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100)
        r = dec.evaluate(d["id"], current_price=12)
        assert r["ok"]
        assert r["pnl"] == 200.0
        assert r["pnl_pct"] == 20.0
        assert "盈利" in r["verdict"]

    def test_evaluate_loss(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100)
        r = dec.evaluate(d["id"], current_price=8)
        assert r["ok"]
        assert r["pnl"] == -200.0
        assert "亏损" in r["verdict"]

    def test_evaluate_hit_stop_loss(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100, stop_loss=9)
        r = dec.evaluate(d["id"], current_price=8.5)
        assert r["hit_stop_loss"]
        assert not r["risk_ok"]
        assert "止损" in r["verdict"]

    def test_evaluate_hit_take_profit(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100, take_profit=12)
        r = dec.evaluate(d["id"], current_price=13)
        assert r["hit_take_profit"]
        assert "止盈" in r["verdict"]

    def test_evaluate_sell_action(self):
        d = dec.create_decision("sell", action="SELL", symbol="X", price=10, size=100)
        r = dec.evaluate(d["id"], current_price=8)
        # SELL profits when price drops
        assert r["pnl"] == 200.0
        assert "盈利" in r["verdict"]

    def test_evaluate_not_found(self):
        r = dec.evaluate("nonexistent", 10)
        assert not r["ok"]

    def test_evaluate_no_price(self):
        d = dec.create_decision("hold", action="HOLD", symbol="X")
        r = dec.evaluate(d["id"], current_price=10)
        assert not r["ok"]

    def test_evaluate_non_trade(self):
        d = dec.create_decision("life", dtype="life")
        r = dec.evaluate(d["id"], current_price=10)
        assert not r["ok"]

    def test_evaluate_high_conf_loss(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100, confidence=0.8)
        r = dec.evaluate(d["id"], current_price=8)
        assert "高信心决策亏损" in r["verdict"]


class TestHasLossMarker:
    """Test the _has_loss_marker helper covering numeric and text signals."""

    def test_numeric_pnl_negative(self):
        assert dec._has_loss_marker({"pnl": -100.0})
        assert dec._has_loss_marker({"pnl_pct": -3.5})

    def test_numeric_pnl_positive_or_zero(self):
        assert not dec._has_loss_marker({"pnl": 0})
        assert not dec._has_loss_marker({"pnl_pct": 5.0})

    def test_text_keywords(self):
        assert dec._has_loss_marker({"outcome": "今日亏损"})
        assert dec._has_loss_marker({"verdict": "触发止损"})
        assert dec._has_loss_marker({"context": "回撤明显"})
        assert dec._has_loss_marker({"outcome": "被打脸"})

    def test_negative_percent_in_text(self):
        assert dec._has_loss_marker({"outcome": "下跌 -2.3%"})

    def test_no_signals(self):
        assert not dec._has_loss_marker({"outcome": "盈利", "pnl": 100})
        assert not dec._has_loss_marker({})


class TestDetectLossPatterns:
    """Test rule-based loss pattern detector."""

    def test_detect_top_pattern_no_stop_loss(self):
        dec.create_decision("追高买入", action="BUY", symbol="A", price=10, confidence=0.8)
        dec.create_decision("回撤止损", action="BUY", symbol="B", price=20, outcome="亏损 -5%", confidence=0.75)

        r = dec.detect_loss_patterns()
        assert r["ok"]
        assert r["total"] == 2
        assert r["top_pattern"] is not None
        assert r["top_pattern"]["type"] == "buy_without_stop"
        assert "无止损" in r["next_day_rule"]

    def test_detect_empty(self):
        r = dec.detect_loss_patterns()
        assert r["ok"]
        assert r["total"] == 0
        assert r["patterns"] == []
        assert "暂无足够样本" in r["next_day_rule"]

    def test_detect_overtrading_day(self):
        for i in range(5):
            dec.create_decision(f"t{i}", action="BUY", symbol=f"S{i}", price=10 + i)
        r = dec.detect_loss_patterns()
        types = [p["type"] for p in r["patterns"]]
        assert "overtrading" in types

    def test_detect_high_confidence_loss(self):
        # All trades have stop_loss, so buy_without_stop won't dominate
        dec.create_decision(
            "高信心买入", action="BUY", symbol="A", price=10,
            stop_loss=9, confidence=0.85, outcome="亏损 -3%",
        )
        dec.create_decision(
            "高信心加仓", action="BUY", symbol="B", price=20,
            stop_loss=18, confidence=0.9, outcome="止损 -4%",
        )
        r = dec.detect_loss_patterns()
        types = [p["type"] for p in r["patterns"]]
        assert "high_confidence_loss" in types

    def test_detect_chase_fomo(self):
        dec.create_decision("追高入场", action="BUY", symbol="A", price=10, stop_loss=9)
        r = dec.detect_loss_patterns()
        types = [p["type"] for p in r["patterns"]]
        assert "chase_fomo" in types

    def test_detect_acted_not_reviewed(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, stop_loss=9)
        dec.update_decision(d["id"], {"state": "acted"})
        r = dec.detect_loss_patterns()
        types = [p["type"] for p in r["patterns"]]
        assert "acted_not_reviewed" in types

    def test_detect_consecutive_losses(self):
        # Two consecutive losses with stop_loss set, so the consecutive rule is the surviving signal
        dec.create_decision(
            "first loss", action="BUY", symbol="A", price=10,
            stop_loss=9, outcome="亏损 -2%",
        )
        dec.create_decision(
            "second loss", action="BUY", symbol="B", price=20,
            stop_loss=18, outcome="止损 -3%",
        )
        r = dec.detect_loss_patterns()
        types = [p["type"] for p in r["patterns"]]
        assert "consecutive_losses" in types

    def test_severity_ordering_top_pattern(self):
        # Mix danger + warn signals; danger should sort to top
        dec.create_decision("no sl", action="BUY", symbol="A", price=10)  # danger: buy_without_stop
        dec.create_decision("追高", action="BUY", symbol="B", price=10, stop_loss=9)  # warn: chase_fomo
        r = dec.detect_loss_patterns()
        assert r["top_pattern"]["severity"] == "danger"

    def test_explicit_decisions_arg(self):
        # When passed explicitly, internal store is bypassed
        custom = [{"action": "BUY", "title": "x"}]
        r = dec.detect_loss_patterns(decisions=custom)
        assert r["total"] == 1
        types = [p["type"] for p in r["patterns"]]
        assert "buy_without_stop" in types

    def test_evaluate_low_conf_win(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100, confidence=0.2)
        r = dec.evaluate(d["id"], current_price=12)
        assert "低信心决策盈利" in r["verdict"]

    def test_evaluate_max_drawdown_breach(self):
        d = dec.create_decision("buy", action="BUY", symbol="X", price=10, size=100, max_drawdown=0.1)
        r = dec.evaluate(d["id"], current_price=8)
        assert not r["risk_ok"]
        assert "最大回撤" in r["verdict"]

    def test_evaluate_chinese_action(self):
        """Chinese action labels should also work."""
        d = dec.create_decision("test", action="买入", symbol="X", price=10, size=100)
        r = dec.evaluate(d["id"], current_price=12)
        assert r["pnl"] == 200.0


# ── Analyze ───────────────────────────────────────────────────────────────────

class TestAnalyze:
    """Test decision pattern analysis."""

    def test_analyze_empty(self):
        r = dec.analyze()
        assert r["ok"]
        assert r["total"] == 0

    def test_analyze_counts(self):
        dec.create_decision("b1", action="BUY", symbol="A", price=10)
        dec.create_decision("b2", action="BUY", symbol="B", price=20)
        dec.create_decision("s1", action="SELL", symbol="C", price=30)
        r = dec.analyze()
        assert r["total"] == 3
        assert r["buys"] == 2
        assert r["sells"] == 1

    def test_analyze_low_confidence_pattern(self):
        dec.create_decision("fomo", action="BUY", symbol="X", price=10, confidence=0.2)
        dec.create_decision("fomo2", action="BUY", symbol="Y", price=20, confidence=0.3)
        r = dec.analyze()
        types = [p["type"] for p in r["patterns"]]
        assert "low_confidence" in types

    def test_analyze_no_stop_loss_pattern(self):
        dec.create_decision("buy", action="BUY", symbol="X", price=10)
        r = dec.analyze()
        types = [p["type"] for p in r["patterns"]]
        assert "no_stop_loss" in types

    def test_analyze_unreviewed_pattern(self):
        dec.create_decision("buy", action="BUY", symbol="X", price=10, state="acted")
        r = dec.analyze()
        types = [p["type"] for p in r["patterns"]]
        assert "no_review" in types

    def test_analyze_ai_ratio(self):
        dec.create_decision("manual", action="BUY", symbol="X", price=10, source="manual")
        dec.create_decision("ai1", action="BUY", symbol="Y", price=20, source="ai")
        r = dec.analyze()
        types = [p["type"] for p in r["patterns"]]
        assert "ai_ratio" in types

    def test_analyze_by_source(self):
        dec.create_decision("m", action="BUY", symbol="X", price=10, source="manual")
        dec.create_decision("a", action="BUY", symbol="Y", price=20, source="ai")
        r = dec.analyze()
        assert r["by_source"]["manual"] == 1
        assert r["by_source"]["ai"] == 1

    def test_analyze_by_state(self):
        dec.create_decision("i", symbol="X", price=10, state="idea")
        dec.create_decision("a", symbol="Y", price=20, state="acted")
        r = dec.analyze()
        assert r["by_state"]["idea"] == 1
        assert r["by_state"]["acted"] == 1
