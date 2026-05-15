"""
Stock screener — scan a pool of A-share stocks and filter by strategy rules.

Data sources:
  - Stock universe: CSI 300 via AkShare `index_stock_cons_csindex`
  - OHLCV history: Sina daily K-line API (reliable)
  - Limit-up pool: AkShare `stock_zt_pool_em`

Strategies:
  golden_cross   — MA5 上穿 MA20，放量确认
  volume_breakout — 量比>2，突破20日最高
  oversold_bounce — RSI<30 + 放量阳线
  limit_up_relay  — 昨日涨停，今日高开
"""

from __future__ import annotations

import json
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib import request as urlrequest

from analysis import quant

log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

STRATEGIES = {
    "golden_cross": {
        "name": "均线金叉",
        "desc": "MA5 上穿 MA20，放量确认",
        "icon": "✦",
    },
    "volume_breakout": {
        "name": "放量突破",
        "desc": "量比>2，价格突破20日最高",
        "icon": "⚡",
    },
    "oversold_bounce": {
        "name": "超跌反弹",
        "desc": "RSI<30 + 当日放量阳线",
        "icon": "↗",
    },
    "limit_up_relay": {
        "name": "涨停接力",
        "desc": "昨日涨停，今日高开3%+",
        "icon": "🔥",
    },
}

# ── Cache ─────────────────────────────────────────────────────────────────────

_POOL_CACHE: dict = {}          # key=pool_name, val={data, ts}
_POOL_TTL = 600                 # 10 min for stock universe
_SCREENER_CACHE: dict = {}      # key=strategy, val={data, ts}
_SCREENER_TTL = 300             # 5 min for scan results
_OHLCV_CACHE: dict = {}         # key=sina_symbol, val={bars, ts}
_OHLCV_TTL = 300                # 5 min per stock

SINA_KLINE_API = (
    "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
    "/CN_MarketData.getKLineData"
)


# ── Stock universe ────────────────────────────────────────────────────────────

def _code_to_sina(code: str) -> str:
    """Convert 6-digit code to Sina symbol like sh600519 or sz000858."""
    if code.startswith(("5", "6", "9")):
        return f"sh{code}"
    return f"sz{code}"


def _code_to_ticker(code: str) -> str:
    """Convert 6-digit code to Yahoo-style ticker like 600519.SS."""
    if code.startswith(("5", "6", "9")):
        return f"{code}.SS"
    return f"{code}.SZ"


def _get_csi300_pool() -> list[dict]:
    """Fetch CSI 300 constituents. Returns [{code, name, ticker, sina}]."""
    now = time.time()
    cached = _POOL_CACHE.get("csi300")
    if cached and (now - cached["ts"]) < _POOL_TTL:
        return cached["data"]

    try:
        import akshare as ak
        df = ak.index_stock_cons_csindex(symbol="000300")
        pool = []
        for _, row in df.iterrows():
            code = str(row["成分券代码"]).zfill(6)
            pool.append({
                "code": code,
                "name": row["成分券名称"],
                "ticker": _code_to_ticker(code),
                "sina": _code_to_sina(code),
            })
        _POOL_CACHE["csi300"] = {"data": pool, "ts": now}
        return pool
    except Exception as e:
        log.warning("CSI300 pool fetch failed: %s", e)
        return cached["data"] if cached else []


def _get_zt_pool(date_str: str) -> list[dict]:
    """Fetch 涨停 pool for a date. Returns [{code, name, change_pct, industry}]."""
    cache_key = f"zt_{date_str}"
    now = time.time()
    cached = _POOL_CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < _POOL_TTL:
        return cached["data"]

    try:
        import akshare as ak
        df = ak.stock_zt_pool_em(date=date_str)
        pool = []
        for _, row in df.iterrows():
            code = str(row["代码"]).zfill(6)
            pool.append({
                "code": code,
                "name": row["名称"],
                "change_pct": float(row["涨跌幅"]) if row["涨跌幅"] else 0,
                "industry": row.get("所属行业", ""),
                "consec": int(row.get("连板数", 1)),
            })
        _POOL_CACHE[cache_key] = {"data": pool, "ts": now}
        return pool
    except Exception as e:
        log.warning("ZT pool fetch failed for %s: %s", date_str, e)
        return cached["data"] if cached else []


# ── OHLCV fetcher ─────────────────────────────────────────────────────────────

