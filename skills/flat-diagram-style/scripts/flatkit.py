"""flatkit — draw clean, flat, minimalist diagrams (PNG).

Pixel-coordinate canvas (default 2100 px wide), 2x supersampled for smooth edges.
Everything is drawn in "logical px"; (0,0) is top-left, y grows downward.

    from flatkit import Canvas, NAVY, TEAL, WARN
    c = Canvas(1200, 675)
    c.chain(50, 240, 180, [(500, NAVY, 'Input', None), (500, TEAL, 'Output', None)])
    c.save('out.png', trim=False)  # retain an exact canvas size
    print(WARN)                  # substantial text shrinkage needs layout review
"""
from functools import lru_cache
import glob
import math
import os
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont

S = 2  # supersampling factor

# ---------------- palette (semantic roles) ----------------
NAVY = '#1F3A5F'    # primary
TEAL = '#2A9D8F'    # secondary
SLATE = '#5A6B82'   # neutral
AMBER = '#E8A33D'   # emphasis
CORAL = '#D9604C'   # problem / exception
INK = '#1F2D3D'     # headings and text on light fills
GRAY = '#5A6B82'    # subtitles, captions
LIGHT = '#F2F4F7'   # card background
WHITE = '#FFFFFF'
LINE = '#CBD2DC'    # axis / lifeline / divider
TINT = {NAVY: '#DCE4EE', TEAL: '#D5ECE8', SLATE: '#E4E8EE', AMBER: '#FAEBD2', CORAL: '#F8DDD8'}


def text_color(fill):
    """Choose dark or white text by contrast, including custom opaque colors."""
    rgb = ImageColor.getrgb(fill) if isinstance(fill, str) else fill
    channels = [v / 255 for v in rgb[:3]]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    lum = sum(v * k for v, k in zip(linear, (0.2126, 0.7152, 0.0722)))
    dark_rgb = ImageColor.getrgb(INK)
    dark_lum = sum(((v / 255 + 0.055) / 1.055) ** 2.4 * k
                   for v, k in zip(dark_rgb, (0.2126, 0.7152, 0.0722)))
    dark_contrast = (max(lum, dark_lum) + 0.05) / (min(lum, dark_lum) + 0.05)
    white_contrast = 1.05 / (lum + 0.05)
    return INK if dark_contrast >= white_contrast else WHITE

# ---------------- fonts ----------------
_cache = {}
_font_paths = {}
_font_face = None
WARN = []
_CJK_DIRS = ['/usr/share/fonts/opentype/noto', '/usr/share/fonts/truetype/noto',
             '/usr/share/fonts/noto-cjk', '/usr/share/fonts/google-noto-cjk',
             str(Path.home() / 'Library/Fonts'), '/System/Library/Fonts', '/Library/Fonts',
             '/usr/share/fonts', '/usr/local/share/fonts',
             str(Path.home() / '.local/share/fonts'), str(Path.home() / '.fonts'),
             str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'),
             str(Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'Microsoft/Windows/Fonts')]


def configure_fonts(regular=None, bold=None, medium=None, index=None):
    """Set process-wide font paths and optional collection face; no args resets discovery.

    A supplied regular font also supplies missing weights. Glyph coverage must be
    checked in the rendered output; discovery does not guarantee every language.
    """
    paths = {k: str(Path(p).expanduser()) for k, p in
             [('Regular', regular), ('Bold', bold or regular), ('Medium', medium or regular)] if p}
    for path in paths.values():
        if not Path(path).is_file():
            raise FileNotFoundError(f'Font not found: {path}')
    global _font_face
    _font_paths.clear()
    _font_paths.update(paths)
    _font_face = index
    _cache.clear()
    _find_font.cache_clear()


