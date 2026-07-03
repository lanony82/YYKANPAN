// ── i18n: all user-facing Chinese strings ────────────────────────────────────
// To localise, duplicate this object with translated values.
const I = {
  // Units
  unit_yi: "亿", unit_wan: "万", unit_consecutive: "连板",

  // Common labels
  lbl_updated_at: "更新时间", lbl_generated_at: "生成时间",
  lbl_date: "日期", lbl_status: "状态", lbl_none: "暂无",

  // Sentiment
  lbl_sentiment_stage: "情绪阶段", lbl_tradable: "是否适合交易",
  lbl_reasons: "理由", lbl_plain: "人话结论",
  lbl_data_note: "数据说明", lbl_last_known: "最近可用值时间",
  stage_rising: "上升", stage_ebbing: "退潮", stage_divergence: "分歧",

  // Stats bar
  lbl_total: "总数", lbl_up: "上涨", lbl_down: "下跌", lbl_flat: "平盘",

  // Limit stats
  lbl_limit_up: "涨停", lbl_limit_down: "跌停",
  lbl_consec_boards: "连板股", lbl_max_consec: "最高连板",
  lbl_yesterday_perf: "📊 昨日涨停今日表现",
  lbl_avg_change: "平均涨跌", lbl_win_rate: "胜率", lbl_verdict: "判定",

  // AI Edge
  lbl_market_bias: "市场偏向", lbl_ai_confidence: "AI 置信度",
  lbl_coverage: "样本覆盖", lbl_up_count: "上涨", lbl_down_count: "下跌",
  lbl_focus: "优先关注", lbl_risks: "风险观察", lbl_playbook: "执行清单",

  // Mainline
  lbl_mainline_sector: "当前主线板块", lbl_leader_stock: "龙头股",
  lbl_participation: "是否值得参与", lbl_analysis_time: "分析时间",
  lbl_reasoning: "判断依据", lbl_suggestion: "建议",

  // Brief
  lbl_market_regime: "市场状态", lbl_avg_pct: "均幅",
  lbl_highlights: "核心观察", lbl_actions: "行动建议",
  lbl_headlines: "头条扫描",
  fallback_no_headlines: "未获取到外部头条，已基于持仓自动分析",

  // Watchdog
  status_green: "风险已控", status_green_detail: "未触发提醒",
  status_yellow: "中等风险", status_red: "高风险预警",
  status_attn: "条告警，需要关注", status_careful: "条告警，请谨慎",
  lbl_inspect_time: "巡检时间", lbl_inspect_range: "巡检范围",
  lbl_thresholds: "阈值", lbl_daily: "单日", lbl_pnl: "浮盈亏",
  lbl_stocks_with: "只股票（其中", lbl_with_pos: "只含持仓数据）",
  lbl_triggered: "触发", lbl_alerts_suffix: "条",
  alert_daily_change: "单日波动", alert_pnl: "浮盈亏",

  // Watchdog starter preset
  preset_title: "Watchdog 测试通知",
  preset_body: "新手设置已完成：单日5%，浮盈亏10%。",
  preset_applied: "已应用新手设置：",
  preset_daily: "- 单日阈值 5%", preset_pnl: "- 浮盈亏阈值 10%",
  preset_notif: "- 浏览器提醒 已启用",
  preset_results: "下面是本次即时巡检结果：",

  // Auto-refresh status
  status_paused: "自动刷新暂停中",
  reason_closed: "休市日", reason_quiet: "15:30-08:30, UTC+8",
  status_active: "自动刷新开启中（UTC+8）",

  // Notifications
  notif_enabled: "通知已开启（点击关闭）",
  notif_disabled: "通知已关闭（点击开启）",
  notif_sentiment_change: "⚠️ Watchdog 情绪变化",
  msg_sentiment_change: "市场情绪变化：",

  // Color mode
  mode_cn: "A股配色", mode_us: "美股配色",

  // Add / Delete stock
  err_no_ticker: "请输入股票代码", btn_adding: "添加中…", btn_add: "＋ 添加",
  msg_added: "已添加", err_add_failed: "添加失败", err_network: "网络错误",
  confirm_delete: "确认删除", err_delete: "删除失败",
  prompt_shares: "持仓股数（留空清除）", prompt_cost: "成本价（留空清除）",

  // Table / Render
  empty_no_stocks: "暂无股票，请添加",
  err_load_failed: "加载失败，请确认服务正在运行",
  btn_loading: "刷新中", btn_position: "仓位", btn_delete: "删除",

  // Loading / error states
  status_collecting: "自动采集中...", status_scraping: "自动抓取中...",
  status_judging: "判断中...", status_mainline: "主线分析中...",
  status_ai: "AI 策略生成中...", status_limit: "涨跌停数据加载中...",
  err_brief_gen: "简报生成失败", err_brief_req: "简报请求失败，请稍后重试",
  err_incomplete_data: "请先填完整四项数据",
  err_judgment: "判断失败", err_request: "请求失败，请稍后重试",
  err_scrape: "自动抓取失败，请稍后重试",
  err_mainline: "主线分析失败", err_ai: "AI 策略生成失败",
  err_limit: "涨跌停数据加载失败",
  empty_history: "暂无历史数据，刷新情绪后将自动记录",
  err_chart: "图表加载失败",

  // Card names
  card_stats: "行情概览", card_ai_edge: "AI 策略引擎",
  card_watchdog: "Watchdog", card_limit: "涨跌停",
  card_sentiment: "情绪判断", card_mainline: "主线板块",
  card_brief: "智能简报", card_invest_tip: "投资锦囊",
  card_macro: "宏观风向标", card_bazi: "今日八字",
  card_xgxz: "新股新债", card_advisor: "参谋信号",
  card_risk: "黑天鹅/灰犀牛", card_decisions: "决策日志",

  // Misc
  lbl_hidden: "已隐藏：",
  cfg_saved: "阈值已保存 ✓", cfg_save_failed: "保存失败",
  lbl_update_prefix: "更新: ",
  btn_refresh: "⟳ 刷新",
  privacy_hidden: "🔒 隐藏", privacy_shown: "🔓 显示",
  notif_watchdog_alert: "Watchdog 提醒",
  lbl_score: "分值",

  // Store defaults
  store_watchdog_default: "使用步骤：\n1) 设置阈值（单日波动 / 浮盈亏）\n2) 勾选\"启用浏览器提醒\"\n3) 点击\"立即巡检\"测试",
  store_limit_default: "加载中...",
  store_mainline_default: "自动读取今日涨幅榜与成交额前排，输出主线、龙头和参与建议",
  store_ai_default: "将持仓涨跌结构转为执行清单（偏多/偏空/震荡 + 关注标的 + 风险标的）",
  store_brief_default: "系统每30分钟自动更新一次，你也可以手动刷新",
  store_sentiment_default: "输入上涨/下跌/涨停/连板数据后点击判断",
};
// ── Card Template ─────────────────────────────────────────────────────────────
// Usage:
//   const card = CardTemplate.create("my-card", "卡片标题", {
//     badge: "可选标签",            // small accent badge next to title
//     bodyHTML: "<p>内容</p>",      // innerHTML for card body
//     buttons: [                    // optional action buttons
//       { id: "btn-xxx", text: "刷新" }
//     ],
//     output: { id: "out-xxx", text: "默认提示文字" },  // .insight-out div
//     noClose: false,               // true = hide ✕ button
//     noDrag: false,                // true = hide drag handle
//   });
//   document.getElementById("insight-wrap").appendChild(card);
//
// The returned element is a standard .insight-card with data-card-id,
// drag handle, collapse & close buttons — identical to hand-written cards.
const CardTemplate = {
  create(id, title, opts = {}) {
    const el = document.createElement("div");
    el.className = "insight-card";
    el.dataset.cardId = id;
    if (!opts.noDrag) el.draggable = true;

    // -- header
    const h3 = document.createElement("h3");
    if (!opts.noDrag) {
      const handle = document.createElement("span");
      handle.className = "drag-handle";
      handle.textContent = "⠇";
      h3.appendChild(handle);
    }
    h3.appendChild(document.createTextNode(" " + title + " "));
    if (opts.badge) {
      const badge = document.createElement("span");
      badge.className = "ai-badge";
      badge.textContent = opts.badge;
      h3.appendChild(badge);
    }
    const colBtn = document.createElement("button");
    colBtn.className = "card-collapse";
    colBtn.title = "折叠/展开";
    colBtn.textContent = "−";
    h3.appendChild(colBtn);
    if (!opts.noClose) {
      const closeBtn = document.createElement("button");
      closeBtn.className = "card-close";
      closeBtn.title = "隐藏卡片";
      closeBtn.textContent = "✕";
      h3.appendChild(closeBtn);
    }
    el.appendChild(h3);

    // -- buttons
    if (opts.buttons) {
      opts.buttons.forEach(b => {
        const btn = document.createElement("button");
        btn.id = b.id;
        if (b.className) btn.className = b.className;
        btn.textContent = b.text;
        if (b.style) btn.style.cssText = b.style;
        el.appendChild(btn);
      });
    }

    // -- body
    if (opts.bodyHTML) {
      const body = document.createElement("div");
      body.innerHTML = opts.bodyHTML;
      el.appendChild(body);
    }

    // -- output
    if (opts.output) {
      const out = document.createElement("div");
      out.className = "insight-out";
      out.id = opts.output.id;
      out.textContent = opts.output.text || "";
      el.appendChild(out);
    }

    return el;
  }
};

// ── Petite-Vue global reactive store ─────────────────────────────────────────
// Phase 1: All existing vanilla JS continues to work.
// New/migrated components can read from this reactive store.
// Existing functions push data here via store.xxx = value.
const { createApp, reactive } = PetiteVue;
const store = reactive({
  // Sentiment card
  sentiment: {
    stage: "",
    tradable: "",
    score: 0,
    plain: "",
    reasons: [],
    loading: false,
    updatedAt: "",
    fallbackNote: "",
    inputs: { up: "", down: "", limitUp: "", consec: "" },
  },
  // Stats bar (shared across cards)
  stats: {
    total: 0, up: 0, down: 0, flat: 0,
    best: "—", worst: "—",
    mv: "—", pnl: "—", pnlCls: "", portfolioChg: "—", portfolioChgCls: "",
    limitUp: "—", limitDown: "—", ztProfit: "—", ztProfitCls: "",
    sentimentStage: "—", sentimentTradable: "—",
  },
  // Watchdog
  watchdog: {
    status: "green", label: I.status_green, detail: I.status_green_detail, alerts: [],
    output: I.store_watchdog_default,
  },
  // Limit-stats card
  limitStats: {
    loading: false,
    output: I.store_limit_default,
  },
  // Mainline card
  mainline: {
    loading: false,
    output: I.store_mainline_default,
  },
  // AI Edge card
  aiEdge: {
    loading: false,
    output: I.store_ai_default,
  },
  // Brief card
  brief: {
    loading: false,
    output: I.store_brief_default,
  },
});
// Expose globally so vanilla JS functions can write to it
window._store = store;

// ── Popular A-share search list ──────────────────────────────────────────────
const A_SHARES = [
  ["600519.SS","贵州茅台"],["000858.SZ","五粮液"],["601318.SS","中国平安"],
  ["600036.SS","招商银行"],["300750.SZ","宁德时代"],["000001.SZ","平安银行"],
  ["600900.SS","长江电力"],["601857.SS","中国石油"],["000002.SZ","万科A"],
  ["601166.SS","兴业银行"],["600276.SS","恒瑞医药"],["002415.SZ","海康威视"],
  ["600887.SS","伊利股份"],["601888.SS","中国中免"],["002594.SZ","比亚迪"],
  ["300760.SZ","迈瑞医疗"],["600030.SS","中信证券"],["601688.SS","华泰证券"],
  ["600031.SS","三一重工"],["000568.SZ","泸州老窖"],["600690.SS","海尔智家"],
  ["002714.SZ","牧原股份"],["601601.SS","中国太保"],["600104.SS","上汽集团"],
  ["000333.SZ","美的集团"],["601398.SS","工商银行"],["601288.SS","农业银行"],
  ["600016.SS","民生银行"],["601939.SS","建设银行"],["601988.SS","中国银行"],
  ["600028.SS","中国石化"],["601088.SS","中国神华"],["600050.SS","中国联通"],
  ["601728.SS","中国电信"],["600941.SS","中国移动"],["688981.SS","中芯国际"],
  ["002049.SZ","紫光国微"],["603986.SS","兆易创新"],["002230.SZ","科大讯飞"],
  ["300014.SZ","亿纬锂能"],["002460.SZ","赣锋锂业"],["000100.SZ","TCL科技"],
  ["601012.SS","隆基绿能"],["600438.SS","通威股份"],["002129.SZ","中环股份"],
  ["600309.SS","万华化学"],["002304.SZ","洋河股份"],["000596.SZ","古井贡酒"],
  ["600763.SS","通策医疗"],["600111.SS","北方稀土"],["601390.SS","中国中铁"],
  ["601186.SS","中国铁建"],["601800.SS","中国交建"],
  ["600977.SS","中国核电"],["601985.SS","中国核建"],["000661.SZ","长春高新"],
  ["600585.SS","海螺水泥"],["601669.SS","中国电建"],["002352.SZ","顺丰控股"],
  ["002475.SZ","立讯精密"],["300059.SZ","东方财富"],["600588.SS","用友网络"],
];

// ── State ────────────────────────────────────────────────────────────────────
let stocks = [];
let sortCol = "change_pct", sortDir = -1;  // default: biggest gainers first
let positions = {};
let privacyHidden = localStorage.getItem("privacy_hidden") === "1";
const WATCHDOG_KEY = "watchdog_config_v1";
const POSITION_KEY = "positions_v1";
const MASK = "****";

// ── Utils ────────────────────────────────────────────────────────────────────
function fmtNum(n, dec=2) {
  if (n == null || isNaN(n)) return "—";
  return Number(n).toLocaleString("zh-CN", {minimumFractionDigits:dec, maximumFractionDigits:dec});
}
function fmtVol(v) {
  if (!v) return "—";
  if (v >= 1e8) return (v/1e8).toFixed(2) + I.unit_yi;
  if (v >= 1e4) return (v/1e4).toFixed(1) + I.unit_wan;
  return v.toLocaleString();
}
function fmtMoney(v) {
  if (v == null || isNaN(v)) return "—";
  return Number(v).toLocaleString("zh-CN", {minimumFractionDigits:2, maximumFractionDigits:2});
}
function cls(v) {
  if (v > 0) return "up";
  if (v < 0) return "down";
  return "flat";
}
function progress(pct) {
  const el = document.getElementById("progress");
  el.style.width = pct + "%";
  if (pct >= 100) setTimeout(()=>{ el.style.width="0"; }, 500);
}

function getBeijingNowParts() {
  const dtf = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  const parts = {};
  for (const p of dtf.formatToParts(new Date())) {
    if (p.type !== "literal") parts[p.type] = p.value;
  }
  return {
    year: Number(parts.year),
    month: Number(parts.month),
    day: Number(parts.day),
    hour: Number(parts.hour),
    minute: Number(parts.minute),
    second: Number(parts.second),
  };
}

function beijingTimestampLabel() {
  const p = getBeijingNowParts();
  const mm = String(p.month).padStart(2, "0");
  const dd = String(p.day).padStart(2, "0");
  const hh = String(p.hour).padStart(2, "0");
  const mi = String(p.minute).padStart(2, "0");
  const ss = String(p.second).padStart(2, "0");
  return `${p.year}-${mm}-${dd} ${hh}:${mi}:${ss} UTC+8`;
}

function withUtc8Label(ts) {
  if (!ts) return "—";
  if (String(ts).includes("UTC+8")) return String(ts);
  return `${ts} UTC+8`;
}

// Chinese A-share market holidays (休市日) — weekends handled separately.
// Format: "MM-DD" for annual fixed dates, "YYYY-MM-DD" for year-specific dates.
const CN_HOLIDAYS_2026 = new Set([
  // 元旦 New Year
  "2026-01-01", "2026-01-02",
  // 春节 Spring Festival
  "2026-01-26", "2026-01-27", "2026-01-28", "2026-01-29", "2026-01-30",
  "2026-02-02", "2026-02-03", "2026-02-04", "2026-02-05", "2026-02-06",
  // 清明 Qingming
  "2026-04-04", "2026-04-05", "2026-04-06",
  // 劳动节 Labour Day
  "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05",
  // 端午 Dragon Boat
  "2026-06-19", "2026-06-20", "2026-06-21",
  // 中秋+国庆 Mid-Autumn + National Day
  "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04", "2026-10-05",
  "2026-10-06", "2026-10-07", "2026-10-08",
]);

