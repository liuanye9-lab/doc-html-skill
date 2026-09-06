#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从正例现场派生负例，验证 v7 视觉纪律的每条规则真的会失败。

为什么派生而不是存死文件：负例若是正例的副本，正例一改就漂移，
而且 8 个 14KB 的副本没有信息量。派生保证负例永远跟着正例走。

用法：
    python3 tests/make_negatives.py            # 生成到 /tmp/rdb-neg
    python3 tests/make_negatives.py --check    # 生成并断言每条都被拦住
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'assets', 'examples', 'theme-modern.html')
CHECKER = os.path.join(ROOT, 'scripts', 'check_blocks.py')
OUT = '/tmp/rdb-neg'

# (文件名, 说明, 变换, 期望命中的关键词)
CASES = [
    ('no-theme', '删掉 body 主题类',
     lambda s: s.replace('<body class="t-modern">', '<body>'), '主题类'),
    ('two-themes', '同时挂两套主题',
     lambda s: s.replace('<body class="t-modern">',
                         '<body class="t-modern t-swiss">'), '多个主题类'),
    ('tight-space', '间距退回常规值（未 ×1.5）',
     lambda s: s.replace('--s1:6px; --s2:12px; --s3:18px; --s4:24px;',
                         '--s1:4px; --s2:8px; --s3:12px; --s4:16px;'), '1.5 倍'),
    ('small-band', '通栏呼吸量压到 40px',
     lambda s: s.replace('--band:88px;', '--band:40px;'), '呼吸量'),
    ('card-shadow', '廉价封闭卡片阴影',
     lambda s: s.replace('.u-q{', '.u-q{box-shadow:0 2px 8px rgba(0,0,0,.18);'),
     '阴影范围过小'),
    ('big-radius', '大圆角',
     lambda s: s.replace('--r:6px;', '--r:24px;'), '圆角'),
    ('too-much-key', '核心色超出 10% 口径',
     # 给大量元素挂上核心色标记；.sk/.eyebrow 是 modern 骨架真实存在的类
     lambda s: s.replace('class="sk"', 'class="sk flag"')
                .replace('class="eyebrow"', 'class="eyebrow flag"')
                .replace('<b>', '<b class="flag">'), '核心色用在'),
    ('second-hue', '引入第二个色相',
     lambda s: s.replace('--ink-3:#86868B;', '--ink-3:#C0392B;'), '色相'),
    # 这两条对应用户的原话「不就是换了个颜色吗」。
    # shared-skeleton 是最关键的一条：模拟「五套共用一份 HTML 骨架，
    # 只切 body 的 class」——这正是被否决两轮的真实错误。
    ('shared-skeleton', '换了主题类但骨架照抄别套',
     lambda s: s.replace('class="t-modern"', 'class="t-swiss"'), '架构组件'),
    ('borrowed-arch', '混用别套的架构组件',
     lambda s: s.replace('class="tile alt"', 'class="tile alt poster"', 1), '借用'),
]


def main():
    if not os.path.isfile(SRC):
        sys.exit('缺正例，请先跑 scripts/make_themes.py：%s' % SRC)
    src = open(SRC, encoding='utf-8').read()
    os.makedirs(OUT, exist_ok=True)
    check = '--check' in sys.argv
    missed = []

    for name, desc, fn, expect in CASES:
        path = os.path.join(OUT, '%s.html' % name)
        mutated = fn(src)
        if mutated == src:
            missed.append('%s：变换未生效，正例结构可能已变' % name)
            continue
        open(path, 'w', encoding='utf-8').write(mutated)
        if not check:
            print('%-14s %s' % (name, desc))
            continue
        r = subprocess.run([sys.executable, CHECKER, path],
                           capture_output=True, text=True)
        hits = [l.strip() for l in r.stdout.splitlines()
                if l.strip().startswith(('ERROR', 'WARN')) and expect in l]
        ok = bool(hits)
        print('%-14s %-24s %s' % (name, desc, '拦住' if ok else '✗ 漏过'))
        if ok:
            print('               → %s' % hits[0][:96])
        else:
            missed.append('%s：期望命中「%s」，实际没报' % (name, expect))

    if check:
        print()
        if missed:
            for m in missed:
                print('漏检：%s' % m)
            sys.exit(1)
        print('%d/%d 条负例全部被拦住' % (len(CASES), len(CASES)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
