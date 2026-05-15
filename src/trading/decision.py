"""
decision.py — Decision Journal: record, track, and review decisions.

Core entity for the YYKANPAN decision-tracking system.
Everything is a Decision: capture → structure → analyze → improve.

Decisions can be trade / life / work type, tracked through kanban states.
Trade decisions carry structured fields (symbol, price, size, confidence, etc.)
that enable post-trade evaluation and pattern mining.
"""

import json
import uuid
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from config import cfg, BASE
from time_utils import BeijingTime

_DECISIONS_FILE = BASE / "data" / "decisions.json"

VALID_TYPES = ("trade", "life", "work")
VALID_STATES = ("idea", "decided", "acted", "reviewed")
VALID_ACTIONS = ("BUY", "SELL", "HOLD")
VALID_SOURCES = ("manual", "rule", "ai")
MAX_DECISIONS = 1000

# ── Trading-specific fields (optional, for type=trade) ───────────────────────
TRADE_FIELDS = {
    "symbol",        # 标的名称
    "price",         # 触发/成交价格
    "size",          # 股数
    "confidence",    # 0~1
    "stop_loss",     # 止损价
    "take_profit",   # 止盈价
    "max_drawdown",  # 最大回撤容忍 (0~1)
    "source",        # manual / rule / ai
    "trade_context", # structured dict (市场环境)
}


