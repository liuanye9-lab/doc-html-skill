#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从正例派生两个负例，用于验证「配色纪律」两条规则真的在生效。

为什么用生成而不是直接提交文件：这两个负例是正例的最小变体（只改配色/类名），
直接提交会得到两份 14KB 的近似副本，正例一改就漂移。生成则永远跟着正例走。

用法：
    python3 tests/make_negatives.py            # 生成到 tests/
    python3 tests/make_negatives.py --check    # 生成并断言两条规则都报错

期望结果：
    negative-multi-hue.html      → ERROR 出现 3 个彩色色相（上限 1）
    negative-too-many-solid.html → ERROR 实底色块共 3 处（上限 1）
"""
import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POSITIVE = os.path.join(ROOT, 'assets', 'examples', 'qualify-block.html')

# 每个负例：文件名 →（替换列表, 期望命中的关键词）
CASES = {
    'negative-multi-hue.html': (
        # 注入第二、第三个色相：破坏「只有一个彩色色相」
        [('--accent:#002FA7;', '--accent:#002FA7;\n  --x1:#047857;\n  --x2:#D97706;')],
        '彩色色相',
    ),
    'negative-too-many-solid.html': (
        # 把两张顶线卡改回实底：破坏「实底 ≤1 处」
        [('class="cell-hd c4"', 'class="fill c4"'),
         ('class="cell-acc c3"', 'class="fill c3"')],
        '实底色块',
    ),
}


def build():
    if not os.path.isfile(POSITIVE):
        sys.exit('找不到正例：%s' % POSITIVE)
    src = open(POSITIVE, encoding='utf-8').read()
    made = []
    for name, (subs, _) in CASES.items():
        out = src
        for old, new in subs:
            if old not in out:
                sys.exit('正例里找不到待替换片段「%s」——正例结构已变，请更新本脚本' % old)
            out = out.replace(old, new)
        path = os.path.join(HERE, name)
        open(path, 'w', encoding='utf-8').write(out)
        made.append(path)
        print('生成 %s' % name)
    return made


def check(paths):
    checker = os.path.join(ROOT, 'scripts', 'check_blocks.py')
    failed = False
    for path in paths:
        name = os.path.basename(path)
        want = CASES[name][1]
        proc = subprocess.run([sys.executable, checker, path],
                              capture_output=True, text=True)
        hit = [ln.strip() for ln in proc.stdout.splitlines()
               if 'ERROR' in ln and want in ln]
        if hit:
            print('  ✓ %-32s %s' % (name, hit[0]))
        else:
            print('  ✗ %-32s 期望命中「%s」但没有报错——规则可能已失效' % (name, want))
            failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    paths = build()
    if '--check' in sys.argv:
        print('\n验证两条配色纪律：')
        sys.exit(check(paths))
