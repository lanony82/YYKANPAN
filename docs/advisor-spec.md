# Advisor Module Spec (Trading Advisor)

## 定位
参谋系统，不是自动交易。基于行情/持仓/情绪/风险事件给出可解释建议。

## 数据结构

### 输入: AdvisorInput
- positions: list[PositionInput]
  - ticker, name, shares, cost, price, change_pct, high52, low52, volume
- context: MarketContext
  - regime ("偏强"|"偏弱"|"震荡"), sentiment_stage ("上升"|"退潮"|"分歧")
  - sentiment_score (-4~+4), tradable (bool), confidence (10~95)
  - risk_events: list[dict] (type, severity, title, detail, time)
- risk_pref: "conservative" | "balanced" | "aggressive"

### 输出: AdvisorOutput
- ok, generated_at, strategy_name
- signals: list[Signal]
  - ticker, name, action ("buy"|"sell"|"hold"|"reduce"|"add")
  - strength (1~5), reasons (list[str]), stop_loss, take_profit
- portfolio_action: "加仓"|"减仓"|"观望"|"清仓避险"
- portfolio_reason: str

## Strategy Protocol
```python
class Strategy(Protocol):
    name: str
    def evaluate(self, position, context, risk_pref) -> Signal: ...
```

## V1 RuleBasedStrategy Rules
| Rule | Condition | Signal |
|------|-----------|--------|
| 止损 | loss ≥ threshold (conserv 7%/balanced 10%/aggr 15%) | sell, str=5 |
| 止盈 | gain ≥ threshold (conserv 15%/balanced 25%/aggr 40%) | reduce, str=3 |
| 52周高 | price ≥ high52×0.97 | reduce, str=2 |
| 52周低 | price ≤ low52×1.03 且 regime≠"偏弱" | add, str=2 |
| 黑天鹅 | severity=high risk event | sell, str=4 |
| 退潮 | sentiment="退潮" + !tradable | hold, str=3 |
| 无信号 | none above | hold, str=1 |

Multiple rules → highest strength wins, reasons merged.

## Portfolio-Level Rules
| Condition | Action |
|-----------|--------|
| 黑天鹅 | "清仓避险" |
| sell ≥ 50% positions | "减仓" |
| 上升 + confidence>70 + no sell | "加仓" |
| else | "观望" |

## Boundary Conditions
- Empty positions → ok=True, signals=[], "观望"
- price=0 → hold, reasons=["数据缺失"]
- high52/low52=None → skip 52w rules
- cost=0 → skip P&L rules, market signals only
- Invalid risk_pref → default "balanced"

## Error Handling
- Sentiment unavailable → tradable=True, individual signals only
- risk_events fetch fail → no events, skip 黑天鹅 rule
- All stock data bad → ok=False, msg="行情数据不可用"
- Strategy exception → hold, str=1, reasons=["策略异常"]

## Files
- src/advisor.py — Strategy protocol + RuleBasedStrategy + evaluate_portfolio()
- tests/test_advisor.py — 25 test cases covering all rules + edges
- server.py — GET /api/advisor?risk_pref=balanced&positions=[...]

## Test Matrix (25 cases)
1. Empty positions → signals=[], "观望"
2. Stop-loss triggered (conservative) → sell, str=5
3. Stop-loss not triggered (balanced threshold)
4. Stop-loss not triggered (aggressive threshold)
5. Take-profit triggered (balanced)
6. Take-profit triggered (conservative)
7. Near 52w high → reduce
8. Not near 52w high → no trigger
9. Near 52w low + non-weak → add
10. Near 52w low + weak → hold
11. Black swan → sell str=5
12. Black swan → portfolio "清仓避险"
13. Grey rhino (medium severity) → no sell
14. 退潮 → hold, str=2
15. Multi-rule conflict → highest strength wins
16. price=0 → hold, "数据缺失"
17. All data bad → ok=False
18. cost=0 → skip P&L
19. Custom strategy injection (mock)
20. Strategy exception caught → hold
21. 上升+high confidence → portfolio "加仓"
22. 上升+low confidence → "观望"
23. Majority sell → portfolio "减仓"
24. Invalid risk_pref → defaults to balanced
25. Price suggestions (stop_loss/take_profit values)

---

## V2 YAMLStrategy (v3.2+)

策略可从 YAML 声明式配置加载，与 RuleBasedStrategy 实现同一 Strategy Protocol。

> 设计决策、YAML 结构示例、评估器注册表详见 [ADR-008](ADR.md#adr-008-autodev--yaml-策略声明--自动决策循环)。

### 与 RuleBasedStrategy 的关系

| 维度 | RuleBasedStrategy | YAMLStrategy |
|------|-------------------|--------------|
| 配置 | 硬编码在 advisor.py | `data/strategies/*.yaml` |
| 热加载 | ✗ | ✓ |
| 因子权重 | 固定 | 可调 |
| Protocol | Strategy | Strategy |

两者可互换注入 `evaluate_portfolio()`。

### AutoDev 集成

`YAMLStrategy` 是 AutoDev 循环的决策核心：
```
AutoDev.decide() → strategy.evaluate(pos, ctx, risk_pref) → Signal
```
