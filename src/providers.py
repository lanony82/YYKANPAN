"""
providers.py — Stock data providers (AkShare, Sina, Yahoo Finance)
Handles fetching, caching, retries, and the A-share fallback chain.
"""

import json
import re
import time

import yfinance as yf
from urllib import request as urlrequest

from config import cfg
from time_utils import BeijingTime

try:
    import akshare as ak
except Exception:
    ak = None

# ── Constants (from config) ───────────────────────────────────────────────────
MAX_FETCH_RETRIES = cfg.MAX_FETCH_RETRIES
RETRY_BACKOFF_SECONDS = cfg.RETRY_BACKOFF_SECONDS
AK_CACHE_TTL_SECONDS = cfg.AK_CACHE_TTL_SECONDS
_52W_CACHE_TTL = cfg.WEEK52_CACHE_TTL_SECONDS

# ── Module-level caches ──────────────────────────────────────────────────────
AK_CACHE_DF = None
AK_CACHE_TS = 0.0
_52W_CACHE: dict = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ticker_to_a_share_code(ticker: str) -> str:
    """Normalize ticker to a 6-digit A-share code (e.g. 600519.SS -> 600519)."""
    return ticker.upper().split(".")[0]


def is_a_share_ticker(ticker: str) -> bool:
    """Detect A-share style tickers (000001.SZ / 600519.SS / plain 6-digit)."""
    t = ticker.upper()
    if t.endswith(".SS") or t.endswith(".SZ"):
        return True
    return len(t) == 6 and t.isdigit()


def _is_retryable_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    retry_tokens = [
        "recv failure", "connection was reset", "connection aborted",
        "remote end closed", "timeout", "timed out", "temporary failure",
        "max retries exceeded", "502", "503", "504",
    ]
    return any(token in msg for token in retry_tokens)


def with_retries(func):
    """Execute *func* with up to MAX_FETCH_RETRIES attempts on transient errors."""
    last_exc = None
    for i in range(MAX_FETCH_RETRIES):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
            if i == MAX_FETCH_RETRIES - 1 or not _is_retryable_error(exc):
                raise
            time.sleep(RETRY_BACKOFF_SECONDS * (i + 1))
    raise last_exc


def _ticker_to_sina_symbol(ticker: str) -> str:
    code = _ticker_to_a_share_code(ticker)
    t = ticker.upper()
    if t.endswith(".SS"):
        market = "sh"
    elif t.endswith(".SZ"):
        market = "sz"
    else:
        market = "sh" if code.startswith(("5", "6", "9")) else "sz"
    return f"{market}{code}"


# ── 52-week high/low (Sina K-line) ────────────────────────────────────────────