function isChinaMarketClosed() {
  const p = getBeijingNowParts();
  // Weekend check (Saturday=6, Sunday=0)
  const dow = new Date(p.year, p.month - 1, p.day).getDay();
  if (dow === 0 || dow === 6) return true;
  // Holiday check
  const dateStr = `${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`;
  return CN_HOLIDAYS_2026.has(dateStr);
}

function isBeijingQuietHours() {
  // If today is a non-trading day (weekend or holiday), always quiet.
  if (isChinaMarketClosed()) return true;
  const p = getBeijingNowParts();
  const minutes = p.hour * 60 + p.minute;
  // Quiet window: 15:30 to next day 08:30 (Beijing time).
  return minutes >= (15 * 60 + 30) || minutes < (8 * 60 + 30);
}

function runAutoTask(task) {
  if (isBeijingQuietHours()) return;
  task();
}

function loadPositions() {
  try {
    const raw = localStorage.getItem(POSITION_KEY);
    positions = raw ? JSON.parse(raw) : {};
    if (!positions || typeof positions !== "object") positions = {};
  } catch {
    positions = {};
  }
}

function savePositions() {
  localStorage.setItem(POSITION_KEY, JSON.stringify(positions));
}

function getPosition(ticker) {
  const p = positions[ticker] || {};
  const shares = Number(p.shares);
  const cost = Number(p.cost);
  return {
    shares: Number.isFinite(shares) && shares > 0 ? shares : null,
    cost: Number.isFinite(cost) && cost > 0 ? cost : null,
  };
}

function upsertPosition(ticker, shares, cost) {
  const cleanShares = Number(shares);
  const cleanCost = Number(cost);
  if (!(Number.isFinite(cleanShares) && cleanShares > 0 && Number.isFinite(cleanCost) && cleanCost > 0)) {
    delete positions[ticker];
  } else {
    positions[ticker] = { shares: cleanShares, cost: cleanCost };
  }
  savePositions();
}

function loadWatchdogConfig() {
  try {
    const raw = localStorage.getItem(WATCHDOG_KEY);
    const cfg = raw ? JSON.parse(raw) : {};
    document.getElementById("inp-watchdog-change").value = cfg.change_threshold ?? 5;
    document.getElementById("inp-watchdog-pnl").value = cfg.pnl_threshold ?? 10;
    document.getElementById("inp-watchdog-enable").checked = cfg.enabled ?? true;
  } catch {
    document.getElementById("inp-watchdog-change").value = 5;
    document.getElementById("inp-watchdog-pnl").value = 10;
    document.getElementById("inp-watchdog-enable").checked = true;
  }
}

function getWatchdogConfig() {
  const cfg = {
    change_threshold: Math.max(0, Number(document.getElementById("inp-watchdog-change").value || 5)),
    pnl_threshold: Math.max(0, Number(document.getElementById("inp-watchdog-pnl").value || 10)),
    enabled: !!document.getElementById("inp-watchdog-enable").checked,
  };
  localStorage.setItem(WATCHDOG_KEY, JSON.stringify(cfg));
  return cfg;
}

/* ── Global notification master switch ── */
const NOTIF_KEY = "global_notif_enabled";
function isNotifEnabled() {
  return localStorage.getItem(NOTIF_KEY) !== "0";
}
function toggleNotif() {
  const next = !isNotifEnabled();
  localStorage.setItem(NOTIF_KEY, next ? "1" : "0");
  syncNotifBtn();
}
function syncNotifBtn() {
  const btn = document.getElementById("btn-notif");
  if (!btn) return;
  const on = isNotifEnabled();
  btn.textContent = on ? "🔔" : "🔕";
  btn.title = on ? I.notif_enabled : I.notif_disabled;
  btn.classList.toggle("off", !on);
}

function maybeNotifyWatchdog(title, body) {
  if (!isNotifEnabled()) return;
  if (!("Notification" in window)) return;
  if (Notification.permission === "granted") {
    new Notification(title, { body });
    return;
  }
  if (Notification.permission !== "denied") {
    Notification.requestPermission().then(p => {
      if (p === "granted") new Notification(title, { body });
    });
  }
}

function applyWatchdogStarterPreset() {
  document.getElementById("inp-watchdog-change").value = 5;
  document.getElementById("inp-watchdog-pnl").value = 10;
  document.getElementById("inp-watchdog-enable").checked = true;
  getWatchdogConfig();

  // Trigger permission flow and a test notification if supported.
  maybeNotifyWatchdog(I.preset_title, I.preset_body);

  runWatchdog();

  const out = document.getElementById("out-watchdog");
  if (out) {
    out.textContent =
`${I.preset_applied}
${I.preset_daily}
${I.preset_pnl}
${I.preset_notif}

${I.preset_results}

${out.textContent}`;
  }
}

function runWatchdog() {
  const out = document.getElementById("out-watchdog");
  const cfg = getWatchdogConfig();
  const valid = stocks.filter(s => !s.error);
  const posCount = valid.filter(s => {
    const p = getPosition(s.ticker);
    return !!(p.shares && p.cost);
  }).length;
  const alerts = [];

  for (const s of valid) {
    const c = Number(s.change_pct || 0);
    if (Math.abs(c) >= cfg.change_threshold && cfg.change_threshold > 0) {
      alerts.push(`${s.ticker} ${s.name || ""} ${I.alert_daily_change} ${c.toFixed(2)}%`);
    }

    const pos = getPosition(s.ticker);
    if (pos.shares && pos.cost && s.price != null) {
      const pnlPct = ((Number(s.price) - pos.cost) / pos.cost) * 100;
      if (Math.abs(pnlPct) >= cfg.pnl_threshold && cfg.pnl_threshold > 0) {
        alerts.push(`${s.ticker} ${s.name || ""} ${I.alert_pnl} ${pnlPct.toFixed(2)}%`);
      }
    }
  }

  // Update traffic light status
  const tlCircle = document.querySelector(".traffic-light-circle");
  const tlLabel = document.getElementById("tl-label");
  const tlDetail = document.getElementById("tl-detail");
  
  let status = "green", statusLabel = I.status_green, statusDetail = I.status_green_detail;
  if (alerts.length >= 1 && alerts.length <= 2) {
    status = "yellow";
    statusLabel = I.status_yellow;
    statusDetail = `${alerts.length} ${I.status_attn}`;
  } else if (alerts.length >= 3) {
    status = "red";
    statusLabel = I.status_red;
    statusDetail = `${alerts.length} ${I.status_careful}`;
  }

  tlCircle.className = `traffic-light-circle ${status}`;
  tlLabel.textContent = statusLabel;
  tlDetail.textContent = statusDetail;

  // Single source: write store, DOM reads from store values above
  store.watchdog.status = status;
  store.watchdog.label = statusLabel;
  store.watchdog.detail = statusDetail;
  store.watchdog.alerts = alerts;

  if (!alerts.length) {
    const watchdogText = `${I.lbl_inspect_time}: ${beijingTimestampLabel()}
${I.lbl_inspect_range}: ${valid.length} ${I.lbl_stocks_with} ${posCount} ${I.lbl_with_pos}
${I.lbl_thresholds}: ${I.lbl_daily} ${cfg.change_threshold}% / ${I.lbl_pnl} ${cfg.pnl_threshold}%
${I.lbl_status}: ${I.status_green_detail}`;
    out.textContent = watchdogText;
    store.watchdog.output = watchdogText;
    return;
  }

  const watchdogText = `${I.lbl_inspect_time}: ${beijingTimestampLabel()}
${I.lbl_inspect_range}: ${valid.length} ${I.lbl_stocks_with} ${posCount} ${I.lbl_with_pos}
${I.lbl_thresholds}: ${I.lbl_daily} ${cfg.change_threshold}% / ${I.lbl_pnl} ${cfg.pnl_threshold}%
${I.lbl_triggered} ${alerts.length} ${I.lbl_alerts_suffix}:
- ${alerts.join("\n- ")}`;
  out.textContent = watchdogText;
  store.watchdog.output = watchdogText;
  if (cfg.enabled) {
    maybeNotifyWatchdog(I.notif_watchdog_alert, alerts.slice(0, 3).join("；"));
  }
}

function applyColorMode(mode) {
  const root = document.documentElement;
  const btn = document.getElementById("btn-color-mode");
  if (mode === "us") {
    root.style.setProperty("--up", "#3fb950");
    root.style.setProperty("--down", "#f85149");
    root.style.setProperty("--badge-up-bg", "#0d2318");
    root.style.setProperty("--badge-down-bg", "#2d1116");
    btn.textContent = I.mode_us;
  } else {
    root.style.setProperty("--up", "#f85149");
    root.style.setProperty("--down", "#3fb950");
    root.style.setProperty("--badge-up-bg", "#2d1116");
    root.style.setProperty("--badge-down-bg", "#0d2318");
    btn.textContent = I.mode_cn;
    mode = "cn";
  }
  localStorage.setItem("color_mode", mode);
}

function updateAutoRefreshStatus() {
  const el = document.getElementById("auto-status");
  if (!el) return;
  const paused = isBeijingQuietHours();
  el.classList.remove("active", "paused");
  if (paused) {
    el.classList.add("paused");
    const reason = isChinaMarketClosed() ? I.reason_closed : I.reason_quiet;
    el.textContent = `${I.status_paused}（${reason}）`;
  } else {
    el.classList.add("active");
    el.textContent = I.status_active;
  }
}

// ── Fetch & render ────────────────────────────────────────────────────────────
async function loadStocks() {
  progress(20);
  const btn = document.getElementById("btn-refresh");
  btn.classList.add("spinning");
  btn.innerHTML = '<span class="spin">⟳</span> ' + I.btn_loading;

  try {
    const res = await fetch("/api/stocks");
    progress(80);
    stocks = await res.json();
    render();
    document.getElementById("last-update").textContent = I.lbl_update_prefix + beijingTimestampLabel();
    runWatchdog();
  } catch(e) {
    document.getElementById("stock-cards").innerHTML =
      `<div class="stock-cards-empty"><big>⚠️</big>${I.err_load_failed}</div>`;
  } finally {
    progress(100);
    btn.classList.remove("spinning");
    btn.innerHTML = I.btn_refresh;
  }
}

// ── Single-direction data flow: store → DOM ──────────────────────────────────
// All stats writes go to `store` first; this function flushes to DOM.
function syncStatsToDOM() {
  const s = store.stats;
  const _t = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  const _tc = (id, val, className) => {
    const el = document.getElementById(id);
    if (el) { el.textContent = val; el.className = `val ${className}`; }
  };
  _t("st-total", s.total);
  _t("st-up", s.up);
  _t("st-down", s.down);
  _t("st-flat", s.flat);
  _t("st-best", s.best);
  _t("st-worst", s.worst);
  _t("st-mv", s.mv);
  _tc("st-portfolio-chg", s.portfolioChg, s.portfolioChgCls);
  _tc("st-pnl", s.pnl, s.pnlCls);
  _t("st-limit-up", s.limitUp);
  _t("st-limit-down", s.limitDown);
  _tc("st-zt-profit", s.ztProfit, s.ztProfitCls);
  _t("st-sentiment-stage", s.sentimentStage);
  _t("st-sentiment-tradable", s.sentimentTradable);
  applyPrivacyMode();
}

function render() {
  const data = [...stocks].filter(s => !s.error);
  const errData = stocks.filter(s => s.error);

  // Sort
  data.sort((a,b) => {
    let va = a[sortCol] ?? 0, vb = b[sortCol] ?? 0;
    if (typeof va === "string") return sortDir * va.localeCompare(vb);
    return sortDir * (va - vb);
  });

  // Stats
  const ups   = data.filter(s => s.change_pct > 0).length;
  const downs = data.filter(s => s.change_pct < 0).length;
  const flat  = data.filter(s => s.change_pct === 0).length;
  const best  = data.length ? data.slice().sort((a,b)=>b.change_pct-a.change_pct)[0] : null;
  const worst = data.length ? data.slice().sort((a,b)=>a.change_pct-b.change_pct)[0] : null;
  let totalMv = 0;
  let totalPnl = 0;

  for (const s of data) {
    const p = getPosition(s.ticker);
    if (p.shares && p.cost && s.price != null) {
      const mv = p.shares * Number(s.price);
      const pnl = p.shares * (Number(s.price) - p.cost);
      totalMv += mv;
      totalPnl += pnl;
    }
  }

  // ── Write to store (single source of truth), then flush to DOM ──
  store.stats.total = stocks.length;
  store.stats.up = ups;
  store.stats.down = downs;
  store.stats.flat = flat;
  store.stats.best = best ? `${best.name} ${best.change_pct>0?"+":""}${best.change_pct}%` : "—";
  store.stats.worst = worst ? `${worst.name} ${worst.change_pct}%` : "—";
  store.stats.mv = totalMv > 0 ? fmtMoney(totalMv) : "—";

  // Portfolio weighted change%
  let wSum = 0, wDiv = 0;
  for (const s of data) {
    const p = getPosition(s.ticker);
    if (p.shares && s.price != null && s.change_pct != null) {
      const mv = p.shares * Number(s.price);
      wSum += mv * Number(s.change_pct);
      wDiv += mv;
    }
  }
  if (wDiv > 0) {
    const wChg = wSum / wDiv;
    store.stats.portfolioChg = `${wChg >= 0 ? "+" : ""}${wChg.toFixed(2)}%`;
    store.stats.portfolioChgCls = cls(wChg);
  } else {
    store.stats.portfolioChg = "—";
    store.stats.portfolioChgCls = "";
  }
  if (totalMv > 0) {
    store.stats.pnl = `${totalPnl >= 0 ? "+" : ""}${fmtMoney(totalPnl)}`;
    store.stats.pnlCls = cls(totalPnl);
  } else {
    store.stats.pnl = "—";
    store.stats.pnlCls = "";
  }

  syncStatsToDOM();

  const allRows = [...data, ...errData];
  if (!allRows.length) {
    document.getElementById("stock-cards").innerHTML =
      `<div class="stock-cards-empty"><big>📋</big>${I.empty_no_stocks}</div>`;
    return;
  }

  document.getElementById("stock-cards").innerHTML = allRows.map(s => {
    if (s.error) return `
      <div class="stock-card error-card">
        <div class="stock-card-header">
          <div class="sc-left">
            <span class="sc-ticker">${s.ticker}</span>
            <span class="sc-name">${s.name||"—"}</span>
          </div>
          <div class="sc-right">
            <button class="del-btn" onclick="removeStock('${s.ticker}')">${I.btn_delete}</button>
          </div>
        </div>
        <div class="sc-error">${s.error}</div>
      </div>`;

    const p = getPosition(s.ticker);
    const shares = p.shares;
    const cost = p.cost;
    const hasPos = shares && cost;
    const pnl = hasPos ? shares * (Number(s.price || 0) - cost) : null;
    const pnlPct = hasPos ? ((Number(s.price || 0) - cost) / cost) * 100 : null;

    const c   = cls(s.change_pct);
    const sgn = s.change_pct > 0 ? "+" : "";
    const pct = s.change_pct == null ? "—" : `${sgn}${fmtNum(s.change_pct,2)}%`;
    const chg = s.change == null    ? "—" : `${sgn}${fmtNum(s.change,2)}`;

    return `<div class="stock-card">
      <div class="stock-card-header">
        <div class="sc-left">
          <span class="sc-ticker">${s.ticker}</span>
          <span class="sc-name" title="${s.name}">${s.name||"—"}</span>
        </div>
        <div class="sc-right">
          <span class="badge ${c}">${pct}</span>
        </div>
      </div>
      <div class="stock-card-price">
        <span class="sc-price ${c}">${fmtNum(s.price,2)}</span>
        <span class="sc-change ${c}">${chg}</span>
      </div>
      <div class="stock-card-spark" id="spark-${s.ticker.replace('.','_')}"></div>
      <div class="stock-card-grid">
        <div class="sc-field"><span class="sc-label">昨收</span><span>${fmtNum(s.prev_close,2)}</span></div>
        <div class="sc-field"><span class="sc-label">成交量</span><span>${fmtVol(s.volume)}</span></div>
        <div class="sc-field"><span class="sc-label">52周高</span><span>${fmtNum(s.high52,2)}</span></div>
        <div class="sc-field"><span class="sc-label">52周低</span><span>${fmtNum(s.low52,2)}</span></div>
        <div class="sc-field priv"><span class="sc-label">持仓</span><span>${privacyHidden ? MASK : (shares ?? "—")}</span></div>
        <div class="sc-field priv"><span class="sc-label">成本</span><span>${privacyHidden ? MASK : (cost ? fmtNum(cost,2) : "—")}</span></div>
        <div class="sc-field priv"><span class="sc-label">浮盈亏</span><span class="${pnl == null ? "flat" : cls(pnl)}">${privacyHidden ? MASK : (pnl == null ? "—" : `${pnl >= 0 ? "+" : ""}${fmtMoney(pnl)}`)}</span></div>
        <div class="sc-field priv"><span class="sc-label">浮盈亏%</span><span class="${pnlPct == null ? "flat" : cls(pnlPct)}">${privacyHidden ? MASK : (pnlPct == null ? "—" : `${pnlPct >= 0 ? "+" : ""}${fmtNum(pnlPct,2)}%`)}</span></div>
      </div>
      <div class="stock-card-signals" id="sig-${s.ticker.replace('.','_')}"></div>
      <div class="stock-card-actions">
        ${s.suggest ? `<div class="stock-card-suggest">
          <span class="suggest-action suggest-${s.suggest.action}">${s.suggest.action}</span>
          <span class="suggest-tip">${s.suggest.tip}</span>
          ${s.suggest.target ? `<span class="suggest-level">目标 ${fmtNum(s.suggest.target,2)}</span>` : ""}
          ${s.suggest.stop ? `<span class="suggest-level">止损 ${fmtNum(s.suggest.stop,2)}</span>` : ""}
        </div>` : ""}
        <button class="del-btn" onclick="editPosition('${s.ticker}')">${I.btn_position}</button>
        <button class="del-btn" onclick="removeStock('${s.ticker}')">${I.btn_delete}</button>
      </div>
    </div>`;
  }).join("");

  // Load sparklines asynchronously after card render
  loadSparklines(allRows.filter(r => !r.error));
  // Load technical signals asynchronously
  loadSignals(allRows.filter(r => !r.error));
}

