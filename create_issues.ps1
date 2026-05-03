# YYKANPAN GitHub Issues 批量创建脚本
# 使用前：安装 gh CLI 并运行 gh auth login
# 运行：.\create_issues.ps1

$repo = "lanony82/YYKANPAN"

# ═══════════════════════════════════════════════════════════════════
# 第一阶段：地基夯实 (Phase 1: Foundation)
# ═══════════════════════════════════════════════════════════════════

gh issue create --repo $repo `
  --title "1.1 建立自动化测试与 CI 流水线" `
  --label "phase-1,priority-high,enhancement" `
  --body @"
## 优先级：🔴 最高 | 预计工作量：2-3 周

## 描述
目前项目仅有 smoke_test.py 一个手工测试脚本，核心模块的任何修改都可能无声地引入错误。需要为关键模块编写单元测试和集成测试，并接入 GitHub Actions，在每次 push 或 PR 时自动运行。

## 子任务
- [ ] 引入 pytest 和 pytest-cov 到开发依赖
- [ ] 为 sentiment.py 中的四态机计算逻辑编写单元测试（覆盖已知边界组合）
- [ ] 为 providers.py 中的解析函数编写 mock 测试（模拟 AkShare/Sina 原始返回）
- [ ] 编写端到端测试：用预设 CSV 样本数据启动 server.py，请求 API 验证返回 JSON
- [ ] 创建 .github/workflows/test.yml（Python 3.12+ 安装依赖、运行测试、覆盖率）
- [ ] 在 README 顶部添加 CI 状态徽章

## 验收标准
- 核心模块（sentiment, providers, analysis）测试覆盖率 ≥ 70%
- 所有 PR 必须通过 CI 测试才能合并
- 新贡献者可以运行 pytest 并看到本地测试结果
"@

gh issue create --repo $repo `
  --title "1.2 容器化部署与一键启动" `
  --label "phase-1,priority-high,enhancement" `
  --body @"
## 优先级：🔴 最高 | 预计工作量：1-2 周

## 描述
当前部署要求 Python 3.14+ 且需手动安装依赖，对非开发者极不友好。通过 Dockerfile 和 docker-compose.yml，用户可以一行命令拉起整个服务。

## 当前状态
✅ Dockerfile 和 docker-compose.yml 已创建（docker/ 目录）
✅ 数据卷挂载已配置

## 剩余子任务
- [ ] 更新 README 增加"📦 五分钟快速开始"章节（docker compose up -d 完整命令）
- [ ] 验证 Docker 构建并在干净环境测试
- [ ] （可选）提供 install.sh 脚本：自动检测 Python、创建虚拟环境、安装依赖

## 验收标准
- 一台仅安装了 Docker 的机器，执行两条命令后即可在浏览器访问完整看板
- 数据目录在容器重启后不丢失
"@

gh issue create --repo $repo `
  --title "1.3 文档分层与故障排查指南" `
  --label "phase-1,priority-medium,documentation" `
  --body @"
## 优先级：🟡 中 | 预计工作量：1 周

## 描述
README 虽然详尽，但缺乏面向非技术用户的"如何排错"内容。需要新增 FAQ 和故障排查文档，并在代码中增强错误提示。

## 子任务
- [ ] 新建 docs/FAQ.md（数据不更新、配色切换、自定义自选股等）
- [ ] 新建 docs/TROUBLESHOOTING.md（网络超时、端口占用、数据源全失效等）
- [ ] 改进 server.py 和 providers.py 错误消息（三个源全部失败时输出友好提示）
- [ ] 添加新手操作指南/功能说明/指标解释

## 验收标准
- 用户遇到 80% 的操作问题能在文档中找到答案，无需阅读源码
"@

gh issue create --repo $repo `
  --title "1.4 数据备份与恢复工具" `
  --label "phase-1,priority-medium,enhancement" `
  --body @"
## 优先级：🟡 中 | 预计工作量：2-3 天

## 描述
配置文件和数据散落在本地，缺乏简单的备份手段。提供小脚本让用户一键归档当前状态。

## 子任务
- [ ] 实现 utils/backup.py：将 data/、watchlist_cn.json 等打包为带日期的压缩包
- [ ] server.py 启动时增加轻量数据完整性检查，损坏时提示备份恢复
- [ ] 文档中说明如何从备份恢复

## 验收标准
- 用户可以随时执行备份命令，拿到一个可迁移的压缩包
"@

gh issue create --repo $repo `
  --title "1.5 配置与代码解耦" `
  --label "phase-1,priority-high,enhancement" `
  --body @"
## 优先级：🔴 最高 | 预计工作量：1 周

## 描述
项目配置参数（缓存TTL、数据源超时、端口等）与业务代码耦合，缺乏独立配置文件，不利于环境切换和参数修改。

## 子任务
- [ ] 创建 config.py 或 .env 配置文件，提取所有可配置参数
- [ ] 支持环境变量覆盖（生产/开发/测试模式切换）
- [ ] 更新文档说明配置方式

## 验收标准
- 修改配置无需改动代码文件
- 支持通过环境变量 override 任何配置项
"@

gh issue create --repo $repo `
  --title "1.6 完善日志系统" `
  --label "phase-1,priority-medium,enhancement" `
  --body @"
