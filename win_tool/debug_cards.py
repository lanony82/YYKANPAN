"""Test all 17 card APIs systematically."""
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
import sys

BASE = "http://localhost:5000"
TIMEOUT = 15
ONLY = None


def _parse_args():
    parser = argparse.ArgumentParser(description="Debug all card-related APIs")
    parser.add_argument("--base", default=BASE, help="API base URL (default: http://localhost:5000)")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="HTTP timeout seconds")
    parser.add_argument(
        "--only",
        default="",
        help="Comma-separated card names to run only, e.g. stats,macro,ai-edge",
    )
    return parser.parse_args()

def get(path):
    try:
        resp = urllib.request.urlopen(f"{BASE}{path}", timeout=TIMEOUT)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            return json.loads(body), e.code
        except:
            return {"raw": body[:200]}, e.code
    except Exception as e:
        return {"error": str(e)}, 0

def post(path, data=None):
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body,
                                headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            return json.loads(body), e.code
        except:
            return {"raw": body[:200]}, e.code
    except Exception as e:
        return {"error": str(e)}, 0

results = []

def test(card_name, method, path, data=None):
    if ONLY is not None and card_name not in ONLY:
        return None

    if method == "GET":
        r, code = get(path)
    else:
        r, code = post(path, data)
    ok = r.get("ok", None) if isinstance(r, dict) else None
    error = r.get("error", "") if isinstance(r, dict) else ""
    status = "OK" if (code == 200 and ok is not False) else "FAIL"
    if code == 0:
        status = "CONN_ERR"
    results.append((card_name, status, code, error))
    # Print compact summary
    symbol = "✓" if status == "OK" else "✗"
    extra = ""
    if isinstance(r, dict):
        # Show key metrics
        keys = [k for k in r if k not in ("ok", "error", "raw")]
        if len(keys) <= 6:
            extra = ", ".join(f"{k}={repr(r[k])[:40]}" for k in keys[:4])
        else:
            extra = f"{len(keys)} keys"
    print(f"  {symbol} [{code}] {method} {path} — {extra[:80]}")
    if status != "OK":
        print(f"       ERROR: {error or r}")
    return r


args = _parse_args()
BASE = args.base.rstrip("/")
TIMEOUT = args.timeout
ONLY = {x.strip() for x in args.only.split(",") if x.strip()} if args.only else None

# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("  CARD-BY-CARD API DEBUG")
print("=" * 60)
print(f"  BASE={BASE} TIMEOUT={TIMEOUT}s")
if ONLY:
    print(f"  ONLY={','.join(sorted(ONLY))}")

# 1. Stats Bar (行情概览) — uses /api/stocks
print("\n── 1. 行情概览 (Stats Bar) ──")
r = test("stats", "GET", "/api/stocks")

# 2. 宏观风向标 — /api/macro + /api/macro-history
print("\n── 2. 宏观风向标 (Macro) ──")
test("macro", "GET", "/api/macro")
test("macro-history", "GET", "/api/macro-history/sh000001")

# 3. AI核心策略 — /api/ai-edge
print("\n── 3. AI核心策略 (AI Edge) ──")
test("ai-edge", "GET", "/api/ai-edge")

# 4. Watchdog — client-side only, uses /api/stocks data
print("\n── 4. Watchdog ──")
print("  ℹ Client-side only (uses stocks data)")

# 5. 涨跌停 — /api/limit-stats
print("\n── 5. 涨跌停 (Limit Stats) ──")
test("limit-stats", "GET", "/api/limit-stats")

# 6. 情绪判断 — /api/market-sentiment-auto + manual + history + config
print("\n── 6. A股情绪 (Sentiment) ──")
test("sentiment-auto", "GET", "/api/market-sentiment-auto")
test("sentiment-history", "GET", "/api/sentiment-history")
test("sentiment-config", "GET", "/api/sentiment-config")
test("sentiment-manual", "POST", "/api/market-sentiment",
     {"up_count": 2800, "down_count": 2200, "limit_up_count": 60,
      "consecutive_limit_count": 15})

# 7. 主线板块 — /api/mainline-auto
print("\n── 7. 主线板块 (Mainline) ──")
test("mainline", "GET", "/api/mainline-auto")

# 8. 智能简报 — /api/auto-brief
print("\n── 8. 智能简报 (Brief) ──")
test("brief", "GET", "/api/auto-brief")

# 9. 投资锦囊 — /api/glossary
print("\n── 9. 投资锦囊 (Invest Tip) ──")
test("glossary", "GET", "/api/glossary")

# 10. 八字/五运六气 — /api/bazi
print("\n── 10. 八字 (Bazi/TCC) ──")
test("bazi", "GET", "/api/bazi")

# 11. 新股新债 — /api/xingu-xinzhai
print("\n── 11. 新股新债 (IPO/CB) ──")
test("xgxz", "GET", "/api/xingu-xinzhai")

# 12. AI决策面板 — /api/advisor
print("\n── 12. AI决策面板 (Advisor) ──")
test("advisor", "GET", "/api/advisor?positions=" + urllib.parse.quote(
    json.dumps([{"ticker": "600519.SS", "shares": 100, "cost": 1800}])))

# 13. 黑天鹅/灰犀牛 — /api/risk-events
print("\n── 13. 风险雷达 (Risk Events) ──")
test("risk-events", "GET", "/api/risk-events")
test("risk-events-3d", "GET", "/api/risk-events?period=3d")

# 14. 选股策略 — /api/screener + strategies
print("\n── 14. 选股策略 (Screener) ──")
test("screener-strats", "GET", "/api/screener/strategies")
test("screener", "GET", "/api/screener?strategy=golden_cross&limit=5")

# 15. 决策日志 — /api/decisions + analyze
print("\n── 15. 决策日志 (Decisions) ──")
test("decisions-list", "GET", "/api/decisions")
test("decisions-analyze", "GET", "/api/decisions/analyze")

# 16. 自动参谋 — /api/autodev/run + status + strategies
print("\n── 16. 自动参谋 (AutoDev) ──")
test("autodev-status", "GET", "/api/autodev/status")
test("strategies", "GET", "/api/strategies")
test("autodev-run", "POST", "/api/autodev/run",
     {"positions": [{"ticker": "600519", "shares": 100, "cost": 1800}],
      "strategy": "rule_v1", "risk_pref": "balanced"})

# 17. 分红日历 — check if endpoint exists
print("\n── 17. 分红日历 (Dividend) ──")
# The dividend card may be frontend-only or use advisor data
print("  ℹ Check if dedicated API exists...")
test("dividend", "GET", "/api/advisor?positions=" + urllib.parse.quote(
    json.dumps([{"ticker": "600519.SS", "shares": 100, "cost": 1800}])))

# Also test data source / provider endpoints
print("\n── Extra: 数据源管理 (Providers) ──")
test("providers-order", "GET", "/api/providers/order")

# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  SUMMARY")
print("=" * 60)
ok_count = sum(1 for _, s, _, _ in results if s == "OK")
fail_count = sum(1 for _, s, _, _ in results if s != "OK")
print(f"  Total: {len(results)} endpoints tested")
print(f"  ✓ OK: {ok_count}")
print(f"  ✗ FAIL: {fail_count}")
if fail_count:
    print("\n  Failed endpoints:")
    for name, status, code, error in results:
        if status != "OK":
            print(f"    {name}: [{code}] {error[:60]}")

sys.exit(1 if fail_count else 0)