// ── Sparkline rendering ───────────────────────────────────────────────────────
const _sparkCache = {};
function loadSparklines(rows) {
  rows.forEach(s => {
    const cellId = `spark-${s.ticker.replace('.','_')}`;
    const cell = document.getElementById(cellId);
    if (!cell) return;

    // Use cache if fresh (< 1h)
    const cached = _sparkCache[s.ticker];
    if (cached && Date.now() - cached.ts < 3600000) {
      cell.innerHTML = renderSparkSVG(cached.closes, s.change_pct);
      return;
    }

    fetch(`/api/history/${encodeURIComponent(s.ticker)}?days=20`)
      .then(r => r.json())
      .then(d => {
        if (d.ok && d.closes && d.closes.length > 1) {
          _sparkCache[s.ticker] = { closes: d.closes, ts: Date.now() };
          cell.innerHTML = renderSparkSVG(d.closes, s.change_pct);
        } else {
          cell.textContent = "—";
        }
      })
      .catch(() => { cell.textContent = "—"; });
  });
}

function renderSparkSVG(closes, changePct) {
  const w = 80, h = 24, pad = 2;
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;
  const points = closes.map((v, i) => {
    const x = pad + (i / (closes.length - 1)) * (w - pad * 2);
    const y = pad + (1 - (v - min) / range) * (h - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  const color = (changePct || 0) >= 0 ? "var(--up)" : "var(--down)";
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="display:block">
    <polyline points="${points}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

// ── Sort (no-op: table headers removed, sorting still works internally) ──────

// ── Technical signals loading ────────────────────────────────────────────────
const _sigCache = {};
function loadSignals(rows) {
  rows.forEach(s => {
    const el = document.getElementById(`sig-${s.ticker.replace('.','_')}`);
    if (!el) return;

    const cached = _sigCache[s.ticker];
    if (cached && Date.now() - cached.ts < 300000) {
      el.innerHTML = renderSignalBadges(cached.data);
      return;
    }

    fetch(`/api/signals/${encodeURIComponent(s.ticker)}`)
      .then(r => r.json())
      .then(d => {
        if (!d.ok) { el.innerHTML = ""; return; }
        _sigCache[s.ticker] = { data: d, ts: Date.now() };
        el.innerHTML = renderSignalBadges(d);
      })
      .catch(() => {});
  });
}

function renderSignalBadges(d) {
  if (!d.signals || !d.signals.length) return "";
  const v = d.summary?.verdict;
  const vCls = v === "买入" ? "sig-buy" : v === "卖出" ? "sig-sell" : "sig-hold";
  const badges = d.signals.slice(0, 4).map(s => {
    const c = s.action === "买" ? "sig-buy" : s.action === "卖" ? "sig-sell" : "sig-hold";
    const dots = "●".repeat(s.strength);
    return `<span class="sig-tag ${c}" title="${s.detail}">${s.name} ${dots}</span>`;
  }).join("");
  const indic = d.indicators || {};
  const mini = [];
  if (indic.rsi6 != null) mini.push(`RSI ${indic.rsi6}`);
  if (indic.kdj?.k != null) mini.push(`K ${indic.kdj.k}`);
  if (indic.macd?.hist != null) mini.push(`MACD ${indic.macd.hist > 0 ? "+" : ""}${indic.macd.hist}`);
  return `<div class="sig-row">
    <span class="sig-verdict ${vCls}">${v || "观望"}</span>
    ${badges}
  </div>
  <div class="sig-mini">${mini.join(" | ")}</div>`;
}

// ── Add stock ─────────────────────────────────────────────────────────────────
document.getElementById("btn-add").addEventListener("click", addStock);
document.getElementById("inp-ticker").addEventListener("keydown", e => { if(e.key==="Enter") addStock(); });

async function addStock() {
  const ticker = document.getElementById("inp-ticker").value.trim().toUpperCase();
  const name   = document.getElementById("inp-name").value.trim();
  const shares = document.getElementById("inp-shares").value.trim();
  const cost   = document.getElementById("inp-cost").value.trim();
  const msg    = document.getElementById("add-msg");

  if (!ticker) { showMsg(I.err_no_ticker, "err"); return; }

  msg.style.display = "none";
  const btn = document.getElementById("btn-add");
  btn.disabled = true; btn.textContent = I.btn_adding;

  try {
    const res  = await fetch("/api/stocks", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ticker, name})
    });
    const data = await res.json();
    if (data.ok) {
      stocks.push(data.stock);
      upsertPosition(ticker, shares, cost);
      render();
      document.getElementById("inp-ticker").value = "";
      document.getElementById("inp-name").value   = "";
      document.getElementById("inp-shares").value = "";
      document.getElementById("inp-cost").value   = "";
      document.getElementById("inp-search").value = "";
      showMsg(`✓ ${data.stock.name || ticker} ${I.msg_added}`, "ok");
    } else {
      showMsg(data.msg || I.err_add_failed, "err");
    }
  } catch(e) {
    showMsg(I.err_network, "err");
  } finally {
    btn.disabled = false; btn.textContent = I.btn_add;
  }
}

async function removeStock(ticker) {
  if (!confirm(`${I.confirm_delete} ${ticker}？`)) return;
  try {
    await fetch(`/api/stocks/${ticker}`, {method:"DELETE"});
    stocks = stocks.filter(s => s.ticker !== ticker);
    delete positions[ticker];
    savePositions();
    render();
  } catch(e) { alert(I.err_delete); }
}

function editPosition(ticker) {
  const current = getPosition(ticker);
  const sharesInput = prompt(`${ticker} ${I.prompt_shares}`, current.shares ?? "");
  if (sharesInput === null) return;
  const costInput = prompt(`${ticker} ${I.prompt_cost}`, current.cost ?? "");
  if (costInput === null) return;
  upsertPosition(ticker, sharesInput, costInput);
  render();
}

function showMsg(text, type) {
  const el = document.getElementById("add-msg");
  el.textContent = text;
  el.className = type;
  el.style.display = "inline-block";
  setTimeout(() => { el.style.display = "none"; }, 4000);
}

// ── Search / Suggest ──────────────────────────────────────────────────────────
const inp      = document.getElementById("inp-search");
const suggBox  = document.getElementById("suggestions");

inp.addEventListener("input", () => {
  const q = inp.value.trim().toLowerCase();
  if (!q) { suggBox.classList.remove("open"); return; }
  const hits = A_SHARES.filter(([code, name]) =>
    code.toLowerCase().includes(q) || name.includes(q)
  ).slice(0, 12);

  if (!hits.length) { suggBox.classList.remove("open"); return; }
  suggBox.innerHTML = hits.map(([code, name]) =>
    `<div class="sug-item" data-code="${code}" data-name="${name}">
      <span class="sug-code">${code}</span>
      <span class="sug-name">${name}</span>
    </div>`).join("");
  suggBox.classList.add("open");
});

suggBox.addEventListener("click", e => {
  const item = e.target.closest(".sug-item");
  if (!item) return;
  document.getElementById("inp-ticker").value = item.dataset.code;
  document.getElementById("inp-name").value   = item.dataset.name;
  inp.value = item.dataset.name + "  " + item.dataset.code;
  suggBox.classList.remove("open");
});

document.addEventListener("click", e => {
  if (!e.target.closest(".suggest-wrap")) suggBox.classList.remove("open");
});

// ── Refresh button (refreshes ALL cards, not just stocks) ─────────────────────
let _refreshing = false;
function refreshAllCards() {
  if (_refreshing) return;          // re-entrance guard
  _refreshing = true;
  loadStocks()
    .then(() => {
      generateAutoBrief(false);
      refreshMarketSentimentAuto();
      loadSentimentChart();
      refreshMainlineAuto();
      refreshAiEdge(false);
      refreshLimitStats();
    })
    .catch(() => {
      // loadStocks failed — still refresh the insight cards independently
      generateAutoBrief(false);
      refreshMarketSentimentAuto();
      loadSentimentChart();
      refreshMainlineAuto();
      refreshAiEdge(false);
      refreshLimitStats();
    })
    .finally(() => { _refreshing = false; });
  loadMacro();
  loadBazi();
  updateAutoRefreshStatus();
}
document.getElementById("btn-refresh").addEventListener("click", refreshAllCards);
document.getElementById("btn-watchdog-guide").addEventListener("click", applyWatchdogStarterPreset);
document.getElementById("btn-watchdog-check").addEventListener("click", runWatchdog);
document.getElementById("inp-watchdog-change").addEventListener("change", getWatchdogConfig);
document.getElementById("inp-watchdog-pnl").addEventListener("change", getWatchdogConfig);
document.getElementById("inp-watchdog-enable").addEventListener("change", getWatchdogConfig);
document.getElementById("btn-notif").addEventListener("click", toggleNotif);
syncNotifBtn();
document.getElementById("btn-privacy").addEventListener("click", () => {
  privacyHidden = !privacyHidden;
  localStorage.setItem("privacy_hidden", privacyHidden ? "1" : "0");
  applyPrivacyMode();
  render();
});

function applyPrivacyMode() {
  const btn = document.getElementById("btn-privacy");
  btn.textContent = privacyHidden ? I.privacy_hidden : I.privacy_shown;
  const ids = ["st-mv", "st-pnl", "st-portfolio-chg"];
  for (const id of ids) {
    const el = document.getElementById(id);
    if (!el) continue;
    if (privacyHidden) {
      if (!el.dataset.real) el.dataset.real = el.textContent;
      el.textContent = MASK;
      el.classList.add("privacy-mask");
    } else {
      if (el.dataset.real) el.textContent = el.dataset.real;
      el.classList.remove("privacy-mask");
    }
  }
}

document.getElementById("btn-color-mode").addEventListener("click", () => {
  const mode = localStorage.getItem("color_mode") === "cn" ? "us" : "cn";
  applyColorMode(mode);
  render();
});

// ── Investment Tips (投资锦囊) ─────────────────────────────────────────────────
const INVEST_TIPS = [
  { text: "止损不犹豫，止盈不贪婪。", source: "交易纪律" },
  { text: "不要把鸡蛋放在一个篮子里——分散投资降低风险。", source: "投资格言" },
  { text: "买入靠信心，持有靠耐心，卖出靠决心。", source: "交易心法" },
  { text: "市场短期是投票器，长期是称重机。", source: "本杰明·格雷厄姆" },
  { text: "别人恐惧时我贪婪，别人贪婪时我恐惧。", source: "沃伦·巴菲特" },
  { text: "永远不要用你输不起的钱去投资。", source: "投资铁律" },
  { text: "趋势是你的朋友，直到它结束。", source: "技术分析" },
  { text: "量价齐升看多，量价背离小心。", source: "量价关系" },
  { text: "利好出尽是利空，利空出尽是利好。", source: "A股谚语" },
  { text: "牛市不言顶，熊市不言底。", source: "市场规律" },
  { text: "会买的是徒弟，会卖的是师傅，会空仓的是祖师爷。", source: "A股老话" },
  { text: "不懂的股票不要买，看不懂的行情不要做。", source: "风险控制" },
  { text: "追涨杀跌是散户亏钱的主要原因。", source: "交易反思" },
  { text: "成交量是股票的元气，量在价先。", source: "量价理论" },
  { text: "投资最重要的事：不要亏钱；第二重要的事：记住第一条。", source: "沃伦·巴菲特" },
  { text: "计划你的交易，交易你的计划。", source: "交易纪律" },
  { text: "均线多头排列看多，空头排列看空。", source: "均线理论" },
  { text: "底部放量是启动信号，顶部放量是出货信号。", source: "量价分析" },
  { text: "大盘好时选强势股，大盘差时空仓观望。", source: "仓位管理" },
  { text: "做投资要像经营企业一样，关注 ROE、现金流和护城河。", source: "价值投资" },
  { text: "短线看量能和情绪，中线看趋势和板块，长线看业绩和估值。", source: "操作框架" },
  { text: "永远保留一部分现金，机会来了才能上车。", source: "仓位管理" },
  { text: "不要频繁交易，手续费和滑点会吞噬利润。", source: "交易成本" },
  { text: "MACD金叉买入，死叉卖出——但要结合大趋势判断。", source: "MACD 指标" },
  { text: "3000点以下多一份勇敢，5000点以上多一份谨慎。", source: "A股经验" },
  { text: "连续涨停板不追，连续跌停板不抄。", source: "风险控制" },
  { text: "研究公司基本面比猜明天涨跌更有价值。", source: "价值投资" },
  { text: "情绪冰点往往是最好的布局时机。", source: "情绪周期" },
  { text: "政策底 → 市场底 → 经济底，依次出现。", source: "A股规律" },
  { text: "复利是世界第八大奇迹——长期持有好公司。", source: "阿尔伯特·爱因斯坦" },
  { text: "板块轮动是A股的常态，跟着资金走。", source: "板块轮动" },
  { text: "KDJ 超买不一定跌，超卖不一定涨——趋势中指标会钝化。", source: "KDJ 指标" },
  { text: "风险管理 > 收益追求。先想能亏多少，再想能赚多少。", source: "风险优先" },
  { text: "市场永远是对的，错的只有自己。", source: "杰西·利弗莫尔" },
  { text: "一根大阳线改变信仰，但别被情绪带着走。", source: "A股现象" },
  { text: "新手看价格，老手看成交量，高手看资金流向。", source: "看盘进阶" },
  { text: "每次交易前问自己：如果反向走了怎么办？", source: "交易计划" },
  { text: "周线定方向，日线找买点。", source: "多周期分析" },
  { text: "高股息策略在震荡市和熊市中表现更优。", source: "红利策略" },
  { text: "投资是认知的变现，亏损是认知的罚单。", source: "投资哲学" },
];
let _tipShown = -1;
function showRandomTip() {
  const tips = INVEST_TIPS;
  let idx;
  do { idx = Math.floor(Math.random() * tips.length); } while (idx === _tipShown && tips.length > 1);
  _tipShown = idx;
  const t = tips[idx];
  document.getElementById("tip-text").textContent = `"${t.text}"`;
  document.getElementById("tip-source").textContent = `—— ${t.source}`;
}
document.getElementById("btn-lucky-tip").addEventListener("click", showRandomTip);
showRandomTip();

// ── Stock section collapse ────────────────────────────────────────────────────
(function() {
  const KEY = "stocks_collapsed";
  const section = document.querySelector(".stock-section");
  const btn = document.getElementById("btn-stocks-collapse");
  const toggleBtn = document.getElementById("btn-toggle-stocks");
  if (!section || !btn) return;

  function sync(collapsed) {
    btn.textContent = collapsed ? "+" : "−";
    localStorage.setItem(KEY, collapsed ? "1" : "0");
  }

  function toggle() {
    const collapsed = section.classList.toggle("collapsed");
    sync(collapsed);
  }

  btn.addEventListener("click", toggle);
  if (toggleBtn) toggleBtn.addEventListener("click", () => {
    section.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  if (localStorage.getItem(KEY) === "1") {
    section.classList.add("collapsed");
    sync(true);
  }
})();

// ── Macro indicators (宏观风向标) ─────────────────────────────────────────────

const _macroSparkCache = {};
let _macroDays = 20;
let _lastMacroData = [];

async function loadMacro() {
  const bar = document.getElementById("macro-bar");
  if (!bar) return;
  try {
    const res = await fetch("/api/macro");
    const data = await res.json();
    if (!data.length) { bar.innerHTML = '<span class="macro-loading">暂无数据</span>'; return; }
    _lastMacroData = data;
    renderMacroChips(data);
    loadMacroSparklines(data, _macroDays);
  } catch (_) {
    bar.innerHTML = '<span class="macro-loading">获取失败</span>';
  }
}

function renderMacroChips(data) {
  const bar = document.getElementById("macro-bar");
  if (!bar) return;
  bar.innerHTML = data.map(d => {
    // Special chips: 两市成交额 and 北向资金 show amount only
    // [claude code] Special chips 契约：只读 d.price（金额本身），
    // 不读 change/change_pct——后端那两个字段对 special chip 永远是 0。
    // 颜色由 price 正负决定。普通 chip（指数/外汇/商品）走下面分支，读 change_pct。
    if (d.symbol === "vol_total") {
      const val = d.price >= 10000 ? (d.price / 10000).toFixed(2) + "万亿" : d.price + "亿";
      return `<div class="macro-chip macro-chip-vol">
        <span class="macro-name">${d.name}</span>
        <span class="macro-price">${val}</span>
      </div>`;
    }
    if (d.symbol === "northbound") {
      // [claude code] 颜色判断基于 price：北向净流入正/负 = 红/绿/灰。
      // 真正的 0 净流入很罕见，灰色对它来说就是正确显示。
      const dir = d.price > 0 ? "up" : d.price < 0 ? "down" : "flat";
      const sign = d.price > 0 ? "+" : "";
      return `<div class="macro-chip macro-chip-nb">
        <span class="macro-name">${d.name}${d.date ? '<span class="macro-date">' + d.date.slice(5) + '</span>' : ''}</span>
        <span class="macro-price ${dir}">${sign}${d.price}${d.unit || ""}</span>
      </div>`;
    }
    const dir = d.change_pct > 0 ? "up" : d.change_pct < 0 ? "down" : "flat";
    const arrow = d.change_pct > 0 ? "▲" : d.change_pct < 0 ? "▼" : "—";
    const sign = d.change > 0 ? "+" : "";
    const sparkId = `macro-spark-${d.symbol.replace(/[^a-zA-Z0-9]/g, "_")}`;
    return `<div class="macro-chip">
      <span class="macro-name">${d.name}</span>
      <span class="macro-price">${d.price}<span class="macro-unit">${d.unit || ""}</span></span>
      <span class="macro-change ${dir}">${arrow} ${sign}${d.change} (${sign}${d.change_pct}%)</span>
      <span class="macro-spark" id="${sparkId}"></span>
    </div>`;
  }).join("");
}

function loadMacroSparklines(indicators, days) {
  indicators.forEach(d => {
    if (d.no_sparkline) return;
    const sparkId = `macro-spark-${d.symbol.replace(/[^a-zA-Z0-9]/g, "_")}`;
    const el = document.getElementById(sparkId);
    if (!el) return;

    const cacheKey = `${d.symbol}_${days}`;
    const cached = _macroSparkCache[cacheKey];
    if (cached && Date.now() - cached.ts < 3600000) {
      el.innerHTML = renderMacroSparkSVG(cached.closes, d.change_pct);
      return;
    }

    el.innerHTML = '<span style="color:var(--muted);font-size:.7rem">…</span>';
    fetch(`/api/macro-history/${encodeURIComponent(d.symbol)}?days=${days}`)
      .then(r => r.json())
      .then(res => {
        if (res.ok && res.closes && res.closes.length > 1) {
          _macroSparkCache[cacheKey] = { closes: res.closes, ts: Date.now() };
          el.innerHTML = renderMacroSparkSVG(res.closes, d.change_pct);
        } else {
          el.textContent = "";
        }
      })
      .catch(() => { el.textContent = ""; });
  });
}

function renderMacroSparkSVG(closes, changePct) {
  const w = 120, h = 28, pad = 2;
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;
  const points = closes.map((v, i) => {
    const x = pad + (i / (closes.length - 1)) * (w - pad * 2);
    const y = pad + (1 - (v - min) / range) * (h - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  const color = (changePct || 0) >= 0 ? "var(--up)" : "var(--down)";
  const lastX = (pad + (w - pad * 2)).toFixed(1);
  const firstX = pad.toFixed(1);
  const fillPoints = `${firstX},${h} ${points} ${lastX},${h}`;
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="display:block;margin-top:4px">
    <polygon points="${fillPoints}" fill="${color}" opacity="0.10"/>
    <polyline points="${points}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

// Period tab click handler
document.getElementById("macro-period-tabs")?.addEventListener("click", e => {
  const btn = e.target.closest(".macro-period-btn");
  if (!btn) return;
  document.querySelectorAll(".macro-period-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  _macroDays = parseInt(btn.dataset.days, 10);
  if (_lastMacroData.length) {
    loadMacroSparklines(_lastMacroData, _macroDays);
  }
});

loadMacro();

// ── Risk events (黑天鹅/灰犀牛) ───────────────────────────────────────────────

async function loadRiskEvents() {
  const list = document.getElementById("risk-events-list");
  const countEl = document.getElementById("risk-count");
  if (!list) return;
  const period = document.getElementById("sel-risk-period")?.value || "today";
  list.innerHTML = '<div class="risk-empty">扫描中…</div>';
  try {
    const res = await fetch(`/api/risk-events?period=${period}`);
    const d = await res.json();
    if (!d.ok) { list.innerHTML = '<div class="risk-empty">获取失败</div>'; return; }
    if (countEl) countEl.textContent = `${d.count} 条`;
    if (!d.events.length) {
      list.innerHTML = '<div class="risk-safe">✅ 当前无异常事件，市场平稳</div>';
      return;
    }
    const _dir = { bullish: "利好 ↑", bearish: "利空 ↓", ambiguous: "方向不明" };
    list.innerHTML = d.events.map(e => {
      const dirTag = e.direction ? `<span class="risk-dir dir-${e.direction}">${_dir[e.direction] || ""}</span>` : "";
      const sectorTag = e.affected_sectors?.length ? `<div class="risk-sectors">📌 ${e.affected_sectors.join(" / ")}</div>` : "";
      const srcLabel = e.auto_detected ? "🤖 自动" : (e.source === "manual" ? "✍️ 手动" : "");
      const srcTag = srcLabel ? `<span class="risk-src">${srcLabel}</span>` : "";
      const manualCls = e.auto_detected === false ? " manual-event" : (e.auto_detected ? " auto-event" : "");
      return `
      <div class="risk-event severity-${e.severity}${manualCls}">
        <span class="risk-badge type-${e.type}">${e.type}</span>
        <div class="risk-body">
          <div class="risk-title">${e.title}${dirTag}${srcTag}</div>
          <div class="risk-detail">${e.detail}</div>
          ${sectorTag}
        </div>
        <span class="risk-time">${e.time}</span>
      </div>
    `;
    }).join("");
  } catch (_) {
    list.innerHTML = '<div class="risk-empty">获取失败</div>';
  }
}
document.getElementById("btn-risk-refresh")?.addEventListener("click", loadRiskEvents);
document.getElementById("sel-risk-period")?.addEventListener("change", loadRiskEvents);
loadRiskEvents();

// Manual risk event input
document.getElementById("btn-risk-add")?.addEventListener("click", async () => {
  const msg = document.getElementById("risk-add-msg");
  const title = document.getElementById("risk-inp-title")?.value?.trim();
  if (!title) { if (msg) msg.textContent = "请输入标题"; return; }
  const payload = {
    title,
    type: document.getElementById("risk-inp-type")?.value || "灰犀牛",
    severity: document.getElementById("risk-inp-severity")?.value || "medium",
    direction: document.getElementById("risk-inp-direction")?.value || "ambiguous",
    source: document.getElementById("risk-inp-source")?.value || "geopolitical",
    duration: document.getElementById("risk-inp-duration")?.value || "short",
    detail: document.getElementById("risk-inp-detail")?.value?.trim() || "",
    affected_sectors: document.getElementById("risk-inp-sectors")?.value?.trim() || "",
  };
  try {
    const res = await fetch("/api/risk-events", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const d = await res.json();
    if (!d.ok) { if (msg) msg.textContent = d.msg || "录入失败"; return; }
    if (msg) msg.textContent = "✅ 已录入";
    document.getElementById("risk-inp-title").value = "";
    document.getElementById("risk-inp-detail").value = "";
    document.getElementById("risk-inp-sectors").value = "";
    loadRiskEvents();
    setTimeout(() => { if (msg) msg.textContent = ""; }, 2000);
  } catch (_) {
    if (msg) msg.textContent = "请求失败";
  }
});

// ── Stock Screener (选股雷达) ────────────────────────────────────────────────

(async function initScreener() {
  const sel = document.getElementById("sel-screener-strategy");
  if (!sel) return;
  try {
    const res = await fetch("/api/screener/strategies");
    const d = await res.json();
    if (d.ok && d.strategies) {
      sel.innerHTML = d.strategies.map(s =>
        `<option value="${s.key}">${s.icon} ${s.name} — ${s.desc}</option>`
      ).join("");
    }
  } catch (_) {
    sel.innerHTML = '<option value="golden_cross">✦ 均线金叉</option>';
  }
})();

async function loadScreener() {
  const sel = document.getElementById("sel-screener-strategy");
  const box = document.getElementById("screener-results");
  const status = document.getElementById("screener-status");
  if (!sel || !box) return;
  const strategy = sel.value;
  if (status) status.textContent = "扫描中…";
  box.innerHTML = '<div class="screener-empty">正在扫描，沪深300需要约10~30秒…</div>';

  try {
    const res = await fetch("/api/screener?strategy=" + encodeURIComponent(strategy));
    const d = await res.json();
    if (!d.ok) {
      box.innerHTML = `<div class="screener-empty">⚠️ ${d.msg || "扫描失败"}</div>`;
      if (status) status.textContent = "";
      return;
    }
    if (status) status.textContent = `${d.scanned} · ${d.hits.length}只命中 · ${d.ts}`;
    if (!d.hits.length) {
      box.innerHTML = '<div class="screener-empty">未找到符合条件的股票</div>';
      return;
    }
    let html = '<table class="screener-table"><thead><tr>'
      + '<th>代码</th><th>名称</th><th>现价</th><th>涨跌%</th><th>分数</th><th>命中原因</th>'
      + '</tr></thead><tbody>';
    d.hits.forEach(h => {
      const cls = h.change_pct > 0 ? "up" : h.change_pct < 0 ? "down" : "";
      const pctStr = (h.change_pct > 0 ? "+" : "") + h.change_pct.toFixed(2) + "%";
      const scoreBar = `<span class="screener-score" style="--sw:${h.score}%">${h.score}</span>`;
      const reasons = h.reasons.map(r => `<span class="screener-reason">${r}</span>`).join(" ");
      html += `<tr>
        <td class="mono">${h.code}</td>
        <td>${h.name}</td>
        <td class="mono right">${h.price.toFixed(2)}</td>
        <td class="mono right ${cls}">${pctStr}</td>
        <td>${scoreBar}</td>
        <td class="screener-reasons">${reasons}</td>
      </tr>`;
    });
    html += '</tbody></table>';
    box.innerHTML = html;
  } catch (_) {
    box.innerHTML = '<div class="screener-empty">网络错误</div>';
    if (status) status.textContent = "";
  }
}

document.getElementById("btn-screener-run")?.addEventListener("click", loadScreener);

// ── Provider test panel ───────────────────────────────────────────────────────

document.getElementById("btn-test-provider")?.addEventListener("click", () => {
  const panel = document.getElementById("provider-panel");
  panel.style.display = panel.style.display === "none" ? "block" : "none";
  // Load current order
  fetch("/api/providers/order").then(r=>r.json()).then(d => {
    const lbl = document.getElementById("provider-order-label");
    if (lbl) lbl.textContent = "当前: " + (d.order||[]).join(" → ");
  }).catch(()=>{});
});
document.getElementById("btn-close-provider")?.addEventListener("click", () => {
  document.getElementById("provider-panel").style.display = "none";
});
document.getElementById("btn-auto-provider")?.addEventListener("click", async () => {
  const box = document.getElementById("provider-results");
  box.innerHTML = '<p class="provider-hint">测试中…请稍候</p>';
  try {
    const res = await fetch("/api/providers/auto", {method:"POST"});
    const d = await res.json();
    let html = '<table><tr><th>数据源</th><th>状态</th><th>耗时</th><th>价格</th></tr>';
    (d.results||[]).forEach(r => {
      const cls = r.ok ? "prov-ok" : "prov-fail";
      const best = r.provider === d.order?.[0] ? " prov-best" : "";
      html += `<tr class="${best}"><td>${r.provider}</td><td class="${cls}">${r.ok?"✓":"✗"}</td><td>${r.time_s}s</td><td>${r.price ?? "—"}</td></tr>`;
    });
    html += '</table>';
    box.innerHTML = html;
    const lbl = document.getElementById("provider-order-label");
    if (lbl) lbl.textContent = "当前: " + (d.order||[]).join(" → ");
  } catch (e) {
    box.innerHTML = '<p class="provider-hint">测试失败</p>';
  }
});

// ── Bazi card (八字) ──────────────────────────────────────────────────────────

async function loadBazi() {
  try {
    const res = await fetch("/api/bazi");
    const d = await res.json();
    if (!d.ok) return;
    const el = (id) => document.getElementById(id);
    el("bazi-solar").textContent = `📅 ${d.solar}`;
    el("bazi-lunar").textContent = `📖 ${d.lunar}`;
    el("bazi-terms").textContent = d.terms ? `🌾 ${d.terms}` : "";
    const wrap = el("bazi-pillars");
    wrap.innerHTML = d.pillars.map(p =>
      `<div class="bazi-pillar"><div class="pillar-label">${p.label}</div><div class="pillar-value">${p.value}</div></div>`
    ).join("");
    el("bazi-nayin").textContent = `纳音：${d.nayin}`;
    // 五运六气 (Five Movements & Six Qi)
    const w = d.wuyun;
    if (w) {
      el("bazi-wuyun").innerHTML = `
        <div class="wuyun-title">☯ 五运六气</div>
        <div class="wuyun-chips">
          <span class="wuyun-chip">岁运 <b>${w.sui_yun}</b></span>
          <span class="wuyun-chip">司天 <b>${w.sitian}</b></span>
          <span class="wuyun-chip">在泉 <b>${w.zaiquan}</b></span>
        </div>
        <div class="wuyun-chips">
          <span class="wuyun-chip active">${w.period_name}</span>
          <span class="wuyun-chip">主气 <b>${w.host_qi}</b></span>
          <span class="wuyun-chip">客气 <b>${w.guest_qi}</b></span>
        </div>
        <div class="wuyun-comment">${w.comment}</div>
        ${w.health_tip ? `<div class="wuyun-tip tip-health">${w.health_tip}</div>` : ''}
        ${w.trading_tip ? `<div class="wuyun-tip tip-trading">${w.trading_tip}</div>` : ''}
      `;
    }
  } catch (_) {}
}
loadBazi();

// ── Insight tools ─────────────────────────────────────────────────────────────

async function generateAutoBrief(forceRefresh=false) {
  const out = document.getElementById("out-auto-brief");
  if (!out) return;

  out.textContent = I.status_collecting;
  store.brief.loading = true;
  try {
    const suffix = forceRefresh ? "?refresh=1" : "";
    const res = await fetch(`/api/auto-brief${suffix}`);
    const data = await res.json();
    if (!data.ok) {
      out.textContent = data.msg || I.err_brief_gen;
      store.brief.output = data.msg || I.err_brief_gen;
      return;
    }

    const highlights = (data.highlights || []).map(s => `- ${s}`).join("\n");
    const actions = (data.actions || []).map(s => `- ${s}`).join("\n");
    const headlines = (data.headline_analysis || [])
      .map(h => `- ${h.title}（${h.impact}）`)
      .join("\n");

    const text =
  `${I.lbl_generated_at}: ${withUtc8Label(data.generated_at)}
${I.lbl_market_regime}: ${data.snapshot?.regime || "—"}（${I.lbl_avg_pct} ${data.snapshot?.avg_change_pct ?? "—"}%）

${I.lbl_highlights}:
${highlights || `- ${I.lbl_none}`}

${I.lbl_actions}:
${actions || `- ${I.lbl_none}`}

${I.lbl_headlines}:
${headlines || `- ${I.fallback_no_headlines}`}`;
    out.textContent = text;
    store.brief.output = text;
  } catch (e) {
    out.textContent = I.err_brief_req;
    store.brief.output = I.err_brief_req;
  } finally {
    store.brief.loading = false;
  }
}

const autoBriefBtn = document.getElementById("btn-auto-brief");
if (autoBriefBtn) {
  autoBriefBtn.addEventListener("click", () => generateAutoBrief(true));
}

const marketSentimentBtn = document.getElementById("btn-market-sentiment");
if (marketSentimentBtn) {
  marketSentimentBtn.addEventListener("click", async () => {
    const out = document.getElementById("out-market-sentiment");
    const up_count = document.getElementById("inp-up-count").value;
    const down_count = document.getElementById("inp-down-count").value;
    const limit_up_count = document.getElementById("inp-limit-up-count").value;
    const consecutive_limit_count = document.getElementById("inp-consecutive-limit-count").value;

    if ([up_count, down_count, limit_up_count, consecutive_limit_count].some(v => v === "")) {
      out.textContent = I.err_incomplete_data;
      return;
    }

    out.textContent = I.status_judging;
    store.sentiment.loading = true;
    try {
      const res = await fetch("/api/market-sentiment", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
          up_count,
          down_count,
          limit_up_count,
          consecutive_limit_count,
        })
      });
      const data = await res.json();
      if (!data.ok) {
        out.textContent = data.msg || I.err_judgment;
        store.sentiment.loading = false;
        return;
      }

      const reasons = (data.reasons || []).map(s => `- ${s}`).join("\n");
      out.textContent =
`${I.lbl_sentiment_stage}: ${data.stage}
${I.lbl_tradable}: ${data.tradable_text}

${I.lbl_reasons}:
${reasons || `- ${I.lbl_none}`}

${I.lbl_plain}:
${data.plain}`;

      // Sync to reactive store → DOM
      store.sentiment.stage = data.stage || "";
      store.sentiment.tradable = data.tradable_text || "";
      store.sentiment.score = data.score ?? 0;
      store.sentiment.plain = data.plain || "";
      store.sentiment.reasons = data.reasons || [];
      store.sentiment.updatedAt = beijingTimestampLabel();
      store.stats.sentimentStage = data.stage || "—";
      store.stats.sentimentTradable = data.tradable_text || "—";
      syncStatsToDOM();
    } catch (e) {
      out.textContent = I.err_request;
    } finally {
      store.sentiment.loading = false;
    }
  });
}

function renderMarketSentiment(data, outEl) {
  if (!outEl) return;
  if (!data.ok) {
    outEl.textContent = data.msg || I.err_judgment;
    store.sentiment.stage = ""; store.sentiment.tradable = "";
    store.stats.sentimentStage = "—"; store.stats.sentimentTradable = "—";
    syncStatsToDOM();
    return;
  }

  const reasons = (data.reasons || []).map(s => `- ${s}`).join("\n");
  const fallbackNote = data.fallback_note ? `\n\n${I.lbl_data_note}:\n- ${data.fallback_note}` : "";
  const updatedAt = data.last_known_updated_at
    ? `\n${I.lbl_last_known}: ${withUtc8Label(data.last_known_updated_at)}`
    : "";
  outEl.textContent =
`${I.lbl_updated_at}: ${beijingTimestampLabel()}
${I.lbl_sentiment_stage}: ${data.stage}
${I.lbl_tradable}: ${data.tradable_text}

${I.lbl_reasons}:
${reasons || `- ${I.lbl_none}`}

${I.lbl_plain}:
${data.plain}${fallbackNote}${updatedAt}`;

  // ── Write store → flush to DOM ──
  store.sentiment.stage = data.stage || "";
  store.sentiment.tradable = data.tradable_text || "";
  store.sentiment.score = data.score ?? 0;
  store.sentiment.plain = data.plain || "";
  store.sentiment.reasons = data.reasons || [];
  store.sentiment.updatedAt = beijingTimestampLabel();
  store.sentiment.fallbackNote = data.fallback_note || "";
  store.stats.sentimentStage = data.stage || "—";
  store.stats.sentimentTradable = data.tradable_text || "—";
  syncStatsToDOM();
}

async function refreshMarketSentimentAuto() {
  const out = document.getElementById("out-market-sentiment");
  if (!out) return;
  out.textContent = I.status_scraping;
  store.sentiment.loading = true;
  try {
    const res = await fetch("/api/market-sentiment-auto");
    const data = await res.json();
    renderMarketSentiment(data, out);
    store.sentiment.loading = false;

    if (data?.inputs?.up_count != null) document.getElementById("inp-up-count").value = data.inputs.up_count;
    if (data?.inputs?.down_count != null) document.getElementById("inp-down-count").value = data.inputs.down_count;
    if (data?.inputs?.limit_up_count != null) document.getElementById("inp-limit-up-count").value = data.inputs.limit_up_count;
    if (data?.inputs?.consecutive_limit_count != null) document.getElementById("inp-consecutive-limit-count").value = data.inputs.consecutive_limit_count;

    // Detect sentiment stage change → Watchdog alert
    const newStage = data.stage;
    if (newStage) {
      const prevStage = localStorage.getItem("last_sentiment_stage");
      if (prevStage && prevStage !== newStage) {
        const msg = `${I.msg_sentiment_change}${prevStage} → ${newStage}`;
        maybeNotifyWatchdog(I.notif_sentiment_change, msg);
        const tlDetail = document.getElementById("tl-detail");
        if (tlDetail) tlDetail.textContent = msg;
      }
      localStorage.setItem("last_sentiment_stage", newStage);
    }
  } catch (e) {
    out.textContent = I.err_scrape;
    store.sentiment.loading = false;
  }
  // Refresh sentiment chart after each update
  loadSentimentChart();
}

// ── Sentiment trend chart ─────────────────────────────────────────────────────
async function loadSentimentChart() {
  const container = document.getElementById("sentiment-chart");
  if (!container) return;
  try {
    const res = await fetch("/api/sentiment-history?days=14");
    const data = await res.json();
    if (!data.ok || !data.history.length) {
      container.innerHTML = `<span style="font-size:.75rem;color:var(--muted)">${I.empty_history}</span>`;
      return;
    }
    renderSentimentChart(container, data.history);
  } catch {
    container.innerHTML = `<span style="font-size:.75rem;color:var(--muted)">${I.err_chart}</span>`;
  }
}

function renderSentimentChart(container, history) {
  const w = container.clientWidth || 300;
  const h = 120;
  const padL = 30, padR = 10, padT = 15, padB = 22;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;

  const scores = history.map(e => e.score);
  const minS = Math.min(...scores, -3);
  const maxS = Math.max(...scores, 3);
  const range = maxS - minS || 1;

  const n = history.length;
  const barGap = 1;
  const barW = Math.max(2, (plotW / n) - barGap);

  // Zero line Y
  const zeroY = padT + (1 - (0 - minS) / range) * plotH;

  // Build bars: red for positive score (up), green for negative (down) — A-share style
  const bars = history.map((e, i) => {
    const x = padL + i * (barW + barGap);
    const scoreY = padT + (1 - (e.score - minS) / range) * plotH;
    const barTop = Math.min(scoreY, zeroY);
    const barH = Math.max(Math.abs(scoreY - zeroY), 1);
    const color = e.score > 0 ? "var(--up)" : e.score < 0 ? "var(--down)" : "var(--muted)";
    return `<rect x="${x.toFixed(1)}" y="${barTop.toFixed(1)}" width="${barW.toFixed(1)}" height="${barH.toFixed(1)}" fill="${color}" opacity="0.85" rx="1">
      <title>${(e.ts||"").slice(0,16)} ${I.lbl_score}:${e.score} ${e.stage}</title>
    </rect>`;
  }).join("");

  // X-axis date labels (show a few)
  let xLabels = "";
  const step = Math.max(1, Math.floor(n / 5));
  for (let i = 0; i < n; i += step) {
    const x = padL + i * (barW + barGap) + barW / 2;
    const label = (history[i].ts || "").slice(5, 10); // "MM-DD"
    xLabels += `<text x="${x}" y="${h - 2}" text-anchor="middle" fill="var(--muted)" font-size="9">${label}</text>`;
  }

  // Y-axis labels
  const yLabels = [maxS, 0, minS].map(v => {
    const y = padT + (1 - (v - minS) / range) * plotH;
    return `<text x="${padL - 4}" y="${y + 3}" text-anchor="end" fill="var(--muted)" font-size="9">${v}</text>`;
  }).join("");

  container.innerHTML = `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="display:block">
    <line x1="${padL}" y1="${zeroY}" x2="${w - padR}" y2="${zeroY}" stroke="var(--border)" stroke-dasharray="3,3" stroke-width="0.5"/>
    ${bars}
    ${yLabels}
    ${xLabels}
  </svg>`;
}

async function refreshMainlineAuto() {
  const out = document.getElementById("out-mainline-auto");
  if (!out) return;
  out.textContent = I.status_mainline;
  store.mainline.loading = true;
  try {
    const res = await fetch("/api/mainline-auto");
    const data = await res.json();
    if (!data.ok) {
      out.textContent = data.msg || I.err_mainline;
      store.mainline.output = data.msg || I.err_mainline;
      return;
    }

    const leader = data.leader_stock || {};
    const text =
  `${I.lbl_mainline_sector}: ${data.mainline_sector}
${I.lbl_leader_stock}: ${leader.name || "—"} (${leader.code || "—"}) ${leader.change_pct ?? "—"}%
${I.lbl_participation}: ${data.tradable_text}
  ${I.lbl_analysis_time}: ${withUtc8Label(data.generated_at)}

${I.lbl_reasoning}:
- ${data.reason}

${I.lbl_suggestion}:
- ${data.suggestion}`;
    out.textContent = text;
    store.mainline.output = text;
  } catch (e) {
    out.textContent = I.err_request;
    store.mainline.output = I.err_request;
  } finally {
    store.mainline.loading = false;
  }
}

async function refreshAiEdge(forceRefresh=false) {
  const out = document.getElementById("out-ai-edge");
  if (!out) return;
  out.textContent = I.status_ai;
  store.aiEdge.loading = true;
  try {
    const suffix = forceRefresh ? "?refresh=1" : "";
    const res = await fetch(`/api/ai-edge${suffix}`);
    const data = await res.json();
    if (!data.ok) {
      out.textContent = data.msg || I.err_ai;
      store.aiEdge.output = data.msg || I.err_ai;
      return;
    }

    const s = data.summary || {};
    const focus = (data.focus || []).map(x => `- ${x.ticker} ${x.name || ""} ${x.change_pct}% (${x.source || "n/a"})`).join("\n");
    const risks = (data.risks || []).map(x => `- ${x.ticker} ${x.name || ""} ${x.change_pct}% (${x.source || "n/a"})`).join("\n");
    const playbook = (data.playbook || []).map(x => `- ${x}`).join("\n");

    const text =
`${I.lbl_generated_at}: ${withUtc8Label(data.generated_at)}
${I.lbl_market_bias}: ${s.market_bias || "—"}
${I.lbl_ai_confidence}: ${s.confidence ?? "—"}/100
${I.lbl_coverage}: ${s.coverage ?? "—"}（${I.lbl_up_count} ${s.up_count ?? "—"} / ${I.lbl_down_count} ${s.down_count ?? "—"}）
${I.lbl_avg_change}: ${s.avg_change_pct ?? "—"}%

${I.lbl_focus}:
${focus || `- ${I.lbl_none}`}

${I.lbl_risks}:
${risks || `- ${I.lbl_none}`}

${I.lbl_playbook}:
${playbook || `- ${I.lbl_none}`}`;
    out.textContent = text;
    store.aiEdge.output = text;
  } catch (e) {
    out.textContent = I.err_request;
    store.aiEdge.output = I.err_request;
  } finally {
    store.aiEdge.loading = false;
  }
}

const mainlineAutoBtn = document.getElementById("btn-mainline-auto");
if (mainlineAutoBtn) {
  mainlineAutoBtn.addEventListener("click", refreshMainlineAuto);
}

const marketSentimentAutoBtn = document.getElementById("btn-market-sentiment-auto");
if (marketSentimentAutoBtn) {
  marketSentimentAutoBtn.addEventListener("click", refreshMarketSentimentAuto);
}

const aiEdgeBtn = document.getElementById("btn-ai-edge");
if (aiEdgeBtn) {
  aiEdgeBtn.addEventListener("click", () => refreshAiEdge(true));
}

const limitStatsBtn = document.getElementById("btn-limit-stats");
if (limitStatsBtn) {
  limitStatsBtn.addEventListener("click", refreshLimitStats);
}

async function refreshLimitStats() {
  const out = document.getElementById("out-limit-stats");
  if (!out) return;
  out.textContent = I.status_limit;
  store.limitStats.loading = true;
  try {
    const res = await fetch("/api/limit-stats");
    const d = await res.json();

    const lu = d.limit_up != null ? d.limit_up : "—";
    const ld = d.limit_down != null ? d.limit_down : "—";
    const cb = d.consecutive_boards != null ? d.consecutive_boards : "—";
    const mb = d.max_board != null ? `${d.max_board}${I.unit_consecutive}` : "—";

    // Write store → flush to DOM
    store.stats.limitUp = lu;
    store.stats.limitDown = ld;

    let ztText = `${I.lbl_updated_at}: ${beijingTimestampLabel()}
${I.lbl_date}: ${d.date || "—"}
${I.lbl_limit_up}: ${lu}    ${I.lbl_limit_down}: ${ld}
${I.lbl_consec_boards}: ${cb}    ${I.lbl_max_consec}: ${mb}`;

    const perf = d.yesterday_limit_up_performance;
    if (perf) {
      store.stats.ztProfit = `${perf.profit_rate}%`;
      store.stats.ztProfitCls = perf.profit_rate >= 50 ? "up" : "down";

      ztText += `\n\n${I.lbl_yesterday_perf}:
${I.lbl_total}: ${perf.total}    ${I.lbl_up}: ${perf.up}    ${I.lbl_down}: ${perf.down}    ${I.lbl_flat}: ${perf.flat}
${I.lbl_avg_change}: ${perf.avg_change_pct}%
${I.lbl_win_rate}: ${perf.profit_rate}%
${I.lbl_verdict}: ${perf.verdict}`;
    } else {
      store.stats.ztProfit = "—";
      store.stats.ztProfitCls = "";
    }

    out.textContent = ztText;
    store.limitStats.output = ztText;
    syncStatsToDOM();
  } catch (e) {
    out.textContent = I.err_limit;
    store.limitStats.output = I.err_limit;
  } finally {
    store.limitStats.loading = false;
  }
}

// ── Auto-refresh (skip in Beijing quiet hours: 15:30-08:30) ────────────────
let _stockRefreshTimer = null;
function _startStockRefresh() {
  if (_stockRefreshTimer) clearInterval(_stockRefreshTimer);
  const ms = parseInt(document.getElementById("sel-refresh-interval").value, 10) || 60000;
  _stockRefreshTimer = setInterval(() => runAutoTask(loadStocks), ms);
}
_startStockRefresh();
document.getElementById("sel-refresh-interval").addEventListener("change", () => {
  _startStockRefresh();
  localStorage.setItem("yykanpan-refresh-interval", document.getElementById("sel-refresh-interval").value);
});
// Restore saved preference
(function() {
  const saved = localStorage.getItem("yykanpan-refresh-interval");
  if (saved) {
    const sel = document.getElementById("sel-refresh-interval");
    sel.value = saved;
    _startStockRefresh();
  }
})();
setInterval(() => runAutoTask(loadMacro), 300_000);  // every 5min
setInterval(() => runAutoTask(() => generateAutoBrief(false)), 1_800_000);
setInterval(() => runAutoTask(refreshMarketSentimentAuto), 1_800_000);
setInterval(() => runAutoTask(refreshMainlineAuto), 1_800_000);
setInterval(() => runAutoTask(() => refreshAiEdge(false)), 1_800_000);
setInterval(() => runAutoTask(refreshLimitStats), 300_000);  // every 5min
setInterval(updateAutoRefreshStatus, 60_000);

// ── Midnight daily refresh (00:00 Beijing time) ──────────────────────────────
(function initMidnightRefresh() {
  let _lastBjDate = "";

  function getBjDateStr() {
    const bj = new Date(Date.now() + (8 * 3600_000 + new Date().getTimezoneOffset() * 60_000));
    return bj.toISOString().slice(0, 10);
  }

  _lastBjDate = getBjDateStr();

  // Check every 30 seconds if Beijing date has rolled over
  setInterval(() => {
    const today = getBjDateStr();
    if (today !== _lastBjDate) {
      _lastBjDate = today;
      console.log("[midnight] Beijing date changed to", today, "— refreshing all cards");
      // Always refresh bazi + xgxz (date-dependent); other cards respect quiet hours
      loadBazi();
      loadXinguXinzhai();
      runAutoTask(refreshAllCards);
    }
  }, 30_000);
})();

// ── Init ──────────────────────────────────────────────────────────────────────
loadPositions();

// Pre-fill demo holdings (only if localStorage is empty)
if (!Object.keys(positions).length) {
  const defaults = {
    "600519.SS": { shares: 100,  cost: 1680.00 },
    "000858.SZ": { shares: 500,  cost: 148.50 },
    "601318.SS": { shares: 1000, cost: 52.00 },
    "300750.SZ": { shares: 200,  cost: 210.00 },
    "000001.SZ": { shares: 2000, cost: 11.50 },
    "600036.SS": { shares: 800,  cost: 35.00 },
    "600900.SS": { shares: 600,  cost: 25.00 },
    "601857.SS": { shares: 3000, cost: 8.80 },
  };
  positions = defaults;
  savePositions();
}

loadWatchdogConfig();

// ── Sentiment threshold config UI ───────────────────────────────────────────
(function initSentimentConfig() {
  const fields = [
    "up-ratio-strong", "up-ratio-mild", "down-ratio-strong", "down-ratio-mild",
    "limit-up-high", "limit-up-mid", "limit-up-low",
    "consec-high", "consec-mid", "consec-low"
  ];
  const toKey = id => id.replace(/-/g, "_");

  function fillInputs(cfg) {
    fields.forEach(f => {
      const el = document.getElementById(`cfg-${f}`);
      if (el && cfg[toKey(f)] != null) el.value = cfg[toKey(f)];
    });
  }

  // Load current config from server
  fetch("/api/sentiment-config").then(r => r.json()).then(d => {
    if (d.ok) fillInputs(d.thresholds);
  }).catch(() => {});

  // Presets
  const presets = {
    bull:   { up_ratio_strong: 0.60, up_ratio_mild: 0.50, down_ratio_strong: 0.70, down_ratio_mild: 0.60, limit_up_high: 60, limit_up_mid: 30, limit_up_low: 12, consec_high: 15, consec_mid: 8, consec_low: 3 },
    normal: { up_ratio_strong: 0.65, up_ratio_mild: 0.55, down_ratio_strong: 0.65, down_ratio_mild: 0.55, limit_up_high: 45, limit_up_mid: 20, limit_up_low: 8, consec_high: 12, consec_mid: 5, consec_low: 2 },
    bear:   { up_ratio_strong: 0.70, up_ratio_mild: 0.60, down_ratio_strong: 0.60, down_ratio_mild: 0.50, limit_up_high: 35, limit_up_mid: 15, limit_up_low: 5, consec_high: 8, consec_mid: 3, consec_low: 1 },
  };

  document.getElementById("cfg-preset-bull")?.addEventListener("click", () => fillInputs(presets.bull));
  document.getElementById("cfg-preset-normal")?.addEventListener("click", () => fillInputs(presets.normal));
  document.getElementById("cfg-preset-bear")?.addEventListener("click", () => fillInputs(presets.bear));

  document.getElementById("cfg-save")?.addEventListener("click", async () => {
    const body = {};
    fields.forEach(f => {
      const el = document.getElementById(`cfg-${f}`);
      if (el && el.value) body[toKey(f)] = Number(el.value);
    });
    try {
      const res = await fetch("/api/sentiment-config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body)
      });
      const d = await res.json();
      if (d.ok) alert(I.cfg_saved);
    } catch { alert(I.cfg_save_failed); }
  });
})();

// ── Card drag-and-drop reorder ──────────────────────────────────────────────
(function initCardDrag() {
  const CARD_ORDER_KEY = "card_order_v1";
  const wrap = document.getElementById("insight-wrap");
  let dragSrc = null;

  function getCards() { return [...wrap.querySelectorAll(".insight-card[data-card-id]")]; }

  function saveOrder() {
    const order = getCards().map(c => c.dataset.cardId);
    localStorage.setItem(CARD_ORDER_KEY, JSON.stringify(order));
  }

  function restoreOrder() {
    try {
      const order = JSON.parse(localStorage.getItem(CARD_ORDER_KEY));
      if (!Array.isArray(order)) return;
      const map = {};
      getCards().forEach(c => { map[c.dataset.cardId] = c; });
      order.forEach(id => { if (map[id]) wrap.appendChild(map[id]); });
    } catch {}
  }

  function bindCard(card) {
    card.addEventListener("dragstart", e => {
      dragSrc = card;
      card.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", card.dataset.cardId);
    });
    card.addEventListener("dragend", () => {
      card.classList.remove("dragging");
      getCards().forEach(c => c.classList.remove("drag-over"));
      dragSrc = null;
    });
    card.addEventListener("dragover", e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      if (card !== dragSrc) card.classList.add("drag-over");
    });
    card.addEventListener("dragleave", () => { card.classList.remove("drag-over"); });
    card.addEventListener("drop", e => {
      e.preventDefault();
      card.classList.remove("drag-over");
      if (!dragSrc || dragSrc === card) return;
      const cards = getCards();
      const fromIdx = cards.indexOf(dragSrc);
      const toIdx = cards.indexOf(card);
      if (fromIdx < toIdx) card.after(dragSrc);
      else card.before(dragSrc);
      saveOrder();
    });
  }

  getCards().forEach(bindCard);
  restoreOrder();
})();

// ── Card hide / restore ─────────────────────────────────────────────────────
(function initCardVisibility() {
  const HIDDEN_KEY = "hidden_cards_v1";
  const CARD_NAMES = {
    stats: I.card_stats, "ai-edge": I.card_ai_edge, watchdog: I.card_watchdog,
    "limit-stats": I.card_limit, sentiment: I.card_sentiment,
    mainline: I.card_mainline, brief: I.card_brief, "invest-tip": I.card_invest_tip,
    macro: I.card_macro, bazi: I.card_bazi, xgxz: I.card_xgxz,
    advisor: I.card_advisor, "risk-events": I.card_risk, decisions: I.card_decisions
  };
  const wrap = document.getElementById("insight-wrap");
  const bar = document.getElementById("restore-bar");

  function getHidden() {
    try { return JSON.parse(localStorage.getItem(HIDDEN_KEY)) || []; } catch { return []; }
  }
  function setHidden(arr) { localStorage.setItem(HIDDEN_KEY, JSON.stringify(arr)); }

  function hideCard(id) {
    const card = wrap.querySelector(`.insight-card[data-card-id="${id}"]`);
    if (card && card.classList.contains("pinned")) return;
    if (card) card.style.display = "none";
    const h = getHidden(); if (!h.includes(id)) { h.push(id); setHidden(h); }
    renderBar();
  }

  function showCard(id) {
    const card = wrap.querySelector(`.insight-card[data-card-id="${id}"]`);
    if (card) card.style.display = "";
    const h = getHidden().filter(x => x !== id); setHidden(h);
    renderBar();
  }

  function renderBar() {
    const h = getHidden();
    bar.innerHTML = "";
    if (!h.length) { bar.classList.remove("has-items"); return; }
    bar.classList.add("has-items");
    const label = document.createElement("span");
    label.className = "lbl";
    label.style.marginLeft = "12px";
    label.textContent = I.lbl_hidden;
    bar.appendChild(label);
    h.forEach(id => {
      const chip = document.createElement("button");
      chip.className = "restore-chip";
      chip.textContent = "+ " + (CARD_NAMES[id] || id);
      chip.onclick = () => showCard(id);
      bar.appendChild(chip);
    });
  }

  // bind close buttons
  wrap.querySelectorAll(".card-close").forEach(btn => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".insight-card");
      if (card) hideCard(card.dataset.cardId);
    });
  });

  // Hide/show all toggle
  let allHidden = false;
  const hideAllBtn = document.getElementById("btn-hide-all");
  hideAllBtn.addEventListener("click", () => {
    const cards = wrap.querySelectorAll(".insight-card");
    allHidden = !allHidden;
    if (allHidden) {
      cards.forEach(c => hideCard(c.dataset.cardId));
      hideAllBtn.textContent = "👁";
      hideAllBtn.title = "显示全部卡片";
    } else {
      const h = [...getHidden()];
      h.forEach(id => showCard(id));
      hideAllBtn.textContent = "👁";
      hideAllBtn.title = "隐藏全部卡片";
    }
  });

  // Restore hidden cards on load
  getHidden().forEach(id => hideCard(id));
  renderBar();

  // ── Card collapse/expand ────────────────────────────────────────────────
  const COLLAPSE_KEY = "card_collapsed_v1";
  function getCollapsed() {
    try { return JSON.parse(localStorage.getItem(COLLAPSE_KEY)) || []; } catch { return []; }
  }
  function setCollapsed(arr) { localStorage.setItem(COLLAPSE_KEY, JSON.stringify(arr)); }

  function toggleCollapse(card) {
    const id = card.dataset.cardId;
    const isCollapsed = card.classList.toggle("collapsed");
    const btn = card.querySelector(".card-collapse");
    if (btn) btn.textContent = isCollapsed ? "+" : "−";
    let arr = getCollapsed();
    if (isCollapsed && !arr.includes(id)) arr.push(id);
    else arr = arr.filter(x => x !== id);
    setCollapsed(arr);
  }

  wrap.querySelectorAll(".card-collapse").forEach(btn => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".insight-card");
      if (card) toggleCollapse(card);
    });
  });

  // Restore collapsed state
  getCollapsed().forEach(id => {
    const card = wrap.querySelector(`.insight-card[data-card-id="${id}"]`);
    if (card) {
      card.classList.add("collapsed");
      const btn = card.querySelector(".card-collapse");
      if (btn) btn.textContent = "+";
    }
  });

  // Global collapse/expand toggle
  let allCollapsed = false;
  const foldBtn = document.getElementById("btn-fold-toggle");
  foldBtn.addEventListener("click", () => {
    allCollapsed = !allCollapsed;
    if (allCollapsed) {
      const ids = [];
      wrap.querySelectorAll(".insight-card").forEach(c => {
        c.classList.add("collapsed");
        const btn = c.querySelector(".card-collapse");
        if (btn) btn.textContent = "+";
        ids.push(c.dataset.cardId);
      });
      setCollapsed(ids);
      foldBtn.textContent = "+";
      foldBtn.title = "全部展开";
    } else {
      wrap.querySelectorAll(".insight-card").forEach(c => {
        c.classList.remove("collapsed");
        const btn = c.querySelector(".card-collapse");
        if (btn) btn.textContent = "−";
      });
      setCollapsed([]);
      foldBtn.textContent = "−";
      foldBtn.title = "全部折叠";
    }
  });
  // Sync fold button state on load
  if (getCollapsed().length === wrap.querySelectorAll(".insight-card").length) {
    allCollapsed = true;
    foldBtn.textContent = "+";
    foldBtn.title = "全部展开";
  }

  // restore saved hidden state
  getHidden().forEach(id => {
    const card = wrap.querySelector(`.insight-card[data-card-id="${id}"]`);
    if (card) card.style.display = "none";
  });
  renderBar();

  // ── Card pin (prevent drag & close) ──────────────────────────────────
  const LOCK_KEY = "card_locked_v1";
  function getLocked() { try { return JSON.parse(localStorage.getItem(LOCK_KEY)) || []; } catch { return []; } }
  function setLocked(arr) { localStorage.setItem(LOCK_KEY, JSON.stringify(arr)); }

  wrap.querySelectorAll(".insight-card[data-card-id]").forEach(card => {
    const h3 = card.querySelector("h3");
    if (!h3) return;
    const collapseBtn = h3.querySelector(".card-collapse");
    const closeBtn = h3.querySelector(".card-close");

    // Wrap all 3 buttons in a group container
    const group = document.createElement("span");
    group.className = "card-btn-group";

    const pinBtn = document.createElement("button");
    pinBtn.className = "card-pin";
    pinBtn.title = "固定位置";
    pinBtn.textContent = "◇";
    group.appendChild(pinBtn);

    if (collapseBtn) { group.appendChild(collapseBtn); }
    if (closeBtn) { group.appendChild(closeBtn); }
    h3.appendChild(group);

    pinBtn.addEventListener("click", () => {
      const id = card.dataset.cardId;
      const isPinned = card.classList.toggle("pinned");
      pinBtn.textContent = isPinned ? "◆" : "◇";
      pinBtn.title = isPinned ? "取消固定" : "固定位置";
      card.setAttribute("draggable", isPinned ? "false" : "true");
      let arr = getLocked();
      if (isPinned && !arr.includes(id)) arr.push(id);
      else arr = arr.filter(x => x !== id);
      setLocked(arr);
    });
  });

  // Restore pinned state
  getLocked().forEach(id => {
    const card = wrap.querySelector(`.insight-card[data-card-id="${id}"]`);
    if (card) {
      card.classList.add("pinned");
      card.setAttribute("draggable", "false");
      const btn = card.querySelector(".card-pin");
      if (btn) { btn.textContent = "◆"; btn.title = "取消固定"; }
    }
  });
})();