## 优先级：🟡 中 | 预计工作量：1 周

## 描述
当前依赖 console 输出，缺乏分类持久化日志，问题定位和故障追踪困难。

## 子任务
- [ ] 引入 Python logging 模块，按级别分类（INFO/WARNING/ERROR）
- [ ] 持久化日志到 logs/ 目录，按日期轮转
- [ ] 数据源调用记录耗时和成功/失败状态
- [ ] Docker 环境下日志输出到 stdout（便于 docker logs 查看）

## 验收标准
- 可通过日志快速定位数据源故障和异常请求
- 日志文件自动轮转，不无限膨胀
"@

# ═══════════════════════════════════════════════════════════════════
# 第二阶段：体验升级 (Phase 2: Experience)
# ═══════════════════════════════════════════════════════════════════

gh issue create --repo $repo `
  --title "2.1 引入 SQLite 替代 CSV 存储" `
  --label "phase-2,priority-high,enhancement" `
  --body @"
## 优先级：🔴 最高 | 预计工作量：3-4 周

## 描述
短线复盘需要更长历史视角，当前 CSV 只存 5 天。SQLite 零配置、单文件、支持高效查询，是本地工具理想存储。

## 子任务
- [ ] 设计表结构：market_snapshot、limit_up_stats、sentiment_log 等
- [ ] 实现 storage.py 模块，封装读写接口
- [ ] 编写 CSV 到 SQLite 数据迁移脚本
- [ ] 为高频查询字段建立索引（确保数月数据查询 < 100ms）
- [ ] 新增 API（/api/history/sentiment?date=YYYY-MM-DD）支持按日查询

## 验收标准
- 存储一年数据后单次查询耗时 < 100ms
- 用户可查看任意历史日期的情绪状态和关键指标
- 旧 CSV 数据能平滑迁移
"@

gh issue create --repo $repo `
  --title "2.2 前端渐进式增强（局部刷新+趋势微图）" `
  --label "phase-2,priority-medium,enhancement" `
  --body @"
## 优先级：🟡 中 | 预计工作量：2-4 周

## 描述
保持现有轻量架构，引入 HTMX 或优化 petite-vue 实现局部刷新和趋势微图，避免整页重载。

## 子任务
- [ ] 使指标卡片区域支持定时自动刷新（无白屏闪烁）
- [ ] 为每个卡片添加近 5 日趋势小图（sparkline）
- [ ] 后台提供 mini 数据接口
- [ ] 优化刷新动效

## 验收标准
- 看板数据按设定间隔自动更新，无白屏闪烁
- 每个指标卡片包含趋势微图，鼠标悬停可看简要数值
"@

gh issue create --repo $repo `
  --title "2.3 数据源健康仪表盘" `
  --label "phase-2,priority-low,enhancement" `
  --body @"
## 优先级：🟢 较低 | 预计工作量：1-2 周

## 描述
三层数据源虽然增加了可靠性，但用户完全不知道当前在用哪个源、各源健康状况如何。

## 子任务
- [ ] providers.py 中埋点：记录每次调用耗时和成功/失败
- [ ] 新增 /api/health/sources 接口（各源最近 1h/24h 成功率和平均延迟）
- [ ] 前端某个数据源连续失败时弹出"已自动切换备用源"提示

## 验收标准
- 管理页面或状态栏可直观看到数据源健康度
- 切换备用源对用户透明，同时有日志可查
"@

gh issue create --repo $repo `
  --title "2.4 策略信号可配置化" `
  --label "phase-2,priority-medium,enhancement" `
  --body @"
## 优先级：🟡 中 | 预计工作量：2-3 周

## 描述
当前情绪四态机阈值硬编码。不同交易者有不同风险偏好，应允许调整。

## 当前状态
✅ 前端已有情绪阈值设置面板（牛市/震荡/熊市预设）
✅ sentiment_config.json 已支持保存配置

## 剩余子任务
- [ ] 创建 strategies/default.yaml 存放所有可配置参数及默认值
- [ ] 支持导出和导入策略文件
- [ ] 支持保存多套策略并随时切换

## 验收标准
- 用户修改阈值后看板信号实时变化
- 可以保存多套策略随时切换
"@

gh issue create --repo $repo `
  --title "2.5 自选股分组管理" `
  --label "phase-2,priority-medium,enhancement" `
  --body @"
## 优先级：🟡 中 | 预计工作量：1-2 周

## 描述
当前所有自选股在一个列表中，无法按板块/策略分组查看。

## 子任务
- [ ] 支持创建自选股分组（如"短线龙头"、"中线底仓"等）
- [ ] 每只股票可属于多个分组
- [ ] 前端增加分组筛选切换
- [ ] 分组配置持久化到 localStorage 或后端 JSON

## 验收标准
- 用户可创建/编辑/删除分组
- 切换分组时表格只显示对应股票
"@

gh issue create --repo $repo `
  --title "2.6 数据导出与复盘笔记" `
  --label "phase-2,priority-low,enhancement" `
  --body @"
