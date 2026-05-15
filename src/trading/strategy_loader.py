"""
strategy_loader.py — Load pluggable strategies from YAML config files.

Separates strategy configuration (YAML) from evaluation logic (Python).
  YAML defines: factor names, weights, evaluator types, risk profiles.
  Python provides: factor evaluator functions registered by name.

Usage:
    strategy = load_strategy("rule_v1")          # from data/strategies/
    signal   = strategy.evaluate(pos, ctx, "balanced")
    all_strats = list_strategies()
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from analysis.advisor import PositionInput, MarketContext, Signal
from config import BASE

try:
    import yaml

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

STRATEGIES_DIR = BASE / "data" / "strategies"


# ── Factor evaluator result ──────────────────────────────────────────────────


@dataclass
class FactorResult:
    """Output of a single factor evaluator."""

    score: int  # -2..+2
    detail: str
    action: str = ""  # "" = no action triggered
    strength: int = 0
    reason: str = ""


# ── Factor evaluator functions ────────────────────────────────────────────────


def _eval_pnl(pos: PositionInput, ctx: MarketContext, th: dict) -> FactorResult:
    if pos.cost <= 0:
        return FactorResult(0, "无持仓成本")
    pnl_pct = (pos.price - pos.cost) / pos.cost
    if pnl_pct <= -th["stop_loss"]:
        r = f"浮亏 {pnl_pct*100:.1f}%，触及止损线 {th['stop_loss']*100:.0f}%"
        return FactorResult(-2, r, "sell", 5, r)
    if pnl_pct >= th["take_profit"]:
        r = f"浮盈 {pnl_pct*100:.1f}%，达到止盈线 {th['take_profit']*100:.0f}%"
        return FactorResult(2, r, "reduce", 3, r)
    if pnl_pct > 0:
        return FactorResult(1, f"浮盈 {pnl_pct*100:.1f}%")
    if pnl_pct < 0:
        return FactorResult(-1, f"浮亏 {pnl_pct*100:.1f}%")
    return FactorResult(0, "持平")


def _eval_week52(pos: PositionInput, ctx: MarketContext, th: dict) -> FactorResult:
    if pos.high52 and pos.price >= pos.high52 * 0.97:
        d = f"接近52周高点 {pos.high52:.2f}"
        return FactorResult(-1, d, "reduce", 2, d)
    if pos.low52 and pos.price <= pos.low52 * 1.03:
        if ctx.regime != "偏弱":
            d = f"接近52周低点 {pos.low52:.2f}，市场非弱势"
            return FactorResult(1, d, "add", 2, d)
        return FactorResult(-1, "接近52周低点但市场偏弱")
    if pos.high52 and pos.low52 and pos.high52 > pos.low52:
        pct = (pos.price - pos.low52) / (pos.high52 - pos.low52)
        return FactorResult(0, f"52周区间 {pct*100:.0f}% 位置")
    return FactorResult(0, "无52周数据")


def _eval_risk(pos: PositionInput, ctx: MarketContext, th: dict) -> FactorResult:
    events = ctx.risk_events or []
    has_black = any(e.get("severity") == "high" for e in events)
    has_grey = any(e.get("severity") == "medium" for e in events)
    if has_black:
        return FactorResult(-2, "黑天鹅事件", "sell", 4, "检测到黑天鹅事件，建议避险")
    if has_grey:
        return FactorResult(-1, "灰犀牛事件")
    return FactorResult(0, "无风险事件")


def _eval_sentiment(pos: PositionInput, ctx: MarketContext, th: dict) -> FactorResult:
    stage = ctx.sentiment_stage
    if stage == "退潮" and not ctx.tradable:
        return FactorResult(-2, "退潮期，不适合交易", "hold", 3, "市场退潮期，暂不适合加仓")
    if stage == "上升":
        return FactorResult(2, "上升期，适合交易")
    if stage == "高潮":
        return FactorResult(1, "高潮期，注意见顶信号")
    return FactorResult(0, f"情绪: {stage}")


def _eval_regime(pos: PositionInput, ctx: MarketContext, th: dict) -> FactorResult:
    score = 1 if ctx.regime == "偏强" else (-1 if ctx.regime == "偏弱" else 0)
    detail = f"市场: {ctx.regime}，信心: {ctx.confidence:.0f}%"
    return FactorResult(score, detail)


# ── Evaluator registry ────────────────────────────────────────────────────────

EVALUATORS: dict[str, callable] = {
    "pnl": _eval_pnl,
    "week52": _eval_week52,
    "risk": _eval_risk,
    "sentiment": _eval_sentiment,
    "regime": _eval_regime,
}


# ── YAML Strategy class ──────────────────────────────────────────────────────


class YAMLStrategy:
    """Strategy loaded from a YAML/JSON config file.

    Implements the Strategy protocol — can be used anywhere
    RuleBasedStrategy is used (e.g. evaluate_portfolio).
    """

    def __init__(self, config: dict):
        self.name: str = config["name"]
        self.version: int = config.get("version", 1)
        self.description: str = config.get("description", "")
        self._risk_profiles: dict = config.get("risk_profiles", {})
        self._factors: list[dict] = config.get("factors", [])
        self._portfolio: dict = config.get("portfolio", {})

        # Validate: all evaluators must be registered
        for f in self._factors:
            ev = f.get("evaluator", "")
            if ev not in EVALUATORS:
                raise ValueError(
                    f"Unknown evaluator '{ev}' for factor '{f.get('name')}'"
                )

    def get_thresholds(self, risk_pref: str) -> dict:
        return self._risk_profiles.get(
            risk_pref,
            self._risk_profiles.get(
                "balanced", {"stop_loss": 0.10, "take_profit": 0.25}
            ),
        )

    @property
    def factor_weights(self) -> dict[str, float]:
        """Return {factor_name: weight} for inspection / learning."""
        return {f["name"]: f["weight"] for f in self._factors}

    def evaluate(
        self, pos: PositionInput, ctx: MarketContext, risk_pref: str
    ) -> Signal:
        """Evaluate a single position — returns a Signal (Strategy protocol)."""
        if pos.price <= 0:
            return Signal(
                ticker=pos.ticker,
                name=pos.name,
                action="hold",
                strength=1,
                reasons=["数据缺失"],
            )

        th = self.get_thresholds(risk_pref)
        factors: list[dict] = []
        reasons: list[str] = []
        best_action = "hold"
        best_strength = 1

        for fconf in self._factors:
            evaluator = EVALUATORS[fconf["evaluator"]]
            result = evaluator(pos, ctx, th)

            factors.append(
                {
                    "name": fconf["name"],
                    "score": result.score,
                    "weight": fconf["weight"],
                    "detail": result.detail,
                }
            )

            if result.action and result.strength > best_strength:
                best_action = result.action
                best_strength = result.strength
                if result.reason:
                    reasons.append(result.reason)

        # Stop-loss / take-profit price suggestions
        stop_loss = round(pos.cost * (1 - th["stop_loss"]), 2) if pos.cost > 0 else None
        take_profit = (
            round(pos.cost * (1 + th["take_profit"]), 2) if pos.cost > 0 else None
        )

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
            factors=factors,
        )


# ── Loader ────────────────────────────────────────────────────────────────────


def _load_config(path: Path) -> dict:
    """Load a YAML or JSON config file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        if not _HAS_YAML:
            raise ImportError(
                "PyYAML required for .yaml files. Install: pip install pyyaml"
            )
        return yaml.safe_load(text)
    return json.loads(text)


def load_strategy(name: str) -> YAMLStrategy:
    """Load a strategy by name from data/strategies/."""
    for ext in (".yaml", ".yml", ".json"):
        path = STRATEGIES_DIR / f"{name}{ext}"
        if path.exists():
            config = _load_config(path)
            return YAMLStrategy(config)
    raise FileNotFoundError(f"Strategy '{name}' not found in {STRATEGIES_DIR}")


def list_strategies() -> list[dict]:
    """List all available strategy configs."""
    if not STRATEGIES_DIR.exists():
        return []
    strategies = []
    for path in sorted(STRATEGIES_DIR.iterdir()):
        if path.suffix in (".yaml", ".yml", ".json"):
            try:
                config = _load_config(path)
                strategies.append(
                    {
                        "name": config.get("name", path.stem),
                        "version": config.get("version", 1),
                        "description": config.get("description", ""),
                        "file": path.name,
                        "factors": len(config.get("factors", [])),
                    }
                )
            except Exception:
                pass
    return strategies
