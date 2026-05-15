# A-Share Dashboard: No-LLM Improvements Roadmap

> ⚠️ **状态说明 (2026-05 更新)**：部分功能已在 v2.x–v3.2 迭代中以不同形式实现。
> 标记 ✅ = 已实现（可能方案不同）、⏳ = 部分实现、❌ = 未做。
> 代码已从 `src/app.py` 迁移到 `src/server.py` + `src/analysis/` + `src/trading/`。

---

## Tier 1: 立即可做（0-2 小时）

### 1.1 体积陷阱检测 (Volume Trap Detection) ❌

**问题**：
- 当前输出 "适合交易" 不考虑成交量确认
- 价格上升但量萎缩 = 虚假突破 (Bull Trap)

**改进方案**：

```python
# 新增函数在 src/app.py
def _evaluate_market_sentiment_with_volume(
    up_count: int,
    down_count: int,
    limit_up_count: int,
    consecutive_limit_count: int,
    avg_volume: float,  # 新参数
    historical_avg_volume: float,  # 基准（默认 1.0 = 历史均值）
) -> dict:
    """
    增强版情绪判断，加入体积确认。
    """
    # 保留原有逻辑
    base_result = _evaluate_market_sentiment(
        up_count, down_count, limit_up_count, consecutive_limit_count
    )
    
    # 新增体积检查
    volume_ratio = avg_volume / historical_avg_volume if historical_avg_volume > 0 else 1.0
    
    # 体积确认规则
    if base_result["tradable"] and volume_ratio < 0.6:
        # 价涨量萎 → 降级风险等级
        base_result["tradable"] = False
        base_result["volume_warning"] = f"价涨量萎 (体积比 {volume_ratio:.1%})，警惕虚假突破"
    elif not base_result["tradable"] and volume_ratio > 1.5:
        # 量能异常放大 + 下跌 → 可能是底部信号
        base_result["volume_signal"] = f"异常放量 ({volume_ratio:.1%})，注意底部反包机会"
    
    return base_result
```

**实现步骤**：
1. 在 `/api/market-sentiment-auto` 端点中，从前 10 只涨停股票计算 `avg_volume`
2. 存储 `历史均值` 在 `data/market_metrics.json`（初始值 = 今天成交量）
3. 前端显示 `volume_warning` 或 `volume_signal`

**成本**：1-2 小时  
**收益**：🔴 显著降低虚假信号

---

### 1.2 宏观事件→持仓映射 (Macro Impact on Portfolio) ✅ (macro_impact in analysis/market.py)

**问题**：
- CPI 高 + 利率高 的消息存在，但不知道对我的持仓有什么影响
- 用户需要"懒人连接"：新闻 → 我的股票

**改进方案**：

```python
# 新增配置表在 src/app.py
MACRO_SECTOR_IMPACT = {
    "inflation_risk": {
        "sectors": ["消费", "食品饮料", "白酒", "家电"],
        "direction": "negative",
        "description": "通胀压力下，消费景气下行，龙头估值承压"
    },
    "rate_hike_risk": {
        "sectors": ["成长", "科技", "新能源", "医药"],
        "direction": "negative",
        "description": "利率上升，贴现率提高，高成长股估值压制"
    },
    "liquidity_loose": {
        "sectors": ["消费", "新能源", "科技", "券商"],
        "direction": "positive",
        "description": "流动性宽松，风险偏好提升，成长股受益"
    },
    "credit_tightening": {
        "sectors": ["房产", "建筑", "基建"],
        "direction": "negative",
        "description": "信用紧缩环境，融资成本提高，周期股承压"
    }
}

# 新增函数
def _analyze_macro_portfolio_impact(
    holdings: dict,  # {ticker: {"name": "...", "sector": "...", "shares": N}}
    macro_conditions: dict,  # {"inflation": "high", "rate": "rising", "liquidity": "loose"}
) -> dict:
    """
    返回持仓中哪些股票会被当前宏观条件影响。
    """
    portfolio_risk = {
        "positive_impacts": [],
        "negative_impacts": [],
        "summary": ""
    }
    
    for ticker, stock_info in holdings.items():
        sector = stock_info.get("sector", "")
        for macro_factor, impact_rule in MACRO_SECTOR_IMPACT.items():
            if sector in impact_rule["sectors"]:
                if macro_conditions.get(macro_factor) == impact_rule["trigger"]:
                    if impact_rule["direction"] == "negative":
                        portfolio_risk["negative_impacts"].append({
                            "ticker": ticker,
                            "name": stock_info["name"],
                            "reason": impact_rule["description"]
                        })
                    else:
                        portfolio_risk["positive_impacts"].append({
                            "ticker": ticker,
                            "name": stock_info["name"],
                            "reason": impact_rule["description"]
                        })
    
    # 生成人话总结
    if portfolio_risk["negative_impacts"]:
        portfolio_risk["summary"] = f"当前宏观环境对持仓不利：{len(portfolio_risk['negative_impacts'])} 只股票面临压力"
    
    return portfolio_risk
```

