# 五套模板的架构组件

选定模板后只读对应小节。通用结构（`.grid` / `.u-*` / `.stack` / `.band`）见 [`block-library.md`](block-library.md)。

**硬规则**：每套必须用自己的一组组件（少于 3 个报 ERROR），**不得借用别套的组件**（借用也报 ERROR）。

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
