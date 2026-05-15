# YYKANPAN API Reference

> Base URL: `http://localhost:5000`  
> Content-Type: `application/json`  
> No authentication required (local single-user tool)  
> No CORS headers (same-origin only)

---

## Stock Management

### GET /api/stocks
Fetch all watchlist stocks with live prices.

**Response** `200`:
```json
[{
  "ticker": "600519.SS",
  "name": "贵州茅台",
  "price": 1800.0,
  "prev_close": 1790.0,
  "change": 10.0,
  "change_pct": 0.56,
  "volume": 12345678,
  "high52": 2000.0,
  "low52": 1500.0,
  "market_cap": 2260000000000,
  "date": "2026-05-12",
  "source": "sina",
  "error": null,
  "suggest": {
    "action": "持有",
    "tip": "处于52周高位区间",
    "target": 1850.0,
    "stop": 1750.0
  }
}]
```

---

### POST /api/stocks
Add a stock to the watchlist.

**Body**:
```json
{"ticker": "600519.SS", "name": "贵州茅台"}
```
- `ticker` (required)
- `name` (optional)

**Response** `200`:
```json
{"ok": true, "stock": {...}}
```

**Errors**:
- `{"ok": false, "msg": "已在列表中"}` — duplicate
- `400` — ticker missing

---

### DELETE /api/stocks/:ticker
Remove a stock from the watchlist.

**Response** `200`: `{"ok": true}`  
**Error** `404`: `{"ok": false, "error": "not found"}`

---

### GET /api/refresh/:ticker
Force-refresh a single stock's data.

**Response**: Single stock object (same structure as array item in GET /api/stocks).

---

### GET /api/history/:ticker
Get recent closing prices for sparkline chart.

**Params**: `days` (int, default=20, max=60)

**Response**:
```json
{"ok": true, "ticker": "600519.SS", "closes": [1780.0, 1785.5, ...]}
```

---

## Market Intelligence

### GET /api/auto-brief
Auto-generated market brief from watchlist data + news.

**Params**: `refresh=1` to force (bypasses cache)

**Response**:
```json
{
  "ok": true,
  "generated_at": "2026-05-12 14:30:00",
  "snapshot": {
    "total": 8, "valid": 8, "error": 0,
    "avg_change_pct": 0.5, "regime": "偏强"
  },
  "highlights": ["市场温度：偏强（平均涨跌幅 0.5%）", ...],
  "actions": ["人话建议：偏强环境下可优先看相对强势股..."],
  "headline_analysis": [{"title": "...", "impact": "中性", "tags": ["政策"]}]
}
```

---

### GET /api/ai-edge
AI strategy playbook with confidence score.

**Params**: `refresh=1` to force

**Response**:
```json
{
  "ok": true,
  "generated_at": "...",
  "summary": {
    "market_bias": "偏多",
    "confidence": 72.5,
    "avg_change_pct": 1.2,
    "up_count": 6, "down_count": 2,
    "coverage": 8
  },
  "focus": [{"ticker": "...", "name": "...", "change_pct": 5.0, "source": "sina"}],
  "risks": [{"ticker": "...", "name": "...", "change_pct": -3.2}],
  "playbook": ["优先观察强势股回踩后的承接..."]
}
```

---

### GET /api/mainline-auto
Auto-detect current market mainline sector.

**Response**:
```json
{
  "ok": true,
  "generated_at": "...",
  "mainline_sector": "半导体",
  "leader_stock": {"code": "300750", "name": "宁德时代", "change_pct": 4.2, "turnover": 500000000},
  "tradable": true,
  "tradable_text": "值得参与",
  "reason": "板块内3只涨停...",
  "suggestion": "关注龙头回踩机会",
  "sector_rank_top5": [...],
  "samples": {"gainers_top": [...], "turnover_top": [...]}
}
```

---

### GET /api/limit-stats
Today's limit-up/down statistics + yesterday's performance.

**Response**:
```json
{
  "ok": true, "date": "20260512",
  "limit_up": 45, "limit_down": 3,
  "consecutive_boards": 8, "max_board": 5,
  "yesterday_limit_up_performance": {
    "total": 30, "up": 18, "down": 10, "flat": 2,
    "avg_change_pct": 1.5, "profit_rate": 60.0,
    "verdict": "短线接力环境好"
  }
}
```

---

### GET /api/macro
Real-time macro indicators from Sina Finance.

