# YYKANPAN Dashboard Cards — Complete Specification

> 14 cards total. Each card is draggable, collapsible, and hideable.

---

## 1. `stats` — 行情概览 (Market Overview)

| Field | Value |
|-------|-------|
| API | None (client-side aggregation from `/api/stocks`) |
| Refresh | On every `refreshAllCards()` cycle |
| Badge | — |

**Displays:**
- 持仓总数、涨/跌/平家数
- 最强/最弱个股（ticker + change_pct）
- 组合市值 (MV)、盈亏 (P&L)、组合涨跌幅
- 涨停/跌停数、昨日涨停胜率
- 情绪阶段 + 交易建议文字

**Data Flow:** stock cards → compute in `updateStats()` → write to `store.stats.*` → petite-vue binds to DOM.

---

## 2. `macro` — 宏观风向标 (Macro Indicators)

| Field | Value |
|-------|-------|
| API | `GET /api/macro` |
| Backend | `_fetch_macro_indicators()` — Sina hq.sinajs.cn |
| Refresh | On `refreshAllCards()` |
| Badge | 宏观 |

**Response:**
```json
[{"name": "上证指数", "price": 3200.5, "unit": "", "change": 12.3, "change_pct": 0.39, "prev": 3188.2}, ...]
```

**Indicators:** 上证指数, 美元/人民币, 国际金价, 原油价格

**Rendering:** Horizontal `.macro-chip` divs — name + price + colored arrow + change_pct.

---

## 3. `ai-edge` — AI 核心策略引擎 (AI Core Strategy Engine)

| Field | Value |
|-------|-------|
| API | `GET /api/ai-edge?refresh=1` |
| Backend | `_build_ai_edge_report()` |
| Refresh | On `refreshAllCards()` |
| Badge | Core Edge |

**Response:**
```json
{
  "ok": true, "generated_at": "2026-05-12 09:35",
  "summary": {"market_bias": "偏多", "confidence": 72.5, "coverage": 15, "up_count": 10, "down_count": 5, "avg_change_pct": 1.2},
  "focus": [{"ticker": "...", "name": "...", "change_pct": 3.5}],
  "risks": [...],
  "playbook": ["优先观察强势股回踩后的承接..."]
}
```

**Logic:** confidence = 60 + breadth×25 + avg×6 − volatility_penalty. Clamped [10, 95].

**Market bias rules:**
- avg ≥ 1% AND up ≥ 60% → "偏多"
- avg ≤ -1% AND down ≥ 60% → "偏空"
- else → "中性震荡"

---

## 4. `watchdog` — Watchdog 提醒系统 (Alert System)

| Field | Value |
|-------|-------|
| API | None (client-side only) |
| Config | localStorage `watchdog_config` |
| Badge | 🚨 |

**Features:**
- Traffic light: 🟢 normal / 🟡 watch / 🔴 alert
- Configurable thresholds: daily change %, P&L %
- Browser `Notification` API triggers on breach
- Manual "巡逻" button for instant check

**Trigger logic:** Scans all stock cards — if any stock's `change_pct` ≥ threshold OR P&L% ≥ threshold → elevate light.

---

## 5. `limit-stats` — 涨跌停 & 昨日涨停表现 (Limit Stats)

| Field | Value |
|-------|-------|
| API | `GET /api/limit-stats` |
| Backend | `_get_limit_stats()` — AkShare `stock_zt_pool_em` / `stock_zt_pool_previous_em` |
| Refresh | On `refreshAllCards()` |
| Badge | 短线核心 |

**Response:**
```json
{
  "ok": true, "date": "2026-05-12",
  "limit_up": 45, "limit_down": 3,
  "consecutive_boards": 8, "max_board": 5,
  "yesterday_limit_up_performance": {
    "total": 40, "up": 22, "down": 15, "flat": 3,
    "avg_change_pct": 1.2, "profit_rate": 55.0,
    "verdict": "弱转强"
  }
}
```

---

## 6. `sentiment` — A股情绪判断 (Market Sentiment)

