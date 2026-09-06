#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用同一份内容渲染 5 套主题，产出 5 个自包含 HTML 块。

为什么用生成而不是手写 5 份：内容必须完全一致，差异才只剩视觉，
否则无法公平比较主题；而且正例内容一改，5 份会立刻漂移。

用法：
    python3 scripts/make_themes.py                     # 生成到 assets/examples/
    python3 scripts/make_themes.py --out /tmp/themes    # 指定目录
    python3 scripts/make_themes.py --check              # 生成并跑静态检查
"""
import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS = os.path.join(ROOT, 'assets', 'base.css')
DEFAULT_OUT = os.path.join(ROOT, 'assets', 'examples')

THEMES = [
    ('modern',    't-modern',
     '苹果式现代主义',
     '通栏交替 · 微圆角 6px · 单一克莱因蓝。底色变化本身就是分隔线，不画边框。'),
    ('swiss',     't-swiss',
     '瑞士国际主义',
     '直角 · 不对称留白 · 瑞士红。层级全靠字号、字重、灰阶，一律左对齐。'),
    ('editorial', 't-editorial',
     '杂志编辑部',
     '极端字号对比 · 细横线 · 零彩色。区块之间 104px 纯留白。'),
    ('gallery',   't-gallery',
     '画廊极简',
     '留白拉到最大 120px · 字号收小 · 石墨青近中性点缀。'),
    ('mono',      't-mono',
     '技术档案',
     '等宽字面 · 表格化数据 · 深靛。适合口径、清单、对照。'),
]

# 同一份内容：第二章「开展条件判断」。五套主题共用，差异只在视觉。
BODY = '''<div class="band">
  <div class="hero">
    <div class="no">02</div>
    <div>
      <span class="kicker">能不能做 · 什么客户 · 什么时机适合做</span>
      <h1>信号回答「值不值得做」，前提回答「做不做得成」</h1>
      <p class="dek">信号差一点，可以和客户一起创造条件；前提缺一项，就建议先补齐再定时间，别把问题留到现场。</p>
    </div>
  </div>

  <div class="grid">
    <div class="u-h c2">
      <span class="lb">五条信号</span>
      <span class="fig">5<em>条</em></span>
      <p>都对上，才值得投一整天。差一到两条可以和客户一起创造条件，不是硬门槛。</p>
      <div class="seg"><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i></div>
      <p><b>本例：5 条全中</b>　决策窗口、高层到场、客户素材、领航员、配合度——五条逐项对照后全部成立。</p>
    </div>
    <div class="u-h c2">
      <span class="lb">六件前提</span>
      <span class="fig">6<em>项</em></span>
      <p>缺哪件补哪件。这是硬门槛——缺一项就别急着定时间。</p>
      <div class="seg"><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i><i></i><i></i></div>
      <p><b>本例：4 项扎实、2 项压线</b>　高层支持、接口人、领航员、场景预演都到位；试用包与互动物料卡到最后一刻。</p>
    </div>
    <div class="u-k c1">
      <span class="lb">劝退</span>
      <span class="fig key">4<em>条</em></span>
      <p>命中任意一条，先别定时间。</p>
    </div>
    <div class="u-t c1">
      <span class="lb">本例压线</span>
      <span class="fig">2<em>项</em></span>
      <p>后来都真出了问题。</p>
    </div>
  </div>
</div>

<div class="band alt tight">
  <div class="sec"><span class="pill">信号</span><small>五条都对上，才值得投一整天</small></div>
  <div class="stack">
    <div class="row"><div class="n">01</div><div>
      <div class="ct">决策窗口临近</div>
      <p>客户 1–2 个月内要选型、定预算或向上汇报，需要一次临门一脚的验证，而不是长期陪跑。</p>
    </div></div>
    <div class="row"><div class="n">02</div><div>
      <div class="ct">高层愿意到场</div>
      <p>一号位或二号位能全程参与开营与点评，风格务实、讲真话不走过场。</p>
    </div></div>
    <div class="row"><div class="n">03</div><div>
      <div class="ct">客户自己有料</div>
      <p>已自行梳理过场景清单或痛点盘点，动手环节不缺真实题目。</p>
    </div></div>
    <div class="row"><div class="n">04</div><div>
      <div class="ct">需要差异化验证</div>
      <p>客户对能不能落地有疑虑，或有竞品同台承诺类似活动。</p>
    </div></div>
    <div class="row"><div class="n">05</div><div>
      <div class="ct">配合度足以脱产一天</div>
      <p>有部门接口人能推动 20–30 名骨干脱产、集中场地、自带电脑，并愿提前完成认证与人员导入。</p>
    </div></div>
  </div>
</div>

<div class="band">
  <div class="mark">
    <div class="big">前提缺一项，就别急着定时间。</div>
    <p>信号可以创造，前提只能补齐——这是这一章唯一需要背下来的判断。</p>
  </div>

  <div class="sec"><span class="pill">前提</span><small>六件事，缺哪件补哪件；第一件是总闸</small></div>
  <div class="grid">
    <div class="u-h c4">
      <span class="lb">总闸 · 缺了其余五项都无意义</span>
      <div class="ct">高层支持</div>
      <p>有人能真正调动资源，且核心高管愿意承担开营与点评。这一项不成立，其余五项准备得再好也撑不起一整天。</p>
    </div>
    <div class="u-t c2">
      <div class="ct">客户侧接口人</div>
      <p>负责认证、导入、分组，并督促骨干全程在场。</p>
    </div>
    <div class="u-t c2">
      <div class="ct">领航员到位</div>
      <p>每人能独立带组：选题、带练、排障、兜底；组数不超过领航员数。</p>
    </div>
    <div class="u-q c2">
      <span class="lb">账号 T-2 闭环</span>
      <p>认证开通后逐人实测登录，另备测试租户预案。</p>
      <p class="flag">本例压线：会前一天才生效</p>
    </div>
    <div class="u-t c1">
      <div class="ct">场景预演</div>
      <p>会前预搭排雷，仅内部用。</p>
    </div>
    <div class="u-q c1">
      <span class="lb">物料 T-1</span>
      <p>签到、投票、问卷提前建好。</p>
      <p class="flag">本例压线</p>
    </div>
  </div>
</div>

<div class="band alt tight">
  <div class="sec key"><span class="pill">劝退</span><small>四条里命中任意一条，就先别定时间</small></div>
  <div class="grid">
    <div class="u-k c3">
      <span class="lb">最常见、也最致命</span>
      <div class="ct">账号或数据没就绪</div>
      <p>认证、导入、试用包没闭环，现场会变成集体排障——一整天的体验会在头 30 分钟直接崩掉，且当场无法挽回。</p>
    </div>
    <div class="u-t c1">
      <div class="ct">决策人不来</div>
      <p>效果传不到决策圈，改做小范围体验。</p>
    </div>
    <div class="u-t c2">
      <div class="ct">客户说不清痛点</div>
      <p>连 3–5 个真实高耗时场景都提不出，应先做场景调研，否则动手环节没有真题。</p>
    </div>
    <div class="u-t c2">
      <div class="ct">领航员配比不够</div>
      <p>1 人带超过 1 个组，或领航员自己没跑通产品，宁可减组、延期。</p>
    </div>
  </div>
</div>

<div class="band">
  <div class="sec"><span class="pill">本例对照</span><small>压线的两项后来都真出了问题</small></div>
  <table>
    <thead><tr><th>项</th><th>本例情况</th><th>结果</th></tr></thead>
    <tbody>
      <tr><td>决策窗口</td><td>次月中完成选型</td><td>扎实满足</td></tr>
      <tr><td>高层到场</td><td>一号位与二号位开营、点评都在</td><td>扎实满足</td></tr>
      <tr><td>客户素材</td><td>已梳理场景清单与试点</td><td>扎实满足</td></tr>
      <tr><td>领航员</td><td>6 人带 5 组，外地同事提前到场</td><td>扎实满足</td></tr>
      <tr><td>试用包</td><td>卡得太紧，会前一天才生效</td><td><b class="flag">压线</b>，几乎没有缓冲</td></tr>
      <tr><td>互动物料</td><td>投票文档当天临场还在找</td><td><b class="flag">压线</b>，没闭环</td></tr>
    </tbody>
  </table>
  <div class="foot"><b>体会：</b>信号差一点可以一起创造条件，前提缺项就建议先补齐再定时间。</div>
</div>'''

ALT = ('开展条件判断：把准入拆成信号与前提两类。信号五条判断值不值得投一整天，'
       '前提六件判断做不做得成，另有四条劝退情形；最后拿本例逐条对照，'
       '标出扎实满足的四项与压线的两项。')

SHELL = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="use-iframe" content="true">
<meta name="html-box-height-mode" content="auto">
<meta name="description" content="{alt}">
<title>开展条件判断</title>
<style>
{css}
</style>
</head>
<body class="{cls}">
{body}
</body>
</html>
'''


def build(outdir):
    if not os.path.isfile(CSS):
        sys.exit('找不到 base.css：%s' % CSS)
    css = open(CSS, encoding='utf-8').read()
    os.makedirs(outdir, exist_ok=True)
    made = []
    for slug, cls, name, desc in THEMES:
        html = SHELL.format(alt=ALT, css=css, cls=cls, body=BODY)
        path = os.path.join(outdir, 'theme-%s.html' % slug)
        open(path, 'w', encoding='utf-8').write(html)
        made.append(path)
        print('%-9s %-9s %s' % (slug, cls, name))
    return made


def check(paths):
    checker = os.path.join(HERE, 'check_blocks.py')
    bad = 0
    print('\n静态检查：')
    for p in paths:
        proc = subprocess.run([sys.executable, checker, p],
                              capture_output=True, text=True)
        head = [ln for ln in proc.stdout.splitlines() if ln.startswith('[')]
        info = [ln.strip() for ln in proc.stdout.splitlines() if 'info' in ln]
        tag = head[0] if head else '(无输出)'
        print('  %s' % tag)
        for i in info:
            print('        %s' % i)
        if 'FAIL' in tag:
            bad += 1
            for ln in proc.stdout.splitlines():
                if 'ERROR' in ln and 'ERROR 0' not in ln:
                    print('        %s' % ln.strip())
    return 1 if bad else 0


if __name__ == '__main__':
    out = DEFAULT_OUT
    if '--out' in sys.argv:
        out = sys.argv[sys.argv.index('--out') + 1]
    paths = build(out)
    if '--check' in sys.argv:
        sys.exit(check(paths))