**Response**:
```json
[
  {"symbol": "sh000001", "name": "上证指数", "price": 3200.5, "prev": 3190.0, "change": 10.5, "change_pct": 0.33, "unit": ""},
  {"symbol": "fx_susdcny", "name": "美元/人民币", "price": 7.1234, "prev": 7.12, "change": 0.003, "change_pct": 0.05, "unit": ""},
  {"symbol": "hf_GC", "name": "黄金(COMEX)", "price": 2350.0, "unit": "$/oz", ...},
  {"symbol": "hf_CL", "name": "原油(WTI)", "price": 78.5, "unit": "$/bbl", ...}
]
```

---

## Sentiment System

### GET /api/market-sentiment-auto
Auto-fetched market sentiment evaluation (iWenCai + AkShare).

**Response**:
```json
{
  "ok": true,
  "stage": "上升",
  "tradable": true,
  "tradable_text": "适合交易",
  "score": 3,
  "metrics": {"score": 3, "up_ratio": 0.65},
  "inputs": {"up_count": 2800, "down_count": 1500, "limit_up_count": 50, "consecutive_limit_count": 12},
  "reasons": ["上涨家数明显占优..."],
  "plain": "当前市场情绪处于上升阶段...",
  "inputs_source": {"up_down": "iwencai", "limit_up": "akshare.stock_zt_pool_em"},
  "fallback_fields": [],
  "last_known_updated_at": "2026-05-12 10:30"
}
```

**Error** (incomplete data):
```json
{"ok": false, "msg": "自动抓取不完整，缺少: limit_up_count", "inputs": {...}, "last_known": {...}}
```

---

### POST /api/market-sentiment
Manual sentiment evaluation with user-provided numbers.

**Body**:
```json
{
  "up_count": 2800,
  "down_count": 1500,
  "limit_up_count": 50,
  "consecutive_limit_count": 12
}
```

**Response**: Same structure as GET auto endpoint.  
**Error**: `{"ok": false, "msg": "四个输入都必须是整数"}`

---

### GET /api/sentiment-history
Historical sentiment data for trend chart.

**Params**: `days` (int, default=30)

**Response**:
```json
{
  "ok": true,
  "history": [
    {"ts": "2026-05-12 10:00", "score": 3, "stage": "上升", "up_ratio": 0.65, "inputs": {...}}
  ]
}
```

---

### GET /api/sentiment-config
Get current sentiment thresholds.

**Response**: `{"ok": true, "thresholds": {...}}`

---

### POST /api/sentiment-config
Update sentiment thresholds.

**Body**: JSON object with threshold key-value pairs.  
**Response**: `{"ok": true, "thresholds": {...updated...}}`

---

## Risk & Analysis

### GET /api/risk-events
Scan for black swan / grey rhino events.

**Params**: `period` = `1h` | `today` (default) | `3d` | `7d` | `30d`

**Response**:
```json
{
  "ok": true,
  "period": "today",
  "count": 2,
  "events": [{
    "type": "黑天鹅",
    "time": "2026-05-12 10:30",
    "title": "上证指数暴跌",
    "detail": "上证指数下跌3.5%，触发黑天鹅预警",
    "severity": "high"
  }]
}
```

---

### POST /api/quickread
News/earnings text analysis — NLP-free keyword approach.

**Body**: `{"text": "某公司发布超预期财报..."}`

**Response**:
```json
{
  "ok": true,
  "summary": "截断摘要(180字)...",
  "tags": ["超预期", "偏利好"],
  "impact": "偏正面",
  "reason": "出现超预期/改善信号...",
  "plain": "一句话总结"
}
```

---

### POST /api/macro-impact
Evaluate impact of macro indicator change.

**Body**:
```json
{"indicator": "cpi", "current": 2.5, "previous": 2.3}
```
- `indicator`: `"cpi"` | `"rate"` | `"earnings"`

**Response**:
```json
{
  "ok": true,
  "indicator": "cpi", "current": 2.5, "previous": 2.3, "delta": 0.2,
  "tone": "偏利空",
  "plain": "人话：CPI 从 2.3 变到 2.5，通胀压力上升..."
}
```

---

## Advisor (参谋)

### GET /api/advisor
Portfolio trading signal evaluation with explainable factor analysis.

**Params**:
- `risk_pref`: `"conservative"` | `"balanced"` (default) | `"aggressive"`
- `positions`: URL-encoded JSON array
  ```json
  [{"ticker": "600519.SS", "shares": 100, "cost": 1700}]
  ```