## 优先级：🟢 较低 | 预计工作量：1-2 周

## 描述
缺乏交易数据导出和在线复盘笔记记录功能。

## 子任务
- [ ] 支持导出当日持仓/盈亏为 CSV/Excel
- [ ] 增加每日复盘笔记输入框（保存到 data/notes/）
- [ ] 笔记可按日期查看历史

## 验收标准
- 用户可一键导出交易数据
- 可记录和查阅历史复盘笔记
"@

gh issue create --repo $repo `
  --title "2.7 优化移动端适配" `
  --label "phase-2,priority-medium,enhancement" `
  --body @"
## 优先级：🟡 中 | 预计工作量：1-2 周

## 描述
前端界面未针对移动设备优化，小屏幕设备上显示和操作体验差。

## 子任务
- [ ] 卡片在移动端自动切换为单列布局
- [ ] 表格在移动端可左右滑动或折叠非关键列
- [ ] 操作按钮增大触控区域
- [ ] 测试 iPhone / Android 主流分辨率

## 验收标准
- 手机浏览器可正常使用所有核心功能
- 不出现水平滚动条（表格除外）
"@

# ═══════════════════════════════════════════════════════════════════
# 第三阶段：智能进化 (Phase 3: Intelligence)
# ═══════════════════════════════════════════════════════════════════

gh issue create --repo $repo `
  --title "3.1 插件化信号源" `
  --label "phase-3,priority-low,enhancement" `
  --body @"
## 优先级：🟢 较低（长期） | 预计工作量：3-4 周

## 描述
设计简单插件接口，允许第三方贡献指标或信号插件，无需修改核心代码。

## 子任务
- [ ] 定义 SignalPlugin 抽象基类
- [ ] 创建 plugins/ 目录，启动时自动发现和加载
- [ ] 提供示例插件（如"炸板率过高告警"、"北向资金异动"）
- [ ] 编写插件开发文档

## 验收标准
- 用户放入一个 Python 文件到 plugins/ 即可在界面上看到新指标
"@

gh issue create --repo $repo `
  --title "3.2 桌面应用打包 / 一键私有化部署" `
  --label "phase-3,priority-low,enhancement" `
  --body @"
## 优先级：🟢 较低 | 预计工作量：2-3 周

## 描述
针对不想接触命令行的用户，提供双击运行的桌面程序或免费部署模板。

## 可能方案
- PyInstaller 打包成 Mac/Windows 单文件
- 或提供 Sealos / Railway 模板一键部署到个人服务器
- 或 Electron 打包为桌面应用

## 验收标准
- 非技术用户可双击运行或一键部署后使用
"@

gh issue create --repo $repo `
  --title "3.3 复盘回放功能" `
  --label "phase-3,priority-low,enhancement" `
  --body @"
## 优先级：🟢 较低 | 预计工作量：3-4 周

## 描述
利用 SQLite 历史数据，实现逐分钟回放某天的情绪指标变化，辅助交易员复盘训练。

## 子任务
- [ ] 日期选择器，选定后时间轴自动推进
- [ ] 动态显示当日情绪四态切换和关键指标曲线
- [ ] 支持播放速度调节（1x/2x/5x）
- [ ] 标注关键事件点（如情绪切换、涨停潮等）

## 验收标准
- 可选择任意历史日期回放当天市场情绪变化
"@

gh issue create --repo $repo `
  --title "3.4 轻量智能建议（历史相似日匹配）" `
  --label "phase-3,priority-low,enhancement" `
  --body @"
## 优先级：🔵 可选 | 预计工作量：2-3 周

## 描述
基于历史情绪序列，展示与当前情绪组合最相似的历史日期及其次日大盘表现。纯统计呈现，不构成投资建议。

## 子任务
- [ ] 实现情绪向量相似度计算
- [ ] 找出最近 N 次相似情绪日期
- [ ] 展示这些日期的次日涨跌幅分布
- [ ] 在前端情绪卡片中增加"历史参考"区块

## 验收标准
- 输出类似"过去 5 次类似情绪下，次日平均涨跌幅 +0.3%"
- 数据仅供辅助参考，明确声明不构成投资建议
"@

gh issue create --repo $repo `
  --title "3.5 用户权限与认证系统" `
  --label "phase-3,priority-low,enhancement" `
  --body @"
## 优先级：🟢 较低 | 预计工作量：2-3 周

## 描述
公网/多人共享部署场景下缺乏用户登录和权限管理，存在数据安全风险。

## 子任务
- [ ] 添加简单的 session-based 或 token-based 认证
- [ ] 支持多用户各自独立的 watchlist
- [ ] 管理员可查看所有用户
- [ ] 敏感操作（删除股票、修改策略）需要认证

## 验收标准
- 多人部署场景下各用户数据隔离
- 未认证用户无法修改数据
"@

Write-Host ""
Write-Host "✅ 所有 Issues 创建完毕！" -ForegroundColor Green
Write-Host "访问 https://github.com/$repo/issues 查看" -ForegroundColor Cyan