def _fetch_ohlcv(sina_sym: str, days: int = 30) -> list[dict]:
    """Fetch OHLCV from Sina kline API with caching."""
    now = time.time()
    cached = _OHLCV_CACHE.get(sina_sym)
    if cached and (now - cached["ts"]) < _OHLCV_TTL:
        return cached["bars"]

    try:
        api = f"{SINA_KLINE_API}?symbol={sina_sym}&scale=240&ma=no&datalen={days}"
        req = urlrequest.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urlrequest.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        data = json.loads(raw)
        if not data:
            return []
        bars = [
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
        _OHLCV_CACHE[sina_sym] = {"bars": bars, "ts": now}
        return bars
    except Exception:
        return cached["bars"] if cached else []


def _prefetch_pool_ohlcv(pool: list[dict], days: int = 30, workers: int = 20) -> None:
    """Pre-fetch OHLCV for all stocks in pool using thread pool.
    Results go into _OHLCV_CACHE so strategy scans hit cache."""
    # Only fetch stocks not already cached
    now = time.time()
    to_fetch = [
        s for s in pool
        if s["sina"] not in _OHLCV_CACHE
        or (now - _OHLCV_CACHE[s["sina"]]["ts"]) >= _OHLCV_TTL
    ]
    if not to_fetch:
        return

    def _do(sina_sym):
        _fetch_ohlcv(sina_sym, days)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futs = {executor.submit(_do, s["sina"]): s for s in to_fetch}
        for fut in as_completed(futs):
            try:
                fut.result()
            except Exception:
                pass


# ── Strategy implementations ─────────────────────────────────────────────────

def _calc_volume_ratio(volumes: list[float], period: int = 5) -> float:
    """Volume ratio: latest volume / avg of previous N volumes."""
    if len(volumes) < period + 1:
        return 0
    avg = sum(volumes[-(period + 1):-1]) / period
    return round(volumes[-1] / avg, 2) if avg > 0 else 0


def _scan_golden_cross(pool: list[dict], max_results: int = 20) -> list[dict]:
    """MA5 crosses above MA20, with volume confirmation."""
    hits = []
    for stock in pool:
        bars = _fetch_ohlcv(stock["sina"], 30)
        if len(bars) < 22:
            continue
        closes = [b["close"] for b in bars]
        volumes = [b["volume"] for b in bars]

        ma5 = quant.calc_ma(closes, 5)
        ma20 = quant.calc_ma(closes, 20)
        i = len(closes) - 1

        if not quant._cross_up(ma5, ma20, i):
            continue

        vol_ratio = _calc_volume_ratio(volumes)
        if vol_ratio < 1.2:
            continue

        score = 60
        if vol_ratio >= 1.5:
            score += 15
        if vol_ratio >= 2.0:
            score += 10
        # Bonus if MACD is also bullish
        macd = quant.calc_macd(closes)
        if macd["dif"][i] is not None and macd["dea"][i] is not None:
            if macd["dif"][i] > macd["dea"][i]:
                score += 10

        hits.append({
            "code": stock["code"],
            "name": stock["name"],
            "ticker": stock["ticker"],
            "price": closes[-1],
            "change_pct": round((closes[-1] - closes[-2]) / closes[-2] * 100, 2),
            "score": min(score, 100),
            "reasons": [
                f"MA5({ma5[i]:.2f})上穿MA20({ma20[i]:.2f})",
                f"量比 {vol_ratio}",
            ],
        })
        if len(hits) >= max_results:
            break
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits


def _scan_volume_breakout(pool: list[dict], max_results: int = 20) -> list[dict]:
    """Volume ratio > 2, price breaks 20-day high, change > 3%."""
    hits = []
    for stock in pool:
        bars = _fetch_ohlcv(stock["sina"], 25)
        if len(bars) < 21:
            continue
        closes = [b["close"] for b in bars]
        highs = [b["high"] for b in bars]
        volumes = [b["volume"] for b in bars]
        i = len(closes) - 1

        vol_ratio = _calc_volume_ratio(volumes)
        if vol_ratio < 2.0:
            continue

        max_20d = max(highs[max(0, i - 20):i])
        if closes[i] <= max_20d:
            continue

        chg_pct = (closes[i] - closes[i - 1]) / closes[i - 1] * 100
        if chg_pct < 3.0:
            continue

        score = 65
        if vol_ratio >= 3.0:
            score += 15
        if chg_pct >= 5.0:
            score += 10

        hits.append({
            "code": stock["code"],
            "name": stock["name"],
            "ticker": stock["ticker"],
            "price": closes[i],
            "change_pct": round(chg_pct, 2),
            "score": min(score, 100),
            "reasons": [
                f"量比 {vol_ratio}",
                f"突破20日高 {max_20d:.2f}",
                f"涨幅 {chg_pct:.1f}%",
            ],
        })
        if len(hits) >= max_results:
            break
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits


def _scan_oversold_bounce(pool: list[dict], max_results: int = 20) -> list[dict]:
    """RSI6 < 30 + volume up + positive close."""
    hits = []
    for stock in pool:
        bars = _fetch_ohlcv(stock["sina"], 30)
        if len(bars) < 10:
            continue
        closes = [b["close"] for b in bars]
        volumes = [b["volume"] for b in bars]
        i = len(closes) - 1

        rsi6 = quant.calc_rsi(closes, 6)
        r = rsi6[i]
        if r is None or r >= 30:
            continue

        chg_pct = (closes[i] - closes[i - 1]) / closes[i - 1] * 100
        if chg_pct <= 0:
            continue

        vol_ratio = _calc_volume_ratio(volumes)
        if vol_ratio < 1.3:
            continue

        score = 55
        if r < 20:
            score += 20
        elif r < 25:
            score += 10
        if vol_ratio >= 2.0:
            score += 10

        hits.append({
            "code": stock["code"],
            "name": stock["name"],
            "ticker": stock["ticker"],
            "price": closes[i],
            "change_pct": round(chg_pct, 2),
            "score": min(score, 100),
            "reasons": [
                f"RSI6={r}",
                f"量比 {vol_ratio}",
                f"阳线 +{chg_pct:.1f}%",
            ],
        })
        if len(hits) >= max_results:
            break
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits


def _scan_limit_up_relay(max_results: int = 20) -> list[dict]:
    """Yesterday limit-up stocks that opened high today (>3%)."""
    today = datetime.now()
    # Find the most recent trading day for ZT pool
    # Try today-1, today-2, today-3 (skip weekends)
    zt_pool = []
    for offset in range(1, 5):
        d = today - timedelta(days=offset)
        if d.weekday() >= 5:
            continue
        ds = d.strftime("%Y%m%d")
        zt_pool = _get_zt_pool(ds)
        if zt_pool:
            break

    if not zt_pool:
        return []

    # Pre-fetch OHLCV for all ZT stocks in parallel
    zt_with_sina = [{"sina": _code_to_sina(s["code"]), **s} for s in zt_pool]
    _prefetch_pool_ohlcv(zt_with_sina, days=5, workers=20)

    hits = []
    for stock in zt_pool:
        bars = _fetch_ohlcv(_code_to_sina(stock["code"]), 5)
        if len(bars) < 2:
            continue
        last = bars[-1]
        prev = bars[-2]

        open_chg = (last["open"] - prev["close"]) / prev["close"] * 100
        if open_chg < 3.0:
            continue

        chg_pct = (last["close"] - prev["close"]) / prev["close"] * 100

        score = 60
        if open_chg >= 5.0:
            score += 15
        if stock.get("consec", 1) >= 2:
            score += 10
        if chg_pct > 5:
            score += 10

        hits.append({
            "code": stock["code"],
            "name": stock["name"],
            "ticker": _code_to_ticker(stock["code"]),
            "price": last["close"],
            "change_pct": round(chg_pct, 2),
            "score": min(score, 100),
            "reasons": [
                f"昨日涨停 +{stock['change_pct']:.1f}%",
                f"今日高开 +{open_chg:.1f}%",
                f"连板数 {stock.get('consec', 1)}",
            ],
        })
        if len(hits) >= max_results:
            break
    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits


# ── Public API ────────────────────────────────────────────────────────────────

_SCAN_FNS = {
    "golden_cross": lambda pool, n: _scan_golden_cross(pool, n),
    "volume_breakout": lambda pool, n: _scan_volume_breakout(pool, n),
    "oversold_bounce": lambda pool, n: _scan_oversold_bounce(pool, n),
}


def run_screen(strategy: str, max_results: int = 20) -> dict:
    """Run a screening strategy. Returns {ok, strategy, name, hits[], scanned, ts}."""
    if strategy not in STRATEGIES:
        return {"ok": False, "msg": f"未知策略: {strategy}"}

    now = time.time()
    cached = _SCREENER_CACHE.get(strategy)
    if cached and (now - cached["ts"]) < _SCREENER_TTL:
        return cached["data"]

    meta = STRATEGIES[strategy]

    # limit_up_relay uses its own data source
    if strategy == "limit_up_relay":
        hits = _scan_limit_up_relay(max_results)
        result = {
            "ok": True,
            "strategy": strategy,
            "name": meta["name"],
            "desc": meta["desc"],
            "icon": meta["icon"],
            "hits": hits,
            "scanned": "涨停池",
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        _SCREENER_CACHE[strategy] = {"data": result, "ts": now}
        return result

    # Other strategies use CSI 300 pool
    pool = _get_csi300_pool()
    if not pool:
        return {"ok": False, "msg": "无法获取股票池"}

    # Parallel pre-fetch all OHLCV data (20 threads, ~15s for 300 stocks)
    _prefetch_pool_ohlcv(pool, days=30, workers=20)

    scan_fn = _SCAN_FNS[strategy]
    hits = scan_fn(pool, max_results)

    result = {
        "ok": True,
        "strategy": strategy,
        "name": meta["name"],
        "desc": meta["desc"],
        "icon": meta["icon"],
        "hits": hits,
        "scanned": f"沪深300 ({len(pool)}只)",
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _SCREENER_CACHE[strategy] = {"data": result, "ts": now}
    return result


def list_strategies() -> list[dict]:
    """Return available strategies for the frontend dropdown."""
    return [
        {"key": k, "name": v["name"], "desc": v["desc"], "icon": v["icon"]}
        for k, v in STRATEGIES.items()
    ]