**Response**:
```json
{
  "ok": true,
  "generated_at": "2026-05-12 14:30:00",
  "strategy": "rule_v1",
  "portfolio_action": "观望",
  "portfolio_reason": "综合信号无明确方向，建议观望",
  "signals": [{
    "ticker": "600519.SS",
    "name": "贵州茅台",
    "action": "hold",
    "strength": 1,
    "reasons": ["无明显信号，建议持有观望"],
    "stop_loss": 1530.0,
    "take_profit": 2125.0,
    "factors": [
      {"name": "盈亏", "score": 1, "weight": 0.30, "detail": "浮盈 5.0%"},
      {"name": "价位", "score": 0, "weight": 0.15, "detail": "52周区间 60% 位置"},
      {"name": "风险", "score": 0, "weight": 0.25, "detail": "无风险事件"},
      {"name": "情绪", "score": 0, "weight": 0.20, "detail": "情绪: 分歧"},
      {"name": "趋势", "score": 0, "weight": 0.10, "detail": "市场: 震荡，信心: 50%"}
    ]
  }],
  "context": {"regime": "震荡", "sentiment_stage": "分歧", "confidence": 65.0},
  "msg": ""
}
```

Factor scores range from -2 (very bearish) to +2 (very bullish). Weights sum to 1.0.

### POST /api/advisor/save-decision
Save an advisor signal as a decision journal entry (auto-creates trade decision).

**Body**:
```json
{
  "ticker": "600519.SS",
  "name": "贵州茅台",
  "action": "sell",
  "reasons": ["浮亏 -12%，触及止损线"],
  "factors": [{"name": "盈亏", "score": -2, "weight": 0.3, "detail": "浮亏"}],
  "risk_pref": "balanced",
  "portfolio_action": "减仓",
  "price": 1700,
  "size": 1000,
  "stop_loss": 1530,
  "take_profit": 2125,
  "strength": 4
}
```

**Response**: `{"ok": true, "decision": {...}}`

The decision is created with:
- `action` mapped to BUY/SELL/HOLD
- `source` = "ai"
- `confidence` = strength / 5.0
- Trading fields: symbol, price, size, stop_loss, take_profit
- `trade_context`: { risk_pref, portfolio_action, factors }

---

## IPO & Bond (新股新债)

### GET /api/xingu-xinzhai
IPO and convertible bond subscription calendar.

**Response**:
```json
{
  "ok": true,
  "date": "2026-05-12",
  "ipo": [{
    "code": "301XXX",
    "name": "某科技",
    "apply_date": "2026-05-12",
    "price": 25.6,
    "win_rate": 0.03,
    "multiple": 1200
  }],
  "bond": [{
    "code": "123XXX",
    "name": "某转债",
    "apply_name": "某转",
    "apply_date": "2026-05-13",
    "list_date": "2026-06-01",
    "win_rate": 0.001
  }]
}
```

---

## Decision Journal (决策日志)

### GET /api/decisions
List decisions with optional filters.

**Params**: `type` (trade|life|work), `state` (idea|decided|acted|reviewed)

**Response**: `{"ok": true, "decisions": [...]}`

---

### POST /api/decisions
Create a new decision.

**Body**:
```json
{
  "title": "买入茅台",
  "type": "trade",
  "state": "idea",
  "context": "当时环境...",
  "action": "BUY",
  "outcome": "",
  "tags": ["白酒", "价值投资"],
  "symbol": "贵州茅台",
  "price": 1700,
  "size": 1000,
  "confidence": 0.7,
  "stop_loss": 1530,
  "take_profit": 2125,
  "max_drawdown": 0.15,
  "source": "manual",
  "trade_context": {"type": "breakout", "volume": "high"}
}
```
- `title` required
- Trade fields (symbol, price, size, confidence, stop_loss, take_profit, max_drawdown, source, trade_context) are optional and only stored for `type=trade`
- `source`: "manual" | "rule" | "ai"
- `confidence`: 0~1 (clamped)

**Response** `201`:
```json
{"ok": true, "decision": {"id": "abc123def456", "title": "买入茅台", ...}}
```

---

### PUT /api/decisions/:did
Update a decision.

**Body**: Any subset of decision fields.  
**Response**: `{"ok": true, "decision": {...}}`  
**Errors**: 400 (validation), 404 (not found)

