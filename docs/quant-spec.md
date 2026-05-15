# 量化交易功能规划

## 概览

四大模块，按依赖关系排序实施。

---

## 1. 技术指标信号 — Easy ⭐

已有 `/api/history/{ticker}?days=20` 返回 OHLCV，只需计算指标 + 标注买卖信号。

| 项目 | 说明 |
|---|---|
| **后端** | 新建 `src/quant.py` — 纯函数: `calc_ma()`, `calc_macd()`, `calc_rsi()`, `calc_kdj()`, `calc_boll()`。输入 = 价格列表，输出 = 指标值 + 信号 (买/卖/观望) |
| **API** | `GET /api/signals/{ticker}` → 返回该股票全部指标 + 信号 |
| **前端** | 在个股卡片上添加信号标签 (🔴买入 / 🟢卖出)；可选迷你指标图 |
| **数据** | 复用现有 history cache，扩展 `days=60` 以支持 MA20/MA60 |
| **工作量** | ~200 行 Python，~50 行 JS。无需新依赖（纯算术运算） |

### 指标算法

- **MA(N)**: 简单移动平均，N=5/10/20/60
- **MACD**: EMA12 - EMA26 = DIF, DIF 的 EMA9 = DEA, (DIF-DEA)*2 = 柱状
- **RSI(N)**: 100 - 100/(1 + avg_gain/avg_loss), N=6/12/24
- **KDJ**: 9日 RSV → K=2/3×K_prev+1/3×RSV, D=2/3×D_prev+1/3×K, J=3K-2D
- **布林带**: MA20 ± 2×std(20)

### 信号规则

| 信号 | 条件 |
|---|---|
| MA金叉 | MA5 上穿 MA20 |
| MA死叉 | MA5 下穿 MA20 |
| MACD金叉 | DIF 上穿 DEA (且 DIF<0 更强) |
| MACD死叉 | DIF 下穿 DEA |
| RSI超卖 | RSI6 < 20 |
| RSI超买 | RSI6 > 80 |
| KDJ金叉 | K 上穿 D (且 J<20) |
| 布林下轨 | 价格触及下轨 (买入参考) |
| 布林上轨 | 价格触及上轨 (卖出参考) |

---

## 2. 模拟盘 — Medium-Hard ⭐⭐⭐

虚拟下单 + 实时盈亏跟踪。

| 项目 | 说明 |
|---|---|
| **后端** | `src/paper_trade.py` — Portfolio: `{cash, positions[]}`。操作: `buy(ticker, shares, price)`, `sell(ticker, shares, price)`。持久化到 `data/portfolio.json` |
| **API** | `POST /api/trade` (买入/卖出), `GET /api/portfolio` (持仓 + 浮动盈亏), `GET /api/trade-history` (已平仓交易) |
| **盈亏** | 实时: 现价 vs 成本均价。已平仓: 卖价 vs 买价。总计: 已实现 + 未实现 |
| **前端** | 新建"模拟盘"卡片 — 买卖表单 (股票代码 + 手数), 持仓表 (红涨绿跌 PnL), 交易记录 |
| **规则** | 初始资金可配置 (默认 100万), T+1 (当日买入不可卖出), 单票仓位上限 10% |
| **工作量** | ~500 行 Python, ~150 行 JS。需要持久化存储 (JSON 文件) |

### 数据结构

```json
{
  "initial_capital": 1000000,
  "cash": 850000,
  "positions": [
    {
      "ticker": "601088.SS",
      "name": "中国神华",
      "shares": 1000,
      "avg_cost": 35.50,
      "buy_date": "2026-05-14",
      "current_price": 36.20,
      "unrealized_pnl": 700,
      "pnl_pct": 1.97
    }
  ],
  "trades": [
    {
      "id": 1,
      "ticker": "601088.SS",
      "action": "buy",
      "shares": 1000,
      "price": 35.50,
      "amount": 35500,
      "time": "2026-05-14 09:35"
    }
  ]
}
```

### 交易规则

- 买入: 金额 = 股数 × 价格 + 佣金 (万2.5)。检查: cash 是否够，仓位是否超限
- 卖出: T+1 检查 (buy_date < today)。金额 = 股数 × 价格 - 佣金 - 印花税 (千1)
- 股数: 必须为 100 的整数倍 (一手)

