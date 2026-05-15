"""
analysis.py — Market analysis engines: AI edge, auto brief, mainline, news, macro, glossary.
"""

import re
import time

from urllib import request as urlrequest

from config import cfg
from time_utils import BeijingTime
from data.providers import with_retries, fetch_stock

try:
    import akshare as ak
except Exception:
    ak = None

# ── Constants (from config) ───────────────────────────────────────────────────
NEWS_FEEDS = cfg.NEWS_FEEDS

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

# ── Stocks snapshot cache ─────────────────────────────────────────────────────
STOCKS_CACHE_DATA = None
STOCKS_CACHE_TS = 0.0
STOCKS_CACHE_TTL_SECONDS = cfg.STOCKS_CACHE_TTL_SECONDS


def invalidate_stocks_cache() -> None:
    global STOCKS_CACHE_DATA, STOCKS_CACHE_TS
    STOCKS_CACHE_DATA = None
    STOCKS_CACHE_TS = 0.0


def get_stocks_snapshot(load_watchlist_fn, force_refresh: bool = False) -> list[dict]:
    global STOCKS_CACHE_DATA, STOCKS_CACHE_TS

    now = time.time()
    if (
        not force_refresh
        and STOCKS_CACHE_DATA is not None
        and (now - STOCKS_CACHE_TS) <= STOCKS_CACHE_TTL_SECONDS
    ):
        return STOCKS_CACHE_DATA

    wl = load_watchlist_fn()
    data = [fetch_stock(s["ticker"], s.get("name", "")) for s in wl]
    STOCKS_CACHE_DATA = data
    STOCKS_CACHE_TS = now
    return data


# ── Limit stats ──────────────────────────────────────────────────────────────
_LIMIT_STATS_CACHE: dict | None = None
_LIMIT_STATS_CACHE_TS: float = 0.0
_LIMIT_STATS_CACHE_TTL = cfg.LIMIT_STATS_CACHE_TTL_SECONDS


def get_limit_stats() -> dict:
    global _LIMIT_STATS_CACHE, _LIMIT_STATS_CACHE_TS

    now = time.time()
    if _LIMIT_STATS_CACHE and (now - _LIMIT_STATS_CACHE_TS) < _LIMIT_STATS_CACHE_TTL:
        return _LIMIT_STATS_CACHE

    date = BeijingTime.yyyymmdd()
    result: dict = {
        "ok": True, "date": date,
        "limit_up": None, "limit_down": None,
        "consecutive_boards": None, "max_board": None,
        "yesterday_limit_up_performance": None,
    }

    if ak is None:
        result["ok"] = False
        result["error"] = "AkShare 不可用"
        return result

    try:
        zt_df = with_retries(lambda: ak.stock_zt_pool_em(date=date))
        if zt_df is not None and not zt_df.empty:
            result["limit_up"] = len(zt_df)
            if "连板数" in zt_df.columns:
                boards = zt_df["连板数"].fillna(0).astype(int)
                result["consecutive_boards"] = int((boards >= 2).sum())
                result["max_board"] = int(boards.max())
    except Exception:
        pass

    try:
        dt_df = with_retries(lambda: ak.stock_zt_pool_dtgc_em(date=date))
        if dt_df is not None and not dt_df.empty:
            result["limit_down"] = len(dt_df)
    except Exception:
        pass

    try:
        zrzt_df = with_retries(lambda: ak.stock_zt_pool_previous_em(date=date))
        if zrzt_df is not None and not zrzt_df.empty:
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
                profit_rate = round(up / total * 100, 1) if total > 0 else 0

                result["yesterday_limit_up_performance"] = {
                    "total": total, "up": up, "down": down, "flat": flat,
                    "avg_change_pct": avg_chg, "profit_rate": profit_rate,
                    "verdict": (
                        "短线接力环境好" if profit_rate >= cfg.PROFIT_RATE_GOOD_THRESHOLD and avg_chg > 1
                        else "短线环境中性" if profit_rate >= cfg.PROFIT_RATE_NEUTRAL_THRESHOLD
                        else "短线周期走弱，谨慎追高"
                    ),
                }
    except Exception:
        pass

    _LIMIT_STATS_CACHE = result
    _LIMIT_STATS_CACHE_TS = now
    return result