---

### DELETE /api/decisions/:did
Delete a decision.

**Response**: `{"ok": true}`  
**Error** `404`: `{"ok": false, "error": "not found"}`

---

### POST /api/decisions/evaluate/:id
Evaluate a trade decision against current market price.

**Body**: `{"current_price": 35.5}`

**Response**:
```json
{
  "ok": true,
  "decision_id": "abc123",
  "symbol": "晶合集成",
  "entry_price": 33.7,
  "current_price": 35.5,
  "size": 1000,
  "pnl": 1800.0,
  "pnl_pct": 5.34,
  "hit_stop_loss": false,
  "hit_take_profit": false,
  "risk_ok": true,
  "verdict": "盈利",
  "confidence": 0.6,
  "source": "manual"
}
```

Verdict includes contextual insights:
- High-confidence loss → "高信心决策亏损，需复盘"
- Low-confidence win → "低信心决策盈利，可能运气"
- Max drawdown breach → "超过最大回撤容忍"

---

### GET /api/decisions/analyze
Analyze trade decisions for behavioral patterns.

**Params**: `type` (default: "trade")

**Response**:
```json
{
  "ok": true,
  "total": 15,
  "with_price": 12,
  "buys": 8,
  "sells": 4,
  "holds": 3,
  "avg_confidence": 0.58,
  "by_source": {"manual": 10, "ai": 5},
  "by_state": {"idea": 3, "decided": 2, "acted": 8, "reviewed": 2},
  "patterns": [
    {"type": "low_confidence", "label": "有 3 笔低信心决策（<40%），建议减少冲动交易", "severity": "warn", "count": 3},
    {"type": "no_stop_loss", "label": "有 5 笔买入没设止损，风控缺失", "severity": "danger", "count": 5},
    {"type": "no_review", "label": "有 8 笔已执行但未复盘，缺少反馈闭环", "severity": "info", "count": 8}
  ]
}
```

Pattern types: `low_confidence`, `no_stop_loss`, `no_review`, `ai_ratio`, `overtrading`

---

## AutoDev (自动决策循环)

### GET /api/strategies
List all available YAML strategy configurations.

**Response** `200`:
```json
{
  "ok": true,
  "strategies": [
    {
      "name": "rule_v1",
      "version": 1,
      "description": "基础规则引擎 — 5因子加权打分",
      "file": "rule_v1.yaml",
      "factors": 5
    },
    {
      "name": "conservative_v1",
      "version": 1,
      "description": "保守策略 — 重风控轻进攻",
      "file": "conservative.yaml",
      "factors": 5
    }
  ]
}
```

---

### POST /api/autodev/cycle
Execute one full AutoDev loop: observe → decide → act → evaluate → learn.

**Body**:
```json
{
  "strategy": "rule_v1",
  "risk_pref": "balanced",
  "positions": [
    {"ticker": "600519.SH", "name": "贵州茅台", "shares": 100, "cost": 1800, "price": 1600, "change_pct": -2.0, "high52": 2000, "low52": 1500, "volume": 50000}
  ],
  "context": {
    "regime": "偏强",
    "sentiment_stage": "上升",
    "sentiment_score": 3,
    "tradable": true,
    "confidence": 80,
    "risk_events": []
  },
  "current_prices": {"贵州茅台": 1650}
}
```

- `strategy` (default: "rule_v1") — strategy name matching `data/strategies/{name}.yaml`
- `risk_pref` (default: "balanced") — "conservative" | "balanced" | "aggressive"
- `positions` — array of position objects
- `context` — market context (regime, sentiment, risk events)
- `current_prices` (optional) — `{symbol: price}` for evaluating past decisions

**Response** `200`:
```json
{
  "ok": true,
  "cycle": {
    "observed_at": "2026-05-15 14:30:00",
    "strategy": "rule_v1",
    "version": 1,
    "risk_pref": "balanced",
    "signals_count": 1,
    "acted_count": 0,
    "evaluations_count": 0,
    "patterns_count": 2,
    "suggestions_count": 1
  },
  "signals": [{
    "ticker": "600519.SH",
    "name": "贵州茅台",
    "action": "hold",
    "strength": 1,
    "reasons": ["无明显信号，建议持有观望"],
    "factors": [
      {"name": "盈亏", "score": -1, "weight": 0.30, "detail": "浮亏 -11.1%"},
      {"name": "风险", "score": 0, "weight": 0.25, "detail": "无风险事件"}
    ]
  }],
  "decisions": [],
  "evaluations": [],
  "analysis": {
    "ok": true,
    "total": 5,
    "patterns": [{"type": "no_stop_loss", "label": "...", "severity": "danger", "count": 3}],
    "suggestions": [{"type": "weight_adjust", "factor": "风险", "direction": "increase", "reason": "3 笔决策未设止损"}]
  }
}
```

