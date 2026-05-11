# YYKANPAN 测试计划 / Test Plan

## 测试概况 / Test Summary

**109 tests, 8 test files** — 全部通过 ✅ (2026-05-11)

| 文件 | 覆盖模块 | 项数 | 类型 |
|------|----------|------|------|
| `smoke_test.py` | `server.py` — API 端点可达性 + JSON 格式验证 | 7 | 集成 |
| `test_analysis.py` | `analysis.py` — quickread/macro/AI edge/主线 | 21 | 单元 |
| `test_config.py` | `config.py` — 默认值, 环境变量覆盖, 路径类型, 阈值 | 4 | 单元 |
| `test_providers.py` | `providers.py` — A股识别, ticker标准化, 重试, 回退链 | 22 | 单元 |
| `test_sentiment.py` | `sentiment.py` — 情绪评估, 合并, 历史去重, 配置持久化 | 10 | 单元 |
| `test_server_csv.py` | `server.py` — CSV 保存/加载回环, 类型还原, 边界 | 11 | 集成 |
| `test_server_trading.py` | `server.py` — 交易时段, 快照分支, 缓存, 线程锁 | 16 | 集成 |
| `test_time_utils.py` | `time_utils.py` — UTC+8 时间, 格式化 | 5 | 单元 |
| `test_watchlist.py` | `server.py` — 自选股 CRUD, 配置导入导出 | 13 | 集成 |
| `conftest.py` | 公共 path 设置 | — | 基础设施 |

---

## 已完成测试 / Completed Tests

### P0 — 核心业务逻辑 (纯函数, 不依赖网络)

#### 1. `test_sentiment.py` — 情绪评估引擎 ✅ (10 tests)
- [x] `evaluate_market_sentiment()` — 上升/退潮/分歧 三阶段分类
- [x] `merge_with_last_known()` — 缺失字段回填 + fallback 字段追踪
- [x] `append_sentiment_history()` — 同小时去重 (ts[:13] 相同则跳过)
- [x] `load/save_sentiment_config()` — JSON 持久化回环

#### 2. `test_analysis.py` — 分析引擎 ✅ (21 tests)
- [x] `quickread_news()` — 关键词标签提取 + 情绪打分 (正面/负面/中性)
- [x] `macro_impact()` — CPI/利率/盈利 delta 分析
- [x] AI Edge 置信度公式: `60 + breadth*25 + avg*6 - vol_penalty*4`, clamp [10,95]
- [x] 主线分析 industry scoring: `count*2 + turnover/1e9*0.2 + avg_pct*0.8`
- [x] 可交易性阈值: concentration ≥ 0.2 && strength ≥ 2.0

#### 3. `test_providers.py` — 数据提供层 ✅ (22 tests)
- [x] `is_a_share_ticker()` — A股代码识别
- [x] Ticker 标准化: `600519.SS` → `600519` (AkShare), `sh600519` (Sina)
- [x] `_is_retryable_error()` — 可重试错误判断
- [x] Fallback 链: A股先 Sina → AkShare → Yahoo; 非A股直接 Yahoo

#### 4. `test_time_utils.py` — 时间工具 ✅ (5 tests)
- [x] `BeijingTime.now()` 返回 UTC+8
- [x] `date_str()` 格式 `YYYY-MM-DD`
- [x] `datetime_str()` 格式 `YYYY-MM-DD HH:MM:SS`
- [x] `yyyymmdd()` 格式 `YYYYMMDD`

---

### P1 — 服务端集成 (Mock 网络调用)

#### 5. `test_server_trading.py` — 交易时段逻辑 ✅ (16 tests)
- [x] `_is_cn_trading_session()` — 工作日 + 非假日 + 09:15–15:30
- [x] `_get_stocks_snapshot()` — 缓存命中 / 休市+CSV / 休市+无CSV / 交易中
- [x] 线程锁: 并发请求只触发一次 scan (double-checked locking)

#### 6. `test_server_csv.py` — CSV 持久化 ✅ (11 tests)
- [x] `_save_stocks_csv()` → `_load_latest_csv()` 回环
- [x] 类型还原: price/change → float, volume/market_cap → int
- [x] None 52w 字段保留, error 行过滤, 空列表不写文件

#### 7. `test_watchlist.py` — 自选股 CRUD ✅ (13 tests)
- [x] POST `/api/stocks` — 添加/幂等
- [x] DELETE `/api/stocks/<ticker>` — 存在/不存在
- [x] GET/POST `/api/config/export` + `/api/config/import` — JSON 导入导出

---

## 未覆盖 / Gaps (可扩展)

### 新增功能（v2.0）— 暂无测试

| 功能 | 建议测试 |
|------|----------|
| `/api/macro` | mock Sina HTTP → 解析4个指标, 缓存 TTL |
| `/api/risk-events` | 构造 macro+stock 数据 → 验证阈值触发 + period 过滤 + 去重 |
| `/api/bazi` + 五运六气 | 固定日期 → 验证四柱/岁运/司天/在泉/主客气 |
| `/api/providers/*` | mock 3个 provider → test/auto/order 切换 |
| `_fetch_macro_indicators()` | mock HTTP → 解析 Sina 宏观行情格式 |
| `calc_wuyun_liuqi()` | 固定年份 → 验证天干地支映射/气期计算 |

### P2 — 前端逻辑 (可选, Node.js 测试)

- [ ] `fmtNum()` — 数字格式化 (千分位, 小数)
- [ ] `fmtVol()` — 成交量 (万/亿)
- [ ] `cls()` — 涨跌 CSS class (up/down/flat)
- [ ] `isChinaMarketClosed()` — 假日集 + 周末
- [ ] `isBeijingQuietHours()` — 15:30–08:30 静默窗口

### P3 — 端到端 / 性能

- [ ] E2E: 启动服务 → 浏览器验证卡片渲染/添加删除/折叠/颜色切换/隐私模式
- [ ] 性能: 首次扫描 < 3min, 缓存命中 < 100ms, 并发锁验证

---

## 运行方式 / How to Run

```bash
# 全量测试 (109 tests)
python -m pytest tests/ --tb=short

# 遇错即停
python -m pytest tests/ -x --tb=short

# 仅指定模块
python -m pytest tests/test_sentiment.py -v

# 仅冒烟测试
python -m pytest tests/smoke_test.py
```

## 优先级说明

- **P0**: 纯函数, 无外部依赖 — ✅ 已完成
- **P1**: 需要 mock 网络/文件 — ✅ 已完成
- **P2**: 前端 JS, 需 Node 环境 — 可延后
- **P3**: E2E / 性能 — 最后实现
