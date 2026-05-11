# Patch and Fix History

This file records code patches and production fixes for this project.

## Run Commands

Use this block in each patch entry to capture exact run commands used.

- Before:
  - App: python src/server.py
  - Collect: python src/collect_stocks.py
  - Summary: python src/summary.py
- After:
  - App: python src/server.py
  - Collect: python src/collect_stocks.py
  - Summary: python src/summary.py
- Verification:
  - Health check: Invoke-WebRequest http://127.0.0.1:5000/
  - API check: Invoke-RestMethod http://127.0.0.1:5000/api/stocks

## 2026-04-28

### 1. Improved stock quote network resilience
- File: app.py
- Type: Fix
- Summary:
  - Added retry logic for transient network failures (reset/timeout style errors).
  - Added Sina quote fallback for A-share tickers.
  - Updated provider order for A-share symbols: Yahoo -> AkShare -> Sina.
- Why:
  - Yahoo and AkShare calls intermittently failed due connection reset/remote close errors.
  - The app needed a fallback path to avoid hard errors in API responses.
- Validation:
  - app.py syntax check succeeded.
  - fetch_stock("600519.SS") returned valid data via Sina fallback.
  - API check on /api/refresh/600519.SS returned error=null.

### 2. Added 10-minute backend API cache
- File: app.py
- Type: Improvement
- Summary:
  - Added in-memory cache for /api/stocks with a TTL of 600 seconds.
  - Added cache invalidation when watchlist changes (add/remove).
  - Added cache invalidation when manually refreshing one ticker.
- Why:
  - Repeated full-table requests were slow due upstream quote-provider latency.
  - A short backend cache speeds UI rendering and reduces repeated provider calls.
- Validation:
  - app.py syntax check succeeded.
  - Benchmark of two consecutive /api/stocks calls: first_ms=186818, second_ms=6.

### 3. Improved CSV collector reliability and retention
- File: src/collect_stocks.py
- Type: Improvement
- Summary:
  - Reused app-level quote fetch logic with multi-provider fallback.
  - Default watchlist source now prefers watchlist_cn.json (fallback to watchlist.txt).
  - Added automatic retention: keep latest 5 daily CSV files.
- Why:
  - Daily collection had frequent Yahoo-only failures and produced mostly error rows.
  - Needed consistent collection behavior aligned with web app data providers.
  - Needed automatic cleanup of old CSV files.
- Validation:
  - Collector run completed with successful quote rows for 8 A-share tickers.
  - Output saved to data/2026-04-28.csv.
  - Console confirmed: "Retention -> kept latest 5 daily files".

### 4. Moved Python codebase into src/
- File: src/app.py, src/collect_stocks.py, src/summary.py, daily_collect.ps1
- Type: Refactor
- Summary:
  - Moved app.py, collect_stocks.py, summary.py into src/.
  - Updated path resolution to project-root assets/data/watchlists after move.
  - Updated scheduler script target to src/collect_stocks.py.
- Why:
  - Keep repository root cleaner and align with common src layout.
  - Avoid broken relative paths after module relocation.
- Validation:
  - Syntax compile passed for src/app.py, src/collect_stocks.py, src/summary.py.
  - Service starts successfully using python src/app.py.
  - Local HTTP check returned status code 200 on http://127.0.0.1:5000/.

### 5. Added financial interpretation APIs and UI tools
- File: src/app.py, static/index.html
- Type: Improvement
- Summary:
  - Added /api/quickread for one-click news/earnings plain-language interpretation.
  - Added /api/macro-impact for CPI/rate/earnings impact analysis.
  - Added /api/glossary for plain-language finance term explanation.
  - Added three matching UI cards in the dashboard.
- Why:
  - Reduce manual analysis effort and provide human-readable interpretation directly in the app.
- Validation:
  - API calls for quickread, macro-impact, and glossary returned expected JSON.
  - Fixed quickread sentiment direction for “CPI up + rate hike concern” scenario.

### 6. Added auto brief mode with periodic refresh
- File: src/app.py, static/index.html
- Type: Improvement
- Summary:
  - Added /api/auto-brief to auto-summarize market state from current holdings.
  - Included highlights, action suggestions, and headline scan.
  - Added UI panel with manual refresh and scheduled refresh.
  - Updated refresh cadence to every 30 minutes while keeping manual refresh available.
