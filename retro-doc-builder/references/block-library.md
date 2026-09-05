# 结构库

13 种信息类型对应 13 种视觉结构。**先判类型，再取结构**；同一类型在全文只用同一种结构。

**本文件的 class 名必须与 `../assets/base.css` 完全一致**——写之前先扫一眼那个文件，不要凭记忆写 class。

## 每个块的完整外壳

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
<style>
/* 整段粘贴 ../assets/base.css */
</style>
</head>
<body>
【结构主体】
</body>
</html>
```

`base.css` 必须整段内联，不能用 `<link>`。

---

## 1. 块报头 → `.hero`

每块必备，全块最高层级。**白底 + 顶部 3px 近黑线 + 巨型浅灰序号**，不是实底色块。

```html
<div class="hero">
  <div class="no">02</div>
  <div>
    <span class="kicker">【这一块回答什么 · 用 · 分隔】</span>
    <h1>【一句话主张，32px 承担视觉重量】</h1>
    <p class="dek">【补充说明，≤42em】</p>
  </div>
</div>
```

`.kicker` 是彩色点缀之一（克莱因蓝亮档）。序号用 `--line-2` 浅灰，靠尺寸而非颜色抢眼。

## 2. 摘要网格 → `.bento` + 尺寸编码

**核心规则：至少一个单元跨列更大。** 全等分会被检查器警告——那只是普通卡片墙。

```html
<div class="bento">
  <div class="cell c2 r2">
    <span class="lb">五条信号</span>
    <span class="fig">5<em>条</em></span>
    <p>【口径说明】</p>
    <div class="seg push"><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i></div>
    <p class="push"><b>本例：</b>【逐项对照结论】</p>
  </div>
  <div class="cell-hd c2">
    <span class="lb">六件前提</span>
    <span class="fig">6<em>项</em></span>
    <p>【硬门槛说明】</p>
  </div>
  <div class="cell-acc c1">
    <span class="lb">劝退</span>
    <span class="fig acc">4<em>条</em></span>
    <p>【命中即劝退】</p>
  </div>
  <div class="cell c1">
    <span class="lb">本例压线</span>
    <span class="fig">2<em>项</em></span>
    <p>【后来出了什么问题】</p>
  </div>
</div>
```

列宽：`.c1` / `.c2` / `.c3` / `.c4`（通栏）；`.r2` 跨两行，配 `.push` 把内容推到底部。

## 3. 卡面四档 → 靠顶线，不靠填色

| 档 | class | 视觉 | 用途 |
|---|---|---|---|
| 结构必备 | `.cell-hd` | 白底 + 顶部 3px 近黑条 | 硬门槛、总闸 |
| 警示 | `.cell-acc` | 白底 + 顶部 3px 克莱因蓝条 | 劝退、致命项 |
| 常规 | `.cell` | 白底 + 1px 描边 | 主体内容 |
| 安静 | `.cell-q` | 极浅灰底 + 1px 描边 | 成组但不抢视线 |
| 焦点 | `.fill` | 近黑实底 + 白字 | 与 `.mark` 合计**最多 1 处** |

顶线由 `::before` 画，**不要改成 `border-top`**——粗线配圆角会在上角长出斜接翘角。

## 4. 竖排条目组 → `.stack`

用于 N 条并列条目。与网格形成密度反差，**不要连着放两个 `.bento`**。

```html
<div class="sec"><span class="pill">信号</span><small>【一句话定位】</small></div>
<div class="stack">
  <div class="row">
    <div class="n">01</div>
    <div>
      <div class="ct">【条目标题】</div>
      <p>【说明】</p>
    </div>
  </div>
</div>
```

## 5. 小节标题 → `.sec`

**文字 + 底线，不是药丸色块。**

```html
<div class="sec"><span class="pill">前提</span><small>【补充】</small></div>
<div class="sec acc"><span class="pill">劝退</span><small>【补充】</small></div>
```

`.sec.acc` 底线与文字转克莱因蓝，用于警示段。

## 6. 全块唯一爆点 → `.mark`

**整块只允许一次**（且与 `.fill` 合计不超过 1 处），留给最值得记住的那句。

```html
<div class="mark">
  <div class="big">【最该被背下来的一句】</div>
  <p>【它为什么成为判断依据】</p>
</div>
```

## 7. 关键指标 → `.fig`

**数字必须来自素材，不得估算。**

```html
<span class="lb">【指标名 · 单位口径】</span>
<span class="fig">5<em>条</em></span>
<span class="fig sm">45′ → 5′</span>
<span class="fig acc">4<em>条</em></span>
```

`.fig` 44px，`.fig.sm` 27px 用于含箭头或中文的长值，`<em>` 装单位自动降为 17px。`.fig.acc` 是彩色点缀，**整块最多一个数字**用它。

## 8. 多维对比 → 表格

只有横向发丝线，表头无底色，首列自动加粗不换行。

```html
<div class="sec"><span class="pill">本例对照</span><small>【背景】</small></div>
<table>
  <thead><tr><th>项</th><th>本例情况</th><th>结果</th></tr></thead>
  <tbody>
    <tr><td>决策窗口</td><td>次月中完成选型</td><td>扎实满足</td></tr>
    <tr><td>试用包</td><td>卡得太紧</td><td><b class="flag">压线</b>，几乎没有缓冲</td></tr>
  </tbody>
</table>
```

## 9. 行内警示标记 → `.flag`

```html
<p class="flag">本例压线：会前一天才生效</p>
<b class="flag">压线</b>
```

克莱因蓝亮档 + 700 字重。**base.css 里写成 `.bento p.flag, p.flag, .flag`**——低特异性会被 `.bento p` 吃掉，改的时候别删掉前缀。

## 10. 核对清单 → `ul.check`

方框由 `li::before` 画，**不用 `<input>`**。

```html
<div class="cell c2">
  <span class="lb">客户侧要落实</span>
  <ul class="check">
    <li>【动作】</li>
    <li>【动作】（<b>关键约束</b>）</li>
  </ul>
</div>
```

## 11. 原声引用 → `.quote`

上下双线（上 2px 近黑 / 下 1px 浅灰），19px 600 字重。**不要加引号字符**——双线已承担引用语义。

```html
<div class="quote">【原话，关键句用 <b> 加粗】<span class="attr">出处</span></div>
```

## 12. 进度 / 分段条 → `.bar` / `.seg`

灰底黑条，**不用彩色**。

```html
<div class="bar"><i style="width:66%"></i></div>
<div class="seg"><i class="on"></i><i class="on"></i><i></i></div>
```

## 13. 脚注收口 → `.foot`

```html
<div class="foot"><b>体会：</b>【一句话总结，或口径预防针】</div>
```

---

## 组合规则

- 一个块可容纳 2–3 种结构，但必须服务同一个问题
- 块内顺序：`.hero` → `.bento` → `.sec` + `.stack` → `.mark` → `.sec` + `.bento` → 表格 → `.foot`
- **相邻区块不得同高**：网格 ↔ 竖排 ↔ 实底带交替
- 多列在 640px 自动塌两列、440px 塌单列，无需另写
- **每块必须有且只有一个视觉重心**：`.fig` 巨数 / `.mark` 实底带 / `.quote` 大引语，三者选一。都没有 → 平；都有 → 乱
