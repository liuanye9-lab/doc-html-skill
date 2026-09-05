#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渲染自检：在真实宽度下验证块的布局、语义色与字号层级。

用法：
    python3 render_check.py <html目录或文件> [--out 截图目录]
                            [--widths 1000,640,360]
退出码：0 无 ERROR / 1 有 ERROR

为什么用 iframe 而不是 --window-size：
    Chrome headless 的视口有约 500px 下限，`--window-size=360` 实际按 500px 渲染
    并裁剪截图，会产出「文字溢出」的假警报。iframe 能得到真实窄视口，
    也正是飞书 HTML5 Block 的真实渲染方式（use-iframe=true）。
"""
import sys, os, re, glob, html, json, zlib, struct, subprocess, shutil, argparse
import threading, functools, socketserver, http.server, tempfile
from collections import Counter

CHROME_CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    shutil.which('google-chrome') or '',
    shutil.which('chromium') or '',
]

SEMANTIC = {
    'brick': (0xA6, 0x3A, 0x22),
    'pine':  (0x2F, 0x6B, 0x4F),
    'ochre': (0x8A, 0x6A, 0x1F),
    'ink':   (0x1C, 0x1B, 0x18),
}
PAPER = [(0xF4, 0xF1, 0xE8), (0xFB, 0xF9, 0xF3)]

PROBE_JS = r"""
window.addEventListener('load', function () {
  setTimeout(function () {
    var out = [];
    var frames = document.querySelectorAll('iframe[data-w]');
    for (var k = 0; k < frames.length; k++) {
      var fr = frames[k];
      var w = fr.getAttribute('data-w');
      var d;
      try { d = fr.contentDocument; } catch (e) { d = null; }
      if (!d) { out.push('W' + w + '|ERR|cross-origin'); continue; }
      var de = d.documentElement;
      var vw = de.clientWidth, sw = de.scrollWidth, sh = de.scrollHeight;
      var bad = 0, worst = '', worstR = 0;
      var all = d.querySelectorAll('body *');
      for (var i = 0; i < all.length; i++) {
        var el = all[i], r = el.getBoundingClientRect();
        if (r.width > 0 && r.right > vw + 0.5) {
          bad++;
          if (r.right > worstR) { worstR = r.right; worst = el.tagName + '.' + (el.className || '-'); }
        }
      }
      var parts = ['W' + w, 'vw=' + vw, 'sw=' + sw, 'sh=' + sh,
                   'ovf=' + bad, 'worst=' + (worst || '-') ,
                   'worstR=' + worstR.toFixed(1)];
      var c2 = d.querySelector('.cols.c2');
      parts.push('c2=' + (c2 ? getComputedStyle(c2).gridTemplateColumns.split(' ').length : 0));
      var c3 = d.querySelector('.cols.c3');
      parts.push('c3=' + (c3 ? getComputedStyle(c3).gridTemplateColumns.split(' ').length : 0));
      var c4 = d.querySelector('.cols.c4');
      parts.push('c4=' + (c4 ? getComputedStyle(c4).gridTemplateColumns.split(' ').length : 0));
      var sizes = [];
      ['.figure', '.hd', '.sec', '.kicker'].forEach(function (s) {
        var e = d.querySelector(s);
        sizes.push(s + ':' + (e ? parseFloat(getComputedStyle(e).fontSize) : 0));
      });
      parts.push('fs=' + sizes.join(','));
      var clipped = 0;
      var texty = d.querySelectorAll('.hd,.sec,.item .t,.figure,.quote,td,th');
      for (var j = 0; j < texty.length; j++) {
        if (texty[j].scrollWidth > texty[j].clientWidth + 1) clipped++;
      }
      parts.push('clipped=' + clipped);
      out.push(parts.join('|'));
    }
    var box = document.createElement('div');
    box.id = 'zzresult';
    box.textContent = 'RSTART' + out.join('\n') + 'REND';
    document.body.appendChild(box);
  }, 700);
});
"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=root, **k)
        def log_message(self, *a, **k):
            pass
    class Srv(socketserver.TCPServer):
        allow_reuse_address = True
    httpd = Srv(('127.0.0.1', 0), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def png_pixels(path, step=3):
    d = open(path, 'rb').read()
    pos, idat, ct = 8, b'', 6
    W = H = 0
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        data = d[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            W, H, bd, ct = struct.unpack('>IIBB', data[:10])
        elif typ == b'IDAT':
            idat += data
        elif typ == b'IEND':
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    bpp = 4 if ct == 6 else 3
    stride = W * bpp
    out = Counter()
    prev = bytearray(stride)
    i = 0
    for y in range(H):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i + stride]); i += stride
        if f == 1:
            for x in range(bpp, stride): line[x] = (line[x] + line[x - bpp]) & 255
        elif f == 2:
            for x in range(stride): line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                c = prev[x - bpp] if x >= bpp else 0
                b = prev[x]
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        if y % step == 0:
            for x in range(0, W, step):
                out[tuple(line[x * bpp:x * bpp + 3])] += 1
        prev = line
    return W, H, out