**实现步骤**：
1. 新增 POST `/api/macro-portfolio-impact` 接口
2. 需要输入：持仓列表 + 当前宏观条件（CPI、利率、流动性）
3. 前端在"AI 核心策略"卡片下方显示受影响股票清单

**成本**：1-2 小时  
**收益**：🔴 显著提升"为什么我的股票跌了"的透视度

---

### 1.3 主题旋转预警 (Theme Rotation Risk) ❌

**问题**：
- 当前只说"主线板块是新能源电池"，没说这个主线有多"老"
- 新手容易在主线已领跑 5+ 天后还在追，导致"追顶"

**改进方案**：

```python
# 新增数据文件 data/mainline_history.json
# 格式：{date: {sector, leader_code, leader_name}, ...}

# 新增函数在 src/app.py
def _detect_theme_rotation_risk(
    current_sector: str,
    history_file_path: str,
    recent_days: int = 5
) -> dict:
    """
    检测主线板块是否即将轮换。
    逻辑：
    - 同一主线连续 1-2 天 → "新兴主线"，可追
    - 同一主线连续 3-4 天 → "成熟主线"，谨慎
    - 同一主线连续 5+ 天 → "老化主线"，防追顶
    """
    try:
        history = json.loads(Path(history_file_path).read_text(encoding="utf-8"))
    except:
        return {"ok": False, "msg": "历史数据暂不可用"}
    
    recent_dates = sorted(list(history.keys()))[-recent_days:]
    recent_sectors = [history[d].get("sector") for d in recent_dates]
    
    # 计算连续天数
    streak = 1
    for i in range(len(recent_sectors) - 1, 0, -1):
        if recent_sectors[i] == recent_sectors[i-1]:
            streak += 1
        else:
            break
    
    if streak >= 5:
        risk_level = "高"
        suggestion = "主线已领跑 5+ 天，可能即将轮换，新手建议观望"
    elif streak >= 3:
        risk_level = "中"
        suggestion = "主线已领跑 3-4 天，进场需要等量能确认"
    elif streak >= 1:
        risk_level = "低"
        suggestion = "新兴主线，可关注低位布局机会"
    
    return {
        "ok": True,
        "sector": current_sector,
        "consecutive_days": streak,
        "risk_level": risk_level,
        "suggestion": suggestion
    }
```

**实现步骤**：
1. 在 `_analyze_mainline_auto()` 后面调用 `_detect_theme_rotation_risk()`
2. 每天自动更新 `data/mainline_history.json`
3. 返回结果添加到 `/api/mainline-auto` 响应

**成本**：1-2 小时（需要建立日志系统）  
**收益**：🟠 防止"追顶"风险，适合新手教育

---

## Tier 2: 推荐做（1-2 小时）

### 2.1 连板强度分级 (Limit-Up Intensity Grade) ✅ (sentiment.py 已有连板分级输出)

**简化版**：不是只返回 `consecutive_limit_count` 数字，而是返回一个强度等级。

```python
def grade_consecutive_strength(consecutive_limit_count: int) -> str:
    if consecutive_limit_count >= 10:
        return "🔥 超强 (10+连板)"
    elif consecutive_limit_count >= 5:
        return "强势 (5-9连板)"
    elif consecutive_limit_count >= 2:
        return "中等 (2-4连板)"
    else:
        return "弱势 (<2连板)"
```

**成本**：0.5 小时  
**收益**：🟠 改善输出易读性

---

### 2.2 持仓分散度评分 (Portfolio Diversification Score) ✅ (advisor.py 集中度检测)

**问题**：用户持仓 10 只股票都是"消费"，市场一旦消费走弱就全线亏

**改进**：
```python
def calc_portfolio_concentration(holdings: list) -> dict:
    """
    holdings = [{"ticker": "...", "sector": "..."}, ...]
    返回各行业占比 + 集中度评分
    """
    from collections import Counter
    
    sectors = [h.get("sector", "未分类") for h in holdings]
    sector_dist = Counter(sectors)
    
    # Herfindahl 指数（行业集中度）
    total = len(holdings)
    herfindahl = sum((count/total)**2 for count in sector_dist.values())
    
    risk_level = "低" if herfindahl < 0.3 else "中" if herfindahl < 0.5 else "高"
    
    return {
        "sector_distribution": dict(sector_dist),
        "concentration_score": round(herfindahl, 2),
        "risk_level": risk_level,
        "advice": "建议分散到 3+ 个行业，降低系统风险" if risk_level == "高" else "分散度合理"
    }
```