---

## 3. 选股策略 — Medium ⭐⭐

扫描全 A 股市场 (~5000 只)，按策略规则筛选。

| 项目 | 说明 |
|---|---|
| **后端** | `GET /api/screener?strategy=golden_cross` — 获取 `ak.stock_zh_a_spot_em()` (全市场快照)，逐一计算指标，按策略规则过滤 |
| **策略** | `golden_cross` (MA5上穿MA20), `volume_breakout` (量比>2 + 突破前高), `limit_up_relay` (昨日涨停今日竞价高开), `oversold_bounce` (RSI<30 + 放量) |
| **API** | 返回 top 20 命中股票，含分数 + 命中原因 |
| **前端** | 新建"选股雷达"卡片，策略下拉框，结果表格 |
| **瓶颈** | 全市场扫描 AkShare 较慢 (~10s)。需缓存 (5分钟 TTL) 或后台扫描 |
| **工作量** | ~400 行 Python, ~100 行 JS/HTML。依赖模块 #1 |

### 策略定义

```python
STRATEGIES = {
    "golden_cross": {
        "name": "均线金叉",
        "desc": "MA5 上穿 MA20，放量确认",
        "rules": ["ma5 > ma20", "ma5_prev <= ma20_prev", "volume_ratio > 1.5"]
    },
    "volume_breakout": {
        "name": "放量突破",
        "desc": "量比>2，价格突破20日最高",
        "rules": ["volume_ratio > 2", "close > max_20d", "change_pct > 3"]
    },
    "limit_up_relay": {
        "name": "涨停接力",
        "desc": "昨日涨停，今日高开3%+",
        "rules": ["prev_change_pct >= 9.8", "open_change_pct >= 3"]
    },
    "oversold_bounce": {
        "name": "超跌反弹",
        "desc": "RSI<30 + 当日放量阳线",
        "rules": ["rsi6 < 30", "volume_ratio > 1.5", "change_pct > 0"]
    }
}
```

---

## 4. 回测框架 — Hard ⭐⭐⭐⭐

历史数据回放 + 策略引擎 + 交易模拟 + 绩效统计。

| 项目 | 说明 |
|---|---|
| **后端** | `src/backtest.py` — Strategy 基类，事件驱动引擎: `on_bar(date, ohlcv)` → `buy()/sell()/hold()`。仓位跟踪，PnL 计算器 |
| **数据** | 需要 1-2 年日线 OHLCV。`ak.stock_zh_a_hist(symbol, period='daily', start_date, end_date)`。存储在 SQLite 或 CSV 缓存 |
| **指标** | 总收益率, 年化收益, 最大回撤, 胜率, 盈亏比, 夏普比率 |
| **API** | `POST /api/backtest` with `{ticker, strategy, start, end}` → 返回权益曲线 + 交易记录 + 绩效指标 |
| **前端** | 权益曲线图 (SVG), 价格图上标注交易点, 绩效指标汇总表 |
| **工作量** | ~800+ 行 Python, ~200 行 JS。需要 SQLite 或文件存储。复杂边界情况 (除权/停牌) |

### 绩效指标

| 指标 | 公式 |
|---|---|
| 总收益率 | (期末资产 - 初始资金) / 初始资金 |
| 年化收益 | (1 + 总收益率) ^ (252/交易日数) - 1 |
| 最大回撤 | max(peak - trough) / peak |
| 胜率 | 盈利交易数 / 总交易数 |
| 盈亏比 | 平均盈利 / 平均亏损 |
| 夏普比率 | (年化收益 - 无风险利率) / 年化波动率 |

### 引擎架构

```
DataLoader → for each bar:
  Strategy.on_bar(date, ohlcv)
    → Signal(buy/sell/hold)
    → Broker.execute(signal)
      → Portfolio.update()
→ Performance.calc_metrics()
→ Report {equity_curve, trades, metrics}
```

---

## 实施顺序

```
1. 技术指标信号 (Easy)     ← 基础模块，其他都依赖它
2. 模拟盘 (Medium-Hard)    ← 最有参与感，体验像真实交易
3. 选股策略 (Medium)       ← 用指标模块选股，结果可直接下单到模拟盘
4. 回测框架 (Hard)         ← 最复杂，可选实施
```