def near(a, b, tol=18):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def run_probe(chrome, root, block_name, widths):
    """在同一页面里用多个 iframe 以真实宽度渲染同一个块。"""
    frames = '\n'.join(
        f'<iframe data-w="{w}" src="./{block_name}" width="{w}" height="2400" '
        f'style="border:0;display:block"></iframe>' for w in widths)
    harness = (
        '<!doctype html><html><head><meta charset="utf-8"><title>h</title>'
        '<style>body{margin:0;display:flex;gap:8px;align-items:flex-start}</style>'
        '</head><body>' + frames +
        '<script src="./__probe.js"></script></body></html>')
    hp = os.path.join(root, '__harness.html')
    jp = os.path.join(root, '__probe.js')
    open(hp, 'w', encoding='utf-8').write(harness)
    open(jp, 'w', encoding='utf-8').write(PROBE_JS)
    httpd, port = serve(root)
    try:
        r = subprocess.run(
            [chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
             f'--window-size={sum(widths) + 80},2000',
             '--virtual-time-budget=8000', '--dump-dom',
             f'http://127.0.0.1:{port}/__harness.html'],
            capture_output=True, text=True, timeout=120)
        dom = r.stdout
        m = (re.search(r'RSTART(.*?)REND', dom, re.S)
             or re.search(r'RSTART(.*?)REND', html.unescape(dom), re.S))
        if not m:
            return None
        body = html.unescape(m.group(1))
        rows = []
        for ln in body.strip().split('\n'):
            if not ln.strip():
                continue
            kv = {}
            bits = ln.split('|')
            kv['w'] = bits[0][1:]
            for b in bits[1:]:
                if '=' in b:
                    k, v = b.split('=', 1)
                    kv[k] = v
            rows.append(kv)
        return rows
    finally:
        httpd.shutdown(); httpd.server_close()
        for p in (hp, jp):
            if os.path.exists(p): os.unlink(p)


