"""Tests for strategy_loader — YAML strategy loading and evaluation."""

import json
import pytest
from pathlib import Path

from trading.strategy_loader import (
    load_strategy,
    list_strategies,
    YAMLStrategy,
    FactorResult,
    EVALUATORS,
    STRATEGIES_DIR,
)
from analysis.advisor import PositionInput, MarketContext, Signal


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def bullish_ctx():
    return MarketContext(
        regime="偏强",
        sentiment_stage="上升",
        sentiment_score=3,
        tradable=True,
        confidence=80.0,
        risk_events=[],
    )


@pytest.fixture
def bearish_ctx():
    return MarketContext(
        regime="偏弱",
        sentiment_stage="退潮",
        sentiment_score=-3,
        tradable=False,
        confidence=20.0,
        risk_events=[{"title": "暴雷", "severity": "high"}],
    )


@pytest.fixture
def neutral_ctx():
    return MarketContext(
        regime="震荡",
        sentiment_stage="分歧",
        sentiment_score=0,
        tradable=True,
        confidence=50.0,
        risk_events=[],
    )


@pytest.fixture
def profitable_pos():
    return PositionInput(
        ticker="000001.SZ", name="平安银行", shares=1000,
        cost=10.0, price=13.0, change_pct=1.5,
        high52=15.0, low52=8.0, volume=100000,
    )


@pytest.fixture
def losing_pos():
    return PositionInput(
        ticker="600519.SH", name="贵州茅台", shares=100,
        cost=1800.0, price=1600.0, change_pct=-2.0,
        high52=2000.0, low52=1500.0, volume=50000,
    )


# ── list_strategies ───────────────────────────────────────────────────────────


class TestListStrategies:
    def test_returns_list(self):
        result = list_strategies()
        assert isinstance(result, list)

    def test_finds_rule_v1(self):
        result = list_strategies()
        names = [s["name"] for s in result]
        assert "rule_v1" in names

    def test_finds_conservative(self):
        result = list_strategies()
        names = [s["name"] for s in result]
        assert "conservative_v1" in names

    def test_strategy_has_fields(self):
        result = list_strategies()
        s = result[0]
        assert "name" in s
        assert "version" in s
        assert "description" in s
        assert "file" in s
        assert "factors" in s


# ── load_strategy ─────────────────────────────────────────────────────────────


class TestLoadStrategy:
    def test_load_rule_v1(self):
        s = load_strategy("rule_v1")
        assert s.name == "rule_v1"
        assert s.version == 1
        assert isinstance(s, YAMLStrategy)

    def test_load_conservative(self):
        s = load_strategy("conservative")
        assert s.name == "conservative_v1"

    def test_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_strategy("nonexistent_xyz")

    def test_factor_weights(self):
        s = load_strategy("rule_v1")
        w = s.factor_weights
        assert w["盈亏"] == 0.30
        assert w["风险"] == 0.25
        total = sum(w.values())
        assert abs(total - 1.0) < 0.01

    def test_conservative_higher_risk_weight(self):
        rv1 = load_strategy("rule_v1")
        con = load_strategy("conservative")
        assert con.factor_weights["风险"] > rv1.factor_weights["风险"]

    def test_risk_profiles(self):
        s = load_strategy("rule_v1")
        th = s.get_thresholds("conservative")
        assert th["stop_loss"] == 0.07
        assert th["take_profit"] == 0.15


# ── YAMLStrategy.evaluate ────────────────────────────────────────────────────