| Field | Value |
|-------|-------|
| API (auto) | `GET /api/market-sentiment-auto` |
| API (manual) | `POST /api/market-sentiment` |
| API (history) | `GET /api/sentiment-history?days=30` |
| API (config) | `GET/POST /api/sentiment-config` |
| Backend | `_evaluate_market_sentiment()`, iWenCai + AkShare |
| Badge | — |

**Sentiment stages:** 上升 → 分歧 → 退潮 (cycle)

**Scoring (score range -4 ~ +4):**
- up_ratio, limit_up_count, consecutive boards → positive
- down_ratio dominant → negative

**Thresholds configurable:** bull/bear/neutral presets stored in `data/sentiment_config.json`.

**History:** Appended to `data/sentiment_history.json` on each evaluation. SVG sparkline chart rendered client-side.

---

## 7. `mainline` — 主线板块自动判断 (Mainline Sector)

| Field | Value |
|-------|-------|
| API | `GET /api/mainline-auto` |
| Backend | `_analyze_mainline_auto()` |
| Refresh | On `refreshAllCards()` |
| Badge | 主线 |

**Response:**
```json
{
  "ok": true, "generated_at": "...",
  "mainline_sector": "新能源",
  "leader_stock": {"name": "宁德时代", "code": "300750", "change_pct": 4.2},
  "tradable_text": "可参与",
  "reason": "板块内3只涨停...",
  "suggestion": "关注龙头回踩机会"
}
```

---

## 8. `brief` — 智能简报 (Smart Brief)

| Field | Value |
|-------|-------|
| API | `GET /api/auto-brief?refresh=1` |
| Backend | `_build_auto_brief()` |
| Refresh | On `refreshAllCards()` |
| Badge | 智能简报 |

**Response:**
```json
{
  "ok": true, "generated_at": "...",
  "snapshot": {"total": 20, "valid": 18, "error": 2, "avg_change_pct": 0.8, "regime": "偏强"},
  "highlights": ["市场温度：偏强（平均涨跌幅 0.8%）", ...],
  "actions": ["人话建议：偏强环境下..."],
  "headline_analysis": [{"title": "...", "impact": "利好", "tags": ["政策"]}]
}
```

**Regime rules:** same as ai-edge (avg ≥ 1% + up ≥ 60% → "偏强", etc.)

---

## 9. `invest-tip` — 投资锦囊 (Investment Tips)

| Field | Value |
|-------|-------|
| API | None (pure frontend) |
| Data | Hardcoded `INVEST_TIPS[]` array (~40 quotes) |
| Badge | 每日一悟 |

**Features:**
- Random tip on load
- "换一条" button → next random (no repeat)
- Format: quote text + source attribution

---

## 10. `bazi` — 今日八字 (Daily Four Pillars)

| Field | Value |
|-------|-------|
| API | `GET /api/bazi` |
| Backend | `BaziCalculator` (天干地支 calendar engine) |
| Refresh | Once at boot + midnight |
| Badge | 四柱 |

**Response:**
```json
{
  "ok": true,
  "solar": "2026年5月12日", "lunar": "四月十六",
  "terms": "立夏",
  "pillars": [{"label": "年柱", "value": "丙午"}, ...],
  "nayin": "天河水",
  "wuyun": {
    "sui_yun": "...", "sitian": "...", "zaiquan": "...",
    "period_name": "三之气", "host_qi": "...", "guest_qi": "...",
    "comment": "...", "health_tip": "...", "trading_tip": "..."
  }
}
```

---

## 11. `xgxz` — 新股新债 (IPO & Bond Subscription)

| Field | Value |
|-------|-------|
| API | `GET /api/xingu-xinzhai` |
| Backend | `_fetch_xingu_xinzhai()` — East Money datacenter API |
| Refresh | Once at boot + midnight (daily cache) |
| Badge | 打新 |

