#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静态检查 HTML5 Block：禁用元素 / meta 头 / alt 语义 / token 合规 / 响应式。
用法：
    python3 check_blocks.py <目录或文件...>
退出码：0 无 ERROR / 1 有 ERROR
"""
import sys, os, re, glob

BANNED = [
    (r'<script\b',                     'ERROR', '禁止 <script>：块必须零 JS'),
    (r'<svg\b',                        'ERROR', '禁止 <svg>：用 CSS 造形'),
    (r'<canvas\b',                     'ERROR', '禁止 <canvas>'),
    (r'<link[^>]+stylesheet',          'ERROR', '禁止外链样式表：base.css 必须内联'),
    (r'<input\b',                      'ERROR', '禁止 <input>：假复选框用 li::before 画'),
    (r'linear-gradient|conic-gradient|radial-gradient',
                                       'ERROR', '禁止渐变：AI slop 头号特征'),
    (r'box-shadow\s*:\s*(?!none)',     'ERROR', '禁止阴影：用顶部 2px 语义线'),
    (r'border-radius\s*:\s*[1-9]px',   'WARN',  '圆角过小（1-9px）：本风格用 18px 大圆角，小圆角会退回普通卡片'),
    (r'#3370FF|#1456FO|#1456F0|#E8F1FF|#5B8CFF|#8FB4FF',
                                       'ERROR', '禁止通用 SaaS 蓝：改用 --brick'),
    (r'#00B42A|#E8FFEA|#FF7D00|#FFF7E8',
                                       'ERROR', '禁止红绿灯语义色：改用 --pine / --ochre'),
    (r'@import\b',                      'ERROR', '禁止 @import 外部资源'),
    (r'src\s*=\s*["\']https?://',      'ERROR', '禁止外链资源（图片/字体/脚本）'),
    (r'fonts\.googleapis|fonts\.gstatic|cdn\.jsdelivr|unpkg\.com',
                                       'ERROR', '禁止外链 CDN / webfont'),
    (r'onclick|onmouseover|addEventListener',
                                       'ERROR', '禁止事件绑定：块必须静态'),
    (r'[\U0001F300-\U0001FAFF\u2600-\u27BF]',
                                       'WARN',  '疑似 emoji 当图标：改用文字标签'),
    (r'@keyframes|animation\s*:',      'WARN',  '动效通常不必要，确认是否刻意'),
]

REQUIRED_META = [
    ('use-iframe',           r'<meta\s+name=["\']use-iframe["\']\s+content=["\']true["\']'),
    ('html-box-height-mode', r'<meta\s+name=["\']html-box-height-mode["\']\s+content=["\']auto["\']'),
    ('description',          r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']{12,}'),
]

TOKENS = ['--page', '--cell', '--ink', '--accent', '--line', '--r']

MAX_SOLID = 1   # 整块允许的实底色块数（.fill + .mark 合计）


def check(path):
    txt = open(path, encoding='utf-8').read()
    errs, warns, infos = [], [], []

    for pat, level, msg in BANNED:
        for m in re.finditer(pat, txt, re.I):
            line = txt[:m.start()].count('\n') + 1
            item = f'L{line}: {msg}  [{m.group(0)[:40]}]'
            (errs if level == 'ERROR' else warns).append(item)

    for name, pat in REQUIRED_META:
        if not re.search(pat, txt, re.I):
            errs.append(f'缺 meta「{name}」或内容过短')

    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)', txt, re.I)
    if m:
        d = m.group(1).strip()
        if len(d) < 20:
            warns.append(f'description 仅 {len(d)} 字，alt 需为完整语义句而非块名')
        elif '：' not in d and '，' not in d and ':' not in d:
            warns.append('description 疑似只是标题，建议写清有几个部分')

    if '<style' not in txt:
        errs.append('缺内联 <style>')
    else:
        missing = [t for t in TOKENS if t not in txt]
        if missing:
            warns.append('base.css token 不全，疑似未整段内联：缺 ' + ', '.join(missing))

    if 'max-width:640px' not in txt.replace(' ', ''):
        if re.search(r'grid-template-columns\s*:\s*(repeat\(|1fr\s+1fr)', txt, re.I):
            errs.append('用了多列但缺 @media(max-width:640px) 塌陷规则')

    if not re.search(r'class=["\'][^"\']*\bhero\b', txt):
        warns.append('缺 .hero 报头：每块顶部应有最高层级的实底报头')

    # 尺寸编码优先级：bento 网格里若所有单元同宽，等于普通卡片墙
    for gi, grid in enumerate(re.findall(r'<div class="bento">(.*?)(?=<div class="(?:bento|sec|mark|stack)"|<table|<div class="foot"|$)', txt, re.S)):
        spans = re.findall(r'class="[^"]*\b(c[1-4])\b', grid)
        if len(spans) >= 3 and len(set(spans)) == 1:
            warns.append(f'第 {gi+1} 个 .bento 全部是 {spans[0]} 等宽单元；尺寸要编码优先级，'
                         f'至少让主要单元用更大跨列（全等分等于普通卡片墙）')

    fs = [float(x) for x in re.findall(r'font-size\s*:\s*([\d.]+)px', txt)]
    if fs:
        span = max(fs) / min(fs)
        infos.append(f'字号 {min(fs)}–{max(fs)}px（跨度 {span:.1f}×）')
        if span < 2.0:
            warns.append(f'字号跨度仅 {span:.1f}×，层级不足；应有 ≥2.5× 的尺度对比')

    # 配色纪律：ink + ground + ONE accent。统计非中性色相的数量
    hues = set()
    for h in re.findall(r'#([0-9A-Fa-f]{6})', txt):
        r, g, b = [int(h[i:i+2],16)/255 for i in (0,2,4)]
        mx, mn = max(r,g,b), min(r,g,b)
        if (mx - mn) * 255 <= 24:                 # 灰阶，不计
            continue
        d = mx - mn                               # 按色相角分桶：
        if mx == r:   hue = (60 * ((g-b)/d)) % 360  # 同一颜色的深浅算一种
        elif mx == g: hue = 60 * ((b-r)/d) + 120
        else:         hue = 60 * ((r-g)/d) + 240
        hues.add(int(hue // 40))                  # 40° 一桶
    if len(hues) > 1:
        errs.append(f'出现 {len(hues)} 个彩色色相；本风格只允许「近黑 + 浅灰 + 一个强调色」，'
                    f'语义请用尺寸与轻重档表达，不要用第二个颜色')

    body = txt[txt.find('<body'):]
    solid = len(re.findall(r'class="[^"]*\bfill\b', body)) + len(re.findall(r'class="mark"', body))
    if solid > MAX_SOLID:
        errs.append(f'实底色块共 {solid} 处（.fill + .mark），上限 {MAX_SOLID} 处。'
                    f'一堆色块会显得杂乱——层级请用字号、留白、顶线粗细表达，'
                    f'实底只留给全块唯一的焦点句')

    # 彩色点缀节制：彩色元素总数不宜过多
    acc = len(re.findall(r'class="[^"]*\b(?:cell-acc|flag)\b', body)) \
        + len(re.findall(r'class="[^"]*\bfig[^"]*\bacc\b', body)) \
        + len(re.findall(r'class="sec acc"', body))
    if acc > 6:
        warns.append(f'彩色点缀 {acc} 处，偏多；彩色只作点缀（细线 / 小标签 / 单个数字），建议 ≤6 处')
    infos.append(f'实底色块 {solid} 处 · 彩色点缀 {acc} 处')

    errs += check_counts(txt)
    e2, w2, i2 = check_feishu(txt)
    errs += e2; warns += w2; infos += i2

    return errs, warns, infos


def check_feishu(txt):
    """
    飞书 html5-block 的嵌入约束。这些问题在本地 Chrome 里看不出来，
    只有写进文档才会暴露，所以必须静态拦住。
    依据：文档正文可用宽度约 820px；HTML 上限 500KB；
    高度模式只能是 auto 或 viewport。
    """
    errs, warns, infos = [], [], []

    size = len(txt.encode('utf-8'))
    infos.append(f'体积 {size/1024:.1f}KB（飞书上限 500KB）')
    if size > 500 * 1024:
        errs.append(f'HTML {size/1024:.0f}KB 超过飞书 500KB 上限')
    elif size > 400 * 1024:
        warns.append(f'HTML {size/1024:.0f}KB 接近 500KB 上限')

    m = re.search(r'name=["\']html-box-height-mode["\']\s+content=["\']([^"\']+)', txt, re.I)
    if m and m.group(1).strip() not in ('auto', 'viewport'):
        errs.append(f'html-box-height-mode 只能是 auto 或 viewport，当前是 {m.group(1)}')

    # 根容器写死像素宽会在 820px 正文里溢出或留白
    for sel in (r'\bbody\s*\{([^}]*)\}', r'\bhtml\s*\{([^}]*)\}'):
        for mm in re.finditer(sel, txt, re.I):
            decl = mm.group(1)
            wm = re.search(r'(?<![-\w])width\s*:\s*([^;}]+)', decl)
            if wm and 'px' in wm.group(1):
                errs.append(f'根容器写死像素宽 width:{wm.group(1).strip()}；'
                            f'飞书正文宽约 820px，应用 100% / max-width:100%')

    # auto 模式下给根容器固定高度或裁剪，会导致内容被截断
    if m and m.group(1).strip() == 'auto':
        for mm in re.finditer(r'\b(?:body|html)\s*\{([^}]*)\}', txt, re.I):
            d = mm.group(1)
            if re.search(r'(?<![-\w])height\s*:\s*\d+(px|vh)', d):
                errs.append('height-mode=auto 时根容器不得设固定高度，否则正文会被截断')
            if re.search(r'overflow(-y)?\s*:\s*hidden', d):
                warns.append('height-mode=auto 时根容器 overflow:hidden 可能裁掉内容')

    # 会破坏 JSON / XML 嵌入的字符
    if ']]>' in txt:
        errs.append('含 ]]>，会破坏 CDATA 嵌入')
    if '\x00' in txt:
        errs.append('含 NUL 字符')
    if txt.startswith('\ufeff'):
        warns.append('文件以 BOM 开头，建议存为无 BOM UTF-8')

    if 'box-sizing' not in txt:
        warns.append('未设 box-sizing:border-box，padding 会把元素撑出容器')

    return errs, warns, infos


CN_NUM = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7,
          '八': 8, '九': 9, '十': 10}


def _cn2int(s):
    if s.isdigit():
        return int(s)
    if s == '十':
        return 10
    if len(s) == 1:
        return CN_NUM.get(s)
    if s.startswith('十'):
        return 10 + CN_NUM.get(s[1], 0)
    if '十' in s:
        a, _, b = s.partition('十')
        return CN_NUM.get(a, 0) * 10 + (CN_NUM.get(b, 0) if b else 0)
    return None


def check_counts(txt):
    """
    小节标题里写了「N 条 / N 件 / N 项」，就必须真的有 N 个条目。
    数量对不上是复盘文档最容易被读者当场抓到的错——比配色难看严重得多。
    注意：小节可能带修饰类（class="sec key" / "sec pos"），切分必须容忍。
    """
    out = []
    body = txt.split('</style>', 1)[-1]
    # 用 class="sec" 或 class="sec <修饰>" 作为切分点
    parts = re.split(r'<div\s+class="sec(?:\s+[^"]*)?"\s*>', body)
    for seg in parts[1:]:
        # 小节标题内部可能有 <span>，取到该 div 结束为止
        head, _, rest = seg.partition('</div>')
        label = re.sub(r'<[^>]+>', ' ', head)
        label = re.sub(r'\s+', ' ', label).strip()
        m = re.search(r'([一二三四五六七八九十\d]+)\s*(条|件|项|个)', label)
        if not m:
            continue
        want = _cn2int(m.group(1))
        if not want:
            continue
        n_item = len(re.findall(r'class="item"', rest))
        n_panel = len(re.findall(r'class="panel[\s"]', rest))
        n_li = len(re.findall(r'<li\b', rest))
        # 取最贴近「一个条目」的语义单位：有 panel 用 panel，否则 item，再否则 li
        got = n_panel or n_item or n_li
        if got and got != want:
            out.append(
                f'「{label[:26]}」声称 {want}{m.group(2)}，实际 {got} 个条目'
                f'（item={n_item} panel={n_panel} li={n_li}）')
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return 1
    files = []
    for a in args:
        if os.path.isdir(a):
            files += sorted(glob.glob(os.path.join(a, '**', '*.html'), recursive=True))
        else:
            files.append(a)
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        print('没有找到 .html 文件'); return 1

    tot_e = tot_w = 0
    for f in files:
        e, w, i = check(f)
        tot_e += len(e); tot_w += len(w)
        mark = 'FAIL' if e else ('WARN' if w else 'PASS')
        print(f'\n[{mark}] {os.path.basename(f)}  (ERROR {len(e)} / WARN {len(w)})')
        for x in e: print(f'   ERROR  {x}')
        for x in w: print(f'   WARN   {x}')
        for x in i: print(f'   info   {x}')

    print(f'\n{"="*56}\n共 {len(files)} 个块：ERROR {tot_e} / WARN {tot_w}')
    if tot_e:
        print('ERROR 阻塞交付，请修复后重跑。')
    else:
        print('静态检查通过。注意：通过 ≠ 好看，必须再跑 render_check.py 并实际查看截图。')
    return 1 if tot_e else 0


if __name__ == '__main__':
    sys.exit(main())
