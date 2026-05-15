"""Tests for autodev — autonomous decision loop."""

import pytest
from unittest.mock import patch
from pathlib import Path

from trading.autodev import AutoDev
from analysis.advisor import PositionInput, MarketContext, Signal


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx():
    return MarketContext(
        regime="偏强",
        sentiment_stage="上升",
        sentiment_score=3,
        tradable=True,
        confidence=80.0,
        risk_events=[],
    )


@pytest.fixture
def positions():
    return [
        PositionInput(
            ticker="000001.SZ", name="平安银行", shares=1000,
            cost=10.0, price=13.0, change_pct=1.5,
            high52=15.0, low52=8.0, volume=100000,
        ),
        PositionInput(
            ticker="600519.SH", name="贵州茅台", shares=100,
            cost=1800.0, price=1600.0, change_pct=-2.0,
            high52=2000.0, low52=1500.0, volume=50000,
        ),
    ]


@pytest.fixture
def dev():
    return AutoDev(strategy_name="rule_v1", risk_pref="balanced")


@pytest.fixture(autouse=True)
def _clean_decisions(tmp_path, monkeypatch):
    """Isolate decision journal to temp dir for each test."""
    import trading.decision as d
    fake_file = tmp_path / "decisions.json"
    monkeypatch.setattr(d, "_DECISIONS_FILE", fake_file)


# ── AutoDev.__init__ ──────────────────────────────────────────────────────────


class TestAutoDevInit:
    def test_default_strategy(self):
        dev = AutoDev()
        assert dev.strategy.name == "rule_v1"
        assert dev.risk_pref == "balanced"

    def test_custom_strategy(self):
        dev = AutoDev(strategy_name="conservative", risk_pref="aggressive")
        assert dev.strategy.name == "conservative_v1"
        assert dev.risk_pref == "aggressive"

    def test_invalid_strategy_raises(self):
        with pytest.raises(FileNotFoundError):
            AutoDev(strategy_name="nonexistent_xyz")

    def test_status_no_cycle(self, dev):
        s = dev.status
        assert s["strategy"] == "rule_v1"
        assert s["last_cycle"] is None


# ── Step 1: Observe ──────────────────────────────────────────────────────────


class TestObserve:
    def test_observe_structure(self, dev, positions, ctx):
        obs = dev.observe(positions, ctx)
        assert obs["positions"] is positions
        assert obs["context"] is ctx
        assert obs["strategy"] == "rule_v1"
        assert obs["risk_pref"] == "balanced"
        assert "observed_at" in obs

    def test_observe_empty_positions(self, dev, ctx):
        obs = dev.observe([], ctx)
        assert obs["positions"] == []


# ── Step 2: Decide ───────────────────────────────────────────────────────────


class TestDecide:
    def test_decide_returns_signals(self, dev, positions, ctx):
        obs = dev.observe(positions, ctx)
        signals = dev.decide(obs)
        assert len(signals) == 2
        assert all(isinstance(s, Signal) for s in signals)

    def test_decide_signal_tickers(self, dev, positions, ctx):
        obs = dev.observe(positions, ctx)
        signals = dev.decide(obs)
        tickers = {s.ticker for s in signals}
        assert tickers == {"000001.SZ", "600519.SH"}

    def test_decide_empty_positions(self, dev, ctx):
        obs = dev.observe([], ctx)
        signals = dev.decide(obs)
        assert signals == []


# ── Step 3: Act ──────────────────────────────────────────────────────────────


class TestAct:
    def test_act_creates_decisions_for_actionable(self, dev, ctx):
        """Only actionable signals (buy/sell/add/reduce) create decisions."""
        obs = dev.observe([], ctx)
        signals = [
            Signal(ticker="A", name="StockA", action="sell", strength=4, reasons=["test"]),
            Signal(ticker="B", name="StockB", action="hold", strength=1, reasons=["ok"]),
            Signal(ticker="C", name="StockC", action="add", strength=2, reasons=["low"]),
        ]
        decisions = dev.act(signals, obs)
        assert len(decisions) == 2  # sell + add, skip hold
        symbols = {d["symbol"] for d in decisions}
        assert symbols == {"StockA", "StockC"}

    def test_act_tags_autodev(self, dev, ctx):
        obs = dev.observe([], ctx)
        signals = [
            Signal(ticker="A", name="X", action="buy", strength=3, reasons=["go"]),
        ]
        decisions = dev.act(signals, obs)
        assert len(decisions) == 1
        assert "autodev" in decisions[0]["tags"]
        assert "rule_v1" in decisions[0]["tags"]

    def test_act_sets_source_rule(self, dev, ctx):
        obs = dev.observe([], ctx)
        signals = [
            Signal(ticker="A", name="X", action="sell", strength=5, reasons=["stop"]),
        ]
        decisions = dev.act(signals, obs)
        assert decisions[0]["source"] == "rule"

    def test_act_maps_actions(self, dev, ctx):
        obs = dev.observe([], ctx)
        signals = [
            Signal(ticker="A", name="X", action="buy", strength=3, reasons=[""]),
            Signal(ticker="B", name="Y", action="reduce", strength=2, reasons=[""]),
        ]
        decisions = dev.act(signals, obs)
        actions = {d["symbol"]: d["action"] for d in decisions}
        assert actions["X"] == "BUY"
        assert actions["Y"] == "SELL"  # reduce maps to SELL

    def test_act_no_actionable(self, dev, ctx):
        obs = dev.observe([], ctx)
        signals = [
            Signal(ticker="A", name="X", action="hold", strength=1, reasons=["wait"]),
        ]
        decisions = dev.act(signals, obs)
        assert decisions == []

    def test_act_records_trade_context(self, dev, ctx):
        obs = dev.observe([], ctx)
        signals = [
            Signal(
                ticker="A", name="X", action="sell", strength=4,
                reasons=["test"], factors=[{"name": "盈亏", "score": -2}],
            ),
        ]
        decisions = dev.act(signals, obs)
        tc = decisions[0].get("trade_context", {})
        assert tc["strategy"] == "rule_v1"
        assert "factors" in tc