**Response:**
```json
{
  "ok": true, "date": "2026-05-12",
  "ipo": [{"code": "...", "name": "...", "apply_date": "2026-05-12", "price": 25.6, "win_rate": "0.03%", "multiple": 1200}],
  "bond": [{"code": "...", "name": "...", "apply_name": "...", "apply_date": "...", "list_date": "...", "win_rate": "0.02%"}]
}
```

**Filters:** Last 3 days + future only. Cap 8 per section.

**Rendering:** Two tables with date-based row styling (`.xgxz-today` blue, `.xgxz-future` accent, `.xgxz-past` muted).

---

## 12. `advisor` — 参谋信号 (Trading Advisor)

| Field | Value |
|-------|-------|
| API | `GET /api/advisor?risk_pref=balanced&positions=[...]` |
| Backend | `adv.evaluate_portfolio()` from `src/advisor.py` |
| Refresh | Manual button click |
| Badge | Advisor |

**See:** [docs/advisor-spec.md](advisor-spec.md) for full strategy spec.

**Response:**
```json
{
  "ok": true, "generated_at": "...", "strategy": "rule_v1",
  "portfolio_action": "observe", "portfolio_reason": "...",
  "signals": [{"ticker": "...", "name": "...", "action": "hold", "strength": 1, "reasons": [...], "stop_loss": null, "take_profit": null}],
  "context": {"regime": "震荡", "sentiment_stage": "分歧", "confidence": 65}
}
```

---

## 13. `risk-events` — 黑天鹅 / 灰犀牛 (Risk Radar)

| Field | Value |
|-------|-------|
| API | `GET /api/risk-events?period=today` |
| Backend | `_scan_risk_events()` — scans macro + stock data |
| Refresh | Manual "扫描" button |
| Badge | 风险雷达 |

**Response:**
```json
{
  "ok": true, "period": "today", "count": 2,
  "events": [{"type": "黑天鹅", "time": "...", "title": "...", "detail": "...", "severity": "high"}]
}
```

**Trigger thresholds:**
| Source | Threshold | Severity |
|--------|-----------|----------|
| 上证指数 | ≥ 3% | high |
| USD/CNY | ≥ 0.5% | medium |
| Gold | ≥ 2% | medium |
| Crude oil | ≥ 3% | medium |
| Individual stock | ≥ 5% or limit | high |

**Time periods:** 1h, today, 3d, 7d, 30d. In-memory `_RISK_EVENT_HISTORY[]`, auto-prune 30d.

---

## 14. `decisions` — 决策日志 (Decision Journal)

| Field | Value |
|-------|-------|
| API | `GET/POST /api/decisions`, `PUT/DELETE /api/decisions/<id>` |
| Backend | `src/decision.py` — JSON file storage |
| Refresh | On form submit / state change |
| Badge | Decision Journal |
| Layout | Wide card (`insight-card--wide`) |

**CRUD operations:**
- **Create:** POST `{title*, type, state, context, action, outcome, tags}`
- **Update:** PUT `{state?, outcome?, tags?}`
- **Delete:** DELETE
- **List:** GET `?type=trade&state=idea`

**Decision states:** idea → decided → acted → reviewed

**Views:**
- Kanban (4-column, drag-and-drop state transitions)
- List (flat table)

**Types:** trade | life | work

---

## Common Card Features

All cards share:
- **Draggable** (`draggable="true"`) — reorder via drag handle (⠇)
- **Collapsible** (−/+ button) — toggle card body
- **Hideable** (✕ button) — hide + show in restore bar
- **Restore bar** — "已隐藏: [+CardName]" chips to restore
- **localStorage persistence** — hidden state + card order saved
- **i18n map** — `CARD_NAMES{}` maps card-id → Chinese display name

---

## Architecture Notes

- **Frontend:** petite-vue 0.4.1 reactive store + vanilla JS IIFEs
- **Data sources:** Sina (primary), AkShare (fallback), Yahoo (last resort), East Money (xgxz), iWenCai (sentiment)
- **Refresh cycle:** `refreshAllCards()` with re-entrance guard + `.catch()` + midnight auto-refresh (respects quiet hours 23:00–06:00)
- **Timezone:** All times in Beijing UTC+8
