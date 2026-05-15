# 黑天鹅 / 灰犀牛 事件分类规范

> Black Swan & Grey Rhino Event Classification Spec

---

## 核心概念

| 类型 | 中文 | 定义 | 特征 |
|------|------|------|------|
| **黑天鹅** | Black Swan | 极低概率、极高冲击、事后才觉合理 | 不可预测、剧烈、不可逆 |
| **灰犀牛** | Grey Rhino | 高概率、高冲击、明明看见却被忽视 | 可预见、渐进积累、忽视风险 |

---

## 分类框架

### 1. 事件来源 (source)

| source | 说明 | 举例 |
|--------|------|------|
| `geopolitical` | 地缘政治 | 外国元首访华、贸易战升级、制裁 |
| `policy` | 国内政策 | 降准降息、印花税调整、IPO暂停 |
| `macro_shock` | 宏观冲击 | 指数暴跌、汇率异动、商品暴涨 |
| `sector` | 行业事件 | 芯片禁令、药品集采、地产暴雷 |
| `company` | 个股事件 | 财务造假、突发退市、重大收购 |
| `external` | 外部冲击 | 疫情、自然灾害、战争 |

### 2. 严重级别 (severity)

| severity | 含义 | 对A股影响 | 持仓建议 |
|----------|------|-----------|----------|
| `critical` | 极端冲击 | 大盘可能跌停/涨停级别 | 立即清仓避险 / 满仓进攻 |
| `high` | 重大影响 | 大盘波动 ≥ 3% | 减仓 / 轻仓防守 |
| `medium` | 显著影响 | 大盘波动 1~3% | 观望 / 结构调仓 |
| `low` | 轻微影响 | 情绪面短暂扰动 | 正常持仓，关注后续 |

### 3. 方向 (direction)

| direction | 说明 |
|-----------|------|
| `bullish` | 利好——推动上涨 |
| `bearish` | 利空——推动下跌 |
| `ambiguous` | 方向不明——取决于后续细节 |

### 4. 时效性 (duration)

| duration | 说明 | 典型 |
|----------|------|------|
| `flash` | 1~3 个交易日内消化 | 领导人讲话、单日数据 |
| `short` | 1~2 周影响 | 贸易谈判回合、政策落地 |
| `medium` | 1~3 个月影响 | 降准周期、制裁升级 |
| `long` | 季度级以上趋势 | 贸易战、产业链重构 |

---

## 事件数据结构

```python
RiskEvent = {
    "type": "黑天鹅" | "灰犀牛",
    "source": "geopolitical" | "policy" | "macro_shock" | "sector" | "company" | "external",
    "severity": "critical" | "high" | "medium" | "low",
    "direction": "bullish" | "bearish" | "ambiguous",
    "duration": "flash" | "short" | "medium" | "long",
    "title": str,          # 简要标题
    "detail": str,         # 详细描述
    "affected_sectors": list[str],   # 受影响板块
    "time": str,           # 发生时间 (UTC+8)
    "auto_detected": bool, # True=系统自动扫描 / False=手动录入
}
```

---

## 黑天鹅 vs 灰犀牛 判定规则

### 黑天鹅 (Black Swan)

事前几乎无法预测，发生后冲击巨大：

| 场景 | 判定依据 | severity |
|------|----------|----------|
| 上证单日暴跌 ≥ 5% | 自动触发 | critical |
| 突发战争/军事冲突 | 手动录入 | critical |
| 疫情级公共卫生事件 | 手动录入 | critical~high |
| 上证单日跌 3~5% | 自动触发 | high |
| 重大金融机构暴雷 | 手动录入 | high |
| 突发外交断裂 | 手动录入 | high |
| 个股跌停 (持仓) | 自动触发 | high |
| 汇率单日波动 ≥ 1.5% | 自动触发 | high |
| 黄金单日波动 ≥ 4% | 自动触发 | medium~high |

### 灰犀牛 (Grey Rhino)

明明可以预见、却被市场忽视的大概率风险：

