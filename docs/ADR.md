# Architecture Decision Records (ADR)

## ADR-001: Provider Fallback Chain (Sina → AkShare → Yahoo)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-04 |
| Context | A股行情数据源单点故障风险高，Sina 偶尔被墙，AkShare 依赖重 |

### Decision

三级数据源链式降级：Sina (主) → AkShare (备) → Yahoo (兜底)。

### Rationale

| 源 | 优势 | 劣势 |
|----|------|------|
| Sina | 零依赖(stdlib urllib)，最快，无限流 | 仅A股，GBK编码，无52w数据 |
| AkShare | 数据最全(市值/行业)，含52w | 需pandas，全量下载5000行 |
| Yahoo | 国际通用，含52w/history | 境内常被墙/限流 |

### Alternatives Rejected
- 单一数据源 → 单点故障不可接受
- 付费API (万得/同花顺) → 个人项目成本过高
- 固定顺序 → 已预留 `_preferred_provider_order` 可动态调序

### Consequences
- 每个 provider 用 `_with_retries()` 包装 (2次重试, 0.8s backoff)
- `/api/providers/test` 可运行时 benchmark
- `/api/providers/order` 可运行时调整顺序

---

## ADR-002: Deadlock Fix — Re-entrance Guard + .catch()

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05 |
| Context | refreshAllCards() 多个触发源 (定时器+手动+午夜) 并发导致UI渲染竞态 |

### Problem

1. **无 `.catch()`** → `loadStocks()` reject 后 Promise chain 中断，后续卡片永不渲染
2. **无重入锁** → 定时器+手动点击同时触发，多个 fetch 并行打 Sina
3. **午夜刷新不尊重静默时段** → 23:00–06:00 无意义请求

### Decision

```
Frontend: _refreshing boolean guard + .catch() + .finally()
Backend: threading.Lock + double-check cache pattern
Midnight: loadBazi() + loadXinguXinzhai() 强刷 + runAutoTask(refreshAllCards)
```

### Consequences
- 并发刷新降为串行
- 失败不会阻塞后续卡片
- 静默时段零 API 调用

---

## ADR-003: Advisor Module — Protocol-based Strategy Pattern

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05 |
| Context | 需要可解释的交易建议系统，未来可能接入 ML 模型 |

### Decision

```python
@runtime_checkable
class Strategy(Protocol):
    name: str
    def evaluate(self, position, context, risk_pref) -> Signal: ...
```

V1 用 `RuleBasedStrategy`(7条规则)，通过 `evaluate_portfolio(positions, ctx, risk_pref, strategy=None)` 注入。

### Rationale
- **Protocol over ABC** → duck-typing，测试时用任意 mock 对象
- **规则优先** → 可解释性 > 准确性，每个信号带 `reasons: list[str]`
- **三档风险偏好** → 同一套规则不同阈值，无需多策略
- **无 LLM 依赖** → 离线可用，确定性，可审计

### Alternatives Rejected
- LLM 生成建议 → 不确定性高，延迟大，无法回测
- 继承体系 (ABC) → 过度工程化，Protocol 够用
- 单一风险配置 → 用户需求差异大

---

## ADR-004: petite-vue 而非 Vue 3 / React

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-03 (initial migration) |
| Context | 2400+ 行 vanilla JS 维护困难，但不想引入构建工具链 |

### Decision

使用 petite-vue 0.4.1 (6KB CDN)，渐进式迁移。

### Rationale
- **零构建** → 无 webpack/vite/node，`<script>` 标签即用
- **渐进式** → 既有 vanilla DOM 操作继续工作，逐卡片迁移
- **reactive() 全局 store** → vanilla JS 和 v-scope 模板共享状态
- **Vue 生态兼容** → 同 `v-` 指令语法，未来可升级 full Vue

### Current State
Phase 0.5: store reactive，部分卡片用 v-scope，大部分仍为命令式 DOM 更新。

---

## ADR-005: 决策日志 — JSON 文件存储

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05 |
| Context | 个人决策日志，最多1000条，需 Docker 友好 |

### Decision

`data/decisions.json` 文件存储，`MAX_DECISIONS = 1000`。

### Rationale
- 零基础设施 → 无 SQLite/Postgres 依赖
- Docker 单卷挂载 (`/app/data`) 即持久化
- 人类可读 → 可直接查看/备份
- Git 友好 → 可版本控制
- 规模有界 → 个人用，1000条上限足够

### Alternatives Rejected
- SQLite → 增加依赖，此规模无查询性能需求
- Redis → 运维复杂度过高
- localStorage only → 无法跨设备

---

## ADR-006: 午夜刷新 + 静默时段

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05 |
| Context | 多个卡片依赖日期(八字/新股)，但非交易时段无需刷行情 |

### Decision