Decisions created by `act()` have `source="rule"`, `tags=["autodev", strategy_name]`.

**Error** `404`: `{"ok": false, "error": "Strategy 'xxx' not found"}`

---

### GET /api/autodev/status
Return available strategies and current AutoDev state.

**Response** `200`:
```json
{
  "ok": true,
  "strategies": [
    {"name": "rule_v1", "version": 1, "description": "基础规则引擎 — 5因子加权打分", "file": "rule_v1.yaml", "factors": 5}
  ]
}
```

---

## Bazi (八字)

### GET /api/bazi
Today's Four Pillars + Five Movements.

**Response**:
```json
{
  "ok": true,
  "solar": "2026年5月12日 周一",
  "lunar": "农历四月十六",
  "terms": "立夏 6天前 │ 15天后 小满",
  "pillars": [
    {"label": "年柱", "value": "丙午"},
    {"label": "月柱", "value": "癸巳"},
    {"label": "日柱", "value": "甲子"},
    {"label": "时柱", "value": "丙寅"}
  ],
  "nayin": "海中金",
  "wuyun": {
    "sui_yun": "...",
    "sitian": "...",
    "zaiquan": "...",
    "period_name": "三之气",
    "host_qi": "...",
    "guest_qi": "...",
    "comment": "...",
    "health_tip": "...",
    "trading_tip": "..."
  }
}
```

---

## Configuration & Providers

### GET /api/config/export
Download watchlist as JSON file.

**Response**: File download (`Content-Disposition: attachment`)
```json
{"watchlist": [...], "exported_at": "2026-05-12 14:30:00"}
```

---

### POST /api/config/import
Import watchlist from JSON.

**Body**: `{"watchlist": [{"ticker": "600519.SS", "name": "贵州茅台"}, ...]}`  
**Response**: `{"ok": true, "count": 8}`

---

### POST /api/providers/test
Benchmark all providers.

**Response**:
```json
{
  "results": [{"provider": "sina", "ok": true, "time_s": 0.45, "price": 1800.0, "error": null}, ...],
  "best": "sina",
  "current": ["sina", "akshare", "yahoo"]
}
```

---

### GET /api/providers/order
Get current provider priority order.

**Response**: `{"order": ["sina", "akshare", "yahoo"]}`

---

### POST /api/providers/order
Set provider priority order.

**Body**: `{"order": ["akshare", "sina", "yahoo"]}`  
**Response**: `{"ok": true, "order": [...]}`

---

### POST /api/providers/auto
Auto-determine best provider order via benchmark.

**Response**: `{"ok": true, "order": [...], "results": [...]}`

---

## Utilities

### GET /api/glossary
Financial term glossary.

**Params**: `term` (optional, e.g. `cpi`)

**Response (no term)**: `{"ok": true, "terms": ["beta", "bps", "cpi", ...]}`  
**Response (with term)**: `{"ok": true, "term": "cpi", "plain": "消费者物价指数..."}`  
**Error**: `{"ok": false, "term": "xxx", "plain": "未收录该术语"}`

---

## Stock Screener

### GET /api/screener/strategies
List available screening strategies.

**Response** `200`:
```json
{
  "ok": true,
  "strategies": [
    {"key": "golden_cross", "name": "均线金叉", "desc": "MA5 上穿 MA20，放量确认", "icon": "✦"},
    {"key": "volume_breakout", "name": "放量突破", "desc": "量比>2，价格突破20日最高", "icon": "⚡"},
    {"key": "oversold_bounce", "name": "超跌反弹", "desc": "RSI<30 + 当日放量阳线", "icon": "↗"},
    {"key": "limit_up_relay", "name": "涨停接力", "desc": "昨日涨停，今日高开3%+", "icon": "🔥"}
  ]
}
```

### GET /api/screener
Run a screening strategy.

