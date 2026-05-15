"""
advisor.py — Trading Advisor (参谋模块)

Produces explainable buy/sell/hold signals per position based on:
- Portfolio positions (shares, cost, current price)
- Market context (regime, sentiment, risk events)
- User risk preference

Strategies are pluggable via the Strategy protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from time_utils import BeijingTime


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class PositionInput:
    ticker: str
    name: str
    shares: int
    cost: float           # per-share cost
    price: float          # current price
    change_pct: float
    high52: float | None
    low52: float | None
    volume: int


@dataclass
class MarketContext:
    regime: str               # "偏强" | "偏弱" | "震荡"
    sentiment_stage: str      # "上升" | "退潮" | "分歧"
    sentiment_score: int      # -4 ~ +4
    tradable: bool
    confidence: float         # 10 ~ 95
    risk_events: list[dict] = field(default_factory=list)


@dataclass
class Signal:
    ticker: str
    name: str
    action: str           # "buy" | "sell" | "hold" | "reduce" | "add"
    strength: int          # 1 ~ 5
    reasons: list[str] = field(default_factory=list)
    stop_loss: float | None = None
    take_profit: float | None = None


@dataclass
class AdvisorOutput:
    ok: bool
    generated_at: str
    signals: list[Signal]
    portfolio_action: str     # "加仓" | "减仓" | "观望" | "清仓避险"
    portfolio_reason: str
    strategy_name: str
    msg: str = ""


# ── Risk-preference thresholds ────────────────────────────────────────────────

_THRESHOLDS = {
    "conservative": {"stop_loss": 0.07, "take_profit": 0.15},
    "balanced":     {"stop_loss": 0.10, "take_profit": 0.25},
    "aggressive":   {"stop_loss": 0.15, "take_profit": 0.40},
}

VALID_RISK_PREFS = tuple(_THRESHOLDS.keys())


def _get_thresholds(risk_pref: str) -> dict:
    return _THRESHOLDS.get(risk_pref, _THRESHOLDS["balanced"])


# ── Strategy protocol ─────────────────────────────────────────────────────────

@runtime_checkable
class Strategy(Protocol):
    name: str

    def evaluate(
        self, position: PositionInput, context: MarketContext, risk_pref: str
    ) -> Signal: ...


# ── V1: Rule-based strategy ──────────────────────────────────────────────────

class RuleBasedStrategy:
    name = "rule_v1"

    def evaluate(
        self, pos: PositionInput, ctx: MarketContext, risk_pref: str
    ) -> Signal:
        reasons: list[str] = []
        best_action = "hold"
        best_strength = 1

        # Data missing
        if pos.price <= 0:
            return Signal(
                ticker=pos.ticker, name=pos.name,
                action="hold", strength=1, reasons=["数据缺失"],
            )

        th = _get_thresholds(risk_pref)

        # ── P&L rules (only if cost > 0) ──
        if pos.cost > 0:
            pnl_pct = (pos.price - pos.cost) / pos.cost

            # Stop-loss
            if pnl_pct <= -th["stop_loss"]:
                r = f"浮亏 {pnl_pct*100:.1f}%，触及止损线 {th['stop_loss']*100:.0f}%"
                reasons.append(r)
                best_action, best_strength = "sell", 5

            # Take-profit
            elif pnl_pct >= th["take_profit"]:
                r = f"浮盈 {pnl_pct*100:.1f}%，达到止盈线 {th['take_profit']*100:.0f}%"
                reasons.append(r)
                if best_strength < 3:
                    best_action, best_strength = "reduce", 3

        # ── 52-week rules ──
        if pos.high52 and pos.price >= pos.high52 * 0.97:
            reasons.append(f"接近52周高点 {pos.high52:.2f}")
            if best_strength < 2:
                best_action, best_strength = "reduce", 2

        if pos.low52 and pos.price <= pos.low52 * 1.03:
            if ctx.regime != "偏弱":
                reasons.append(f"接近52周低点 {pos.low52:.2f}，市场非弱势")
                if best_strength < 2:
                    best_action, best_strength = "add", 2
            else:
                reasons.append(f"接近52周低点但市场偏弱，不宜抄底")

        # ── Black-swan rule ──
        has_black_swan = any(
            e.get("severity") == "high" for e in ctx.risk_events
        )
        if has_black_swan:
            reasons.append("检测到黑天鹅事件，建议避险")
            if best_strength < 4:
                best_action, best_strength = "sell", 4

        # ── Sentiment ebb-tide rule ──
        if ctx.sentiment_stage == "退潮" and not ctx.tradable:
            reasons.append("市场退潮期，暂不适合加仓")
            if best_strength < 3 and best_action in ("hold", "add", "buy"):
                best_action, best_strength = "hold", 3

        # ── Stop-loss / take-profit price suggestions ──
        stop_loss = None
        take_profit = None
        if pos.cost > 0:
            stop_loss = round(pos.cost * (1 - th["stop_loss"]), 2)
            take_profit = round(pos.cost * (1 + th["take_profit"]), 2)

        if not reasons:
            reasons.append("无明显信号，建议持有观望")

        return Signal(
            ticker=pos.ticker,
            name=pos.name,
            action=best_action,
            strength=best_strength,
            reasons=reasons,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )


# ── Portfolio-level evaluation ────────────────────────────────────────────────

def evaluate_portfolio(
    positions: list[PositionInput],
    context: MarketContext,
    risk_pref: str = "balanced",
    strategy: Strategy | None = None,
) -> AdvisorOutput:
    """Evaluate all positions and produce portfolio-level advice."""
    if risk_pref not in VALID_RISK_PREFS:
        risk_pref = "balanced"

    strat = strategy or RuleBasedStrategy()
    now_str = BeijingTime.datetime_str()

    if not positions:
        return AdvisorOutput(
            ok=True,
            generated_at=now_str,
            signals=[],
            portfolio_action="观望",
            portfolio_reason="持仓为空，暂无建议",
            strategy_name=strat.name,
        )

    # Evaluate each position
    signals: list[Signal] = []
    for pos in positions:
        try:
            sig = strat.evaluate(pos, context, risk_pref)
            signals.append(sig)
        except Exception:
            signals.append(Signal(
                ticker=pos.ticker, name=pos.name,
                action="hold", strength=1, reasons=["策略异常"],
            ))

    # Check if all data was bad
    all_bad = all(s.reasons == ["数据缺失"] for s in signals)
    if all_bad and signals:
        return AdvisorOutput(
            ok=False,
            generated_at=now_str,
            signals=signals,
            portfolio_action="观望",
            portfolio_reason="行情数据不可用",
            strategy_name=strat.name,
            msg="行情数据不可用",
        )

    # ── Portfolio-level decision ──
    has_black_swan = any(e.get("severity") == "high" for e in context.risk_events)
    sell_count = sum(1 for s in signals if s.action == "sell")
    total = len(signals)

    if has_black_swan:
        action = "清仓避险"
        reason = "检测到黑天鹅事件，建议清仓避险"
    elif total > 0 and sell_count / total >= 0.5:
        action = "减仓"
        reason = f"{sell_count}/{total} 只持仓触发卖出信号"
    elif (
        context.sentiment_stage == "上升"
        and context.confidence > 70
        and sell_count == 0
    ):
        action = "加仓"
        reason = "市场上升期，AI置信度高，可适当加仓"
    else:
        action = "观望"
        reason = "综合信号无明确方向，建议观望"

    return AdvisorOutput(
        ok=True,
        generated_at=now_str,
        signals=signals,
        portfolio_action=action,
        portfolio_reason=reason,
        strategy_name=strat.name,
    )
