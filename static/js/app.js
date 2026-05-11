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

// ── Refresh button ────────────────────────────────────────────────────────────
document.getElementById("btn-refresh").addEventListener("click", loadStocks);
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

async function loadMacro() {
  const bar = document.getElementById("macro-bar");
  if (!bar) return;
  try {
    const res = await fetch("/api/macro");
    const data = await res.json();
    if (!data.length) { bar.innerHTML = '<span class="macro-loading">暂无数据</span>'; return; }
    bar.innerHTML = data.map(d => {
      const dir = d.change_pct > 0 ? "up" : d.change_pct < 0 ? "down" : "flat";
      const arrow = d.change_pct > 0 ? "▲" : d.change_pct < 0 ? "▼" : "—";
      const sign = d.change > 0 ? "+" : "";
      return `<div class="macro-chip">
        <span class="macro-name">${d.name}</span>
        <span class="macro-price">${d.price}<span class="macro-unit">${d.unit || ""}</span></span>
        <span class="macro-change ${dir}">${arrow} ${sign}${d.change} (${sign}${d.change_pct}%)</span>
      </div>`;
    }).join("");
  } catch (_) {
    bar.innerHTML = '<span class="macro-loading">获取失败</span>';
  }
}
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
    list.innerHTML = d.events.map(e => `
      <div class="risk-event severity-${e.severity}">
        <span class="risk-badge type-${e.type}">${e.type}</span>
        <div class="risk-body">
          <div class="risk-title">${e.title}</div>
          <div class="risk-detail">${e.detail}</div>
        </div>
        <span class="risk-time">${e.time}</span>
      </div>
    `).join("");
  } catch (_) {
    list.innerHTML = '<div class="risk-empty">获取失败</div>';
  }
}
document.getElementById("btn-risk-refresh")?.addEventListener("click", loadRiskEvents);
document.getElementById("sel-risk-period")?.addEventListener("change", loadRiskEvents);
loadRiskEvents();

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

  const stageColors = { [I.stage_rising]: "var(--up)", [I.stage_ebbing]: "var(--down)", [I.stage_divergence]: "var(--muted)" };

  // Build points
  const pts = history.map((e, i) => {
    const x = padL + (i / Math.max(history.length - 1, 1)) * plotW;
    const y = padT + (1 - (e.score - minS) / range) * plotH;
    return { x, y, ...e };
  });

  const polyline = pts.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");

  // Stage background bands
  let bands = "";
  let bandStart = 0;
  let bandStage = pts[0]?.stage;
  for (let i = 1; i <= pts.length; i++) {
    const cur = i < pts.length ? pts[i].stage : null;
    if (cur !== bandStage || i === pts.length) {
      const x1 = pts[bandStart].x;
      const x2 = pts[Math.min(i, pts.length - 1)].x;
      const color = stageColors[bandStage] || "var(--muted)";
      bands += `<rect x="${x1}" y="${padT}" width="${Math.max(x2 - x1, 2)}" height="${plotH}" fill="${color}" opacity="0.07"/>`;
      bandStart = i;
      bandStage = cur;
    }
  }

  // Zero line
  const zeroY = padT + (1 - (0 - minS) / range) * plotH;

  // X-axis date labels (show a few)
  let xLabels = "";
  const step = Math.max(1, Math.floor(history.length / 5));
  for (let i = 0; i < history.length; i += step) {
    const p = pts[i];
    const label = (p.ts || "").slice(5, 10); // "MM-DD"
    xLabels += `<text x="${p.x}" y="${h - 2}" text-anchor="middle" fill="var(--muted)" font-size="9">${label}</text>`;
  }

  // Dots with stage color
  const dots = pts.map(p => {
    const c = stageColors[p.stage] || "var(--muted)";
    return `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3" fill="${c}" stroke="var(--bg)" stroke-width="1">
      <title>${(p.ts||"").slice(0,16)} ${I.lbl_score}:${p.score} ${p.stage}</title>
    </circle>`;
  }).join("");

  // Y-axis labels
  const yLabels = [maxS, 0, minS].map(v => {
    const y = padT + (1 - (v - minS) / range) * plotH;
    return `<text x="${padL - 4}" y="${y + 3}" text-anchor="end" fill="var(--muted)" font-size="9">${v}</text>`;
  }).join("");

  container.innerHTML = `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="display:block">
    ${bands}
    <line x1="${padL}" y1="${zeroY}" x2="${w - padR}" y2="${zeroY}" stroke="var(--border)" stroke-dasharray="3,3" stroke-width="0.5"/>
    <polyline points="${polyline}" fill="none" stroke="var(--accent)" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>
    ${dots}
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
    mainline: I.card_mainline, brief: I.card_brief, "invest-tip": I.card_invest_tip
  };
  const wrap = document.getElementById("insight-wrap");
  const bar = document.getElementById("restore-bar");

  function getHidden() {
    try { return JSON.parse(localStorage.getItem(HIDDEN_KEY)) || []; } catch { return []; }
  }
  function setHidden(arr) { localStorage.setItem(HIDDEN_KEY, JSON.stringify(arr)); }

  function hideCard(id) {
    const card = wrap.querySelector(`.insight-card[data-card-id="${id}"]`);
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

// Load watchlist stocks first, then kick off heavier market-wide endpoints
loadStocks().then(() => {
  generateAutoBrief(false);
  refreshMarketSentimentAuto();
  loadSentimentChart();
  refreshMainlineAuto();
  refreshAiEdge(false);
  refreshLimitStats();
});
