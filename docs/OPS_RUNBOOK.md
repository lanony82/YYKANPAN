# YYKANPAN 运维手册 (Operations Runbook)

---

## 1. 快速启动

### 本地开发 (Windows)

```powershell
# 1. 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -e .

# 3. 准备 watchlist（首次）
copy watchlist_cn_sample.json watchlist_cn.json
# 编辑 watchlist_cn.json 添加你的股票

# 4. 启动服务
python src/server.py
# → http://localhost:5000
```

### Docker 部署

```bash
# 1. 准备 watchlist
cp watchlist_cn_sample.json watchlist_cn.json

# 2. 构建 + 启动
docker-compose up -d

# 3. 查看日志
docker logs -f yykanpan
```

---

## 2. 环境配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `TZ` | `Asia/Shanghai` | 时区（必须北京时间） |
| `HOST` | `127.0.0.1` | 绑定地址（Docker 用 `0.0.0.0`） |
| `FLASK_DEBUG` | `1` | 调试模式（生产设为 `0`） |
| `COLLECT_CRON` | `0 18 * * 1-5` | 数据采集 cron 表达式 |
| `COLLECT_ENABLED` | `1` | 设为 `0` 禁用定时采集 |
| `GUNICORN_WORKERS` | `2` | 生产 worker 数 |

---

## 3. 数据持久化

所有持久数据在 `data/` 目录：

| 文件 | 用途 | 备份建议 |
|------|------|----------|
| `data/*.csv` | 日线收盘数据 | 可再生（每日18:00自动采集） |
| `data/sentiment_history.json` | 情绪历史 | 建议备份 |
| `data/sentiment_config.json` | 情绪阈值配置 | 建议备份 |
| `data/sentiment_last_known.json` | 最近已知情绪数据 | 可再生 |
| `data/decisions.json` | 决策日志 | **重要，必须备份** |
| `data/strategies/*.yaml` | YAML策略配置 | 建议备份（可版本控制） |
| `watchlist_cn.json` | 股票列表 | **重要，必须备份** |

**Docker 卷映射:**
```yaml
volumes:
  - ./data:/app/data          # 所有数据
  - ./watchlist_cn.json:/app/watchlist_cn.json:ro  # 只读挂载
```

---

## 4. 常见问题排查

### 4.1 服务无法启动

**症状:** `python src/server.py` exit code 1

**排查步骤:**
```powershell
# 检查端口占用
netstat -ano | findstr :5000

# 检查 Python 环境
.\.venv\Scripts\python.exe -c "import flask, akshare; print('OK')"

# 检查 import 错误
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'src'); import server"
```

**常见原因:**
- 端口 5000 被占用 → 杀掉占用进程或换端口
- 缺少依赖 → `pip install -e .`
- watchlist_cn.json 不存在 → 从 sample 复制

---

### 4.2 行情数据获取失败

**症状:** 所有股票显示 "error"

**排查步骤:**
```powershell
# 测试 Sina 数据源
python -c "
import urllib.request
url = 'https://hq.sinajs.cn/list=sh600519'
req = urllib.request.Request(url, headers={'Referer':'https://finance.sina.com.cn','User-Agent':'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
print(resp.read().decode('gbk')[:100])
"

# 测试 AkShare
python -c "import akshare; df = akshare.stock_zh_a_spot_em(); print(df.head())"

# 使用内置 benchmark
curl -X POST http://localhost:5000/api/providers/test
```

**常见原因:**
- VPN/代理干扰 → 切换网络或关闭 VPN
- Sina 被限流 → 自动降级到 AkShare
- AkShare 接口变更 → 更新 akshare 包: `pip install --upgrade akshare`

**恢复措施:**
```bash
# 手动切换 provider 顺序
curl -X POST http://localhost:5000/api/providers/order \
  -H "Content-Type: application/json" \
  -d '{"order": ["akshare", "sina", "yahoo"]}'

# 或自动选最快
curl -X POST http://localhost:5000/api/providers/auto
```

---

### 4.3 情绪数据缺失

**症状:** "自动抓取不完整，缺少: limit_up_count"

**原因:** AkShare 涨停池接口在非交易时段或数据尚未更新时返回空。

