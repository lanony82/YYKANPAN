"""
Technical indicator calculations and signal generation for A-share stocks.

Pure functions — no I/O, no side effects.
Indicators: MA, MACD, RSI, KDJ, Bollinger Bands.
"""

from __future__ import annotations


# ── Moving Average ─────────────────────────────────────────────────────────────

def calc_ma(closes: list[float], period: int) -> list[float | None]:
    """Simple Moving Average.  Returns list same length as closes."""
    out: list[float | None] = [None] * len(closes)
    if len(closes) < period:
        return out
    s = sum(closes[:period])
    out[period - 1] = round(s / period, 3)
    for i in range(period, len(closes)):
        s += closes[i] - closes[i - period]
        out[i] = round(s / period, 3)
    return out


def _ema(values: list[float], period: int) -> list[float | None]:
    """Exponential Moving Average (internal helper)."""
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    k = 2 / (period + 1)
    # seed with SMA
    out[period - 1] = sum(values[:period]) / period
    for i in range(period, len(values)):
        out[i] = values[i] * k + out[i - 1] * (1 - k)  # type: ignore[operator]
    return out


# ── MACD ───────────────────────────────────────────────────────────────────────

def calc_macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict:
    """
    Returns {dif: [], dea: [], hist: []} — all same length as closes.
    hist = (DIF - DEA) * 2  (bar chart value).
    """
    n = len(closes)
    ema_fast = _ema(closes, fast)
    ema_slow = _ema(closes, slow)

    dif: list[float | None] = [None] * n
    for i in range(n):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            dif[i] = round(ema_fast[i] - ema_slow[i], 4)  # type: ignore[operator]

    # DEA = EMA(DIF, signal) — only over non-None DIF values
    dif_start = next((i for i in range(n) if dif[i] is not None), n)
    dif_vals = [dif[i] for i in range(dif_start, n)]  # type: ignore[arg-type]
    dea_part = _ema(dif_vals, signal) if len(dif_vals) >= signal else [None] * len(dif_vals)

    dea: list[float | None] = [None] * n
    for j, i in enumerate(range(dif_start, n)):
        dea[i] = round(dea_part[j], 4) if dea_part[j] is not None else None

    hist: list[float | None] = [None] * n
    for i in range(n):
        if dif[i] is not None and dea[i] is not None:
            hist[i] = round((dif[i] - dea[i]) * 2, 4)  # type: ignore[operator]

    return {"dif": dif, "dea": dea, "hist": hist}


# ── RSI ────────────────────────────────────────────────────────────────────────

def calc_rsi(closes: list[float], period: int = 6) -> list[float | None]:
    """Wilder's RSI.  Returns list same length as closes."""
    n = len(closes)
    out: list[float | None] = [None] * n
    if n < period + 1:
        return out

    gains = []
    losses = []
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        out[period] = 100.0
    else:
        out[period] = round(100 - 100 / (1 + avg_gain / avg_loss), 2)

    for i in range(period + 1, n):
        d = closes[i] - closes[i - 1]
        avg_gain = (avg_gain * (period - 1) + max(d, 0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-d, 0)) / period
        if avg_loss == 0:
            out[i] = 100.0
        else:
            out[i] = round(100 - 100 / (1 + avg_gain / avg_loss), 2)
    return out


# ── KDJ ────────────────────────────────────────────────────────────────────────

def calc_kdj(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 9,
) -> dict:
    """Returns {k: [], d: [], j: []} same length as input lists."""
    n = len(closes)
    k_out: list[float | None] = [None] * n
    d_out: list[float | None] = [None] * n
    j_out: list[float | None] = [None] * n
    if n < period:
        return {"k": k_out, "d": d_out, "j": j_out}

    k_prev = 50.0
    d_prev = 50.0

    for i in range(period - 1, n):
        window_high = max(highs[i - period + 1 : i + 1])
        window_low = min(lows[i - period + 1 : i + 1])
        if window_high == window_low:
            rsv = 50.0
        else:
            rsv = (closes[i] - window_low) / (window_high - window_low) * 100

        k = 2 / 3 * k_prev + 1 / 3 * rsv
        d = 2 / 3 * d_prev + 1 / 3 * k
        j = 3 * k - 2 * d

        k_out[i] = round(k, 2)
        d_out[i] = round(d, 2)
        j_out[i] = round(j, 2)
        k_prev = k
        d_prev = d

    return {"k": k_out, "d": d_out, "j": j_out}