// ── [claude code] Beginner mode (新手三键模式) ──────────────────────────────
// Default surface for first-time users: only 3 cards (stats/advisor/decisions)
// + the always-visible 我的持仓 stock section. Power-user controls
// (drag/pin/close/hide-all/fold-all/layout selector) are CSS-suppressed via
// body.beginner-mode in style.css. Toggling switches body class only;
// all other state (HIDDEN_KEY/COLLAPSE_KEY/LOCK_KEY/CARD_ORDER) stays intact,
// so leaving beginner mode restores whatever the user had before.
(function initBeginnerMode() {
  const KEY = "beginner_mode_v1";
  const btn = document.getElementById("btn-mode-toggle");
  if (!btn) return;

  // First-time detection: if user has NEVER touched any power-user state,
  // they're a newbie → default ON. If any of those keys exist, they've used
  // the dashboard before → keep advanced default OFF.
  function isFirstTime() {
    return !localStorage.getItem("hidden_cards_v1")
        && !localStorage.getItem("card_collapsed_v1")
        && !localStorage.getItem("card_locked_v1")
        && !localStorage.getItem("card_order_v1")
        && !localStorage.getItem("card_cols_v1");
  }

  function isOn() {
    const v = localStorage.getItem(KEY);
    if (v === null) return isFirstTime();   // auto-enable for newbies
    return v === "1";
  }

  function apply(on) {
    document.body.classList.toggle("beginner-mode", on);
    btn.textContent = on ? "🎓 新手" : "⚙️ 进阶";
    btn.title = on ? "当前：新手模式（点击切换到进阶）" : "当前：进阶模式（点击切换到新手）";
  }

  btn.addEventListener("click", () => {
    const next = !isOn();
    localStorage.setItem(KEY, next ? "1" : "0");
    apply(next);
  });

  apply(isOn());
})();

