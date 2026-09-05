# 飞书 HTML5 Block 写入

## 文档里长什么样

正文 XML 中每个块只是一个占位节点，真实内容在独立 HTML 文件：

```xml
<html5-block id="doxcnXXXX"
             alt="这场 Workshop 到底在做什么：想做成什么样——一天动手做出成果；
                  它不做什么——不是功能培训、不是完整 POC、不替代签约交付"
             data-ref="html5_1"></html5-block>
```

## alt 是降级文本层，不是标题

**`alt` 必须是完整语义描述，不是"图1"或块名。** 大纲视图、全文搜索、AI 读取、无障碍、导出场景全都读不到 HTML，只能读 `alt`。

```
✅ alt="怎么判断一个客户能不能做：五个适合做的信号、六件要先备齐的前提、四种建议先别做的情况"
❌ alt="判断框架"
❌ alt="图4"
```

判据：**只看 alt 能不能知道这块讲了什么、有几个部分。** 不能就重写。

`alt` 与 `<meta name="description">` 写同一句。

## meta 头三行必须有

```html
<meta name="use-iframe" content="true">           <!-- 沙箱渲染，样式不污染宿主文档 -->
<meta name="html-box-height-mode" content="auto">  <!-- 高度自适应，不出内部滚动条 -->
<meta name="description" content="【同 alt】">
```

缺 `use-iframe` 会让块内 CSS 泄漏到文档；缺 `height-mode` 会出现块内滚动条。

## 每块自包含

`base.css` 整段内联进 `<style>`，**不要用 `<link rel="stylesheet">`**——块之间不共享文件系统。

代价是每个块各带一份约 10KB CSS。这是刻意取舍：换来任何环境都能独立渲染。

## 硬约束（写之前就要满足，不是写完再改）

来自飞书官方 `html5-block` 规格，本地 Chrome 里看不出来，只有写进文档才暴露：

| 约束 | 值 | 违反后果 |
|---|---|---|
| 文档正文可用宽度 | **约 820px** | 按 1000px+ 设计会溢出或右侧留白 |
| 根容器宽度 | 只能 `100%` / `max-width:100%` | 写死 px 会横向溢出 |
| `box-sizing` | 必须 `border-box` | padding 会把元素撑出容器 |
| HTML 总长度 | **上限 500KB** | 超限写入失败 |
| `height-mode` | 只能 `auto` 或 `viewport` | 其他值行为未定义 |
| `auto` 模式下根容器 | 不得设固定 `height` / `overflow:hidden` | 正文被截断 |

**820px 是最主要的真实场景，设计和验收都以它为准**，不要只在 1000px 下看着满意就交付。`base.css` 已含 880 / 640 / 440px 三档断点，880px 这档专门照顾飞书正文宽度。

上述约束已全部写进 `check_blocks.py`，交付前跑一次即可拦住。

## 写正文 XML 的四个坑（都是实际踩出来的）

这四条在 `parse` 阶段**不一定报错**，但会让成品可见地坏掉：

| 坑 | 错误写法 | 正确写法 |
|---|---|---|
| `@path` 基准 | `path="@./block.html"`（以为相对草稿目录） | `path="@./<work_dir>/block.html"`——**以运行 lark-cli 的 CWD 为基准**，不是草稿文件所在目录 |
| 加粗标签 | `<text-bold>重点</text-bold>` | `<b>重点</b>`——`text-bold` 不在 schema 内，会被<text-bold>转义成字面文本</text-bold>显示给读者 |
| callout 图标 | `emoji-id="lock"` | `emoji="🔒"`——`emoji-id` 不在 schema 内，静默丢弃 |
| 文档标题 | 只写 `<h1>` | 必须有唯一 `<title>`；缺了文档显示为「Untitled」。且 `<title>` 与 `<h1>` 内容重复时应删掉 `<h1>` |

**`@path` 那条最隐蔽**：`parse` 会明确报 `resource_preflight_failed`，属于好拦；但另外三条只在 `+create` 的 `warnings[]` 里出现，`ok:true` 照样返回。**所以 `+create` 返回后必须逐条读 `warnings`，不能只看 `ok`。**

修复已创建文档时，用 `docs +update --command str_replace` 对标签本身做替换（`--pattern "<text-bold>" --content ""`），一次清一种标记；**不要重新建一个文档**。

## 写入流程

1. 读 `lark-doc` skill 的 `SKILL.md`，按 online-doc 分支路由；从零创作走创建工作流
2. 提交 Presentation Decision → `init-draft`，记下返回的 `work_dir` 与 `draft_path`
3. 把每个块的 HTML 存进 `work_dir`，正文 XML 用 `<html5-block path="@./<work_dir>/xxx.html"/>` 引用
4. `lark-cli docs +script --command parse` 校验草稿，看 `data.assessment.status`
5. `lark-cli docs +create --doc-format xml --content "@./<draft_path>"` 创建
6. **逐条读返回的 `warnings[]`**，有降级就按上一节的 `str_replace` 局部修复
7. `lark-cli docs +fetch --doc <URL> --detail full` 回读校验

**回读校验不可省。** 写入成功不等于渲染正确，`+fetch` 是与写入路径不同的验证通道。回读时逐项确认：块数量对得上 · 每块 `alt` 非空且是完整句 · 正文没有字面标签残留。

## 正文该留什么

| 留正文 | 理由 |
|---|---|
| 顶部密级 callout | 边界声明，要显眼且随时可改 |
| 导读 callout | 不同读者怎么读 |
| 后续进展 / 商机动态 | 每周都变，进 HTML 每次都要重出整块 |
| 材料索引 | 用 `<cite>` 文档卡片，链接会增删 |
| 议程取舍的解释 | 需要论证语气，卡片装不下 |
| 第五章开头的口径预防针 | 必须在数据之前被读到 |

## 常见故障

| 现象 | 原因 | 解法 |
|---|---|---|
| 块内出现滚动条 | 缺 `height-mode=auto` | 补 meta |
| 文档其他部分样式错乱 | 缺 `use-iframe=true` | 补 meta |
| 大纲/搜索里块是空白 | `alt` 为空或只写了块名 | 重写 `alt` 为完整语义句 |
| 块渲染成空白 | CSS 用了 `<link>` 外链 | 改为内联 `<style>` |
| 移动端多列挤在一起 | 缺 `@media(max-width:640px)` | base.css 已含，确认没被删 |
| 右侧被切 / 出现横向滚动 | 按 >820px 设计，或根容器写死 px | 按 820px 复验，根容器改 `100%` |
| 中文标题字形被拉歪 | 用了 `font-style:italic` | 中文字体无真斜体，会合成倾斜；改用字重与字号 |
| `+create` 报 network timeout | 环境网络问题，非内容问题 | 与 XML 无关，重试或换网络环境；不要为此改内容 |