# ── Sparkline history cache ──────────────────────────────────────────────────
_HISTORY_CACHE: dict = {}
_HISTORY_CACHE_TTL = cfg.HISTORY_CACHE_TTL_SECONDS


def get_history(ticker: str, days: int) -> dict:
    from data.providers import fetch_history_closes
    ticker = ticker.upper()
    now = time.time()
    cache_key = f"{ticker}_{days}"
    cached = _HISTORY_CACHE.get(cache_key)
    if cached and (now - cached["ts"]) < _HISTORY_CACHE_TTL:
        return cached["data"]

    closes = fetch_history_closes(ticker, days)
    result = {"ok": bool(closes), "ticker": ticker, "closes": closes}
    _HISTORY_CACHE[cache_key] = {"data": result, "ts": now}
    return result


# ── News & text analysis ─────────────────────────────────────────────────────

def _contains_any(text: str, words: list[str]) -> bool:
    return any(w in text for w in words)


def quickread_news(text: str) -> dict:
    t = (text or "").strip()
    if not t:
        return {"ok": False, "msg": "请输入新闻或财报内容"}

    lower = t.lower()
    summary = t[:cfg.NEWS_SUMMARY_MAX_LENGTH] + ("..." if len(t) > cfg.NEWS_SUMMARY_MAX_LENGTH else "")
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
        "ok": True, "summary": summary, "tags": tags,
        "impact": impact, "reason": reason,
        "plain": f"一句话：这条信息整体{impact}，核心原因是{reason}",
    }


def macro_impact(indicator: str, current: float | None, previous: float | None) -> dict:
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
        "ok": True, "indicator": ind,
        "current": current, "previous": previous,
        "delta": round(delta, 4), "tone": tone,
        "plain": f"人话：{ind.upper()} 从 {previous} 变到 {current}，整体{tone}。{explain}",
    }


def _fetch_market_headlines(limit: int = cfg.NEWS_HEADLINE_LIMIT) -> list[str]:
    headlines = []
    seen = set()

    for feed in NEWS_FEEDS:
        try:
            req = urlrequest.Request(feed, headers={"User-Agent": "Mozilla/5.0"})

            def _download():
                with urlrequest.urlopen(req, timeout=cfg.NEWS_FEED_TIMEOUT) as resp:
                    return resp.read().decode("utf-8", errors="ignore")

            xml_text = with_retries(_download)
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


# ── AI Edge report ────────────────────────────────────────────────────────────

def build_ai_edge_report(load_watchlist_fn, force_refresh: bool = False) -> dict:
    rows = get_stocks_snapshot(load_watchlist_fn, force_refresh=force_refresh)
    valid = [r for r in rows if not r.get("error")]

    if not valid:
        return {"ok": False, "msg": "当前无可用行情数据，无法生成AI策略。"}

    up = [r for r in valid if (r.get("change_pct") or 0) > 0]
    down = [r for r in valid if (r.get("change_pct") or 0) < 0]
    avg = sum((r.get("change_pct") or 0) for r in valid) / len(valid)

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
        "generated_at": BeijingTime.datetime_str(),
        "summary": {
            "market_bias": market_bias, "confidence": confidence,
            "avg_change_pct": round(avg, 2),
            "up_count": len(up), "down_count": len(down), "coverage": len(valid),
        },
        "focus": [
            {"ticker": r.get("ticker"), "name": r.get("name"),
             "change_pct": round(float(r.get("change_pct") or 0), 2), "source": r.get("source")}
            for r in focus_list
        ],
        "risks": [
            {"ticker": r.get("ticker"), "name": r.get("name"),
             "change_pct": round(float(r.get("change_pct") or 0), 2), "source": r.get("source")}
            for r in risk_list
        ],
        "playbook": playbook,
    }


