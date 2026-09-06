# 结构库（v7）

13 种信息类型对应 13 种视觉结构。**先判类型，再取结构**；同一类型在全文只用同一种结构。

所有 class 均以 `assets/base.css` 为准，本文件已逐个核对。

## 块的完整外壳

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="use-iframe" content="true">
<meta name="html-box-height-mode" content="auto">
<meta name="description" content="【与 alt 同一句完整语义描述】">
<title>【4-6 字块名】</title>
<style>/* 整段粘贴 assets/base.css */</style>
</head>
<body class="t-modern">
【结构主体，由若干 .band 通栏模块组成】
</body>
</html>
```

两件必须做对：

1. `base.css` **整段内联**，不能用 `<link>`
2. `<body>` **必须挂主题类**：`t-modern` / `t-swiss` / `t-editorial` / `t-gallery` / `t-mono`。缺了 token 落回默认值，检查器会 ERROR

---

## 0. 通栏模块：一切内容的容器

**这是 v7 的骨架。** 内容不再装进卡片，而是装进通栏模块；模块之间靠底色变化分隔，不画边框。

```html
<div class="band">        <!-- 白底，默认 -->
<div class="band alt">    <!-- 浅底，换底色 = 换段落 -->
<div class="band ink">    <!-- 深底反白，整块最多 1 处 -->
<div class="band tight">  <!-- 呼吸量减半，用于紧接的两段 -->
```

**不要连续两个同底色的 `.band`**——那等于没分隔。白 → 浅 → 白 → 浅 交替。

三种分隔手段，按优先级：纯留白（`.band` 自带）> 细横线（`.rule`）> 通栏换底色（`.band.alt`）。

```html
<hr class="rule">              <!-- 1px 细横线 -->
<hr class="rule short">        <!-- 56px 短线 -->
<hr class="rule key">          <!-- 56px 核心色短线 -->
<hr class="rule strong">       <!-- 2px 近黑线 -->
```

## 1. 块报头（每块必备）

巨型序号 + 三段式，**左对齐**。

```html
<div class="hero">
  <div class="no">02</div>
  <div>
    <span class="kicker">【章节定位 · 这一块回答什么】</span>
    <h1>【一句话主张，承担视觉重量】</h1>
    <p class="dek">【补充说明，17px，比正文大一档】</p>
  </div>
</div>
```

`t-swiss` 会自动把报头变成不对称三列（右侧留一整列空白）；`t-gallery` 会改成序号独占一行。**不需要为不同主题改 HTML。**

## 2. 并列同权 → 开放网格

用于 N 条经验、N 个要点。**无边框、无阴影，单元之间只有空气。**

```html
<div class="grid">
  <div class="u-t c2">
    <span class="lb">标签</span>
    <div class="ct">【要点标题】</div>
    <p>【说明】</p>
  </div>
  <div class="u-t c2">…</div>
</div>
```

跨列：`.c1` `.c2` `.c3` `.c4`（`.c4` = 通栏）。**至少要有一个单元比其他更大**——全等分等于普通卡片墙，检查器会警告。

单元五档，轻重靠顶线：

| class | 视觉 | 用途 |
|---|---|---|
| `.u` | 只有留白 | 最轻 |
| `.u-t` | 顶部 1px 细线 | 主体内容 |
| `.u-h` | 顶部 2px 近黑线（`.c4` 时 3px） | 硬门槛、总闸 |
| `.u-k` | 顶部 2px 核心色线 | 劝退、致命项 |
| `.u-q` | 极浅底 + 微圆角，无边框 | 成组但不抢视线 |

## 3. 二元对照 → 顶线分档

用于做/不做、扎实/压线、必备/可选。**不用两种颜色，用两种顶线。**

```html
<div class="grid">
  <div class="u-h c2">
    <span class="lb">必须满足</span>
    <div class="ct">【要点】</div>
    <p>【说明】</p>
  </div>
  <div class="u-k c2">
    <span class="lb">建议先别做</span>
    <div class="ct">【要点】</div>
    <p>【说明】</p>
  </div>
</div>
```

## 4. 关键指标 → 巨大数字

**数字必须来自素材，不得估算。**

```html
<div class="grid">
  <div class="u-h c2">
    <span class="lb">指标名 · 单位口径</span>
    <span class="fig">5<em>条</em></span>
    <p>【口径说明】</p>
    <div class="seg"><i class="on"></i><i class="on"></i><i class="on"></i><i></i><i></i></div>
    <p><b>本例：3/5</b>　【怎么得出的】</p>
  </div>
  <div class="u-k c1">
    <span class="lb">劝退</span>
    <span class="fig key">4<em>条</em></span>
    <p>【说明】</p>
  </div>