def _load_all() -> list[dict]:
    try:
        if _DECISIONS_FILE.exists():
            data = json.loads(_DECISIONS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def _save_all(decisions: list[dict]) -> None:
    try:
        _DECISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _DECISIONS_FILE.write_text(
            json.dumps(decisions[-MAX_DECISIONS:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def list_decisions(dtype: Optional[str] = None, state: Optional[str] = None) -> list[dict]:
    """Return decisions, optionally filtered by type and/or state."""
    decisions = _load_all()
    if dtype:
        decisions = [d for d in decisions if d.get("type") == dtype]
    if state:
        decisions = [d for d in decisions if d.get("state") == state]
    return decisions


def get_decision(decision_id: str) -> Optional[dict]:
    for d in _load_all():
        if d.get("id") == decision_id:
            return d
    return None


def create_decision(
    title: str,
    dtype: str = "trade",
    context: str = "",
    action: str = "",
    outcome: str = "",
    tags: Optional[list[str]] = None,
    state: str = "idea",
    *,
    # ── Trading fields (for dtype="trade") ──
    symbol: str = "",
    price: float = 0.0,
    size: int = 0,
    confidence: float = 0.0,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    max_drawdown: Optional[float] = None,
    source: str = "manual",
    trade_context: Optional[dict] = None,
) -> dict:
    """Create a new decision and persist it."""
    if dtype not in VALID_TYPES:
        raise ValueError(f"type must be one of {VALID_TYPES}")
    if state not in VALID_STATES:
        raise ValueError(f"state must be one of {VALID_STATES}")

    now = BeijingTime.datetime_str()
    decision = {
        "id": uuid.uuid4().hex[:12],
        "title": title.strip(),
        "type": dtype,
        "context": context.strip() if isinstance(context, str) else context,
        "action": action.strip() if isinstance(action, str) else action,
        "outcome": outcome.strip() if isinstance(outcome, str) else outcome,
        "tags": [t.strip() for t in (tags or []) if t.strip()],
        "state": state,
        "created_at": now,
        "updated_at": now,
    }
    # Attach trading fields for trade decisions
    if dtype == "trade":
        if symbol:
            decision["symbol"] = symbol.strip() if isinstance(symbol, str) else symbol
        if price:
            decision["price"] = float(price)
        if size:
            decision["size"] = int(size)
        if confidence:
            decision["confidence"] = max(0.0, min(1.0, float(confidence)))
        if stop_loss is not None:
            decision["stop_loss"] = float(stop_loss)
        if take_profit is not None:
            decision["take_profit"] = float(take_profit)
        if max_drawdown is not None:
            decision["max_drawdown"] = max(0.0, min(1.0, float(max_drawdown)))
        if source and source in VALID_SOURCES:
            decision["source"] = source
        if trade_context and isinstance(trade_context, dict):
            decision["trade_context"] = trade_context

    decisions = _load_all()
    decisions.append(decision)
    _save_all(decisions)
    return decision


def update_decision(decision_id: str, updates: dict) -> Optional[dict]:
    """Update fields of an existing decision. Returns updated dict or None."""
    decisions = _load_all()
    for d in decisions:
        if d.get("id") == decision_id:
            if "type" in updates and updates["type"] not in VALID_TYPES:
                raise ValueError(f"type must be one of {VALID_TYPES}")
            if "state" in updates and updates["state"] not in VALID_STATES:
                raise ValueError(f"state must be one of {VALID_STATES}")

            allowed = {"title", "type", "context", "action", "outcome", "tags", "state"}
            allowed |= TRADE_FIELDS
            for k, v in updates.items():
                if k in allowed:
                    if k == "tags" and isinstance(v, list):
                        v = [t.strip() for t in v if isinstance(t, str) and t.strip()]
                    elif isinstance(v, str):
                        v = v.strip()
                    d[k] = v
            d["updated_at"] = BeijingTime.datetime_str()
            _save_all(decisions)
            return d
    return None


def delete_decision(decision_id: str) -> bool:
    """Delete a decision by id. Returns True if found and deleted."""
    decisions = _load_all()
    before = len(decisions)
    decisions = [d for d in decisions if d.get("id") != decision_id]
    if len(decisions) < before:
        _save_all(decisions)
        return True
    return False


# ── Evaluate: post-trade scoring ─────────────────────────────────────────────

def evaluate(decision_id: str, current_price: float) -> dict:
    """Evaluate a trade decision against current price.

    Returns P&L, stop-loss/take-profit hit status, and risk assessment.
    """
    d = get_decision(decision_id)
    if not d:
        return {"ok": False, "error": "decision not found"}
    if d.get("type") != "trade":
        return {"ok": False, "error": "not a trade decision"}

    entry_price = d.get("price", 0)
    size = d.get("size", 0)
    action = d.get("action", "").upper()

    if not entry_price or entry_price <= 0:
        return {"ok": False, "error": "no entry price recorded"}

    # P&L calculation
    if action in ("BUY", "买入", "加仓"):
        pnl = (current_price - entry_price) * size
        pnl_pct = (current_price - entry_price) / entry_price * 100
    elif action in ("SELL", "卖出", "减仓"):
        pnl = (entry_price - current_price) * size
        pnl_pct = (entry_price - current_price) / entry_price * 100
    else:
        pnl = 0.0
        pnl_pct = 0.0

    # Stop-loss / take-profit checks
    sl = d.get("stop_loss")
    tp = d.get("take_profit")
    hit_stop = bool(sl and current_price <= sl)
    hit_tp = bool(tp and current_price >= tp)

    # Risk assessment
    risk_ok = not hit_stop
    verdict_parts = []
    if pnl > 0:
        verdict_parts.append("盈利")
    elif pnl < 0:
        verdict_parts.append("亏损")
    else:
        verdict_parts.append("持平")

    if hit_stop:
        verdict_parts.append("已触发止损")
    if hit_tp:
        verdict_parts.append("已触发止盈")

    # Confidence assessment
    conf = d.get("confidence", 0)
    if conf and pnl < 0 and conf >= 0.7:
        verdict_parts.append("高信心决策亏损，需复盘")
    if conf and pnl > 0 and conf < 0.3:
        verdict_parts.append("低信心决策盈利，可能运气")

    # Max drawdown check
    max_dd = d.get("max_drawdown")
    if max_dd and entry_price > 0:
        dd = (entry_price - current_price) / entry_price
        if dd > max_dd:
            verdict_parts.append(f"超过最大回撤容忍({max_dd:.0%})")
            risk_ok = False

    return {
        "ok": True,
        "decision_id": decision_id,
        "symbol": d.get("symbol", ""),
        "entry_price": entry_price,
        "current_price": current_price,
        "size": size,
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "hit_stop_loss": hit_stop,
        "hit_take_profit": hit_tp,
        "risk_ok": risk_ok,
        "verdict": "；".join(verdict_parts),
        "confidence": conf,
        "source": d.get("source", "manual"),
    }


# ── Analyze: pattern mining across decisions ──────────────────────────────────

def analyze(dtype: str = "trade") -> dict:
    """Analyze trade decisions for behavioral patterns.

    Returns stats and actionable insights like 'most common loss pattern'.
    """
    all_decs = list_decisions(dtype=dtype)
    trade_decs = [d for d in all_decs if d.get("price") or d.get("symbol")]

    if not all_decs:
        return {"ok": True, "total": 0, "patterns": [], "stats": {}}

    # Basic stats
    by_source = {}
    for d in all_decs:
        src = d.get("source", "manual")
        by_source[src] = by_source.get(src, 0) + 1

    by_state = {}
    for d in all_decs:
        st = d.get("state", "idea")
        by_state[st] = by_state.get(st, 0) + 1

    buys = [d for d in all_decs if d.get("action", "").upper() in ("BUY", "买入", "加仓")]
    sells = [d for d in all_decs if d.get("action", "").upper() in ("SELL", "卖出", "减仓")]
    holds = [d for d in all_decs if d.get("action", "").upper() in ("HOLD", "持有", "观望")]

    # Confidence distribution
    confidences = [d["confidence"] for d in all_decs if d.get("confidence")]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0

    # Patterns (rule-based, expandable to AI)
    patterns = []

    # 1. Low confidence trades
    low_conf = [d for d in trade_decs if d.get("confidence") and d["confidence"] < 0.4]
    if low_conf:
        patterns.append({
            "type": "low_confidence",
            "label": f"有 {len(low_conf)} 笔低信心决策（<40%），建议减少冲动交易",
            "severity": "warn",
            "count": len(low_conf),
        })

    # 2. No stop-loss on buys
    no_sl = [d for d in trade_decs
             if d.get("action", "").upper() in ("BUY", "买入", "加仓")
             and not d.get("stop_loss")]
    if no_sl:
        patterns.append({
            "type": "no_stop_loss",
            "label": f"有 {len(no_sl)} 笔买入没设止损，风控缺失",
            "severity": "danger",
            "count": len(no_sl),
        })

    # 3. Decisions never reviewed
    never_reviewed = [d for d in all_decs if d.get("state") == "acted"]
    if never_reviewed:
        patterns.append({
            "type": "no_review",
            "label": f"有 {len(never_reviewed)} 笔已执行但未复盘，缺少反馈闭环",
            "severity": "info",
            "count": len(never_reviewed),
        })

    # 4. AI decisions vs manual
    ai_count = by_source.get("ai", 0)
    manual_count = by_source.get("manual", 0)
    if ai_count and manual_count:
        ratio = ai_count / (ai_count + manual_count) * 100
        patterns.append({
            "type": "ai_ratio",
            "label": f"AI建议占比 {ratio:.0f}%（{ai_count}/{ai_count + manual_count}）",
            "severity": "info",
            "count": ai_count,
        })

    # 5. Too many decisions in one day
    by_date = {}
    for d in all_decs:
        date = (d.get("created_at") or "")[:10]
        if date:
            by_date[date] = by_date.get(date, 0) + 1
    busy_days = {k: v for k, v in by_date.items() if v >= 5}
    if busy_days:
        patterns.append({
            "type": "overtrading",
            "label": f"有 {len(busy_days)} 天决策超过5笔，警惕过度交易",
            "severity": "warn",
            "count": len(busy_days),
        })

    return {
        "ok": True,
        "total": len(all_decs),
        "with_price": len(trade_decs),
        "buys": len(buys),
        "sells": len(sells),
        "holds": len(holds),
        "avg_confidence": round(avg_conf, 2),
        "by_source": by_source,
        "by_state": by_state,
        "patterns": patterns,
    }
