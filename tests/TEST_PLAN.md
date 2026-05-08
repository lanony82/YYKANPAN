# YYKANPAN 测试计划 / Test Plan

## 现有测试覆盖 / Existing Coverage

| 文件 | 覆盖模块 | 类型 |
|------|----------|------|
| `test_config.py` | `config.py` — 默认值, 环境变量覆盖, 路径类型, 阈值结构 | 单元 |
| `smoke_test.py` | `server.py` — 20 个 API 端点可达性 + JSON 格式验证 | 集成 |
| `conftest.py` | 公共 path 设置 | 基础设施 |

---

## 测试计划 / Planned Tests

### P0 — 核心业务逻辑 (纯函数, 不依赖网络)

#### 1. `test_sentiment.py` — 情绪评估引擎
- [ ] `evaluate_market_sentiment()` — 上升/退潮/分歧 三阶段分类
  - 全强 → "上升", score ≥ 2, tradable=True
  - score ≤ -1 或弱组合 → "退潮", tradable=False
  - 中间态 → "分歧"
- [ ] `merge_with_last_known()` — 缺失字段回填 + fallback 字段追踪
- [ ] `append_sentiment_history()` — 同小时去重 (ts[:13] 相同则跳过)
- [ ] `load/save_sentiment_config()` — JSON 持久化回环

#### 2. `test_analysis.py` — 分析引擎
- [ ] `quickread_news()` — 关键词标签提取 + 情绪打分
  - 正面关键词 ("增长", "超预期") → positive tags, score > 0
  - 负面关键词 ("下跌", "亏损") → negative tags, score < 0
  - 中性文本 → score ≈ 0
- [ ] `macro_impact()` — CPI/利率/盈利 delta 分析
  - CPI 上升 → 通胀预警
  - 利率下降 → 利好
- [ ] AI Edge 置信度公式: `60 + breadth*25 + avg*6 - vol_penalty*4`, clamp [10,95]
- [ ] 主线分析 industry scoring: `count*2 + turnover/1e9*0.2 + avg_pct*0.8`
- [ ] 可交易性阈值: concentration ≥ 0.2 && strength ≥ 2.0

#### 3. `test_providers.py` — 数据提供层
- [ ] `is_a_share_ticker()` — A股代码识别
  - `"600519.SS"` → True
  - `"000001.SZ"` → True
  - `"AAPL"` → False
- [ ] Ticker 标准化: `600519.SS` → `600519` (AkShare), `sh600519` (Sina)
- [ ] `_is_retryable_error()` — 可重试错误判断
- [ ] Fallback 链: A股先 AkShare → Sina → Yahoo; 非A股直接 Yahoo

#### 4. `test_time_utils.py` — 时间工具
- [ ] `BeijingTime.now()` 返回 UTC+8
- [ ] `date_str()` 格式 `YYYY-MM-DD`
- [ ] `datetime_str()` 格式 `YYYY-MM-DD HH:MM:SS`
- [ ] `yyyymmdd()` 格式 `YYYYMMDD`

---

### P1 — 服务端集成 (Mock 网络调用)

#### 5. `test_server_trading.py` — 交易时段逻辑
- [ ] `_is_cn_trading_session()` — 工作日 + 非假日 + 09:15–15:30
  - 周末 → False
  - 假日 (2026-01-01) → False
  - 交易时段内 → True
  - 盘前 08:00 → False
- [ ] `_get_stocks_snapshot()` — 线程安全 + 分支逻辑
  - 缓存命中 → 直接返回, 不加锁
  - 休市 + 有 CSV → 返回 CSV 数据
  - 休市 + 无 CSV → 返回 offline 占位符
  - 交易中 → 调用 fetch_stock (mock)
- [ ] 线程锁: 并发请求只触发一次 scan (double-checked locking)

#### 6. `test_server_csv.py` — CSV 持久化
- [ ] `_save_stocks_csv()` → `_load_latest_csv()` 回环
- [ ] 类型还原: price/change 等从 string → float
- [ ] 空数据 / 错误行容错

#### 7. `test_watchlist.py` — 自选股 CRUD
- [ ] POST `/api/stocks` — 添加有效 ticker → 200, 写入 watchlist
- [ ] POST `/api/stocks` — 重复 ticker → 仍 200 (幂等)
- [ ] DELETE `/api/stocks/<ticker>` — 存在 → 200, 不存在 → 404
- [ ] GET/POST `/api/config/export` + `/api/config/import` — JSON 导入导出

---

### P2 — 前端逻辑 (可选, Node.js 测试)

#### 8. `test_app_js.md` — JS 工具函数
- [ ] `fmtNum()` — 数字格式化 (千分位, 小数)
- [ ] `fmtVol()` — 成交量 (万/亿)
- [ ] `cls()` — 涨跌 CSS class (up/down/flat)
- [ ] `isChinaMarketClosed()` — 假日集 + 周末
- [ ] `isBeijingQuietHours()` — 15:30–08:30 静默窗口
- [ ] `runWatchdog()` — 红绿灯阈值分类

---

### P3 — 端到端 / 性能

#### 9. E2E (手动 / Playwright)
- [ ] 启动服务 → 打开浏览器 → 验证股票卡片渲染
- [ ] 添加/删除股票 → 卡片更新
- [ ] 折叠/展开所有卡片
- [ ] 颜色模式切换 (中美)
- [ ] 隐私模式切换

#### 10. 性能基线
- [ ] 首次 AkShare 扫描 < 3 分钟 (58 页)
- [ ] 缓存命中 API 响应 < 100ms
- [ ] 并发 10 请求不触发多次扫描 (threading lock)

---

## 运行方式 / How to Run

```bash
# 单元测试 (P0)
python -m pytest tests/ -v --tb=short

# 冒烟测试
python tests/smoke_test.py

# 仅指定模块
python -m pytest tests/test_sentiment.py -v
```

## 优先级说明

- **P0**: 纯函数, 无外部依赖, 应当立即编写
- **P1**: 需要 mock 网络/文件, 中等复杂度
- **P2**: 前端 JS, 需 Node 环境, 可延后
- **P3**: E2E / 性能, 最后实现