// ── Column layout selector ─────────────────────────────────────────────────────────
(function initColLayout() {
  const COL_KEY = "card_cols_v1";
  const wrap = document.getElementById("insight-wrap");
  const btns = document.querySelectorAll(".col-layout");

  function apply(val) {
    if (val === "auto") {
      wrap.style.gridTemplateColumns = "repeat(auto-fit, minmax(280px, 1fr))";
    } else {
      wrap.style.gridTemplateColumns = `repeat(${val}, 1fr)`;
    }
    btns.forEach(b => b.classList.toggle("active", b.dataset.cols === val));
    localStorage.setItem(COL_KEY, val);
  }

  btns.forEach(b => b.addEventListener("click", () => apply(b.dataset.cols)));
  apply(localStorage.getItem(COL_KEY) || "auto");
})();

applyColorMode(localStorage.getItem("color_mode") || "cn");
applyPrivacyMode();
updateAutoRefreshStatus();

// ── Decision Journal (决策日志) ──────────────────────────────────────────────
(function initDecisionJournal() {
  const TYPE_LABEL = { trade: "交易", life: "生活", work: "工作" };
  const STATE_LABEL = { idea: "💡 想法", decided: "✅ 已决", acted: "🚀 已执行", reviewed: "📝 已复盘" };
  const STATES = ["idea", "decided", "acted", "reviewed"];

  let allDecisions = [];
  let currentView = "kanban";

  // ── API helpers ──
  async function apiGet(url) { const r = await fetch(url); return r.json(); }
  async function apiPost(url, body) {
    return (await fetch(url, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body) })).json();
  }
  async function apiPut(url, body) {
    return (await fetch(url, { method: "PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body) })).json();
  }
  async function apiDel(url) { return (await fetch(url, { method: "DELETE" })).json(); }

  // ── Load & render ──
  async function loadDecisions() {
    const typeFilter = document.getElementById("dec-filter-type")?.value || "";
    const params = new URLSearchParams();
    if (typeFilter) params.set("type", typeFilter);
    const url = "/api/decisions" + (params.toString() ? "?" + params : "");
    const d = await apiGet(url);
    if (d.ok) allDecisions = d.decisions;
    render();
  }

  function render() {
    const total = document.getElementById("dec-total");
    if (total) total.textContent = `共 ${allDecisions.length} 条`;
    if (currentView === "kanban") renderKanban();
    else renderList();
  }

  function makeCardHTML(d) {
    const tags = (d.tags || []).map(t => `<span class="dec-tag">${esc(t)}</span>`).join("");
    const time = d.created_at ? d.created_at.slice(5, 16) : "";
    // Trade info line
    let tradeInfo = "";
    if (d.type === "trade" && d.symbol) {
      const actionCls = (d.action || "").toUpperCase();
      const badge = actionCls === "BUY" ? "ac-buy" : actionCls === "SELL" ? "ac-sell" : "ac-hold";
      const parts = [`<span class="dec-action-badge ${badge}">${d.action || "HOLD"}</span>`];
      parts.push(`<span>${esc(d.symbol)}</span>`);
      if (d.price) parts.push(`<span>¥${d.price}</span>`);
      if (d.size) parts.push(`<span>×${d.size}</span>`);
      if (d.confidence) parts.push(`<span title="信心">🎯${(d.confidence * 100).toFixed(0)}%</span>`);
      if (d.source && d.source !== "manual") parts.push(`<span class="dec-src-badge">${d.source}</span>`);
      tradeInfo = `<div class="dec-trade-info">${parts.join(" ")}</div>`;
    }
    return `<div class="dec-card" draggable="true" data-id="${d.id}">
      <div class="dec-card-title">${esc(d.title)}</div>
      <div class="dec-card-meta">
        <span class="dec-type-badge" data-type="${d.type}">${TYPE_LABEL[d.type] || d.type}</span>
        ${tags}
      </div>
      ${tradeInfo}
      ${d.context ? `<div class="dec-card-time" title="环境">${esc(d.context.slice(0, 60))}</div>` : ""}
      <div class="dec-card-time">${time}</div>
      <div class="dec-card-actions">
        ${STATES.filter(s => s !== d.state).map(s =>
          `<button data-id="${d.id}" data-to="${s}" class="dec-move-btn">${STATE_LABEL[s]}</button>`
        ).join("")}
        <button data-id="${d.id}" class="dec-del-btn" title="删除">🗑</button>
      </div>
    </div>`;
  }

  function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

  function renderKanban() {
    document.getElementById("dec-kanban").style.display = "";
    document.getElementById("dec-list-view").style.display = "none";
    STATES.forEach(state => {
      const col = document.querySelector(`.dec-col-body[data-state="${state}"]`);
      if (!col) return;
      const items = allDecisions.filter(d => d.state === state);
      col.innerHTML = items.map(makeCardHTML).join("") || `<div style="color:var(--muted);font-size:.75rem;text-align:center;padding:12px 0">空</div>`;
    });
    bindCardEvents();
    bindKanbanDrag();
  }

  function renderList() {
    document.getElementById("dec-kanban").style.display = "none";
    const lv = document.getElementById("dec-list-view");
    lv.style.display = "";
    const sorted = [...allDecisions].sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
    lv.innerHTML = sorted.map(d => {
      const tags = (d.tags || []).map(t => `<span class="dec-tag">${esc(t)}</span>`).join(" ");
      return `<div class="dec-list-item">
        <span class="dec-type-badge" data-type="${d.type}">${TYPE_LABEL[d.type]}</span>
        <span>${esc(d.title)} ${tags}</span>
        <span style="color:var(--muted);font-size:.75rem">${(d.created_at || "").slice(5, 16)}</span>
        <span style="font-size:.75rem">${STATE_LABEL[d.state] || d.state}</span>
      </div>`;
    }).join("") || `<div style="color:var(--muted);text-align:center;padding:16px">暂无决策</div>`;
  }

  // ── Card interaction events ──
  function bindCardEvents() {
    document.querySelectorAll(".dec-move-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        await apiPut(`/api/decisions/${btn.dataset.id}`, { state: btn.dataset.to });
        loadDecisions();
      });
    });
    document.querySelectorAll(".dec-del-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        if (!confirm("确定删除此决策？")) return;
        await apiDel(`/api/decisions/${btn.dataset.id}`);
        loadDecisions();
      });
    });
  }

  // ── Kanban drag-and-drop (move between columns) ──
  function bindKanbanDrag() {
    let dragCard = null;
    document.querySelectorAll(".dec-card[draggable]").forEach(card => {
      card.addEventListener("dragstart", e => {
        dragCard = card;
        card.classList.add("dragging");
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", card.dataset.id);
      });
      card.addEventListener("dragend", () => {
        card.classList.remove("dragging");
        document.querySelectorAll(".dec-col-body").forEach(c => c.classList.remove("drag-over"));
        dragCard = null;
      });
    });
    document.querySelectorAll(".dec-col-body").forEach(col => {
      col.addEventListener("dragover", e => { e.preventDefault(); col.classList.add("drag-over"); });
      col.addEventListener("dragleave", () => col.classList.remove("drag-over"));
      col.addEventListener("drop", async e => {
        e.preventDefault();
        col.classList.remove("drag-over");
        if (!dragCard) return;
        const newState = col.dataset.state;
        const id = dragCard.dataset.id;
        await apiPut(`/api/decisions/${id}`, { state: newState });
        loadDecisions();
      });
    });
  }

  // ── Create decision ──
  document.getElementById("btn-dec-save")?.addEventListener("click", async () => {
    const title = document.getElementById("dec-title")?.value?.trim();
    if (!title) { document.getElementById("dec-msg").textContent = "请输入标题"; return; }
    const dtype = document.getElementById("dec-type")?.value || "trade";
    const body = {
      title,
      type: dtype,
      state: document.getElementById("dec-state")?.value || "idea",
      context: document.getElementById("dec-context")?.value || "",
      action: document.getElementById("dec-action")?.value || "",
      outcome: document.getElementById("dec-outcome")?.value || "",
      tags: (document.getElementById("dec-tags")?.value || "").split(",").map(s => s.trim()).filter(Boolean),
    };
    // Attach trade fields if type=trade
    if (dtype === "trade") {
      const tradeAction = document.getElementById("dec-trade-action")?.value;
      if (tradeAction) body.action = tradeAction;
      const symbol = document.getElementById("dec-symbol")?.value?.trim();
      if (symbol) body.symbol = symbol;
      const price = parseFloat(document.getElementById("dec-price")?.value);
      if (price > 0) body.price = price;
      const size = parseInt(document.getElementById("dec-size")?.value);
      if (size > 0) body.size = size;
      const sl = parseFloat(document.getElementById("dec-stoploss")?.value);
      if (sl > 0) body.stop_loss = sl;
      const tp = parseFloat(document.getElementById("dec-takeprofit")?.value);
      if (tp > 0) body.take_profit = tp;
      const conf = parseFloat(document.getElementById("dec-confidence")?.value);
      if (conf >= 0 && conf <= 1) body.confidence = conf;
      body.source = "manual";
    }
    const r = await apiPost("/api/decisions", body);
    if (r.ok) {
      document.getElementById("dec-msg").textContent = "✓ 已保存";
      // Reset form
      ["dec-title", "dec-context", "dec-action", "dec-outcome", "dec-tags",
       "dec-symbol", "dec-price", "dec-size", "dec-stoploss", "dec-takeprofit", "dec-confidence"
      ].forEach(id => {
        const el = document.getElementById(id); if (el) el.value = "";
      });
      const ta = document.getElementById("dec-trade-action");
      if (ta) ta.selectedIndex = 0;
      loadDecisions();
      setTimeout(() => { document.getElementById("dec-msg").textContent = ""; }, 2000);
    } else {
      document.getElementById("dec-msg").textContent = "✗ " + (r.error || "保存失败");
    }
  });

  // ── Type toggle: show/hide trade fields ──
  document.getElementById("dec-type")?.addEventListener("change", e => {
    const tf = document.getElementById("dec-trade-fields");
    if (tf) tf.style.display = e.target.value === "trade" ? "" : "none";
  });

  // ── View toggle ──
  document.querySelectorAll(".dec-view-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      currentView = btn.dataset.view;
      document.querySelectorAll(".dec-view-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      render();
    });
  });

  // ── Filter ──
  document.getElementById("dec-filter-type")?.addEventListener("change", () => loadDecisions());

  // ── Analyze ──
  document.getElementById("btn-dec-analyze")?.addEventListener("click", async () => {
    const panel = document.getElementById("dec-analyze-panel");
    if (!panel) return;
    if (panel.style.display !== "none") { panel.style.display = "none"; return; }
    panel.innerHTML = '<span style="color:var(--muted)">分析中…</span>';
    panel.style.display = "";
    const resp = await fetch("/api/decisions/analyze?type=trade");
    const r = await resp.json();
    if (!r.ok) { panel.innerHTML = '<span style="color:var(--down)">分析失败</span>'; return; }
    const sevColor = { danger: "var(--down)", warn: "#f0ad4e", info: "var(--muted)" };
    const patternHTML = (r.patterns || []).map(p =>
      `<div class="dec-pattern" style="border-left:3px solid ${sevColor[p.severity] || 'var(--muted)'}">
        <span class="dec-pattern-label">${esc(p.label)}</span>
      </div>`
    ).join("") || '<div style="color:var(--muted)">暂无模式发现</div>';
    panel.innerHTML = `
      <div class="dec-analyze-stats">
        <div class="dec-stat"><span class="dec-stat-num">${r.total}</span><span class="dec-stat-label">总决策</span></div>
        <div class="dec-stat"><span class="dec-stat-num" style="color:var(--up)">${r.buys}</span><span class="dec-stat-label">买入</span></div>
        <div class="dec-stat"><span class="dec-stat-num" style="color:var(--down)">${r.sells}</span><span class="dec-stat-label">卖出</span></div>
        <div class="dec-stat"><span class="dec-stat-num">${r.holds}</span><span class="dec-stat-label">持有</span></div>
        <div class="dec-stat"><span class="dec-stat-num">${(r.avg_confidence * 100).toFixed(0)}%</span><span class="dec-stat-label">平均信心</span></div>
      </div>
      <div class="dec-analyze-sources">
        ${Object.entries(r.by_source || {}).map(([k, v]) =>
          `<span class="dec-src-chip">${k}: ${v}</span>`
        ).join("")}
      </div>
      <div class="dec-analyze-patterns">
        <div style="font-weight:600;margin-bottom:6px">🔍 行为模式</div>
        ${patternHTML}
      </div>
    `;
  });

  // ── Boot ──
  window._reloadDecisions = loadDecisions;
  loadDecisions();
})();

