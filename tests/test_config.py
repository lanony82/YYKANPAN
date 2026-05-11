"""Tests for src/config.py — centralized configuration module."""

import os
import pathlib
import sys

import pytest

SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(autouse=True)
def _clean_config_import():
    """Ensure fresh config import for each test (env var isolation)."""
    saved = {k: sys.modules[k] for k in list(sys.modules) if k.startswith("config")}
    for m in saved:
        del sys.modules[m]
    yield
    # Remove any config modules created during the test
    for m in [k for k in sys.modules if k.startswith("config")]:
        del sys.modules[m]
    # Restore the original modules so other test files aren't affected
    sys.modules.update(saved)


def test_defaults_without_env():
    from config import cfg

    assert cfg.SERVER_PORT == 5000
    assert cfg.AK_CACHE_TTL_SECONDS == 120
    assert cfg.MAX_FETCH_RETRIES == 2
    assert cfg.SINA_KLINE_TIMEOUT == 8
    assert cfg.YAHOO_TIMEOUT == 10
    assert cfg.NEWS_HEADLINE_LIMIT == 5
    assert isinstance(cfg.NEWS_FEEDS, list)
    assert len(cfg.NEWS_FEEDS) == 2


def test_env_override(monkeypatch):
    monkeypatch.setenv("FUN_PORT", "9999")
    monkeypatch.setenv("FUN_MAX_RETRIES", "5")
    monkeypatch.setenv("FUN_DEBUG", "false")

    from config import cfg

    assert cfg.SERVER_PORT == 9999
    assert cfg.MAX_FETCH_RETRIES == 5
    assert cfg.DEBUG_MODE is False


def test_paths_are_pathlib():
    from config import cfg

    assert isinstance(cfg.WATCHLIST_PATH, pathlib.Path)
    assert isinstance(cfg.SENTIMENT_CACHE_PATH, pathlib.Path)
    assert isinstance(cfg.DATA_DIR, pathlib.Path)


def test_sentiment_thresholds_structure():
    from config import cfg

    t = cfg.SENTIMENT_THRESHOLDS
    assert "up_ratio_strong" in t
    assert "consec_low" in t
    assert t["up_ratio_strong"] == 0.65