**新增端点**：`GET /api/portfolio-diversification`  
**成本**：1 小时  
**收益**：🟠 教育用户风险管理

---

### 2.3 主题"热度"衰减曲线 (Theme Heat Decay) ❌

**概念**：主线板块的"热度"会随时间衰减。第 1 天 100 热度，第 5 天可能只有 30。

```python
def calc_theme_heat_decay(
    consecutive_days: int,
    initial_heat: float = 100.0,
    decay_rate: float = 0.7  # 每天保留 70%
) -> dict:
    current_heat = initial_heat * (decay_rate ** (consecutive_days - 1))
    
    if current_heat > 70:
        status = "火热"
    elif current_heat > 40:
        status = "温热"
    else:
        status = "冷却中"
    
    return {
        "current_heat": round(current_heat, 1),
        "status": status,
        "days_until_cold": next((d for d in range(1, 10) if initial_heat * (decay_rate**d) < 30), None)
    }
```

**成本**：2 小时（需整合历史数据）  
**收益**：🟠 中等

---

## Tier 3: 架构优化（2-3 小时）

### 3.1 龙头股策略模式 ✅ (screener.py HybridLeader 已实现)

**当前**：硬编码一个 `leader_score` 公式  
**改进**：使用策略模式，支持多种龙头识别方法

```python
from abc import ABC, abstractmethod

class LeaderStrategy(ABC):
    @abstractmethod
    def rank(self, stocks_df) -> list:
        pass

class TurnoverLeader(LeaderStrategy):
    """按成交额排序"""
    def rank(self, stocks_df):
        return stocks_df.nlargest(3, "成交额")

class MomentumLeader(LeaderStrategy):
    """按涨幅排序"""
    def rank(self, stocks_df):
        return stocks_df.nlargest(3, "涨跌幅")

class HybridLeader(LeaderStrategy):
    """综合评分：成交额 60% + 涨幅 40%"""
    def rank(self, stocks_df):
        stocks_df["hybrid_score"] = (
            stocks_df["成交额"].rank(pct=True) * 0.6 +
            stocks_df["涨跌幅"].rank(pct=True) * 0.4
        )
        return stocks_df.nlargest(3, "hybrid_score")

# 使用
strategy = HybridLeader()
leaders = strategy.rank(sector_stocks)
```

**成本**：2-3 小时  
**收益**：🟡 代码可维护性提升，易于添加新算法

---

### 3.2 静态/动态数据分离 (Static vs. Dynamic Data Split) ❌

**当前**：每次 `/api/stocks` 都抓一遍所有数据  
**改进**：分离端点

```
GET /api/stocks/meta  # 公司名、行业、标签（日级缓存，24小时）
GET /api/stocks/live  # 价格、涨跌%（10分钟缓存）

前端合并：
meta_data = GET /api/stocks/meta
live_data = GET /api/stocks/live
result = merge(meta_data, live_data)
```

**收益**：
- 减少上游 API 调用 50%
- 前端加载速度快 40%

**成本**：2-3 小时  
**收益**：🟡 性能优化

---

## Tier 4: 数据持久化（1-2 小时）

新增/修改的数据文件：

```
data/
├── sentiment_last_known.json      # 已有
├── market_metrics.json            # 新：日均成交量、波动率等基准值
├── mainline_history.json          # 新：主线板块的 5 天历史
└── portfolio_snapshot.json        # 新：每天的持仓快照（用于计算涨跌）
```

**实现**：在 `src/collect_stocks.py` 中每次运行自动更新这些文件

---

## 推荐实施顺序

**第 1 天**：
1. ✅ 体积陷阱检测 (1.1) — 最高收益
2. ✅ 宏观→持仓映射 (1.2) — 最高收益
3. ✅ 连板强度分级 (2.1) — 快速赢

**第 2 天**：
1. ✅ 主题旋转预警 (1.3) — 需要历史数据累积
2. ✅ 龙头股策略模式 (3.1) — 代码质量

**第 3 天**：
1. ✅ 静态/动态分离 (3.2) — 性能优化
2. ✅ 主题热度衰减 (2.3) — 可选

---

## 预期效果

完成 Tier 1 + Tier 2 后：

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| **风险识别能力** | 单维度 (只看涨跌) | 三维度 (涨跌 + 体积 + 宏观) |
| **新手保护** | 无 | 高 (虚假突破 + 追顶预警) |
| **持仓透视度** | 低 (只看个股) | 高 (知道为什么跌) |
| **API 调用成本** | 基础 | 降低 50% |
| **代码可维护性** | 一般 | 优良 |

---

## 工作量总计

- **Tier 1 全部**：4-6 小时
- **+ Tier 2 推荐**：+2-3 小时
- **+ Tier 3 关键项**：+4-6 小时
- **总计（推荐方案）**：10-12 小时，分 2-3 天完成