# ── Bollinger Bands ────────────────────────────────────────────────────────────

def calc_boll(
    closes: list[float], period: int = 20, num_std: float = 2.0
) -> dict:
    """Returns {mid: [], upper: [], lower: []} same length as closes."""
    n = len(closes)
    mid: list[float | None] = [None] * n
    upper: list[float | None] = [None] * n
    lower: list[float | None] = [None] * n
    if n < period:
        return {"mid": mid, "upper": upper, "lower": lower}

    for i in range(period - 1, n):
        window = closes[i - period + 1 : i + 1]
        avg = sum(window) / period
        var = sum((x - avg) ** 2 for x in window) / period
        std = var ** 0.5
        mid[i] = round(avg, 3)
        upper[i] = round(avg + num_std * std, 3)
        lower[i] = round(avg - num_std * std, 3)

    return {"mid": mid, "upper": upper, "lower": lower}


# ── Signal Generation ──────────────────────────────────────────────────────────

def _cross_up(fast: list, slow: list, idx: int) -> bool:
    """True if fast crossed above slow at index idx."""
    if idx < 1:
        return False
    if fast[idx] is None or slow[idx] is None:
        return False
    if fast[idx - 1] is None or slow[idx - 1] is None:
        return False
    return fast[idx - 1] <= slow[idx - 1] and fast[idx] > slow[idx]


def _cross_down(fast: list, slow: list, idx: int) -> bool:
    """True if fast crossed below slow at index idx."""
    if idx < 1:
        return False
    if fast[idx] is None or slow[idx] is None:
        return False
    if fast[idx - 1] is None or slow[idx - 1] is None:
        return False
    return fast[idx - 1] >= slow[idx - 1] and fast[idx] < slow[idx]


