# -*- coding: utf-8 -*-
"""Genera menus_es.dat: los sprites de texto del menú de la colección dibujados en español.

Uso:  python menus_build.py <carpeta con los archivos del juego ya deserializados> <salida .dat> [--preview carpeta]

No copia nada de Konami: los textos se dibujan desde cero con fuentes del sistema y solo se usan las imágenes originales
para medir (tamaño de letra, color, posición de la línea base). El .dat contiene únicamente los píxeles nuevos y las
coordenadas que hay que ajustar; el instalador los aplica sobre los archivos del propio usuario.
"""
import base64
import json
import os
import sys
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import menus_textos as T

FONTS = os.environ.get('WINDIR', r'C:\Windows') + '/Fonts/'
BASE = (208, 205, 192)

# fuente, variación, color de relleno (o degradado), contorno, sombra, resplandor, separación entre letras
STYLES = {
    'btn':   dict(font='YuGothM.ttc', fill=BASE, outline=((19, 19, 19), 1.0, 0.95), shadow=(2, 2, 1.5, 0.55, (0, 0, 0))),
    'area':  dict(font='arial.ttf', fill=BASE, outline=((16, 16, 16), 1.0, 0.95), shadow=(2, 3, 2.0, 0.6, (0, 0, 0))),
    'bind':  dict(font='YuGothR.ttc', fill=BASE, shadow=(2, 2, 2.0, 0.65, (0, 0, 0))),
    'opt':   dict(font='bahnschrift.ttf', var='SemiLight Condensed', fill=BASE, shadow=(2, 2, 1.5, 0.6, (0, 0, 0))),
    'hdr':   dict(font='bahnschrift.ttf', var='Bold Condensed', fill=BASE, shadow=(2, 2, 1.5, 0.6, (0, 0, 0))),
    'stat':  dict(font='timesbd.ttf', fill=BASE),
    'desc':  dict(font='YuGothR.ttc', fill=BASE, shadow=(1, 2, 2.0, 0.7, (0, 0, 0))),
    'cy_s':  dict(font='ARLRDBD.TTF', thin=0.30, fill=(200, 234, 245), outline=((0, 0, 0), 2.5, 1.0)),
    'cy_b':  dict(font='ARLRDBD.TTF', thin=0.30, fill=(209, 244, 255), outline=((0, 0, 0), 3.0, 1.0)),
    'gm_note': dict(font='YuGothM.ttc', fill=(75, 236, 255), outline=((11, 15, 15), 1.2, 0.95), shadow=(2, 2, 1.5, 0.6, (0, 0, 0))),
    'gm_ver': dict(font='YuGothM.ttc', fill=(218, 218, 218), outline=((17, 17, 17), 1.0, 0.95), shadow=(2, 2, 1.5, 0.55, (0, 0, 0))),
    'gm_sel': dict(font='YuGothM.ttc', fill=(218, 218, 218), outline=((18, 18, 18), 1.0, 0.95), shadow=(2, 2, 1.5, 0.55, (0, 0, 0))),
    'gm_title': dict(font='timesbd.ttf', fill=[(0.0, (241, 217, 225)), (1.0, (215, 193, 198))], outline=((50, 36, 40), 1.0, 0.95), shadow=(3, 3, 3.0, 0.8, (0, 0, 0))),
    'gm_last': dict(font='YuGothB.ttc', fill=(132, 138, 144), shadow=(1, 1, 1.0, 0.5, (0, 0, 0))),
    'ready': dict(font='PERTILI.TTF', fill=(255, 255, 255), glow=((255, 255, 255), 6, 0.9), outline=((60, 60, 60), 1.0, 0.6)),
    'load':  dict(font='timesbd.ttf', fill=(200, 240, 255)),
    'load_blur': dict(font='timesbd.ttf', fill=(0, 0, 255), glow=((0, 0, 255), 7, 0.9)),
    'press': dict(font='timesbd.ttf', fill=[(0.0, (177, 177, 180)), (1.0, (170, 167, 170))], shadow=(2, 3, 3.0, 0.8, (0, 0, 0)), tracking=1.5),
    'mp_desc': dict(font='YuGothL.ttc', fill=(183, 183, 183), outline=((65, 36, 30), 2.0, 0.9)),
    'story': dict(font='YuGothL.ttc', fill=(167, 167, 167)),
}
STORY = {}
# anchos máximos concretos (px) para etiquetas que comparten fila con otros elementos
ID_LIMITS = {'0135': 290, '0136': 290, '0137': 290, '0138': 290, '0139': 290, '0140': 290, '0141': 290}
LATEST_PSB_VERSION = {'system/motion/pausemenu.psb': 3}


