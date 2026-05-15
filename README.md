# 🚀 YYKANPAN（看盘）— A股短线交易助手 V3

> 决策辅助系统：帮你判断"今天能不能做"、"资金在去哪里"、"别冲动"

## 核心能力

| 模块 | 功能 | 数据源 |
|------|------|--------|
| **市场情绪** | 4态机（上升/高潮/分歧/退潮）+ 交易建议 | iWenCai + AkShare |
| **涨跌停统计** | 涨停/跌停家数、连板、最高板 | AkShare |
| **昨日涨停表现** | 胜率 + 平均涨幅 → 短线周期判定 | AkShare |
| **主线识别** | 板块聚类 + 龙头股 + 参与建议 | AkShare |
| **持仓监控** | 实时盈亏、加权涨幅、市值 | Sina + AkShare |
| **宏观指标** | 上证/美元人民币/黄金/原油 实时芯片 | Sina |
| **黑天鹅/灰犀牛** | 异常波动自动扫描 + 时段过滤 | 规则引擎 |
| **八字/五运六气** | 今日四柱 + 岁运/六气/养生/行业提示 | 本地计算 |
| **Watchdog** | 交通灯 🔴🟡🟢 + 情绪变化推送 | 规则引擎 |
| **技术信号** | MA/MACD/RSI/KDJ/布林 指标 + 买卖信号 | Sina K线 |
| **选股策略** | 金叉/放量突破/超跌反弹/涨停接力 | 沪深300+涨停池 |
| **参谋系统** | 持仓评估 + 止盈止损 + 组合建议 | 规则引擎 |
| **决策日志** | 交易/生活/工作决策记录 + 回顾 | 本地JSON |
| **新股新债** | IPO/可转债 申购日历 | AkShare |
| **AI策略** | 偏多/偏空/震荡 + 关注/风险标的 | 规则引擎 |
| **数据源管理** | 自动测速/手动切换数据源优先级 | Sina/AkShare/Yahoo |
| **隐私模式** | 一键隐藏持仓金额 (****) | 前端 |

## 快速开始

```powershell
# 1. 激活环境
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -e .

# 3. 启动
python src/server.py
```

打开 http://127.0.0.1:5000

## 项目结构

```
src/
  config.py           集中配置（环境变量覆盖）
  server.py           Flask 后端 + API
  time_utils.py       UTC+8 时间工具类
  analysis/
    market.py         主线/策略分析
    sentiment.py      情绪判断引擎
    summary.py        终端快速查看
    quant.py          技术指标（MA/MACD/RSI/KDJ/布林）
    screener.py       选股策略引擎
    advisor.py        参谋系统（持仓评估）
  data/
    providers.py      数据源（Sina/AkShare/Yahoo）
    collect_stocks.py 每日 CSV 快照采集
  trading/
    decision.py       决策日志
  tools/
    bazi_core.py      八字/五运六气计算库
static/
  index.html          前端单页面（暗色主题）
  css/style.css       样式表
  js/app.js           前端逻辑（petite-vue + vanilla JS）
data/
  YYYY-MM-DD.csv      每日快照（保留最近5天）
  sentiment_config.json     情绪阈值配置
  sentiment_history.json    情绪历史
  sentiment_last_known.json 情绪缓存
docker/
  Dockerfile          容器构建
  docker-entrypoint.sh  启动脚本（cron + gunicorn）
tests/
  conftest.py             公共 path 设置
  smoke_test.py           集成回归测试（7项）
  test_advisor.py         参谋系统（25项）
  test_analysis.py        分析引擎（21项）
  test_config.py          配置模块（4项）
  test_decision.py        决策日志（24项）
  test_new_features.py    新功能集成（33项）
  test_providers.py       数据源层（22项）
  test_screener.py        选股策略（23项）
  test_sentiment.py       情绪引擎（10项）
  test_server_csv.py      CSV 持久化（11项）
  test_server_trading.py  交易时段逻辑（16项）
  test_time_utils.py      时间工具（5项）
  test_watchlist.py       自选股 CRUD（13项）
  test_xgxz.py            新股新债（11项）
```

