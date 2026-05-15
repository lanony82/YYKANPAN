"""Tests for advisor.py — Trading Advisor (14 spec'd cases + extras)."""

from __future__ import annotations

import pytest

from analysis.advisor import (
    AdvisorOutput,
    MarketContext,
    PositionInput,
    RuleBasedStrategy,
    Signal,
    Strategy,
    evaluate_portfolio,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pos(
    ticker="600519.SS", name="贵州茅台",
    shares=100, cost=100.0, price=100.0,
    change_pct=0.0, high52=None, low52=None, volume=10000,
) -> PositionInput:
    return PositionInput(
        ticker=ticker, name=name, shares=shares, cost=cost,
        price=price, change_pct=change_pct,
        high52=high52, low52=low52, volume=volume,
    )


def _ctx(
    regime="震荡", sentiment_stage="分歧", sentiment_score=0,
    tradable=True, confidence=50.0, risk_events=None,
) -> MarketContext:
    return MarketContext(
        regime=regime, sentiment_stage=sentiment_stage,
        sentiment_score=sentiment_score, tradable=tradable,
        confidence=confidence, risk_events=risk_events or [],
    )


# ── Test 1: Empty positions ──────────────────────────────────────────────────

class TestEmptyPositions:
    def test_returns_observe(self):
        result = evaluate_portfolio([], _ctx())
        assert result.ok is True
        assert result.signals == []
        assert result.portfolio_action == "观望"
        assert "持仓为空" in result.portfolio_reason


# ── Test 2: Stop-loss triggered (conservative: 7%) ──────────────────────────

class TestStopLoss:
    def test_conservative_stop_loss(self):
        pos = _pos(cost=100, price=92)  # -8%
        result = evaluate_portfolio([pos], _ctx(), risk_pref="conservative")
        sig = result.signals[0]
        assert sig.action == "sell"
        assert sig.strength == 5
        assert any("止损" in r for r in sig.reasons)

    def test_balanced_not_triggered(self):
        """8% loss doesn't trigger balanced (10% threshold)."""
        pos = _pos(cost=100, price=92)
        result = evaluate_portfolio([pos], _ctx(), risk_pref="balanced")
        sig = result.signals[0]
        assert sig.action != "sell" or sig.strength < 5

    def test_aggressive_not_triggered(self):
        """8% loss doesn't trigger aggressive (15% threshold)."""
        pos = _pos(cost=100, price=92)
        result = evaluate_portfolio([pos], _ctx(), risk_pref="aggressive")
        sig = result.signals[0]
        assert sig.action != "sell" or sig.strength < 5


# ── Test 4: Take-profit triggered ────────────────────────────────────────────

class TestTakeProfit:
    def test_balanced_take_profit(self):
        pos = _pos(cost=100, price=126)  # +26%
        result = evaluate_portfolio([pos], _ctx(), risk_pref="balanced")
        sig = result.signals[0]
        assert sig.action == "reduce"
        assert sig.strength >= 3
        assert any("止盈" in r for r in sig.reasons)

    def test_conservative_take_profit(self):
        pos = _pos(cost=100, price=116)  # +16% > 15%
        result = evaluate_portfolio([pos], _ctx(), risk_pref="conservative")
        sig = result.signals[0]
        assert sig.action == "reduce"


# ── Test 5: Near 52-week high ────────────────────────────────────────────────

class TestNear52High:
    def test_near_high(self):
        pos = _pos(cost=80, price=98, high52=100.0)  # 98 >= 100*0.97
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        assert any("52周高" in r for r in sig.reasons)

    def test_not_near_high(self):
        pos = _pos(cost=80, price=90, high52=100.0)  # 90 < 97
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        assert not any("52周高" in r for r in sig.reasons)


# ── Test 6 & 7: Near 52-week low ─────────────────────────────────────────────

class TestNear52Low:
    def test_near_low_non_weak(self):
        pos = _pos(cost=80, price=51, low52=50.0)  # 51 <= 50*1.03=51.5
        result = evaluate_portfolio([pos], _ctx(regime="震荡"))
        sig = result.signals[0]
        assert any("52周低" in r and "非弱势" in r for r in sig.reasons)

    def test_near_low_weak_regime(self):
        """Near 52w low but regime is weak → don't buy the dip."""
        pos = _pos(cost=80, price=51, low52=50.0)
        result = evaluate_portfolio([pos], _ctx(regime="偏弱"))
        sig = result.signals[0]
        assert sig.action != "add"
        assert any("偏弱" in r for r in sig.reasons)


# ── Test 8: Black swan ──────────────────────────────────────────────────────

class TestBlackSwan:
    def test_black_swan_signal(self):
        events = [{"type": "黑天鹅", "severity": "high", "title": "暴跌"}]
        pos = _pos(cost=100, price=100)
        result = evaluate_portfolio([pos], _ctx(risk_events=events))
        sig = result.signals[0]
        assert sig.action == "sell"
        assert sig.strength >= 4
        assert any("黑天鹅" in r for r in sig.reasons)

    def test_black_swan_portfolio(self):
        events = [{"type": "黑天鹅", "severity": "high", "title": "暴跌"}]
        pos = _pos()
        result = evaluate_portfolio([pos], _ctx(risk_events=events))
        assert result.portfolio_action == "清仓避险"

    def test_grey_rhino_no_sell(self):
        """Grey rhino (severity=medium) does NOT trigger black-swan rule."""
        events = [{"type": "灰犀牛", "severity": "medium", "title": "波动"}]
        pos = _pos(cost=100, price=100)
        result = evaluate_portfolio([pos], _ctx(risk_events=events))
        sig = result.signals[0]
        assert sig.action != "sell"


# ── Test 9: Ebb tide (退潮) ──────────────────────────────────────────────────

class TestEbbTide:
    def test_ebb_tide_hold(self):
        pos = _pos(cost=100, price=100)
        ctx = _ctx(sentiment_stage="退潮", tradable=False)
        result = evaluate_portfolio([pos], ctx)
        sig = result.signals[0]
        assert any("退潮" in r for r in sig.reasons)
        assert sig.action == "hold"
        assert sig.strength >= 3


# ── Test 10: Multi-rule conflict ─────────────────────────────────────────────

class TestMultiRule:
    def test_stop_loss_plus_black_swan(self):
        """Stop-loss (str=5) beats black swan (str=4), but both reasons appear."""
        events = [{"type": "黑天鹅", "severity": "high", "title": "暴跌"}]
        pos = _pos(cost=100, price=85)  # -15% triggers stop-loss
        result = evaluate_portfolio([pos], _ctx(risk_events=events), risk_pref="balanced")
        sig = result.signals[0]
        assert sig.action == "sell"
        assert sig.strength == 5
        assert any("止损" in r for r in sig.reasons)
        assert any("黑天鹅" in r for r in sig.reasons)


# ── Test 11: price=0 (data missing) ─────────────────────────────────────────

class TestDataMissing:
    def test_price_zero(self):
        pos = _pos(cost=100, price=0)
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        assert sig.action == "hold"
        assert "数据缺失" in sig.reasons

    def test_all_data_bad(self):
        positions = [_pos(price=0), _pos(ticker="000001.SZ", price=0)]
        result = evaluate_portfolio(positions, _ctx())
        assert result.ok is False
        assert "不可用" in result.msg


# ── Test 12: cost=0 (no cost basis) ─────────────────────────────────────────

class TestNoCost:
    def test_cost_zero_skips_pnl(self):
        pos = _pos(cost=0, price=100, high52=200.0)
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        # Should not have stop-loss/take-profit reasons
        assert not any("止损" in r for r in sig.reasons)
        assert not any("止盈" in r for r in sig.reasons)
        # Should still evaluate 52w rules
        assert sig.stop_loss is None
        assert sig.take_profit is None


# ── Test 13: Custom strategy injection ───────────────────────────────────────

class TestCustomStrategy:
    def test_inject_mock_strategy(self):
        class MockStrategy:
            name = "mock_v1"

            def evaluate(self, pos, ctx, risk_pref):
                return Signal(
                    ticker=pos.ticker, name=pos.name,
                    action="buy", strength=4, reasons=["mock信号"],
                )

        pos = _pos()
        result = evaluate_portfolio([pos], _ctx(), strategy=MockStrategy())
        assert result.strategy_name == "mock_v1"
        assert result.signals[0].action == "buy"
        assert "mock信号" in result.signals[0].reasons

    def test_strategy_exception_caught(self):
        class BrokenStrategy:
            name = "broken"

            def evaluate(self, pos, ctx, risk_pref):
                raise RuntimeError("boom")

        pos = _pos()
        result = evaluate_portfolio([pos], _ctx(), strategy=BrokenStrategy())
        assert result.ok is True
        sig = result.signals[0]
        assert sig.action == "hold"
        assert "策略异常" in sig.reasons


# ── Test 14: Rising market + high confidence → "加仓" ────────────────────────

class TestPortfolioAdd:
    def test_rising_high_confidence(self):
        pos = _pos(cost=100, price=105)  # mild gain, no sell signal
        ctx = _ctx(sentiment_stage="上升", confidence=80, tradable=True)
        result = evaluate_portfolio([pos], ctx)
        assert result.portfolio_action == "加仓"

    def test_rising_low_confidence(self):
        """Rising but low confidence → observe."""
        pos = _pos(cost=100, price=105)
        ctx = _ctx(sentiment_stage="上升", confidence=50, tradable=True)
        result = evaluate_portfolio([pos], ctx)
        assert result.portfolio_action == "观望"


# ── Test 15: Portfolio "减仓" when ≥50% positions are sell ───────────────────

class TestPortfolioReduce:
    def test_majority_sell(self):
        positions = [
            _pos(ticker="A", cost=100, price=85),  # stop-loss → sell
            _pos(ticker="B", cost=100, price=84),  # stop-loss → sell
            _pos(ticker="C", cost=100, price=105), # fine → hold
        ]
        result = evaluate_portfolio(positions, _ctx(), risk_pref="balanced")
        assert result.portfolio_action == "减仓"


# ── Test 16: Invalid risk_pref defaults to balanced ─────────────────────────

class TestInvalidRiskPref:
    def test_defaults_to_balanced(self):
        pos = _pos(cost=100, price=89)  # -11%, triggers balanced (10%) but not conservative (7%)
        result = evaluate_portfolio([pos], _ctx(), risk_pref="yolo")
        sig = result.signals[0]
        assert sig.action == "sell"
        assert sig.strength == 5


# ── Test 17: Stop-loss / take-profit price suggestions ──────────────────────

class TestPriceSuggestions:
    def test_stop_loss_price(self):
        pos = _pos(cost=100, price=105)
        result = evaluate_portfolio([pos], _ctx(), risk_pref="balanced")
        sig = result.signals[0]
        assert sig.stop_loss == 90.0   # 100 * (1 - 0.10)
        assert sig.take_profit == 125.0  # 100 * (1 + 0.25)


# ── Test 18: Factor scores present in signal ────────────────────────────────

class TestFactors:
    def test_factors_returned(self):
        """Every signal should have 5 factors."""
        pos = _pos(cost=100, price=105, high52=120, low52=80)
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        assert len(sig.factors) == 5
        names = {f["name"] for f in sig.factors}
        assert names == {"盈亏", "价位", "风险", "情绪", "趋势"}

    def test_factor_scores_range(self):
        """All factor scores should be in [-2, +2]."""
        pos = _pos(cost=100, price=92, high52=120, low52=80)
        events = [{"severity": "high", "title": "暴跌"}]
        ctx = _ctx(sentiment_stage="退潮", tradable=False, risk_events=events)
        result = evaluate_portfolio([pos], ctx, risk_pref="conservative")
        sig = result.signals[0]
        for f in sig.factors:
            assert -2 <= f["score"] <= 2, f"{f['name']} score out of range: {f['score']}"
            assert 0 < f["weight"] <= 1.0

    def test_stop_loss_factor_neg2(self):
        """Stop-loss trigger → 盈亏 factor = -2."""
        pos = _pos(cost=100, price=85)  # -15%
        result = evaluate_portfolio([pos], _ctx(), risk_pref="balanced")
        sig = result.signals[0]
        pnl_f = next(f for f in sig.factors if f["name"] == "盈亏")
        assert pnl_f["score"] == -2

    def test_take_profit_factor_pos2(self):
        """Take-profit trigger → 盈亏 factor = +2."""
        pos = _pos(cost=100, price=130)  # +30%
        result = evaluate_portfolio([pos], _ctx(), risk_pref="balanced")
        sig = result.signals[0]
        pnl_f = next(f for f in sig.factors if f["name"] == "盈亏")
        assert pnl_f["score"] == 2

    def test_black_swan_risk_factor(self):
        """Black swan → 风险 factor = -2."""
        events = [{"severity": "high", "title": "暴跌"}]
        pos = _pos(cost=100, price=100)
        result = evaluate_portfolio([pos], _ctx(risk_events=events))
        sig = result.signals[0]
        risk_f = next(f for f in sig.factors if f["name"] == "风险")
        assert risk_f["score"] == -2

    def test_grey_rhino_risk_factor(self):
        """Grey rhino → 风险 factor = -1."""
        events = [{"severity": "medium", "title": "波动"}]
        pos = _pos(cost=100, price=100)
        result = evaluate_portfolio([pos], _ctx(risk_events=events))
        sig = result.signals[0]
        risk_f = next(f for f in sig.factors if f["name"] == "风险")
        assert risk_f["score"] == -1

    def test_rising_sentiment_factor(self):
        """上升 sentiment → 情绪 factor = +2."""
        pos = _pos(cost=100, price=105)
        result = evaluate_portfolio([pos], _ctx(sentiment_stage="上升"))
        sig = result.signals[0]
        sent_f = next(f for f in sig.factors if f["name"] == "情绪")
        assert sent_f["score"] == 2

    def test_ebb_sentiment_factor(self):
        """退潮 + not tradable → 情绪 factor = -2."""
        pos = _pos(cost=100, price=105)
        result = evaluate_portfolio([pos], _ctx(sentiment_stage="退潮", tradable=False))
        sig = result.signals[0]
        sent_f = next(f for f in sig.factors if f["name"] == "情绪")
        assert sent_f["score"] == -2

    def test_strong_regime_factor(self):
        """偏强 regime → 趋势 factor = +1."""
        pos = _pos(cost=100, price=105)
        result = evaluate_portfolio([pos], _ctx(regime="偏强"))
        sig = result.signals[0]
        regime_f = next(f for f in sig.factors if f["name"] == "趋势")
        assert regime_f["score"] == 1

    def test_data_missing_no_factors(self):
        """price=0 → no factors."""
        pos = _pos(cost=100, price=0)
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        assert sig.factors == []

    def test_factor_weights_sum(self):
        """Factor weights should sum to 1.0."""
        pos = _pos(cost=100, price=105, high52=120, low52=80)
        result = evaluate_portfolio([pos], _ctx())
        sig = result.signals[0]
        total = sum(f["weight"] for f in sig.factors)
        assert abs(total - 1.0) < 0.01