- Why:
  - Minimize user input and provide proactive, recurring market context.
- Validation:
  - /api/auto-brief returns structured brief content with snapshot/highlights/actions.

### 7. Added A-share sentiment engine (manual + auto)
- File: src/app.py, static/index.html
- Type: Improvement
- Summary:
  - Added /api/market-sentiment (manual inputs: up/down/limit-up/consecutive-limit).
  - Added /api/market-sentiment-auto (automatic data collection + sentiment evaluation).
  - Added sentiment UI card and top summary chips (stage + tradable recommendation).
  - Added auto-refresh every 30 minutes and manual refresh button.
- Why:
  - Provide consistent “stage + tradable” output without repeated manual calculations.
- Validation:
  - Sample strong-market input classified as stage=上升 and tradable=适合交易.
  - Auto endpoint returns complete sentiment payload when sources are available.

### 8. Added auto mainline sector and leader analysis
- File: src/app.py, static/index.html
- Type: Improvement
- Summary:
  - Added /api/mainline-auto to infer mainline sector, leader stock, and participation advice.
  - Uses gainers + turnover leaders and ranks sectors by concentration/strength.
  - Added fallback data-source chain when primary gainers source is unavailable.
  - Added UI card with manual and 30-minute auto refresh.
- Why:
  - Automatically answer: current mainline, leader, and whether worth participating.
- Validation:
  - Endpoint returns sector, leader, tradable_text, reason, suggestion, and source metadata.

### 9. Persisted sentiment last-known values to local file
- File: src/app.py, data/sentiment_last_known.json, static/index.html
- Type: Fix
- Summary:
  - Added local persistence for last-known sentiment metrics.
  - Loads cache on startup and writes updates after successful metric refresh.
  - Auto sentiment now falls back to persisted values when live source is unstable.
  - Frontend displays fallback note when cached values are used.
- Why:
  - Stabilize auto sentiment output under intermittent upstream/network failures.
  - Preserve usability across service restarts.
- Validation:
  - /api/market-sentiment-auto returns ok=true with fallback_fields when live fetch is partial.
  - data/sentiment_last_known.json is created and updated with latest values.

### 10. Unified Beijing timezone behavior (UTC+8)
- File: src/app.py, src/collect_stocks.py, src/summary.py, static/index.html
- Type: Fix
- Summary:
  - Backend now generates date/time using explicit Beijing timezone helpers.
  - Collector and summary default "today" file resolution now use UTC+8 date.
  - Frontend now displays timestamp labels with explicit UTC+8 suffix.
  - Added frontend quiet-window control to skip auto refresh during 15:30-08:30 (UTC+8).
- Why:
  - Keep backend and frontend time interpretation consistent across different host machine timezones.
  - Avoid unnecessary overnight/off-session auto-refresh traffic while preserving manual refresh.
- Validation:
  - Collector log shows timezone-aware banner: "Collecting ... (Beijing UTC+8)".
  - Frontend header and analysis cards show UTC+8-labeled timestamps.

### 11. Added smoke regression test suite
- File: tests/smoke_test.py, README.md
- Type: Improvement
- Summary:
  - Added runnable smoke regression test using unittest and Flask test_client.
  - Covers core local endpoints and validates auto endpoints return JSON payloads.
  - Includes timezone helper format checks for Beijing date/time helpers.
  - Documented command in README: python tests/smoke_test.py.
- Why:
  - Provide fast regression guardrail for core API contracts after iterative patching.
- Validation:
  - Local run completed: Ran 7 tests, OK.

### 12. Enhanced Markdown runbook documentation
- File: README.md, PATCH_HISTORY.md
- Type: Improvement
- Summary:
  - Expanded README with quick start, operations checklist, and expected runtime behaviors.
  - Clarified CSV behavior (same-day overwrite) and retention behavior (keep latest 5, no archive by default).
  - Added practical smoke-test guidance and expected-output interpretation.
  - Updated patch history to include this documentation enhancement.
- Why:
  - Reduce repeated confusion during operations and make onboarding/debugging faster.
- Validation:
  - README sections render correctly and commands align with current src-based structure.

