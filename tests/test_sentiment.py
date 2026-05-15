"""Tests for src/sentiment.py — evaluate_market_sentiment + merge/history helpers."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
from unittest.mock import patch

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Must import config first to set up defaults
import config  # noqa: F401
from analysis.sentiment import (
    evaluate_market_sentiment,
    merge_with_last_known,
    append_sentiment_history,
    load_sentiment_history,
    SENTIMENT_THRESHOLDS,
)


# ── evaluate_market_sentiment ────────────────────────────────────────────────

class TestEvaluateMarketSentiment:
    """Test the core 上升/退潮/分歧 classification engine."""

    def test_strong_bullish_returns_shangsheng(self):
        """All metrics strong → 上升 stage, tradable."""
        result = evaluate_market_sentiment(
            up_count=3500, down_count=1500,
            limit_up_count=50, consecutive_limit_count=15,
        )
        assert result["ok"] is True
        assert result["stage"] == "上升"
        assert result["tradable"] is True
        assert result["metrics"]["score"] >= 2

    def test_strong_bearish_returns_tuichao(self):
        """All metrics weak → 退潮 stage, not tradable."""
        result = evaluate_market_sentiment(
            up_count=1000, down_count=4000,
            limit_up_count=5, consecutive_limit_count=1,
        )
        assert result["ok"] is True
        assert result["stage"] == "退潮"
        assert result["tradable"] is False
        assert result["metrics"]["score"] <= -1

    def test_mixed_returns_fenqi(self):
        """Middling metrics → 分歧 stage."""
        result = evaluate_market_sentiment(
            up_count=2500, down_count=2500,
            limit_up_count=25, consecutive_limit_count=6,
        )
        assert result["ok"] is True
        assert result["stage"] == "分歧"
        assert result["tradable"] is False

    def test_up_ratio_calculated(self):
        result = evaluate_market_sentiment(
            up_count=3000, down_count=2000,
            limit_up_count=30, consecutive_limit_count=8,
        )
        assert result["metrics"]["up_ratio"] == pytest.approx(0.6, abs=0.01)

    def test_zero_total_no_crash(self):
        """Both counts zero should not divide by zero."""
        result = evaluate_market_sentiment(0, 0, 0, 0)
        assert result["ok"] is True
        assert "stage" in result

    def test_result_has_plain_text(self):
        result = evaluate_market_sentiment(3000, 2000, 25, 6)
        assert isinstance(result["plain"], str)
        assert len(result["plain"]) > 10

    def test_reasons_list_populated(self):
        result = evaluate_market_sentiment(3500, 1500, 50, 15)
        assert isinstance(result["reasons"], list)
        assert len(result["reasons"]) >= 1


# ── merge_with_last_known ────────────────────────────────────────────────────

class TestMergeWithLastKnown:
    def test_no_fallback_when_complete(self):
        metrics = {"up_count": 100, "down_count": 50,
                   "limit_up_count": 10, "consecutive_limit_count": 3}
        merged, fallbacks = merge_with_last_known(metrics)
        assert fallbacks == []
        assert merged == metrics

    def test_fills_missing_from_cache(self):
        metrics = {"up_count": None, "down_count": 200,
                   "limit_up_count": None, "consecutive_limit_count": 5}
        merged, fallbacks = merge_with_last_known(metrics)
        assert "up_count" in fallbacks
        assert "limit_up_count" in fallbacks
        assert merged["down_count"] == 200
        assert merged["consecutive_limit_count"] == 5


# ── append_sentiment_history ─────────────────────────────────────────────────

class TestAppendSentimentHistory:
    def test_dedup_same_hour(self, tmp_path):
        """Same hour entries should be deduplicated."""
        hist_file = tmp_path / "history.json"
        hist_file.write_text("[]", encoding="utf-8")

        with patch("analysis.sentiment._SENTIMENT_HISTORY_FILE", hist_file), \
             patch("analysis.sentiment.BeijingTime") as mock_bt:
            mock_bt.datetime_str.return_value = "2026-05-08 14:30:00"

            result = {"metrics": {"score": 2}, "stage": "上升"}

            # First append succeeds
            append_sentiment_history(result)
            data = json.loads(hist_file.read_text(encoding="utf-8"))
            assert len(data) == 1

            # Same hour → skipped
            mock_bt.datetime_str.return_value = "2026-05-08 14:45:00"
            append_sentiment_history(result)
            data = json.loads(hist_file.read_text(encoding="utf-8"))
            assert len(data) == 1

            # New hour → appended
            mock_bt.datetime_str.return_value = "2026-05-08 15:00:00"
            append_sentiment_history(result)
            data = json.loads(hist_file.read_text(encoding="utf-8"))
            assert len(data) == 2
