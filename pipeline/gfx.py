"""Motion-graphics overlay renderer for 'Leadership Begins When the Plan Falls Apart'.

Renders a transparent 1920x1080 overlay, frame-for-frame with the source (8272 frames @ 30fps).
Hard guards on every frame:
  * nothing may be drawn at y >= SUB_TOP (burned-in subtitles live there)
  * nothing may be drawn inside the tracked face box (+ margin)
Violations are logged; the run fails if any occur, so layouts get fixed rather than silently clipped.
"""
import json, math, os, re, sys, functools, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.environ["SCR"]
FPS, NF, W, H = 30, 8272, 1920, 1080
SUB_TOP = 850            # subtitles start ~y=875; keep all graphics above 850
LX, RX = 72, 1848        # outer edges of left / right zones

F = S + "/assets/fonts/"
FONTS = {
    "disp": F + "inter/extras/ttf/InterDisplay-Bold.ttf",
    "black": F + "inter/extras/ttf/InterDisplay-Black.ttf",
    "semi": F + "inter/extras/ttf/Inter-SemiBold.ttf",
    "med": F + "inter/extras/ttf/Inter-Medium.ttf",
    "mono": F + "jbm/fonts/ttf/JetBrainsMono-Bold.ttf",
    "monom": F + "jbm/fonts/ttf/JetBrainsMono-Medium.ttf",
    "tamil": F + "NotoSansTamil.ttf",
    "sc": F + "NotoSansSC.ttf",
}

@functools.lru_cache(None)
def font(name, size):
    return ImageFont.truetype(FONTS[name], size, layout_engine=ImageFont.Layout.RAQM)

INK = (20, 20, 24, 255)
MUTED = (112, 112, 122, 255)
WHITE = (255, 255, 255, 255)
CARD = (255, 255, 255, 240)
DARK = (22, 22, 28, 232)
GOLD = (245, 189, 35, 255)
GOLD_SOFT = (255, 233, 168, 255)
GOLD_TXT = (176, 124, 0, 255)
RED = (226, 64, 70, 255)
RED_SOFT = (255, 222, 222, 255)
LINE = (232, 232, 236, 255)

# ---------------------------------------------------------------- words / anchors
def norm(w): return re.sub(r"[^a-z0-9%]", "", w.lower())
def load_tokens(p):
    out = []
    for w in json.load(open(p)):
        n = norm(w["w"])
        if n: out.append((n, w["s"], w["e"]))
    return out
TOKS = [load_tokens(S + "/work/words_v.json"), load_tokens(S + "/work/words.json")]

def T(phrase, after=0.0, end=False):
    ps = [norm(p) for p in phrase.split()]
    for toks in TOKS:
        for i in range(len(toks) - len(ps) + 1):
            if toks[i][1] < after - 0.05: continue
            if all(toks[i + j][0] == ps[j] for j in range(len(ps))):
                return round(toks[i + len(ps) - 1][2] if end else toks[i][1], 3)
    raise ValueError("anchor not found: %r after %s" % (phrase, after))

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def ease_back(x, s=1.9):
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_inout(x): x = clamp(x); return 3 * x * x - 2 * x * x * x

# ---------------------------------------------------------------- SFX cue list
SFX = []
def sfx(kind, t, gain=1.0, note=""):
    if t is not None: SFX.append({"t": round(t, 3), "kind": kind, "gain": gain, "note": note})

# ---------------------------------------------------------------- rich text
TOKEN_RE = re.compile(r"\[([^\]]+)\]|\{([^}]+)\}|~([^~]+)~|([^\[\]{}~\s]+)|(\s+)")
def parse_rich(text):
    """[gold highlight] {red} ~struck~ ; returns list of (word, style)."""
    out = []
    for m in TOKEN_RE.finditer(text):
        g, r, s, w, sp = m.groups()
        if sp: continue
        if g:  out += [(x, "gold") for x in g.split()]
        elif r: out += [(x, "red") for x in r.split()]
        elif s: out += [(x, "strike") for x in s.split()]
        else: out.append((w, "n"))
    return out