</div>
```

- `.fig` 52px，`.fig.sm` 30px 用于含箭头或中文的长值
- `.fig.key` 用核心色，**整块最多一个数字用它**
- `<em>` 装单位，自动降为 17px
- `.seg` 是 1px 发丝刻度线，不是色块。`<i class="on">` 表示已达成

## 5. 竖排条目 → 细横线列表

用于时序、分层递进、固定流程、N 条清单。**与网格形成密度反差。**

```html
<div class="stack">
  <div class="row"><div class="n">01</div><div>
    <div class="ct">【条目标题】</div>
    <p>【说明】</p>
  </div></div>
  <div class="row"><div class="n">02</div><div>…</div></div>
</div>
```

`.n` 放序号、时刻（`09:00`）或层级名，自动等宽对齐。`t-editorial` 会把序号放大到 24px。

## 6. 多维对比 → 表格

只有横向发丝线，无竖线无斑马纹。表头无底色。

```html
<table>
  <thead><tr><th>维度</th><th>本例情况</th><th>结果</th></tr></thead>
  <tbody>
    <tr><td>决策窗口</td><td>次月中完成选型</td><td>扎实满足</td></tr>
    <tr><td>试用包</td><td>会前一天才生效</td><td><b class="flag">压线</b>，几乎没有缓冲</td></tr>
  </tbody>
</table>
```

首列自动加粗且不换行，适合放维度名。`.flag` 是核心色行内标记。

## 7. 核对清单 → 假复选框

方框由 1px 线画出，**不用 `<input>`**。

```html
<div class="u-q c2">
  <span class="lb">客户侧要落实</span>
  <ul class="check">
    <li>【动作】</li>
    <li>【动作】（<b>关键约束</b>）</li>
  </ul>
</div>
```

## 8. 原声引用 → 上下双线

**必须可溯源**，`.attr` 写出处。

```html
<div class="quote">【原话，关键句用 <b> 标】<span class="attr">出处</span></div>
```

不要加引号字符——上下双线已经承担了引用语义。

## 9. 全文唯一爆点 → 深底反白

**全块只允许出现一次**，留给最值得记住的那一句。出现两次就都不突出了。

```html
<div class="mark">
  <div class="big">【最值得记住的一句】</div>
  <p>【它为什么成为记忆点】</p>
</div>
```

`t-editorial` 与 `t-gallery` 会自动把它变成「上下线 + 无底色」的版本，避免深色块打断长文阅读。

## 10. 小节标题

```html
<div class="sec"><span class="pill">信号</span><small>【一句话定位】</small></div>
<div class="sec key"><span class="pill">劝退</span><small>【一句话定位】</small></div>
```

`.sec.key` 把下划线换成核心色。**不要用色块药丸**。

## 11. 脚注 / 口径声明

```html
<div class="foot"><b>体会：</b>【口径、限制、来源说明】</div>
```

## 12. 实底强调单元

```html
<div class="fill c2">
  <span class="lb">标签</span>
  <div class="ct">【标题】</div>
  <p>【说明】</p>
</div>
```

**`.fill` 与 `.mark` 与 `.band.ink` 合计整块最多 1 处**，检查器会 ERROR。

---

## 组合规则

- 一个块由 3–6 个 `.band` 组成，底色交替
- 块内层级：`.band > .hero` → `.band > .sec + 结构` → `.band > .foot`
- 多列一律 `.grid` + `.c1`~`.c4`，640px 自动塌两列、440px 塌单列，无需另写
- **相邻区块不得同高**：开放网格 ↔ 竖排 `.stack` ↔ 深底 `.mark` 交替

## 节奏配方

```
.band          报头
.band          开放网格（1 个跨列主单元 + 2–3 个小单元）
.band.alt      竖排条目
.band          .mark 焦点带 + 主次混合网格
.band.alt      次要网格（.u-t 轻档）
.band          表格 / .foot 收口
```

---

# 五套模板各自的架构组件

**上面的通用结构（`.grid` / `.u-*` / `.stack` / `.band`）仍可用**，但五套模板各有自己的一组架构组件，决定整页怎么组织。**不要混用**——检查器会拦。

## t-swiss｜海报式 12 栏网格

```html
<div class="poster">
  <div class="pno">02</div>                    <!-- 150px 序号，占 1–4 栏 -->
  <div class="pkick">眉题</div>                 <!-- 4–11 栏，下方一条黑线 -->
  <h1>标题</h1>
  <p class="pdek">导语</p>