@lru_cache(maxsize=None)
def _find_font(weight):
    if weight in _font_paths:
        return _font_paths[weight]
    patterns = [f'NotoSansCJK-{weight}.ttc', f'NotoSansCJKsc-{weight}.otf',
                f'NotoSansSC-{weight}.otf', 'NotoSansCJK.ttc', 'NotoSansCJK-Regular.ttc',
                'PingFang.ttc', 'Hiragino Sans GB.ttc', 'msyh.ttc', 'msjh.ttc',
                'wqy-*.tt*', '*CJK*.tt*']
    patterns += ['DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf'] if weight == 'Bold' else []
    patterns += ['DejaVuSans.ttf', 'Arial.ttf', 'arial.ttf']
    for pat in patterns:
        for d in _CJK_DIRS:
            for p in glob.glob(os.path.join(d, '**', pat), recursive=True):
                return p
    raise RuntimeError('No usable font found. Call configure_fonts(regular="/path/to/font.ttf") '
                       'with a font covering the requested language.')


@lru_cache(maxsize=None)
def _sc_index(path, weight='Regular'):
    """Prefer a Simplified-Chinese face and the requested weight within a collection."""
    if not path.lower().endswith(('.ttc', '.otc')):
        return 0
    best_index, best_score = 0, -1
    for i in range(64):
        try:
            f = ImageFont.truetype(path, 20, index=i)
        except OSError:
            break
        family, style = f.getname()
        score = 4 * ('SC' in family or ' GB' in family) + 2 * (weight.lower() in style.lower())
        if score > best_score:
            best_index, best_score = i, score
    return best_index


def font(size, w='Regular'):
    k = (max(1, round(size * S)), w)
    if k not in _cache:
        p = _find_font(w if w in ('Regular', 'Bold', 'Medium') else 'Regular')
        index = _font_face if _font_face is not None else _sc_index(p, w)
        _cache[k] = ImageFont.truetype(p, k[0], index=index)
    return _cache[k]


def T(text, size=28, w='Regular', color=None):
    """a styled text line (or multi-line with \\n) for stack()/box(items=[...])"""
    return dict(text=text, size=size, w=w, color=color)


