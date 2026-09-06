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
    ('modern',    't-modern',    '苹果式现代主义', '产品页 tile 序列：一屏一个信息，居中，交替底色'),
    ('swiss',     't-swiss',     '瑞士国际主义',   '海报式 12 栏可见网格：栏位精确落位，右侧毛边'),
    ('editorial', 't-editorial', '杂志编辑部',     '报纸头版：报头 + 首字下沉 + 三栏正文流 + 抽言'),
    ('gallery',   't-gallery',   '画廊极简',       '展览动线：一屏一件展品，标签在下，无网格'),
    ('mono',      't-mono',      '技术档案',       '终端记录卡：框线容器 + 字段名值对齐'),
]

# ---------------------------------------------------------------
# 内容相同，版面架构不同。
#
# 这是本文件最重要的设计：五套主题**各有自己的 HTML 骨架**。
# 早先版本五套共用一个 BODY 常量，只切 body 的 class——结果无论
# CSS 怎么写，五套的阅读顺序、组件构成、信息容器都是同一套，被
# 一眼看破「不就是换了个颜色吗」。
#
# 换风格的意思是换版面：报头是海报还是报头还是居中标题、数据是
# 栏位落位还是陈列还是读数、条目是悬挂还是多栏流还是字段行。
# ---------------------------------------------------------------

# 各套共用的事实（改内容只改这里，五套自动同步）
F = {
    'kick': '能不能做 · 什么客户 · 什么时机适合做',
    'h1':   '信号回答「值不值得做」，前提回答「做不做得成」',
    'dek':  '信号差一点，可以和客户一起创造条件；前提缺一项，就建议先补齐再定时间，别把问题留到现场。',
    'key':  '前提缺一项，就别急着定时间。',
    'keys': '信号可以创造，前提只能补齐——这是这一章唯一需要背下来的判断。',
    'foot': '信号差一点可以一起创造条件，前提缺项就建议先补齐再定时间。',
    'sig': [
        ('决策窗口临近', '客户 1–2 个月内要选型、定预算或向上汇报，需要一次临门一脚的验证，而不是长期陪跑。'),
        ('高层愿意到场', '一号位或二号位能全程参与开营与点评，风格务实、讲真话不走过场。'),
        ('客户自己有料', '已自行梳理过场景清单或痛点盘点，动手环节不缺真实题目。'),
        ('需要差异化验证', '客户对能不能落地有疑虑，或有竞品同台承诺类似活动。'),
        ('配合度足以脱产一天', '有部门接口人能推动 20–30 名骨干脱产、集中场地、自带电脑，并愿提前完成认证与人员导入。'),
    ],
    'pre': [
        ('高层支持', '有人能真正调动资源，且核心高管愿意承担开营与点评。这一项不成立，其余五项准备得再好也撑不起一整天。', 'gate'),
        ('客户侧接口人', '负责认证、导入、分组，并督促骨干全程在场。', ''),
        ('领航员到位', '每人能独立带组：选题、带练、排障、兜底；组数不超过领航员数。', ''),
        ('账号 T-2 闭环', '认证开通后逐人实测登录，另备测试租户预案。本例压线：会前一天才生效。', 'warn'),
        ('场景预演', '会前预搭排雷，仅内部用。', ''),
        ('物料 T-1', '签到、投票、问卷提前建好。本例压线。', 'warn'),
    ],
    'no': [
        ('账号或数据没就绪', '认证、导入、试用包没闭环，现场会变成集体排障——一整天的体验会在头 30 分钟直接崩掉，且当场无法挽回。'),
        ('决策人不来', '效果传不到决策圈，改做小范围体验。'),
        ('客户说不清痛点', '连 3–5 个真实高耗时场景都提不出，应先做场景调研，否则动手环节没有真题。'),
        ('领航员配比不够', '1 人带超过 1 个组，或领航员自己没跑通产品，宁可减组、延期。'),
    ],
    'tab': [
        ('决策窗口', '次月中完成选型', '扎实满足', 0),
        ('高层到场', '一号位与二号位开营、点评都在', '扎实满足', 0),
        ('客户素材', '已梳理场景清单与试点', '扎实满足', 0),
        ('领航员', '6 人带 5 组，外地同事提前到场', '扎实满足', 0),
        ('试用包', '卡得太紧，会前一天才生效', '压线，几乎没有缓冲', 1),
        ('互动物料', '投票文档当天临场还在找', '压线，没闭环', 1),
    ],
}