### 13. Implemented first-priority frontend upgrades
- File: static/index.html, README.md
- Type: Improvement
- Summary:
  - Added P&L display with optional position fields (shares/cost) and total position summary chips.
  - Added Watchdog reminder system with configurable thresholds and optional browser notification.
  - Added A-share / US-style color mode toggle (红涨绿跌 <-> 绿涨红跌) with persistence.
  - Added visible auto-refresh status badge for quiet-window behavior.
- Why:
  - Satisfy first-priority usability requirements for trading visibility and proactive alerting.
- Validation:
  - Frontend renders new columns/cards and refreshes without backend API contract changes.
  - Existing smoke regression test remains green.

### 14. Removed three user-input interpretation modules from UI
- File: static/index.html, README.md
- Type: Change
- Summary:
  - Removed these frontend cards and handlers:
    - 秒读财报 / 新闻
    - 解读 CPI / 利率 / 财报影响
    - 专业词人话解释
  - Simplified dashboard to focus on auto-analysis and trading operations modules.
  - Updated README endpoint note to clarify backend endpoints are kept but hidden from current UX.
- Why:
  - User requested to defer user-input interpretation modules for a later phase.
- Validation:
  - Frontend loads without missing-element JS errors.
  - Smoke test remains green.

### 15. Refined src with shared class utility (less duplication)
- File: src/time_utils.py, src/app.py, src/collect_stocks.py, src/summary.py
- Type: Refactor
- Summary:
  - Added shared class `BeijingTime` for UTC+8 date/time generation.
  - Replaced duplicated timezone setup in app/collector/summary with shared utility calls.
  - Kept compatibility helper functions in app (`_bj_date_str`, `_bj_datetime_str`, `_bj_yyyymmdd`) to avoid test/runtime breakage.
- Why:
  - Improve readability and maintainability.
  - Reduce repeated timezone logic across multiple files.
- Validation:
  - Syntax compile passed for app/collector/summary/time_utils.
  - Smoke regression test passed (7 tests, OK).

### 16. Reduced upstream warning-log noise
- File: src/app.py
- Type: Fix
- Summary:
  - Added configurable upstream logger suppression for noisy third-party modules.
  - Default behavior now keeps runtime/test output clean under unstable data-source network conditions.
  - Added env switch `FUN_QUIET_UPSTREAM_LOGS` (default `1`) to allow re-enabling verbose upstream logs when needed.
- Why:
  - Frequent external-source warnings obscured real failures during routine smoke runs.
- Validation:
  - Smoke test output became concise (no repeated upstream reset/delisted warning spam).
  - Smoke regression test remained green (7 tests, OK).

## 2026-04-29

### 17. Rearranged Watchdog controls into one-line layout
- File: static/index.html
- Type: Improvement
- Summary:
  - Reworked Watchdog control area into a single inline row.
  - Combined two threshold textboxes, notification checkbox, and two action buttons in one control strip.
  - Added responsive wrapping rules for tablet/mobile widths.
- Why:
  - Improve visual density and reduce vertical space usage in the full-row Watchdog card.
- Validation:
  - Frontend loads with the updated control layout and no missing-element errors.
  - Smoke regression test passed (7 tests, OK).

### 18. Updated data-source strategy, AI endpoint, and then restored preferred dark theme
- File: src/app.py, static/index.html, tests/smoke_test.py, README.md
- Type: Change
- Summary:
  - Switched A-share quote provider order to AkShare -> Sina -> Yahoo.
  - Added new AI strategy endpoint `/api/ai-edge` and frontend panel integration.
  - Extended smoke test auto-endpoint coverage to include `/api/ai-edge`.
  - After UX feedback, reverted visual theme from Streamlit-like light style back to prior dark style while keeping new features.
- Why:
  - Align data behavior with preferred A-share source.
  - Add AI-generated actionable strategy as a core capability.
  - Respect user visual preference for the previous dashboard style.
- Validation:
  - Syntax compile for src/app.py passed.
  - Smoke regression test passed (7 tests, OK).

## Entry Template

Copy this template for each new patch:

### N. Short title
- File: file/path.py
- Type: Fix | Patch | Improvement | Refactor
- Summary:
  - Change 1
  - Change 2
- Why:
  - Reason for the change
- Validation:
  - Test or verification result

---

## 🎉 V1 Release — 2026-04-29

### 19. Added Traffic Light Watchdog UI
- File: static/index.html
- Type: Improvement
- Summary:
  - Added visual traffic light indicator at top of Watchdog card.
  - 🟢 Green (0 alerts), 🟡 Yellow (1-2), 🔴 Red (3+).
  - Displays status label and detail text.