## API 端点

| 端点 | 方法 | 说明 | 缓存 |
|------|------|------|------|
| `/api/stocks` | GET | 持仓行情 | 10min |
| `/api/stocks` | POST | 添加自选股 | — |
| `/api/stocks/<ticker>` | DELETE | 删除自选股 | — |
| `/api/refresh/<ticker>` | GET | 刷新单只 | — |
| `/api/history/<ticker>` | GET | 历史K线 | — |
| `/api/limit-stats` | GET | 涨跌停 + 昨涨停表现 | 5min |
| `/api/market-sentiment-auto` | GET | 自动情绪判断 | — |
| `/api/market-sentiment` | POST | 手动情绪判断 | — |
| `/api/sentiment-history` | GET | 情绪历史记录 | — |
| `/api/sentiment-config` | GET/POST | 情绪阈值配置 | — |
| `/api/mainline-auto` | GET | 主线 + 龙头 | — |
| `/api/ai-edge` | GET | AI 策略引擎 | 30min |
| `/api/auto-brief` | GET | 智能简报 | 30min |
| `/api/quickread` | POST | 新闻一键解读 | — |
| `/api/macro-impact` | POST | 宏观事件影响分析 | — |
| `/api/glossary` | GET | 金融术语解释 | — |
| `/api/macro` | GET | 宏观指标（上证/汇率/黄金/原油） | 60s |
| `/api/risk-events` | GET | 黑天鹅/灰犀牛扫描 (`?period=1h\|today\|3d\|7d\|30d`) | — |
| `/api/bazi` | GET | 今日八字 + 五运六气 | — |
| `/api/config/export` | GET | 导出配置 | — |
| `/api/config/import` | POST | 导入配置 | — |
| `/api/signals/<ticker>` | GET | 技术指标信号 | — |
| `/api/screener/strategies` | GET | 选股策略列表 | — |
| `/api/screener` | GET | 执行选股 | — |
| `/api/xingu-xinzhai` | GET | 新股新债日历 | — |
| `/api/decisions` | GET/POST/PUT/DELETE | 决策日志 CRUD | — |
| `/api/advisor` | GET | 参谋系统 | — |
| `/api/macro-history/<symbol>` | GET | 宏观指标历史 | — |
| `/api/providers/test` | POST | 测试所有数据源速度 | — |
| `/api/providers/order` | GET/POST | 获取/设置数据源优先级 | — |
| `/api/providers/auto` | POST | 自动选择最快数据源 | — |

## 数据源优先级（A股）

1. **Sina** — 新浪财经实时行情（快速，逐只查询）
2. **AkShare** — 东方财富（慢，全市场扫描，约3分钟）
3. **Yahoo Finance** — 最终兜底

52周高低价：Sina K线 API（260日线，12小时缓存）

> 可通过 ⚡数据源 按钮或 `/api/providers/auto` 自动测速切换。

## 前端功能

- **Stats Bar**: 14个指标芯片（持仓/涨跌/最强最弱/市值/盈亏/持仓涨幅/涨停/跌停/昨涨停胜率/情绪/建议）
- **宏观指标芯片**: 上证指数/美元人民币/黄金/原油 实时价格 + 涨跌箭头
- **交通灯 Watchdog**: 🟢无告警 / 🟡1-2条 / 🔴3+条；情绪变化自动推送
- **14张 Insight 卡片**: Watchdog、涨跌停、主线、情绪、简报、AI策略、宏观、风险雷达、八字/五运六气、数据源管理、技术信号、选股、参谋、新股新债
- **黑天鹅/灰犀牛雷达**: 自动扫描异常波动，支持 1h/today/3d/7d/30d 时段切换
- **八字/五运六气**: 今日四柱纳音 + 岁运/司天/在泉/主客气 + 养生/行业提示
- **数据源面板**: ⚡ 一键测速、自动选择最快源、手动调整优先级
- **刷新频率选择**: 10s/30s/1m/10m/30m 可选（默认30m）
- **配色切换**: A股（红涨绿跌）/ 美股（绿涨红跌），badge背景跟随切换
- **隐私模式**: 🔓/🔒 按钮一键遮蔽成本/股数/盈亏
- **静默时段**: 15:30-08:30 (UTC+8) 自动暂停刷新
- **持仓预填**: 首次打开自动填入10只持仓