def generate_signals(
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
) -> dict:
    """
    Compute all indicators on OHLCV data and generate trading signals.

    Returns dict with:
      indicators: {ma5, ma10, ma20, ma60, macd, rsi6, rsi12, kdj, boll}
      signals: list of {name, action: "买"|"卖"|"观望", strength: 1-3, detail}
      summary: {buy_count, sell_count, net_signal, verdict: "买入"|"卖出"|"观望"}
    """
    n = len(closes)
    if n < 2:
        return {"indicators": {}, "signals": [], "summary": _empty_summary()}

    # ── Calculate indicators ──
    ma5 = calc_ma(closes, 5)
    ma10 = calc_ma(closes, 10)
    ma20 = calc_ma(closes, 20)
    ma60 = calc_ma(closes, 60)
    macd = calc_macd(closes)
    rsi6 = calc_rsi(closes, 6)
    rsi12 = calc_rsi(closes, 12)
    kdj = calc_kdj(highs, lows, closes)
    boll = calc_boll(closes)

    i = n - 1  # latest bar
    signals: list[dict] = []

    # ── MA signals ──
    if _cross_up(ma5, ma20, i):
        signals.append({"name": "MA金叉", "action": "买", "strength": 2,
                        "detail": f"MA5({_v(ma5,i)}) 上穿 MA20({_v(ma20,i)})"})
    elif _cross_down(ma5, ma20, i):
        signals.append({"name": "MA死叉", "action": "卖", "strength": 2,
                        "detail": f"MA5({_v(ma5,i)}) 下穿 MA20({_v(ma20,i)})"})

    # MA trend: price vs MA20
    if ma20[i] is not None:
        if closes[i] > ma20[i] * 1.02:
            signals.append({"name": "MA多头", "action": "买", "strength": 1,
                            "detail": f"价格在MA20上方 ({_v(ma20,i)})"})
        elif closes[i] < ma20[i] * 0.98:
            signals.append({"name": "MA空头", "action": "卖", "strength": 1,
                            "detail": f"价格在MA20下方 ({_v(ma20,i)})"})

    # ── MACD signals ──
    dif, dea = macd["dif"], macd["dea"]
    if _cross_up(dif, dea, i):
        extra = " (水下金叉, 强)" if (dif[i] or 0) < 0 else ""
        signals.append({"name": "MACD金叉", "action": "买", "strength": 2 if (dif[i] or 0) < 0 else 1,
                        "detail": f"DIF({_v(dif,i)}) 上穿 DEA({_v(dea,i)}){extra}"})
    elif _cross_down(dif, dea, i):
        signals.append({"name": "MACD死叉", "action": "卖", "strength": 2,
                        "detail": f"DIF({_v(dif,i)}) 下穿 DEA({_v(dea,i)})"})

    # ── RSI signals ──
    r6 = rsi6[i]
    if r6 is not None:
        if r6 < 20:
            signals.append({"name": "RSI超卖", "action": "买", "strength": 2,
                            "detail": f"RSI6={r6} < 20"})
        elif r6 < 30:
            signals.append({"name": "RSI偏低", "action": "买", "strength": 1,
                            "detail": f"RSI6={r6} < 30"})
        elif r6 > 80:
            signals.append({"name": "RSI超买", "action": "卖", "strength": 2,
                            "detail": f"RSI6={r6} > 80"})
        elif r6 > 70:
            signals.append({"name": "RSI偏高", "action": "卖", "strength": 1,
                            "detail": f"RSI6={r6} > 70"})

    # ── KDJ signals ──
    kv, dv, jv = kdj["k"], kdj["d"], kdj["j"]
    if _cross_up(kv, dv, i):
        extra = " (超卖区, 强)" if (jv[i] or 50) < 20 else ""
        signals.append({"name": "KDJ金叉", "action": "买", "strength": 2 if (jv[i] or 50) < 20 else 1,
                        "detail": f"K({_v(kv,i)}) 上穿 D({_v(dv,i)}), J={_v(jv,i)}{extra}"})
    elif _cross_down(kv, dv, i):
        signals.append({"name": "KDJ死叉", "action": "卖", "strength": 1,
                        "detail": f"K({_v(kv,i)}) 下穿 D({_v(dv,i)}), J={_v(jv,i)}"})

    if jv[i] is not None and jv[i] > 100:
        signals.append({"name": "J值超买", "action": "卖", "strength": 1,
                        "detail": f"J={_v(jv,i)} > 100"})
    elif jv[i] is not None and jv[i] < 0:
        signals.append({"name": "J值超卖", "action": "买", "strength": 1,
                        "detail": f"J={_v(jv,i)} < 0"})

    # ── Bollinger signals ──
    if boll["lower"][i] is not None:
        if closes[i] <= boll["lower"][i]:
            signals.append({"name": "触及布林下轨", "action": "买", "strength": 2,
                            "detail": f"价格{closes[i]} ≤ 下轨{_v(boll['lower'],i)}"})
        elif closes[i] >= boll["upper"][i]:
            signals.append({"name": "触及布林上轨", "action": "卖", "strength": 2,
                            "detail": f"价格{closes[i]} ≥ 上轨{_v(boll['upper'],i)}"})

    # ── Summary ──
    buy_pts = sum(s["strength"] for s in signals if s["action"] == "买")
    sell_pts = sum(s["strength"] for s in signals if s["action"] == "卖")
    net = buy_pts - sell_pts
    if net >= 3:
        verdict = "买入"
    elif net <= -3:
        verdict = "卖出"
    else:
        verdict = "观望"

    indicators = {
        "ma5": _v(ma5, i), "ma10": _v(ma10, i),
        "ma20": _v(ma20, i), "ma60": _v(ma60, i),
        "macd": {"dif": _v(dif, i), "dea": _v(dea, i), "hist": _v(macd["hist"], i)},
        "rsi6": _v(rsi6, i), "rsi12": _v(rsi12, i),
        "kdj": {"k": _v(kv, i), "d": _v(dv, i), "j": _v(jv, i)},
        "boll": {
            "upper": _v(boll["upper"], i),
            "mid": _v(boll["mid"], i),
            "lower": _v(boll["lower"], i),
        },
    }

    return {
        "indicators": indicators,
        "signals": signals,
        "summary": {
            "buy_count": sum(1 for s in signals if s["action"] == "买"),
            "sell_count": sum(1 for s in signals if s["action"] == "卖"),
            "buy_strength": buy_pts,
            "sell_strength": sell_pts,
            "net_signal": net,
            "verdict": verdict,
        },
    }


def _v(arr: list, idx: int):
    """Safe value getter — returns value or None."""
    if idx < 0 or idx >= len(arr):
        return None
    return arr[idx]


def _empty_summary() -> dict:
    return {
        "buy_count": 0, "sell_count": 0,
        "buy_strength": 0, "sell_strength": 0,
        "net_signal": 0, "verdict": "观望",
    }