def _table(rows):
    out = ['<table>', '<thead><tr><th>项</th><th>本例情况</th><th>结果</th></tr></thead>', '<tbody>']
    for k, v, r, warn in rows:
        r = '<b class="flag">压线</b>' + r[2:] if warn else r
        out.append('  <tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (k, v, r))
    out += ['</tbody>', '</table>']
    return '\n'.join(out)


# ▓▓▓ swiss：海报式 12 栏网格 ▓▓▓
def body_swiss():
    gw = ['<ul class="gwall">']
    gw.append('  <li class="w6 lead"><span class="gk">五条信号 · 值不值得做</span>'
              '<span class="gv">5<em>条</em></span>'
              '<p>都对上，才值得投一整天。差一到两条可以和客户一起创造条件，不是硬门槛。'
              '本例 5 条全中。</p></li>')
    gw.append('  <li class="w6 lead"><span class="gk">六件前提 · 做不做得成</span>'
              '<span class="gv">6<em>项</em></span>'
              '<p>缺哪件补哪件。这是硬门槛——缺一项就别急着定时间。'
              '本例 4 项扎实、2 项压线。</p></li>')
    gw.append('  <li class="warn"><span class="gk">劝退</span>'
              '<span class="gv warn">4<em>条</em></span>'
              '<p>命中任意一条，先别定时间。</p></li>')
    gw.append('  <li><span class="gk">本例压线</span><span class="gv">2<em>项</em></span>'
              '<p>后来都真出了问题。</p></li>')
    gw.append('  <li class="w6"><span class="gk">结论</span>'
              '<p>五条信号逐项对照后全部成立，六件前提里两件卡到最后一刻——'
              '这两件后来都真出了问题。</p></li>')
    gw.append('</ul>')

    def hang(items, off=0):
        o = ['<ul class="hang">']
        for i, (t, d) in enumerate(items, 1 + off):
            o.append('  <li><div class="hn">%02d</div><div class="hb"><b>%s</b><p>%s</p></div></li>'
                     % (i, t, d))
        o.append('</ul>')
        return '\n'.join(o)

    pre = ['<ul class="hang">']
    for i, (t, d, m) in enumerate(F['pre'], 1):
        cls = ' class="%s"' % m if m else ''
        pre.append('  <li%s><div class="hn">%02d</div><div class="hb"><b>%s</b><p>%s</p></div></li>'
                   % (cls, i, t, d))
    pre.append('</ul>')

    return '\n'.join([
        '<div class="poster">',
        '  <div class="pno">02</div>',
        '  <div class="pkick">%s</div>' % F['kick'],
        '  <h1>%s</h1>' % F['h1'],
        '  <p class="pdek">%s</p>' % F['dek'],
        '</div>',
        '\n'.join(gw),
        '<div class="sbar"><b>信号</b><span>五条都对上，才值得投一整天</span></div>',
        hang(F['sig']),
        '<div class="mark">',
        '  <div class="big">%s</div>' % F['key'],
        '  <p>%s</p>' % F['keys'],
        '</div>',
        '<div class="sbar"><b>前提</b><span>六件事，缺哪件补哪件；第一件是总闸</span></div>',
        '\n'.join(pre),
        '<div class="sbar"><b class="warn">劝退</b><span>四条里命中任意一条，就先别定时间</span></div>',
        hang(F['no']),
        '<div class="sbar"><b>本例对照</b><span>压线的两项后来都真出了问题</span></div>',
        _table(F['tab']),
        '<div class="foot"><b>体会：</b>%s</div>' % F['foot'],
    ])


# ▓▓▓ editorial：报纸头版 ▓▓▓
def body_editorial():
    flow = ['<div class="flow">']
    for i, (t, d) in enumerate(F['sig'], 1):
        flow.append('  <div class="grp"><h3><i>%02d</i>%s</h3><p>%s</p></div>' % (i, t, d))
    flow.append('</div>')

    bars = ['<ul class="barlist">']
    for t, d, m in F['pre']:
        cls = ' class="gate"' if m == 'gate' else ''
        d2 = d if m != 'warn' else d.replace('本例压线', '<b class="flag">本例压线</b>')
        bars.append('  <li%s><b>%s</b><p>%s</p></li>' % (cls, t, d2))
    bars.append('</ul>')

    noflow = ['<div class="flow" style="column-count:2">']
    for i, (t, d) in enumerate(F['no'], 1):
        noflow.append('  <div class="grp"><h3><i>%02d</i>%s</h3><p>%s</p></div>' % (i, t, d))
    noflow.append('</div>')

    return '\n'.join([
        '<div class="mast"><span class="mt">开展条件判断</span>'
        '<span>第二章</span><span>%s</span></div>' % F['kick'],
        '<div class="lede">',
        '  <h1>%s</h1>' % F['h1'],
        '  <p class="sub">%s</p>' % F['dek'],
        '</div>',
        '<div class="pullq">%s<small>%s</small></div>' % (F['key'], F['keys']),
        '<div class="mast" style="border-top-width:1px"><span>信号 · 五条</span>'
        '<span>都对上，才值得投一整天</span></div>',
        '\n'.join(flow),
        '<div class="withbar">',
        '  <div>',
        '    <div class="bar-h">本例对照 · 压线的两项后来都真出了问题</div>',
        _table(F['tab']),
        '  </div>',
        '  <div>',
        '    <div class="bar-h">前提 · 六件，第一件是总闸</div>',
        '\n'.join(bars),
        '  </div>',
        '</div>',
        '<div class="mast" style="border-top-width:1px"><span>劝退 · 四条</span>'
        '<span>命中任意一条，先别定时间</span></div>',
        '\n'.join(noflow),
        '<div class="foot"><b>体会：</b>%s</div>' % F['foot'],
    ])


# ▓▓▓ gallery：展览动线 ▓▓▓
def body_gallery():
    out = ['<div class="walk">']
    out.append('  <div class="plate wide"><div class="idx">第二章 · 开展条件判断</div>'
               '<p class="art">%s</p>'
               '<p class="note">%s</p>'
               '<div class="cap"><span class="cn">Qualify</span><span>%s</span></div></div>'
               % (F['h1'], F['dek'], F['kick']))
    out.append('  <div class="plate wide"><div class="vitrine">'
               '<div><div class="vv">5<em>条</em></div><div class="vk">信号</div></div>'
               '<div><div class="vv">6<em>项</em></div><div class="vk">前提</div></div>'
               '<div><div class="vv warn">4<em>条</em></div><div class="vk warn">劝退</div></div>'
               '<div><div class="vv">2<em>项</em></div><div class="vk">本例压线</div></div>'
               '</div>'
               '<p class="note">信号判断值不值得投一整天，前提判断做不做得成。'
               '本例五条信号全中，六件前提里两件卡到最后一刻。</p></div>')
    out.append('  <div class="plate wide"><p class="art"><b>%s</b></p>'
               '<p class="note">%s</p>'
               '<div class="cap"><span class="cn">唯一需要背下来的判断</span></div></div>'
               % (F['key'], F['keys']))
    out.append('</div>')
    out.append('<div class="walk pair">')
    for i, (t, d) in enumerate(F['sig'], 1):
        out.append('  <div class="plate"><div class="idx">信号 %02d / 05</div>'
                   '<p class="art">%s</p><p class="note">%s</p>'
                   '<div class="cap"><span class="cn">值不值得做</span></div></div>' % (i, t, d))
    for t, d, m in F['pre']:
        cap = '总闸' if m == 'gate' else ('本例压线' if m == 'warn' else '前提')
        w = ' warn' if m == 'warn' else ''
        out.append('  <div class="plate"><div class="idx">前提</div>'
                   '<p class="art">%s</p><p class="note">%s</p>'
                   '<div class="cap%s"><span class="cn">%s</span></div></div>' % (t, d, w, cap))
    for t, d in F['no']:
        out.append('  <div class="plate"><div class="idx">劝退</div>'
                   '<p class="art">%s</p><p class="note">%s</p>'
                   '<div class="cap warn"><span class="cn">先别定时间</span></div></div>' % (t, d))
    out.append('</div>')
    out.append('<div class="walk">')
    out.append('  <div class="plate wide"><div class="idx">本例对照</div>')
    out.append(_table(F['tab']))
    out.append('  <p class="note"><b>体会：</b>%s</p></div>' % F['foot'])
    out.append('</div>')
    return '\n'.join(out)


# ▓▓▓ modern：产品页 tile 序列 ▓▓▓
def body_modern():
    feats = ['<div class="feats">']
    for t, d in F['sig']:
        feats.append('  <div><b>%s</b><p>%s</p></div>' % (t, d))
    feats.append('</div>')

    pre = ['<div class="feats">']
    for t, d, m in F['pre']:
        tag = '　总闸' if m == 'gate' else ('　本例压线' if m == 'warn' else '')
        feats_t = t + tag
        pre.append('  <div><b>%s</b><p>%s</p></div>' % (feats_t, d))
    pre.append('</div>')

    no = ['<div class="feats">']
    for t, d in F['no']:
        no.append('  <div><b>%s</b><p>%s</p></div>' % (t, d))
    no.append('</div>')

    return '\n'.join([
        '<div class="tile">',
        '  <div class="no">第二章</div>',
        '  <div class="eyebrow">%s</div>' % F['kick'],
        '  <h2>%s</h2>' % F['h1'],
        '  <p class="say long">%s</p>' % F['dek'],
        '</div>',
        '<div class="tile alt">',
        '  <div class="eyebrow">准入拆成两类</div>',
        '  <h2>信号可以创造，前提只能补齐</h2>',
        '  <div class="statrow">',
        '    <div><div class="sv">5<em>条</em></div><div class="sk">信号</div></div>',
        '    <div><div class="sv">6<em>项</em></div><div class="sk">前提</div></div>',
        '    <div><div class="sv warn">4<em>条</em></div><div class="sk">劝退</div></div>',
        '    <div><div class="sv">2<em>项</em></div><div class="sk">本例压线</div></div>',
        '  </div>',
        '  <div class="pills"><span class="on">决策窗口</span><span class="on">高层到场</span>'
        '<span class="on">客户素材</span><span class="on">领航员</span>'
        '<span class="on">配合度</span></div>',
        '</div>',
        '<div class="tile dark">',
        '  <h2>%s</h2>' % F['key'],
        '  <p class="say">%s</p>' % F['keys'],
        '</div>',
        '<div class="tile">',
        '  <div class="eyebrow">信号 · 五条</div>',
        '  <h2>都对上，才值得投一整天</h2>',
        '\n'.join(feats),
        '</div>',
        '<div class="tile alt">',
        '  <div class="eyebrow">前提 · 六件</div>',
        '  <h2>缺哪件补哪件，第一件是总闸</h2>',
        '\n'.join(pre),
        '</div>',
        '<div class="tile">',
        '  <div class="eyebrow">劝退 · 四条</div>',
        '  <h2>命中任意一条，先别定时间</h2>',
        '\n'.join(no),
        '</div>',
        '<div class="tile alt">',
        '  <div class="eyebrow">本例对照</div>',
        '  <h2>压线的两项后来都真出了问题</h2>',
        '  <div style="max-width:38em;margin:var(--s6) auto 0;text-align:left">',
        _table(F['tab']),
        '  <div class="foot"><b>体会：</b>%s</div>' % F['foot'],
        '  </div>',
        '</div>',
    ])


# ▓▓▓ mono：终端记录卡 ▓▓▓
def body_mono():
    sig = ['<ul class="entries">']
    for i, (t, d) in enumerate(F['sig'], 1):
        sig.append('  <li><div class="en">S%02d</div><div><b>%s</b><p>%s</p></div></li>' % (i, t, d))
    sig.append('</ul>')

    kv = ['<dl class="kv">']
    for t, d, m in F['pre']:
        cls = ' class="%s"' % m if m else ''
        d2 = d.replace('本例压线', '<b class="flag">本例压线</b>') if m == 'warn' else d
        kv.append('  <dt%s>%s</dt><dd>%s</dd>' % (cls, t, d2))
    kv.append('</dl>')

    no = ['<ul class="entries">']
    for i, (t, d) in enumerate(F['no'], 1):
        no.append('  <li><div class="en">N%02d</div><div><b>%s</b><p>%s</p></div></li>' % (i, t, d))
    no.append('</ul>')

    return '\n'.join([
        '<div class="rec">',
        '  <div class="rh"><span>REC · 02 开展条件判断</span><i>%s</i></div>' % F['kick'],
        '  <div class="rb">',
        '    <dl class="kv">',
        '      <dt>判断结论</dt><dd><b>%s</b></dd>' % F['h1'],
        '      <dt>口径</dt><dd>%s</dd>' % F['dek'],
        '    </dl>',
        '  </div>',
        '</div>',
        '<div class="rec">',
        '  <div class="rh"><span>READOUT · 关键读数</span><i>signal / prereq / stop</i></div>',
        '  <div class="rb"><div class="readout">',
        '    <div><div class="rv">5</div><div class="rk">信号 条</div>'
        '<div class="gauge"><b>▪▪▪▪▪</b></div></div>',
        '    <div><div class="rv">6</div><div class="rk">前提 项</div>'
        '<div class="gauge"><b>▪▪▪▪</b>··</div></div>',
        '    <div><div class="rv warn">4</div><div class="rk">劝退 条</div></div>',
        '    <div><div class="rv">2</div><div class="rk">本例压线 项</div></div>',
        '  </div></div>',
        '</div>',
        '<div class="mark">',
        '  <div class="big">%s</div>' % F['key'],
        '  <p>%s</p>' % F['keys'],
        '</div>',
        '<div class="rec">',
        '  <div class="rh"><span>SIGNAL · 五条</span><i>都对上才值得投一整天</i></div>',
        '  <div class="rb">%s</div>' % '\n'.join(sig),
        '</div>',
        '<div class="rec">',
        '  <div class="rh"><span>PREREQ · 六件</span><i>▸ 标记为总闸</i></div>',
        '  <div class="rb">%s</div>' % '\n'.join(kv),
        '</div>',
        '<div class="rec">',
        '  <div class="rh"><span>STOP · 四条</span><i>命中任意一条先别定时间</i></div>',
        '  <div class="rb">%s</div>' % '\n'.join(no),
        '</div>',
        '<div class="rec">',
        '  <div class="rh"><span>VERIFY · 本例对照</span><i>压线两项后来都真出了问题</i></div>',
        '  <div class="rb">%s</div>' % _table(F['tab']),
        '</div>',
        '<div class="foot"><b>体会：</b>%s</div>' % F['foot'],
    ])


BUILDERS = {
    'modern':    body_modern,
    'swiss':     body_swiss,
    'editorial': body_editorial,
    'gallery':   body_gallery,
    'mono':      body_mono,
}

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
        html = SHELL.format(alt=ALT, css=css, cls=cls, body=BUILDERS[slug]())
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
