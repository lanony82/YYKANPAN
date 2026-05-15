"""
autodev.py — Autonomous Development Loop.

Minimal skeleton for automated decision-making cycle:
  observe → decide → act → evaluate → learn

Each step is independently testable and composable.
The loop can run once (run_cycle) or be scheduled externally.
"""

from __future__ import annotations

from dataclasses import asdict

from analysis.advisor import PositionInput, MarketContext, Signal
from trading.decision import create_decision, list_decisions, evaluate, analyze
from trading.strategy_loader import load_strategy, YAMLStrategy
from time_utils import BeijingTime


class AutoDev:
    """Autonomous development loop: observe → decide → act → evaluate → learn."""

    def __init__(self, strategy_name: str = "rule_v1", risk_pref: str = "balanced"):
        self.strategy: YAMLStrategy = load_strategy(strategy_name)
        self.risk_pref = risk_pref
        self._last_cycle: dict | None = None

    # ── Step 1: Observe ──────────────────────────────────────────────────────

    def observe(
        self, positions: list[PositionInput], context: MarketContext
    ) -> dict:
        """Package raw inputs into a structured observation."""
        return {
            "positions": positions,
            "context": context,
            "observed_at": BeijingTime.datetime_str(),
            "strategy": self.strategy.name,
            "risk_pref": self.risk_pref,
        }

    # ── Step 2: Decide ───────────────────────────────────────────────────────

    def decide(self, observation: dict) -> list[Signal]:
        """Run strategy on each position, produce signals."""
        signals = []
        for pos in observation["positions"]:
            sig = self.strategy.evaluate(
                pos, observation["context"], self.risk_pref
            )
            signals.append(sig)
        return signals

    # ── Step 3: Act ──────────────────────────────────────────────────────────

    def act(self, signals: list[Signal], observation: dict) -> list[dict]:
        """Record actionable signals as decisions in the journal."""
        decisions = []
        actionable = ("buy", "sell", "reduce", "add")
        action_map = {"buy": "BUY", "sell": "SELL", "reduce": "SELL", "add": "BUY"}

        for sig in signals:
            if sig.action not in actionable:
                continue

            d = create_decision(
                title=f"[AutoDev] {sig.name} → {sig.action}",
                dtype="trade",
                action=action_map.get(sig.action, "HOLD"),
                symbol=sig.name,
                confidence=sig.strength / 5.0,
                stop_loss=sig.stop_loss,
                take_profit=sig.take_profit,
                source="rule",
                trade_context={
                    "strategy": self.strategy.name,
                    "risk_pref": self.risk_pref,
                    "factors": sig.factors,
                    "reasons": sig.reasons,
                    "observed_at": observation["observed_at"],
                },
                tags=["autodev", self.strategy.name],
            )
            decisions.append(d)
        return decisions

    # ── Step 4: Evaluate ─────────────────────────────────────────────────────

    def evaluate_past(
        self, current_prices: dict[str, float] | None = None
    ) -> list[dict]:
        """Evaluate past AutoDev decisions against current prices."""
        if not current_prices:
            return []
        all_decs = list_decisions(dtype="trade")
        results = []
        for d in all_decs:
            tags = d.get("tags") or []
            if "autodev" not in tags:
                continue
            if d.get("state") != "acted":
                continue
            sym = d.get("symbol", "")
            if sym in current_prices:
                try:
                    r = evaluate(d["id"], current_prices[sym])
                    results.append(r)
                except Exception:
                    pass
        return results

    # ── Step 5: Learn ────────────────────────────────────────────────────────

    def learn(self) -> dict:
        """Analyze decision patterns and suggest strategy adjustments."""
        analysis = analyze(dtype="trade")

        suggestions = []
        for pat in analysis.get("patterns", []):
            ptype = pat.get("type", "")
            if ptype == "no_stop_loss":
                suggestions.append(
                    {
                        "type": "weight_adjust",
                        "factor": "风险",
                        "direction": "increase",
                        "reason": f"{pat.get('count', 0)} 笔决策未设止损",
                    }
                )
            elif ptype == "low_confidence":
                suggestions.append(
                    {
                        "type": "threshold",
                        "param": "min_confidence",
                        "direction": "increase",
                        "reason": f"{pat.get('count', 0)} 笔低信心决策",
                    }
                )
            elif ptype == "overtrading":
                suggestions.append(
                    {
                        "type": "cooldown",
                        "param": "min_interval_hours",
                        "direction": "increase",
                        "reason": pat.get("label", "交易过频"),
                    }
                )

        analysis["suggestions"] = suggestions
        return analysis

    # ── Full Cycle ───────────────────────────────────────────────────────────

    def run_cycle(
        self,
        positions: list[PositionInput],
        context: MarketContext,
        current_prices: dict[str, float] | None = None,
    ) -> dict:
        """Execute one full loop: observe → decide → act → evaluate → learn."""
        obs = self.observe(positions, context)
        signals = self.decide(obs)
        acted = self.act(signals, obs)
        evals = self.evaluate_past(current_prices)
        analysis = self.learn()

        self._last_cycle = {
            "observed_at": obs["observed_at"],
            "strategy": self.strategy.name,
            "version": self.strategy.version,
            "risk_pref": self.risk_pref,
            "signals_count": len(signals),
            "acted_count": len(acted),
            "evaluations_count": len(evals),
            "patterns_count": len(analysis.get("patterns", [])),
            "suggestions_count": len(analysis.get("suggestions", [])),
        }

        return {
            "ok": True,
            "cycle": self._last_cycle,
            "signals": [asdict(s) for s in signals],
            "decisions": acted,
            "evaluations": evals,
            "analysis": analysis,
        }

    @property
    def status(self) -> dict:
        """Return current AutoDev state."""
        return {
            "strategy": self.strategy.name,
            "version": self.strategy.version,
            "risk_pref": self.risk_pref,
            "factor_weights": self.strategy.factor_weights,
            "last_cycle": self._last_cycle,
        }