| 场景 | 判定依据 | severity |
|------|----------|----------|
| 贸易战持续升级 | 手动录入 | high~medium |
| 地产债务危机蔓延 | 手动录入 | high |
| 美联储连续加息周期 | 手动录入 | medium |
| 外资持续净流出 (>N日) | 可自动 | medium |
| 人民币持续贬值趋势 | 可自动 | medium |
| 某行业监管风暴渐起 | 手动录入 | medium |
| 市场连续缩量阴跌 | 可自动 | medium~low |
| 外国元首访华 (如 Trump) | 手动录入 | medium |
| IPO/再融资提速 | 手动录入 | low~medium |

---

## 实例：Trump 访华

```json
{
  "type": "灰犀牛",
  "source": "geopolitical",
  "severity": "medium",
  "direction": "ambiguous",
  "duration": "short",
  "title": "特朗普访华",
  "detail": "美国总统访华，可能涉及贸易协议、关税调整、科技管控等议题。历史上外国元首访华期间A股多数走稳，但具体协议内容可能引发板块分化。",
  "affected_sectors": ["半导体", "军工", "消费", "稀土", "农业"],
  "time": "2026-05-12 08:00",
  "auto_detected": false
}
```

**为什么是灰犀牛而非黑天鹅？**
- 访问是提前公开的（可预见）→ 不符合黑天鹅"不可预测"
- 但市场常低估地缘事件的实际影响 → 典型灰犀牛特征
- 方向 `ambiguous`：可能利好（达成协议）也可能利空（谈崩）
- **如果访问期间出台意外重大协议/制裁** → 升级为黑天鹅 `critical`

---

## 分级触发矩阵 (建议动作)

| severity | direction=bearish | direction=bullish | direction=ambiguous |
|----------|-------------------|-------------------|---------------------|
| critical | 清仓避险 | 满仓进攻 | 减仓至半仓 |
| high | 减仓 50% | 加仓至 8 成 | 减仓至 6 成 |
| medium | 轻仓观望 | 正常持仓 | 正常持仓，设止损 |
| low | 正常持仓 | 正常持仓 | 正常持仓 |

---

## 与现有系统的集成

### 当前实现 (V1 — 自动扫描)

已有：基于价格波动的自动检测（`_scan_risk_events()`）

| 数据源 | 黑天鹅阈值 | 灰犀牛阈值 |
|--------|-----------|-----------|
| 上证指数 | ≥ 5% | ≥ 3% |
| 美元/人民币 | ≥ 1.5% | ≥ 0.5% |
| 黄金 | ≥ 4% | ≥ 2% |
| 原油 | ≥ 6% | ≥ 3% |
| 持仓个股 | 跌停 | ≥ 5% |

### 未来扩展 (V2 — 手动录入 + 模板)

| 功能 | 描述 |
|------|------|
| 手动事件录入 | UI 表单录入地缘/政策事件 |
| 事件模板库 | 预置常见事件模板（元首访问、降准、制裁等） |
| 板块联动 | 事件关联受影响板块，自动标记持仓风险 |
| 事件升降级 | 灰犀牛 → 黑天鹅 的升级机制 |
| 历史对比 | 相似历史事件的A股表现参考 |

---

## 常见事件模板参考

| 事件类型 | 默认分类 | severity | direction | duration | 受影响板块 |
|----------|---------|----------|-----------|----------|-----------|
| 外国元首访华 | 灰犀牛 | medium | ambiguous | short | 消费/军工/科技 |
| 降准降息 | 灰犀牛 | medium | bullish | medium | 银行/地产/券商 |
| 印花税下调 | 黑天鹅 | high | bullish | flash | 全市场 |
| 贸易关税加征 | 灰犀牛 | high | bearish | medium | 出口/科技/农业 |
| 芯片制裁升级 | 灰犀牛 | high | bearish | long | 半导体/科技 |
| 突发战争 | 黑天鹅 | critical | bearish | short~medium | 全市场/军工利好 |
| 重大疫情爆发 | 黑天鹅 | critical | bearish | long | 全市场/医药利好 |
| 央行逆回购放量 | 灰犀牛 | low | bullish | flash | 银行/券商 |
| 地产公司暴雷 | 灰犀牛 | high | bearish | medium | 地产/银行/建材 |
| IPO 暂停/收紧 | 灰犀牛 | medium | bullish | short | 券商/次新股 |
