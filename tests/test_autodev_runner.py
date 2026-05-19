"""Tests for autodev_runner.py — autonomous data assembly + cycle execution."""
import sys
import pathlib
import pytest

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trading.autodev_runner import build_positions, build_context, run_auto
from analysis.advisor import PositionInput, MarketContext


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _isolate_decisions(tmp_path, monkeypatch):
    """Redirect decision journal to temp dir."""
    monkeypatch.setattr(
        "trading.decision._DECISIONS_FILE", tmp_path / "decisions.json"
    )


STOCK_MAP = {
    "600519": {
        "ticker": "600519",
        "name": "贵州茅台",
        "price": 1750.0,
        "prev_close": 1800.0,
        "change_pct": -2.78,
        "volume": 50000,
        "high52": 2100.0,
        "low52": 1500.0,
        "source": "akshare",
    },
    "000001": {
        "ticker": "000001",
        "name": "平安银行",
        "price": 12.5,
        "prev_close": 12.3,
        "change_pct": 1.63,
        "volume": 800000,
        "high52": 15.0,
        "low52": 9.0,
        "source": "sina",
    },
}

HOLDINGS = [
    {"ticker": "600519", "shares": 100, "cost": 1800.0},
    {"ticker": "000001", "shares": 500, "cost": 11.0, "name": "平银"},
]


# ── build_positions ──────────────────────────────────────────────────────────

class TestBuildPositions:
    def test_basic(self):
        pos = build_positions(HOLDINGS, STOCK_MAP)
        assert len(pos) == 2
        assert isinstance(pos[0], PositionInput)

    def test_fills_price_from_stock_map(self):
        pos = build_positions(HOLDINGS, STOCK_MAP)
        assert pos[0].price == 1750.0
        assert pos[0].high52 == 2100.0
        assert pos[0].low52 == 1500.0

    def test_keeps_cost_from_holdings(self):
        pos = build_positions(HOLDINGS, STOCK_MAP)
        assert pos[0].cost == 1800.0
        assert pos[1].cost == 11.0

    def test_name_from_stock_map(self):
        pos = build_positions(HOLDINGS, STOCK_MAP)
        assert pos[0].name == "贵州茅台"  # from stock_map

    def test_name_fallback_to_holdings(self):
        pos = build_positions(
            [{"ticker": "999999", "shares": 10, "cost": 5.0, "name": "测试"}],
            {},
        )
        assert pos[0].name == "测试"

    def test_missing_stock_data(self):
        pos = build_positions(
            [{"ticker": "UNKNOWN", "shares": 1, "cost": 1.0}],
            {},
        )
        # Fallback: price = cost when no market data
        assert pos[0].price == 1.0
        assert pos[0].high52 is None

    def test_missing_stock_data_zero_cost(self):
        pos = build_positions(
            [{"ticker": "UNKNOWN", "shares": 1, "cost": 0}],
            {},
        )
        assert pos[0].price == 0

    def test_empty_holdings(self):
        assert build_positions([], STOCK_MAP) == []


# ── build_context ────────────────────────────────────────────────────────────

class TestBuildContext:
    def test_defaults(self):
        ctx = build_context()
        assert isinstance(ctx, MarketContext)
        assert ctx.regime == "震荡"
        assert ctx.sentiment_stage == "分歧"
        assert ctx.risk_events == []

    def test_custom(self):
        ctx = build_context(
            regime="偏强",
            sentiment_stage="上升",
            sentiment_score=3,
            tradable=True,
            confidence=80.0,
            risk_events=[{"type": "灰犀牛", "severity": "medium"}],
        )
        assert ctx.regime == "偏强"
        assert ctx.confidence == 80.0
        assert len(ctx.risk_events) == 1


# ── run_auto ─────────────────────────────────────────────────────────────────

class TestRunAuto:
    def test_returns_all_sections(self):
        result = run_auto(HOLDINGS, STOCK_MAP)
        for key in ("ok", "cycle", "signals", "decisions", "evaluations", "analysis", "data_sources"):
            assert key in result, f"missing section: {key}"

    def test_data_sources_attached(self):
        result = run_auto(HOLDINGS, STOCK_MAP)
        ds = result["data_sources"]
        assert ds["positions_count"] == 2
        assert ds["regime"] == "震荡"

    def test_custom_strategy(self):
        result = run_auto(
            HOLDINGS, STOCK_MAP, strategy_name="conservative",
        )
        assert result["cycle"]["strategy"] == "conservative_v1"

    def test_custom_risk_pref(self):
        result = run_auto(
            HOLDINGS, STOCK_MAP, risk_pref="aggressive",
        )
        assert result["cycle"]["risk_pref"] == "aggressive"

    def test_risk_events_in_context(self):
        events = [{"type": "黑天鹅", "severity": "high", "title": "暴跌"}]
        result = run_auto(HOLDINGS, STOCK_MAP, risk_events=events)
        assert result["data_sources"]["risk_events_count"] == 1

    def test_sentiment_stage_passed(self):
        result = run_auto(
            HOLDINGS, STOCK_MAP,
            sentiment_stage="退潮", sentiment_score=-2, tradable=False,
        )
        assert result["data_sources"]["sentiment_stage"] == "退潮"

    def test_empty_positions_still_works(self):
        result = run_auto([], STOCK_MAP)
        assert result["cycle"]["signals_count"] == 0

    def test_invalid_strategy_raises(self):
        with pytest.raises(FileNotFoundError):
            run_auto(HOLDINGS, STOCK_MAP, strategy_name="nonexistent")

    def test_evaluations_present(self):
        """Verify evaluations key exists (may be empty if no acted decisions)."""
        result = run_auto(HOLDINGS, STOCK_MAP)
        assert "evaluations" in result