# ------------------------------------------------------------------------------------------------ dibujo
def load_font(path, size, var=None):
    f = ImageFont.truetype(FONTS + path, size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def mask_of(text, f, xs=1.0, pad=14, tracking=0.0, thin=0.0):
    asc, desc = f.getmetrics()
    tw = int(f.getlength(text) + tracking * max(0, len(text) - 1)) + 2 * pad
    im = Image.new('L', (tw, asc + desc + 2 * pad), 0)
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch in text:
            d.text((x, pad + asc), ch, font=f, fill=255, anchor='ls')
            x += f.getlength(ch) + tracking
    else:
        d.text((pad, pad + asc), text, font=f, fill=255, anchor='ls')
    if thin:
        a = np.array(im.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255.0
        im = Image.fromarray((np.clip((a - thin) / (1 - thin), 0, 1) * 255).astype(np.uint8))
    if xs != 1.0:
        im = im.resize((max(1, int(round(im.width * xs))), im.height), Image.LANCZOS)
    return im, pad + asc


def compose(m, fill, outline=None, shadow=None, glow=None):
    """m: máscara L ya con margen. Devuelve RGBA uint8 (alfa recta) del mismo tamaño."""
    W, H = m.size
    out = np.zeros((H, W, 4), np.float32)

    def layer(mask, rgb, alpha=1.0):
        col = np.zeros((H, W, 4), np.float32)
        col[..., 0:3] = rgb
        col[..., 3] = np.array(mask, np.float32) / 255.0 * alpha
        return col

    def over(dst, src):
        sa, da = src[..., 3:4], dst[..., 3:4]
        oa = sa + da * (1 - sa)
        oc = np.where(oa > 0, (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
        return np.concatenate([oc, oa], -1)

    if glow:
        rgb, r, al = glow
        out = over(out, layer(m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(r)), rgb, al))
    if shadow:
        dx, dy, blur, al, rgb = shadow
        base = m.filter(ImageFilter.MaxFilter(2 * int(round(outline[1])) + 1)) if outline else m
        sh = Image.new('L', (W, H), 0)
        sh.paste(base, (dx, dy))
        if blur:
            sh = sh.filter(ImageFilter.GaussianBlur(blur))
        out = over(out, layer(sh, rgb, al))
    if outline:
        rgb, r, al = outline
        ol = m.filter(ImageFilter.MaxFilter(2 * int(round(r)) + 1))
        if r > 0.5:
            ol = ol.filter(ImageFilter.GaussianBlur(0.6))
        out = over(out, layer(ol, rgb, al))
    f = layer(m, (255, 255, 255))
    if isinstance(fill[0], (int, float)):
        f[..., 0:3] = fill
    else:
        ma = np.array(m) > 8
        rows = np.where(ma.any(1))[0]
        y0, y1 = (rows.min(), rows.max()) if len(rows) else (0, H - 1)
        t = np.clip((np.arange(H, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)
        cols = np.stack([np.interp(t, [s[0] for s in fill], [s[1][c] for s in fill]) for c in range(3)], 1)
        f[..., 0:3] = cols[:, None, :]
    out = over(out, f)
    return np.clip(np.concatenate([out[..., :3], out[..., 3:4] * 255], -1), 0, 255).astype(np.uint8)


class Sprite:
    """Texto dibujado + datos para colocarlo: posición del relleno y de la línea base dentro de la imagen."""
    def __init__(self, arr, fill_l, fill_r, base):
        self.arr, self.fill_l, self.fill_r, self.base = arr, fill_l, fill_r, base

    @property
    def fill_w(self):
        return self.fill_r - self.fill_l


def crop_alpha(arr, fl, fr, base, pad=1):
    ys, xs = np.where(arr[..., 3] > 1)
    y0, y1, x0, x1 = max(0, ys.min() - pad), ys.max() + 1 + pad, max(0, xs.min() - pad), xs.max() + 1 + pad
    out = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    sub = arr[y0:y1, x0:x1]
    out[:sub.shape[0], :sub.shape[1]] = sub
    return Sprite(out, fl - x0, fr - x0, base - y0)


def render_line(text, st, size, xs=1.0, fill=None):
    f = load_font(st['font'], size, st.get('var'))
    m, base = mask_of(text, f, xs, tracking=st.get('tracking', 0.0), thin=st.get('thin', 0.0))
    a = np.array(m)
    ys, xs_ = np.where(a > 128)
    fl, fr = int(xs_.min()), int(xs_.max()) + 1
    arr = compose(m, fill if fill is not None else st['fill'], st.get('outline'), st.get('shadow'), st.get('glow'))
    return crop_alpha(arr, fl, fr, base)


def render_runs(runs, st, size, xs=1.0):
    """runs: [(texto, color|None)] en una sola línea; cada tramo con su color."""
    f = load_font(st['font'], size, st.get('var'))
    asc, desc = f.getmetrics()
    pad = 14
    total = sum(f.getlength(t) for t, _ in runs)
    W, H = int(total) + 2 * pad, asc + desc + 2 * pad
    base = pad + asc
    pieces, x = [], pad
    for t, col in runs:
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).text((x, base), t, font=f, fill=255, anchor='ls')
        pieces.append((im, col if col is not None else st['fill']))
        x += f.getlength(t)
    arr = None
    allm = Image.new('L', (W, H), 0)
    for im, col in pieces:
        allm = Image.fromarray(np.maximum(np.array(allm), np.array(im)))
        a = compose(im, col, st.get('outline'), st.get('shadow'), st.get('glow'))
        if arr is None:
            arr = a
        else:
            sa, da = a[..., 3:4] / 255.0, arr[..., 3:4] / 255.0
            oa = sa + da * (1 - sa)
            oc = np.where(oa > 0, (a[..., :3] * sa + arr[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
            arr = np.clip(np.concatenate([oc, oa * 255], -1), 0, 255).astype(np.uint8)
    if xs != 1.0:
        nw = max(1, int(round(W * xs)))
        arr = np.array(Image.fromarray(arr).resize((nw, H), Image.LANCZOS))
        allm = allm.resize((nw, H), Image.LANCZOS)
    a = np.array(allm)
    ys, xs_ = np.where(a > 128)
    return crop_alpha(arr, int(xs_.min()), int(xs_.max()) + 1, base)


def paste_over(out, sub, x0, y0):
    """Pega `sub` (RGBA) sobre `out` en (x0, y0) recortando lo que se salga; alfa 'over' correcto."""
    H, W = out.shape[:2]
    sy0, sx0 = max(0, -y0), max(0, -x0)
    dy0, dx0 = max(0, y0), max(0, x0)
    h, w = min(sub.shape[0] - sy0, H - dy0), min(sub.shape[1] - sx0, W - dx0)
    if h <= 0 or w <= 0:
        return
    src = sub[sy0:sy0 + h, sx0:sx0 + w].astype(np.float32)
    dst = out[dy0:dy0 + h, dx0:dx0 + w].astype(np.float32)
    sa, da = src[..., 3:4] / 255.0, dst[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    oc = np.where(oa > 0, (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
    out[dy0:dy0 + h, dx0:dx0 + w] = np.clip(np.concatenate([oc, oa * 255], -1), 0, 255).astype(np.uint8)


def stack_lines(sprites, pitch, align='center'):
    """Une varias líneas ya dibujadas (cada una con su línea base) en un solo Sprite."""
    lefts = []
    wmax = max(s.arr.shape[1] for s in sprites)
    tops = [i * pitch - s.base for i, s in enumerate(sprites)]
    ymin = min(tops)
    H = max(t + s.arr.shape[0] for t, s in zip(tops, sprites)) - ymin
    out = np.zeros((H, wmax, 4), np.uint8)
    fl, fr = 10 ** 9, -1
    for s, t in zip(sprites, tops):
        x0 = (wmax - s.arr.shape[1]) // 2 if align == 'center' else 0
        y0 = t - ymin
        h, w = s.arr.shape[:2]
        dst = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
        src = s.arr.astype(np.float32)
        sa, da = src[..., 3:4] / 255.0, dst[..., 3:4] / 255.0
        oa = sa + da * (1 - sa)
        oc = np.where(oa > 0, (src[..., :3] * sa + dst[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
        out[y0:y0 + h, x0:x0 + w] = np.clip(np.concatenate([oc, oa * 255], -1), 0, 255).astype(np.uint8)
        fl, fr = min(fl, x0 + s.fill_l), max(fr, x0 + s.fill_r)
    return Sprite(out, fl, fr, -ymin)


# ------------------------------------------------------------------------------------------------ medidas del original
class Atlas:
    def __init__(self, root, psb, tex, png_stream):
        self.psb, self.tex = psb, tex
        self.json_path = os.path.join(root, psb + '.json')
        self.j = json.load(open(self.json_path, encoding='utf-8'))
        self.src = self.j['source'][tex]
        self.icons = self.src['icon']
        t = self.src['texture']
        self.W, self.H = int(t['width']), int(t['height'])
        self.stream_n = int(t['pixel'].split(':')[-1])
        sp = os.path.join(root, psb + '.streams', 'stream_%d' % self.stream_n)
        self.px = np.frombuffer(open(sp, 'rb').read(), np.uint8)[:self.W * self.H * 4].reshape(self.H, self.W, 4).copy()
        self.trunc_h = int(t.get('truncated_height', self.H))
        self.ops = []          # (x, y, w, h, rgba|None)  None = borrar
        self.edits = {}        # id -> [l, t, w, h, ox, oy]
        self.next_y = self.trunc_h + 2
        self.shelf = [0, 0, 0]  # x, y, alto de la fila
        self.new_trunc = self.trunc_h

    def rect(self, n):
        i = self.icons[n]
        return [int(i[k]) for k in ('left', 'top', 'width', 'height', 'originX', 'originY')]

    def crop(self, n):
        l, t, w, h = self.rect(n)[:4]
        return self.px[t:t + h, l:l + w]

    def measure(self, n, soft=False):
        l, t, w, h, ox, oy = self.rect(n)
        c = self.px[t:t + h, l:l + w].astype(float)
        lum = 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]
        m = (c[..., 3] > 200) & (lum > 100)
        if soft:
            m = c[..., 3] > 10
        ys, xs = np.where(m)
        if len(ys) == 0:
            ys, xs = np.where(c[..., 3] > 10)
        return dict(w=w, h=h, ox=ox, oy=oy, ftop=int(ys.min()), fbot=int(ys.max()) + 1, fl=int(xs.min()), fr=int(xs.max()) + 1)

    def free_regions(self, block=8, min_w=96, min_h=40, maximo=10):
        """Rectángulos del atlas que ningún icono ocupa (relleno blanco sin usar), de mayor a menor."""
        gh, gw = self.H // block, self.W // block
        g = np.zeros((gh, gw), bool)
        for n, i in self.icons.items():
            l, t, w, h = [int(i[k]) for k in ('left', 'top', 'width', 'height')]
            g[t // block:(t + h + block - 1) // block, l // block:(l + w + block - 1) // block] = True
        regs = []
        for _ in range(maximo):
            best, height = None, np.zeros(gw, int)
            for y in range(gh):
                height = np.where(g[y], 0, height + 1)
                st = []
                for x in range(gw + 1):
                    cur = height[x] if x < gw else 0
                    start = x
                    while st and st[-1][1] >= cur:
                        sx, sh = st.pop()
                        area = (x - sx) * sh
                        if best is None or area > best[0]:
                            best = (area, sx, y - sh + 1, x - sx, sh)
                        start = sx
                    st.append((start, cur))
            if best is None or best[3] * block < min_w or best[4] * block < min_h:
                break
            _, bx, by, bw, bh = best
            g[by:by + bh, bx:bx + bw] = True
            regs.append([bx * block, by * block, bw * block, bh * block, 0, 0, 0])   # x, y, w, h, cursor x, cursor y, alto de fila
        return regs

    def alloc(self, w, h):
        """Reserva w x h en el espacio libre (empaquetado por filas con 2 px de margen)."""
        if not hasattr(self, 'regs'):
            self.regs = self.free_regions()
        for r in self.regs:
            x0, y0, rw, rh = r[:4]
            cx, cy, rowh = r[4], r[5], r[6]
            if cx + w + 2 > rw:
                cy += rowh
                cx, rowh = 0, 0
            if w + 2 <= rw and cy + h + 2 <= rh:
                r[4], r[5], r[6] = cx + w + 2, cy, max(rowh, h + 2)
                self.new_trunc = max(self.new_trunc, y0 + cy + h + 2)
                return (x0 + cx + 1, y0 + cy + 1)
        raise SystemExit('sin espacio en el atlas %s (%dx%d)' % (self.psb, w, h))

    def put(self, n, spr, anchor, orig, reuse=True):
        """Coloca el sprite `spr` como nuevo contenido del icono n respetando el ancla del original."""
        K = orig['base_k']
        # posición relativa al origen
        if anchor == 'center':
            fill_left_rel = (orig['fl'] + orig['fr']) / 2.0 - orig['ox'] - spr.fill_w / 2.0
        elif anchor == 'left':
            fill_left_rel = orig['fl'] - orig['ox']
        else:  # right
            fill_left_rel = orig['fr'] - orig['ox'] - spr.fill_w
        left_rel = int(round(fill_left_rel - spr.fill_l))
        top_rel = int(round(K - spr.base))
        h, w = spr.arr.shape[:2]
        l0, t0, ow, oh, _, _ = self.rect(n)
        self.ops.append((l0, t0, ow, oh, None))
        if reuse and w <= ow and h <= oh:
            x, y = l0, t0
        else:
            x, y = self.alloc(w, h)
        self.ops.append((x, y, w, h, spr.arr))
        self.edits[n] = [int(x), int(y), int(w), int(h), int(-left_rel), int(-top_rel)]


def band_rows(c, thr=20):
    rows = (c[..., 3] > thr).any(1)
    bands, start = [], None
    for i, v in enumerate(list(rows) + [False]):
        if v and start is None:
            start = i
        if not v and start is not None:
            bands.append((start, i))
            start = None
    return bands


# ------------------------------------------------------------------------------------------------ calibración
def calibrate(atlas, entries):
    """Por clase: tamaño de letra, factor horizontal y posición de la línea base respecto al origen, midiendo los iconos
    originales cuyo texto en inglés conocemos (alto del relleno -> tamaño; ancho -> factor horizontal)."""
    by = {}
    for n, cls, en, es in entries:
        if isinstance(en, str) and cls != 'load_blur':
            by.setdefault(cls, []).append((n, en))
    out = {}
    for cls, refs in by.items():
        st = STYLES[cls]
        sizes = []
        for n, en in refs[:12]:
            o = atlas.measure(n)
            target_h = o['fbot'] - o['ftop']
            best = None
            for sz in range(8, 120):
                f = load_font(st['font'], sz, st.get('var'))
                m, _ = mask_of(en, f, tracking=st.get('tracking', 0.0), thin=st.get('thin', 0.0))
                ys, xs = np.where(np.array(m) > 128)
                d = abs((ys.max() - ys.min() + 1) - target_h)
                if best is None or d < best[0]:
                    best = (d, sz)
            sizes.append(best[1])
        sz = int(round(float(np.median(sizes))))
        f = load_font(st['font'], sz, st.get('var'))
        ratios, ks = [], []
        for n, en in refs[:12]:
            o = atlas.measure(n)
            m, base = mask_of(en, f, tracking=st.get('tracking', 0.0), thin=st.get('thin', 0.0))
            ys, xs = np.where(np.array(m) > 128)
            ratios.append((o['fr'] - o['fl']) / float(xs.max() - xs.min() + 1))
            ks.append(o['fbot'] - (ys.max() + 1 - base) - o['oy'])
        out[cls] = dict(size=sz, xs=float(np.clip(np.median(ratios), 0.6, 1.2)), k=int(round(float(np.median(ks)))), n=len(refs))
    if 'load_blur' in {e[1] for e in entries} and 'load' in out:
        out['load_blur'] = dict(out['load'])
    return out


def anchor_of(o):
    """Cómo se alinea el texto original respecto al origen del icono: 'center' (origen en medio), 'left' (grupo con el
    mismo origen ~200: el texto empieza siempre en el mismo sitio) o 'right' (el texto termina junto al origen)."""
    w, ox = o['w'], o['ox']
    if abs(ox - w / 2.0) <= max(3, 0.03 * w):
        return 'center'
    if 190 <= ox <= 205 and ox > w - 2:
        return 'left'
    if ox >= w - 2:
        return 'right'
    return 'left'


def ajustar(hacer, size, xs, limite, n, texto, log):
    """Dibuja el texto y, si no cabe en `limite` px, lo estrecha como mucho un 15 % y después reduce la letra."""
    spr = hacer(size, xs)
    if limite and spr.fill_w > limite:
        xs2 = max(xs * 0.85, xs * limite / spr.fill_w)
        spr = hacer(size, xs2)
        sz = size
        while spr.fill_w > limite and sz > 8:
            sz -= 1
            spr = hacer(sz, xs2)
        log('  %s %-34s ajustado (estrechado %.2f, letra %d de %d)' % (n, texto[:34], xs2 / xs, sz, size))
    return spr


def build_atlas(atlas, entries, cal, max_w, log):
    for n, cls, en, es in entries:
        if n not in atlas.icons:
            log('  aviso: el icono %s no existe' % n)
            continue
        c = cal[cls]
        st = STYLES[cls]
        if cls == 'load_blur':
            blur_center(atlas, n, es, c, st)
            continue
        o = atlas.measure(n)
        o['base_k'] = c['k']
        anchor = anchor_of(o)
        text = es if isinstance(es, str) else None
        xs = c['xs']
        limit = ID_LIMITS.get(n, max_w.get(cls))
        if text is not None:
            spr = ajustar(lambda sz, x: render_line(text, st, sz, x), c['size'], xs, limit, n, text, log)
        else:
            pitch = 31
            spr = ajustar(lambda sz, x: stack_lines([render_line(t, st, sz, x) for t in es], pitch), c['size'], xs, limit, n, ' / '.join(es), log)
        atlas.put(n, spr, anchor, o)


def blur_center(atlas, n, text, c, st):
    """Sombra azul difuminada de 'Cargando...': se centra sobre el centro del original."""
    o = atlas.measure(n, soft=True)
    spr = render_line(text, st, c['size'], c['xs'])
    h, w = spr.arr.shape[:2]
    cx = (o['fl'] + o['fr']) / 2.0 - o['ox']
    cy = (o['ftop'] + o['fbot']) / 2.0 - o['oy']
    left_rel = int(round(cx - w / 2.0))
    top_rel = int(round(cy - h / 2.0))
    l0, t0, ow, oh, _, _ = atlas.rect(n)
    atlas.ops.append((l0, t0, ow, oh, None))
    if w <= ow and h <= oh:
        x, y = l0, t0
    else:
        x, y = atlas.alloc(w, h)
    atlas.ops.append((x, y, w, h, spr.arr))
    atlas.edits[n] = [int(x), int(y), int(w), int(h), int(-left_rel), int(-top_rel)]


# ------------------------------------------------------------------------------------------------ casos especiales
def special_cierre(atlas, pausa_cal, log):
    n, cls, parts = T.PAUSA_CIERRE
    st = STYLES[cls]
    c = pausa_cal[cls]
    l, t, w, h, ox, oy = atlas.rect(n)
    cr = atlas.crop(n)
    # el original son tres tramos separados por huecos: buscamos los huecos (columnas vacías de 20 px o más)
    cols = (cr[..., 3] > 20).any(0)
    runs, start = [], None
    for i, v in enumerate(list(cols) + [False]):
        if v and start is None:
            start = i
        if not v and start is not None:
            runs.append([start, i])
            start = None
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < 20:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    if len(merged) != 3:
        raise SystemExit('0255: no encuentro los tres tramos (%d)' % len(merged))
    o = atlas.measure(n)
    base_k = c['k']
    xs = c['xs']
    s1 = render_line(parts[0], st, c['size'], xs)
    s2 = render_line(parts[1], st, c['size'], xs)
    s3 = render_line(parts[2], st, c['size'], xs)
    # tramo central ('+') en su sitio; el izquierdo termina donde empieza el hueco izquierdo y el derecho empieza donde acaba el derecho
    mid_l, mid_r = merged[1]
    left_end, right_start = merged[0][1], merged[2][0]
    # coordenadas relativas al origen
    x_plus = (mid_l + mid_r) / 2.0 - ox - s2.fill_w / 2.0
    x1 = left_end - ox - s1.fill_w
    x3 = right_start - ox
    left_rel = min(x1 - s1.fill_l, x_plus - s2.fill_l, x3 - s3.fill_l)
    right_rel = max(x1 - s1.fill_l + s1.arr.shape[1], x3 - s3.fill_l + s3.arr.shape[1], x_plus - s2.fill_l + s2.arr.shape[1])
    left_rel, right_rel = int(np.floor(left_rel)), int(np.ceil(right_rel))
    W = right_rel - left_rel
    Hh = max(s.arr.shape[0] for s in (s1, s2, s3)) + 4
    base = max(s.base for s in (s1, s2, s3)) + 1
    out = np.zeros((Hh, W, 4), np.uint8)
    for s, xx in ((s1, x1), (s2, x_plus), (s3, x3)):
        paste_over(out, s.arr, int(round(xx - s.fill_l - left_rel)), base - s.base)
    spr = Sprite(out, 0, W, base)
    o['base_k'] = base_k
    # ancla: el centro del original se conserva
    top_rel = int(round(base_k - spr.base))
    l0, t0, ow, oh, _, _ = atlas.rect(n)
    atlas.ops.append((l0, t0, ow, oh, None))
    if W <= ow and Hh <= oh:
        x, y = l0, t0
    else:
        x, y = atlas.alloc(W, Hh)
    atlas.ops.append((x, y, W, Hh, out))
    atlas.edits[n] = [int(x), int(y), int(W), int(Hh), int(-left_rel), int(-top_rel)]
    log('  0255 tres tramos: ancho %d (original %d)' % (W, w))


def special_vacia(atlas, cal, log):
    n, lines1, runs2 = T.MUSICA_VACIA
    st = STYLES['mp_desc']
    o = atlas.measure(n)
    # tamaño: dos líneas de ~ 32 px de paso; medimos con las bandas de filas del original
    cr = atlas.crop(n)
    bands = band_rows(cr)
    log('  0043 bandas originales: %s (h=%d)' % (bands, o['h']))
    # calibración por ancho de la primera línea: "No tracks are yet registered in this playlist."
    first = cr[bands[0][0]:bands[0][1]]
    cols = np.where((first[..., 3] > 200).any(0))[0]
    wtarget = cols.max() - cols.min() + 1
    htarget = bands[0][1] - bands[0][0]
    best = None
    for sz in range(14, 60):
        f = load_font(st['font'], sz)
        m, _ = mask_of('No tracks are yet registered in this playlist.', f)
        a = np.array(m)
        ys, xs = np.where(a > 128)
        d = abs((xs.max() - xs.min() + 1) - wtarget)
        if best is None or d < best[0]:
            best = (d, sz)
    size = best[1]
    pitch = bands[1][0] - bands[0][0]
    sp1 = render_line(lines1[0], st, size)
    sp2 = render_runs([(runs2[0], None), (runs2[1], (225, 205, 0)), (runs2[2], None)], st, size)
    spr = stack_lines([sp1, sp2], pitch)
    o['base_k'] = 0
    # alineación: centro del original
    fill_left_rel = (o['w'] / 2.0) - o['ox'] - spr.fill_w / 2.0
    left_rel = int(round(fill_left_rel - spr.fill_l))
    base0 = bands[0][1] - 2 - 0          # línea base de la primera línea en el original (aprox. fin de banda)
    top_rel = int(round(base0 - o['oy'] - spr.base))
    h, w = spr.arr.shape[:2]
    l0, t0, ow, oh, _, _ = atlas.rect(n)
    atlas.ops.append((l0, t0, ow, oh, None))
    if w <= ow and h <= oh:
        x, y = l0, t0
    else:
        x, y = atlas.alloc(w, h)
    atlas.ops.append((x, y, w, h, spr.arr))
    atlas.edits[n] = [int(x), int(y), int(w), int(h), int(-left_rel), int(-top_rel)]


def wrap(text, f, xs, width):
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) * xs <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


def special_historia(atlas, n, paras, log):
    """Bloques de historia de cada juego: párrafos largos que se parten con el ancho del original y se reducen si
    no caben en su alto."""
    st = STYLES['story']
    o = atlas.measure(n)
    cr = atlas.crop(n)
    inner = cr[:, 4:-4]                               # el original lleva una raya de 1-2 px en el borde izquierdo
    bands = band_rows(inner, 150)
    cols = np.where((inner[..., 3] > 200).any(0))[0] + 4
    width_max = cols.max() - cols.min() + 1
    height_max = o['h']
    if n == '0004':                                   # calibración con 'The year is 1830.' (una sola línea)
        first = inner[bands[0][0]:bands[0][1]]
        fc = np.where((first[..., 3] > 200).any(0))[0]
        fr_ = np.where((first[..., 3] > 200).any(1))[0]
        best = None
        for sz in range(14, 50):
            f = load_font(st['font'], sz)
            m, _ = mask_of('The year is 1830.', f)
            ys, xs = np.where(np.array(m) > 128)
            d = abs((ys.max() - ys.min() + 1) - (fr_.max() - fr_.min() + 1))
            if best is None or d < best[0]:
                best = (d, sz, xs.max() - xs.min() + 1)
        log('  calibración historia: banda %s alto %d ancho %d -> letra %d' % (bands[0], fr_.max() - fr_.min() + 1, fc.max() - fc.min() + 1, best[1]))
        STORY.update(size=best[1], xs=(fc.max() - fc.min() + 1) / float(best[2]), pitch=27)
    size, xs_, pitch = STORY['size'], STORY['xs'], STORY['pitch']
    y_off = bands[0][0]                                # el texto del original empieza unas filas más abajo
    scale = 1.0
    while True:
        sz = max(10, int(round(size * scale)))
        f = load_font(st['font'], sz)
        pt = max(14, int(round(pitch * scale)))
        lines = []
        for i, p in enumerate(paras):
            if i:
                lines.append(None)
            lines += wrap(p, f, xs_, width_max - 2)
        total = (len(lines) - 1) * pt + int(sz * 1.3) + y_off
        if total <= height_max or sz <= 12:
            break
        scale -= 0.01
    log('  historia %s: %d líneas, letra %d (original %d), alto %d de %d' % (n, len(lines), sz, size, total, height_max))
    sprs = [render_line(t, st, sz, xs_) if t else None for t in lines]
    ref = next(s for s in sprs if s)
    out = np.zeros((y_off + (len(sprs) - 1) * pt + ref.arr.shape[0] + 8, width_max + 12, 4), np.uint8)
    for i, s in enumerate(sprs):
        if s is None:
            continue
        y0 = y_off - 1 + ref.base + i * pt - s.base
        paste_over(out, s.arr, 0, y0)
    left_rel = int(cols.min() - o['ox'] - ref.fill_l)
    l0, t0, ow, oh, _, _ = atlas.rect(n)
    arr = out[:oh, :ow]
    atlas.ops.append((l0, t0, ow, oh, None))
    atlas.ops.append((l0, t0, arr.shape[1], arr.shape[0], arr))
    atlas.edits[n] = [int(l0), int(t0), int(arr.shape[1]), int(arr.shape[0]), int(-left_rel), int(o['oy'])]


# ------------------------------------------------------------------------------------------------ vista previa y volcado
def apply_preview(atlas):
    px = atlas.px.copy()
    for x, y, w, h, arr in atlas.ops:
        if arr is None:
            px[y:y + h, x:x + w] = 0
        else:
            px[y:y + h, x:x + w] = arr
    return px


def pack_ops(atlas):
    ops = []
    for x, y, w, h, arr in atlas.ops:
        if arr is None:
            ops.append(['clear', int(x), int(y), int(w), int(h)])
        else:
            ops.append(['put', int(x), int(y), int(w), int(h), base64.b64encode(zlib.compress(arr.tobytes(), 9)).decode('ascii')])
    return ops


# ------------------------------------------------------------------------------------------------ retoques en sitio
def retocar_parche(atlas, n, caja, relleno, spr, x_centro=None, base_y=None):
    """Sustituye el contenido de `caja` (x0, y0, x1, y1 dentro del icono n, límites incluidos) por `relleno` (RGBA) y
    pinta encima el sprite de texto. El resto del icono no se toca y las coordenadas del icono no cambian."""
    l, t, w, h, ox, oy = atlas.rect(n)
    x0, y0, x1, y1 = caja
    cw, ch = x1 - x0 + 1, y1 - y0 + 1
    base = np.zeros((ch, cw, 4), np.uint8)
    base[:] = relleno
    if x_centro is None:
        x_centro = (x0 + x1) / 2.0
    px = int(round(x_centro - (spr.fill_l + spr.fill_r) / 2.0)) - x0
    py = int((base_y if base_y is not None else y1) - spr.base) - y0
    paste_over(base, spr.arr, px, py)
    atlas.ops.append((l + x0, t + y0, cw, ch, base))


def special_retoques(atlas, log):
    # 'Purchasable' -> 'En venta' (fondo negro semitransparente, texto cian con halo oscuro)
    st = dict(font='ARLRDBD.TTF', thin=0.36, fill=(0, 198, 255), outline=((0, 0, 0), 1.3, 1.0))
    best = None
    for sz in range(12, 40):
        f = load_font(st['font'], sz)
        m, _ = mask_of('En venta', f, thin=st['thin'])
        ys, xs = np.where(np.array(m) > 128)
        d = abs((ys.max() - ys.min() + 1) - 15)
        if best is None or d < best[0]:
            best = (d, sz)
    spr = render_line('En venta', st, best[1], 1.0)
    retocar_parche(atlas, '0010', (11, 5, 160, 25), (0, 0, 0, 128), spr, x_centro=86, base_y=21)
    log('  0010 En venta (letra %d, ancho %d)' % (best[1], spr.fill_w))
    # 'Area' -> 'Área' (serif gris claro sobre la línea decorativa)
    st = dict(font='timesbd.ttf', fill=(208, 205, 192))
    f = load_font(st['font'], 19)
    asc, _ = f.getmetrics()
    ancho_objetivo = 60
    base_w = f.getlength('Área')
    tr = max(0.0, (ancho_objetivo - base_w) / 3.0)
    st['tracking'] = tr
    spr = render_line('Área', st, 19, 1.0)
    retocar_parche(atlas, '0041', (44, 0, 124, 19), (208, 205, 192, 0), spr, x_centro=82, base_y=19)
    log('  0041 Área (tracking %.1f, ancho %d)' % (tr, spr.fill_w))


# ------------------------------------------------------------------------------------------------ fuentes
# Marcas de acento dibujadas desde cero (escala 1.0 = fuente del menú de 32 px de celda; 1.55 = fuente de la enciclopedia).
def _acento(nombre, esc):
    SS = 8
    def px(v):
        return int(round(v * esc))
    if nombre == 'agudo':
        w, h = max(5, px(6)), max(5, px(5.5))
        grosor = max(2.0, 2.0 * esc)
        im = Image.new('L', (w * SS, h * SS), 0)
        d = ImageDraw.Draw(im)
        d.line([(0.78 * w * SS, 0.5 * SS), (0.22 * w * SS, (h - 0.5) * SS)], fill=255, width=int(grosor * SS * 0.95))
    elif nombre == 'tilde':
        w, h = max(10, px(12)), max(4, px(4))
        grosor = max(1.6, 1.7 * esc)
        im = Image.new('L', (w * SS, h * SS), 0)
        d = ImageDraw.Draw(im)
        puntos = []
        for i in range(0, 61):
            t = i / 60.0
            x = (0.5 + t * (w - 1.0)) * SS
            y = (h / 2.0 + 0.5 - 0.5 * (h - grosor) * np.sin(t * 2 * np.pi)) * SS
            puntos.append((x, y))
        d.line(puntos, fill=255, width=int(grosor * SS), joint='curve')
    elif nombre == 'dieresis':
        punto = max(2, px(2.2))
        sep = max(3, px(3.0))
        w, h = 2 * punto + sep, punto + 1
        im = Image.new('L', (w * SS, h * SS), 0)
        d = ImageDraw.Draw(im)
        for x0 in (0, punto + sep):
            d.ellipse([x0 * SS, 0.5 * SS, (x0 + punto) * SS - 1, (0.5 + punto) * SS - 1], fill=255)
    else:
        raise ValueError(nombre)
    a = np.array(im.resize((im.width // SS, im.height // SS), Image.BOX), np.float32)
    a = np.clip(a * 1.35, 0, 255).astype(np.uint8)
    return a


FUENTES = [
    # archivo, id de la textura, ancho, alto, fila libre, escala del acento, hueco entre acento y letra
    dict(ruta='system/font/idemitsu_font.psb', id=10, stream=10, ancho=2048, alto=1024, y0=800, esc=1.0, hueco=2, dy=28, dd=5),
    dict(ruta='system/font/zukan_font.psb', id=2, stream=2, ancho=2048, alto=2048, y0=1800, esc=1.55, hueco=3, dy=43, dd=7),
]
GLIFOS = [   # carácter, letra base, acento, ¿quitar el punto de la i?
    ('á', 'a', 'agudo', 0), ('é', 'e', 'agudo', 0), ('í', 'i', 'agudo', 1), ('ó', 'o', 'agudo', 0), ('ú', 'u', 'agudo', 0),
    ('Á', 'A', 'agudo', 0), ('É', 'E', 'agudo', 0), ('Í', 'I', 'agudo', 0), ('Ó', 'O', 'agudo', 0), ('Ú', 'U', 'agudo', 0),
    ('ñ', 'n', 'tilde', 0), ('Ñ', 'N', 'tilde', 0), ('ü', 'u', 'dieresis', 0), ('Ü', 'U', 'dieresis', 0),
]
ROTADOS = [  # carácter, original que se gira 180°, filas que bajan de la línea base
    ('¿', '?', 5), ('¡', '!', 3),
]


def build_fonts():
    out = []
    for f in FUENTES:
        acentos = {}
        for n in ('agudo', 'tilde', 'dieresis'):
            a = _acento(n, f['esc'])
            acentos[n] = [int(a.shape[1]), int(a.shape[0]), base64.b64encode(zlib.compress(a.tobytes(), 9)).decode('ascii')]
        out.append(dict(ruta=f['ruta'], ver=2, id=f['id'], stream=f['stream'], ancho=f['ancho'], alto=f['alto'], y0=f['y0'],
                        hueco=f['hueco'], dy=f['dy'], dd=f['dd'], acentos=acentos,
                        glifos=[list(g) for g in GLIFOS], rotados=[list(r) for r in ROTADOS]))
    return out


def build_texts():
    import menus_ui as U
    pares = {
        'system/config/notice.psb': [(['message', 'NoticeMsg__' + k], t) for k, t in U.NOTICE.items()],
        'system/config/menu_item.psb': [(['message', 'MenuItemText__' + k], t) for k, t in U.MENU_ITEM.items()],
        'system/config/guide_parts.psb': [(['root', 'GuideParts__' + k, 'text'], '#{scale,0.7}' + t) for k, t in U.GUIDE_PARTS.items()]
                                       + [(['root', 'GuideParts__' + k, 'text'], t) for k, t in U.GUIDE_PARTS_PLAIN.items()],
        'system/config/encyclopedia.psb': [(['message', 'EncyclopediaText__' + k], t) for k, t in U.ENCYCLOPEDIA.items()],
    }
    out = [dict(ruta=r, ver=2, ediciones=[[p, t] for p, t in lst]) for r, lst in pares.items()]
    # textos de «datos guardados»: el juego ya trae su traducción en la ranura 'spa'; se copia a 'eng' para que también
    # la usen quienes tienen Steam en español latinoamericano
    out.append(dict(ruta='system/config/win_savedata_string.psb', ver=2, ediciones=[], copiar_spa_a_eng=True))
    for g in ('090', '091', '092', '093'):
        out.append(dict(ruta='%s/config/title_menu_string.psb' % g, ver=2, solo_eng=True,
                        ediciones=[[['message', 'MenuInfoMsg__PLAY_SIDE'], 'Elige jugar en el lado del jugador 1 (1P) o del jugador 2 (2P).']]))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('out')
    ap.add_argument('--preview')
    a = ap.parse_args()
    root = a.root
    files = {}

    def log(m):
        print(m)

    def atlas_for(psb, tex):
        key = (psb, tex)
        if key not in files:
            files[key] = Atlas(root, psb, tex, None)
        return files[key]

    jobs = [
        ('system/motion/pausemenu.psb', 'tex', T.PAUSA, {'btn': 395, 'area': 450, 'bind': 425, 'opt': 130, 'desc': 700, 'cy_s': 300, 'cy_b': 420}),
        ('022/motion/title_grandmenu.psb', 'tex#000', T.GRANDMENU, {'gm_note': 760, 'gm_ver': 300, 'gm_title': 450}),
        ('022/motion/title_ui_parts.psb', 'tex', T.UI_PARTS, {'ready': 700, 'btn': 260}),
        ('system/motion/music_player.psb', 'tex', T.MUSICA, {'cy_b': 440}),
        ('system/motion/nowloading.psb', 'tex', T.CARGA, {}),
        ('022/motion/title_opening_screen.psb', 'tex', T.APERTURA, {'press': 520}),
    ]
    for psb, tex, entries, max_w in jobs:
        at = atlas_for(psb, tex)
        log('%s %s' % (psb, tex))
        cal = calibrate(at, entries)
        for k, v in cal.items():
            log('  clase %-9s tamaño %3d  horizontal %.2f  línea base %+d  (%d refs)' % (k, v['size'], v['xs'], v['k'], v['n']))
        build_atlas(at, entries, cal, max_w, log)
        if psb.endswith('pausemenu.psb'):
            special_cierre(at, cal, log)
            special_retoques(at, log)
    gm1 = atlas_for('022/motion/title_grandmenu.psb', 'tex#000')
    for n in ('0004', '0008', '0011'):
        special_historia(gm1, n, T.HISTORIAS[n], log)
    gm2 = atlas_for('022/motion/title_grandmenu.psb', 'tex#001')
    special_historia(gm2, '0014', T.HISTORIAS['0014'], log)
    special_vacia(atlas_for('system/motion/music_player.psb', 'tex'), None, log)

    data = {'version': 2, 'archivos': [], 'fuentes': build_fonts(), 'textos': build_texts()}
    byfile = {}
    for (psb, tex), at in files.items():
        byfile.setdefault(psb, []).append((tex, at))
    for psb, lst in byfile.items():
        item = {'ruta': psb, 'ver': 3, 'texturas': []}
        for tex, at in lst:
            item['texturas'].append({
                'tex': tex, 'stream': at.stream_n, 'ancho': int(at.W), 'alto': int(at.H), 'trunc_alto': int(at.new_trunc),
                'iconos': at.edits, 'ops': pack_ops(at)})
        data['archivos'].append(item)
    blob = zlib.compress(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)
    open(a.out, 'wb').write(blob)
    log('escrito %s (%d KB)' % (a.out, len(blob) // 1024))

    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        for (psb, tex), at in files.items():
            px = apply_preview(at)
            name = '%s_%s.png' % (os.path.basename(psb).replace('.psb', ''), tex.replace('#', ''))
            Image.fromarray(px).save(os.path.join(a.preview, name))
            # hoja comparativa: original | nuevo para cada icono tocado
            cells = []
            for n, (x, y, w, h, ox, oy) in at.edits.items():
                l, t, ow, oh = at.rect(n)[:4]
                cells.append((n, Image.fromarray(at.px[t:t + oh, l:l + ow]), Image.fromarray(px[y:y + h, x:x + w])))
            W = 1500
            half = (W - 20) // 2
            rows = []
            for n, a0, b0 in cells:
                s = min(1.0, (half - 8) / max(a0.width, b0.width), 0.9 * 70 / max(a0.height, b0.height))
                if s < 1:
                    a0 = a0.resize((max(1, int(a0.width * s)), max(1, int(a0.height * s))))
                    b0 = b0.resize((max(1, int(b0.width * s)), max(1, int(b0.height * s))))
                rows.append((n, a0, b0))
            per = 16
            for si in range(0, len(rows), per):
                chunk = rows[si:si + per]
                Hs = [max(r[1].height, r[2].height) + 16 for r in chunk]
                sheet = Image.new('RGBA', (W, sum(Hs) + 4), (70, 70, 70, 255))
                d = ImageDraw.Draw(sheet)
                y = 2
                for (n, a0, b0), hh in zip(chunk, Hs):
                    d.text((4, y), n, fill=(255, 255, 0, 255))
                    sheet.paste(a0, (4, y + 13), a0)
                    sheet.paste(b0, (half + 20, y + 13), b0)
                    y += hh
                sheet.convert('RGB').save(os.path.join(a.preview, 'hoja_%s_%02d.png' % (name[:-4], si // per)))


if __name__ == '__main__':
    main()
