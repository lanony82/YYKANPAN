"""Tests for src/providers.py — ticker detection, normalization, retry logic."""

from __future__ import annotations

import pathlib
import sys

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from providers import (
    is_a_share_ticker,
    _ticker_to_a_share_code,
    _ticker_to_sina_symbol,
    _is_retryable_error,
    with_retries,
)


# ── A-share detection ────────────────────────────────────────────────────────

class TestIsAShareTicker:
    def test_ss_suffix(self):
        assert is_a_share_ticker("600519.SS") is True

    def test_sz_suffix(self):
        assert is_a_share_ticker("000001.SZ") is True

    def test_plain_six_digit(self):
        assert is_a_share_ticker("300750") is True

    def test_us_ticker(self):
        assert is_a_share_ticker("AAPL") is False

    def test_short_digit(self):
        assert is_a_share_ticker("123") is False

    def test_case_insensitive(self):
        assert is_a_share_ticker("600519.ss") is True


# ── Ticker normalization ─────────────────────────────────────────────────────

class TestTickerNormalization:
    def test_strip_ss_suffix(self):
        assert _ticker_to_a_share_code("600519.SS") == "600519"

    def test_strip_sz_suffix(self):
        assert _ticker_to_a_share_code("000001.SZ") == "000001"

    def test_plain_passthrough(self):
        assert _ticker_to_a_share_code("300750") == "300750"

    def test_sina_sh_for_ss(self):
        assert _ticker_to_sina_symbol("600519.SS") == "sh600519"

    def test_sina_sz_for_sz(self):
        assert _ticker_to_sina_symbol("000001.SZ") == "sz000001"

    def test_sina_sh_for_6_prefix(self):
        assert _ticker_to_sina_symbol("600519") == "sh600519"

    def test_sina_sz_for_0_prefix(self):
        assert _ticker_to_sina_symbol("000001") == "sz000001"

    def test_sina_sz_for_3_prefix(self):
        assert _ticker_to_sina_symbol("300750") == "sz300750"


# ── Retryable error detection ────────────────────────────────────────────────

class TestRetryableError:
    def test_timeout_retryable(self):
        assert _is_retryable_error(Exception("Connection timed out")) is True

    def test_502_retryable(self):
        assert _is_retryable_error(Exception("HTTP 502 Bad Gateway")) is True

    def test_reset_retryable(self):
        assert _is_retryable_error(Exception("connection was reset")) is True

    def test_value_error_not_retryable(self):
        assert _is_retryable_error(ValueError("invalid literal")) is False

    def test_key_error_not_retryable(self):
        assert _is_retryable_error(KeyError("missing")) is False


# ── with_retries ─────────────────────────────────────────────────────────────

class TestWithRetries:
    def test_success_first_try(self):
        assert with_retries(lambda: 42) == 42

    def test_retries_on_transient_then_succeeds(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 2:
                raise ConnectionError("recv failure")
            return "ok"

        assert with_retries(flaky) == "ok"
        assert calls["n"] == 2

    def test_raises_non_retryable_immediately(self):
        with pytest.raises(ValueError):
            with_retries(lambda: (_ for _ in ()).throw(ValueError("bad")))