</div>

<ul class="gwall">                              <!-- 数据按栏位落位 -->
  <li class="w6 lead"><span class="gk">标签</span>
    <span class="gv">5<em>条</em></span><p>说明</p></li>
  <li class="warn"><span class="gk">劝退</span>
    <span class="gv warn">4<em>条</em></span><p>说明</p></li>
</ul>

<div class="sbar"><b>信号</b><span>副标</span></div>   <!-- 实心黑条反白字 -->
<ul class="hang">                                     <!-- 序号进左栏槽 -->
  <li><div class="hn">01</div><div class="hb"><b>标题</b><p>正文</p></div></li>
</ul>
```

`li` 宽度：默认 `span 3`，`.w4` / `.w6` 加宽；`.lead` 加粗左线，`.warn` 用核心色左线。

## t-editorial｜报纸头版

```html
<div class="mast"><span class="mt">栏目</span><span>第二章</span><span>眉题</span></div>
<div class="lede">
  <h1>56px 大标题</h1>
  <p class="sub">导语，首字自动下沉</p>          <!-- ::first-letter 浮左 -->
</div>
<div class="pullq">抽言<small>补充</small></div>  <!-- 打断栏流 -->

<div class="flow">                                <!-- 三栏正文流 + 栏间竖线 -->
  <div class="grp"><h3><i>01</i>标题</h3><p>正文</p></div>
</div>

<div class="withbar">                             <!-- 正文 + 300px 边栏 -->
  <div><div class="bar-h">主区标题</div>…</div>
  <div><div class="bar-h">边栏标题</div>
    <ul class="barlist"><li class="gate"><b>标题</b><p>正文</p></li></ul></div>
</div>
```

`.flow` 想改两栏：`style="column-count:2"`。

## t-gallery｜展览动线

```html
<div class="walk">
  <div class="plate wide">                        <!-- 通栏展签 -->
    <div class="idx">第二章</div>
    <p class="art">展品正文，31px 细字</p>
    <p class="note">说明</p>
    <div class="cap"><span class="cn">标签</span></div>   <!-- 标签在下方 -->
  </div>
</div>
<div class="walk pair">                            <!-- 成对并置，避免 20 屏 -->
  <div class="plate">…</div>
  <div class="plate">…</div>
</div>

<div class="vitrine">                              <!-- 数字陈列 -->
  <div><div class="vv">5<em>条</em></div><div class="vk">信号</div></div>
</div>
```

## t-modern｜产品页 tile 序列

```html
<div class="tile">                                 <!-- 一屏一个信息 -->
  <div class="no">第二章</div>
  <div class="eyebrow">眉题</div>
  <h2>标题</h2>
  <p class="say long">正文，long 表示左对齐</p>
</div>
<div class="tile alt">…</div>                      <!-- 浅底，底色变化即分隔 -->
<div class="tile dark">…</div>                     <!-- 深底焦点，整块 1 处 -->

<div class="statrow">                              <!-- 一排大数字 -->
  <div><div class="sv">5<em>条</em></div><div class="sk">信号</div></div>
</div>
<div class="pills"><span class="on">决策窗口</span></div>
<div class="feats"><div><b>标题</b><p>正文</p></div></div>
```

## t-mono｜终端记录卡

```html
<div class="rec">
  <div class="rh"><span>REC · 02 标题</span><i>副标</i></div>
  <div class="rb">
    <dl class="kv">                                <!-- 字段名值对齐 -->
      <dt class="gate">高层支持</dt><dd>值</dd>     <!-- gate 加 ▸ 前缀 -->
      <dt class="warn">账号 T-2</dt><dd>值</dd>
    </dl>
  </div>
</div>

<div class="readout">                              <!-- 关键读数 -->
  <div><div class="rv">5</div><div class="rk">信号 条</div>
    <div class="gauge"><b>▪▪▪▪▪</b>··</div></div>   <!-- 字符刻度 -->
</div>

<ul class="entries">
  <li><div class="en">S01</div><div><b>标题</b><p>正文</p></div></li>
</ul>
```