class Canvas:
    LH = 1.34  # line-height multiplier

    def __init__(self, W=2100, H=1400, title='', subtitle=None, name='', *, background=WHITE, margin=50):
        self.W, self.H, self.name = W, H, name
        self.background, self.margin = background, margin
        self.content_w = W - 2 * margin
        self.img = Image.new('RGB', (W * S, H * S), background)
        self.d = ImageDraw.Draw(self.img)
        if title:
            self.raw(margin, 60, title, 50, 'Bold', text_color(background), 'lm')
        if subtitle:
            subtitle_color = GRAY if text_color(background) == INK else WHITE
            self.raw(margin, 142, subtitle, 31, 'Regular', subtitle_color, 'lm')

    # ================= primitives =================
    def raw(self, x, y, text, size, w='Regular', color=INK, anchor='lm'):
        self.d.text((x * S, y * S), text, font=font(size, w), fill=color, anchor=anchor)

    def tw(self, text, size, w='Regular'):
        """text width in logical px"""
        return max(font(size, w).getlength(l) for l in text.split('\n')) / S

    def rect(self, x, y, w, h, fill, r=0, outline=None, lw=0):
        b = (x * S, y * S, (x + w) * S, (y + h) * S)
        r = min(r, w / 2, h / 2)
        if r > 0:
            self.d.rounded_rectangle(b, radius=r * S, fill=fill, outline=outline, width=int(lw * S))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=int(lw * S))

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def circle(self, cx, cy, r, fill):
        self.d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=fill)

    def line(self, pts, color=SLATE, lw=6, dash=None):
        P = [(x * S, y * S) for x, y in pts]
        if dash is None:
            self.d.line(P, fill=color, width=int(lw * S), joint='curve')
            return
        for (x1, y1), (x2, y2) in zip(P[:-1], P[1:]):
            L = math.hypot(x2 - x1, y2 - y1)
            if L == 0:
                continue
            period = (dash[0] + dash[1]) * S
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            a = 0.0
            while a < L:
                b = min(a + dash[0] * S, L)
                self.d.line([(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)],
                            fill=color, width=int(lw * S))
                a += period

    def arrow(self, pts, color=SLATE, lw=6, head=26, dash=None):
        """polyline with a solid triangular head on the last point"""
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        L = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        bx, by = x2 - ux * head, y2 - uy * head
        self.line(list(pts[:-1]) + [(bx + ux * 2, by + uy * 2)], color, lw, dash)
        px, py = -uy, ux
        hw = head * 0.55
        self.poly([(x2, y2), (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw)], color)

    def trap(self, x, y, w, h, fill, narrow='right', k=0.2):
        """trapezoid (encoder / decoder / funnel). narrow: 'right' or 'left'"""
        d = h * k
        pts = [(x, y), (x + w, y + d), (x + w, y + h - d), (x, y + h)] if narrow == 'right' \
            else [(x, y + d), (x + w, y), (x + w, y + h), (x, y + h - d)]
        self.poly(pts, fill)

    # ================= text layout =================
    def stack(self, x, y, w, h, items, align='center', valign='center', pad=22, gap=10, padv=None):
        """Lay out T() items vertically inside a rect; shrinks uniformly to fit (logs to WARN if <0.78x)."""
        items = [dict(i) for i in items if i and i['text'] != '']
        if not items:
            return
        pv = min(pad, 14) if padv is None else padv

        def dims(s):
            ws, hs = [], []
            for it in items:
                sz = it['size'] * s
                ls = it['text'].split('\n')
                ws.append(max(font(sz, it['w']).getlength(l) for l in ls) / S)
                hs.append(len(ls) * sz * self.LH)
            return ws, hs

        ws, hs = dims(1)
        tot = sum(hs) + gap * (len(items) - 1)
        s = min(1.0, (w - 2 * pad) / max(ws), (h - 2 * pv) / tot)
        if s < 0.78:
            WARN.append(f'[{self.name}] shrink {s:.2f}: {items[0]["text"][:18]!r}')
        ws, hs = dims(s)
        tot = sum(hs) + gap * s * (len(items) - 1)
        cy = y + (h - tot) / 2 if valign == 'center' else y + pv
        for it, hh in zip(items, hs):
            sz = it['size'] * s
            col = it['color'] or INK
            lh = sz * self.LH
            for i, l in enumerate(it['text'].split('\n')):
                yy = cy + (i + 0.5) * lh
                if align == 'center':
                    self.raw(x + w / 2, yy, l, sz, it['w'], col, 'mm')
                else:
                    self.raw(x + pad, yy, l, sz, it['w'], col, 'lm')
            cy += hh + gap * s

    def box(self, x, y, w, h, fill, title=None, body=None, ts=32, bs=26, r=22, align='center',
            valign='center', pad=22, gap=10, color=None, items=None, outline=None, lw=0):
        """rounded flat card; title (bold) + body (regular), or custom items=[T(...)]"""
        self.rect(x, y, w, h, fill, r, outline, lw)
        col = color or text_color(fill)
        if items:
            its = [dict(i, color=i['color'] or col) for i in items]
        else:
            its = []
            if title: its.append(T(title, ts, 'Bold', col))
            if body: its.append(T(body, bs, 'Regular', col))
        self.stack(x, y, w, h, its, align, valign, pad, gap)

    # ================= components =================
    def section(self, y, text, x=None, accent=AMBER, size=36, color=None):
        """Heading with an optional accent bar; accent=None omits the bar."""
        x = self.margin if x is None else x
        if accent is not None:
            self.rect(x, y, 14, 44, accent)
        self.raw(x + (32 if accent is not None else 0), y + 22, text, size, 'Bold',
                 color or text_color(self.background), 'lm')

    def label(self, cx, cy, text, size=24, color=GRAY, bg=WHITE, w='Regular'):
        """small caption centred on a point (white backing so it can sit on a line)"""
        tw = self.tw(text, size, w) + 16
        if bg:
            self.rect(cx - tw / 2, cy - size * 0.75, tw, size * 1.5, bg)
        self.raw(cx, cy, text, size, w, color, 'mm')

    def pill(self, x, y, text, fill, size=26, h=52, padx=26):
        w = self.tw(text, size, 'Bold') + 2 * padx
        self.box(x, y, w, h, fill, None, None, items=[T(text, size, 'Bold')], r=h / 2, pad=8)
        return w

    def strip(self, y, text, fill=LIGHT, x=None, w=None, h=76, size=28, color=None, bold=False):
        """full-width one-line takeaway / footnote bar"""
        x = self.margin if x is None else x
        w = self.W - self.margin - x if w is None else w
        self.box(x, y, w, h, fill, None, None, items=[T(text, size, 'Bold' if bold else 'Regular')], r=18, color=color)

    def placeholder(self, x, y, w, h, text, color=AMBER, size=26):
        """dashed outline box marking data that still has to be filled in"""
        self.line([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y - 1)], color, 3, dash=(14, 9))
        self.stack(x, y, w, h, [T(text, size, 'Regular', GRAY)])

    def chain(self, x, y, h, specs, gap=64, lw=6):
        """horizontal flow: boxes joined by arrows. spec=(w, fill, title, body[, box_kwargs]). returns [(x,y,w,h)]"""
        pos, cx = [], x
        for sp in specs:
            w, fill, title, body = sp[:4]
            kw = sp[4] if len(sp) > 4 else {}
            self.box(cx, y, w, h, fill, title, body, **kw)
            pos.append((cx, y, w, h))
            cx += w + gap
        for a, b in zip(pos[:-1], pos[1:]):
            self.arrow([(a[0] + a[2] + 8, y + h / 2), (b[0] - 8, y + h / 2)], SLATE, lw, head=min(26, gap * 0.45))
        return pos

    def kpi_row(self, y, h, cards, x0=None, total_w=None, g=40, big=84):
        """big-number cards. cards=[(number, caption, color)]. returns bottom y"""
        x0 = self.margin if x0 is None else x0
        total_w = self.W - self.margin - x0 if total_w is None else total_w
        n = len(cards)
        w = (total_w - g * (n - 1)) / n
        for i, (num, cap, col) in enumerate(cards):
            x = x0 + i * (w + g)
            self.rect(x, y, w, h, LIGHT, 24)
            self.stack(x, y, w, h, [T(num, big, 'Bold', col), T(cap, 30, 'Regular', GRAY)], gap=16)
        return y + h

    def chips(self, x, y, w, items, fill=LIGHT, h=56, size=25, gap=14, padx=22, color=None):
        """auto-width tags that wrap inside width w. returns bottom y"""
        cx, cy = x, y
        for t in items:
            cw = self.tw(t, size) + 2 * padx
            if cx + cw > x + w and cx > x:
                cx, cy = x, cy + h + gap
            self.box(cx, cy, cw, h, fill, None, None, items=[T(t, size, 'Regular')], r=h / 2, pad=8, color=color)
            cx += cw + gap
        return cy + h

    def hbars(self, rows, y, x_label=50, label_w=300, scale=10, bar_h=56, pitch=80, label_size=28,
              extra_x=None, extra_size=26):
        """Nonnegative bars. rows=[(label, value, fill, value_text, extra_text|None)]."""
        if scale <= 0 or any(not math.isfinite(row[1]) or row[1] < 0 for row in rows):
            raise ValueError('hbars requires finite nonnegative values and a positive scale')
        bx = x_label + label_w + 30
        for i, (lab, val, fill, vt, ex) in enumerate(rows):
            yy = y + i * pitch
            self.raw(x_label + label_w, yy + bar_h / 2, lab, label_size, 'Regular', INK, 'rm')
            bw = val * scale
            if bw > 0:
                self.rect(bx, yy, bw, bar_h, fill, 10)
            self.raw(bx + bw + 18, yy + bar_h / 2, vt, 30, 'Bold', INK, 'lm')
            if ex and extra_x:
                self.raw(extra_x, yy + bar_h / 2, ex, extra_size, 'Regular', GRAY, 'lm')
        return y + len(rows) * pitch - (pitch - bar_h)

    def vbar(self, x, base, w, value, scale, fill, top_text=None, bottom_text=None, size=44):
        """one vertical bar standing on y=base (rounded top, flat bottom)"""
        if not math.isfinite(value) or value < 0 or scale <= 0:
            raise ValueError('vbar requires a finite nonnegative value and a positive scale')
        h = value * scale
        if h > 0:
            radius = min(12, h / 2, w / 2)
            self.rect(x, base - h, w, h, fill, radius)
            self.rect(x, base - radius, w, radius, fill)
        if top_text:
            self.raw(x + w / 2, base - h - size * 0.8, top_text, size, 'Bold', INK, 'mm')
        if bottom_text:
            self.raw(x + w / 2, base + 40, bottom_text, 28, 'Regular', GRAY, 'mm')

    def table(self, x, y, colw, header, rows, rh=110, hh=70, fs=26, hs=28, aligns=None, bold_col=None, pill_col=None):
        """flat table: navy header, zebra rows. pill_col=(col_idx, {text: fill}) renders that column as pills"""
        n = len(colw)
        aligns = aligns or ['left'] * n
        tot = sum(colw)
        self.rect(x, y, tot, hh, NAVY, 16)
        self.rect(x, y + hh - 16, tot, 16, NAVY)
        cx = x
        for i, c in enumerate(colw):
            self.stack(cx, y, c, hh, [T(header[i], hs, 'Bold', WHITE)], aligns[i], pad=24)
            cx += c
        yy = y + hh
        for ri, row in enumerate(rows):
            self.rect(x, yy, tot, rh, LIGHT if ri % 2 else WHITE)
            cx = x
            for i, c in enumerate(colw):
                txt = row[i]
                if pill_col and i == pill_col[0]:
                    fill = pill_col[1].get(txt, SLATE)
                    pw = min(c - 30, self.tw(txt, fs, 'Bold') + 44)
                    self.box(cx + (c - pw) / 2, yy + rh / 2 - 26, pw, 52, fill, None, None,
                             items=[T(txt, fs - 2, 'Bold')], r=26, pad=8)
                else:
                    wt = 'Bold' if bold_col and i in bold_col else 'Regular'
                    self.stack(cx, yy, c, rh, [T(txt, fs, wt, INK)], aligns[i], pad=24)
                cx += c
            yy += rh
        self.rect(x, yy, tot, 3, LINE)
        return yy

    # ---------- sequence diagram ----------
    def seq_participants(self, specs, y=210, w=300, h=90, bottom=1200):
        """specs=[(center_x, name, fill)]. draws dashed lifelines, then header boxes"""
        for cx, name, fill in specs:
            self.line([(cx, y + h), (cx, bottom)], LINE, 3, dash=(12, 10))
        for cx, name, fill in specs:
            self.box(cx - w / 2, y, w, h, fill, name, None, ts=30)

    def seq_msg(self, y, x1, x2, text, color=SLATE, dash=False, size=25, sub=None):
        """horizontal message arrow x1 -> x2, label above (optional grey sub-label below)"""
        d = 1 if x2 > x1 else -1
        self.arrow([(x1 + 8 * d, y), (x2 - 8 * d, y)], color, 5, 22, dash=(14, 9) if dash else None)
        self.label((x1 + x2) / 2, y - 30, text, size, INK)
        if sub:
            self.label((x1 + x2) / 2, y + 30, sub, size - 3, GRAY)

    def seq_self(self, y, x, text, w=90, h=46, size=25):
        """self-call loop on a lifeline"""
        self.arrow([(x + 8, y), (x + w, y), (x + w, y + h), (x + 10, y + h)], SLATE, 5, 22)
        self.raw(x + w + 20, y + h / 2, text, size, 'Regular', INK, 'lm')

    def seq_cross(self, x, y, color=CORAL, s=18):
        """failure marker on a lifeline"""
        self.line([(x - s, y - s), (x + s, y + s)], color, 8)
        self.line([(x - s, y + s), (x + s, y - s)], color, 8)

    # ================= output =================
    def save(self, path, trim=True, margin=None):
        """save PNG at logical size. trim=True crops blank space below the last drawn element."""
        im = self.img
        margin = self.margin if margin is None else margin
        if trim:
            bbox = ImageChops.difference(im, Image.new('RGB', im.size, self.background)).getbbox()
            if bbox:
                im = im.crop((0, 0, im.width, min(im.height, bbox[3] + margin * S)))
        im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        im.save(path, optimize=True)
        return path
