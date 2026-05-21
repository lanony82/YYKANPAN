"""
Decision quality tests — 决策质量测试

NOT unit tests.  These are scenario-based and property-based tests that verify
the advisor's *decision logic* produces sensible outputs under realistic conditions.

Two categories:
  1. Scenario tests:  Given a known market event, does the advisor produce the
     correct directional signal?
  2. Property tests:  For randomly-generated portfolios, do all outputs pass
     logical consistency invariants?
"""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from analysis.advisor import (
    AdvisorOutput,
    MarketContext,
    PositionInput,
    RuleBasedStrategy,
    Signal,
    VALID_RISK_PREFS,
    evaluate_portfolio,
)

# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _pos(ticker="600519", name="贵州茅台", shares=100, cost=1800.0,
         price=1800.0, change_pct=0.0, high52=2100.0, low52=1300.0,
         volume=50000) -> PositionInput:
    return PositionInput(
        ticker=ticker, name=name, shares=shares, cost=cost,
        price=price, change_pct=change_pct,
        high52=high52, low52=low52, volume=volume,
    )


def _ctx(regime="震荡", sentiment_stage="上升", sentiment_score=2,
         tradable=True, confidence=60.0, risk_events=None) -> MarketContext:
    return MarketContext(
        regime=regime, sentiment_stage=sentiment_stage,
        sentiment_score=sentiment_score, tradable=tradable,
        confidence=confidence, risk_events=risk_events or [],
    )


VALID_ACTIONS = {"buy", "sell", "hold", "reduce", "add"}
BEARISH_ACTIONS = {"sell", "reduce"}
BULLISH_ACTIONS = {"buy", "add"}


# ══════════════════════════════════════════════════════════════════════════════
# 1. Scenario tests — 黑天鹅 / 极端行情场景
# ══════════════════════════════════════════════════════════════════════════════

class TestBlackSwanScenarios:
    """Given known crisis scenarios, advisor must produce defensive signals."""

    def test_black_swan_triggers_sell(self):
        """黑天鹅事件 → 个股 sell/reduce + 组合 清仓避险。"""
        pos = _pos(price=1750, cost=1800)
        ctx = _ctx(
            regime="偏弱",
            sentiment_stage="退潮",
            risk_events=[{"severity": "high", "type": "黑天鹅",
                          "detail": "突发系统性风险"}],
        )
        out = evaluate_portfolio([pos], ctx, "balanced")
        assert out.ok
        # Portfolio-level: must recommend full exit
        assert out.portfolio_action == "清仓避险"
        # Signal-level: every position must be sell
        for sig in out.signals:
            assert sig.action in BEARISH_ACTIONS
            assert sig.strength >= 4

    def test_black_swan_overrides_profit(self):
        """即使持仓盈利，黑天鹅也应触发卖出。"""
        pos = _pos(price=2200, cost=1800)  # 22% 盈利
        ctx = _ctx(
            regime="偏弱",
            risk_events=[{"severity": "high", "type": "黑天鹅",
                          "detail": "全球金融危机"}],
        )
        out = evaluate_portfolio([pos], ctx, "aggressive")
        assert out.portfolio_action == "清仓避险"
        assert out.signals[0].action in BEARISH_ACTIONS

    def test_market_crash_with_stop_loss(self):
        """持仓已跌破止损线 → sell，strength 5。"""
        for pref in VALID_RISK_PREFS:
            # conservative: 7%, balanced: 10%, aggressive: 15%
            loss_map = {"conservative": 0.08, "balanced": 0.12, "aggressive": 0.18}
            loss = loss_map[pref]
            pos = _pos(cost=100, price=100 * (1 - loss))
            ctx = _ctx(regime="偏弱", sentiment_stage="退潮")
            out = evaluate_portfolio([pos], ctx, pref)
            sig = out.signals[0]
            assert sig.action == "sell", (
                f"risk_pref={pref}, loss={loss*100:.0f}% should trigger sell"
            )
            assert sig.strength == 5

    def test_sentiment_ebb_blocks_buy(self):
        """退潮期且不可交易 → 不应给出 buy/add。"""
        pos = _pos(price=1300, cost=1800, low52=1290)  # near 52w low
        ctx = _ctx(
            regime="震荡",
            sentiment_stage="退潮",
            tradable=False,
            sentiment_score=-3,
        )
        out = evaluate_portfolio([pos], ctx, "balanced")
        for sig in out.signals:
            assert sig.action not in BULLISH_ACTIONS, \
                "退潮期 + 不可交易时不应建议 buy/add"

    def test_grey_rhino_lowers_risk_factor(self):
        """灰犀牛事件 → 风险因子 score 应为 -1。"""
        pos = _pos(price=1800, cost=1800)
        ctx = _ctx(risk_events=[{"severity": "medium", "type": "灰犀牛"}])
        out = evaluate_portfolio([pos], ctx, "balanced")
        sig = out.signals[0]
        risk_factors = [f for f in sig.factors if f["name"] == "风险"]
        assert risk_factors
        assert risk_factors[0]["score"] == -1

    def test_multi_position_crash(self):
        """多只持仓同时大跌 → 组合动作应为 减仓 或 清仓避险。"""
        positions = [
            _pos("600519", "茅台", cost=1800, price=1500),
            _pos("000858", "五粮液", cost=200, price=165),
            _pos("000333", "美的", cost=80, price=68),
        ]
        ctx = _ctx(regime="偏弱", sentiment_stage="退潮")
        out = evaluate_portfolio(positions, ctx, "balanced")
        # All three exceed 10% stop loss → all sell → portfolio 减仓 or 清仓
        assert out.portfolio_action in ("减仓", "清仓避险")
        sell_signals = [s for s in out.signals if s.action == "sell"]
        assert len(sell_signals) >= 2

    def test_strong_bull_allows_add(self):
        """上升期 + 高信心 + 无卖出信号 → 允许加仓建议。"""
        pos = _pos(price=1850, cost=1800)  # slight profit
        ctx = _ctx(
            regime="偏强",
            sentiment_stage="上升",
            confidence=80,
            tradable=True,
        )
        out = evaluate_portfolio([pos], ctx, "aggressive")
        assert out.portfolio_action == "加仓"


