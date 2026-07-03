# TODO

> **Mission:** Most traders track profits. YYKANPAN tracks decisions — and learns from them.

## 🔥 Immediate (this session)

- [x] Read [tests/test_decision_quality.py](tests/test_decision_quality.py) — this file is advisor robustness/consistency tests, not `compute_quality`
- [x] Read [docs/advisor-spec.md](docs/advisor-spec.md)
- [x] Decide: commit v4.1 first, then start quality metric work on clean baseline
- [x] **2026-07-01 System Audit** — wxfile retention + 五运六气配图 + wechat 集成
  - [x] Implement wxfile 5-day retention (matching CSV cleanup)
  - [x] Broaden image search from "wu xing" → "flower tree landscape"
  - [x] Create comprehensive test suites (96 test cases)
  - [x] Bug fix: wxfile prune logic for img/ subdirectory edge case
  - [x] Add logging to error recovery paths
  - See detailed audit: [.review_2026-07-01_system_check.md](.review_2026-07-01_system_check.md)

## ✅ Review Notes (2026-05-21)

- Current `tests/test_decision_quality.py` focuses on advisor decision logic quality (scenario/property tests), not score compounding math.
- Existing decision APIs already include CRUD + `POST /api/decisions/evaluate/<decision_id>` + `GET /api/decisions/analyze`.
- `compute_quality` and `GET /api/decisions/quality` are not implemented yet.
- Confidence scale currently differs by source (`decision` uses 0-1, advisor signal strength is 1-5): normalize before scoring.

## 📦 Pending Commit — v4.1

Already done, awaiting commit:
- Macro indicators: 深证成指 / 创业板指 / 两市成交额 / 北向资金 (9 issues fixed)
- Northbound 30min cache + sanity clamp (5000亿)
- vol_total dynamic insertion after last index
- Empty-result-not-cached contract
- 🎓 新手三键模式 (beginner mode, 3-card default)
- Tests: 345 → 370 (25 new)
- README: beginner mode bullet added

```bash
git add -A
git commit -m "v4.1: macro indicators expansion + beginner mode + 25 new tests"
```

## 🗺️ Roadmap — Decision Quality Compounding Engine

Anchored on closing the feedback loop, not adding features.

### Phase 1 — Lock the quality metric ⭐ START HERE
- [ ] Define `compute_quality(decisions: list[dict]) -> float` signature
- [ ] Define scoring contract: output range (0-100), minimum sample handling, and weighting (P&L vs process/risk adherence)
- [ ] Add dedicated unit tests in `tests/test_quality_metric.py` (keep `tests/test_decision_quality.py` for advisor logic)
- [ ] Add `/api/decisions/quality` endpoint
- [ ] Add API tests for quality endpoint in `tests/test_server_trading.py`
- [ ] Update [docs/API.md](docs/API.md) for new endpoint schema
- [ ] Add dashboard card + JS wiring for quality score and trend (frontend parity with API changes)
- [ ] **Why first:** every other phase depends on a stable quality number

### Phase 2 — Auto-evaluate cron
- [ ] Background job: acted decisions → auto-evaluated after N days
- [ ] No user click required to close the loop

---

## 📋 System Hardening Backlog — 2026-Q3

From [.review_2026-07-01_system_check.md](.review_2026-07-01_system_check.md):

### P1 — Consistency & Observability (this week)
- [ ] Add image fetch failure logging (`_fetch_pd_image` error → warning log)
- [ ] Unify data retention policies:
  - CSV: 5 days ✓
  - wxfile: 5 days ✓  
  - sentiment: currently `SENTIMENT_HISTORY_MAX_ENTRIES=200` → **convert to max 20 days instead**
  - [ ] Update config.py: `SENTIMENT_HISTORY_MAX_DAYS = 20`
  - [ ] Modify `_save_sentiment_history()` to prune by date instead of raw count

### P2 — Config & Reliability (2 weeks)
- [ ] Move wxfile directory to config.py (`WXFILE_DIR` constant)
- [ ] Add retry logic to image fetch (`_fetch_pd_image` with exponential backoff)
  - Wikimedia timeout frequently hit from China; needs 2-3 retries with 1s/2s/4s delays
- [ ] Lock dependency versions: generate `requirements-lock.txt` from `pip freeze`

### P3 — Data Integrity (ongoing)
- [ ] Add pydantic schema validation for CSV rows instead of bare `try/except`
- [ ] Document wxfile format contract in [docs/paper-trade-spec.md](docs/paper-trade-spec.md)


- [ ] Writes P&L + risk-adherence back to decision log
- [ ] **Why:** today the loop only closes if user remembers to evaluate

### Phase 3 — Quality trend chart
- [ ] Dashboard card: quality score over time (7d / 30d / 90d)
- [ ] Breakdown by source: manual / rule / ai
- [ ] **Why:** make the compounding visible — the whole point of the system

### Phase 4 — AutoDev `learn` step
- [ ] Currently empty in observe→decide→act→evaluate→**learn** loop
- [ ] Propose factor-weight adjustments based on realized outcomes
- [ ] Write proposals to log; require human approval before applying
- [ ] **Why:** turn the YAML strategy into a learning artifact

### Phase 5 — Calibration view
- [ ] Plot stated confidence vs. realized hit rate
- [ ] Surface overconfidence / underconfidence per source
- [ ] **Why:** confidence is currently a free-text number — calibrate it

### Phase 6 — Counterfactual quality
- [ ] Compare advisor recommendation vs. user action on same setup
- [ ] Quality(advisor) vs. Quality(user) over time
- [ ] **Why:** answers the real question — *am I getting better?*

## 🚫 Explicitly NOT now

- More cards / indicators / data sources — we have 17 cards already
- Logging service / observability infra — not needed at current scale
- AWS/cloud deployment — local-first is fine for now
- ML models / LLM integration — quality metric must come first

## 📌 Open questions

- What's the exact formula for `compute_quality`? Risk-adjusted P&L? Process score? Hybrid?
- How many days until auto-evaluation triggers? (Phase 2)
- Quality score: 0-100, 0-1, or letter grade for UX?