```
30s 轮询检测日期变化:
  → loadBazi() + loadXinguXinzhai() 无条件刷新
  → refreshAllCards() 通过 runAutoTask() (尊重静默时段)

静默时段: 15:30–08:30 BJ + 周末 + CN_HOLIDAYS_2026
```

### Rationale
- **轮询 > setTimeout精确午夜** → 更简单，处理浏览器 tab 休眠/唤醒
- **八字/新股必须刷** → 数据按日变化，与行情无关
- **行情静默** → 收盘后 Sina 返回收盘价不变，无需反复请求

---

## ADR-007: 新股新债 — East Money API + 日缓存

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05 |
| Context | 需要A股 IPO/可转债申购日历 |

### Decision

East Money datacenter API (`RPTA_APP_IPOAPPLY` + `RPT_BOND_CB_LIST`)，日期键缓存，过滤近3天+未来，每类上限8条。

### Rationale
- East Money 是A股打新数据事实标准，公开 JSON API 无需认证
- 日缓存 → 数据每日变更一次，无需分钟级刷新
- 3天+未来 → 显示刚结束的(参考中签率)和即将来的
- 8条上限 → UI 空间限制，14+卡片共存

---

## ADR-008: AutoDev — YAML 策略声明 + 自动决策循环

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-05 |
| Context | 策略逻辑硬编码在 Python 里，无法对比/热加载/版本化。决策流程缺少闭环 |

### Decision

**两层分离：YAML 配置 (what) + Python 评估器 (how)**

```
data/strategies/rule_v1.yaml     ← 声明式：因子名/权重/阈值/风控线
src/trading/strategy_loader.py   ← 5个注册评估器 + YAMLStrategy 类
src/trading/autodev.py           ← 5步循环：observe → decide → act → evaluate → learn
```

**循环架构：**
```
observe(positions, context)
    → decide(observation) → [Signal, ...]
        → act(signals) → [Decision, ...]  (source="rule", tags=["autodev"])
            → evaluate_past(current_prices) → [P&L, ...]
                → learn() → {patterns, suggestions}
                    ⟶ (OPEN) suggestions 不自动回写 YAML
```

### Rationale

- **YAML over hardcode** → 改权重只改 YAML，改逻辑只改 evaluator，互不耦合
- **YAMLStrategy implements Strategy Protocol** → 可直接注入 `evaluate_portfolio()`，与 RuleBasedStrategy 兼容
- **评估器注册表** → `EVALUATORS = {"pnl": _eval_pnl, ...}`，新因子只需注册函数
- **learn() 开环设计** → V1 只输出 suggestions，不自动修改配置。原因：
  - 避免无人值守下策略漂移
  - 保持人类审核（手动采纳建议后改 YAML）
  - V2 可加 `apply_suggestions()` + 版本快照实现真闭环
- **PyYAML 依赖** → ~100KB，标准配置库，不违反"纯 Python"原则

### Current Loop Status (v3.2)

| Step | 方法 | 输入 | 输出 | 状态 |
|------|------|------|------|------|
| **Observe** | `observe()` | positions + context | structured observation | ✅ |
| **Decide** | `decide()` | observation | Signal per position | ✅ |
| **Act** | `act()` | signals | Decision (journal entry) | ✅ |
| **Evaluate** | `evaluate_past()` | current_prices | P&L + risk verdict | ✅ |
| **Learn** | `learn()` | — | patterns + suggestions | ⚠️ 开环 |

**闭环缺口：** `learn()` → `observe()` 之间无自动反馈。suggestions 需人工审核后手动修改 YAML。

### Closing the Loop (Future V2)

```
learn() → suggestions
    → apply_suggestions()        # 自动调整权重 (带上下限)
    → save_strategy_version()    # 快照当前版本
    → compare_versions()         # 新旧策略绩效对比
    → promote_or_rollback()      # 人工确认后切换
```

### Alternatives Rejected

- **eval() 条件表达式** → YAML 里写 `"pnl_pct <= -0.10"` 用 eval 执行 → 安全风险
- **全自动闭环** → learn 直接改 YAML → 无人值守策略漂移，V1 不适合
- **SQLite 策略存储** → 此规模 YAML 文件够用，人类可读可 Git 版本化
- **无 YAML，纯 JSON** → YAML 注释支持、可读性更好

### Files

- `data/strategies/rule_v1.yaml` — 5因子基础策略 (盈亏0.30/风险0.25/情绪0.20/价位0.15/趋势0.10)
- `data/strategies/conservative.yaml` — 保守变体 (风险0.40)
- `src/trading/strategy_loader.py` — YAMLStrategy + 5 evaluators + load/list
- `src/trading/autodev.py` — AutoDev loop (observe/decide/act/evaluate/learn)
- `tests/test_strategy_loader.py` — 22 tests
- `tests/test_autodev.py` — 25 tests
