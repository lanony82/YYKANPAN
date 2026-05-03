"""
sentiment.py — Market sentiment evaluation, history, and configurable thresholds.
"""

import json
import pathlib

from config import cfg
from time_utils import BeijingTime
from providers import with_retries

try:
    import akshare as ak
except Exception:
    ak = None

from urllib import request as urlrequest
from urllib import parse as urlparse
import re

# ── Paths (from config) ──────────────────────────────────────────────────────
BASE = pathlib.Path(__file__).resolve().parent.parent
SENTIMENT_CACHE_FILE = cfg.SENTIMENT_CACHE_PATH
_SENTIMENT_CONFIG_FILE = cfg.SENTIMENT_CONFIG_PATH
_SENTIMENT_HISTORY_FILE = cfg.SENTIMENT_HISTORY_PATH

# ── Configurable thresholds ───────────────────────────────────────────────────
SENTIMENT_THRESHOLDS = dict(cfg.SENTIMENT_THRESHOLDS)

SENTIMENT_LAST_KNOWN = dict(cfg.SENTIMENT_DEFAULTS)


# ── Config persistence ───────────────────────────────────────────────────────

def load_sentiment_config():
    global SENTIMENT_THRESHOLDS
    try:
        if _SENTIMENT_CONFIG_FILE.exists():
            with open(_SENTIMENT_CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            SENTIMENT_THRESHOLDS.update(saved)
    except Exception:
        pass


def save_sentiment_config():
    try:
        _SENTIMENT_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_SENTIMENT_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(SENTIMENT_THRESHOLDS, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ── Last-known cache ─────────────────────────────────────────────────────────

def load_sentiment_last_known() -> None:
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


def update_sentiment_last_known(metrics: dict) -> None:
    global SENTIMENT_LAST_KNOWN
    changed = False
    for k in ["up_count", "down_count", "limit_up_count", "consecutive_limit_count"]:
        if metrics.get(k) is not None:
            SENTIMENT_LAST_KNOWN[k] = metrics[k]
            changed = True
    if changed:
        SENTIMENT_LAST_KNOWN["updated_at"] = BeijingTime.datetime_str()
        _save_sentiment_last_known()


def merge_with_last_known(metrics: dict) -> tuple[dict, list[str]]:
    merged = dict(metrics)
    fallback_fields = []
    for k in ["up_count", "down_count", "limit_up_count", "consecutive_limit_count"]:
        if merged.get(k) is None and SENTIMENT_LAST_KNOWN.get(k) is not None:
            merged[k] = SENTIMENT_LAST_KNOWN[k]
            fallback_fields.append(k)
    return merged, fallback_fields


# ── Sentiment history ─────────────────────────────────────────────────────────

def load_sentiment_history() -> list:
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


def append_sentiment_history(result: dict) -> None:
    """Append a sentiment evaluation snapshot to history (max 1 per hour)."""
    history = load_sentiment_history()
    ts = BeijingTime.datetime_str()
    hour_key = ts[:13]  # "YYYY-MM-DD HH"
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


# ── Core evaluation ──────────────────────────────────────────────────────────

def evaluate_market_sentiment(
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
            "up_count": up_count, "down_count": down_count,
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


# ── Auto-fetch inputs ────────────────────────────────────────────────────────

def _fetch_iwencai_count(keyword: str, pattern: str) -> int | None:
    url = f"{cfg.IWENCAI_URL}?w={urlparse.quote(keyword)}"
    req = urlrequest.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        def _download():
            with urlrequest.urlopen(req, timeout=cfg.IWENCAI_TIMEOUT) as resp:
                return resp.read().decode("utf-8", errors="ignore")

        text = with_retries(_download)
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            return None
        return int(m.group(1))
    except Exception:
        return None


def get_market_sentiment_inputs_auto() -> dict:
    """Auto-fetch four metrics: up/down count, limit-up count, and consecutive-board count."""
    up_count = _fetch_iwencai_count("上涨家数", r"涨跌幅>0%\s*\((\d+)个\)")
    down_count = _fetch_iwencai_count("下跌家数", r"涨跌幅<0%\s*\((\d+)个\)")

    limit_up_count = None
    consecutive_limit_count = None

    try:
        date = BeijingTime.yyyymmdd()
        zt_df = with_retries(lambda: ak.stock_zt_pool_em(date=date)) if ak is not None else None
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


# ── Init on import ───────────────────────────────────────────────────────────
load_sentiment_config()
load_sentiment_last_known()
