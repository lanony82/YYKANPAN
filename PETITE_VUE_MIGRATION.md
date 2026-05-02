# Petite-Vue 渐进迁移指南

## 当前状态（Phase 0.5 — 已完成）

已在 `index.html` 中引入 Petite-Vue 0.4.1 CDN 和全局 reactive store。
现有的 vanilla JS 代码完全不受影响，但已经开始向 `store` 写入数据。

```js
// 任何现有函数都可以写入 store，Petite-Vue 会自动响应
store.sentiment.stage = "上升";
store.stats.sentimentStage = "上升";
```

---

## Phase 1：声明式绑定（替换 .textContent / .innerHTML）

### 示例：情绪判断卡片输出区域

**迁移前（vanilla JS）：**
```html
<div class="insight-out" id="out-market-sentiment">输入数据后点击判断</div>
```
```js
document.getElementById("out-market-sentiment").textContent = `情绪阶段: ${data.stage}`;
```

**迁移后（Petite-Vue）：**
```html
<div class="insight-out" id="out-market-sentiment"
     v-scope="{ get store() { return _store } }">
  <template v-if="store.sentiment.stage">
    <div>更新时间: {{ store.sentiment.updatedAt }}</div>
    <div>情绪阶段: <strong>{{ store.sentiment.stage }}</strong></div>
    <div>是否适合交易: {{ store.sentiment.tradable }}</div>
    <div style="margin-top:6px">理由:</div>
    <div v-for="r in store.sentiment.reasons">- {{ r }}</div>
    <div style="margin-top:6px">人话结论:</div>
    <div>{{ store.sentiment.plain }}</div>
  </template>
  <template v-else>
    <span v-if="store.sentiment.loading">自动抓取中...</span>
    <span v-else>输入上涨/下跌/涨停/连板数据后点击判断</span>
  </template>
</div>
```

关键改动：
1. HTML 加 `v-scope` — Petite-Vue 会接管这个 DOM 区域
2. 移除 JS 中的 `outEl.textContent = ...` 赋值
3. `renderMarketSentiment()` 只需写 `store.sentiment.xxx = value`

### 迁移步骤

1. 在目标元素上加 `v-scope`
2. 用 `{{ }}` / `v-text` 替换 `.textContent`
3. 用 `v-for` 替换 `.innerHTML` 拼接
4. 用 `v-if` / `v-show` 替换 `.style.display = "none"`
5. 保留 `addEventListener` 不变（或后续用 `@click`）
6. **删除对应的 `getElementById + .textContent = ...` 行**

---

## Phase 2：组件封装

将每张卡片抽成函数组件 + `<template>` 模板：

```html
<!-- 模板放在 body 底部 -->
<template id="tpl-sentiment-card">
  <div class="insight-card" data-card-id="sentiment" draggable="true">
    <h3>
      <span class="drag-handle">⠇</span> A股情绪判断
      <button class="card-collapse" @click="toggleCollapse">{{ collapsed ? '+' : '−' }}</button>
      <button class="card-close" @click="hide">✕</button>
    </h3>
    <!-- inputs, buttons, output all here with v-model / @click -->
  </div>
</template>

<script>
function SentimentCard() {
  return {
    $template: '#tpl-sentiment-card',
    collapsed: false,
    toggleCollapse() { this.collapsed = !this.collapsed; },
    hide() { /* ... */ },
    async judge() {
      store.sentiment.loading = true;
      const res = await fetch("/api/market-sentiment-auto");
      const data = await res.json();
      Object.assign(store.sentiment, { stage: data.stage, ... });
      store.sentiment.loading = false;
    }
  };
}
</script>
```

### 建议的迁移顺序

| 优先级 | 卡片 | 理由 |
|--------|------|------|
| 1 | 情绪判断 | 数据绑定多，收益最大 |
| 2 | 行情概览 (stats) | 大量 `.textContent` 赋值 |
| 3 | Watchdog | 状态灯 + 输出区域 |
| 4 | 涨跌停 | 简单输出 |
| 5 | AI 策略 / 主线 / 简报 | 纯展示，最后迁移 |

---

## Phase 3：模块化分离（当 index.html > 3000 行时）

```
static/
  index.html          ← 只保留 HTML 骨架 + <script type="module">
  js/
    store.js          ← reactive store 定义
    api.js            ← 所有 fetch 封装
    components/
      sentiment.js    ← 情绪卡片组件
      watchdog.js     ← Watchdog 组件
      stats.js        ← 行情概览组件
    utils.js          ← fmtNum, fmtVol, cls 等
```

```html
<!-- index.html -->
<script type="module">
  import { store } from './js/store.js';
  import { SentimentCard } from './js/components/sentiment.js';
  // ...
  PetiteVue.createApp({ store, SentimentCard }).mount('#app');
</script>
```

---

## 注意事项

- **不要急着删除 `getElementById`**：Phase 1 中 vanilla JS 和 Petite-Vue 可以共存
- **性能**：Petite-Vue 的响应式更新粒度比手动 DOM 操作大，A 股行情的 60 秒刷新完全没问题
- **sparkline / SVG 图表**：保留原生 JS 渲染，不需要迁移到 Petite-Vue
- **拖拽排序**：继续使用原生 Drag API，不受 Petite-Vue 影响
- **localStorage 持久化**：可以用 `watch` 或在 store setter 中同步
