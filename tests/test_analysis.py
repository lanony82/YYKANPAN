"""Tests for src/analysis.py — quickread, macro_impact, AI edge formulas."""

from __future__ import annotations

import pathlib
import sys

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analysis import quickread_news, macro_impact, GLOSSARY


# ── quickread_news ───────────────────────────────────────────────────────────

class TestQuickreadNews:
    def test_empty_text_returns_error(self):
        result = quickread_news("")
        assert result["ok"] is False

    def test_positive_keywords_score_positive(self):
        result = quickread_news("公司财报显示营收增长，EPS超预期")
        assert result["ok"] is True
        assert "偏利好" in result["tags"]
        assert result["impact"] == "偏正面"

    def test_negative_keywords_score_negative(self):
        result = quickread_news("公司亏损加剧，净利润下滑严重")
        assert result["ok"] is True
        assert "偏利空" in result["tags"]
        assert result["impact"] == "偏负面"

    def test_neutral_text(self):
        result = quickread_news("今天天气不错，阳光明媚")
        assert result["ok"] is True
        assert "中性信息" in result["tags"]
        assert result["impact"] == "中性"

    def test_inflation_upward_is_negative(self):
        result = quickread_news("CPI通胀抬升，市场走高担忧加剧")
        assert result["ok"] is True
        assert "通胀线索" in result["tags"]

    def test_rate_cut_is_positive(self):
        result = quickread_news("央行宣布降息25bps，偏鸽信号明显")
        assert result["ok"] is True
        assert "利率线索" in result["tags"]
        assert "偏利好" in result["tags"]

    def test_rate_hike_is_negative(self):
        result = quickread_news("FOMC加息50bps，偏鹰超预期")
        assert result["ok"] is True
        assert "利率线索" in result["tags"]

    def test_summary_truncated(self):
        long_text = "A" * 500
        result = quickread_news(long_text)
        assert result["ok"] is True
        assert result["summary"].endswith("...")

    def test_has_plain_field(self):
        result = quickread_news("公司盈利改善，业绩超预期")
        assert "plain" in result
        assert isinstance(result["plain"], str)


# ── macro_impact ─────────────────────────────────────────────────────────────

class TestMacroImpact:
    def test_invalid_indicator(self):
        result = macro_impact("gdp", 2.0, 1.5)
        assert result["ok"] is False

    def test_missing_values(self):
        result = macro_impact("cpi", None, 2.0)
        assert result["ok"] is False

    def test_cpi_up_is_bearish(self):
        result = macro_impact("cpi", 2.5, 2.0)
        assert result["ok"] is True
        assert result["tone"] == "偏利空"
        assert result["delta"] == pytest.approx(0.5)

    def test_cpi_down_is_bullish(self):
        result = macro_impact("cpi", 1.8, 2.3)
        assert result["ok"] is True
        assert result["tone"] == "偏利好"

    def test_cpi_flat_is_neutral(self):
        result = macro_impact("cpi", 2.0, 2.0)
        assert result["ok"] is True
        assert result["tone"] == "中性"

    def test_rate_up_bearish(self):
        result = macro_impact("rate", 4.5, 4.0)
        assert result["tone"] == "偏利空"

    def test_rate_down_bullish(self):
        result = macro_impact("rate", 3.5, 4.0)
        assert result["tone"] == "偏利好"

    def test_earnings_up_bullish(self):
        result = macro_impact("earnings", 1.5, 1.2)
        assert result["tone"] == "偏利好"

    def test_earnings_down_bearish(self):
        result = macro_impact("earnings", 0.8, 1.2)
        assert result["tone"] == "偏利空"

    def test_has_plain_text(self):
        result = macro_impact("cpi", 2.5, 2.0)
        assert "plain" in result
        assert "CPI" in result["plain"]


# ── Glossary ─────────────────────────────────────────────────────────────────

class TestGlossary:
    def test_known_terms_exist(self):
        for term in ["cpi", "pe", "eps", "roe", "beta", "fomc"]:
            assert term in GLOSSARY

    def test_glossary_values_are_strings(self):
        for v in GLOSSARY.values():
            assert isinstance(v, str)
            assert len(v) > 5