- Validation: Visual check confirmed color transitions.

### 20. Added portfolio weighted change chip + sentiment change detection
- File: static/index.html
- Type: Improvement
- Summary:
  - Stats bar: new "持仓涨幅" chip showing market-value-weighted change%.
  - Sentiment change detection: compares current stage vs localStorage, pushes Watchdog notification on change.
- Validation: Chip renders correctly; notification fires on simulated stage change.

### 21. Pre-filled holdings from broker snapshot
- File: static/index.html
- Type: Improvement
- Summary:
  - On first load (empty localStorage), auto-fills 10 holdings with shares + cost from broker data.
  - Does not overwrite existing user data.
- Validation: Fresh localStorage correctly populated with 10 positions.

### 22. Added privacy toggle (show/hide personal data)
- File: static/index.html
- Type: Improvement
- Summary:
  - Header button 🔓/🔒 toggles visibility of sensitive columns (shares, cost, P&L).
  - Stats bar values (市值, 盈亏, 涨幅) also masked.
  - State persisted in localStorage.
- Validation: Toggle masks/unmasks correctly; persists across page reload.

### 23. Fixed 52-week high/low always empty
- File: src/app.py
- Type: Fix
- Summary:
  - AkShare provider: reads 52周最高/52周最低 from spot table columns.
  - Sina provider: added `_fetch_52w()` using Sina daily K-line API (260 days, 12h cache).
  - New in-memory cache `_52W_CACHE` avoids repeated K-line downloads.
- Validation: `_fetch_52w('601088.SS')` → high52=50.38, low52=36.62.

### 24. Added limit-up/down stats and yesterday limit-up performance
- File: src/app.py, static/index.html
- Type: Improvement
- Summary:
  - New `/api/limit-stats` endpoint: today's limit-up/down counts, consecutive boards, max board, yesterday limit-up profit rate.
  - New insight card "涨跌停 & 昨日涨停表现" with 5min auto-refresh.
  - Stats bar: 3 new chips (涨停, 跌停, 昨涨停胜率).
  - Verdict logic: ≥60% + avg>1% = "接力环境好", ≥40% = "中性", <40% = "周期走弱".
- Validation: Live test returned limit_up=100, limit_down=13, profit_rate=53.4%.

### 25. Fixed color mode badge backgrounds + added timestamps
- File: static/index.html
- Type: Fix
- Summary:
  - Badge backgrounds now use CSS vars (`--badge-up-bg`, `--badge-down-bg`) that swap with color mode.
  - Added `更新时间` timestamp to sentiment and limit-stats insight cards.
- Validation: Color toggle correctly swaps badge backgrounds; timestamps show on all cards.

### 26. V1 documentation refresh
- File: README.md, PATCH_HISTORY.md
- Type: Improvement
- Summary:
  - README rewritten as product-focused V1 document with capability table, API reference, tech stack.
  - PATCH_HISTORY updated with all V1 session entries (19-26).

## 2026-04-30

### 27. Dashboard card drag-reorder, hide/restore, and column layout selector
- File: static/index.html
- Type: Improvement
- Summary:
  - All insight cards are now draggable; card order persists in localStorage (`card_order_v1`).
  - Added drag handle (⡿) and close button (✕) on each card header.
  - Hidden cards appear as restore chips in a bar above the grid; click to restore.
  - Added column layout bar (1 / 2 / 3 / auto) with persistence (`card_cols_v1`).
  - Stats bar moved inside its own card so it participates in reorder/hide.
  - AI Core Edge card promoted to second position by default.
  - Sentiment inputs now show placeholder examples and help text.
  - Updated default positions (removed 601398, added 000001/600036/600900/601857).
- Why:
  - Let users customize dashboard layout and focus on the cards they use most.
- Validation:
  - Drag reorder persists across page reload.
  - Hidden cards reappear via restore chips.
  - Column selector correctly changes grid layout.

### 28. Fixed /api/limit-stats missing "ok" field
- File: src/app.py
- Type: Fix
- Summary:
  - Added `"ok": True` to the `_get_limit_stats()` response dict.
  - Set `"ok": False` when AkShare is unavailable.
  - This aligns `/api/limit-stats` with the contract expected by `tests/smoke_test.py`.