class TestYAMLStrategyEvaluate:
    def test_returns_signal(self, profitable_pos, bullish_ctx):
        s = load_strategy("rule_v1")
        sig = s.evaluate(profitable_pos, bullish_ctx, "balanced")
        assert isinstance(sig, Signal)
        assert sig.ticker == "000001.SZ"
        assert sig.name == "平安银行"

    def test_has_factors(self, profitable_pos, bullish_ctx):
        s = load_strategy("rule_v1")
        sig = s.evaluate(profitable_pos, bullish_ctx, "balanced")
        assert len(sig.factors) == 5
        names = {f["name"] for f in sig.factors}
        assert names == {"盈亏", "价位", "风险", "情绪", "趋势"}

    def test_stop_loss_trigger(self, bullish_ctx):
        """Position at -15% should trigger sell for balanced profile."""
        pos = PositionInput(
            ticker="T", name="Test", shares=100,
            cost=100.0, price=85.0, change_pct=-15.0,
            high52=120.0, low52=80.0, volume=10000,
        )
        s = load_strategy("rule_v1")
        sig = s.evaluate(pos, bullish_ctx, "balanced")
        assert sig.action == "sell"
        assert sig.strength >= 4

    def test_take_profit_trigger(self, bullish_ctx):
        """Position at +30% should trigger reduce for balanced profile."""
        pos = PositionInput(
            ticker="T", name="Test", shares=100,
            cost=100.0, price=130.0, change_pct=30.0,
            high52=135.0, low52=80.0, volume=10000,
        )
        s = load_strategy("rule_v1")
        sig = s.evaluate(pos, bullish_ctx, "balanced")
        assert sig.action == "reduce"

    def test_black_swan_triggers_sell(self, profitable_pos, bearish_ctx):
        s = load_strategy("rule_v1")
        sig = s.evaluate(profitable_pos, bearish_ctx, "balanced")
        assert sig.action == "sell"
        assert sig.strength >= 4

    def test_no_price_returns_hold(self, bullish_ctx):
        pos = PositionInput(
            ticker="T", name="Test", shares=0,
            cost=0, price=0, change_pct=0,
            high52=None, low52=None, volume=0,
        )
        s = load_strategy("rule_v1")
        sig = s.evaluate(pos, bullish_ctx, "balanced")
        assert sig.action == "hold"
        assert "数据缺失" in sig.reasons

    def test_neutral_hold(self, neutral_ctx):
        """Mid-range position in neutral market → hold."""
        pos = PositionInput(
            ticker="T", name="Test", shares=100,
            cost=100.0, price=102.0, change_pct=2.0,
            high52=120.0, low52=80.0, volume=10000,
        )
        s = load_strategy("rule_v1")
        sig = s.evaluate(pos, neutral_ctx, "balanced")
        assert sig.action == "hold"

    def test_stop_take_profit_prices(self, profitable_pos, bullish_ctx):
        s = load_strategy("rule_v1")
        sig = s.evaluate(profitable_pos, bullish_ctx, "balanced")
        assert sig.stop_loss == 9.0   # cost=10, stop=10%
        assert sig.take_profit == 12.5  # cost=10, tp=25%

    def test_conservative_tighter_thresholds(self, bullish_ctx):
        """Conservative stop-loss is tighter → triggers sell earlier."""
        pos = PositionInput(
            ticker="T", name="Test", shares=100,
            cost=100.0, price=92.0, change_pct=-8.0,
            high52=None, low52=None, volume=10000,
        )
        rule = load_strategy("rule_v1")
        cons = load_strategy("conservative")
        sig_rule = rule.evaluate(pos, bullish_ctx, "balanced")
        sig_cons = cons.evaluate(pos, bullish_ctx, "balanced")
        # -8% loss: rule_v1 balanced (10%) = hold, conservative balanced (7%) = sell
        assert sig_rule.action == "hold"
        assert sig_cons.action == "sell"


# ── Invalid config ────────────────────────────────────────────────────────────


class TestInvalidConfig:
    def test_unknown_evaluator_raises(self):
        config = {
            "name": "bad",
            "factors": [{"name": "X", "weight": 0.5, "evaluator": "nonexistent"}],
        }
        with pytest.raises(ValueError, match="Unknown evaluator"):
            YAMLStrategy(config)

    def test_missing_name_raises(self):
        config = {"factors": []}
        with pytest.raises(KeyError):
            YAMLStrategy(config)


# ── JSON fallback ─────────────────────────────────────────────────────────────


class TestJSONFallback:
    def test_load_json_strategy(self, tmp_path, monkeypatch):
        """Strategies can also be loaded from JSON files."""
        import trading.strategy_loader as sl

        config = {
            "name": "json_test",
            "version": 1,
            "risk_profiles": {
                "balanced": {"stop_loss": 0.10, "take_profit": 0.25}
            },
            "factors": [
                {"name": "盈亏", "weight": 1.0, "evaluator": "pnl"},
            ],
        }
        (tmp_path / "json_test.json").write_text(
            json.dumps(config), encoding="utf-8"
        )
        monkeypatch.setattr(sl, "STRATEGIES_DIR", tmp_path)
        s = sl.load_strategy("json_test")
        assert s.name == "json_test"
        assert len(s._factors) == 1