def shoot(chrome, root, name, out, w):
    """截图供人眼确认。宽度 <520 时用 iframe 包装以绕过 headless 视口下限。"""
    if w >= 520:
        httpd, port = serve(root)
        try:
            subprocess.run([chrome, '--headless=new', '--disable-gpu',
                            '--hide-scrollbars', f'--window-size={w},1600',
                            f'--screenshot={out}',
                            f'http://127.0.0.1:{port}/{name}'],
                           capture_output=True, timeout=90)
        finally:
            httpd.shutdown(); httpd.server_close()
    else:
        wrap = (f'<!doctype html><html><head><meta charset="utf-8">'
                f'<style>html,body{{margin:0;background:#F4F1E8}}'
                f'iframe{{border:0;display:block}}</style></head><body>'
                f'<iframe src="./{name}" width="{w}" height="2200"></iframe>'
                f'</body></html>')
        wp = os.path.join(root, '__wrap.html')
        open(wp, 'w', encoding='utf-8').write(wrap)
        httpd, port = serve(root)
        try:
            subprocess.run([chrome, '--headless=new', '--disable-gpu',
                            '--hide-scrollbars', f'--window-size={w},1600',
                            f'--screenshot={out}',
                            f'http://127.0.0.1:{port}/__wrap.html'],
                           capture_output=True, timeout=90)
        finally:
            httpd.shutdown(); httpd.server_close()
            if os.path.exists(wp): os.unlink(wp)
    return os.path.isfile(out)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('target')
    ap.add_argument('--out', default=None)
    ap.add_argument('--widths', default='1000,640,360')
    a = ap.parse_args()
    widths = [int(x) for x in a.widths.split(',')]

    chrome = find_chrome()
    if not chrome:
        print('未找到 Chrome/Chromium/Edge，无法渲染自检。')
        print('请安装其一，或手动在浏览器按 360 / 640 / 1000px 三个宽度目视确认。')
        return 1
    print(f'渲染引擎：{chrome}')
    print(f'测试宽度：{widths}（窄宽度经 iframe，规避 headless 视口下限）\n')

    files = sorted(glob.glob(os.path.join(a.target, '**', '*.html'), recursive=True)) \
        if os.path.isdir(a.target) else [a.target]
    files = [f for f in files if os.path.isfile(f)
             and not os.path.basename(f).startswith('__')]
    if not files:
        print('没有找到 .html 文件'); return 1

    root = a.target if os.path.isdir(a.target) else os.path.dirname(os.path.abspath(a.target))
    outdir = a.out or os.path.join(root, '_shots')
    os.makedirs(outdir, exist_ok=True)

    tot_e = tot_w = 0
    for f in files:
        name = os.path.basename(f)
        base = os.path.splitext(name)[0]
        errs, warns, infos = [], [], []

        rows = run_probe(chrome, root, name, widths)
        if rows is None:
            errs.append('布局探针无输出，无法验证真实宽度下的布局')
        else:
            for r in rows:
                w = r.get('w')
                ovf = int(r.get('ovf', 0))
                clipped = int(r.get('clipped', 0))
                c2, c3, c4 = (int(r.get(k, 0)) for k in ('c2', 'c3', 'c4'))
                infos.append(f'{w}px: 列数 c2={c2} c3={c3} c4={c4} · '
                             f'内容高 {r.get("sh")}px · 溢出 {ovf} · 截断 {clipped}')
                if ovf:
                    errs.append(f'{w}px 有 {ovf} 个元素横向溢出，'
                                f'最右 {r.get("worst")} @ {r.get("worstR")}')
                if clipped:
                    errs.append(f'{w}px 有 {clipped} 处文字被截断')
                if int(w) <= 640:
                    for label, v in (('c2', c2), ('c3', c3), ('c4', c4)):
                        if v > 1:
                            errs.append(f'{w}px 下 .cols.{label} 仍是 {v} 列，'
                                        f'未塌陷为单列')
                if int(w) >= 900:
                    if c3 and c3 < 3:
                        warns.append(f'{w}px 下 .cols.c3 只有 {c3} 列，桌面端应为 3 列')
                # 字号层级只在桌面宽度考核：移动端本就会压缩标题。
                # 且没有 .figure 的块（如判断框架类）天然跨度较小，只提示不告警。
                if int(w) >= 900:
                    fs = dict(p.split(':') for p in r.get('fs', '').split(',') if ':' in p)
                    vals = [float(v) for v in fs.values() if float(v) > 0]
                    has_fig = float(fs.get('.figure', 0)) > 0
                    if vals:
                        span = max(vals) / min(vals)
                        infos.append(f'{w}px 字号跨度 {span:.1f}×'
                                     + ('' if has_fig else '（本块无 .figure，跨度天然较小）'))
                        if has_fig and span < 2.5:
                            warns.append(f'{w}px 有 .figure 但字号跨度仅 {span:.1f}×，'
                                         f'尺度对比不足')
                        elif not has_fig and span < 1.6:
                            warns.append(f'{w}px 字号跨度仅 {span:.1f}×，层级过平')

        dpng = os.path.join(outdir, f'{base}.{widths[0]}.png')
        if shoot(chrome, root, name, dpng, widths[0]):
            W, H, px = png_pixels(dpng, step=3)
            total = sum(px.values())
            src = open(f, encoding='utf-8').read()
            found = {}
            for k, rgb in SEMANTIC.items():
                found[k] = sum(c for p, c in px.items() if near(p, rgb))
            infos.append('语义色像素：' + '  '.join(f'{k}={v}' for k, v in found.items()))
            for k in ('brick', 'pine', 'ochre'):
                if re.search(r'var\(--' + k + r'\)', src) and found[k] < 20:
                    warns.append(f'{k} 在 CSS 中被使用，渲染像素仅 {found[k]}，'
                                 f'可能太深或太浅而读不出色相')
            nonpaper = sum(c for p, c in px.items()
                           if not any(near(p, q, 6) for q in PAPER))
            ratio = nonpaper / total if total else 0
            infos.append(f'墨量占比 {ratio:.1%}（0.5%–12% 为宜）')
            if ratio > 0.20:
                warns.append(f'墨量 {ratio:.1%} 偏高，可能装饰过多或发丝线过重')
            if ratio < 0.003:
                errs.append(f'墨量 {ratio:.1%} 极低，块可能渲染为空白')
        else:
            errs.append(f'{widths[0]}px 截图失败')

        if len(widths) > 1:
            mpng = os.path.join(outdir, f'{base}.{widths[-1]}.png')
            if not shoot(chrome, root, name, mpng, widths[-1]):
                warns.append(f'{widths[-1]}px 截图失败')

        mark = 'FAIL' if errs else ('WARN' if warns else 'PASS')
        tot_e += len(errs); tot_w += len(warns)
        print(f'[{mark}] {base}  (ERROR {len(errs)} / WARN {len(warns)})')
        for x in errs: print(f'   ERROR  {x}')
        for x in warns: print(f'   WARN   {x}')
        for x in infos: print(f'   info   {x}')
        print()

    print('=' * 60)
    print(f'共 {len(files)} 个块：ERROR {tot_e} / WARN {tot_w}')
    print(f'截图目录：{outdir}')
    print('\n【必做】脚本只能测机械问题。请打开截图确认三件事：')
    print('  1. 字号层级是否真的拉开（巨大数字 vs 元信息）')
    print('  2. brick / pine / ochre 三色是否都能辨认出色相')
    print('  3. 发丝线是否过重、压过了文字')
    return 1 if tot_e else 0


if __name__ == '__main__':
    sys.exit(main())
