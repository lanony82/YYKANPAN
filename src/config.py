"""
config.py — Centralized configuration for YYKANPAN.

All tunable parameters are defined here with sensible defaults.
Override any value via environment variables (prefixed with FUN_).

Usage:
    from config import cfg
    timeout = cfg.SINA_QUOTE_TIMEOUT
"""

import os
import pathlib


def _env(key: str, default, cast=None):
    """Read from environment variable, cast to type if provided."""
    val = os.environ.get(key)
    if val is None:
        return default
    if cast is bool:
        return val.lower() in ("1", "true", "yes", "on")
    if cast is not None:
        return cast(val)
    return val


# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = pathlib.Path(__file__).resolve().parent.parent


class _Config:
    """Application configuration — all values overridable via env vars."""

    # ── Server ────────────────────────────────────────────────────────────────
    SERVER_HOST: str = _env("FUN_HOST", "127.0.0.1")
    SERVER_PORT: int = _env("FUN_PORT", 5000, int)
    DEBUG_MODE: bool = _env("FUN_DEBUG", True, bool)

    # ── Cache TTLs (seconds) ──────────────────────────────────────────────────
    AK_CACHE_TTL_SECONDS: int = _env("FUN_AK_CACHE_TTL", 120, int)
    STOCKS_CACHE_TTL_SECONDS: int = _env("FUN_STOCKS_CACHE_TTL", 600, int)
    WEEK52_CACHE_TTL_SECONDS: int = _env("FUN_52W_CACHE_TTL", 43200, int)
    HISTORY_CACHE_TTL_SECONDS: int = _env("FUN_HISTORY_CACHE_TTL", 3600, int)
    LIMIT_STATS_CACHE_TTL_SECONDS: int = _env("FUN_LIMIT_STATS_CACHE_TTL", 300, int)

    # ── Retry ─────────────────────────────────────────────────────────────────
    MAX_FETCH_RETRIES: int = _env("FUN_MAX_RETRIES", 2, int)
    RETRY_BACKOFF_SECONDS: float = _env("FUN_RETRY_BACKOFF", 0.8, float)
    LIVE_FETCH_TIMEOUT_SECONDS: int = _env("FUN_LIVE_FETCH_TIMEOUT", 180, int)

    # ── Timeouts (seconds) ────────────────────────────────────────────────────
    SINA_KLINE_TIMEOUT: int = _env("FUN_SINA_KLINE_TIMEOUT", 8, int)
    SINA_QUOTE_TIMEOUT: int = _env("FUN_SINA_QUOTE_TIMEOUT", 10, int)
    YAHOO_TIMEOUT: int = _env("FUN_YAHOO_TIMEOUT", 10, int)
    IWENCAI_TIMEOUT: int = _env("FUN_IWENCAI_TIMEOUT", 10, int)
    NEWS_FEED_TIMEOUT: int = _env("FUN_NEWS_TIMEOUT", 8, int)

    # ── Data source URLs ──────────────────────────────────────────────────────
    SINA_KLINE_API_URL: str = _env(
        "FUN_SINA_KLINE_URL",
        "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData",
    )
    SINA_QUOTE_API_URL: str = _env("FUN_SINA_QUOTE_URL", "https://hq.sinajs.cn/list=")
    IWENCAI_URL: str = _env(
        "FUN_IWENCAI_URL",
        "https://www.iwencai.com/unifiedwap/result",
    )
    NEWS_FEEDS: list = [
        "https://finance.yahoo.com/news/rssindex",
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    ]

    # ── Data parameters ───────────────────────────────────────────────────────
    TRADING_DAYS_PER_YEAR: int = _env("FUN_TRADING_DAYS", 260, int)
    YAHOO_HISTORY_PERIOD: str = _env("FUN_YAHOO_PERIOD", "2d")

    # ── Limits ────────────────────────────────────────────────────────────────
    SENTIMENT_HISTORY_MAX_ENTRIES: int = _env("FUN_SENTIMENT_HISTORY_MAX", 200, int)
    NEWS_HEADLINE_LIMIT: int = _env("FUN_NEWS_HEADLINE_LIMIT", 5, int)
    NEWS_SUMMARY_MAX_LENGTH: int = _env("FUN_NEWS_SUMMARY_MAX_LEN", 180, int)
    AUTO_BRIEF_HEADLINE_COUNT: int = _env("FUN_BRIEF_HEADLINES", 3, int)
    HISTORY_DEFAULT_DAYS: int = _env("FUN_HISTORY_DEFAULT_DAYS", 20, int)
    HISTORY_MAX_DAYS: int = _env("FUN_HISTORY_MAX_DAYS", 60, int)

    # ── Sentiment thresholds (defaults, overridden by sentiment_config.json) ──
    SENTIMENT_THRESHOLDS: dict = {
        "up_ratio_strong": 0.65,
        "up_ratio_mild": 0.55,
        "down_ratio_strong": 0.65,
        "down_ratio_mild": 0.55,
        "limit_up_high": 45,
        "limit_up_mid": 20,
        "limit_up_low": 8,
        "consec_high": 12,
        "consec_mid": 5,
        "consec_low": 2,
    }

    SENTIMENT_DEFAULTS: dict = {
        "up_count": 3877,
        "down_count": 1480,
        "limit_up_count": None,
        "consecutive_limit_count": None,
        "updated_at": None,
    }

    # ── Analysis thresholds ───────────────────────────────────────────────────
    PROFIT_RATE_GOOD_THRESHOLD: float = _env("FUN_PROFIT_RATE_GOOD", 60, float)
    PROFIT_RATE_NEUTRAL_THRESHOLD: float = _env("FUN_PROFIT_RATE_NEUTRAL", 40, float)
    MAINLINE_CONCENTRATION_THRESHOLD: float = _env("FUN_MAINLINE_CONC", 0.2, float)
    MAINLINE_STRENGTH_THRESHOLD: float = _env("FUN_MAINLINE_STRENGTH", 2.0, float)

    # ── File paths (relative to project root) ─────────────────────────────────
    WATCHLIST_PATH: pathlib.Path = BASE / "watchlist_cn.json"
    SENTIMENT_CACHE_PATH: pathlib.Path = BASE / "data" / "sentiment_last_known.json"
    SENTIMENT_CONFIG_PATH: pathlib.Path = BASE / "data" / "sentiment_config.json"
    SENTIMENT_HISTORY_PATH: pathlib.Path = BASE / "data" / "sentiment_history.json"
    DATA_DIR: pathlib.Path = BASE / "data"
    STATIC_DIR: pathlib.Path = BASE / "static"


cfg = _Config()
