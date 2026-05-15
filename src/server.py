"""
app.py — Daily Stock Tracker Web App
Serves the frontend and provides a JSON API backed by AkShare-first data.

Run:
    python src/app.py
Then open http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory, abort
import pathlib
import json
import csv
import time
import re
import os
import logging
import threading
from datetime import datetime, timedelta
from urllib import request as urlrequest
from urllib import parse as urlparse
from config import cfg, load_watchlist, save_watchlist, DEFAULT_STOCKS
from time_utils import BeijingTime
from data.providers import (
    fetch_stock_yahoo as _fetch_stock_yahoo,
    fetch_stock_akshare as _fetch_stock_akshare,
    fetch_stock_sina as _fetch_stock_sina,
    is_a_share_ticker as _is_a_share_ticker,
    with_retries as _with_retries,
    _ticker_to_a_share_code,
    _ticker_to_sina_symbol,
    _fetch_52w,
)
from trading import decision as dec
from analysis import advisor as adv
from analysis import quant
from analysis import screener
from tools.bazi_core import (
    BaziCalculator, get_bazi_data, get_lunar_date_string, get_solar_term_info,
    calc_wuyun_liuqi,
)

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
STATIC_DIR  = cfg.STATIC_DIR
WATCHLIST   = cfg.WATCHLIST_PATH
SENTIMENT_CACHE_FILE = cfg.SENTIMENT_CACHE_PATH

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    template_folder=str(STATIC_DIR),
)

# Keep a short-lived in-memory cache for the stocks snapshot.
STOCKS_CACHE_DATA = None
STOCKS_CACHE_TS = 0.0
STOCKS_CACHE_TTL_SECONDS = cfg.STOCKS_CACHE_TTL_SECONDS

NEWS_FEEDS = cfg.NEWS_FEEDS
SENTIMENT_LAST_KNOWN = dict(cfg.SENTIMENT_DEFAULTS)

# ── Configurable sentiment thresholds ────────────────────────────────────────
SENTIMENT_THRESHOLDS = dict(cfg.SENTIMENT_THRESHOLDS)
_SENTIMENT_CONFIG_FILE = cfg.SENTIMENT_CONFIG_PATH

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
_SENTIMENT_HISTORY_FILE = cfg.SENTIMENT_HISTORY_PATH

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
            json.dumps(history[-cfg.SENTIMENT_HISTORY_MAX_ENTRIES:], ensure_ascii=False, indent=2),
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



# ── Market-hours & CSV persistence ────────────────────────────────────────────
# Chinese A-share market holidays 2026 (weekends handled separately).
_CN_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-02",
    "2026-01-26", "2026-01-27", "2026-01-28", "2026-01-29", "2026-01-30",
    "2026-02-02", "2026-02-03", "2026-02-04", "2026-02-05", "2026-02-06",
    "2026-04-04", "2026-04-05", "2026-04-06",
    "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05",
    "2026-06-19", "2026-06-20", "2026-06-21",
    "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05",
    "2026-10-06", "2026-10-07", "2026-10-08",
}

_CSV_FIELDS = [
    "ticker", "name", "price", "prev_close", "change", "change_pct",
    "volume", "market_cap", "high52", "low52", "date", "source", "error",
]
_CSV_KEEP_DAYS = 5


def _is_cn_trading_session() -> bool:
    """True when Beijing time is within A-share continuous trading window
    on a trading day (weekday + non-holiday), roughly 09:15–15:30 UTC+8."""
    now = _bj_now()
    dow = now.weekday()  # Mon=0 .. Sun=6
    if dow >= 5:
        return False
    if now.strftime("%Y-%m-%d") in _CN_HOLIDAYS_2026:
        return False
    minutes = now.hour * 60 + now.minute
    return (9 * 60 + 15) <= minutes <= (15 * 60 + 30)


def _save_stocks_csv(data: list[dict]) -> None:
    """Persist the latest successful snapshot to data/YYYY-MM-DD.csv."""
    valid = [r for r in data if not r.get("error")]
    if not valid:
        return
    data_dir = cfg.DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    out_file = data_dir / f"{_bj_date_str()}.csv"
    try:
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(valid)
        # Cleanup old files
        csv_files = sorted(
            [p for p in data_dir.glob("*.csv") if len(p.stem) == 10],
            key=lambda p: p.stem, reverse=True,
        )
        for old in csv_files[_CSV_KEEP_DAYS:]:
            old.unlink(missing_ok=True)
    except Exception:
        pass


def _load_latest_csv() -> list[dict] | None:
    """Load the most recent daily CSV from data/. Returns None if unavailable."""
    data_dir = cfg.DATA_DIR
    if not data_dir.exists():
        return None
    csv_files = sorted(
        [p for p in data_dir.glob("*.csv") if len(p.stem) == 10],
        key=lambda p: p.stem, reverse=True,
    )
    if not csv_files:
        return None
    try:
        with open(csv_files[0], newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                # Convert numeric fields back from strings
                for k in ("price", "prev_close", "change", "change_pct", "high52", "low52"):
                    if row.get(k):
                        try:
                            row[k] = float(row[k])
                        except (ValueError, TypeError):
                            row[k] = None
                    else:
                        row[k] = None
                for k in ("volume", "market_cap"):
                    if row.get(k):
                        try:
                            row[k] = int(float(row[k]))
                        except (ValueError, TypeError):
                            row[k] = None
                    else:
                        row[k] = None
                # Normalize empty error to None
                if not row.get("error"):
                    row["error"] = None
                rows.append(row)
        return rows if rows else None
    except Exception:
        return None


def _invalidate_stocks_cache() -> None:
    global STOCKS_CACHE_DATA, STOCKS_CACHE_TS
    STOCKS_CACHE_DATA = None
    STOCKS_CACHE_TS = 0.0


def _backfill_52w(rows: list[dict]) -> None:
    """Fill in missing 52-week high/low via Sina K-line for CSV-loaded rows."""
    for row in rows:
        if row.get("high52") is None and _is_a_share_ticker(row.get("ticker", "")):
            h, l = _fetch_52w(row["ticker"])
            row["high52"] = h
            row["low52"] = l


_stocks_lock = threading.Lock()

def _get_stocks_snapshot(force_refresh: bool = False) -> list[dict]:
    global STOCKS_CACHE_DATA, STOCKS_CACHE_TS

    now = time.time()
    if (
        not force_refresh
        and STOCKS_CACHE_DATA is not None
        and (now - STOCKS_CACHE_TS) <= STOCKS_CACHE_TTL_SECONDS
    ):
        return STOCKS_CACHE_DATA

    # Serialize heavy fetches so only one thread scans at a time
    with _stocks_lock:
        # Double-check after acquiring lock
        now = time.time()
        if (
            not force_refresh
            and STOCKS_CACHE_DATA is not None
            and (now - STOCKS_CACHE_TS) <= STOCKS_CACHE_TTL_SECONDS
        ):
            return STOCKS_CACHE_DATA

        # Outside trading hours → serve last saved CSV (avoids slow/empty fetches)
        # If no CSV exists, fall through to live fetch so we get real data.
        if not _is_cn_trading_session():
            cached_csv = _load_latest_csv()
            if cached_csv:
                _backfill_52w(cached_csv)
                STOCKS_CACHE_DATA = cached_csv
                STOCKS_CACHE_TS = now
                return STOCKS_CACHE_DATA

        wl = load_watchlist()

        # Run live fetch in a background thread with a 30-second timeout.
        # If it doesn't finish in time, fall back to the latest CSV.
        fetch_result = [None]

        def _do_fetch():
            fetch_result[0] = [fetch_stock(s["ticker"], s.get("name", "")) for s in wl]

        t = threading.Thread(target=_do_fetch, daemon=True)
        t.start()
        t.join(timeout=cfg.LIVE_FETCH_TIMEOUT_SECONDS)

        if fetch_result[0] is not None:
            data = fetch_result[0]
            STOCKS_CACHE_DATA = data
            STOCKS_CACHE_TS = now
            _save_stocks_csv(data)
            return data

        # Live fetch timed out — fall back to CSV
        cached_csv = _load_latest_csv()
        if cached_csv:
            _backfill_52w(cached_csv)
            STOCKS_CACHE_DATA = cached_csv
            STOCKS_CACHE_TS = now
            return STOCKS_CACHE_DATA

        # No CSV either — return placeholders
        STOCKS_CACHE_DATA = [
            {"ticker": s["ticker"], "name": s.get("name", s["ticker"]),
             "price": None, "prev_close": None, "change": None,
             "change_pct": None, "volume": None, "high52": None,
             "low52": None, "market_cap": None, "date": None,
             "source": "offline", "error": "实时数据超时，暂无历史数据"}
            for s in wl
        ]
        STOCKS_CACHE_TS = now
        return STOCKS_CACHE_DATA


def _generate_stock_suggestion(s: dict) -> dict | None:
    """Rule-based suggestion for a single stock row.

    Returns {"action": "买入"/"卖出"/"持有"/"观望",
             "tip": str, "target": float|None, "stop": float|None}
    or None if data is insufficient.
    """
    price = s.get("price")
    if not price or s.get("error"):
        return None

    change_pct = s.get("change_pct") or 0
    high52 = s.get("high52")
    low52 = s.get("low52")
    prev_close = s.get("prev_close") or price

    tips = []
    score = 0  # positive = bullish, negative = bearish

    # ── 52-week position ──────────────────────────────────────────────────
    if high52 and low52 and high52 > low52:
        range52 = high52 - low52
        pos52 = (price - low52) / range52  # 0 = at low, 1 = at high

        if pos52 >= 0.95:
            tips.append("接近52周新高，注意追高风险")
            score -= 1
        elif pos52 >= 0.80:
            tips.append("处于52周高位区间")
        elif pos52 <= 0.10:
            tips.append("接近52周新低，可能超卖")
            score += 1
        elif pos52 <= 0.25:
            tips.append("处于52周低位区间")
            score += 0.5

        # Target / stop based on 52-week range
        target = round(price + range52 * 0.15, 2) if pos52 < 0.85 else None
        stop = round(price - range52 * 0.10, 2) if pos52 > 0.15 else None
    else:
        target = None
        stop = None

    # ── Intraday momentum ─────────────────────────────────────────────────
    if change_pct >= 5:
        tips.append("放量大涨，关注是否突破")
        score += 1
    elif change_pct >= 2:
        tips.append("涨势良好")
        score += 0.5
    elif change_pct <= -5:
        tips.append("大幅下跌，谨慎操作")
        score -= 1
    elif change_pct <= -2:
        tips.append("弱势回调")
        score -= 0.5

    # ── Support / resistance proximity ────────────────────────────────────
    if prev_close and price:
        gap_pct = abs(price - prev_close) / prev_close * 100
        if gap_pct < 0.3:
            tips.append("窄幅震荡，等待方向")

    # ── Action recommendation ─────────────────────────────────────────────
    if score >= 1.5:
        action = "买入"
    elif score >= 0.5:
        action = "持有"
    elif score <= -1.5:
        action = "卖出"
    elif score <= -0.5:
        action = "观望"
    else:
        action = "持有"

    if not tips:
        tips.append("暂无明显信号")

    return {
        "action": action,
        "tip": "；".join(tips),
        "target": target,
        "stop": stop,
    }


# ── Provider preference ──────────────────────────────────────────────────────
_PROVIDER_FUNCS = {
    "sina": _fetch_stock_sina,
    "akshare": _fetch_stock_akshare,
    "yahoo": _fetch_stock_yahoo,
}
_A_SHARE_DEFAULT_ORDER = ["sina", "akshare", "yahoo"]
_preferred_provider_order: list[str] = list(_A_SHARE_DEFAULT_ORDER)


def _test_providers(ticker: str = "600519.SS", name: str = "贵州茅台") -> list[dict]:
    """Test all providers with a sample ticker, return timing and status."""
    results = []
    for pname in ["sina", "akshare", "yahoo"]:
        fn = _PROVIDER_FUNCS[pname]
        t0 = time.time()
        try:
            r = fn(ticker, name)
            elapsed = round(time.time() - t0, 2)
            ok = r.get("price") is not None and not r.get("error")
            results.append({
                "provider": pname,
                "ok": ok,
                "time_s": elapsed,
                "price": r.get("price"),
                "error": r.get("error"),
            })
        except Exception as e:
            elapsed = round(time.time() - t0, 2)
            results.append({
                "provider": pname,
                "ok": False,
                "time_s": elapsed,
                "price": None,
                "error": str(e),
            })
    return results


def fetch_stock(ticker: str, name: str = "") -> dict:
    """
    Fetch a stock snapshot.
    Strategy:
    1) For A-shares: try providers in _preferred_provider_order.
    2) For non A-shares: Yahoo only.
    """
    if _is_a_share_ticker(ticker):
        errors = {}
        for pname in _preferred_provider_order:
            fn = _PROVIDER_FUNCS[pname]
            result = fn(ticker, name)
            if not result.get("error"):
                return result
            errors[pname] = result.get("error")

        # All failed — return last result with combined error
        result["error"] = " | ".join(f"{k}失败: {v}" for k, v in errors.items())
        return result

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
                with urlrequest.urlopen(req, timeout=cfg.NEWS_FEED_TIMEOUT) as resp:
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
    url = f"{cfg.IWENCAI_URL}?w={urlparse.quote(keyword)}"
    req = urlrequest.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        def _download():
            with urlrequest.urlopen(req, timeout=cfg.IWENCAI_TIMEOUT) as resp:
                return resp.read().decode("utf-8", errors="ignore")

        text = _with_retries(_download)
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            return None
        return int(m.group(1))
    except Exception:
        return None


def _fetch_up_down_akshare() -> tuple[int | None, int | None]:
    """Fetch up/down counts via ak.stock_market_activity_legu()."""
    if ak is None:
        return None, None
    try:
        df = _with_retries(lambda: ak.stock_market_activity_legu())
        lookup = dict(zip(df["item"], df["value"]))
        up = int(lookup["上涨"]) if "上涨" in lookup else None
        down = int(lookup["下跌"]) if "下跌" in lookup else None
        return up, down
    except Exception:
        return None, None


def _get_market_sentiment_inputs_auto() -> dict:
    """Auto-fetch four metrics: up/down count, limit-up count, and consecutive-board count."""
    if not _is_cn_trading_session():
        return {"up_count": None, "down_count": None,
                "limit_up_count": None, "consecutive_limit_count": None}

    up_count, down_count = _fetch_up_down_akshare()

    # Fallback to iWenCai if AkShare failed
    if up_count is None:
        up_count = _fetch_iwencai_count("上涨家数", r"涨跌幅>0%\s*\((\d+)个\)")
    if down_count is None:
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
    if not _is_cn_trading_session():
        return {"ok": False, "msg": "休市中，暂无实时主线数据"}

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
    rows = _get_stocks_snapshot()
    _backfill_52w(rows)
    for row in rows:
        row["suggest"] = _generate_stock_suggestion(row)
    return jsonify(rows)

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


# ── Technical signals endpoint ─────────────────────────────────────────────────

def _fetch_history_ohlcv(ticker: str, days: int = 80) -> list[dict]:
    """Fetch recent OHLCV bars via Sina daily K-line API."""
    if not _is_a_share_ticker(ticker):
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
        return [
            {
                "day": d["day"],
                "open": float(d["open"]),
                "high": float(d["high"]),
                "low": float(d["low"]),
                "close": float(d["close"]),
                "volume": float(d["volume"]),
            }
            for d in data
            if d.get("close")
        ]
    except Exception:
        return []


_SIGNALS_CACHE: dict = {}
_SIGNALS_CACHE_TTL = 300  # 5 min

@app.route("/api/signals/<path:ticker>")
def signals(ticker):
    """Return technical indicators + trading signals for a stock."""
    ticker = ticker.upper()
    now = time.time()
    cached = _SIGNALS_CACHE.get(ticker)
    if cached and (now - cached["ts"]) < _SIGNALS_CACHE_TTL:
        return jsonify(cached["data"])

    bars = _fetch_history_ohlcv(ticker, 80)
    if not bars:
        return jsonify({"ok": False, "ticker": ticker, "msg": "无历史数据"})

    opens = [b["open"] for b in bars]
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]
    closes = [b["close"] for b in bars]
    volumes = [b["volume"] for b in bars]

    result = quant.generate_signals(opens, highs, lows, closes, volumes)
    result["ok"] = True
    result["ticker"] = ticker
    result["last_price"] = closes[-1] if closes else None
    result["last_day"] = bars[-1]["day"] if bars else None

    _SIGNALS_CACHE[ticker] = {"data": result, "ts": now}
    return jsonify(result)


# ── Stock screener endpoints ──────────────────────────────────────────────────

@app.route("/api/screener/strategies")
def screener_strategies():
    """List available screening strategies."""
    return jsonify({"ok": True, "strategies": screener.list_strategies()})


@app.route("/api/screener")
def screener_scan():
    """Run a screening strategy. ?strategy=golden_cross&limit=20"""
    strategy = request.args.get("strategy", "golden_cross")
    limit = min(int(request.args.get("limit", "20")), 50)
    result = screener.run_screen(strategy, limit)
    return jsonify(result)


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

    if not _is_cn_trading_session():
        return _LIMIT_STATS_CACHE or {"ok": False, "msg": "休市中，暂无实时数据"}

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
        # During non-trading hours, return last known result if history exists
        if not _is_cn_trading_session():
            history = _load_sentiment_history()
            if history:
                last = history[-1]
                return jsonify({
                    "ok": True,
                    "stage": last.get("stage", ""),
                    "tradable": last.get("stage") == "上升",
                    "tradable_text": "适合交易" if last.get("stage") == "上升" else "暂不适合积极交易",
                    "metrics": {"score": last.get("score", 0), "up_ratio": last.get("up_ratio")},
                    "inputs": last.get("inputs", {}),
                    "reasons": [],
                    "plain": f"休市中，显示最近交易日数据：情绪处于{last.get('stage', '未知')}阶段",
                    "fallback_note": f"休市中，数据来自 {last.get('ts', '未知时间')}",
                    "last_known_updated_at": last.get("ts"),
                })
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
        "up_down": "akshare.stock_market_activity_legu",
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
    payload = {"watchlist": watchlist, "exported_at": BeijingTime.datetime_str()}
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


# ── Macro indicators (宏观指标) ───────────────────────────────────────────────

_MACRO_SYMBOLS = "sh000001,fx_susdcny,hf_GC,hf_CL"
_MACRO_CACHE: dict | None = None
_MACRO_CACHE_TS: float = 0
_MACRO_CACHE_TTL = 60  # seconds


def _fetch_macro_indicators() -> list[dict]:
    """Fetch key macro indicators from Sina in one HTTP call."""
    global _MACRO_CACHE, _MACRO_CACHE_TS
    now = time.time()
    if _MACRO_CACHE is not None and (now - _MACRO_CACHE_TS) <= _MACRO_CACHE_TTL:
        return _MACRO_CACHE

    url = f"{cfg.SINA_QUOTE_API_URL}{_MACRO_SYMBOLS}"
    req = urlrequest.Request(url, headers={
        "Referer": "https://finance.sina.com.cn",
        "User-Agent": "Mozilla/5.0",
    })
    try:
        with urlrequest.urlopen(req, timeout=cfg.SINA_QUOTE_TIMEOUT) as resp:
            raw = resp.read().decode("gbk", errors="replace")
    except Exception as e:
        return [{"name": "Error", "error": str(e)}]

    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or '="' not in line:
            continue
        key_part = line.split("=")[0]  # var hq_str_XXXX
        symbol = key_part.rsplit("_", 1)[-1] if "_" in key_part else key_part
        fields = line.split('"')[1].split(",") if '"' in line else []
        if not fields:
            continue

        try:
            if symbol == "sh000001":
                # Shanghai index: [0]=name [1]=open [2]=prev_close [3]=price
                # [4]=high [5]=low ... [8]=volume [9]=turnover
                name = fields[0] or "上证指数"
                price = float(fields[3])
                prev = float(fields[2])
                change = round(price - prev, 2)
                pct = round(change / prev * 100, 2) if prev else 0
                results.append({"symbol": "sh000001", "name": name,
                                "price": price, "prev": prev,
                                "change": change, "change_pct": pct, "unit": ""})

            elif "susdcny" in symbol:
                # Forex: [0]=time [1]=prev_close ... [5]=price (buy)
                price = float(fields[5])
                prev = float(fields[1])
                change = round(price - prev, 4)
                pct = round(change / prev * 100, 2) if prev else 0
                results.append({"symbol": "fx_susdcny", "name": "美元/人民币",
                                "price": round(price, 4), "prev": round(prev, 4),
                                "change": change, "change_pct": pct, "unit": ""})

            elif symbol == "GC":
                # Gold COMEX: [0]=price ... [7]=prev_settlement
                price = float(fields[0])
                prev = float(fields[7])
                change = round(price - prev, 2)
                pct = round(change / prev * 100, 2) if prev else 0
                results.append({"symbol": "hf_GC", "name": "黄金(COMEX)",
                                "price": price, "prev": prev,
                                "change": change, "change_pct": pct, "unit": "$/oz"})

            elif symbol == "CL":
                # Oil WTI: [0]=price ... [7]=prev_settlement
                price = float(fields[0])
                prev = float(fields[7])
                change = round(price - prev, 2)
                pct = round(change / prev * 100, 2) if prev else 0
                results.append({"symbol": "hf_CL", "name": "原油(WTI)",
                                "price": price, "prev": prev,
                                "change": change, "change_pct": pct, "unit": "$/bbl"})
        except (IndexError, ValueError):
            continue

    _MACRO_CACHE = results
    _MACRO_CACHE_TS = time.time()
    return results


@app.route("/api/macro", methods=["GET"])
def macro():
    data = _fetch_macro_indicators()
    return jsonify(data)


# ── Macro history (宏观指标走势) ──────────────────────────────────────────────

_MACRO_HISTORY_CACHE: dict = {}
_MACRO_HISTORY_TTL = 3600  # 1 hour

_MACRO_SYMBOL_MAP = {
    "sh000001": "sh000001",
    "fx_susdcny": "fx_susdcny",
    "hf_GC": "hf_GC",
    "hf_CL": "hf_CL",
}


def _fetch_macro_history(symbol: str, days: int = 20) -> list[float]:
    """Fetch recent close prices for a macro symbol."""
    now = time.time()
    cache_key = f"{symbol}_{days}"
    cached = _MACRO_HISTORY_CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < _MACRO_HISTORY_TTL:
        return cached["closes"]

    closes: list[float] = []
    try:
        if symbol == "sh000001":
            # Shanghai index: use Sina K-line (same as stock history)
            api = (
                f"{cfg.SINA_KLINE_API_URL}"
                f"?symbol=sh000001&scale=240&ma=no&datalen={days}"
            )
            req = urlrequest.Request(api, headers={"User-Agent": "Mozilla/5.0"})
            with urlrequest.urlopen(req, timeout=cfg.SINA_KLINE_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)
            closes = [round(float(d["close"]), 2) for d in data if d.get("close")]

        elif symbol.startswith("fx_"):
            # Forex: Sina forex daily K-line (returns pipe-delimited CSV)
            pair = symbol.replace("fx_s", "").upper()  # "USDCNY"
            api = (
                f"https://vip.stock.finance.sina.com.cn/forex/api/jsonp.php"
                f"/data/NewForexService.getDayKLine?symbol={pair}"
            )
            req = urlrequest.Request(api, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.sina.com.cn",
            })
            with urlrequest.urlopen(req, timeout=cfg.SINA_KLINE_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            # Response: data("date,open,low,high,close,|date,...")
            # Extract the string between data(" and ")
            start = raw.index('("') + 2
            end = raw.rindex('")')
            csv_str = raw[start:end]
            bars = [b.strip() for b in csv_str.split("|") if b.strip()]
            all_closes = []
            for bar in bars:
                parts = bar.split(",")
                if len(parts) >= 5:
                    all_closes.append(round(float(parts[4]), 4))
            closes = all_closes[-days:]

        elif symbol.startswith("hf_"):
            # Commodities: Sina futures daily K-line
            code = symbol.replace("hf_", "")  # "GC" or "CL"
            api = (
                f"https://stock2.finance.sina.com.cn/futures/api/jsonp.php"
                f"/data/GlobalFuturesService.getGlobalFuturesDailyKLine"
                f"?symbol={code}"
            )
            req = urlrequest.Request(api, headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.sina.com.cn",
            })
            with urlrequest.urlopen(req, timeout=cfg.SINA_KLINE_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
            json_str = raw[raw.index("["):raw.rindex("]") + 1]
            data = json.loads(json_str)
            closes = [round(float(d["close"]), 2) for d in data[-days:] if d.get("close")]

    except Exception as e:
        logging.warning("macro-history %s failed: %s", symbol, e)
        return []

    _MACRO_HISTORY_CACHE[cache_key] = {"closes": closes, "ts": now}
    return closes


@app.route("/api/macro-history/<path:symbol>")
def macro_history(symbol):
    """Return recent closes for a macro indicator for sparkline rendering."""
    if symbol not in _MACRO_SYMBOL_MAP:
        return jsonify({"ok": False, "error": "unknown symbol"}), 400
    days = min(int(request.args.get("days", 20)), 260)
    closes = _fetch_macro_history(symbol, days)
    return jsonify({"ok": bool(closes), "symbol": symbol, "closes": closes})


# ── Risk events (黑天鹅 / 灰犀牛) ────────────────────────────────────────────

_RISK_EVENT_HISTORY: list[dict] = []  # in-memory event log

# Keyword rules for auto-detecting major news from CLS/CCTV feeds.
# Each rule: (keywords_any, type, severity, direction, source, duration, affected_sectors)
_NEWS_KEYWORD_RULES = [
    # Geopolitical — foreign leaders visiting China
    (["访华", "国事访问", "元首会晤", "首脑会谈"],
     "灰犀牛", "medium", "ambiguous", "geopolitical", "short", ["消费", "军工", "科技"]),
    # Trade war / tariffs
    (["贸易战", "加征关税", "关税壁垒", "贸易摩擦", "贸易制裁"],
     "灰犀牛", "high", "bearish", "geopolitical", "medium", ["出口", "科技", "农业"]),
    # Chip / tech sanctions
    (["芯片制裁", "芯片禁令", "实体清单", "出口管制", "技术封锁"],
     "灰犀牛", "high", "bearish", "geopolitical", "long", ["半导体", "科技"]),
    # Monetary policy — rate cut / RRR cut
    (["降准", "降息", "下调存款准备金", "LPR下调"],
     "灰犀牛", "medium", "bullish", "policy", "medium", ["银行", "地产", "券商"]),
    # Stamp duty
    (["印花税", "证券交易印花税"],
     "黑天鹅", "high", "bullish", "policy", "flash", ["券商", "全市场"]),
    # IPO policy
    (["IPO暂停", "暂缓IPO", "IPO收紧", "暂停新股发行"],
     "灰犀牛", "medium", "bullish", "policy", "short", ["券商", "次新股"]),
    # Real estate crisis
    (["暴雷", "债务违约", "停工停贷", "房企违约"],
     "灰犀牛", "high", "bearish", "sector", "medium", ["地产", "银行", "建材"]),
    # War / military conflict
    (["战争", "军事冲突", "武装冲突", "开战", "空袭"],
     "黑天鹅", "critical", "bearish", "external", "short", ["全市场", "军工", "黄金"]),
    # Pandemic
    (["疫情爆发", "新冠", "封城", "大流行"],
     "黑天鹅", "high", "bearish", "external", "long", ["全市场", "医药"]),
]


def _scan_news_events() -> list[dict]:
    """Scan CLS (财联社) flash news + CCTV news for keyword-matched events."""
    events = []
    if ak is None:
        return events

    now_str = _bj_now().strftime("%Y-%m-%d %H:%M")
    seen_titles: set[str] = set()

    # --- Source 1: CLS 财联社 real-time flash news ---
    try:
        df = _with_retries(lambda: ak.stock_info_global_cls())
        if df is not None and not df.empty:
            for _, row in df.head(30).iterrows():
                title = str(row.get("标题", ""))
                content = str(row.get("内容", ""))
                text = title + content

                for keywords, evt_type, severity, direction, source, duration, sectors in _NEWS_KEYWORD_RULES:
                    if any(kw in text for kw in keywords):
                        evt_title = title[:100] if title else content[:100]
                        if evt_title in seen_titles:
                            break
                        seen_titles.add(evt_title)
                        detail = content[:200] if content else ""
                        events.append({
                            "type": evt_type,
                            "source": source,
                            "severity": severity,
                            "direction": direction,
                            "duration": duration,
                            "title": evt_title,
                            "detail": detail,
                            "affected_sectors": sectors,
                            "time": now_str,
                            "auto_detected": True,
                        })
                        break
    except Exception:
        pass

    # --- Source 2: CCTV news (political / state visits / policy) ---
    # Check today + yesterday (CCTV publishes evening news, may be empty early)
    try:
        bj = _bj_now()
        cctv_dates = [bj.strftime("%Y%m%d"), (bj - timedelta(days=1)).strftime("%Y%m%d")]
        for cctv_date in cctv_dates:
            try:
                df2 = _with_retries(lambda d=cctv_date: ak.news_cctv(date=d))
            except Exception:
                continue
            if df2 is None or df2.empty:
                continue
            for _, row in df2.head(20).iterrows():
                title = str(row.get("title", ""))
                content = str(row.get("content", ""))
                text = title + content

                for keywords, evt_type, severity, direction, source, duration, sectors in _NEWS_KEYWORD_RULES:
                    if any(kw in text for kw in keywords):
                        evt_title = title[:100] if title else content[:100]
                        if evt_title in seen_titles:
                            break
                        seen_titles.add(evt_title)
                        detail = content[:200] if content else ""
                        events.append({
                            "type": evt_type,
                            "source": source,
                            "severity": severity,
                            "direction": direction,
                            "duration": duration,
                            "title": f"[CCTV] {evt_title}",
                            "detail": detail,
                            "affected_sectors": sectors,
                            "time": now_str,
                            "auto_detected": True,
                        })
                        break
    except Exception:
        pass

    return events


def _scan_risk_events() -> list[dict]:
    """Scan macro + stock + news data for Black Swan / Grey Rhino signals."""
    events: list[dict] = []
    now_str = _bj_now().strftime("%Y-%m-%d %H:%M")

    # 1) Macro indicator shocks
    macro = _fetch_macro_indicators()
    for m in macro:
        pct = abs(m.get("change_pct", 0))
        name = m.get("name", "")
        direction = "暴涨" if m.get("change_pct", 0) > 0 else "暴跌"

        if "上证" in name and pct >= 3:
            level = "黑天鹅" if pct >= 5 else "灰犀牛"
            events.append({
                "type": level, "time": now_str,
                "title": f"上证指数{direction} {m.get('change_pct')}%",
                "detail": f"当前 {m.get('price')}，前收 {m.get('prev')}",
                "severity": "high" if pct >= 5 else "medium",
            })
        elif "美元" in name and pct >= 0.5:
            level = "黑天鹅" if pct >= 1.5 else "灰犀牛"
            events.append({
                "type": level, "time": now_str,
                "title": f"美元/人民币{direction} {m.get('change_pct')}%",
                "detail": f"当前 {m.get('price')}，前收 {m.get('prev')}",
                "severity": "high" if pct >= 1.5 else "medium",
            })
        elif "黄金" in name and pct >= 2:
            level = "黑天鹅" if pct >= 4 else "灰犀牛"
            events.append({
                "type": level, "time": now_str,
                "title": f"黄金{direction} {m.get('change_pct')}%",
                "detail": f"当前 ${m.get('price')}/oz",
                "severity": "high" if pct >= 4 else "medium",
            })
        elif "原油" in name and pct >= 3:
            level = "黑天鹅" if pct >= 6 else "灰犀牛"
            events.append({
                "type": level, "time": now_str,
                "title": f"原油{direction} {m.get('change_pct')}%",
                "detail": f"当前 ${m.get('price')}/bbl",
                "severity": "high" if pct >= 6 else "medium",
            })

    # 2) Individual stock extremes from watchlist
    try:
        rows = STOCKS_CACHE_DATA or []
        for s in rows:
            pct = abs(s.get("change_pct") or 0)
            name = s.get("name", s.get("ticker", ""))
            if pct >= 9.8:
                tag = "涨停" if (s.get("change_pct") or 0) > 0 else "跌停"
                events.append({
                    "type": "灰犀牛" if tag == "涨停" else "黑天鹅",
                    "time": now_str,
                    "title": f"{name} {tag} {s.get('change_pct')}%",
                    "detail": f"价格 {s.get('price')}",
                    "severity": "high" if tag == "跌停" else "medium",
                })
            elif pct >= 5:
                direction = "大涨" if (s.get("change_pct") or 0) > 0 else "大跌"
                events.append({
                    "type": "灰犀牛", "time": now_str,
                    "title": f"{name} {direction} {s.get('change_pct')}%",
                    "detail": f"价格 {s.get('price')}",
                    "severity": "medium",
                })
    except Exception:
        pass

    # 3) Auto-detect major news from CLS feed
    try:
        news_events = _scan_news_events()
        events.extend(news_events)
    except Exception:
        pass

    # 5) Persist new events (deduplicate by title within same hour)
    existing_keys = {(e["title"], e["time"][:13]) for e in _RISK_EVENT_HISTORY}
    for e in events:
        key = (e["title"], e["time"][:13])
        if key not in existing_keys:
            _RISK_EVENT_HISTORY.append(e)
            existing_keys.add(key)

    # 6) Trim old events: drop entries older than max_age_days, cap total count
    cutoff_age = (_bj_now() - timedelta(days=cfg.RISK_EVENT_MAX_AGE_DAYS)).strftime("%Y-%m-%d %H:%M")
    _RISK_EVENT_HISTORY[:] = [
        e for e in _RISK_EVENT_HISTORY if e["time"] >= cutoff_age
    ][-cfg.RISK_EVENT_MAX_ENTRIES:]

    return events


@app.route("/api/risk-events", methods=["GET"])
def risk_events():
    """Return risk events. ?period=1h|today|3d|7d|30d"""
    # Scan for new events
    _scan_risk_events()

    period = request.args.get("period", "today")
    now = _bj_now()

    if period == "1h":
        cutoff = now - timedelta(hours=1)
    elif period == "3d":
        cutoff = now - timedelta(days=3)
    elif period == "7d":
        cutoff = now - timedelta(days=7)
    elif period == "30d":
        cutoff = now - timedelta(days=30)
    else:  # today
        cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)

    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M")
    filtered = [e for e in _RISK_EVENT_HISTORY if e["time"] >= cutoff_str]
    # Sort newest first
    filtered.sort(key=lambda e: e["time"], reverse=True)

    return jsonify({
        "ok": True,
        "period": period,
        "events": filtered,
        "count": len(filtered),
    })


_VALID_RISK_TYPES = {"黑天鹅", "灰犀牛"}
_VALID_SEVERITIES = {"critical", "high", "medium", "low"}
_VALID_DIRECTIONS = {"bullish", "bearish", "ambiguous"}
_VALID_SOURCES = {"geopolitical", "policy", "macro_shock", "sector", "company", "external"}
_VALID_DURATIONS = {"flash", "short", "medium", "long"}


@app.route("/api/risk-events", methods=["POST"])
def risk_events_add():
    """Manually add a risk event."""
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"ok": False, "msg": "标题不能为空"})
    if len(title) > 200:
        return jsonify({"ok": False, "msg": "标题过长"})

    evt_type = data.get("type", "灰犀牛")
    if evt_type not in _VALID_RISK_TYPES:
        evt_type = "灰犀牛"
    severity = data.get("severity", "medium")
    if severity not in _VALID_SEVERITIES:
        severity = "medium"
    direction = data.get("direction", "ambiguous")
    if direction not in _VALID_DIRECTIONS:
        direction = "ambiguous"
    source = data.get("source", "geopolitical")
    if source not in _VALID_SOURCES:
        source = "geopolitical"
    duration = data.get("duration", "short")
    if duration not in _VALID_DURATIONS:
        duration = "short"

    detail = (data.get("detail") or "").strip()[:500]
    sectors = data.get("affected_sectors") or []
    if isinstance(sectors, str):
        sectors = [s.strip() for s in sectors.split(",") if s.strip()]

    event = {
        "type": evt_type,
        "source": source,
        "severity": severity,
        "direction": direction,
        "duration": duration,
        "title": title,
        "detail": detail,
        "affected_sectors": sectors[:10],
        "time": _bj_now().strftime("%Y-%m-%d %H:%M"),
        "auto_detected": False,
    }
    _RISK_EVENT_HISTORY.append(event)
    return jsonify({"ok": True, "event": event})


# ── Bazi (八字) endpoint ──────────────────────────────────────────────────────

@app.route("/api/bazi", methods=["GET"])
def bazi():
    now = _bj_now().replace(tzinfo=None)
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    # Lunar
    lunar_str = get_lunar_date_string(now)

    # Solar terms
    info = get_solar_term_info(now)
    term_parts = []
    if info["prev"]:
        name, _season, days_ago = info["prev"]
        term_parts.append(f"{name} {days_ago}天前")
    if info["today"]:
        name, _season = info["today"]
        term_parts.append(f"★ 今日{name}")
    if info["next"]:
        name, _season, days_left = info["next"]
        term_parts.append(f"{days_left}天后 {name}")

    # Bazi pillars
    year_str, month_str, day_str, hours = get_bazi_data(now)
    calc = BaziCalculator(now)
    hour_zhi = calc.get_hour_zhi()
    day_gan = calc.calc_day_gan_zhi()[0]
    hour_gan = calc.calc_hour_gan(day_gan, hour_zhi)
    hour_str = f"{hour_gan}{hour_zhi}"
    nayin = calc.get_nayin(hour_gan, hour_zhi)

    # 五运六气
    wuyun = calc_wuyun_liuqi(now)

    return jsonify({
        "ok": True,
        "solar": f"{now.year}年{now.month}月{now.day}日 {weekdays[now.weekday()]}",
        "lunar": lunar_str,
        "terms": " │ ".join(term_parts) if term_parts else "",
        "pillars": [
            {"label": "年柱", "value": year_str},
            {"label": "月柱", "value": month_str},
            {"label": "日柱", "value": day_str},
            {"label": "时柱", "value": hour_str},
        ],
        "nayin": nayin,
        "wuyun": wuyun,
    })


# ── Provider test & select ────────────────────────────────────────────────────

@app.route("/api/providers/test", methods=["POST"])
def test_providers():
    """Test all data providers and return timing results."""
    results = _test_providers()
    # Auto-select: sort by ok (True first) then by speed
    ranked = sorted(results, key=lambda r: (not r["ok"], r["time_s"]))
    best = ranked[0]["provider"] if ranked and ranked[0]["ok"] else None
    return jsonify({"results": results, "best": best, "current": list(_preferred_provider_order)})


@app.route("/api/providers/order", methods=["GET"])
def get_provider_order():
    return jsonify({"order": list(_preferred_provider_order)})


@app.route("/api/providers/order", methods=["POST"])
def set_provider_order():
    """Set provider priority order. Body: {"order": ["sina","akshare","yahoo"]}"""
    global _preferred_provider_order
    data = request.get_json(silent=True) or {}
    order = data.get("order", [])
    valid = [p for p in order if p in _PROVIDER_FUNCS]
    # Append any missing providers at the end
    for p in _A_SHARE_DEFAULT_ORDER:
        if p not in valid:
            valid.append(p)
    _preferred_provider_order = valid
    return jsonify({"ok": True, "order": _preferred_provider_order})


@app.route("/api/providers/auto", methods=["POST"])
def auto_select_provider():
    """Test all providers and auto-set the fastest working one as primary."""
    global _preferred_provider_order
    results = _test_providers()
    ranked = sorted(results, key=lambda r: (not r["ok"], r["time_s"]))
    new_order = [r["provider"] for r in ranked if r["ok"]]
    # Append failed providers at end as fallbacks
    for r in ranked:
        if r["provider"] not in new_order:
            new_order.append(r["provider"])
    _preferred_provider_order = new_order
    return jsonify({"ok": True, "order": _preferred_provider_order, "results": results})


# ── 新股新债 (IPO & convertible bond subscription) ─────────────────────────────

_XGXZ_CACHE: dict | None = None
_XGXZ_CACHE_DATE: str = ""


def _fetch_xingu_xinzhai() -> dict:
    """Fetch upcoming IPO + convertible bond data from East Money."""
    global _XGXZ_CACHE, _XGXZ_CACHE_DATE
    today = _bj_now().strftime("%Y-%m-%d")
    if _XGXZ_CACHE and _XGXZ_CACHE_DATE == today:
        return _XGXZ_CACHE

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://data.eastmoney.com",
    }
    ipo_list: list[dict] = []
    bond_list: list[dict] = []

    # ── 新股 (IPO) ──
    try:
        ipo_url = (
            "https://datacenter-web.eastmoney.com/api/data/v1/get?"
            "sortColumns=APPLY_DATE&sortTypes=-1&pageSize=20&pageNumber=1"
            "&reportName=RPTA_APP_IPOAPPLY"
            "&columns=SECURITY_CODE,SECURITY_NAME,APPLY_DATE,ISSUE_PRICE,ONLINE_ISSUE_LWR,INITIAL_MULTIPLE"
            "&source=WEB&client=WEB"
        )
        req = urlrequest.Request(ipo_url, headers=headers)
        with urlrequest.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if data.get("success") and data.get("result", {}).get("data"):
            for row in data["result"]["data"]:
                apply_date = (row.get("APPLY_DATE") or "")[:10]
                ipo_list.append({
                    "code": row.get("SECURITY_CODE", ""),
                    "name": row.get("SECURITY_NAME", ""),
                    "apply_date": apply_date,
                    "price": row.get("ISSUE_PRICE"),
                    "win_rate": row.get("ONLINE_ISSUE_LWR"),
                    "multiple": row.get("INITIAL_MULTIPLE"),
                })
    except Exception as e:
        logging.warning("新股 fetch failed: %s", e)

    # ── 新债 (convertible bond) ──
    try:
        bond_url = (
            "https://datacenter-web.eastmoney.com/api/data/v1/get?"
            "sortColumns=PUBLIC_START_DATE&sortTypes=-1&pageSize=20&pageNumber=1"
            "&reportName=RPT_BOND_CB_LIST"
            "&columns=SECURITY_CODE,SECURITY_NAME_ABBR,CORRECODE_NAME_ABBR,"
            "PUBLIC_START_DATE,LISTING_DATE,ONLINE_GENERAL_LWR"
            "&source=WEB&client=WEB"
        )
        req = urlrequest.Request(bond_url, headers=headers)
        with urlrequest.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if data.get("success") and data.get("result", {}).get("data"):
            for row in data["result"]["data"]:
                apply_date = (row.get("PUBLIC_START_DATE") or "")[:10]
                list_date = (row.get("LISTING_DATE") or "")[:10]
                bond_list.append({
                    "code": row.get("SECURITY_CODE", ""),
                    "name": row.get("SECURITY_NAME_ABBR", ""),
                    "apply_name": row.get("CORRECODE_NAME_ABBR", ""),
                    "apply_date": apply_date,
                    "list_date": list_date,
                    "win_rate": row.get("ONLINE_GENERAL_LWR"),
                })
    except Exception as e:
        logging.warning("新债 fetch failed: %s", e)

    # Only keep items from last 3 days + future, cap at 8 per section
    cutoff = (_bj_now() - timedelta(days=3)).strftime("%Y-%m-%d")
    ipo_list = [r for r in ipo_list if (r["apply_date"] or "") >= cutoff][:8]
    bond_list = [r for r in bond_list if (r["apply_date"] or "") >= cutoff][:8]

    result = {"ok": True, "date": today, "ipo": ipo_list, "bond": bond_list}
    _XGXZ_CACHE = result
    _XGXZ_CACHE_DATE = today
    return result


@app.route("/api/xingu-xinzhai", methods=["GET"])
def xingu_xinzhai():
    return jsonify(_fetch_xingu_xinzhai())


# ── Decision Journal ──────────────────────────────────────────────────────────

@app.route("/api/decisions", methods=["GET"])
def list_decisions():
    dtype = request.args.get("type")
    state = request.args.get("state")
    return jsonify({"ok": True, "decisions": dec.list_decisions(dtype, state)})


@app.route("/api/decisions", methods=["POST"])
def create_decision():
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"ok": False, "error": "title is required"}), 400
    try:
        # Build kwargs — include trade fields if provided
        kwargs = {}
        for tf in ("symbol", "source"):
            if data.get(tf):
                kwargs[tf] = data[tf]
        for tf in ("price", "stop_loss", "take_profit", "max_drawdown", "confidence"):
            if data.get(tf) is not None:
                kwargs[tf] = float(data[tf])
        if data.get("size") is not None:
            kwargs["size"] = int(data["size"])
        if isinstance(data.get("trade_context"), dict):
            kwargs["trade_context"] = data["trade_context"]

        d = dec.create_decision(
            title=title,
            dtype=data.get("type", "trade"),
            context=data.get("context", ""),
            action=data.get("action", ""),
            outcome=data.get("outcome", ""),
            tags=data.get("tags", []),
            state=data.get("state", "idea"),
            **kwargs,
        )
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "decision": d}), 201


@app.route("/api/decisions/<did>", methods=["PUT"])
def update_decision(did):
    data = request.get_json(force=True, silent=True) or {}
    try:
        d = dec.update_decision(did, data)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if d is None:
        return jsonify({"ok": False, "error": "not found"}), 404
    return jsonify({"ok": True, "decision": d})


@app.route("/api/decisions/<did>", methods=["DELETE"])
def delete_decision(did):
    if dec.delete_decision(did):
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "not found"}), 404


# ── Advisor (参谋模块) ─────────────────────────────────────────────────────

@app.route("/api/advisor", methods=["GET"])
def advisor_endpoint():
    risk_pref = request.args.get("risk_pref", "balanced")

    # Gather positions from frontend (sent as query param JSON)
    raw_positions = request.args.get("positions", "[]")
    try:
        client_positions = json.loads(raw_positions)
    except (json.JSONDecodeError, TypeError):
        client_positions = []

    # Get stock data
    rows = _get_stocks_snapshot()
    stock_map = {r["ticker"]: r for r in rows if not r.get("error")}

    # Build PositionInput list
    positions: list[adv.PositionInput] = []
    for p in client_positions:
        ticker = p.get("ticker", "")
        stock = stock_map.get(ticker, {})
        positions.append(adv.PositionInput(
            ticker=ticker,
            name=stock.get("name", p.get("name", ticker)),
            shares=int(p.get("shares", 0)),
            cost=float(p.get("cost", 0)),
            price=float(stock.get("price", 0)),
            change_pct=float(stock.get("change_pct", 0)),
            high52=stock.get("high52"),
            low52=stock.get("low52"),
            volume=int(stock.get("volume", 0)),
        ))

    # Build market context
    brief = _build_auto_brief()
    regime = brief.get("snapshot", {}).get("regime", "震荡")

    ai = _build_ai_edge_report()
    confidence = ai.get("summary", {}).get("confidence", 50.0)

    # Sentiment: use last known from history
    sentiment_stage = "分歧"
    sentiment_score = 0
    tradable = True
    history = _load_sentiment_history()
    if history:
        last = history[-1]
        sentiment_stage = last.get("stage", "分歧")
        sentiment_score = last.get("score", 0)
        tradable = sentiment_stage == "上升"

    ctx = adv.MarketContext(
        regime=regime,
        sentiment_stage=sentiment_stage,
        sentiment_score=sentiment_score,
        tradable=tradable,
        confidence=confidence,
        risk_events=_RISK_EVENT_HISTORY[-20:],
    )

    result = adv.evaluate_portfolio(positions, ctx, risk_pref)
    return jsonify({
        "ok": result.ok,
        "generated_at": result.generated_at,
        "strategy": result.strategy_name,
        "portfolio_action": result.portfolio_action,
        "portfolio_reason": result.portfolio_reason,
        "signals": [
            {
                "ticker": s.ticker,
                "name": s.name,
                "action": s.action,
                "strength": s.strength,
                "reasons": s.reasons,
                "stop_loss": s.stop_loss,
                "take_profit": s.take_profit,
                "factors": s.factors,
            }
            for s in result.signals
        ],
        "context": {
            "regime": regime,
            "sentiment_stage": sentiment_stage,
            "confidence": confidence,
        },
        "msg": result.msg,
    })


@app.route("/api/advisor/save-decision", methods=["POST"])
def advisor_save_decision():
    """Save an advisor signal as a decision journal entry."""
    data = request.get_json(silent=True) or {}
    ticker = data.get("ticker", "")
    name = data.get("name", ticker)
    action = data.get("action", "hold")
    reasons = data.get("reasons", [])
    factors = data.get("factors", [])
    risk_pref = data.get("risk_pref", "balanced")
    portfolio_action = data.get("portfolio_action", "")

    action_label = {
        "buy": "买入", "sell": "卖出", "hold": "持有",
        "reduce": "减仓", "add": "加仓",
    }
    title = f"[AI建议] {name} ({ticker}) → {action_label.get(action, action)}"
    context_parts = [f"风险偏好: {risk_pref}", f"组合建议: {portfolio_action}"]
    action_text = "；".join(reasons) if reasons else "无明显信号"
    factor_lines = [f"{f['name']}({f['score']:+d}): {f['detail']}" for f in factors]
    context_text = " | ".join(context_parts)
    if factor_lines:
        context_text += "\n因子分析: " + " / ".join(factor_lines)

    # Build structured trade context for the Decision model
    trade_ctx = {
        "risk_pref": risk_pref,
        "portfolio_action": portfolio_action,
        "factors": factors,
    }
    # Map advisor action → Decision action
    dec_action = {
        "buy": "BUY", "add": "BUY",
        "sell": "SELL", "reduce": "SELL",
        "hold": "HOLD",
    }.get(action, "HOLD")

    # Extract price/size from posted data (frontend sends position info)
    price = data.get("price", 0)
    size = data.get("size", 0)
    strength = data.get("strength", 1)

    try:
        entry = dec.create_decision(
            title=title,
            dtype="trade",
            context=context_text,
            action=dec_action,
            tags=["ai-advisor", ticker],
            state="idea",
            symbol=name,
            price=float(price) if price else 0.0,
            size=int(size) if size else 0,
            confidence=strength / 5.0 if strength else 0.2,
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            source="ai",
            trade_context=trade_ctx,
        )
        return jsonify({"ok": True, "decision": entry})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/decisions/evaluate/<decision_id>", methods=["POST"])
def evaluate_decision(decision_id):
    """Evaluate a trade decision against current price."""
    data = request.get_json(silent=True) or {}
    current_price = data.get("current_price", 0)
    if not current_price or float(current_price) <= 0:
        return jsonify({"ok": False, "error": "current_price required (>0)"}), 400
    result = dec.evaluate(decision_id, float(current_price))
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@app.route("/api/decisions/analyze", methods=["GET"])
def analyze_decisions():
    """Analyze trade decisions for behavioral patterns."""
    dtype = request.args.get("type", "trade")
    return jsonify(dec.analyze(dtype=dtype))


# ── Serve frontend ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


if __name__ == "__main__":
    print("Starting Stock Tracker -> http://localhost:5000")
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host=host, debug=debug, port=5000)