def _fetch_52w(ticker: str) -> tuple:
    """Return (high52, low52) using Sina daily K-line (260 trading days ≈ 1 year).
    Results are cached for 12 hours per ticker."""
    code = _ticker_to_a_share_code(ticker)
    now = time.time()
    cached = _52W_CACHE.get(code)
    if cached and (now - cached["ts"]) < _52W_CACHE_TTL:
        return cached["high52"], cached["low52"]

    try:
        symbol = _ticker_to_sina_symbol(ticker)
        api = (
            f"{cfg.SINA_KLINE_API_URL}"
            f"?symbol={symbol}&scale=240&ma=no&datalen={cfg.TRADING_DAYS_PER_YEAR}"
        )
        req = urlrequest.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urlrequest.urlopen(req, timeout=cfg.SINA_KLINE_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")

        data = json.loads(raw)
        if not data:
            return None, None

        highs = [float(d.get("high", 0)) for d in data if d.get("high")]
        lows = [float(d.get("low", 0)) for d in data if d.get("low")]
        high52 = round(max(highs), 2) if highs else None
        low52 = round(min(lows), 2) if lows else None

        _52W_CACHE[code] = {"high52": high52, "low52": low52, "ts": now}
        return high52, low52
    except Exception:
        return None, None


# ── Individual providers ──────────────────────────────────────────────────────

def fetch_stock_yahoo(ticker: str, name: str = "") -> dict:
    """Primary provider: Yahoo Finance via yfinance."""
    try:
        def _query():
            t_local = yf.Ticker(ticker)
            hist_local = t_local.history(period=cfg.YAHOO_HISTORY_PERIOD, timeout=cfg.YAHOO_TIMEOUT)
            return t_local, hist_local

        t, hist = with_retries(_query)
        if hist.empty:
            return {"ticker": ticker, "name": name, "error": "无数据"}

        today = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]

        price = round(float(today["Close"]), 2)
        prev_close = round(float(prev["Close"]), 2)
        change = round(price - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        volume = int(today["Volume"])

        info = t.fast_info
        high52 = round(float(getattr(info, "fifty_two_week_high", 0) or 0), 2)
        low52 = round(float(getattr(info, "fifty_two_week_low", 0) or 0), 2)
        mktcap = getattr(info, "market_cap", None)

        display_name = name or (t.info.get("longName") or t.info.get("shortName") or ticker)

        return {
            "ticker": ticker, "name": display_name, "price": price,
            "prev_close": prev_close, "change": change, "change_pct": change_pct,
            "volume": volume, "high52": high52, "low52": low52,
            "market_cap": mktcap, "date": today.name.date().isoformat(),
            "source": "yahoo", "error": None,
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "error": str(e)}


def fetch_stock_akshare(ticker: str, name: str = "") -> dict:
    """Fallback provider for A-shares only via AkShare (东方财富)."""
    global AK_CACHE_DF, AK_CACHE_TS

    if ak is None:
        return {"ticker": ticker, "name": name, "error": "AkShare not installed"}

    code = _ticker_to_a_share_code(ticker)
    now = time.time()

    try:
        if AK_CACHE_DF is None or (now - AK_CACHE_TS) > AK_CACHE_TTL_SECONDS:
            AK_CACHE_DF = with_retries(ak.stock_zh_a_spot_em)
            AK_CACHE_TS = now

        df = AK_CACHE_DF
        if df is None or df.empty:
            return {"ticker": ticker, "name": name, "error": "A股实时数据为空"}

        row_df = df[df["代码"].astype(str) == code]
        if row_df.empty:
            return {"ticker": ticker, "name": name, "error": "代码不存在"}

        row = row_df.iloc[0]
        price = float(row.get("最新价", 0) or 0)
        change_pct = float(row.get("涨跌幅", 0) or 0)
        change = float(row.get("涨跌额", 0) or 0)
        volume = int(float(row.get("成交量", 0) or 0))
        market_cap = row.get("总市值", None)
        prev_close = round(price - change, 2)

        high52 = row.get("52周最高") or row.get("year_high") or None
        low52 = row.get("52周最低") or row.get("year_low") or None
        try:
            high52 = round(float(high52), 2) if high52 else None
        except (ValueError, TypeError):
            high52 = None
        try:
            low52 = round(float(low52), 2) if low52 else None
        except (ValueError, TypeError):
            low52 = None

        display_name = name or str(row.get("名称", "")).strip() or ticker

        return {
            "ticker": ticker, "name": display_name, "price": round(price, 2),
            "prev_close": prev_close, "change": round(change, 2),
            "change_pct": round(change_pct, 2), "volume": volume,
            "high52": high52, "low52": low52, "market_cap": market_cap,
            "date": BeijingTime.date_str(), "source": "akshare", "error": None,
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "error": str(e)}


def fetch_stock_sina(ticker: str, name: str = "") -> dict:
    """Fallback provider for A-shares only using Sina real-time quote endpoint."""
    if not is_a_share_ticker(ticker):
        return {"ticker": ticker, "name": name, "error": "not an A-share ticker"}

    symbol = _ticker_to_sina_symbol(ticker)
    url = f"{cfg.SINA_QUOTE_API_URL}{symbol}"
    req = urlrequest.Request(
        url,
        headers={
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0",
        },
    )

    try:
        def _download():
            with urlrequest.urlopen(req, timeout=cfg.SINA_QUOTE_TIMEOUT) as resp:
                return resp.read().decode("gbk", errors="ignore")

        body = with_retries(_download)
        match = re.search(r'="([^"]*)"', body)
        if not match:
            return {"ticker": ticker, "name": name, "error": "Sina响应格式异常"}

        payload = match.group(1)
        if not payload:
            return {"ticker": ticker, "name": name, "error": "Sina返回空数据"}

        parts = payload.split(",")
        if len(parts) < 32:
            return {"ticker": ticker, "name": name, "error": "Sina字段不足"}

        display_name = name or parts[0].strip() or ticker
        price = float(parts[3] or 0)
        prev_close = float(parts[2] or 0)
        change = round(price - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        volume = int(float(parts[8] or 0))
        trade_date = parts[30].strip() if len(parts) > 30 else BeijingTime.date_str()

        high52, low52 = _fetch_52w(ticker)

        return {
            "ticker": ticker, "name": display_name, "price": round(price, 2),
            "prev_close": round(prev_close, 2), "change": change,
            "change_pct": change_pct, "volume": volume, "high52": high52,
            "low52": low52, "market_cap": None, "date": trade_date,
            "source": "sina", "error": None,
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "error": str(e)}


def fetch_history_closes(ticker: str, days: int) -> list[float]:
    """Fetch recent close prices via Sina daily K-line API."""
    if not is_a_share_ticker(ticker):
        return []
    try:
        symbol = _ticker_to_sina_symbol(ticker)
        api = (
            f"{cfg.SINA_KLINE_API_URL}"
            f"?symbol={symbol}&scale=240&ma=no&datalen={days}"
        )
        req = urlrequest.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urlrequest.urlopen(req, timeout=cfg.SINA_KLINE_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        data = json.loads(raw)
        if not data:
            return []
        return [round(float(d["close"]), 2) for d in data if d.get("close")]
    except Exception:
        return []


# ── Unified fetch with fallback chain ─────────────────────────────────────────

def fetch_stock(ticker: str, name: str = "") -> dict:
    """
    Fetch a stock snapshot.
    Strategy:
      A-shares: AkShare → Sina → Yahoo
      Non A-shares: Yahoo only
    """
    if is_a_share_ticker(ticker):
        primary = fetch_stock_akshare(ticker, name)
        if not primary.get("error"):
            return primary

        fallback = fetch_stock_sina(ticker, name)
        if not fallback.get("error"):
            return fallback

        fallback2 = fetch_stock_yahoo(ticker, name)
        if not fallback2.get("error"):
            return fallback2

        fallback2["error"] = (
            f"AkShare失败: {primary.get('error')} | "
            f"Sina失败: {fallback.get('error')} | "
            f"Yahoo失败: {fallback2.get('error')}"
        )
        return fallback2

    return fetch_stock_yahoo(ticker, name)