// ── 新股新债 (IPO & bond subscription, refreshes at midnight only) ───────────
async function loadXinguXinzhai() {
  const body = document.getElementById("xgxz-body");
  if (!body) return;
  body.innerHTML = '<span class="macro-loading">加载中…</span>';
  try {
    const res = await fetch("/api/xingu-xinzhai");
    const d = await res.json();
    if (!d.ok) { body.innerHTML = '<span class="macro-loading">获取失败</span>'; return; }
    const today = d.date;  // "YYYY-MM-DD"
    function dateCls(dt) {
      if (!dt) return "";
      if (dt === today) return "xgxz-today";
      return dt > today ? "xgxz-future" : "xgxz-past";
    }
    function fmtRate(r) {
      if (r == null) return "—";
      return (r * 100).toFixed(4) + "%";
    }
    function fmtMult(m) {
      if (m == null) return "—";
      return m.toFixed(0) + "倍";
    }
    let html = '';
    // 新股
    html += '<div class="xgxz-section-title">📈 新股申购</div>';
    if (d.ipo.length) {
      html += '<table class="xgxz-table"><tr><th>代码</th><th>名称</th><th>申购日</th><th>发行价</th><th>中签率</th><th>超额倍数</th></tr>';
      d.ipo.forEach(s => {
        const cls = dateCls(s.apply_date);
        html += `<tr class="${cls}"><td>${s.code}</td><td>${s.name}</td><td>${s.apply_date || "—"}</td><td>${s.price != null ? s.price.toFixed(2) : "—"}</td><td>${fmtRate(s.win_rate)}</td><td>${fmtMult(s.multiple)}</td></tr>`;
      });
      html += '</table>';
    } else {
      html += '<div class="xgxz-empty">暂无新股数据</div>';
    }
    // 新债
    html += '<div class="xgxz-section-title">📊 新债申购</div>';
    if (d.bond.length) {
      html += '<table class="xgxz-table"><tr><th>代码</th><th>名称</th><th>申购日</th><th>上市日</th><th>中签率</th></tr>';
      d.bond.forEach(b => {
        const cls = dateCls(b.apply_date);
        html += `<tr class="${cls}"><td>${b.code}</td><td>${b.apply_name || b.name}</td><td>${b.apply_date || "—"}</td><td>${b.list_date || "—"}</td><td>${fmtRate(b.win_rate)}</td></tr>`;
      });
      html += '</table>';
    } else {
      html += '<div class="xgxz-empty">暂无新债数据</div>';
    }
    body.innerHTML = html;
    // Reset scroll and update fade hint after content loaded
    body.scrollLeft = 0;
    body.classList.remove("scrolled-end");
  } catch (_) {
    body.innerHTML = '<span class="macro-loading">获取失败</span>';
  }
}
loadXinguXinzhai();  // boot once