**处理:**
- 交易时段内(9:30–15:00)重试 → 通常10:00后数据可用
- 非交易时段 → 系统自动使用 `sentiment_last_known.json` 中缓存的最近值
- 若 iWenCai 也失败 → 手动输入: 打开情绪卡片手动填写四个数字

---

### 4.4 新股新债无数据

**症状:** xgxz 卡片显示"暂无近期新股新债"

**排查:**
```powershell
# 直接测试 East Money API
python -c "
import urllib.request, json
url = 'https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_APP_IPOAPPLY&pageSize=5&sortColumns=APPLY_DATE&sortTypes=-1'
resp = urllib.request.urlopen(url, timeout=10)
data = json.loads(resp.read())
print(data.get('result',{}).get('count'))
"
```

**常见原因:**
- 近期无新股/新债发行 → 正常
- East Money API 变更 → 检查 reportName 是否仍有效
- 网络问题 → 检查 `datacenter-web.eastmoney.com` 可达性

---

### 4.5 Docker 容器内 cron 不执行

**排查:**
```bash
docker exec yykanpan cat /etc/cron.d/stock-collect
docker exec yykanpan crontab -l
docker exec yykanpan cat /app/logs/collect.log
```

**常见原因:**
- `COLLECT_ENABLED=0` → 检查 docker-compose.yml
- 时区不对 → `docker exec yykanpan date` 验证
- 权限问题 → cron 文件需要 0644

---

## 5. 性能调优

### 刷新频率

| 数据类型 | 默认间隔 | 可调范围 | 说明 |
|----------|----------|----------|------|
| 股票行情 | 60s | 30s–300s | 交易时段内 |
| 宏观指标 | 5min | — | 低频变化 |
| 简报/AI | 30min | — | 计算量大 |
| 新股新债 | 日缓存 | — | 数据日级别变化 |
| 八字 | 日缓存 | — | 按日计算 |

### 静默时段

15:30–08:30 (北京时间) + 周末 + 法定假日 → 零 API 调用。

修改假日列表: `static/js/app.js` 搜索 `CN_HOLIDAYS_2026`。

---

## 6. 备份与恢复

### 备份

```powershell
# 关键数据
$ts = Get-Date -Format "yyyyMMdd"
Copy-Item data/decisions.json "backup/decisions_$ts.json"
Copy-Item watchlist_cn.json "backup/watchlist_$ts.json"
Copy-Item data/sentiment_history.json "backup/sentiment_$ts.json"

# 或全量
Compress-Archive -Path data/, watchlist_cn.json -DestinationPath "backup/yykanpan_$ts.zip"
```

### 恢复

```powershell
Copy-Item backup/decisions_20260512.json data/decisions.json
Copy-Item backup/watchlist_20260512.json watchlist_cn.json
# 重启服务
```

### 通过 API 导入/导出

```bash
# 导出 watchlist
curl http://localhost:5000/api/config/export -o backup_watchlist.json

# 导入 watchlist
curl -X POST http://localhost:5000/api/config/import \
  -H "Content-Type: application/json" \
  -d @backup_watchlist.json
```

---

## 7. 日志

| 来源 | 位置 | 说明 |
|------|------|------|
| Flask dev | stdout | 开发模式直接输出 |
| Gunicorn (Docker) | stdout (access) | `docker logs yykanpan` |
| 定时采集 | `/app/logs/collect.log` | Docker 内 |
| Provider 降级 | stdout 日志 | 包含 `[provider]` 前缀 |

---

## 8. 升级流程

```powershell
# 1. 备份数据
Copy-Item data/ backup/data_$(Get-Date -f yyyyMMdd)/ -Recurse

# 2. 拉取新代码
git pull

# 3. 更新依赖
pip install -e .

# 4. 运行测试
python -m pytest tests/ --tb=short -q

# 5. 重启服务
# 本地: Ctrl+C 后重新 python src/server.py
# Docker: docker-compose up -d --build
```

---

## 9. 安全注意事项

- **仅限本地使用** — 无认证，无 CORS，不暴露到公网
- **watchlist_cn.json** 含个人持仓信息 → 已在 .gitignore
- **decisions.json** 含个人决策 → 已在 .gitignore
- **Docker**: 默认绑定 `0.0.0.0:5000`，若在公网服务器需配防火墙
- **数据源**: 所有 API 调用为只读抓取，不做交易操作