# ══════════════════════════════════════════════════════════════════════════════
# 2. Property tests — 逻辑一致性校验 (100 random portfolios)
# ══════════════════════════════════════════════════════════════════════════════

# Deterministic seed for reproducibility in CI
_RNG = random.Random(42)

_SAMPLE_STOCKS = [
    ("600519", "贵州茅台"), ("000858", "五粮液"), ("601318", "中国平安"),
    ("000333", "美的集团"), ("002714", "牧原股份"), ("600036", "招商银行"),
    ("601012", "隆基绿能"), ("000001", "平安银行"), ("002475", "立讯精密"),
    ("600900", "长江电力"), ("601398", "工商银行"), ("002594", "比亚迪"),
    ("300750", "宁德时代"), ("603259", "药明康德"), ("601888", "中国中免"),
    ("000568", "泸州老窖"), ("002304", "洋河股份"), ("600887", "伊利股份"),
    ("000661", "长春高新"), ("002352", "顺丰控股"),
]

_REGIMES = ["偏强", "偏弱", "震荡"]
_SENTIMENTS = ["上升", "高潮", "退潮", "分歧"]


def _random_portfolio(n_positions: int) -> tuple[list[PositionInput], MarketContext, str]:
    """Generate a random but realistic portfolio + context."""
    positions = []
    chosen = _RNG.sample(_SAMPLE_STOCKS, min(n_positions, len(_SAMPLE_STOCKS)))
    for ticker, name in chosen:
        cost = round(_RNG.uniform(10, 2000), 2)
        # Price can deviate -40% to +60% from cost
        price = round(cost * _RNG.uniform(0.6, 1.6), 2)
        high52 = round(max(price, cost) * _RNG.uniform(1.0, 1.3), 2)
        low52 = round(min(price, cost) * _RNG.uniform(0.7, 1.0), 2)
        positions.append(PositionInput(
            ticker=ticker, name=name,
            shares=_RNG.randint(100, 10000),
            cost=cost, price=price,
            change_pct=round(_RNG.uniform(-10, 10), 2),
            high52=high52, low52=low52,
            volume=_RNG.randint(10000, 5000000),
        ))

    regime = _RNG.choice(_REGIMES)
    stage = _RNG.choice(_SENTIMENTS)
    tradable = stage != "退潮" or _RNG.random() > 0.5
    confidence = round(_RNG.uniform(10, 95), 1)
    # 30% chance of a risk event
    events = []
    if _RNG.random() < 0.3:
        events.append({"severity": _RNG.choice(["high", "medium", "low"]),
                        "type": "测试事件"})
    ctx = MarketContext(
        regime=regime, sentiment_stage=stage,
        sentiment_score=_RNG.randint(-4, 4),
        tradable=tradable, confidence=confidence,
        risk_events=events,
    )
    risk_pref = _RNG.choice(list(VALID_RISK_PREFS))
    return positions, ctx, risk_pref