## 自动刷新频率

| 数据 | 间隔 |
|------|------|
| 行情报价 | 可选 10s/30s/1m/10m/30m（默认30m） |
| 宏观指标 | 5 分钟 |
| 涨跌停统计 | 5 分钟 |
| 情绪/主线/简报/AI | 30 分钟 |

## 每日采集（可选）

```powershell
python src/collect_stocks.py          # 手动
.\daily_collect.ps1 -Register         # 注册计划任务（工作日18:00）
```

## 测试

```powershell
python -m pytest tests/                # 225 项全量测试
python -m pytest tests/ -x --tb=short  # 遇错即停
python -m pytest tests/smoke_test.py   # 仅集成烟测（7项）
```

## 技术栈

- Python 3.14+ / Flask
- Sina + AkShare + Yahoo Finance（动态优先级）
- 前端: petite-vue 0.4.1 + vanilla JS + CSS（暗色主题）
- 存储: localStorage（持仓/配置）+ CSV + JSON
- 时区: UTC+8 全链路

## 配置

所有参数通过 `src/config.py` 集中管理，支持 `FUN_*` 环境变量覆盖：

```bash
# 示例：修改端口和缓存时间
FUN_PORT=8080
FUN_STOCKS_CACHE_TTL=300
FUN_SINA_KLINE_TIMEOUT=12
```

完整变量列表见 `.env.example`。复制为 `.env` 即可使用。

## .gitignore

已排除个人数据：watchlist_cn.json、data/*.csv、.env 等。
保留 watchlist_cn_sample.json 作为模板。

## Smoke Regression Test

Run a quick end-to-end smoke test (local API + key endpoint contracts):

```powershell
python -m pytest tests/smoke_test.py
```

Or run the full suite (225 tests):

```powershell
python -m pytest tests/ --tb=short
```

What it checks:
- Core local endpoints (`/api/market-sentiment`)
- Auto endpoints return JSON even under unstable upstream data (`/api/auto-brief`, `/api/ai-edge`, `/api/market-sentiment-auto`, `/api/mainline-auto`)
- Beijing timezone helper output formats

Recommended usage:
- Run before merging significant backend/frontend changes.
- Run after timezone, data-source, or cache-related patches.

Expected result:
- Terminal ends with "Ran N tests" and "OK".
- Upstream source warning logs may still appear and are acceptable if test result is OK.

## Operations Checklist

Daily:
- Start service: `python src/server.py`
- Collect snapshot: `python src/collect_stocks.py`
- Confirm latest data file in data/

Before release:
- Run syntax check: `python -m py_compile src/server.py src/collect_stocks.py src/summary.py`
- Run full tests: `python -m pytest tests/ --tb=short`
- Log changes in PATCH_HISTORY.md

## Troubleshooting

- If root command fails, use `python src/server.py`.
- If Yahoo requests fail due network resets, collector/app fallback providers should still return A-share data.
- Check PATCH_HISTORY.md for recent fixes and validation notes.

Common confusion:
- "No new CSV created today": collector writes one file per date, so same-day runs update existing file.
- "Old files not archived": retention currently deletes files beyond latest 5 instead of moving them to archive.

## Contact

- WeChat: mapleyyy
- Email: lanony82@gmail.com