# ── Auto brief ────────────────────────────────────────────────────────────────

def build_auto_brief(load_watchlist_fn, force_refresh: bool = False) -> dict:
    rows = get_stocks_snapshot(load_watchlist_fn, force_refresh=force_refresh)
    valid = [r for r in rows if not r.get("error")]
    errors = [r for r in rows if r.get("error")]

    if not valid:
        return {"ok": False, "msg": "当前无可用行情数据，请稍后重试。", "error_count": len(errors)}

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
        q = quickread_news(h)
        headline_analysis.append({
            "title": h, "impact": q.get("impact", "中性"), "tags": q.get("tags", []),
        })

    return {
        "ok": True,
        "generated_at": BeijingTime.datetime_str(),
        "snapshot": {
            "total": len(rows), "valid": len(valid), "error": len(errors),
            "avg_change_pct": avg_change, "regime": regime,
        },
        "highlights": highlights,
        "actions": actions,
        "headline_analysis": headline_analysis,
    }


# ── Mainline sector analysis ─────────────────────────────────────────────────

def _normalize_code(code: str) -> str:
    c = str(code or "").strip().upper()
    if c.startswith("SZ") or c.startswith("SH") or c.startswith("BJ"):
        return c[2:]
    return c


def analyze_mainline_auto() -> dict:
    if ak is None:
        return {"ok": False, "msg": "AkShare 不可用"}

    date = BeijingTime.yyyymmdd()
    try:
        strong_df = with_retries(lambda: ak.stock_zt_pool_strong_em(date=date))
    except Exception:
        return {"ok": False, "msg": "自动分析失败：强势池数据暂不可用"}

    if strong_df is None or strong_df.empty:
        return {"ok": False, "msg": "自动分析失败：强势池为空"}

    gainers = None
    gainers_source = "stock_hot_up_em"
    try:
        gainers = with_retries(ak.stock_hot_up_em)
    except Exception:
        gainers = None

    if gainers is None or gainers.empty:
        try:
            gainers = with_retries(ak.stock_hot_rank_em)
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
        "generated_at": BeijingTime.datetime_str(),
        "mainline_sector": mainline_sector,
        "leader_stock": {
            "code": str(leader.get("代码")), "name": str(leader.get("名称")),
            "change_pct": round(float(leader.get("涨跌幅") or 0), 2),
            "turnover": int(float(leader.get("成交额") or 0)),
        },
        "tradable": tradable,
        "tradable_text": "值得参与" if tradable else "谨慎参与",
        "inputs_source": {"gainers": gainers_source, "turnover": "stock_zt_pool_strong_em"},
        "reason": (
            f"主线板块在成交额前排中占比约 {round(concentration * 100, 1)}%，"
            f"板块前排平均涨幅 {round(hot_strength, 2)}%。"
        ),
        "suggestion": suggestion,
        "sector_rank_top5": [
            {"sector": ind, "count": v["count"], "avg_pct": round(v["avg_pct"], 2),
             "turnover": int(v["turnover"])}
            for ind, v in ranked_industries[:5]
        ],
        "samples": {
            "gainers_top": [
                {"code": str(r.get("代码")), "name": str(r.get("股票名称")),
                 "change_pct": round(float(r.get("涨跌幅") or 0), 2)}
                for _, r in top_gainers.head(10).iterrows()
            ],
            "turnover_top": [
                {"code": str(r.get("代码")), "name": str(r.get("名称")),
                 "sector": str(r.get("所属行业")),
                 "change_pct": round(float(r.get("涨跌幅") or 0), 2),
                 "turnover": int(float(r.get("成交额") or 0))}
                for _, r in top_turnover.head(10).iterrows()
            ],
        },
    }