// ── Advisor Card (可解释AI决策面板) ─────────────────────────────────────────
(function() {
  const btn = document.getElementById("btn-advisor-run");
  const body = document.getElementById("advisor-body");
  const status = document.getElementById("advisor-status");
  const selRisk = document.getElementById("advisor-risk-pref");

  // ── Radar chart SVG (5 factors) ──
  function renderRadarChart(factors) {
    const size = 140, cx = size / 2, cy = size / 2, r = 52;
    const n = factors.length;
    if (n < 3) return "";

    const angle = (i) => (Math.PI * 2 * i / n) - Math.PI / 2;
    const pt = (i, scale) => {
      const a = angle(i);
      return [cx + r * scale * Math.cos(a), cy + r * scale * Math.sin(a)];
    };

    // Grid rings
    let grid = "";
    for (const s of [0.25, 0.5, 0.75, 1.0]) {
      const pts = factors.map((_, i) => pt(i, s).join(",")).join(" ");
      grid += `<polygon points="${pts}" fill="none" stroke="var(--border)" stroke-width="0.5" opacity="0.5"/>`;
    }

    // Axis lines + labels
    let axes = "";
    factors.forEach((f, i) => {
      const [x, y] = pt(i, 1.0);
      axes += `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="var(--border)" stroke-width="0.5" opacity="0.4"/>`;
      const [lx, ly] = pt(i, 1.25);
      axes += `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" fill="var(--muted)" font-size="9">${f.name}</text>`;
    });

    // Data polygon: score -2..+2 → 0..1
    const dataPts = factors.map((f, i) => {
      const norm = (f.score + 2) / 4; // -2→0, 0→0.5, +2→1
      return pt(i, Math.max(norm, 0.05)).join(",");
    }).join(" ");

    // Color: aggregate score
    const avg = factors.reduce((s, f) => s + f.score, 0) / n;
    const fill = avg > 0.5 ? "var(--up)" : avg < -0.5 ? "var(--down)" : "var(--muted)";

    return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" class="advisor-radar">
      ${grid}${axes}
      <polygon points="${dataPts}" fill="${fill}" fill-opacity="0.2" stroke="${fill}" stroke-width="1.5"/>
    </svg>`;
  }

  // ── Factor bar row ──
  function renderFactorBar(f) {
    // score: -2..+2 → bar position in 0..100%, center at 50%
    const pct = ((f.score + 2) / 4) * 100;
    const barCls = f.score > 0 ? "factor-pos" : f.score < 0 ? "factor-neg" : "factor-neu";
    const scoreLabel = f.score > 0 ? `+${f.score}` : `${f.score}`;
    return `<div class="factor-row">
      <span class="factor-name">${f.name}</span>
      <div class="factor-track">
        <div class="factor-center"></div>
        <div class="factor-fill ${barCls}" style="width:${pct}%"></div>
      </div>
      <span class="factor-score ${barCls}">${scoreLabel}</span>
      <span class="factor-detail" title="${f.detail}">${f.detail}</span>
    </div>`;
  }

  // ── Save signal to decision journal ──
  async function saveToJournal(sig, riskPref, portfolioAction) {
    // Find position data from localStorage for price/size
    const posMap = JSON.parse(localStorage.getItem("positions_v1") || "{}");
    const pos = posMap[sig.ticker] || {};
    try {
      const res = await fetch("/api/advisor/save-decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker: sig.ticker,
          name: sig.name,
          action: sig.action,
          reasons: sig.reasons,
          factors: sig.factors || [],
          risk_pref: riskPref,
          portfolio_action: portfolioAction,
          price: pos.cost || 0,
          size: pos.shares || 0,
          stop_loss: sig.stop_loss || null,
          take_profit: sig.take_profit || null,
          strength: sig.strength || 1,
        })
      });
      const d = await res.json();
      if (d.ok) {
        alert(`✓ 已记录到决策日志`);
        // Reload decision journal if the IIFE exposed a reload
        if (typeof window._reloadDecisions === "function") window._reloadDecisions();
      } else {
        alert("保存失败: " + (d.error || "未知错误"));
      }
    } catch (e) {
      alert("网络错误");
    }
  }

  async function loadAdvisor() {
    // Build positions array from localStorage
    const posMap = JSON.parse(localStorage.getItem("positions_v1") || "{}");
    const posArr = Object.entries(posMap)
      .filter(([, v]) => v && v.shares > 0 && v.cost > 0)
      .map(([ticker, v]) => ({ ticker, shares: v.shares, cost: v.cost }));

    if (posArr.length === 0) {
      body.innerHTML = '<div class="advisor-no-positions">暂无持仓数据。请先在股票卡片中设置持仓和成本。</div>';
      return;
    }

    const riskPref = selRisk.value;
    status.textContent = "评估中…";
    btn.disabled = true;

    try {
      const url = `/api/advisor?risk_pref=${encodeURIComponent(riskPref)}&positions=${encodeURIComponent(JSON.stringify(posArr))}`;
      const resp = await fetch(url);
      const data = await resp.json();

      if (!data.ok) {
        body.innerHTML = `<div class="advisor-empty">${data.msg || "评估失败"}</div>`;
        status.textContent = "";
        return;
      }

      let html = '';

      // ── Portfolio-level action banner ──
      const pa = data.portfolio_action || "观望";
      const paCls = pa === "加仓" ? "pa-add" : pa === "减仓" ? "pa-reduce" : pa === "清仓避险" ? "pa-danger" : "pa-hold";
      html += `<div class="advisor-portfolio ${paCls}">`;
      html += `<div class="advisor-portfolio-action">${pa}</div>`;
      html += `<div class="advisor-portfolio-reason">${data.portfolio_reason || ""}</div>`;
      const ctx = data.context || {};
      html += `<div class="advisor-ctx">`;
      html += `<span class="advisor-ctx-chip">市场 <b>${ctx.regime || "—"}</b></span>`;
      html += `<span class="advisor-ctx-chip">情绪 <b>${ctx.sentiment_stage || "—"}</b></span>`;
      html += `<span class="advisor-ctx-chip">信心 <b>${ctx.confidence ?? "—"}%</b></span>`;
      html += `<span class="advisor-ctx-chip">策略 <b>${data.strategy || "—"}</b></span>`;
      html += `</div></div>`;

      // ── Per-stock explainable signals ──
      if (data.signals && data.signals.length > 0) {
        html += '<div class="advisor-signals">';
        for (const sig of data.signals) {
          const ac = sig.action || "hold";
          const acLabel = {buy:"买入",sell:"卖出",hold:"持有",reduce:"减仓",add:"加仓",watch:"观望"}[ac] || ac;
          const acCls = ac === "sell" || ac === "reduce" ? "ac-sell" : ac === "buy" || ac === "add" ? "ac-buy" : ac === "watch" ? "ac-watch" : "ac-hold";
          const bars = "█".repeat(sig.strength || 1) + "░".repeat(5 - (sig.strength || 1));

          html += `<div class="advisor-signal">`;
          // Header: ticker + action badge + strength
          html += `<div class="advisor-signal-head">`;
          html += `<span class="advisor-signal-name">${sig.name || sig.ticker}</span>`;
          html += `<span class="advisor-signal-action ${acCls}">${acLabel}</span>`;
          html += `<span class="advisor-signal-strength">${bars}</span>`;
          html += `</div>`;

          // Radar + Factor bars side by side
          const factors = sig.factors || [];
          if (factors.length > 0) {
            html += `<div class="advisor-explain">`;
            html += `<div class="advisor-radar-wrap">${renderRadarChart(factors)}</div>`;
            html += `<div class="advisor-factors">${factors.map(renderFactorBar).join("")}</div>`;
            html += `</div>`;
          }

          // Reasons
          if (sig.reasons && sig.reasons.length) {
            html += `<div class="advisor-signal-reasons">`;
            sig.reasons.forEach(r => {
              html += `<span class="advisor-reason-chip">${r}</span>`;
            });
            html += `</div>`;
          }

          // Stop/Take-profit + Save button
          html += `<div class="advisor-signal-footer">`;
          if (sig.stop_loss || sig.take_profit) {
            const parts = [];
            if (sig.stop_loss) parts.push(`止损 ¥${sig.stop_loss.toFixed(2)}`);
            if (sig.take_profit) parts.push(`止盈 ¥${sig.take_profit.toFixed(2)}`);
            html += `<span class="advisor-signal-prices">${parts.join(" | ")}</span>`;
          }
          html += `<button class="advisor-save-btn" data-sig='${JSON.stringify({ticker:sig.ticker,name:sig.name,action:sig.action,reasons:sig.reasons,factors:sig.factors||[]})}'>📋 记录决策</button>`;
          html += `</div>`;

          html += `</div>`;
        }
        html += '</div>';
      }

      body.innerHTML = html;

      // Bind save buttons
      body.querySelectorAll(".advisor-save-btn").forEach(b => {
        b.addEventListener("click", () => {
          const sig = JSON.parse(b.dataset.sig);
          saveToJournal(sig, riskPref, data.portfolio_action);
        });
      });

      status.textContent = data.generated_at ? `更新: ${data.generated_at.slice(11, 16)}` : "";
    } catch (e) {
      body.innerHTML = '<div class="advisor-empty">请求失败，请稍后重试</div>';
      status.textContent = "";
    } finally {
      btn.disabled = false;
    }
  }

  btn.addEventListener("click", loadAdvisor);
})();

// ── AutoDev Card (一键自动循环) ──────────────────────────────────────────────
(function() {
  const btn = document.getElementById("btn-autodev-run");
  const body = document.getElementById("autodev-body");
  const status = document.getElementById("autodev-status");
  const selStrategy = document.getElementById("autodev-strategy");
  const selRisk = document.getElementById("autodev-risk");
  if (!btn) return;

  async function runAutodev() {
    // Build positions from localStorage (same as advisor)
    const posMap = JSON.parse(localStorage.getItem("positions_v1") || "{}");
    const posArr = Object.entries(posMap)
      .filter(([, v]) => v && v.shares > 0 && v.cost > 0)
      .map(([ticker, v]) => ({ ticker, shares: v.shares, cost: v.cost }));

    if (posArr.length === 0) {
      body.innerHTML = '<div class="autodev-empty">暂无持仓数据。请先在股票卡片中设置持仓和成本。</div>';
      return;
    }

    status.textContent = "运行中…";
    btn.disabled = true;

    try {
      const resp = await fetch("/api/autodev/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          positions: posArr,
          strategy: selStrategy.value,
          risk_pref: selRisk.value,
        }),
      });
      const data = await resp.json();

      if (!data.ok) {
        body.innerHTML = `<div class="autodev-empty">${data.error || "运行失败"}</div>`;
        status.textContent = "";
        return;
      }

      let html = "";

      // ── Cycle summary banner ──
      const c = data.cycle || {};
      const ds = data.data_sources || {};
      html += `<div class="autodev-summary">`;
      html += `<div class="autodev-summary-row">`;
      html += `<span class="autodev-chip">策略 <b>${c.strategy || "—"}</b></span>`;
      html += `<span class="autodev-chip">风控 <b>${c.risk_pref || "—"}</b></span>`;
      html += `<span class="autodev-chip">市场 <b>${ds.regime || "—"}</b></span>`;
      html += `<span class="autodev-chip">情绪 <b>${ds.sentiment_stage || "—"}</b></span>`;
      html += `<span class="autodev-chip">风险 <b>${ds.risk_events_count || 0}</b>个</span>`;
      html += `</div>`;
      html += `<div class="autodev-pipeline">`;
      const steps = [
        { label: "观察", icon: "👁", count: c.positions_count ?? c.signals_count ?? "—" },
        { label: "决策", icon: "🧠", count: c.signals_count ?? "—" },
        { label: "执行", icon: "⚡", count: c.acted_count ?? 0 },
        { label: "评估", icon: "📊", count: c.evaluations_count ?? 0 },
        { label: "学习", icon: "💡", count: c.suggestions_count ?? 0 },
      ];
      steps.forEach((s, i) => {
        html += `<span class="autodev-step">${s.icon} ${s.label} <b>${s.count}</b></span>`;
        if (i < steps.length - 1) html += `<span class="autodev-arrow">→</span>`;
      });
      html += `</div></div>`;

      // ── Signals ──
      const signals = data.signals || [];
      if (signals.length > 0) {
        html += '<div class="autodev-signals">';
        for (const sig of signals) {
          const ac = sig.action || "hold";
          const acLabel = {buy:"买入",sell:"卖出",hold:"持有",reduce:"减仓",add:"加仓",watch:"观望"}[ac] || ac;
          const acCls = ac === "sell" || ac === "reduce" ? "ac-sell" : ac === "buy" || ac === "add" ? "ac-buy" : ac === "watch" ? "ac-watch" : "ac-hold";
          const bars = "█".repeat(sig.strength || 1) + "░".repeat(5 - (sig.strength || 1));

          html += `<div class="autodev-signal">`;
          html += `<span class="autodev-sig-name">${sig.name || sig.ticker}</span>`;
          html += `<span class="advisor-signal-action ${acCls}">${acLabel}</span>`;
          html += `<span class="autodev-sig-strength">${bars}</span>`;
          if (sig.reasons && sig.reasons.length) {
            html += `<span class="autodev-sig-reasons">${sig.reasons.join("；")}</span>`;
          }
          html += `</div>`;
        }
        html += '</div>';
      } else {
        html += '<div class="autodev-empty">无持仓信号</div>';
      }

      // ── Suggestions from learn() ──
      const suggestions = (data.analysis || {}).suggestions || [];
      if (suggestions.length > 0) {
        html += '<div class="autodev-suggestions">';
        html += '<div class="autodev-suggestions-title">💡 学习建议</div>';
        for (const sg of suggestions) {
          html += `<div class="autodev-suggestion">`;
          html += `<span class="autodev-sg-type">${sg.type}</span> `;
          html += `<span class="autodev-sg-reason">${sg.reason}</span>`;
          html += `</div>`;
        }
        html += '</div>';
      }

      body.innerHTML = html;
      status.textContent = c.observed_at ? c.observed_at.slice(11, 16) : "";
    } catch (e) {
      body.innerHTML = '<div class="autodev-empty">请求失败，请稍后重试</div>';
      status.textContent = "";
    } finally {
      btn.disabled = false;
    }
  }

  btn.addEventListener("click", runAutodev);

  // ── Show strategy picks (e.g. 分红标的池) when strategy has picks ──
  const picksDiv = document.getElementById("autodev-picks");
  async function updatePicks() {
    if (!picksDiv) return;
    try {
      const r = await fetch("/api/strategies");
      const d = await r.json();
      if (!d.ok) return;
      const strat = (d.strategies || []).find(s => s.name === selStrategy.value || s.file === selStrategy.value + ".yaml");
      if (strat && strat.picks && strat.picks.length > 0) {
        let h = '<table class="picks-table"><thead><tr><th>标的</th><th>股息率</th><th>买点</th><th>仓位</th><th>备注</th></tr></thead><tbody>';
        for (const p of strat.picks) {
          h += `<tr><td><b>${p.name}</b></td><td>${(p.dividend_yield * 100).toFixed(1)}%</td><td>${Number(p.entry).toFixed(2)}</td><td>${(p.position * 100).toFixed(0)}%</td><td class="picks-note">${p.note || ""}</td></tr>`;
        }
        h += '</tbody></table>';
        picksDiv.innerHTML = h;
        picksDiv.style.display = "";
      } else {
        picksDiv.style.display = "none";
        picksDiv.innerHTML = "";
      }
    } catch (e) { picksDiv.style.display = "none"; }
  }
  selStrategy.addEventListener("change", updatePicks);
  updatePicks();
})();

// ── 分红策略 Card (dedicated) ────────────────────────────────────────────────
(function() {
  const btn = document.getElementById("btn-dividend-run");
  const picksDiv = document.getElementById("dividend-picks");
  const body = document.getElementById("dividend-body");
  const status = document.getElementById("dividend-status");
  const selRisk = document.getElementById("dividend-risk");
  if (!btn || !picksDiv) return;

  function renderPicks(picks) {
    let h = '<table class="picks-table"><thead><tr><th>标的</th><th>股息率</th><th>买点</th><th>仓位</th><th>备注</th></tr></thead><tbody>';
    for (const p of picks) {
      h += `<tr><td><b>${p.name}</b></td><td>${(p.dividend_yield * 100).toFixed(1)}%</td><td>${Number(p.entry).toFixed(2)}</td><td>${(p.position * 100).toFixed(0)}%</td><td class="picks-note">${p.note || ""}</td></tr>`;
    }
    h += '</tbody></table>';
    picksDiv.innerHTML = h;
  }

  async function loadPicks() {
    try {
      const r = await fetch("/api/strategies");
      const d = await r.json();
      if (!d.ok) return;
      const strat = (d.strategies || []).find(s => s.file === "dividend.yaml");
      if (strat && strat.picks && strat.picks.length > 0) {
        renderPicks(strat.picks);
        body.innerHTML = '<div class="autodev-empty">点击「运行分红循环」评估标的池当前状态</div>';
      } else {
        picksDiv.innerHTML = '<div class="autodev-empty">未找到分红策略配置</div>';
      }
    } catch (e) {
      picksDiv.innerHTML = '<div class="autodev-empty">加载失败</div>';
    }
  }

  async function runDividend() {
    status.textContent = "运行中…";
    btn.disabled = true;
    try {
      // Use dividend picks as positions (entry as cost)
      const r1 = await fetch("/api/strategies");
      const d1 = await r1.json();
      const strat = (d1.strategies || []).find(s => s.file === "dividend.yaml");
      const picks = (strat && strat.picks) || [];
      if (picks.length === 0) { body.innerHTML = '<div class="autodev-empty">无分红标的</div>'; return; }

      const positions = picks.map(p => ({ ticker: p.ticker, name: p.name, shares: p.held ? 1000 : 0, cost: p.entry }));

      const resp = await fetch("/api/autodev/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ positions, strategy: "dividend", risk_pref: selRisk.value }),
      });
      const data = await resp.json();
      if (!data.ok) { body.innerHTML = `<div class="autodev-empty">${data.error || "运行失败"}</div>`; return; }

      let html = "";
      const signals = data.signals || [];
      if (signals.length > 0) {
        html += '<div class="autodev-signals">';
        for (const sig of signals) {
          const ac = sig.action || "hold";
          const acLabel = {buy:"买入",sell:"卖出",hold:"持有",reduce:"减仓",add:"加仓",watch:"观望"}[ac] || ac;
          const acCls = ac === "sell" || ac === "reduce" ? "ac-sell" : ac === "buy" || ac === "add" ? "ac-buy" : ac === "watch" ? "ac-watch" : "ac-hold";
          const bars = "█".repeat(sig.strength || 1) + "░".repeat(5 - (sig.strength || 1));
          html += `<div class="autodev-signal"><span class="autodev-sig-name">${sig.name || sig.ticker}</span>`;
          html += `<span class="advisor-signal-action ${acCls}">${acLabel}</span>`;
          html += `<span class="autodev-sig-strength">${bars}</span>`;
          if (sig.stop_loss) html += `<span class="picks-note">止损 ${sig.stop_loss}</span>`;
          if (sig.reasons && sig.reasons.length) html += `<span class="autodev-sig-reasons">${sig.reasons.join("；")}</span>`;
          html += `</div>`;
        }
        html += '</div>';
      } else {
        html += '<div class="autodev-empty">无信号</div>';
      }
      body.innerHTML = html;
      const c = data.cycle || {};
      status.textContent = c.observed_at ? c.observed_at.slice(11, 16) : "✓";
    } catch (e) {
      body.innerHTML = '<div class="autodev-empty">请求失败</div>';
      status.textContent = "";
    } finally {
      btn.disabled = false;
    }
  }

  btn.addEventListener("click", runDividend);
  loadPicks();
})();

// ── Horizontal scroll-hint management ────────────────────────────────────────
(function initScrollHints() {
  function updateHint(el) {
    const atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 2;
    el.classList.toggle("scrolled-end", atEnd);
  }
  // Monitor all .scroll-hint elements
  function bind(el) {
    el.addEventListener("scroll", () => updateHint(el), { passive: true });
    updateHint(el);
  }
  // Bind existing + watch for new ones via MutationObserver
  document.querySelectorAll(".scroll-hint").forEach(bind);
  new MutationObserver(muts => {
    muts.forEach(m => m.addedNodes.forEach(n => {
      if (n.nodeType === 1) {
        if (n.classList?.contains("scroll-hint")) bind(n);
        n.querySelectorAll?.(".scroll-hint").forEach(bind);
      }
    }));
  }).observe(document.body, { childList: true, subtree: true });

  // Re-check after content loads (tables render async)
  window.addEventListener("load", () => {
    document.querySelectorAll(".scroll-hint").forEach(updateHint);
  });
})();

// ── Boot: load all cards ─────────────────────────────────────────────────────
refreshAllCards();
