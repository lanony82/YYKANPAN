"""
app.py — Daily Stock Tracker Web App
Serves the frontend and provides a JSON API backed by AkShare-first data.

Run:
    python src/app.py
Then open http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory, abort
import yfinance as yf
import pathlib
import json
import time
import re
import os
import logging
from datetime import datetime
from urllib import request as urlrequest
from urllib import parse as urlparse
from time_utils import BeijingTime

try:
    # AkShare is used as a fallback for Chinese A-shares when Yahoo is blocked.
    import akshare as ak
except Exception:
    ak = None


def _configure_upstream_logging() -> None:
    """Reduce noisy third-party warning logs unless explicitly enabled."""
    if os.getenv("FUN_QUIET_UPSTREAM_LOGS", "1") != "1":
        return

    noisy_loggers = [
        "yfinance",
        "urllib3",
        "urllib3.connectionpool",
        "curl_cffi",
        "curl_cffi.requests",
    ]
    for name in noisy_loggers:
        logging.getLogger(name).setLevel(logging.CRITICAL)


_configure_upstream_logging()

BASE        = pathlib.Path(__file__).resolve().parent.parent
STATIC_DIR  = BASE / "static"
WATCHLIST   = BASE / "watchlist_cn.json"
SENTIMENT_CACHE_FILE = BASE / "data" / "sentiment_last_known.json"

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    template_folder=str(STATIC_DIR),
)

# Keep a short-lived in-memory cache to avoid repeatedly downloading
# the full A-share quote table on every ticker request.
AK_CACHE_DF = None
AK_CACHE_TS = 0.0
AK_CACHE_TTL_SECONDS = 20
STOCKS_CACHE_DATA = None
STOCKS_CACHE_TS = 0.0
STOCKS_CACHE_TTL_SECONDS = 600
MAX_FETCH_RETRIES = 2
RETRY_BACKOFF_SECONDS = 0.8

# 52-week high/low cache — keyed by code, refreshed every 12 hours.
_52W_CACHE: dict = {}
_52W_CACHE_TTL = 12 * 3600
NEWS_FEEDS = [
    "https://finance.yahoo.com/news/rssindex",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
]
SENTIMENT_LAST_KNOWN = {
    "up_count": 3877,
    "down_count": 1480,
    "limit_up_count": None,
    "consecutive_limit_count": None,
    "updated_at": None,
}

# ── Configurable sentiment thresholds ────────────────────────────────────────
SENTIMENT_THRESHOLDS = {
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
_SENTIMENT_CONFIG_FILE = BASE / "data" / "sentiment_config.json"

def _load_sentiment_config():
    global SENTIMENT_THRESHOLDS
    try:
        if _SENTIMENT_CONFIG_FILE.exists():
            with open(_SENTIMENT_CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            SENTIMENT_THRESHOLDS.update(saved)
    except Exception:
        pass

def _save_sentiment_config():
    try:
        _SENTIMENT_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_SENTIMENT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(SENTIMENT_THRESHOLDS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

_load_sentiment_config()

def _bj_now() -> datetime:
    return BeijingTime.now()


def _bj_date_str() -> str:
    return BeijingTime.date_str()


def _bj_datetime_str() -> str:
    return BeijingTime.datetime_str()


def _bj_yyyymmdd() -> str:
    return BeijingTime.yyyymmdd()


def _load_sentiment_last_known() -> None:
    global SENTIMENT_LAST_KNOWN
    try:
        if not SENTIMENT_CACHE_FILE.exists():
            return
        data = json.loads(SENTIMENT_CACHE_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return
        for k in ["up_count", "down_count", "limit_up_count", "consecutive_limit_count", "updated_at"]:
            if k in data:
                SENTIMENT_LAST_KNOWN[k] = data.get(k)
    except Exception:
        pass


def _save_sentiment_last_known() -> None:
    try:
        SENTIMENT_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SENTIMENT_CACHE_FILE.write_text(
            json.dumps(SENTIMENT_LAST_KNOWN, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


_load_sentiment_last_known()

# ── Sentiment history (for trend chart) ──────────────────────────────────────
_SENTIMENT_HISTORY_FILE = BASE / "data" / "sentiment_history.json"

def _load_sentiment_history() -> list:
    try:
        if _SENTIMENT_HISTORY_FILE.exists():
            data = json.loads(_SENTIMENT_HISTORY_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def _save_sentiment_history(history: list) -> None:
    try:
        _SENTIMENT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        _SENTIMENT_HISTORY_FILE.write_text(
            json.dumps(history[-200:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass

def _append_sentiment_history(result: dict) -> None:
    """Append a sentiment evaluation snapshot to history (max 1 per hour)."""
    history = _load_sentiment_history()
    ts = _bj_datetime_str()
    hour_key = ts[:13]  # "YYYY-MM-DD HH"
    # Deduplicate: skip if we already have an entry this hour
    if history and history[-1].get("ts", "")[:13] == hour_key:
        return
    entry = {
        "ts": ts,
        "score": result.get("metrics", {}).get("score", 0),
        "stage": result.get("stage", ""),
        "up_ratio": result.get("metrics", {}).get("up_ratio"),
        "inputs": result.get("inputs"),
    }
    history.append(entry)
    _save_sentiment_history(history)

GLOSSARY = {
    "cpi": "CPI 就是居民消费价格指数。你可以把它理解成'日常买菜、房租、交通'这类生活成本的温度计。",
    "ppi": "PPI 是工业品出厂价格指数，反映上游原材料和工厂出厂价格的变化。",
    "bps": "bps 是基点，100 个基点等于 1%。加息 25bps 就是加 0.25%。",
    "eps": "EPS 是每股收益，简单说就是公司每一股股票能赚多少钱。",
    "pe": "PE 是市盈率，表示你愿意用多少年利润去买这家公司。越高通常代表预期越高。",
    "pb": "PB 是市净率，表示股价相对净资产的倍数。适合看银行、周期等资产型公司。",
    "roe": "ROE 是净资产收益率，表示公司用股东的钱赚钱的效率。",
    "beta": "Beta 衡量股价相对大盘的波动幅度。大于 1 往往比大盘更'激进'。",
    "fomc": "FOMC 是美联储议息会议，市场会根据其加息/降息路径调整风险偏好。",
}

# ── Default watchlist (popular A-shares) ─────────────────────────────────────
DEFAULT_STOCKS = [
    {"ticker": "600519.SS", "name": "贵州茅台"},
    {"ticker": "000858.SZ", "name": "五粮液"},
    {"ticker": "601318.SS", "name": "中国平安"},
    {"ticker": "600036.SS", "name": "招商银行"},
    {"ticker": "300750.SZ", "name": "宁德时代"},
    {"ticker": "000001.SZ", "name": "平安银行"},
    {"ticker": "600900.SS", "name": "长江电力"},
    {"ticker": "601857.SS", "name": "中国石油"},
]

def load_watchlist():
    if WATCHLIST.exists():
        return json.loads(WATCHLIST.read_text(encoding="utf-8"))
    save_watchlist(DEFAULT_STOCKS)
    return DEFAULT_STOCKS

def save_watchlist(data):
    WATCHLIST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _ticker_to_a_share_code(ticker: str) -> str:
    """Normalize ticker to a 6-digit A-share code (e.g. 600519.SS -> 600519)."""
    code = ticker.upper().split(".")[0]
    return code


def _is_a_share_ticker(ticker: str) -> bool:
    """
    Detect A-share style tickers:
    - With suffix: 000001.SZ / 600519.SS
    - Without suffix: 000001 / 600519
    """
    t = ticker.upper()
    if t.endswith(".SS") or t.endswith(".SZ"):
        return True
    return len(t) == 6 and t.isdigit()


def _is_retryable_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    retry_tokens = [
        "recv failure",
        "connection was reset",
        "connection aborted",
        "remote end closed",
        "timeout",
        "timed out",
        "temporary failure",
        "max retries exceeded",
        "502",
        "503",
        "504",
    ]
    return any(token in msg for token in retry_tokens)


def _with_retries(func):
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
            f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=260"
        )
        req = urlrequest.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urlrequest.urlopen(req, timeout=8) as resp:
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


def _invalidate_stocks_cache() -> None:
    global STOCKS_CACHE_DATA, STOCKS_CACHE_TS
    STOCKS_CACHE_DATA = None
    STOCKS_CACHE_TS = 0.0


def _get_stocks_snapshot(force_refresh: bool = False) -> list[dict]:
    global STOCKS_CACHE_DATA, STOCKS_CACHE_TS

    now = time.time()
    if (
        not force_refresh
        and STOCKS_CACHE_DATA is not None
        and (now - STOCKS_CACHE_TS) <= STOCKS_CACHE_TTL_SECONDS
    ):
        return STOCKS_CACHE_DATA

    wl = load_watchlist()
    data = [fetch_stock(s["ticker"], s.get("name", "")) for s in wl]
    STOCKS_CACHE_DATA = data
    STOCKS_CACHE_TS = now
    return data


def _fetch_stock_yahoo(ticker: str, name: str = "") -> dict:
    """Primary provider: Yahoo Finance via yfinance."""
    try:
        def _query():
            t_local = yf.Ticker(ticker)
            hist_local = t_local.history(period="2d", timeout=10)
            return t_local, hist_local

        t, hist = _with_retries(_query)
        if hist.empty:
            return {"ticker": ticker, "name": name, "error": "无数据"}

        today  = hist.iloc[-1]
        prev   = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]

        price      = round(float(today["Close"]), 2)
        prev_close = round(float(prev["Close"]), 2)
        change     = round(price - prev_close, 2)
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        volume     = int(today["Volume"])

        info = t.fast_info
        high52 = round(float(getattr(info, "fifty_two_week_high", 0) or 0), 2)
        low52  = round(float(getattr(info, "fifty_two_week_low",  0) or 0), 2)
        mktcap = getattr(info, "market_cap", None)

        display_name = name or (t.info.get("longName") or t.info.get("shortName") or ticker)

        return {
            "ticker":     ticker,
            "name":       display_name,
            "price":      price,
            "prev_close": prev_close,
            "change":     change,
            "change_pct": change_pct,
            "volume":     volume,
            "high52":     high52,
            "low52":      low52,
            "market_cap": mktcap,
            "date":       today.name.date().isoformat(),
            "source":     "yahoo",
            "error":      None,
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "error": str(e)}


def _fetch_stock_akshare(ticker: str, name: str = "") -> dict:
    """
    Fallback provider for A-shares only.
    AkShare returns the whole spot table; we cache it briefly and then look up
    the required symbol locally.
    """
    global AK_CACHE_DF, AK_CACHE_TS

    if ak is None:
        return {"ticker": ticker, "name": name, "error": "AkShare not installed"}

    code = _ticker_to_a_share_code(ticker)
    now = time.time()

    try:
        if AK_CACHE_DF is None or (now - AK_CACHE_TS) > AK_CACHE_TTL_SECONDS:
            AK_CACHE_DF = _with_retries(ak.stock_zh_a_spot_em)
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

        # Reconstruct previous close from price and absolute change.
        prev_close = round(price - change, 2)

        # 52-week high/low from spot table (东方财富 columns)
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
            "ticker": ticker,
            "name": display_name,
            "price": round(price, 2),
            "prev_close": prev_close,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "high52": high52,
            "low52": low52,
            "market_cap": market_cap,
            "date": _bj_date_str(),
            "source": "akshare",
            "error": None,
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "error": str(e)}


def _fetch_stock_sina(ticker: str, name: str = "") -> dict:
    """
    Fallback provider for A-shares only using Sina real-time quote endpoint.
    This path has no third-party dependency and helps when other providers are flaky.
    """
    if not _is_a_share_ticker(ticker):
        return {"ticker": ticker, "name": name, "error": "not an A-share ticker"}

    symbol = _ticker_to_sina_symbol(ticker)
    url = f"https://hq.sinajs.cn/list={symbol}"
    req = urlrequest.Request(
        url,
        headers={
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0",
        },
    )

    try:
        def _download():
            with urlrequest.urlopen(req, timeout=10) as resp:
                return resp.read().decode("gbk", errors="ignore")

        body = _with_retries(_download)
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
        trade_date = parts[30].strip() if len(parts) > 30 else _bj_date_str()

        # 52-week high/low via Sina K-line (cached 12h)
        high52, low52 = _fetch_52w(ticker)

        return {
            "ticker": ticker,
            "name": display_name,
            "price": round(price, 2),
            "prev_close": round(prev_close, 2),
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "high52": high52,
            "low52": low52,
            "market_cap": None,
            "date": trade_date,
            "source": "sina",
            "error": None,
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "error": str(e)}


def fetch_stock(ticker: str, name: str = "") -> dict:
    """
    Fetch a stock snapshot.
    Strategy:
    1) For A-shares: AkShare -> Sina -> Yahoo.
    2) For non A-shares: Yahoo only.
    """
    if _is_a_share_ticker(ticker):
        primary = _fetch_stock_akshare(ticker, name)
        if not primary.get("error"):
            return primary

        fallback = _fetch_stock_sina(ticker, name)
        if not fallback.get("error"):
            return fallback

        fallback2 = _fetch_stock_yahoo(ticker, name)
        if not fallback2.get("error"):
            return fallback2

        fallback2["error"] = (
            f"AkShare失败: {primary.get('error')} | "
            f"Sina失败: {fallback.get('error')} | "
            f"Yahoo失败: {fallback2.get('error')}"
        )
        return fallback2

    return _fetch_stock_yahoo(ticker, name)


def _build_ai_edge_report(force_refresh: bool = False) -> dict:
    """Generate a compact AI-style market playbook from live watchlist data."""
    rows = _get_stocks_snapshot(force_refresh=force_refresh)
    valid = [r for r in rows if not r.get("error")]

    if not valid:
        return {
            "ok": False,
            "msg": "当前无可用行情数据，无法生成AI策略。",
        }

    up = [r for r in valid if (r.get("change_pct") or 0) > 0]
    down = [r for r in valid if (r.get("change_pct") or 0) < 0]
    avg = sum((r.get("change_pct") or 0) for r in valid) / len(valid)

    # AI confidence score: breadth + trend + volatility risk.
    breadth_score = (len(up) - len(down)) / max(len(valid), 1)
    volatility_penalty = sum(abs(r.get("change_pct") or 0) for r in valid) / len(valid)
    confidence = 60 + breadth_score * 25 + avg * 6 - max(0, volatility_penalty - 2.5) * 4
    confidence = max(10, min(95, round(confidence, 1)))

    focus_list = sorted(valid, key=lambda r: (r.get("change_pct") or -999), reverse=True)[:3]
    risk_list = sorted(valid, key=lambda r: (r.get("change_pct") or 999))[:3]

    market_bias = "中性震荡"
    if avg >= 1 and len(up) >= int(len(valid) * 0.6):
        market_bias = "偏多"
    elif avg <= -1 and len(down) >= int(len(valid) * 0.6):
        market_bias = "偏空"

    playbook = []
    if market_bias == "偏多":
        playbook.append("优先观察强势股回踩后的承接，不追高尾盘拉升。")
        playbook.append("仓位可从轻仓提升到中性，但保持分批。")
    elif market_bias == "偏空":
        playbook.append("先做风险控制，减少逆势加仓与情绪化交易。")
        playbook.append("等待缩量止跌或龙头反包后再提高仓位。")
    else:
        playbook.append("维持中性仓位，执行快进快出与严格止损。")
        playbook.append("只做相对强于指数的标的，弱势票不补仓。")

    return {
        "ok": True,
        "generated_at": _bj_datetime_str(),
        "summary": {
            "market_bias": market_bias,
            "confidence": confidence,
            "avg_change_pct": round(avg, 2),
            "up_count": len(up),
            "down_count": len(down),
            "coverage": len(valid),
        },
        "focus": [
            {
                "ticker": r.get("ticker"),
                "name": r.get("name"),
                "change_pct": round(float(r.get("change_pct") or 0), 2),
                "source": r.get("source"),
            }
            for r in focus_list
        ],
        "risks": [
            {
                "ticker": r.get("ticker"),
                "name": r.get("name"),
                "change_pct": round(float(r.get("change_pct") or 0), 2),
                "source": r.get("source"),
            }
            for r in risk_list
        ],
        "playbook": playbook,
    }


def _contains_any(text: str, words: list[str]) -> bool:
    return any(w in text for w in words)


def _quickread_news(text: str) -> dict:
    t = (text or "").strip()
    if not t:
        return {"ok": False, "msg": "请输入新闻或财报内容"}

    lower = t.lower()
    summary = t[:180] + ("..." if len(t) > 180 else "")
    tags = []
    score = 0

    if _contains_any(lower, ["cpi", "通胀", "inflation"]):
        tags.append("通胀线索")
    if _contains_any(lower, ["加息", "降息", "利率", "fomc", "fed"]):
        tags.append("利率线索")
    if _contains_any(lower, ["财报", "营收", "净利润", "guidance", "eps"]):
        tags.append("财报线索")

    if _contains_any(lower, ["超预期", "beat", "上修", "增长", "改善", "修复"]):
        score += 1
    if _contains_any(lower, ["不及预期", "miss", "下修", "下滑", "亏损", "担心", "承压"]):
        score -= 1
    if _contains_any(lower, ["cpi", "通胀"]) and _contains_any(lower, ["上行", "抬升", "走高"]):
        score -= 1
    if _contains_any(lower, ["加息", "偏鹰"]):
        score -= 1
    if _contains_any(lower, ["降息", "偏鸽"]):
        score += 1

    if score > 0:
        tags.append("偏利好")
    elif score < 0:
        tags.append("偏利空")

    if not tags:
        tags.append("中性信息")

    impact = "中性"
    reason = "信息偏描述性，需要结合行业和估值判断。"
    if "偏利好" in tags and "偏利空" not in tags:
        impact = "偏正面"
        reason = "出现超预期/改善信号，短期可能提升风险偏好。"
    elif "偏利空" in tags and "偏利好" not in tags:
        impact = "偏负面"
        reason = "出现不及预期/下修信号，短期可能压制估值。"

    return {
        "ok": True,
        "summary": summary,
        "tags": tags,
        "impact": impact,
        "reason": reason,
        "plain": f"一句话：这条信息整体{impact}，核心原因是{reason}",
    }


def _macro_impact(indicator: str, current: float | None, previous: float | None) -> dict:
    ind = (indicator or "").strip().lower()
    if ind not in {"cpi", "rate", "earnings"}:
        return {"ok": False, "msg": "indicator 仅支持 cpi / rate / earnings"}

    if current is None or previous is None:
        return {"ok": False, "msg": "请提供 current 和 previous 数值"}

    delta = current - previous
    tone = "中性"
    explain = ""

    if ind == "cpi":
        if delta > 0:
            tone = "偏利空"
            explain = "CPI 上行通常意味着通胀压力更高，市场会担心后续偏紧政策。"
        elif delta < 0:
            tone = "偏利好"
            explain = "CPI 回落通常缓解通胀压力，有利于市场风险偏好修复。"
        else:
            explain = "CPI 持平，通常对市场是中性影响。"

    if ind == "rate":
        if delta > 0:
            tone = "偏利空"
            explain = "利率上行会抬高贴现率，成长资产估值通常承压。"
        elif delta < 0:
            tone = "偏利好"
            explain = "利率下行通常缓解估值压力，对高估值板块更友好。"
        else:
            explain = "利率不变，资金面影响相对中性。"

    if ind == "earnings":
        if delta > 0:
            tone = "偏利好"
            explain = "盈利改善说明基本面增强，若可持续通常支撑股价中期表现。"
        elif delta < 0:
            tone = "偏利空"
            explain = "盈利走弱会压缩估值容忍度，市场更关注后续修复节奏。"
        else:
            explain = "盈利持平，股价更多取决于估值和预期变化。"

    return {
        "ok": True,
        "indicator": ind,
        "current": current,
        "previous": previous,
        "delta": round(delta, 4),
        "tone": tone,
        "plain": f"人话：{ind.upper()} 从 {previous} 变到 {current}，整体{tone}。{explain}",
    }


def _fetch_market_headlines(limit: int = 5) -> list[str]:
    headlines = []
    seen = set()

    for feed in NEWS_FEEDS:
        try:
            req = urlrequest.Request(feed, headers={"User-Agent": "Mozilla/5.0"})

            def _download():
                with urlrequest.urlopen(req, timeout=8) as resp:
                    return resp.read().decode("utf-8", errors="ignore")

            xml_text = _with_retries(_download)
            matches = re.findall(r"<title>(.*?)</title>", xml_text, flags=re.IGNORECASE | re.DOTALL)
            for raw in matches:
                title = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", raw, flags=re.DOTALL).strip()
                title = re.sub(r"\s+", " ", title)
                if not title:
                    continue
                if title.lower() in {"rss", "market news", "markets"}:
                    continue
                if title in seen:
                    continue
                seen.add(title)
                headlines.append(title)
                if len(headlines) >= limit:
                    return headlines
        except Exception:
            continue

    return headlines


def _build_auto_brief(force_refresh: bool = False) -> dict:
    rows = _get_stocks_snapshot(force_refresh=force_refresh)
    valid = [r for r in rows if not r.get("error")]
    errors = [r for r in rows if r.get("error")]

    if not valid:
        return {
            "ok": False,
            "msg": "当前无可用行情数据，请稍后重试。",
            "error_count": len(errors),
        }

    ups = [r for r in valid if (r.get("change_pct") or 0) > 0]
    downs = [r for r in valid if (r.get("change_pct") or 0) < 0]
    flats = [r for r in valid if (r.get("change_pct") or 0) == 0]
    avg_change = round(sum((r.get("change_pct") or 0) for r in valid) / len(valid), 2)

    best = max(valid, key=lambda r: r.get("change_pct") or -999)
    worst = min(valid, key=lambda r: r.get("change_pct") or 999)

    regime = "震荡"
    if avg_change >= 1 and len(ups) >= max(1, int(len(valid) * 0.6)):
        regime = "偏强"
    elif avg_change <= -1 and len(downs) >= max(1, int(len(valid) * 0.6)):
        regime = "偏弱"

    highlights = [
        f"市场温度：{regime}（平均涨跌幅 {avg_change}%）",
        f"上涨 {len(ups)} 家，下跌 {len(downs)} 家，平盘 {len(flats)} 家",
        f"最强：{best.get('name') or best.get('ticker')} {best.get('change_pct')}%",
        f"最弱：{worst.get('name') or worst.get('ticker')} {worst.get('change_pct')}%",
    ]

    risks = []
    if len(errors) > 0:
        risks.append(f"有 {len(errors)} 条行情抓取失败，建议关注数据源稳定性。")
    if abs((worst.get("change_pct") or 0)) >= 4:
        risks.append("出现较大波动个股，短线仓位建议控制节奏。")

    actions = []
    if regime == "偏强":
        actions.append("人话建议：偏强环境下可优先看相对强势股，回调分批观察。")
    elif regime == "偏弱":
        actions.append("人话建议：偏弱环境下先控回撤，减少追高，等待企稳信号。")
    else:
        actions.append("人话建议：震荡市重在节奏，强弱切换快，仓位宜中性。")

    if risks:
        actions.append("风险提示：" + " ".join(risks))

    headlines = _fetch_market_headlines(limit=3)
    headline_analysis = []
    for h in headlines:
        q = _quickread_news(h)
        headline_analysis.append({
            "title": h,
            "impact": q.get("impact", "中性"),
            "tags": q.get("tags", []),
        })

    return {
        "ok": True,
        "generated_at": _bj_datetime_str(),
        "snapshot": {
            "total": len(rows),
            "valid": len(valid),
            "error": len(errors),
            "avg_change_pct": avg_change,
            "regime": regime,
        },
        "highlights": highlights,
        "actions": actions,
        "headline_analysis": headline_analysis,
    }


def _evaluate_market_sentiment(
    up_count: int,
    down_count: int,
    limit_up_count: int,
    consecutive_limit_count: int,
) -> dict:
    t = SENTIMENT_THRESHOLDS
    total = max(up_count + down_count, 1)
    up_ratio = up_count / total
    down_ratio = down_count / total

    score = 0
    reasons = []

    if up_ratio >= t["up_ratio_strong"]:
        score += 2
        reasons.append("上涨家数明显占优，赚钱效应扩散。")
    elif up_ratio >= t["up_ratio_mild"]:
        score += 1
        reasons.append("上涨家数略占优，情绪有修复。")
    elif down_ratio >= t["down_ratio_strong"]:
        score -= 2
        reasons.append("下跌家数明显占优，市场承接偏弱。")
    elif down_ratio >= t["down_ratio_mild"]:
        score -= 1
        reasons.append("下跌家数略占优，情绪偏谨慎。")

    if limit_up_count >= t["limit_up_high"]:
        score += 2
        reasons.append("涨停数量高，短线做多热度强。")
    elif limit_up_count >= t["limit_up_mid"]:
        score += 1
        reasons.append("涨停数量尚可，说明市场仍有活跃主线。")
    elif limit_up_count <= t["limit_up_low"]:
        score -= 1
        reasons.append("涨停数量偏少，连板扩散能力有限。")

    if consecutive_limit_count >= t["consec_high"]:
        score += 2
        reasons.append("连板数量高，核心龙头具备持续带动作用。")
    elif consecutive_limit_count >= t["consec_mid"]:
        score += 1
        reasons.append("连板数量中等，短线接力情绪仍在。")
    elif consecutive_limit_count <= t["consec_low"]:
        score -= 1
        reasons.append("连板数量偏少，高标接力意愿不足。")

    if up_ratio >= t["up_ratio_mild"] and limit_up_count >= t["limit_up_mid"] and consecutive_limit_count >= t["consec_mid"]:
        stage = "上升"
        tradable = True
        advice = "适合交易，可优先围绕强势主线和核心个股，但仍需分批参与。"
    elif score <= -1 or (down_ratio > up_ratio and consecutive_limit_count <= 3):
        stage = "退潮"
        tradable = False
        advice = "不太适合积极交易，先控制回撤，尽量少追高，多观察情绪止跌信号。"
    else:
        stage = "分歧"
        tradable = False
        advice = "适合轻仓试错，不适合重仓激进交易，重点看强弱分离后的胜出方向。"

    return {
        "ok": True,
        "inputs": {
            "up_count": up_count,
            "down_count": down_count,
            "limit_up_count": limit_up_count,
            "consecutive_limit_count": consecutive_limit_count,
        },
        "metrics": {
            "up_ratio": round(up_ratio, 4),
            "down_ratio": round(down_ratio, 4),
            "score": score,
        },
        "stage": stage,
        "tradable": tradable,
        "tradable_text": "适合交易" if tradable else "暂不适合积极交易",
        "reasons": reasons,
        "plain": f"当前市场情绪处于{stage}阶段，{('适合交易' if tradable else '不太适合积极交易')}。{advice}",
    }


def _fetch_iwencai_count(keyword: str, pattern: str) -> int | None:
    """Fetch count from iWenCai page text using a regex pattern with one capture group."""
    url = f"https://www.iwencai.com/unifiedwap/result?w={urlparse.quote(keyword)}"
    req = urlrequest.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        def _download():
            with urlrequest.urlopen(req, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="ignore")

        text = _with_retries(_download)
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            return None
        return int(m.group(1))
    except Exception:
        return None


def _get_market_sentiment_inputs_auto() -> dict:
    """Auto-fetch four metrics: up/down count, limit-up count, and consecutive-board count."""
    up_count = _fetch_iwencai_count("上涨家数", r"涨跌幅>0%\s*\((\d+)个\)")
    down_count = _fetch_iwencai_count("下跌家数", r"涨跌幅<0%\s*\((\d+)个\)")

    limit_up_count = None
    consecutive_limit_count = None

    try:
        date = _bj_yyyymmdd()
        zt_df = _with_retries(lambda: ak.stock_zt_pool_em(date=date)) if ak is not None else None
        if zt_df is not None:
            limit_up_count = int(len(zt_df))
            if "连板数" in zt_df.columns:
                s = zt_df["连板数"].fillna(0).astype(int)
                consecutive_limit_count = int((s >= 2).sum())
    except Exception:
        pass

    return {
        "up_count": up_count,
        "down_count": down_count,
        "limit_up_count": limit_up_count,
        "consecutive_limit_count": consecutive_limit_count,
    }


def _update_sentiment_last_known(metrics: dict) -> None:
    global SENTIMENT_LAST_KNOWN
    changed = False
    for k in ["up_count", "down_count", "limit_up_count", "consecutive_limit_count"]:
        if metrics.get(k) is not None:
            SENTIMENT_LAST_KNOWN[k] = metrics[k]
            changed = True
    if changed:
        SENTIMENT_LAST_KNOWN["updated_at"] = _bj_datetime_str()
        _save_sentiment_last_known()


def _merge_with_last_known(metrics: dict) -> tuple[dict, list[str]]:
    merged = dict(metrics)
    fallback_fields = []
    for k in ["up_count", "down_count", "limit_up_count", "consecutive_limit_count"]:
        if merged.get(k) is None and SENTIMENT_LAST_KNOWN.get(k) is not None:
            merged[k] = SENTIMENT_LAST_KNOWN[k]
            fallback_fields.append(k)
    return merged, fallback_fields


def _normalize_code(code: str) -> str:
    c = str(code or "").strip().upper()
    if c.startswith("SZ") or c.startswith("SH") or c.startswith("BJ"):
        return c[2:]
    return c


def _analyze_mainline_auto() -> dict:
    if ak is None:
        return {"ok": False, "msg": "AkShare 不可用"}

    date = _bj_yyyymmdd()
    try:
        strong_df = _with_retries(lambda: ak.stock_zt_pool_strong_em(date=date))
    except Exception:
        return {"ok": False, "msg": "自动分析失败：强势池数据暂不可用"}

    if strong_df is None or strong_df.empty:
        return {"ok": False, "msg": "自动分析失败：强势池为空"}

    gainers = None
    gainers_source = "stock_hot_up_em"
    try:
        gainers = _with_retries(ak.stock_hot_up_em)
    except Exception:
        gainers = None

    if gainers is None or gainers.empty:
        try:
            gainers = _with_retries(ak.stock_hot_rank_em)
            gainers_source = "stock_hot_rank_em"
            if "股票名称" not in gainers.columns and "名称" in gainers.columns:
                gainers = gainers.rename(columns={"名称": "股票名称"})
        except Exception:
            gainers = None

    if gainers is None or gainers.empty:
        gainers_source = "stock_zt_pool_strong_em"
        gainers = strong_df.rename(columns={"名称": "股票名称"}).copy()

    gainers = gainers.copy()
    strong_df = strong_df.copy()
    gainers["涨跌幅"] = gainers["涨跌幅"].astype(float)
    strong_df["涨跌幅"] = strong_df["涨跌幅"].astype(float)
    strong_df["成交额"] = strong_df["成交额"].astype(float)
    gainers["_code"] = gainers["代码"].map(_normalize_code)
    strong_df["_code"] = strong_df["代码"].map(_normalize_code)

    top_gainers = gainers.sort_values("涨跌幅", ascending=False).head(30)
    top_turnover = strong_df.sort_values("成交额", ascending=False).head(30)

    industry_strength = {}
    for _, row in top_turnover.iterrows():
        ind = str(row.get("所属行业") or "未知").strip()
        val = float(row.get("成交额") or 0)
        pct = float(row.get("涨跌幅") or 0)
        if ind not in industry_strength:
            industry_strength[ind] = {"count": 0, "turnover": 0.0, "sum_pct": 0.0}
        industry_strength[ind]["count"] += 1
        industry_strength[ind]["turnover"] += val
        industry_strength[ind]["sum_pct"] += pct

    for ind, v in industry_strength.items():
        v["avg_pct"] = v["sum_pct"] / max(v["count"], 1)
        v["score"] = v["count"] * 2 + (v["turnover"] / 1e9) * 0.2 + max(v["avg_pct"], 0) * 0.8

    ranked_industries = sorted(industry_strength.items(), key=lambda x: x[1]["score"], reverse=True)
    if not ranked_industries:
        return {"ok": False, "msg": "未识别到主线板块"}

    mainline_sector, mainline_stats = ranked_industries[0]

    gainers_set = set(top_gainers["_code"].tolist())
    pool = top_turnover[top_turnover["所属行业"].astype(str).str.strip() == mainline_sector].copy()
    if pool.empty:
        pool = top_turnover.copy()

    pool["is_gainer"] = pool["_code"].map(lambda c: 1 if c in gainers_set else 0)
    pool["leader_score"] = (
        pool["成交额"].astype(float) / 1e8
        + pool["涨跌幅"].astype(float).clip(lower=0) * 2
        + pool["is_gainer"] * 6
    )
    leader = pool.sort_values("leader_score", ascending=False).iloc[0]

    concentration = mainline_stats["count"] / 30
    hot_strength = float(mainline_stats["avg_pct"])
    tradable = concentration >= 0.2 and hot_strength >= 2
    if tradable:
        suggestion = "值得参与，但建议围绕主线龙头和前排，分批介入，不追高尾盘加速。"
    elif concentration >= 0.16 or hot_strength >= 1.2:
        suggestion = "可轻仓试错，优先看分时转强和量能持续，不宜重仓。"
    else:
        suggestion = "暂不建议积极参与，主线不够清晰，先观察强度持续性。"

    return {
        "ok": True,
        "generated_at": _bj_datetime_str(),
        "mainline_sector": mainline_sector,
        "leader_stock": {
            "code": str(leader.get("代码")),
            "name": str(leader.get("名称")),
            "change_pct": round(float(leader.get("涨跌幅") or 0), 2),
            "turnover": int(float(leader.get("成交额") or 0)),
        },
        "tradable": tradable,
        "tradable_text": "值得参与" if tradable else "谨慎参与",
        "inputs_source": {
            "gainers": gainers_source,
            "turnover": "stock_zt_pool_strong_em",
        },
        "reason": (
            f"主线板块在成交额前排中占比约 {round(concentration * 100, 1)}%，"
            f"板块前排平均涨幅 {round(hot_strength, 2)}%。"
        ),
        "suggestion": suggestion,
        "sector_rank_top5": [
            {
                "sector": ind,
                "count": v["count"],
                "avg_pct": round(v["avg_pct"], 2),
                "turnover": int(v["turnover"]),
            }
            for ind, v in ranked_industries[:5]
        ],
        "samples": {
            "gainers_top": [
                {
                    "code": str(r.get("代码")),
                    "name": str(r.get("股票名称")),
                    "change_pct": round(float(r.get("涨跌幅") or 0), 2),
                }
                for _, r in top_gainers.head(10).iterrows()
            ],
            "turnover_top": [
                {
                    "code": str(r.get("代码")),
                    "name": str(r.get("名称")),
                    "sector": str(r.get("所属行业")),
                    "change_pct": round(float(r.get("涨跌幅") or 0), 2),
                    "turnover": int(float(r.get("成交额") or 0)),
                }
                for _, r in top_turnover.head(10).iterrows()
            ],
        },
    }


# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    return jsonify(_get_stocks_snapshot())

@app.route("/api/stocks", methods=["POST"])
def add_stock():
    body   = request.get_json(force=True)
    ticker = (body.get("ticker") or "").strip().upper()
    name   = (body.get("name")   or "").strip()
    if not ticker:
        abort(400, "ticker required")

    wl = load_watchlist()
    if any(s["ticker"] == ticker for s in wl):
        return jsonify({"ok": False, "msg": "已在列表中"}), 200

    # Validate via configured providers before writing to watchlist.
    test = fetch_stock(ticker, name)
    if test.get("error"):
        return jsonify({"ok": False, "msg": f"无法获取数据: {test['error']}"}), 200

    wl.append({"ticker": ticker, "name": name or test.get("name", ticker)})
    save_watchlist(wl)
    _invalidate_stocks_cache()
    return jsonify({"ok": True, "stock": test})

@app.route("/api/stocks/<path:ticker>", methods=["DELETE"])
def remove_stock(ticker):
    ticker = ticker.upper()
    wl     = load_watchlist()
    new_wl = [s for s in wl if s["ticker"] != ticker]
    if len(new_wl) == len(wl):
        abort(404, "not found")
    save_watchlist(new_wl)
    _invalidate_stocks_cache()
    return jsonify({"ok": True})

@app.route("/api/refresh/<path:ticker>")
def refresh_one(ticker):
    wl   = load_watchlist()
    name = next((s.get("name","") for s in wl if s["ticker"]==ticker.upper()), "")
    data = fetch_stock(ticker.upper(), name)
    _invalidate_stocks_cache()
    return jsonify(data)


# ── Sparkline history endpoint ───────────────────────────────────────────────
_HISTORY_CACHE: dict = {}
_HISTORY_CACHE_TTL = 3600  # 1 hour

@app.route("/api/history/<path:ticker>")
def history(ticker):
    """Return last N trading days of close prices for sparkline rendering."""
    ticker = ticker.upper()
    days = min(int(request.args.get("days", 20)), 60)
    now = time.time()
    cache_key = f"{ticker}_{days}"
    cached = _HISTORY_CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < _HISTORY_CACHE_TTL:
        return jsonify(cached["data"])

    closes = _fetch_history_closes(ticker, days)
    result = {"ok": bool(closes), "ticker": ticker, "closes": closes}
    _HISTORY_CACHE[cache_key] = {"data": result, "ts": now}
    return jsonify(result)


def _fetch_history_closes(ticker: str, days: int) -> list[float]:
    """Fetch recent close prices via Sina daily K-line API."""
    if not _is_a_share_ticker(ticker):
        return []
    try:
        symbol = _ticker_to_sina_symbol(ticker)
        api = (
            f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen={days}"
        )
        req = urlrequest.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urlrequest.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        data = json.loads(raw)
        if not data:
            return []
        return [round(float(d["close"]), 2) for d in data if d.get("close")]
    except Exception:
        return []


@app.route("/api/quickread", methods=["POST"])
def quickread():
    body = request.get_json(force=True) or {}
    text = (body.get("text") or "").strip()
    return jsonify(_quickread_news(text))


@app.route("/api/macro-impact", methods=["POST"])
def macro_impact():
    body = request.get_json(force=True) or {}
    indicator = body.get("indicator")
    try:
        current = float(body.get("current")) if body.get("current") is not None else None
        previous = float(body.get("previous")) if body.get("previous") is not None else None
    except Exception:
        return jsonify({"ok": False, "msg": "current/previous 必须是数字"})
    return jsonify(_macro_impact(indicator, current, previous))


@app.route("/api/glossary", methods=["GET"])
def glossary():
    term = (request.args.get("term") or "").strip().lower()
    if not term:
        return jsonify({"ok": True, "terms": sorted(GLOSSARY.keys())})
    return jsonify({
        "ok": term in GLOSSARY,
        "term": term,
        "plain": GLOSSARY.get(term, "未收录该术语，可尝试：cpi, ppi, bps, eps, pe, pb, roe, beta, fomc"),
    })


@app.route("/api/auto-brief", methods=["GET"])
def auto_brief():
    refresh_flag = (request.args.get("refresh") or "").strip().lower()
    force_refresh = refresh_flag in {"1", "true", "yes", "y"}
    return jsonify(_build_auto_brief(force_refresh=force_refresh))


# ── Short-termer dashboard: limit stats + yesterday performance ──────────────

_LIMIT_STATS_CACHE: dict | None = None
_LIMIT_STATS_CACHE_TS: float = 0.0
_LIMIT_STATS_CACHE_TTL = 300  # 5 min

def _get_limit_stats() -> dict:
    """Return limit-up/down counts, consecutive board stats, and yesterday limit-up
    performance using AkShare pool endpoints. Results cached 5 min."""
    global _LIMIT_STATS_CACHE, _LIMIT_STATS_CACHE_TS

    now = time.time()
    if _LIMIT_STATS_CACHE and (now - _LIMIT_STATS_CACHE_TS) < _LIMIT_STATS_CACHE_TTL:
        return _LIMIT_STATS_CACHE

    date = _bj_yyyymmdd()
    result: dict = {
        "ok": True,
        "date": date,
        "limit_up": None,
        "limit_down": None,
        "consecutive_boards": None,
        "max_board": None,
        "yesterday_limit_up_performance": None,
    }

    if ak is None:
        result["ok"] = False
        result["error"] = "AkShare 不可用"
        return result

    # 1) Today's limit-up pool
    try:
        zt_df = _with_retries(lambda: ak.stock_zt_pool_em(date=date))
        if zt_df is not None and not zt_df.empty:
            result["limit_up"] = len(zt_df)
            if "连板数" in zt_df.columns:
                boards = zt_df["连板数"].fillna(0).astype(int)
                result["consecutive_boards"] = int((boards >= 2).sum())
                result["max_board"] = int(boards.max())
    except Exception:
        pass

    # 2) Today's limit-down pool
    try:
        dt_df = _with_retries(lambda: ak.stock_zt_pool_dtgc_em(date=date))
        if dt_df is not None and not dt_df.empty:
            result["limit_down"] = len(dt_df)
    except Exception:
        pass

    # 3) Yesterday's limit-up performance today
    try:
        zrzt_df = _with_retries(lambda: ak.stock_zt_pool_previous_em(date=date))
        if zrzt_df is not None and not zrzt_df.empty:
            # This endpoint returns stocks that hit limit-up yesterday with today's performance
            total = len(zrzt_df)
            chg_col = None
            for c in ["涨跌幅", "今日涨跌幅"]:
                if c in zrzt_df.columns:
                    chg_col = c
                    break

            if chg_col:
                changes = zrzt_df[chg_col].fillna(0).astype(float)
                up = int((changes > 0).sum())
                down = int((changes < 0).sum())
                flat = total - up - down
                avg_chg = round(float(changes.mean()), 2)

                # Profitability rate: how many stay positive
                profit_rate = round(up / total * 100, 1) if total > 0 else 0

                result["yesterday_limit_up_performance"] = {
                    "total": total,
                    "up": up,
                    "down": down,
                    "flat": flat,
                    "avg_change_pct": avg_chg,
                    "profit_rate": profit_rate,
                    "verdict": (
                        "短线接力环境好" if profit_rate >= 60 and avg_chg > 1
                        else "短线环境中性" if profit_rate >= 40
                        else "短线周期走弱，谨慎追高"
                    ),
                }
    except Exception:
        pass

    _LIMIT_STATS_CACHE = result
    _LIMIT_STATS_CACHE_TS = now
    return result


@app.route("/api/limit-stats", methods=["GET"])
def limit_stats():
    return jsonify(_get_limit_stats())


@app.route("/api/sentiment-config", methods=["GET"])
def get_sentiment_config():
    return jsonify({"ok": True, "thresholds": SENTIMENT_THRESHOLDS})


@app.route("/api/sentiment-config", methods=["POST"])
def set_sentiment_config():
    body = request.get_json(force=True) or {}
    allowed_keys = set(SENTIMENT_THRESHOLDS.keys())
    for k, v in body.items():
        if k in allowed_keys:
            SENTIMENT_THRESHOLDS[k] = float(v)
    _save_sentiment_config()
    return jsonify({"ok": True, "thresholds": SENTIMENT_THRESHOLDS})


@app.route("/api/market-sentiment", methods=["POST"])
def market_sentiment():
    body = request.get_json(force=True) or {}
    try:
        up_count = int(body.get("up_count"))
        down_count = int(body.get("down_count"))
        limit_up_count = int(body.get("limit_up_count"))
        consecutive_limit_count = int(body.get("consecutive_limit_count"))
    except Exception:
        return jsonify({"ok": False, "msg": "四个输入都必须是整数"})

    _update_sentiment_last_known({
        "up_count": up_count,
        "down_count": down_count,
        "limit_up_count": limit_up_count,
        "consecutive_limit_count": consecutive_limit_count,
    })

    result = _evaluate_market_sentiment(
        up_count,
        down_count,
        limit_up_count,
        consecutive_limit_count,
    )
    _append_sentiment_history(result)
    return jsonify(result)


@app.route("/api/market-sentiment-auto", methods=["GET"])
def market_sentiment_auto():
    metrics_live = _get_market_sentiment_inputs_auto()
    _update_sentiment_last_known(metrics_live)
    metrics, fallback_fields = _merge_with_last_known(metrics_live)
    missing = [k for k, v in metrics.items() if v is None]
    if missing:
        return jsonify({
            "ok": False,
            "msg": f"自动抓取不完整，缺少: {', '.join(missing)}",
            "inputs": metrics_live,
            "last_known": SENTIMENT_LAST_KNOWN,
        })

    result = _evaluate_market_sentiment(
        metrics["up_count"],
        metrics["down_count"],
        metrics["limit_up_count"],
        metrics["consecutive_limit_count"],
    )
    result["inputs_source"] = {
        "up_down": "iwencai",
        "limit_up": "akshare.stock_zt_pool_em",
    }
    if fallback_fields:
        result["fallback_fields"] = fallback_fields
        result["fallback_note"] = f"以下字段使用最近一次可用值: {', '.join(fallback_fields)}"
        result["last_known_updated_at"] = SENTIMENT_LAST_KNOWN.get("updated_at")
    _append_sentiment_history(result)
    return jsonify(result)


@app.route("/api/sentiment-history", methods=["GET"])
def sentiment_history():
    days = request.args.get("days", "30")
    try:
        days = int(days)
    except ValueError:
        days = 30
    history = _load_sentiment_history()
    # Return the last N days (approx: 24 entries/day max)
    return jsonify({"ok": True, "history": history[-(days * 24):]})


@app.route("/api/mainline-auto", methods=["GET"])
def mainline_auto():
    try:
        return jsonify(_analyze_mainline_auto())
    except Exception as e:
        return jsonify({"ok": False, "msg": f"自动分析失败: {e}"})


@app.route("/api/ai-edge", methods=["GET"])
def ai_edge():
    refresh_flag = (request.args.get("refresh") or "").strip().lower()
    force_refresh = refresh_flag in {"1", "true", "yes", "y"}
    return jsonify(_build_ai_edge_report(force_refresh=force_refresh))


@app.route("/api/config/export", methods=["GET"])
def config_export():
    """Export watchlist as a downloadable JSON config file."""
    try:
        watchlist = json.loads(WATCHLIST.read_text(encoding="utf-8")) if WATCHLIST.exists() else []
    except Exception:
        watchlist = []
    payload = {"watchlist": watchlist, "exported_at": BeijingTime.now_str()}
    return app.response_class(
        json.dumps(payload, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=yykanpan_config.json"},
    )


@app.route("/api/config/import", methods=["POST"])
def config_import():
    """Import a previously exported config JSON (watchlist + positions)."""
    data = request.get_json(silent=True)
    if not data or "watchlist" not in data:
        return jsonify({"ok": False, "msg": "无效的配置文件"})
    watchlist = data["watchlist"]
    if not isinstance(watchlist, list):
        return jsonify({"ok": False, "msg": "watchlist 格式无效"})
    # Validate each entry
    for entry in watchlist:
        if not isinstance(entry, dict) or "ticker" not in entry:
            return jsonify({"ok": False, "msg": "watchlist 条目缺少 ticker 字段"})
    try:
        WATCHLIST.write_text(json.dumps(watchlist, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        return jsonify({"ok": False, "msg": f"保存失败: {e}"})
    return jsonify({"ok": True, "count": len(watchlist)})


# ── Serve frontend ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


if __name__ == "__main__":
    print("Starting Stock Tracker -> http://localhost:5000")
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host=host, debug=debug, port=5000)