- Why:
  - Smoke test `test_auto_endpoints_return_json` asserted `"ok" in data` for all auto endpoints but `/api/limit-stats` never included it.
- Validation:
  - Smoke regression test passed (7 tests, OK).

## 2026-05-03

### 29. Config decoupling — centralized configuration module
- File: src/config.py (new), src/providers.py, src/sentiment.py, src/analysis.py, src/server.py, .env.example (new)
- Type: Refactor
- Summary:
  - Created `src/config.py` with a `_Config` class exposing all tunable parameters.
  - All values overridable via `FUN_*` environment variables (e.g. `FUN_PORT`, `FUN_SINA_KLINE_TIMEOUT`).
  - Updated `providers.py`: URLs, timeouts, cache TTLs, retry settings now read from `cfg`.
  - Updated `sentiment.py`: file paths, thresholds, defaults, iwencai timeout from `cfg`.
  - Updated `analysis.py`: NEWS_FEEDS, cache TTLs, profit thresholds, limits from `cfg`.
  - Updated `server.py`: all previously duplicated constants reference `cfg`.
  - Added `.env.example` documenting every environment variable with its default.
- Why:
  - Eliminate ~6 duplicate copies of the same constants across modules.
  - Allow runtime tuning via environment variables without code changes.
  - Enable different configurations for dev/docker/production via `.env` file.
- Validation:
  - All four modules import cleanly: `from config import cfg` succeeds.
  - Server starts without errors on port 5000.

## 🎉 V2 Release — 2026-05-08

### 30. Petite-Vue reactive store integration
- File: static/index.html, static/js/app.js, PETITE_VUE_MIGRATION.md
- Type: Improvement
- Summary:
  - Introduced petite-vue 0.4.1 CDN and global reactive `store`.
  - Existing vanilla JS writes data into store for reactive UI binding.
  - Created migration guide for phased declarative-binding adoption.

### 31. Sticky header with page-head wrapper
- File: static/index.html, static/css/style.css
- Type: Improvement
- Summary:
  - Wrapped `<header>`, `.add-bar`, `.layout-bar` inside `<div class="page-head">`.
  - `page-head` uses `position: sticky; top: 0; z-index: 100` so controls stay visible on scroll.
  - Moved `position: sticky` from `header` to `.page-head`.

### 32. Layout bar reorganization + scroll-to-stocks button
- File: static/index.html, static/css/style.css, static/js/app.js
- Type: Improvement
- Summary:
  - Moved fold/hide buttons into `<span class="layout-bar-right">` with `margin-left: auto`.
  - Added 📊 button that smooth-scrolls to the stock card section.
  - Added `scroll-margin-top: 120px` on `.stock-section` to clear sticky header.
  - Removed stale `.active` class toggle from sync function.

### 33. CSV timeout fallback for live fetch
- File: src/server.py, src/config.py
- Type: Fix
- Summary:
  - `_get_stocks_snapshot()` now runs live fetch in a daemon thread with 30s timeout.
  - If timeout expires, falls back to latest CSV file, then placeholder data.
  - Timeout configurable via `FUN_LIVE_FETCH_TIMEOUT` env var (default 30).

### 34. Sentiment non-trading fallback
- File: src/server.py
- Type: Fix
- Summary:
  - `/api/market-sentiment-auto` now falls back to `sentiment_history.json` when off-hours and live data has missing values.
  - Returns last history entry with "休市中，显示最近交易日数据" message.

### 35. P1 test suite — trading session and snapshot tests
- File: tests/test_server_trading.py
- Type: Improvement
- Summary:
  - TestIsCnTradingSession: weekend, holiday, within/at/before/after hours, Labor Day, National Day.
  - TestGetStocksSnapshot: cache hit, off-hours CSV, off-hours no CSV, trading-hours fetch, force refresh.
  - TestDoubleCheckedLocking: concurrent requests trigger single scan.

### 36. Docker and config decoupling
- File: docker/Dockerfile, docker/docker-entrypoint.sh, docker-compose.yml, src/config.py
- Type: Improvement
- Summary:
  - Added Docker support with Dockerfile, entrypoint script, and docker-compose.
  - Centralized all tunable parameters in `src/config.py` with `FUN_*` env var overrides.