# ── Step 4: Evaluate ─────────────────────────────────────────────────────────


class TestEvaluatePast:
    def test_no_prices_returns_empty(self, dev):
        assert dev.evaluate_past() == []
        assert dev.evaluate_past({}) == []

    def test_evaluates_autodev_acted(self, dev, ctx):
        """Create an autodev decision, advance to acted, then evaluate."""
        from trading.decision import update_decision

        obs = dev.observe([], ctx)
        signals = [
            Signal(
                ticker="A", name="Stock", action="buy", strength=3,
                reasons=["go"], stop_loss=9.0, take_profit=12.0,
            ),
        ]
        decisions = dev.act(signals, obs)
        did = decisions[0]["id"]
        # Manually set price and move to acted state
        update_decision(did, {"state": "acted", "price": 10.0, "size": 100})

        results = dev.evaluate_past({"Stock": 11.0})
        assert len(results) == 1
        assert results[0]["ok"]
        assert results[0]["pnl"] > 0


# ── Step 5: Learn ────────────────────────────────────────────────────────────


class TestLearn:
    def test_learn_returns_analysis(self, dev):
        analysis = dev.learn()
        assert "ok" in analysis
        assert "patterns" in analysis
        assert "suggestions" in analysis

    def test_learn_with_no_stop_loss_pattern(self, dev, ctx):
        """Buys without stop_loss should generate a suggestion."""
        from trading.decision import create_decision

        for i in range(3):
            create_decision(
                title=f"Buy {i}", dtype="trade", action="BUY",
                symbol=f"S{i}", price=10.0, source="manual",
                # no stop_loss
            )

        analysis = dev.learn()
        types = {s["type"] for s in analysis["suggestions"]}
        assert "weight_adjust" in types

    def test_learn_with_low_confidence(self, dev, ctx):
        from trading.decision import create_decision

        for i in range(3):
            create_decision(
                title=f"LC {i}", dtype="trade", action="BUY",
                symbol=f"LC{i}", price=10.0, confidence=0.2,
                source="manual",
            )

        analysis = dev.learn()
        types = {s["type"] for s in analysis["suggestions"]}
        assert "threshold" in types


# ── Full Cycle ────────────────────────────────────────────────────────────────


class TestRunCycle:
    def test_cycle_returns_all_sections(self, dev, positions, ctx):
        result = dev.run_cycle(positions, ctx)
        assert result["ok"]
        assert "cycle" in result
        assert "signals" in result
        assert "decisions" in result
        assert "evaluations" in result
        assert "analysis" in result

    def test_cycle_summary(self, dev, positions, ctx):
        result = dev.run_cycle(positions, ctx)
        c = result["cycle"]
        assert c["strategy"] == "rule_v1"
        assert c["signals_count"] == 2
        assert "observed_at" in c

    def test_cycle_updates_status(self, dev, positions, ctx):
        assert dev.status["last_cycle"] is None
        dev.run_cycle(positions, ctx)
        assert dev.status["last_cycle"] is not None

    def test_cycle_empty_positions(self, dev, ctx):
        result = dev.run_cycle([], ctx)
        assert result["ok"]
        assert result["cycle"]["signals_count"] == 0
        assert result["cycle"]["acted_count"] == 0

    def test_cycle_with_different_strategy(self, positions, ctx):
        dev = AutoDev(strategy_name="conservative", risk_pref="conservative")
        result = dev.run_cycle(positions, ctx)
        assert result["ok"]
        assert result["cycle"]["strategy"] == "conservative_v1"