class TestLogicalConsistency:
    """Property-based tests: run advisor on 100 random portfolios,
    check invariants on every output."""

    @pytest.fixture(scope="class")
    def random_outputs(self) -> list[tuple[AdvisorOutput, MarketContext, str]]:
        """Pre-generate 100 portfolio evaluations."""
        results = []
        for _ in range(100):
            n = _RNG.randint(1, 8)
            positions, ctx, pref = _random_portfolio(n)
            out = evaluate_portfolio(positions, ctx, pref)
            results.append((out, ctx, pref))
        return results

    # ── Invariant 1: no crashes ──

    def test_all_100_succeed(self, random_outputs):
        """Advisor must not crash on any random portfolio."""
        for out, _, _ in random_outputs:
            assert out.ok

    # ── Invariant 2: valid action values ──

    def test_signal_actions_valid(self, random_outputs):
        """Every signal.action must be in {buy, sell, hold, reduce, add}."""
        for out, _, _ in random_outputs:
            for sig in out.signals:
                assert sig.action in VALID_ACTIONS, \
                    f"Invalid action '{sig.action}' for {sig.ticker}"

    # ── Invariant 3: strength range ──

    def test_signal_strength_range(self, random_outputs):
        """Signal strength must be 1~5."""
        for out, _, _ in random_outputs:
            for sig in out.signals:
                assert 1 <= sig.strength <= 5, \
                    f"strength={sig.strength} out of range for {sig.ticker}"

    # ── Invariant 4: factors completeness ──

    def test_factors_present(self, random_outputs):
        """Each signal must have 5 factors with required keys."""
        required_keys = {"name", "score", "weight", "detail"}
        expected_names = {"盈亏", "价位", "风险", "情绪", "趋势"}
        for out, _, _ in random_outputs:
            for sig in out.signals:
                if sig.reasons == ["数据缺失"] or sig.reasons == ["策略异常"]:
                    continue
                assert len(sig.factors) == 5, \
                    f"{sig.ticker} has {len(sig.factors)} factors, expected 5"
                for f in sig.factors:
                    assert required_keys <= set(f.keys()), \
                        f"factor missing keys: {required_keys - set(f.keys())}"
                names = {f["name"] for f in sig.factors}
                assert names == expected_names, \
                    f"factor names mismatch: {names}"

    # ── Invariant 5: factor scores in range ──

    def test_factor_scores_range(self, random_outputs):
        """Factor scores must be in [-2, +2]."""
        for out, _, _ in random_outputs:
            for sig in out.signals:
                for f in sig.factors:
                    assert -2 <= f["score"] <= 2, \
                        f"factor '{f['name']}' score={f['score']} out of [-2,2]"

    # ── Invariant 6: factor weights sum to ~1.0 ──

    def test_factor_weights_sum(self, random_outputs):
        """Factor weights should sum to 1.0 (±0.01)."""
        for out, _, _ in random_outputs:
            for sig in out.signals:
                if not sig.factors:
                    continue
                total = sum(f["weight"] for f in sig.factors)
                assert abs(total - 1.0) < 0.01, \
                    f"{sig.ticker} factor weights sum to {total}"

    # ── Invariant 7: stop-loss < cost < take-profit ──

    def test_stop_loss_take_profit_bounds(self, random_outputs):
        """stop_loss < cost < take_profit when cost > 0."""
        for out, _, _ in random_outputs:
            for sig in out.signals:
                if sig.stop_loss is None or sig.take_profit is None:
                    continue
                # Find the matching position cost from factors
                pnl = [f for f in sig.factors if f["name"] == "盈亏"]
                if not pnl:
                    continue
                assert sig.stop_loss < sig.take_profit, \
                    f"{sig.ticker}: SL={sig.stop_loss} >= TP={sig.take_profit}"

    # ── Invariant 8: portfolio action consistency ──

    VALID_PORTFOLIO_ACTIONS = {"加仓", "减仓", "观望", "清仓避险"}

    def test_portfolio_action_valid(self, random_outputs):
        """Portfolio action must be one of the defined set."""
        for out, _, _ in random_outputs:
            assert out.portfolio_action in self.VALID_PORTFOLIO_ACTIONS, \
                f"Invalid portfolio_action: {out.portfolio_action}"

    # ── Invariant 9: black swan → must not say 加仓 ──

    def test_black_swan_never_suggests_add(self, random_outputs):
        """If black swan present, portfolio_action must not be 加仓."""
        for out, ctx, _ in random_outputs:
            has_bs = any(e.get("severity") == "high" for e in ctx.risk_events)
            if has_bs:
                assert out.portfolio_action != "加仓", \
                    "Portfolio says 加仓 despite black swan"

    # ── Invariant 10: sell signals should have reasons ──

    def test_sell_has_reasons(self, random_outputs):
        """Every sell/reduce signal must have at least one reason."""
        for out, _, _ in random_outputs:
            for sig in out.signals:
                if sig.action in BEARISH_ACTIONS:
                    assert sig.reasons, \
                        f"{sig.ticker} action={sig.action} but no reasons"

    # ── Invariant 11: stop-loss triggered → must sell ──

    def test_stop_loss_triggered_implies_sell(self):
        """If loss exceeds stop-loss threshold, action MUST be sell."""
        for pref in VALID_RISK_PREFS:
            thresholds = {"conservative": 0.07, "balanced": 0.10, "aggressive": 0.15}
            th = thresholds[pref]
            for loss_pct in [th + 0.01, th + 0.05, th + 0.10]:
                price = round(100 * (1 - loss_pct), 2)
                pos = _pos(cost=100, price=price)
                ctx = _ctx()
                out = evaluate_portfolio([pos], ctx, pref)
                sig = out.signals[0]
                assert sig.action == "sell", (
                    f"pref={pref}, loss={loss_pct*100:.0f}%: "
                    f"expected sell, got {sig.action}"
                )

    # ── Invariant 12: signal count == position count ──

    def test_signal_count_matches_positions(self, random_outputs):
        """Number of signals must equal number of input positions."""
        for _ in range(50):
            n = _RNG.randint(1, 10)
            positions, ctx, pref = _random_portfolio(n)
            out = evaluate_portfolio(positions, ctx, pref)
            assert len(out.signals) == len(positions), \
                f"Expected {len(positions)} signals, got {len(out.signals)}"

    # ── Invariant 13: empty portfolio → 观望 ──

    def test_empty_portfolio(self):
        """Empty portfolio must return 观望."""
        ctx = _ctx()
        out = evaluate_portfolio([], ctx, "balanced")
        assert out.ok
        assert out.portfolio_action == "观望"
        assert out.signals == []

    # ── Invariant 14: risk_pref escalation ──

    def test_conservative_more_defensive(self):
        """Conservative should be at least as defensive as aggressive
        for the same portfolio."""
        for _ in range(30):
            positions, ctx, _ = _random_portfolio(_RNG.randint(1, 5))
            out_c = evaluate_portfolio(positions, ctx, "conservative")
            out_a = evaluate_portfolio(positions, ctx, "aggressive")
            # Count sell+reduce signals
            sells_c = sum(1 for s in out_c.signals if s.action in BEARISH_ACTIONS)
            sells_a = sum(1 for s in out_a.signals if s.action in BEARISH_ACTIONS)
            # Conservative should trigger sell at least as often
            assert sells_c >= sells_a, (
                f"Conservative ({sells_c} sells) less defensive "
                f"than aggressive ({sells_a} sells)"
            )