**Params**:
- `strategy` — one of `golden_cross`, `volume_breakout`, `oversold_bounce`, `limit_up_relay` (default: `golden_cross`)
- `limit` — max results, 1–50 (default: `20`)

**Response** `200`:
```json
{
  "ok": true,
  "strategy": "golden_cross",
  "name": "均线金叉",
  "desc": "MA5 上穿 MA20，放量确认",
  "icon": "✦",
  "hits": [
    {
      "code": "600519",
      "name": "贵州茅台",
      "ticker": "600519.SS",
      "price": 1800.0,
      "change_pct": 2.35,
      "score": 85,
      "reasons": ["MA5(1795.00)上穿MA20(1760.00)", "量比 1.8"]
    }
  ],
  "scanned": "沪深300 (300只)",
  "ts": "2026-05-14 10:30"
}
```

**Error**: `{"ok": false, "msg": "未知策略: xxx"}`

---

## Technical Signals (技术指标)

### GET /api/signals/:ticker
Get technical indicators and trading signals for a stock.

**Response** `200`:
```json
{
  "ok": true,
  "ticker": "600519.SS",
  "last_price": 1800.0,
  "last_day": "2026-05-15",
  "indicators": {"ma5": 1795.0, "ma20": 1760.0, "rsi6": 65.2, ...},
  "signals": [{"name": "MA金叉", "type": "buy", "detail": "MA5上穿MA20"}, ...],
  "summary": {"verdict": "观望", "buy_count": 2, "sell_count": 1}
}
```

**Error**: `{"ok": false, "ticker": "...", "msg": "无历史数据"}`

Cache: 5 minutes per ticker.

---

## Macro History

### GET /api/macro-history/:symbol
Get recent closing prices for a macro indicator (for sparkline).

**Params**: `days` (int, default=20, max=260)

**Response**:
```json
{"ok": true, "symbol": "sh000001", "closes": [3180.0, 3195.5, ...]}
```

**Error** `400`: `{"ok": false, "error": "unknown symbol"}`

---

## Summary Table

| # | Method | Path | Purpose |
|---|--------|------|---------|
| 1 | GET | `/api/stocks` | All watchlist stocks |
| 2 | POST | `/api/stocks` | Add stock |
| 3 | DELETE | `/api/stocks/:ticker` | Remove stock |
| 4 | GET | `/api/refresh/:ticker` | Refresh one stock |
| 5 | GET | `/api/history/:ticker` | Price history |
| 6 | GET | `/api/signals/:ticker` | Technical signals |
| 7 | GET | `/api/auto-brief` | Smart brief |
| 8 | GET | `/api/ai-edge` | AI playbook |
| 9 | GET | `/api/mainline-auto` | Mainline sector |
| 10 | GET | `/api/limit-stats` | Limit stats |
| 11 | GET | `/api/macro` | Macro indicators |
| 12 | GET | `/api/macro-history/:symbol` | Macro sparkline |
| 13 | GET | `/api/market-sentiment-auto` | Auto sentiment |
| 14 | POST | `/api/market-sentiment` | Manual sentiment |
| 15 | GET | `/api/sentiment-history` | Sentiment trend |
| 16 | GET/POST | `/api/sentiment-config` | Thresholds |
| 17 | GET | `/api/risk-events` | Risk radar |
| 18 | POST | `/api/quickread` | News analysis |
| 19 | POST | `/api/macro-impact` | Macro impact |
| 20 | GET | `/api/advisor` | Trading advisor (explainable) |
| 21 | POST | `/api/advisor/save-decision` | Save signal → journal |
| 23 | GET | `/api/xingu-xinzhai` | IPO/bond |
| 24 | GET/POST/PUT/DELETE | `/api/decisions` | Decision journal CRUD |
| 25 | POST | `/api/decisions/evaluate/:id` | Evaluate trade decision |
| 26 | GET | `/api/decisions/analyze` | Decision pattern analysis |
| 27 | GET | `/api/bazi` | Daily bazi |
| 28 | GET | `/api/config/export` | Export config |
| 29 | POST | `/api/config/import` | Import config |
| 30 | POST | `/api/providers/test` | Provider benchmark |
| 31 | GET/POST | `/api/providers/order` | Provider order |
| 32 | POST | `/api/providers/auto` | Auto-order providers |
| 33 | GET | `/api/glossary` | Term glossary |
| 34 | GET | `/api/screener/strategies` | Screener strategies |
| 35 | GET | `/api/screener` | Run stock screen |
