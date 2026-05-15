"""Tests for Decision Journal (src/decision.py)."""

import json
import sys
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
from trading import decision as dec


@pytest.fixture(autouse=True)
def _tmp_decisions(tmp_path, monkeypatch):
    """Redirect decisions file to a temp directory."""
    tmp_file = tmp_path / "decisions.json"
    monkeypatch.setattr(dec, "_DECISIONS_FILE", tmp_file)
    yield tmp_file


class TestCreateDecision:
    def test_basic_create(self):
        d = dec.create_decision("Buy AAPL on dip")
        assert d["title"] == "Buy AAPL on dip"
        assert d["type"] == "trade"
        assert d["state"] == "idea"
        assert d["id"]
        assert d["created_at"]
        assert d["tags"] == []

    def test_create_with_all_fields(self):
        d = dec.create_decision(
            title="Switch jobs",
            dtype="work",
            context="Market downturn, good offers",
            action="Accepted offer B",
            outcome="Salary +30%",
            tags=["career", "risk"],
            state="reviewed",
        )
        assert d["type"] == "work"
        assert d["state"] == "reviewed"
        assert d["tags"] == ["career", "risk"]
        assert d["outcome"] == "Salary +30%"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="type must be"):
            dec.create_decision("test", dtype="invalid")

    def test_invalid_state_raises(self):
        with pytest.raises(ValueError, match="state must be"):
            dec.create_decision("test", state="invalid")

    def test_whitespace_stripped(self):
        d = dec.create_decision("  spaced title  ", context="  ctx  ")
        assert d["title"] == "spaced title"
        assert d["context"] == "ctx"

    def test_tags_cleaned(self):
        d = dec.create_decision("t", tags=["  a ", "", "  b  ", ""])
        assert d["tags"] == ["a", "b"]


class TestListDecisions:
    def test_list_empty(self):
        assert dec.list_decisions() == []

    def test_list_all(self):
        dec.create_decision("A", dtype="trade")
        dec.create_decision("B", dtype="life")
        dec.create_decision("C", dtype="work")
        assert len(dec.list_decisions()) == 3

    def test_filter_by_type(self):
        dec.create_decision("A", dtype="trade")
        dec.create_decision("B", dtype="life")
        result = dec.list_decisions(dtype="trade")
        assert len(result) == 1
        assert result[0]["title"] == "A"

    def test_filter_by_state(self):
        dec.create_decision("A", state="idea")
        dec.create_decision("B", state="acted")
        result = dec.list_decisions(state="acted")
        assert len(result) == 1
        assert result[0]["title"] == "B"

    def test_filter_by_type_and_state(self):
        dec.create_decision("A", dtype="trade", state="idea")
        dec.create_decision("B", dtype="trade", state="acted")
        dec.create_decision("C", dtype="life", state="idea")
        result = dec.list_decisions(dtype="trade", state="idea")
        assert len(result) == 1
        assert result[0]["title"] == "A"


class TestGetDecision:
    def test_get_existing(self):
        d = dec.create_decision("Find me")
        found = dec.get_decision(d["id"])
        assert found["title"] == "Find me"

    def test_get_missing(self):
        assert dec.get_decision("nonexistent") is None


class TestUpdateDecision:
    def test_update_title_and_state(self):
        d = dec.create_decision("Original")
        updated = dec.update_decision(d["id"], {"title": "Changed", "state": "acted"})
        assert updated["title"] == "Changed"
        assert updated["state"] == "acted"
        assert updated["updated_at"] >= d["created_at"]

    def test_update_tags(self):
        d = dec.create_decision("T", tags=["a"])
        updated = dec.update_decision(d["id"], {"tags": ["b", "c"]})
        assert updated["tags"] == ["b", "c"]

    def test_update_invalid_type(self):
        d = dec.create_decision("T")
        with pytest.raises(ValueError):
            dec.update_decision(d["id"], {"type": "bad"})

    def test_update_invalid_state(self):
        d = dec.create_decision("T")
        with pytest.raises(ValueError):
            dec.update_decision(d["id"], {"state": "bad"})

    def test_update_nonexistent(self):
        assert dec.update_decision("nope", {"title": "x"}) is None

    def test_ignores_unknown_fields(self):
        d = dec.create_decision("T")
        updated = dec.update_decision(d["id"], {"title": "New", "hacker": "drop table"})
        assert updated["title"] == "New"
        assert "hacker" not in updated


class TestDeleteDecision:
    def test_delete_existing(self):
        d = dec.create_decision("Delete me")
        assert dec.delete_decision(d["id"]) is True
        assert dec.list_decisions() == []

    def test_delete_nonexistent(self):
        assert dec.delete_decision("nope") is False


class TestPersistence:
    def test_survives_reload(self, _tmp_decisions):
        dec.create_decision("Persistent")
        # Re-read from file
        data = json.loads(_tmp_decisions.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["title"] == "Persistent"

    def test_max_cap(self, monkeypatch):
        monkeypatch.setattr(dec, "MAX_DECISIONS", 3)
        for i in range(5):
            dec.create_decision(f"D{i}")
        result = dec.list_decisions()
        assert len(result) == 3
        assert result[0]["title"] == "D2"  # oldest kept


class TestKanbanFlow:
    """Test a realistic kanban workflow: idea → decided → acted → reviewed."""

    def test_full_flow(self):
        d = dec.create_decision("Buy 600519 breakout", dtype="trade", tags=["breakout"])
        assert d["state"] == "idea"

        d = dec.update_decision(d["id"], {"state": "decided", "action": "Set limit order at 1700"})
        assert d["state"] == "decided"
        assert d["action"] == "Set limit order at 1700"

        d = dec.update_decision(d["id"], {"state": "acted"})
        assert d["state"] == "acted"

        d = dec.update_decision(d["id"], {"state": "reviewed", "outcome": "+5% in 3 days"})
        assert d["state"] == "reviewed"
        assert d["outcome"] == "+5% in 3 days"
