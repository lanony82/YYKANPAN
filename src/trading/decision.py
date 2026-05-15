"""
decision.py — Decision Journal: record, track, and review decisions.

Core entity for the YYKANPAN decision-tracking system.
Decisions can be trade / life / work type, tracked through kanban states.
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
MAX_DECISIONS = 1000


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
        "context": context.strip(),
        "action": action.strip(),
        "outcome": outcome.strip(),
        "tags": [t.strip() for t in (tags or []) if t.strip()],
        "state": state,
        "created_at": now,
        "updated_at": now,
    }
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