### 37. Macro indicator card (上证/汇率/黄金/原油)
- File: src/server.py, static/index.html, static/js/app.js, static/css/style.css
- Type: Improvement
- Summary:
  - New `/api/macro` endpoint fetching 4 indicators from Sina real-time API (`hq.sinajs.cn`).
  - 60-second TTL cache. Returns name, price, change%, arrow direction.
  - Frontend macro chips row with 5-minute auto-refresh.
- Validation: API returns 4 indicators with live prices.

### 38. Black Swan / Grey Rhino risk event radar
- File: src/server.py, static/index.html, static/js/app.js, static/css/style.css
- Type: Improvement
- Summary:
  - New `/api/risk-events` endpoint scanning macro + stock data for anomalies.
  - Black Swan: single-stock crash ≥7%, macro index drop ≥3%, gold/oil spike ≥5%.
  - Grey Rhino: multi-stock cluster drop, market breadth ≤20%, CNY weakness, sustained decline.
  - In-memory `_RISK_EVENT_HISTORY` with hourly dedup.
  - Period filter: `?period=1h|today|3d|7d|30d`.
  - Frontend radar card with period select and manual refresh.
- Validation: Simulated data correctly triggers both event types.

### 39. Bazi (八字) + Wuyun Liuqi (五运六气) card
- File: src/tools/bazi_core.py, src/server.py, static/index.html, static/js/app.js, static/css/style.css
- Type: Improvement
- Summary:
  - New `calc_wuyun_liuqi(dt)` in bazi_core.py: computes 岁运, 司天, 在泉, 当前气期, 主气, 客气.
  - Added health tips (`_HEALTH_TIPS`) and trading sector hints (`_TRADING_TIPS`) per element/period.
  - New `/api/bazi` endpoint returns four pillars + wuyun liuqi data.
  - Frontend bazi card with pillar display, wuyun chips, and tip sections.
  - Styled with `.wuyun-section`, `.wuyun-chip`, `.wuyun-tip`, `.tip-health`, `.tip-trading`.
- Validation: 2026 丙午年 → 水运太过, 少阴君火司天, 阳明燥金在泉.

### 40. Data source management panel
- File: src/server.py, static/index.html, static/js/app.js
- Type: Improvement
- Summary:
  - New `/api/providers/test` (POST): tests all providers with timing.
  - New `/api/providers/order` (GET/POST): get/set provider priority.
  - New `/api/providers/auto` (POST): auto-select fastest provider.
  - Dynamic `_preferred_provider_order` list, default Sina-first.
  - Frontend ⚡ panel with test/auto buttons and draggable order.
- Validation: Provider test returns response times; auto-select picks fastest.

### 41. Configurable refresh interval selector
- File: static/index.html, static/js/app.js
- Type: Improvement
- Summary:
  - Added dropdown selector for stock quote refresh: 10s/30s/1m/10m/30m.
  - Default changed from 1m to 30m to reduce API load.
  - Selection persisted in localStorage.
- Validation: Changing interval immediately adjusts timer.

### 42. Provider order changed: Sina first
- File: src/server.py, src/providers.py
- Type: Change
- Summary:
  - Default A-share provider order changed from AkShare→Sina→Yahoo to Sina→AkShare→Yahoo.
  - Sina is faster for individual stock queries; AkShare bulk scan ~3min is now fallback.
- Validation: Single-stock fetch completes in <1s via Sina.

### 43. Test suite expansion to 109 tests
- File: tests/ (all test files)
- Type: Improvement
- Summary:
  - Expanded from 7 smoke tests to 109 comprehensive tests across 8 files.
  - P0 unit tests: sentiment (10), analysis (21), providers (22), time_utils (5), config (4).
  - P1 integration: server_trading (16), server_csv (11), watchlist (13), smoke (7).
  - Fixed test isolation: `_clean_config_import` fixture now saves/restores sys.modules.
  - Fixed CSV test patching: patches `stock_app.cfg` directly instead of re-importing.
- Validation: `python -m pytest tests/` → 109 passed.

### 44. Cleaned up unused files
- File: src/tools/8zi.py (deleted), src/tools/widget.py (deleted)
- Type: Cleanup
- Summary:
  - Removed standalone `8zi.py` (superseded by bazi_core.py).
  - Removed standalone `widget.py` (unused widget script).
- Validation: No imports reference deleted files; all tests pass.