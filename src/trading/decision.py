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
import re
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


def _has_loss_marker(d: dict) -> bool:
    """Best-effort loss detection from decision record fields."""
    for k in ("pnl", "pnl_pct"):
        v = d.get(k)
        if isinstance(v, (int, float)) and v < 0:
            return True

    text_parts = [
        str(d.get("outcome", "")),
        str(d.get("verdict", "")),
        str(d.get("context", "")),
    ]
    text = " ".join(text_parts)
    if any(w in text for w in ("亏损", "止损", "回撤", "打脸")):
        return True
    if re.search(r"-\d+(?:\.\d+)?%", text):
        return True
    return False


def detect_loss_patterns(decisions: Optional[list[dict]] = None) -> dict:
    """Detect common loss-driving behavior patterns from trade decisions.

    This is a rule-based MVP focused on actionable behavior feedback.
    """
    trades = decisions if decisions is not None else list_decisions(dtype="trade")
    if not trades:
        return {
            "ok": True,
            "total": 0,
            "patterns": [],
            "top_pattern": None,
            "next_day_rule": "暂无足够样本，先保证每笔交易有计划与止损。",
        }

    patterns = []
    losses = [d for d in trades if _has_loss_marker(d)]

    # 1) Buy without stop-loss
    no_sl_buys = [
        d for d in trades
        if d.get("action", "").upper() in ("BUY", "买入", "加仓") and not d.get("stop_loss")
    ]
    if no_sl_buys:
        patterns.append({
            "type": "buy_without_stop",
            "label": f"有 {len(no_sl_buys)} 笔买入未设止损，亏损易失控",
            "severity": "danger",
            "count": len(no_sl_buys),
        })

    # 2) High-confidence but loss
    high_conf_loss = [d for d in losses if (d.get("confidence") or 0) >= 0.7]
    if high_conf_loss:
        patterns.append({
            "type": "high_confidence_loss",
            "label": f"有 {len(high_conf_loss)} 笔高信心(>=0.7)仍亏损，存在过度自信",
            "severity": "danger",
            "count": len(high_conf_loss),
        })

    # 3) Chase/FOMO wording pattern
    chase_words = ("追高", "fomo", "怕踏空", "冲动")
    chase = [
        d for d in trades
        if any(w in str(d.get("title", "")).lower() for w in chase_words)
        or any(w in str(d.get("context", "")).lower() for w in chase_words)
        or any(w in str((d.get("trade_context") or {}).get("emotion", "")).lower() for w in chase_words)
    ]
    if chase:
        patterns.append({
            "type": "chase_fomo",
            "label": f"发现 {len(chase)} 笔疑似追高/FOMO 行为",
            "severity": "warn",
            "count": len(chase),
        })

    # 4) No review after acted
    no_review = [d for d in trades if d.get("state") == "acted"]
    if no_review:
        patterns.append({
            "type": "acted_not_reviewed",
            "label": f"有 {len(no_review)} 笔已执行未复盘，学习闭环断裂",
            "severity": "info",
            "count": len(no_review),
        })

    # 5) Overtrading day (>=5 trade decisions/day)
    by_date = {}
    for d in trades:
        date = (d.get("created_at") or "")[:10]
        if date:
            by_date[date] = by_date.get(date, 0) + 1
    overtrading_days = {k: v for k, v in by_date.items() if v >= 5}
    if overtrading_days:
        patterns.append({
            "type": "overtrading",
            "label": f"有 {len(overtrading_days)} 天交易决策 >=5 笔，疑似过度交易",
            "severity": "warn",
            "count": len(overtrading_days),
        })

    # 6) Consecutive losses (by created order)
    consec_loss = 0
    max_consec_loss = 0
    for d in sorted(trades, key=lambda x: x.get("created_at", "")):
        if _has_loss_marker(d):
            consec_loss += 1
            max_consec_loss = max(max_consec_loss, consec_loss)
        else:
            consec_loss = 0
    if max_consec_loss >= 2:
        patterns.append({
            "type": "consecutive_losses",
            "label": f"出现连续亏损（最长 {max_consec_loss} 笔），应触发降频机制",
            "severity": "warn",
            "count": max_consec_loss,
        })

    severity_rank = {"danger": 3, "warn": 2, "info": 1}
    patterns.sort(key=lambda p: (severity_rank.get(p.get("severity", "info"), 0), p.get("count", 0)), reverse=True)
    top_pattern = patterns[0] if patterns else None

    rule_map = {
        "buy_without_stop": "明日硬约束：无止损不下单，止损位必须在建仓前写入。",
        "high_confidence_loss": "明日硬约束：信心>0.7 的单子仓位上限降至常规的 50%。",
        "chase_fomo": "明日硬约束：不追涨，必须等待一次回踩确认再决策。",
        "acted_not_reviewed": "明日硬约束：先补齐今日复盘，再允许新增交易决策。",
        "overtrading": "明日硬约束：单日决策不超过 3 笔，超过后只允许观察。",
        "consecutive_losses": "明日硬约束：连续两笔亏损后，暂停新开仓直到下一交易日。",
    }
    next_day_rule = rule_map.get(top_pattern["type"], "明日硬约束：先执行计划，再执行交易。") if top_pattern else "暂无明显亏损模式，维持纪律执行。"

    return {
        "ok": True,
        "total": len(trades),
        "loss_samples": len(losses),
        "patterns": patterns,
        "top_pattern": top_pattern,
        "next_day_rule": next_day_rule,
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