def draw_rich(text, fname, size, width, color=INK, dark=False, align="l", lh=1.16):
    words = parse_rich(text)
    f = font(fname, size)
    sp = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w, st in words:
        wl = f.getlength(w) + (size * 0.5 if st == "gold" else 0)
        if cur and cw + sp + wl > width:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, st, f.getlength(w))); cw += (sp if len(cur) > 1 else 0) + wl
    if cur: lines.append(cur)
    lhp = int(size * lh)
    padx = int(size * 0.18)
    img = Image.new("RGBA", (width + 2 * padx, lhp * len(lines) + int(size * 0.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    asc = f.getmetrics()[0]
    for li, line in enumerate(lines):
        lw = sum(x[2] for x in line) + sp * (len(line) - 1)
        x = padx + (width - lw if align == "r" else (width - lw) / 2 if align == "c" else 0)
        y = li * lhp + int(size * 0.08)
        # merge contiguous gold runs into one pill
        i = 0
        while i < len(line):
            w, st, wl = line[i]
            if st == "gold" and not dark:
                if i > 0: x += size * 0.25
                j, run = i, 0
                while j < len(line) and line[j][1] == "gold":
                    run += line[j][2] + (sp if j > i else 0); j += 1
                d.rounded_rectangle([x - padx * 0.8, y + size * 0.02, x + run + padx * 0.8, y + size * 1.12], radius=int(size * 0.22), fill=GOLD)
                for k in range(i, j):
                    d.text((x, y + asc * 0.0), line[k][0], font=f, fill=INK); x += line[k][2] + sp
                x += size * 0.25
                i = j; continue
            col = color
            if st == "gold": col = GOLD
            if st == "red": col = RED
            if st == "strike": col = MUTED if not dark else (170, 170, 178, 255)
            d.text((x, y), w, font=f, fill=col)
            if st == "strike":
                yy = y + size * 0.62
                d.line([x - 4, yy, x + wl + 4, yy], fill=RED, width=max(3, size // 12))
            x += wl + sp
            i += 1
    return img

# ---------------------------------------------------------------- icons (flat, drawn)
def icon_check(size, bg=GOLD, fg=INK):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=bg)
    d.line([(s * .27, s * .52), (s * .44, s * .68), (s * .74, s * .34)], fill=fg, width=int(s * .11), joint="curve")
    return im.resize((size, size), Image.LANCZOS)
def icon_x(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, s - 1, s - 1], fill=RED)
    w = int(s * .11)
    d.line([(s * .32, s * .32), (s * .68, s * .68)], fill=WHITE, width=w)
    d.line([(s * .68, s * .32), (s * .32, s * .68)], fill=WHITE, width=w)
    return im.resize((size, size), Image.LANCZOS)
def icon_dot(size, col=GOLD):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); ImageDraw.Draw(im).ellipse([0, 0, s - 1, s - 1], fill=col)
    return im.resize((size, size), Image.LANCZOS)

# ---------------------------------------------------------------- rows
class Row:
    """A horizontal strip inside a card. at=None -> visible with card. Dynamic rows implement frame(t)."""
    dynamic = False
    def __init__(self, at=None, sfx_kind=None, anim="rise"):
        self.at, self.sfx_kind, self.anim = at, sfx_kind, anim
    def size(self): return self.img.size
    def frame(self, t): return self.img
    def key(self, t): return 0

def _txt(text, fname, size, width, color=INK, dark=False, align="l"):
    return draw_rich(text, fname, size, width, color, dark, align)

class K(Row):  # kicker: mono caps with dot
    def __init__(self, text, at=None, col=None, **kw):
        super().__init__(at, **kw); self.text, self.col = text, col
    def build(self, width, dark):
        f = font("mono", 21)
        col = self.col or (GOLD if dark else MUTED)
        im = Image.new("RGBA", (width, 34), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        im.alpha_composite(icon_dot(12, self.col or GOLD), (0, 11))
        d.text((22, 5), self.text.upper(), font=f, fill=col)
        self.img = im

class Hd(Row):  # headline
    def __init__(self, text, size=46, at=None, fname="disp", align="l", **kw):
        super().__init__(at, **kw); self.text, self.fs, self.fname, self.align = text, size, fname, align
    def build(self, width, dark):
        self.img = _txt(self.text, self.fname, self.fs, width - 12, WHITE if dark else INK, dark, self.align)

class P(Row):  # body text
    def __init__(self, text, size=28, at=None, col=None, **kw):
        super().__init__(at, **kw); self.text, self.fs, self.col = text, size, col
    def build(self, width, dark):
        self.img = _txt(self.text, "med", self.fs, width - 12, self.col or ((205, 205, 212, 255) if dark else MUTED), dark)

class Chk(Row):  # check-list row
    def __init__(self, text, at=None, size=32, mark="check", **kw):
        super().__init__(at, sfx_kind=kw.pop("sfx_kind", "tick"), **kw); self.text, self.fs, self.mark = text, size, mark
    def build(self, width, dark):
        ic = icon_check(int(self.fs * 1.15)) if self.mark == "check" else icon_x(int(self.fs * 1.15))
        tx = _txt(self.text, "semi", self.fs, width - ic.width - 30, WHITE if dark else INK, dark)
        h = max(ic.height, tx.height) + 6
        im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
        im.alpha_composite(ic, (0, (h - ic.height) // 2)); im.alpha_composite(tx, (ic.width + 14, (h - tx.height) // 2 + 2))
        self.img = im

class Strike(Row):  # text that gets struck through at strike_at
    dynamic = True
    def __init__(self, text, strike_at, size=40, at=None, **kw):
        super().__init__(at, **kw); self.text, self.sa, self.fs = text, strike_at, size
        sfx("whoosh", strike_at, 0.55, "strike-through: " + text)
    def build(self, width, dark):
        self.base = _txt(self.text, "disp", self.fs, width - 12, WHITE if dark else INK, dark)
        f = font("disp", self.fs); self.tw = f.getlength(self.text)
        self.img = self.base
    def key(self, t): return round(clamp((t - self.sa) / 0.25), 2)
    def frame(self, t):
        p = ease_out((t - self.sa) / 0.25)
        if p <= 0: return self.base
        im = self.base.copy(); d = ImageDraw.Draw(im)
        pad = int(self.fs * 0.18)
        y = int(self.fs * 0.08 + self.fs * 0.6)
        d.line([pad - 6, y, pad - 6 + (self.tw + 12) * p, y], fill=RED, width=max(5, self.fs // 9))
        if p >= 1:  # grey the word under the line slightly
            pass
        return im

class Chip(Row):  # pill / stamp
    def __init__(self, text, at=None, style="gold", size=28, stamp=False, **kw):
        kind = "thump" if stamp else "pop"
        super().__init__(at, sfx_kind=kw.pop("sfx_kind", kind), anim="stamp" if stamp else "pop", **kw)
        self.text, self.style, self.fs, self.stamp = text, style, size, stamp
    def build(self, width, dark):
        f = font("mono" if not self.stamp else "black", self.fs)
        tw = f.getlength(self.text)
        padx, h = int(self.fs * 0.7), int(self.fs * 1.75)
        im = Image.new("RGBA", (width, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        bg, fg = {"gold": (GOLD, INK), "red": (RED, WHITE), "dark": (INK, GOLD), "soft": (GOLD_SOFT, INK), "line": ((0, 0, 0, 0), INK)}[self.style]
        if self.stamp:
            d.rounded_rectangle([4, 4, 4 + tw + 2 * padx, 4 + h], radius=10, outline=bg, width=5, fill=(bg[0], bg[1], bg[2], 40))
            d.text((4 + padx, 4 + (h - self.fs * 1.2) / 2), self.text, font=f, fill=bg if self.style != "gold" else GOLD_TXT)
        else:
            d.rounded_rectangle([0, 4, tw + 2 * padx, 4 + h], radius=h // 2, fill=bg)
            d.text((padx, 4 + (h - self.fs * 1.25) / 2), self.text, font=f, fill=fg)
        self.img = im

class Chips(Row):  # several pills in a wrapped row, each with its own reveal time
    dynamic = True
    def __init__(self, items, size=26, style="soft", at=None, **kw):
        super().__init__(at, **kw); self.items, self.fs, self.style = items, size, style
        for txt, t in items: sfx("pop", t, 0.8, "chip: " + txt)
    def build(self, width, dark):
        f = font("mono", self.fs); padx, h = int(self.fs * .65), int(self.fs * 1.7)
        x = y = 0; self.pos = []
        for txt, t in self.items:
            w = f.getlength(txt) + 2 * padx
            if x and x + w > width: x, y = 0, y + h + 12
            self.pos.append((x, y, w, txt, t)); x += w + 12
        self.h = y + h + 6; self.w = width; self.f = f; self.ph = h; self.padx = padx
        self.img = Image.new("RGBA", (width, self.h), (0, 0, 0, 0))
    def key(self, t): return tuple(round(clamp((t - it[4]) / 0.3), 2) for it in self.pos)
    def frame(self, t):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for x, y, w, txt, t0 in self.pos:
            p = (t - t0) / 0.3
            if p <= 0: continue
            sc = 0.6 + 0.4 * ease_back(p)
            pill = Image.new("RGBA", (int(w) + 2, self.ph + 2), (0, 0, 0, 0)); d = ImageDraw.Draw(pill)
            bg = GOLD_SOFT if self.style == "soft" else GOLD
            d.rounded_rectangle([0, 0, w, self.ph], radius=self.ph // 2, fill=bg)
            d.text((self.padx, (self.ph - self.fs * 1.25) / 2), txt, font=self.f, fill=INK)
            if abs(sc - 1) > 0.01:
                pw, ph = max(1, int(pill.width * sc)), max(1, int(pill.height * sc))
                pill2 = pill.resize((pw, ph), Image.BILINEAR)
                im.alpha_composite(pill2, (int(x + (pill.width - pw) / 2), int(y + (pill.height - ph) / 2)))
            else:
                im.alpha_composite(pill, (int(x), int(y)))
        return im

class Counter(Row):
    dynamic = True
    def __init__(self, fmt, a, b, t0, dur, size=72, at=None, col=None, prefix_k=None, ticks=True, **kw):
        super().__init__(at, **kw); self.fmt, self.a, self.b, self.t0, self.dur, self.fs, self.col = fmt, a, b, t0, dur, size, col
        self.prefix_k = prefix_k
        if ticks:
            n = max(4, int(dur / 0.075))
            for i in range(n + 1):
                sfx("count", t0 + dur * i / n, 0.55 if i < n else 0.9, "counter %s" % fmt.format(n=b))
    def build(self, width, dark):
        self.width, self.dark = width, dark
        self.img = self.render(self.b)
    def val(self, t):
        p = ease_out((t - self.t0) / self.dur)
        return int(round(self.a + (self.b - self.a) * p))
    def render(self, v):
        f = font("black", self.fs)
        im = Image.new("RGBA", (self.width, int(self.fs * 1.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        txt = self.fmt.format(n=v)
        d.text((4, 0), txt, font=f, fill=self.col or (GOLD if self.dark else INK))
        return im
    def key(self, t): return self.val(t)
    def frame(self, t): return self.render(self.val(t))

class Bar(Row):
    dynamic = True
    def __init__(self, frac, t0, dur, at=None, **kw):
        super().__init__(at, **kw); self.frac, self.t0, self.dur = frac, t0, dur
    def build(self, width, dark):
        self.w = width; self.img = self.render(1)
    def render(self, p):
        im = Image.new("RGBA", (self.w, 26), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 4, self.w - 12, 22], radius=9, fill=LINE)
        fw = (self.w - 12) * self.frac * p
        if fw > 18: d.rounded_rectangle([0, 4, fw, 22], radius=9, fill=GOLD)
        return im
    def key(self, t): return round(ease_out((t - self.t0) / self.dur), 2)
    def frame(self, t): return self.render(ease_out((t - self.t0) / self.dur))

class Photo(Row):
    def __init__(self, path, h, credit, focus=0.3, at=None, **kw):
        super().__init__(at, **kw); self.path, self.h, self.credit, self.focus = path, h, credit, focus
    def build(self, width, dark):
        src = Image.open(S + "/assets/photos/" + self.path).convert("RGB")
        w = width - 12; r = max(w / src.width, self.h / src.height)
        im = src.resize((int(src.width * r + 1), int(src.height * r + 1)), Image.LANCZOS)
        x0 = (im.width - w) // 2; y0 = int((im.height - self.h) * self.focus)
        im = im.crop((x0, y0, x0 + w, y0 + self.h)).convert("RGBA")
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, self.h - 1], radius=18, fill=255)
        im.putalpha(m)
        f = font("monom", 15)
        lines, cur = [], ""
        for wd in self.credit.split(" "):
            if cur and f.getlength(cur + " " + wd) > w: lines.append(cur); cur = wd
            else: cur = (cur + " " + wd).strip()
        lines.append(cur)
        out = Image.new("RGBA", (width, self.h + 8 + 19 * len(lines)), (0, 0, 0, 0))
        out.alpha_composite(im, (0, 0))
        for i, ln in enumerate(lines):
            ImageDraw.Draw(out).text((2, self.h + 6 + 19 * i), ln, font=f, fill=(140, 140, 148, 255))
        self.img = out

class Placeholder(Row):
    def __init__(self, label, h=210, at=None, **kw):
        super().__init__(at, **kw); self.label, self.h = label, h
    def build(self, width, dark):
        w = width - 12
        im = Image.new("RGBA", (width, self.h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w, self.h - 1], radius=18, fill=(244, 244, 247, 255))
        for x in range(0, int(w), 26):  # dashed border
            d.line([x, 0, min(x + 14, w), 0], fill=(180, 180, 188, 255), width=3)
            d.line([x, self.h - 2, min(x + 14, w), self.h - 2], fill=(180, 180, 188, 255), width=3)
        for y in range(0, self.h, 26):
            d.line([0, y, 0, min(y + 14, self.h)], fill=(180, 180, 188, 255), width=3)
            d.line([w, y, w, min(y + 14, self.h)], fill=(180, 180, 188, 255), width=3)
        # simple image glyph
        cx, cy = w / 2, self.h / 2 - 22
        d.rounded_rectangle([cx - 34, cy - 26, cx + 34, cy + 26], radius=8, outline=(160, 160, 168, 255), width=4)
        d.polygon([(cx - 24, cy + 18), (cx - 4, cy - 4), (cx + 10, cy + 10), (cx + 18, cy + 2), (cx + 28, cy + 18)], fill=(160, 160, 168, 255))
        f = font("mono", 19)
        tw = f.getlength(self.label); d.text(((w - tw) / 2, cy + 40), self.label, font=f, fill=(120, 120, 128, 255))
        self.img = im

class Spacer(Row):
    def __init__(self, h): super().__init__(None); self.h = h
    def build(self, width, dark): self.img = Image.new("RGBA", (width, self.h), (0, 0, 0, 0))

class Custom(Row):
    """Dynamic row drawn by a function draw(img, draw, p_dict, t)."""
    dynamic = True
    def __init__(self, h, fn, keyfn, at=None, **kw):
        super().__init__(at, **kw); self.h, self.fn, self.keyfn = h, fn, keyfn
    def build(self, width, dark):
        self.w = width; self.img = Image.new("RGBA", (width, self.h), (0, 0, 0, 0))
    def key(self, t): return self.keyfn(t)
    def frame(self, t):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        self.fn(im, ImageDraw.Draw(im), t, self.w, self.h); return im

# ---------------------------------------------------------------- shadows / backgrounds
@functools.lru_cache(None)
def card_bg(w, h, style):
    pad = 40
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=30, fill=(0, 0, 0, 80))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    fill = {"card": CARD, "dark": DARK, "gold": (255, 246, 220, 244), "red": (255, 244, 244, 244)}[style]
    d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=30, fill=fill)
    if style == "gold": d.rounded_rectangle([pad, pad, pad + 10, pad + h], radius=5, fill=GOLD)
    if style == "red": d.rounded_rectangle([pad, pad, pad + 10, pad + h], radius=5, fill=RED)
    return im, pad

# ---------------------------------------------------------------- elements
ELEMS = []
class Card:
    def __init__(self, name, zone, y, t_in, t_out, rows, w=560, style="card", anim=None, sfx_in=None, frame_no=None, x=None, gap=12, padding=30):
        self.name, self.zone, self.y, self.t_in, self.t_out = name, zone, y, t_in, t_out
        self.rows, self.w, self.style, self.frame_no = rows, w, style, frame_no
        self.anim = anim or {"L": "slideL", "R": "slideR", "T": "drop"}[zone]
        dark = style == "dark"
        inner = w - 2 * padding - (10 if style in ("gold", "red") else 0)
        offx = padding + (10 if style in ("gold", "red") else 0)
        yy = padding; self.layout = []
        for r in rows:
            r.build(inner, dark)
            self.layout.append((r, offx, yy)); yy += r.size()[1] + gap
        self.h = yy - gap + padding
        self.bg, self.pad = card_bg(w, self.h, style)
        self.x = x if x is not None else (LX if zone == "L" else RX - w if zone == "R" else (W - w) // 2)
        sfx_in = sfx_in or ("whoosh" if self.anim in ("slideL", "slideR") else "pop")
        sfx(sfx_in, t_in, 0.8, "in: " + name)
        for r in rows:
            if r.at is not None and r.sfx_kind: sfx(r.sfx_kind, r.at, 0.9, "%s row" % name)
        self._cache_key = None; self._cache = None
        ELEMS.append(self)

    def bbox(self):  # full extent incl. shadow, at rest
        return (self.x - self.pad, self.y - self.pad, self.x + self.w + self.pad, self.y + self.h + self.pad)

    def compose(self, t):
        key = []
        for r, ox, oy in self.layout:
            if r.at is not None:
                p = clamp((t - r.at) / 0.3)
                key.append(round(p, 2))
            else: key.append(1)
            if r.dynamic: key.append(r.key(t))
        key = tuple(key)
        if key == self._cache_key: return self._cache
        im = self.bg.copy()
        for r, ox, oy in self.layout:
            p = 1.0 if r.at is None else (t - r.at) / 0.3
            if p <= 0: continue
            src = r.frame(t)
            if p < 1:
                a = clamp(p / 0.5)
                if r.anim == "stamp":
                    sc = 1.6 - 0.6 * ease_back(p, 1.2)
                elif r.anim == "pop":
                    sc = 0.6 + 0.4 * ease_back(p)
                else:
                    sc = 1.0
                dy = 16 * (1 - ease_back(p)) if r.anim == "rise" else 0
                if abs(sc - 1) > 0.01:
                    sw, sh = max(1, int(src.width * sc)), max(1, int(src.height * sc))
                    src2 = src.resize((sw, sh), Image.BILINEAR)
                    # anchor scale at the left-centre of the row
                    px, py = ox + self.pad, oy + self.pad + int((src.height - sh) / 2)
                    src = src2
                else:
                    px, py = ox + self.pad, oy + self.pad + int(dy)
                src = with_alpha(src, a)
                paste(im, src, px, py)
            else:
                paste(im, src, ox + self.pad, oy + self.pad)
        self._cache_key, self._cache = key, im
        return im

    def state(self, t):
        """returns (alpha, dx, dy, scale) or None"""
        if t < self.t_in or t >= self.t_out: return None
        pi = (t - self.t_in) / 0.3
        po = clamp((t - (self.t_out - 0.22)) / 0.22)
        a = clamp(pi / 0.45) * (1 - po)
        dx = dy = 0; sc = 1.0
        e = ease_back(pi)
        if self.anim == "slideL": dx = -150 * (1 - e) - 50 * ease_out(po)
        elif self.anim == "slideR": dx = 150 * (1 - e) + 50 * ease_out(po)
        elif self.anim == "drop": dy = -30 * (1 - e) - 20 * ease_out(po)
        elif self.anim == "pop": sc = 0.7 + 0.3 * e - 0.05 * ease_out(po)
        return a, dx, dy, sc

    def render(self, canvas, t):
        st = self.state(t)
        if not st: return
        a, dx, dy, sc = st
        if a <= 0.004: return
        im = self.compose(t)
        x = self.x - self.pad + dx; y = self.y - self.pad + dy
        if abs(sc - 1) > 0.005:
            sw, sh = int(im.width * sc), int(im.height * sc)
            x += (im.width - sw) / 2; y += (im.height - sh) / 2
            im = im.resize((sw, sh), Image.BILINEAR)
        paste(canvas, with_alpha(im, a), int(round(x)), int(round(y)))

def with_alpha(im, a):
    if a >= 0.999: return im
    arr = np.array(im); arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def paste(dst, src, x, y):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.width, x + src.width), min(dst.height, y + src.height)
    if x1 <= x0 or y1 <= y0: return
    if (x0, y0, x1, y1) != (x, y, x + src.width, y + src.height):
        src = src.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    dst.alpha_composite(src, (x0, y0))

# ---------------------------------------------------------------- special elements
class FreeElem:
    """Element drawn by a function each frame; bbox given for audits."""
    def __init__(self, name, t_in, t_out, box, fn, frame_no=None, zone="T"):
        self.name, self.t_in, self.t_out, self._box, self.fn, self.frame_no, self.zone = name, t_in, t_out, box, fn, frame_no, zone
        ELEMS.append(self)
    def bbox(self): return self._box
    def render(self, canvas, t):
        if self.t_in <= t < self.t_out: self.fn(canvas, t)

def build_timeline():
    G = "gold"
    # ---------- Frame 1: greeting + colour grade bit
    t_wait = T("wait", 3); t_adj = T("adjust", 6); t_grade = 260 / 30.0; t_ok = T("okay", 8.5); t_lets = T("lets get started", 10)
    Card("Greeting", "L", 190, 1.44, t_wait - 0.1, [
        K("Salam · 3 languages"),
        Hd("Assalamu'alaikum", 50),
        Custom(64, draw_greet, lambda t: 0),
    ], w=520, anim="pop", frame_no=1)

    def slider_rows(t):
        p = ease_inout((t - t_adj) / (t_grade - t_adj))
        return p
    def draw_sliders(im, d, t, w, h):
        p = slider_rows(t)
        f = font("mono", 20)
        for i, (lab, a, b) in enumerate([("EXPOSURE", .45, .55), ("CONTRAST", .30, .72), ("SATURATION", .22, .80)]):
            y = 8 + i * 58
            d.text((0, y), lab, font=f, fill=MUTED)
            v = a + (b - a) * p
            d.text((w - 80, y), "%+.0f" % ((v - .5) * 100), font=f, fill=INK)
            yy = y + 34
            d.rounded_rectangle([0, yy, w - 14, yy + 8], radius=4, fill=LINE)
            d.rounded_rectangle([0, yy, (w - 14) * v, yy + 8], radius=4, fill=GOLD)
            cx = (w - 14) * v
            d.ellipse([cx - 11, yy - 7, cx + 11, yy + 15], fill=WHITE, outline=INK, width=3)
    Card("Colour grade panel", "R", 200, T("colour", 4), t_lets - 0.12, [
        K("Colour grade"),
        Custom(176, draw_sliders, lambda t: round(slider_rows(t), 3)),
        Chip("✓ GRADED", at=t_grade, style="gold", size=34, stamp=True),
    ], w=470, frame_no=1)
    Card("S-LOG tag", "T", 40, t_wait, t_grade, [Chip("● S-LOG · UNGRADED", style="red", size=20)], w=330, style="dark", padding=14, frame_no=1)

    # ---------- Frame 2
    Card("Let's get started", "L", 300, t_lets, T("let me ask", 11.5) - 0.12, [
        Hd("Let's get [started]", 58, fname="black")], w=560, anim="pop", frame_no=2)

    # ---------- Frame 3-4: question, life plan that cracks, big idea
    t_q = T("question", 13); t_have = T("have you ever", 13.5); t_true = T("true leadership", 17); t_fall = T("fall apart", 20); t_hi = T("hi", 21.5)
    Card("Question", "L", 200, t_q - 0.1, t_true - 0.15, [
        K("Question for you"),
        Hd("Have you ever planned your life [so carefully]?", 46),
    ], w=560, frame_no=3)
    Card("Big idea", "L", 200, t_true, t_hi - 0.1, [
        K("The big idea"),
        Hd("Leadership begins when the [plan falls apart]", 50),
    ], w=560, style="card", frame_no=4)
    plan = PlanCard(T("ever", 14), t_fall, t_hi - 0.05, T("planned", 14.5), T("life", 15), T("carefully", 15.5))
    sfx("thump", t_fall, 1.0, "PLAN cracks")
    sfx("whoosh", t_fall + 0.35, 0.6, "PLAN falls")

    # ---------- Frame 5: intro
    t_cap = T("capricorn", 25); t_grow = T("growing up", 33)
    Card("Name card", "L", 230, t_hi, t_grow - 0.15, [
        K("Hi, I'm"),
        Hd("Nur Anis Nasuha binti Rosli", 44),
        P("Liberal Studies · UKM"),
    ], w=600, frame_no=5)
    Card("Capricorn", "R", 160, t_cap, t_grow - 0.15, [K("Star sign"), Hd("Capricorn", 36, fname="disp")], w=330, anim="pop", frame_no=5, padding=22)
    Card("Creativity + detail", "R", 300, T("blending", 27), t_grow - 0.15, [
        K("I love blending"),
        Hd("Creativity + [detail]", 42),
        Chips([("MULTIMEDIA", T("multimedia", 29)), ("DIGITAL MARKETING", T("digital", 30)), ("IT", T("it", 31)), ("JOURNALISM", T("journalism", 32))]),
    ], w=560, frame_no=5)

    # ---------- Frame 6
    t_when = T("when i took", 39)
    Card("Mum = teacher", "L", 230, T("my mom", 34), t_when - 0.15, [K("Growing up"), Hd("Mum = [teacher]", 54)], w=480, frame_no=6)
    Card("Priorities", "R", 260, T("education", 36), t_when - 0.15, [
        K("Top priorities"),
        Chips([("EDUCATION", T("education", 36)), ("DISCIPLINE", T("discipline", 37))], size=30, style="gold")], w=480, frame_no=6)

    # ---------- Frame 7
    t_thr = T("i thrive", 46)
    Card("16Personalities", "L", 210, T("16 personalities", 40), t_thr - 0.12, [
        K("Test 1"), Hd("16Personalities", 36), Hd("→ [ISTJ]", 64, fname="black", at=T("istj", 42)),
        P("“Like looking in a mirror”", at=T("like looking", 45))], w=470, frame_no=7)
    Card("DOPE test", "R", 210, T("doctors", 41), t_thr - 0.12, [
        K("Test 2"), Hd("DOPE", 36), Hd("→ [OWL]", 64, fname="black", at=T("owl", 43))], w=420, frame_no=7)

    # ---------- Frame 8
    t_after = T("after finishing", 51)
    Card("Logic-plan-goals", "R", 220, T("logic", 47) - 0.1, t_after - 0.12, [
        K("How I work"),
        Hd("Logic", 46),
        Hd("→ Solid [plan]", 46, at=T("plan", 49)),
        Hd("→ Goals", 46, at=T("goals", 50)),
    ], w=440, frame_no=8)

    # ---------- Frame 9
    t_later = T("later", 63)
    Card("Diploma", "L", 210, T("diploma", 52), t_later - 0.12, [
        K("Diploma"), Hd("Multimedia", 46), P("UniKL MIIT")], w=460, frame_no=9)
    Card("PNB / ASNB", "R", 200, T("spent", 55), t_later - 0.12, [
        K("Work · almost 1 year"), Hd("Marketing for ASNB", 42), P("Permodalan Nasional Berhad (PNB)"),
        Chip("DETAIL-ORIENTED", at=T("very detailed", 62) - 0.1, style="gold", size=26)], w=540, frame_no=9)

    # ---------- Frame 10
    t_atf = T("at first", 71)
    Card("UKM year 1", "L", 210, T("first year", 64), t_atf - 0.12, [
        K("UKM · Year 1"), Hd("Liberal Studies", 46)], w=460, frame_no=10)
    Card("Head of Media Exco", "R", 210, T("head of the media", 67), t_atf - 0.12, [
        K("Annual event · Kolej Keris Mas"), Hd("Head of [Media Exco]", 44)], w=560, frame_no=10)

    # ---------- Frame 11
    t_real = T("realizing", 79.5)
    Card("Perfectionism = problem", "L", 200, T("my corporate", 72), t_real - 0.12, [
        K("At first", col=RED), Hd("Corporate perfectionism = {problem}", 46)], w=560, style="red", frame_no=11)
    Card("Control every design", "R", 230, T("anxious", 74.5), t_real - 0.12, [
        Chk("Anxious delegating tasks", at=T("delegating", 75), mark="x", sfx_kind="pop"),
        Hd("Control {every} design", 46, at=T("control", 77))], w=520, frame_no=11)

    # ---------- Frame 12
    t_icr = T("i created", 86.5)
    Card("Burning out", "L", 220, t_real, t_icr - 0.12, [
        K("Micromanaging", col=RED), Hd("= {burning out}", 50, at=T("burning", 81)),
        P("…and holding my team back", at=T("holding", 82))], w=520, style="red", frame_no=12)
    Card("Controlling to empowering", "R", 230, T("shifted", 84) - 0.2, t_icr - 0.12, [
        K("I shifted from"),
        Strike("Controlling", strike_at=T("controlling", 85), size=44),
        Hd("→ [Empowering]", 50, at=T("empowering", 85.5))], w=480, frame_no=12)

    # ---------- Frame 13
    t_res = T("as a result", 92)
    Card("The fix", "L", 200, t_icr, t_res - 0.12, [
        K("The fix"),
        Chk("Clear creative brief", at=T("clear creative", 87.5)),
        Chk("Easy templates", at=T("templates", 89)),
        Chk("Full team ownership", at=T("full ownership", 90.5))], w=520, frame_no=13)

    # ---------- Frame 14
    t_taught = T("that taught", 98.5)
    PhoneGrid(T("instagram", 93.5), t_taught - 0.12, T("on time", 94.5))
    Card("Launched on time stamp", "R", 690, T("on time", 94.5) - 0.1, t_taught - 0.12, [
        Chip("✓ LAUNCHED ON TIME", style="gold", size=26, stamp=True, at=T("on time", 94.5))], w=380, anim="pop", sfx_in="pop", padding=16, frame_no=14)
    Card("Team-owned work", "L", 240, T("my team did", 95.5), t_taught - 0.12, [
        K("Result"), Hd("[Team-owned] work", 46), P("Amazing work, on their own")], w=500, frame_no=14)

    # ---------- Frame 15
    t_made = T("that made me", 107)
    Card("Lesson learned tag", "T", 40, t_taught, t_made - 0.12, [Chip("LESSON LEARNED", style="gold", size=20)], w=290, style="dark", padding=14, frame_no=15)
    Card("Leadership is not", "L", 200, T("true leadership", 100), t_made - 0.12, [
        K("True leadership"), Hd("{≠} doing everything yourself", 46)], w=560, frame_no=15)
    Card("Systems + trust", "R", 240, T("building", 103.8), t_made - 0.12, [
        K("It is"), Hd("Clear [systems]", 46), Hd("+ [Trust] your team", 46, at=T("trusting", 105))], w=500, frame_no=15)

    # ---------- Frame 16
    t_like = T("like me", 115)
    t_tome = T("to me", 124)
    Card("Real leadership", "L", 220, T("real leadership", 108), t_like - 0.12, [
        K("Real leadership"), Hd("Under [pressure]", 50)], w=460, frame_no=16)
    Card("Syed Saddiq photo", "R", 150, T("my idol", 111.5), t_tome - 0.12, [
        K("My idol"),
        Photo("saddiq.jpg", 300, "Photo: US Embassy Kuala Lumpur · Public domain · Wikimedia Commons", focus=0.12),
        Hd("Syed Saddiq", 40),
        Counter("AGE {n}", 0, 33, T("33", 113.5), 0.7, size=34, col=GOLD_TXT, at=T("33", 113.5) - 0.05),
    ], w=460, frame_no=16)

    # ---------- Frame 17
    Card("Not a nepo baby", "L", 170, t_like, t_tome - 0.12, [
        K("Like me"), Strike("Nepo baby", strike_at=T("baby", 116.8), size=48),
        Chip("NOT A NEPO BABY", at=T("baby", 116.8) + 0.25, style="red", size=24, stamp=True)], w=480, frame_no=17)
    Card("Mother a teacher", "L", 470, T("mother", 118.5), t_tome - 0.12, [
        K("His mother"), Hd("A [teacher] too", 44),
        Chip("SUCCESS IS EARNED", at=T("earned", 122.5), style="gold", size=24)], w=480, frame_no=17)

    # ---------- Frame 18
    t_ment = T("mentally", 131)
    Card("Corporate Athlete", "L", 210, T("corporate athlete", 125), t_ment - 0.12, [
        K("To me, he is a true"), Hd("[Corporate Athlete]", 54, fname="black"),
        P("Trained to survive politics", at=T("survive", 129.5))], w=560, frame_no=18)
    PillarGrid(T("trains", 126.5), t_ment - 0.12,
               [T("mind", 127), T("body", 128), T("emotions", 128.5), T("values", 129.5)])

    # ---------- Pillar sections
    t_at = T("at", 133.5)
    t_that = T("that is the well", 139)
    Card("Pillar MIND", "L", 210, t_ment, t_that - 0.12, [
        K("Pillar 1"), Hd("[Mind]", 72, fname="black"), P("Super sharp", at=T("super sharp", 132.5))], w=420, frame_no=19)
    Card("Debating champion", "R", 200, T("debate", 135), t_that - 0.12, [
        K("At UIA"), Hd("Asian Debating [Champion]", 44),
        Counter("{n}", 2000, 2015, T("2015", 137), 0.6, size=56, col=GOLD_TXT, at=T("2015", 137) - 0.05)], w=520, frame_no=19)

    t_ms = T("mental strength", 145)
    Card("My goal at UKM", "L", 200, T("well rounded", 139.5), t_ms - 0.12, [
        K("My goal at UKM"), Hd("Well-rounded student", 44),
        Chk("Lead outside class", at=T("leading outside", 142)),
        Chk("Keep strong grades", at=T("strong grades", 144))], w=540, frame_no=20)

    t_hon = T("honestly", 151.5)
    Card("Sacrifice", "L", 220, t_ms, t_hon - 0.12, [
        K("Mental strength"), Hd("= [Sacrifice]", 56, fname="black"),
        Chip("TO SERVE MALAYSIA", at=T("serve", 150.5), style="gold", size=24)], w=480, frame_no=21)
    Card("Oxford", "R", 160, T("oxford", 148.5), t_hon - 0.12, [
        K("Oxford scholarship"),
        Photo("oxford.jpg", 250, "Photo: Julian Herzog · CC BY 4.0 · Wikimedia Commons", focus=0.5),
        Chip("DECLINED ×2", at=T("twice", 149.5), style="red", size=30, stamp=True)], w=480, frame_no=21)

    t_iwould = T("i would study", 158)
    Card("I'd take it", "L", 220, t_hon, t_iwould - 0.12, [
        K("Honestly…"), Hd("If I got into Oxford, I'd take it in a [heartbeat]", 46)], w=560, frame_no=22)
    ECGCard(T("if i got", 154.5), T("heartbeat", 157), t_iwould - 0.12)

    t_why = T("why give", 174.5)
    Card("Logical path", "R", 160, t_iwould, t_why - 0.12, [
        K("The logical path"),
        Hd("Oxford", 42), Hd("→ Back to Malaysia", 42, at=T("back to malaysia", 159.5)),
        Hd("→ Top management", 42, at=T("top management", 161)),
        P("GLC / MNC", at=T("glc", 162)),
        Chip("= THE LOGICAL PATH", at=T("logical", 165), style="gold", size=24)], w=520, frame_no=23)
    Card("You get", "L", 200, T("you get better", 166), t_why - 0.12, [
        K("You get"),
        Chk("Physical & mental comfort", at=T("mental comfort", 168)),
        Chk("Huge bonuses", at=T("huge bonuses", 169.5)),
        Chk("Way more money", at=T("way more money", 170.5)),
        P("…what most brilliant students choose", at=T("most brilliant", 172))], w=540, frame_no=23)

    t_img = T("imagine", 180)
    Card("Headache", "L", 220, t_why, t_img - 0.12, [
        K("So why…"), Hd("Give yourself a [headache]?", 50)], w=520, frame_no=24)
    Card("Personal profit = 0", "R", 220, T("fighting", 176), t_img - 0.12, [
        K("Personal profit"),
        Hd("{= 0}", 96, fname="black", at=T("0", 178.3), anim="stamp", sfx_kind="thump")], w=380, frame_no=24)

    t_phys = T("physically", 187)
    Card("Selfish vs selfless", "L", 200, T("chosen", 182), t_phys - 0.12, [
        K("Imagine if he chose"),
        Strike("Selfish", strike_at=T("selfless", 184) - 0.2, size=52, at=T("selfish", 182.8)),
        Hd("→ [Selfless]", 52, at=T("selfless", 184))], w=440, frame_no=25)
    Card("People of Muar", "R", 240, T("what would have", 184.8), t_phys - 0.12, [
        K("The people of Muar"), Hd("What would have happened?", 44)], w=500, frame_no=25)

    t_also = T("he also used", 201)
    Card("Pillar BODY", "L", 180, t_phys, t_also - 0.12, [
        K("Pillar 2"), Hd("[Body]", 72, fname="black"), P("Incredible stamina", at=T("stamina", 189))], w=420, frame_no=26)
    Card("RM160,000 raised", "L", 470, T("raising", 197.5), t_also - 0.12, [
        K("Raised for his people"),
        Counter("RM{n:,}+", 0, 160000, T("160", 198), 1.1, size=58, col=INK)], w=440, frame_no=26)
    RouteCard(T("2024", 190.5), t_also - 0.12, T("ran", 193), T("parliament", 195.3))

    t_emo = T("emotionally", 207)
    Card("Image to funding", "L", 220, t_also, t_emo - 0.12, [
        K("Smart move"), Hd("His [image]", 44),
        Hd("→ Modelling for PrimaValet", 40, at=T("primaveli", 204) - 0.1),
        Hd("→ [Funds] political work", 40, at=T("find", 205) - 0.1)], w=560, frame_no=27)
    Card("PrimaValet placeholder", "R", 240, T("modelling", 203.4), t_emo - 0.12, [
        K("PrimaValet campaign"), Placeholder("PHOTO PLACEHOLDER · ADD IMAGE")], w=440, frame_no=27)

    t_he = T("he deeply", 211)
    Card("Pillar EMOTIONS", "L", 200, t_emo, t_he - 0.12, [
        K("Pillar 3"), Hd("[Emotions]", 68, fname="black"), P("Strength that stands out", at=T("stands out", 208.5))], w=460, frame_no=28)
    Card("Minister at 26", "R", 240, T("even as a minister", 209), t_he - 0.12, [
        K("Minister at"), Counter("{n}", 0, 26, T("minister", 209.8), 0.5, size=96, col=GOLD_TXT)], w=300, frame_no=28)

    t_dur = T("during the 2020", 218.8)
    Card("Mahathir", "R", 150, T("his idol", 212.5), t_dur - 0.12, [
        K("His idol"),
        Photo("mahathir.jpg", 300, "Photo: kremlin.ru · CC BY 4.0 · Wikimedia Commons", focus=0.15),
        Hd("Tun Dr. Mahathir", 40)], w=440, frame_no=29)
    Card("Change + respect", "L", 220, T("proving", 214.5), t_dur - 0.12, [
        K("Young leaders can"),
        Hd("Push for [change]", 46, at=T("change", 216.5)),
        Hd("+ Honour [veterans]", 46, at=T("honouring", 217.3))], w=520, frame_no=29)

    t_fin = T("finally", 225)
    Card("Sheraton Move", "L", 210, t_dur, t_fin - 0.12, [
        K("2020"), Hd("Sheraton Move", 46),
        Hd("+ years of court trials", 38, at=T("years of court", 221))], w=520, frame_no=30)
    Card("Calm in public", "R", 260, T("stayed calm", 223.2), t_fin - 0.12, [
        Hd("Stayed [calm] in public", 46)], w=460, anim="pop", frame_no=30)

    t_even = T("even on a personal", 234)
    Card("Pillar VALUES", "L", 210, t_fin, t_even - 0.12, [
        K("Pillar 4"), Hd("[Values]", 72, fname="black")], w=420, frame_no=31)
    Card("Undi18", "R", 190, T("passing", 226), t_even - 0.12, [
        K("Undi18 · 2019"), P("Voting age lowered to 18", size=28, col=INK),
        Counter("{n}%+", 0, 50, T("50", 230.3), 0.8, size=72, col=GOLD_TXT, at=T("gave young", 229) ),
        P("of the voting power", at=T("50", 230.3)),
        Bar(0.5, T("50", 230.3), 0.8, at=T("50", 230.3))], w=500, frame_no=31)

    t_inst = T("instead of luxury", 241.5)
    Card("10 Oct 2026", "L", 220, T("married", 236), t_inst - 0.12, [
        K("Personal level"), Hd("Married Bella Astillah", 44), P("10 October 2026", at=T("10 october", 238), col=INK)], w=520, frame_no=32)
    Card("Broke old traditions", "R", 260, T("broke", 240) - 0.1, t_inst - 0.12, [
        Chip("BROKE OLD TRADITIONS", style="red", size=28, stamp=True, at=T("broke", 240) - 0.05)], w=500, anim="pop", frame_no=32)

    t_asan = T("as an", 250.5)
    Card("Hantaran", "R", 170, t_inst, t_asan - 0.12, [
        K("His hantaran"),
        Strike("Luxury bags", strike_at=T("bags", 242.3) + 0.15, size=44),
        Counter("RM{n:,} EPF", 0, 100000, T("100", 243.8), 0.9, size=46, col=INK, at=T("100", 243.8) - 0.05, sfx_kind="tick"),
        Chk("Master's degree · Taylor's", at=T("masters", 248))], w=560, frame_no=33)

    t_since = T("since id", 256) if True else None
    Card("ISTJ practical", "L", 220, t_asan, t_since - 0.12, [
        K("As an"), Hd("ISTJ ✓", 40), Hd("→ [Practical]", 54, fname="black", at=T("practical", 253.5))], w=440, frame_no=34)
    Card("Owl forward-thinking", "R", 220, T("outward", 252), t_since - 0.12, [
        K("And an"), Hd("Owl ✓", 40), Hd("→ [Forward-thinking]", 44, fname="black", at=T("forward", 254.3))], w=600, frame_no=34)

    t_asi = T("as i build", 262)
    Card("Balance", "L", 220, t_since, t_asi - 0.12, [
        K("True leadership"), Hd("= [Balance]", 64, fname="black")], w=440, frame_no=35)
    BalanceCard(T("balancing", 258.5), t_asi - 0.12, [T("mind", 259), T("body", 260), T("emotions", 260.5), T("value", 261)])

    t_lets2 = T("lets not", 266.5)
    Card("My own path", "L", 220, t_asi, t_lets2 - 0.12, [
        K("My path"), Hd("Building my own path @ [UKM]", 46)], w=520, frame_no=36)
    Card("Role model", "R", 200, T("he is the role", 264.5), t_lets2 - 0.12, [
        K("Role model"),
        Photo("saddiq.jpg", 210, "Photo: US Embassy Kuala Lumpur · Public domain · Wikimedia Commons", focus=0.1)], w=380, frame_no=36)

    t_thank = T("thank you", 273)
    Card("Not just titles", "L", 200, t_lets2, t_thank - 0.12, [
        K("Let's not just"), Strike("Chase titles", strike_at=T("scientists", 267.6) + 0.2, size=46, at=T("chase", 267.4)),
        Hd("Grow in our [20s]", 46, at=T("growing", 269.4))], w=480, frame_no=37)
    Card("Build real skills", "R", 240, T("building", 271), t_thank - 0.12, [
        Hd("Build [real skills] to lead", 46)], w=480, frame_no=37)

    Card("Thank you", "L", 220, t_thank, NF / FPS + 1, [
        K("Thank you"), Hd("Nur Anis Nasuha", 50), P("Liberal Studies · UKM")], w=520, anim="pop", frame_no=38)

    TopBar()
    PillarTracker(T("survive", 129.5) + 0.5, t_asi - 0.12, t_ment, t_phys, t_emo, t_fin, t_since,
                  [T("mind", 259), T("body", 260), T("emotions", 260.5), T("value", 261)])

# --- greeting multi-script line
def draw_greet(im, d, t, w, h):
    x = 2
    for txt, fn in [("大家好", "sc"), (" · ", "semi"), ("வணக்கம்", "tamil")]:
        f = font(fn, 38); d.text((x, 6), txt, font=f, fill=INK); x += f.getlength(txt) + 4

# --- PLAN card that gets ticked, cracks and falls
class PlanCard:
    def __init__(self, t_in, t_crack, t_out, *ticks):
        self.name, self.frame_no, self.zone = "My life plan (cracks & falls)", 3, "R"
        self.card = Card("My life plan", "R", 200, t_in, t_out + 10, [
            K("My life plan"),
            Chk("Study", at=ticks[0]), Chk("Career", at=ticks[1]), Chk("Goals", at=ticks[2])], w=420, frame_no=3)
        ELEMS.remove(self.card)
        self.t_in, self.t_out, self.tc = t_in, t_out, t_crack
        ELEMS.append(self)
    def bbox(self): return self.card.bbox()
    def render(self, canvas, t):
        if not (self.t_in <= t < self.t_out): return
        if t < self.tc:
            self.card.render(canvas, t); return
        im = self.card.compose(t).copy()
        p = (t - self.tc)
        d = ImageDraw.Draw(im)
        cx = im.width // 2
        pts = [(cx - 10, 30), (cx + 18, im.height * .3), (cx - 14, im.height * .55), (cx + 12, im.height * .8), (cx - 6, im.height - 30)]
        d.line(pts, fill=RED, width=6, joint="curve")
        x0, y0 = self.card.x - self.card.pad, self.card.y - self.card.pad
        if p < 0.3:
            shake = int(6 * math.sin(p * 90))
            paste(canvas, im, x0 + shake, y0); return
        q = ease_inout((p - 0.3) / 0.45)
        a = 1 - q
        if a <= 0: return
        L = im.crop((0, 0, cx, im.height)).rotate(-14 * q, resample=Image.BILINEAR, expand=False)
        R = im.crop((cx, 0, im.width, im.height)).rotate(14 * q, resample=Image.BILINEAR, expand=False)
        drop = int(160 * q * q)
        paste(canvas, with_alpha(L, a), x0 - int(30 * q), y0 + drop)
        paste(canvas, with_alpha(R, a), x0 + cx + int(30 * q), y0 + drop)

class PhoneGrid:
    def __init__(self, t_in, t_out, t_stamp):
        self.name, self.frame_no, self.zone = "Instagram 3x3 feed (phone)", 14, "R"
        self.t_in, self.t_out, self.ts = t_in, t_out, t_stamp
        self.x, self.y, self.w, self.h = RX - 300, 170, 300, 440
        for i in range(9): sfx("pop", t_in + 0.08 + i * 0.06, 0.35, "feed tile")
        sfx("whoosh", t_in, 0.7, "phone slide-in")
        frame = Image.new("RGBA", (self.w + 80, self.h + 80), (0, 0, 0, 0))
        sh = Image.new("RGBA", frame.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([40, 52, 40 + self.w, 52 + self.h], radius=48, fill=(0, 0, 0, 90))
        frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([40, 40, 40 + self.w, 40 + self.h], radius=48, fill=(22, 22, 28, 255))
        d.rounded_rectangle([52, 52, 28 + self.w, 28 + self.h], radius=38, fill=(250, 250, 252, 255))
        d.rounded_rectangle([40 + self.w / 2 - 46, 62, 40 + self.w / 2 + 46, 82], radius=10, fill=(22, 22, 28, 255))
        f = font("disp", 20); d.text((118, 100), "our_event", font=f, fill=INK)
        d.ellipse([68, 96, 108, 136], fill=GOLD)
        f2 = font("mono", 16)
        for i, (n, l) in enumerate([("9", "posts"), ("1.2k", "fans")]):
            d.text((118 + i * 72, 124), n + " " + l[:5 if i else 5], font=f2, fill=MUTED)
        self.frame = frame
        cols = [(245, 189, 35), (40, 40, 48), (232, 220, 200), (226, 64, 70), (250, 240, 214), (70, 120, 200), (30, 30, 36), (245, 189, 35), (210, 210, 218)]
        self.tiles = []
        ts = (self.w - 24 - 8) / 3
        for i, c in enumerate(cols):
            tile = Image.new("RGBA", (int(ts), int(ts)), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
            td.rounded_rectangle([0, 0, ts - 1, ts - 1], radius=8, fill=c + (255,))
            fg = INK if sum(c) > 400 else GOLD
            k = i % 3
            if k == 0: td.ellipse([ts * .3, ts * .3, ts * .7, ts * .7], outline=fg, width=6)
            elif k == 1: td.rectangle([ts * .28, ts * .42, ts * .72, ts * .58], fill=fg)
            else: td.polygon([(ts * .3, ts * .7), (ts * .5, ts * .3), (ts * .7, ts * .7)], fill=fg)
            self.tiles.append((tile, 40 + 12 + 4 + (i % 3) * (ts + 4), 40 + 112 + (i // 3) * (ts + 4)))
        self.stamp = Chip("✓ LAUNCHED ON TIME", style="gold", size=24, stamp=True); self.stamp.build(320, False)
        ELEMS.append(self)
    def bbox(self): return (self.x - 40, self.y - 40, self.x + self.w + 40, self.y + self.h + 40)
    def render(self, canvas, t):
        if not (self.t_in <= t < self.t_out): return
        pi = (t - self.t_in) / 0.3; po = clamp((t - (self.t_out - 0.22)) / 0.22)
        a = clamp(pi / 0.45) * (1 - po); dx = 150 * (1 - ease_back(pi)) + 50 * ease_out(po)
        im = self.frame.copy()
        for i, (tile, tx, ty) in enumerate(self.tiles):
            p = (t - self.t_in - 0.08 - i * 0.06) / 0.25
            if p <= 0: continue
            sc = 0.5 + 0.5 * ease_back(p)
            tl = tile.resize((max(1, int(tile.width * sc)), max(1, int(tile.height * sc))), Image.BILINEAR) if sc != 1 else tile
            paste(im, with_alpha(tl, clamp(p * 2)), int(tx + (tile.width - tl.width) / 2), int(ty + (tile.height - tl.height) / 2))
        ps = (t - self.ts) / 0.3
        if False:
            sc = 1.6 - 0.6 * ease_back(ps, 1.2)
            st = self.stamp.img
            st2 = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
            paste(im, with_alpha(st2, clamp(ps * 2)), int(40 + 10 + (st.width - st2.width) / 2), int(40 + 470 + (st.height - st2.height) / 2))
        paste(canvas, with_alpha(im, a), int(self.x - 40 + dx), self.y - 40)

class PillarGrid:
    LABELS = ["MIND", "BODY", "EMOTIONS", "VALUES"]
    def __init__(self, t_in, t_out, times):
        self.name, self.frame_no, self.zone = "Corporate-athlete pillars 2x2", 18, "R"
        self.t_in, self.t_out, self.times = t_in, t_out, times
        self.x, self.y = RX - 500, 220
        for l, tt in zip(self.LABELS, times): sfx("pop", tt, 0.85, "pillar " + l)
        ELEMS.append(self)
        self.tiles = []
        for i, l in enumerate(self.LABELS):
            bg, pad = card_bg(240, 150, "card")
            im = bg.copy(); d = ImageDraw.Draw(im)
            draw_pillar_icon(d, pad + 30, pad + 26, i, 46)
            d.text((pad + 26, pad + 92), l, font=font("mono", 26), fill=INK)
            d.text((pad + 190, pad + 22), "0%d" % (i + 1), font=font("mono", 18), fill=MUTED)
            self.tiles.append((im, pad))
    def bbox(self): return (self.x - 40, self.y - 40, self.x + 500 + 40, self.y + 320 + 40)
    def render(self, canvas, t):
        if not (self.t_in <= t < self.t_out): return
        po = clamp((t - (self.t_out - 0.22)) / 0.22)
        for i, ((im, pad), tt) in enumerate(zip(self.tiles, self.times)):
            p = (t - tt) / 0.3
            if p <= 0: continue
            sc = (0.6 + 0.4 * ease_back(p)) * (1 - 0.05 * po)
            a = clamp(p * 2) * (1 - po)
            x = self.x + (i % 2) * 260 - pad; y = self.y + (i // 2) * 170 - pad
            im2 = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR) if abs(sc - 1) > .005 else im
            paste(canvas, with_alpha(im2, a), int(x + (im.width - im2.width) / 2), int(y + (im.height - im2.height) / 2))

def draw_pillar_icon(d, x, y, i, s, col=GOLD):
    if i == 0:   # mind: brain-ish circle with spark
        d.ellipse([x, y, x + s, y + s], outline=col, width=6); d.line([x + s / 2, y + 8, x + s / 2, y + s - 8], fill=col, width=5)
    elif i == 1:  # body: bolt
        d.polygon([(x + s * .55, y), (x + s * .15, y + s * .58), (x + s * .45, y + s * .58), (x + s * .35, y + s), (x + s * .85, y + s * .38), (x + s * .55, y + s * .38)], fill=col)
    elif i == 2:  # emotions: heart
        d.ellipse([x, y + 4, x + s * .55, y + s * .55], fill=col); d.ellipse([x + s * .45, y + 4, x + s, y + s * .55], fill=col)
        d.polygon([(x + 2, y + s * .38), (x + s - 2, y + s * .38), (x + s / 2, y + s)], fill=col)
    else:        # values: diamond
        d.polygon([(x + s / 2, y), (x + s, y + s / 2), (x + s / 2, y + s), (x, y + s / 2)], fill=col)

class ECGCard:
    def __init__(self, t_in, t_beat, t_out):
        self.name, self.frame_no, self.zone = "Heartbeat line ♥", 22, "R"
        self.c = Card("Heartbeat", "R", 260, t_in, t_out, [
            K("In a heartbeat"),
            Custom(150, self.draw, lambda t: round(clamp((t - t_in) / (t_beat - t_in + 0.3)), 2) if t < t_beat + 0.6 else round(min(1.0, (t - t_beat) / 0.3), 2) + 2)], w=460, frame_no=22)
        self.t_in, self.tb = t_in, t_beat
        sfx("pop", t_beat, 0.9, "heart pop")
    def draw(self, im, d, t, w, h):
        p = clamp((t - self.t_in) / (self.tb - self.t_in + 0.3))
        pts = []
        N = 160
        for i in range(int(N * p) + 1):
            u = i / N; x = u * (w - 70)
            ph = (u * 3) % 1
            yv = 0
            if 0.40 < ph < 0.46: yv = -18
            elif 0.46 < ph < 0.52: yv = 55
            elif 0.52 < ph < 0.58: yv = -60
            elif 0.58 < ph < 0.64: yv = 20
            pts.append((x, h / 2 - yv * 0.9))
        if len(pts) > 1: d.line(pts, fill=RED, width=6, joint="curve")
        q = (t - self.tb) / 0.3
        if q > 0:
            s = 46 * (0.6 + 0.4 * ease_back(q)); cx, cy = w - 36, h / 2
            d.ellipse([cx - s / 2, cy - s / 2, cx, cy], fill=RED); d.ellipse([cx - s * 0.05, cy - s / 2, cx + s / 2, cy], fill=RED)
            d.polygon([(cx - s / 2 + 1, cy - s * .2), (cx + s / 2 - 1, cy - s * .2), (cx, cy + s * .55)], fill=RED)

class RouteCard:
    def __init__(self, t_in, t_out, t_run, t_parl):
        self.name, self.frame_no, self.zone = "Langkah Muar route + 200 KM", 26, "R"
        self.t_run, self.t_parl = t_run, t_parl
        Card("Langkah Muar route", "R", 150, t_in, t_out, [
            K("Langkah Muar · 2024"),
            Custom(150, self.draw, lambda t: round(clamp((t - t_run) / (t_parl - t_run + 0.4)), 2)),
            Counter("{n} KM", 0, 200, t_run, t_parl + 0.4 - t_run, size=50, col=GOLD_TXT),
            Photo("parliament.jpg", 190, "Photo: Earth (en.wikipedia) · CC BY 2.5 · Wikimedia Commons", focus=0.45),
        ], w=500, frame_no=26)
    def draw(self, im, d, t, w, h):
        p = ease_inout((t - self.t_run) / (self.t_parl - self.t_run + 0.4))
        x0, x1, y = 30, w - 50, 70
        for x in range(x0, x1, 22): d.line([x, y, x + 10, y], fill=LINE, width=6)
        xe = x0 + (x1 - x0) * p
        if p > 0: d.line([x0, y, xe, y], fill=GOLD, width=8)
        d.ellipse([x0 - 12, y - 12, x0 + 12, y + 12], fill=INK)
        d.ellipse([x1 - 12, y - 12, x1 + 12, y + 12], fill=GOLD if p >= 1 else LINE)
        if 0 < p < 1:
            d.ellipse([xe - 9, y - 9, xe + 9, y + 9], fill=WHITE, outline=GOLD, width=4)
        f = font("mono", 20)
        d.text((x0 - 14, y + 26), "MUAR", font=f, fill=INK)
        tw = f.getlength("PARLIAMENT"); d.text((x1 + 14 - tw, y + 26), "PARLIAMENT", font=f, fill=INK if p >= 1 else MUTED)

class BalanceCard:
    def __init__(self, t_in, t_out, times):
        self.name, self.frame_no = "Balance: 4 pillars", 35
        self.times = times
        for l, tt in zip(PillarGrid.LABELS, times): sfx("tick", tt, 0.8, "balance " + l)
        Card("Balance pillars", "R", 220, t_in, t_out, [
            K("Mind · Body · Emotions · Values"),
            Custom(250, self.draw, lambda t: tuple(round(clamp((t - x) / 0.3), 2) for x in times))], w=500, frame_no=35)
    def draw(self, im, d, t, w, h):
        cw = (w - 24) / 4
        base = h - 30
        d.rounded_rectangle([0, base, w - 12, base + 12], radius=6, fill=INK)
        for i, (l, tt) in enumerate(zip(PillarGrid.LABELS, self.times)):
            p = ease_back((t - tt) / 0.3) if t > tt else 0
            ph = 150 * p
            x = i * cw + 8
            col = GOLD if p > 0 else LINE
            d.rounded_rectangle([x + 18, base - 10 - max(ph, 14), x + cw - 18, base - 6], radius=10, fill=col)
            draw_pillar_icon(d, x + cw / 2 - 16, base - 52 - max(ph, 14), i, 32, INK if p > 0 else LINE)

class TopBar:
    CH = [(0.0, "Intro"), (None, "My story"), (None, "My idol"), (None, "4 pillars"), (None, "Takeaway")]
    def __init__(self):
        self.name, self.frame_no, self.zone = "Top bar: chapter pill + progress", 0, "T"
        b = [0.0, T("hi", 21.5), T("my idol", 111.5), T("mentally", 131), T("since id", 256), NF / FPS]
        self.b = b
        self.t_in, self.t_out = 0.4, NF / FPS + 1
        for t in b[1:5]: sfx("whoosh", t, 0.45, "chapter change")
        ELEMS.append(self)
        self.cache = {}
    def bbox(self): return (LX - 10, 22, LX + 640, 112)
    def render(self, canvas, t):
        if t < self.t_in: return
        a = clamp((t - self.t_in) / 0.3)
        ci = max(i for i in range(5) if t >= self.b[i])
        prog = clamp((t - self.b[ci]) / (self.b[ci + 1] - self.b[ci]))
        key = (ci, round(prog, 3), round(a, 2))
        im = self.cache.get(key)
        if im is None:
            im = Image.new("RGBA", (660, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            sw = 112
            for i in range(5):
                x = 10 + i * (sw + 8)
                d.rounded_rectangle([x, 12, x + sw, 18], radius=3, fill=(255, 255, 255, 150))
                fill = 1 if i < ci else prog if i == ci else 0
                if fill > 0: d.rounded_rectangle([x, 12, x + max(6, sw * fill), 18], radius=3, fill=GOLD)
            label = "%02d / 05  %s" % (ci + 1, self.CH[ci][1].upper())
            f = font("mono", 21); tw = f.getlength(label)
            # chapter label pop on change
            pc = clamp((t - self.b[ci]) / 0.3) if ci > 0 else 1
            d.rounded_rectangle([10, 32, 10 + tw + 36, 72], radius=20, fill=(20, 20, 26, 215))
            d.rounded_rectangle([10, 32, 10 + 110, 72], radius=20, fill=GOLD)
            d.text((28, 40), label[:7], font=f, fill=INK)
            d.text((28 + f.getlength(label[:7]) + 22, 40), label[9:], font=f, fill=WHITE)
            im = with_alpha(im, a * (0.4 + 0.6 * ease_out(pc)))
            if len(self.cache) > 200: self.cache.clear()
            self.cache[key] = im
        paste(canvas, im, LX - 10, 18)

class PillarTracker:
    def __init__(self, t_in, t_out, t1, t2, t3, t4, t_bal, bal_times):
        self.name, self.frame_no, self.zone = "Top bar: pillar tracker", 18, "T"
        self.t_in, self.t_out, self.ts, self.bal = t_in, t_out, [t1, t2, t3, t4], bal_times
        self.t_bal = t_bal
        ELEMS.append(self)
        self.cache = {}
        sfx("pop", t_in, 0.6, "pillar tracker appears")
    def bbox(self): return (RX - 640, 22, RX + 10, 112)
    def active(self, t):
        if t >= self.bal[0] - 0.01:
            return [t >= x for x in self.bal]
        act = [False] * 4
        for i in range(4):
            nxt = self.ts[i + 1] if i < 3 else self.t_bal
            if self.ts[i] <= t < nxt: act[i] = True
        return act
    def render(self, canvas, t):
        if not (self.t_in <= t < self.t_out): return
        pi = clamp((t - self.t_in) / 0.3); po = clamp((t - (self.t_out - 0.22)) / 0.22)
        a = pi * (1 - po)
        act = tuple(self.active(t))
        key = (act, round(a, 2))
        im = self.cache.get(key)
        if im is None:
            im = Image.new("RGBA", (640, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            f = font("mono", 19)
            x = 640
            for i in reversed(range(4)):
                l = PillarGrid.LABELS[i]; tw = f.getlength(l); w = tw + 66
                x -= w
                on = act[i]
                d.rounded_rectangle([x, 14, x + w - 8, 54], radius=20, fill=GOLD if on else (20, 20, 26, 190))
                draw_pillar_icon(d, x + 14, 24, i, 20, INK if on else (150, 150, 158, 255))
                d.text((x + 44, 22), l, font=f, fill=INK if on else (220, 220, 226, 255))
            im = with_alpha(im, a)
            self.cache[key] = im
        paste(canvas, im, RX - 640, 22)

# ---------------------------------------------------------------- face boxes
def load_faces():
    raw = json.load(open(S + "/work/faces.json"))
    out, last = [], None
    for boxes in raw:
        lm = [b for b in boxes if b[0] == "lm"]
        if lm:
            b = lm[0]; x0, y0, x1, y1 = b[1:]
            for f in boxes:  # union with overlapping detector box
                if f[0] == "fd" and not (f[3] < x0 or f[1] > x1 or f[4] < y0 or f[2] > y1):
                    x0, y0, x1, y1 = min(x0, f[1]), min(y0, f[2]), max(x1, f[3]), max(y1, f[4])
            last = (x0, y0, x1, y1)
        out.append(last)
    # backfill leading Nones
    first = next(b for b in out if b)
    out = [b or first for b in out]
    zones = []
    for x0, y0, x1, y1 in out:
        w, h = x1 - x0, y1 - y0
        zones.append((int(x0 - 0.30 * w), int(y0 - 0.45 * h), int(x1 + 0.30 * w), int(y1 + 0.25 * h)))
    return zones

# ---------------------------------------------------------------- main
def render_range(a, b, outpath, faces):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H), "-r", str(FPS),
                            "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", outpath], stdin=subprocess.PIPE)
    viol = []
    for n in range(a, b):
        t = n / FPS
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for e in ELEMS: e.render(canvas, t)
        # guard 1: subtitle band
        if canvas.crop((0, SUB_TOP, W, H)).getextrema()[3][1] > 0:
            viol.append(("subtitle", n)); canvas.paste((0, 0, 0, 0), (0, SUB_TOP, W, H))
        # guard 2: face
        fx0, fy0, fx1, fy1 = faces[n]
        box = (max(0, fx0), max(0, fy0), min(W, fx1), min(H, fy1))
        if canvas.crop(box).getextrema()[3][1] > 0:
            viol.append(("face", n)); canvas.paste((0, 0, 0, 0), box)
        enc.stdin.write(canvas.tobytes())
    enc.stdin.close(); enc.wait()
    return viol

if __name__ == "__main__":
    build_timeline()
    mode = sys.argv[1]
    if mode == "plan":
        faces = load_faces()
        json.dump(sorted(SFX, key=lambda x: x["t"]), open(S + "/work/sfx.json", "w"), indent=0)
        rows = []
        for e in ELEMS:
            txt = " | ".join(re.sub(r"[\[\]{}~]", "", str(getattr(r, "text", "") or "")) for r in getattr(e, "rows", []) if getattr(r, "text", None))
            rows.append({"text": txt, "name": e.name, "frame": e.frame_no, "zone": getattr(e, "zone", ""), "t_in": round(e.t_in, 3), "t_out": round(min(e.t_out, NF / FPS), 3), "bbox": [int(v) for v in e.bbox()]})
        json.dump(rows, open(S + "/work/elements.json", "w"), indent=1)
        # static audits: bbox vs subtitle band and vs face zone (every frame each element is on screen)
        bad = 0
        for e in rows:
            x0, y0, x1, y1 = e["bbox"]
            if y1 > SUB_TOP + 25: print("BBOX into subtitle band:", e["name"], e["bbox"]); bad += 1
            for n in range(int(e["t_in"] * FPS), min(NF, int(e["t_out"] * FPS) + 1)):
                fx0, fy0, fx1, fy1 = faces[n]
                if not (x1 <= fx0 or x0 >= fx1 or y1 <= fy0 or y0 >= fy1):
                    print("BBOX overlaps face:", e["name"], e["bbox"], "frame", n, faces[n]); bad += 1; break
        # same-zone overlap audit
        for i, p in enumerate(rows):
            for q in rows[i + 1:]:
                if p["t_in"] < q["t_out"] and q["t_in"] < p["t_out"]:
                    a, b2 = p["bbox"], q["bbox"]
                    ix = min(a[2], b2[2]) - max(a[0], b2[0]); iy = min(a[3], b2[3]) - max(a[1], b2[1])
                    if ix > 80 and iy > 80: print("OVERLAP %-32s %-32s %.2f-%.2f" % (p["name"], q["name"], max(p["t_in"], q["t_in"]), min(p["t_out"], q["t_out"])))
        print("elements", len(rows), "sfx", len(SFX), "static issues", bad)
    elif mode == "still":
        out = sys.argv[2]
        for ts in sys.argv[3:]:
            t = float(ts); canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for e in ELEMS: e.render(canvas, t)
            canvas.save("%s/ov_%07.2f.png" % (out, t))
    elif mode == "render":
        a, b, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        faces = load_faces()
        v = render_range(a, b, outp, faces)
        json.dump(v, open(outp + ".viol.json", "w"))
        print("done", a, b, "violations", len(v))
