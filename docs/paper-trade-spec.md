# 模拟盘 Paper Trading — Spec

## 定位

虚拟下单 + 实时盈亏跟踪。用真实行情，假钱练手。
不连接任何券商 API，纯本地模拟。

---

## 后端: `src/trading/paper_trade.py`

### 核心类

```python
class PaperPortfolio:
    initial_capital: float       # 初始资金 (默认 1,000,000)
    cash: float                  # 可用现金
    positions: list[Position]    # 当前持仓
    trades: list[Trade]          # 全部交易记录

    def buy(ticker, name, shares, price) -> Trade
    def sell(ticker, shares, price) -> Trade
    def get_portfolio(prices: dict) -> PortfolioSnapshot
    def reset() -> None
```

### 数据结构

```json
{
  "initial_capital": 1000000,
  "cash": 850000,
  "positions": [
    {
      "ticker": "sh601088",
      "name": "中国神华",
      "shares": 1000,
      "avg_cost": 35.50,
      "buy_date": "2026-05-14"
    }
  ],
  "trades": [
    {
      "id": 1,
      "ticker": "sh601088",
      "name": "中国神华",
      "action": "buy",
      "shares": 1000,
      "price": 35.50,
      "commission": 8.88,
      "amount": 35508.88,
      "time": "2026-05-14T09:35:00"
    }
  ]
}
```

### 持久化

- 文件: `data/portfolio.json`
- 每次交易后写入，启动时读取
- 无数据时自动初始化默认组合

---

## 交易规则

| 规则 | 说明 |
|------|------|
| **T+1** | 当日买入不可当日卖出 (`buy_date < today`) |
| **整手** | 股数必须为 100 的整数倍 |
| **资金检查** | 买入金额 + 佣金 ≤ 可用现金 |
| **仓位上限** | 单票持仓市值 ≤ 总资产 × 10% (可配置) |
| **持仓检查** | 卖出股数 ≤ 当前持仓 |

### 费用

| 费用项 | 费率 | 备注 |
|--------|------|------|
| 佣金 | 万 2.5 (0.025%) | 买卖双向，最低 5 元 |
| 印花税 | 千 1 (0.1%) | 仅卖出时收取 |
| 过户费 | 忽略 | 金额极小，简化处理 |

### 盈亏计算

- **未实现盈亏**: `(current_price - avg_cost) × shares`
- **已实现盈亏**: 卖出交易的 `(sell_price - avg_cost) × shares - fees`
- **总资产**: `cash + Σ(shares × current_price)`
- **总收益率**: `(总资产 - initial_capital) / initial_capital`

---

## API

### `GET /api/portfolio`

返回当前持仓 + 实时盈亏。需要从行情 API 获取最新价格注入。

```json
{
  "ok": true,
  "initial_capital": 1000000,
  "cash": 850000,
  "total_assets": 1002700,
  "total_pnl": 2700,
  "total_pnl_pct": 0.27,
  "realized_pnl": 2000,
  "unrealized_pnl": 700,
  "positions": [
    {
      "ticker": "sh601088",
      "name": "中国神华",
      "shares": 1000,
      "avg_cost": 35.50,
      "current_price": 36.20,
      "market_value": 36200,
      "unrealized_pnl": 700,
      "pnl_pct": 1.97,
      "weight": 3.61,
      "sellable": true
    }
  ]
}
```

### `POST /api/trade`

下单 (买入/卖出)。

**Request:**
```json
{
  "action": "buy",
  "ticker": "sh601088",
  "name": "中国神华",
  "shares": 1000,
  "price": 35.50
}
```

**Response (success):**
```json
{
  "ok": true,
  "trade": {
    "id": 1,
    "action": "buy",
    "ticker": "sh601088",
    "shares": 1000,
    "price": 35.50,
    "commission": 8.88,
    "tax": 0,
    "amount": 35508.88,
    "time": "2026-05-14T09:35:00"
  },
  "cash_after": 964491.12
}
```

**Response (error):**
```json
{
  "ok": false,
  "error": "资金不足: 需要 355008.88, 可用 100000.00"
}
```

**验证错误码:**
| error | 原因 |
|-------|------|
| `资金不足` | cash < amount + commission |
| `仓位超限` | 单票市值 > 总资产 × 10% |
| `T+1限制` | 当日买入当日卖出 |
| `股数必须为100的整数倍` | shares % 100 != 0 |
| `持仓不足` | 卖出股数 > 持有股数 |
| `未知操作` | action 不是 buy/sell |

### `GET /api/trades`

全部交易记录 (最近在前)。

```json
{
  "ok": true,
  "trades": [ ... ],
  "count": 5
}
```

### `POST /api/portfolio/reset`

重置组合到初始状态。

```json
{ "ok": true, "cash": 1000000 }
```

---

## 前端: 模拟盘卡片

### 卡片结构

```
┌─ 模拟盘 Paper Trading ──────────────────────┐
│                                               │
│  总资产: ¥1,002,700   收益: +¥2,700 (+0.27%) │
│  可用: ¥850,000       已实现: +¥2,000         │
│                                               │
│  ── 下单 ──────────────────────────────────── │
│  代码: [sh601088] 名称: 中国神华              │
│  价格: [36.20]    手数: [10]   = 1000股       │
│  [买入]  [卖出]                               │
│                                               │
│  ── 持仓 ──────────────────────────────────── │
│  股票    成本    现价    盈亏     仓位         │
│  中国神华 35.50  36.20  +1.97%   3.6%         │
│  ...                                          │
│                                               │
│  ── 最近交易 ───────────────────────────────  │
│  05-14 09:35  买入 中国神华 1000股 @35.50     │
│  ...                                          │
└───────────────────────────────────────────────┘
```

### 交互

- 代码输入: 支持 watchlist 里的股票代码，自动补全名称和最新价
- 手数输入: 整数，代表 N 手 (N×100 股)
- 买入/卖出按钮: 调用 `POST /api/trade`，成功后刷新持仓
- 持仓表: 红涨绿跌配色，点击可快速填入卖出表单
- 重置按钮: 确认对话框后调用 `POST /api/portfolio/reset`

---

## 实施步骤

1. **后端 `src/trading/paper_trade.py`** — PaperPortfolio 类 + JSON 持久化
2. **API routes** — 在 `server.py` 注册 4 个端点
3. **测试 `tests/test_paper_trade.py`** — 买入/卖出/T+1/费用/边界 cases
4. **前端卡片** — HTML + JS + CSS
5. **集成** — 持仓表从行情 API 获取最新价

---

## 配置

在 `src/config.py` 中添加:

```python
PAPER_TRADE = {
    "initial_capital": 1_000_000,
    "commission_rate": 0.00025,    # 万2.5
    "commission_min": 5.0,         # 最低5元
    "stamp_tax_rate": 0.001,       # 千1, 仅卖出
    "max_position_pct": 0.10,      # 单票上限10%
}
```
