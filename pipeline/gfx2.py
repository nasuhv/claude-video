"""Revision 2 of the motion graphics (client notes round 1).

Reuses the engine in gfx.py (cards, rows, guards) and adds:
  Kinetic      - word-by-word text synced to speech, centred above the head
  PhotoFrame   - photo with keyframed Ken Burns push, entrance rotation settle, label pill
  ZodiacWheel  - rotating zodiac ring that lands on Capricorn
  IconFloat    - floating icon discs with labels
  BehindWord   - big words composited *behind* the speaker using a person mask
  Lanyard      - swinging ID badge
  video zoom   - keyframed zoom on the picture, only where no subtitles are on screen
"""
import json, math, os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

S = os.environ["SCR"]
sys.path.insert(0, S + "/scripts")
import gfx as G
from gfx import (T, sfx, clamp, ease_back, ease_out, ease_inout, paste, with_alpha, font, card_bg,
                 Card, K, Hd, P, Chk, Strike, Chip, Chips, Counter, Bar, Spacer, Custom,
                 INK, MUTED, WHITE, GOLD, GOLD_SOFT, GOLD_TXT, RED, LINE, LX, RX, W, H, FPS, NF)

G.FONTS["dejavu"] = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
G.FONTS["hand"] = S + "/assets/fonts/Caveat-Bold.ttf"
UP = S + "/assets/user/"
PH = S + "/assets/photos/"
ELEMS = G.ELEMS

# ------------------------------------------------------------------ icon library (flat, drawn at 4x)
def icon_img(name, size, col=INK):
    s = size * 4; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = max(4, int(s * 0.085)); c = col
    if name == "cap":
        d.polygon([(s*.5, s*.18), (s*.95, s*.38), (s*.5, s*.58), (s*.05, s*.38)], fill=c)
        d.rounded_rectangle([s*.24, s*.45, s*.76, s*.74], radius=int(s*.08), fill=c)
        d.line([(s*.86, s*.42), (s*.86, s*.72)], fill=c, width=w); d.ellipse([s*.81, s*.7, s*.91, s*.8], fill=c)
    elif name == "briefcase":
        d.rounded_rectangle([s*.36, s*.18, s*.64, s*.34], radius=int(s*.05), outline=c, width=w)
        d.rounded_rectangle([s*.1, s*.3, s*.9, s*.82], radius=int(s*.1), fill=c)
    elif name == "target":
        for r, f in ((.42, False), (.28, False), (.12, True)):
            box = [s*(.5-r), s*(.5-r), s*(.5+r), s*(.5+r)]
            d.ellipse(box, fill=c) if f else d.ellipse(box, outline=c, width=w)
    elif name == "bulb":
        d.ellipse([s*.22, s*.08, s*.78, s*.64], fill=c)
        d.rounded_rectangle([s*.36, s*.6, s*.64, s*.84], radius=int(s*.05), fill=c)
        d.line([(s*.38, s*.9), (s*.62, s*.9)], fill=c, width=w)
    elif name == "magnifier":
        d.ellipse([s*.1, s*.1, s*.66, s*.66], outline=c, width=int(w*1.3))
        d.line([(s*.6, s*.6), (s*.9, s*.9)], fill=c, width=int(w*1.8))
    elif name == "play":
        d.rounded_rectangle([s*.06, s*.18, s*.94, s*.82], radius=int(s*.14), fill=c)
        d.polygon([(s*.42, s*.34), (s*.68, s*.5), (s*.42, s*.66)], fill=WHITE)
    elif name == "megaphone":
        d.polygon([(s*.12, s*.38), (s*.68, s*.14), (s*.68, s*.86), (s*.12, s*.62)], fill=c)
        d.rounded_rectangle([s*.2, s*.56, s*.38, s*.88], radius=int(s*.05), fill=c)
        for k in (-1, 0, 1): d.line([(s*.78, s*(.5+k*.18)), (s*.92, s*(.5+k*.26))], fill=c, width=w)
    elif name == "code":
        d.line([(s*.34, s*.24), (s*.1, s*.5), (s*.34, s*.76)], fill=c, width=int(w*1.3), joint="curve")
        d.line([(s*.66, s*.24), (s*.9, s*.5), (s*.66, s*.76)], fill=c, width=int(w*1.3), joint="curve")
        d.line([(s*.58, s*.16), (s*.42, s*.84)], fill=c, width=int(w*1.1))
    elif name == "pen":
        d.polygon([(s*.5, s*.06), (s*.8, s*.46), (s*.5, s*.94), (s*.2, s*.46)], fill=c)
        d.line([(s*.5, s*.4), (s*.5, s*.8)], fill=WHITE, width=w); d.ellipse([s*.42, s*.34, s*.58, s*.5], fill=WHITE)
    elif name == "clipboard":
        d.rounded_rectangle([s*.14, s*.14, s*.86, s*.94], radius=int(s*.1), fill=c)
        d.rounded_rectangle([s*.34, s*.06, s*.66, s*.24], radius=int(s*.06), fill=c)
        for i, y in enumerate((.42, .6, .78)):
            d.line([(s*.28, s*y), (s*.36, s*(y+.06)), (s*.48, s*(y-.06))], fill=GOLD if c != GOLD else INK, width=w)
            d.line([(s*.56, s*y), (s*.76, s*y)], fill=WHITE, width=w)
    elif name == "owl":
        d.ellipse([s*.14, s*.22, s*.86, s*.96], fill=c)
        d.polygon([(s*.16, s*.32), (s*.24, s*.08), (s*.38, s*.26)], fill=c)
        d.polygon([(s*.84, s*.32), (s*.76, s*.08), (s*.62, s*.26)], fill=c)
        for cx in (.36, .64):
            d.ellipse([s*(cx-.15), s*.32, s*(cx+.15), s*.62], fill=WHITE)
            d.ellipse([s*(cx-.07), s*.4, s*(cx+.07), s*.54], fill=INK if c != INK else GOLD)
        d.polygon([(s*.44, s*.6), (s*.56, s*.6), (s*.5, s*.72)], fill=GOLD if c != GOLD else INK)
    elif name == "heart":
        d.ellipse([s*.06, s*.14, s*.54, s*.6], fill=c); d.ellipse([s*.46, s*.14, s*.94, s*.6], fill=c)
        d.polygon([(s*.08, s*.44), (s*.92, s*.44), (s*.5, s*.92)], fill=c)
    elif name == "trophy":
        d.rounded_rectangle([s*.26, s*.1, s*.74, s*.52], radius=int(s*.16), fill=c)
        d.arc([s*.06, s*.14, s*.36, s*.44], 90, 270, fill=c, width=w); d.arc([s*.64, s*.14, s*.94, s*.44], 270, 90, fill=c, width=w)
        d.rectangle([s*.44, s*.5, s*.56, s*.72], fill=c); d.rounded_rectangle([s*.28, s*.72, s*.72, s*.88], radius=int(s*.04), fill=c)
    elif name == "id":
        d.rounded_rectangle([s*.1, s*.2, s*.9, s*.8], radius=int(s*.1), fill=c)
        d.ellipse([s*.2, s*.34, s*.42, s*.56], fill=WHITE); d.line([(s*.52, s*.4), (s*.8, s*.4)], fill=WHITE, width=w)
        d.line([(s*.52, s*.58), (s*.72, s*.58)], fill=WHITE, width=w)
    return im.resize((size, size), Image.LANCZOS)

def icon_disc(name, size, bg=GOLD, fg=INK, shadow=True):
    pad = 24 if shadow else 0
    im = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([pad, pad + 8, pad + size, pad + size + 8], fill=(0, 0, 0, 90))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    big = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=bg)
    im.alpha_composite(big.resize((size, size), Image.LANCZOS), (pad, pad))
    ic = icon_img(name, int(size * 0.64), fg)
    im.alpha_composite(ic, (pad + (size - ic.width) // 2, pad + (size - ic.height) // 2))
    return im

# ------------------------------------------------------------------ rows using icons / logos
class IconLine(G.Row):
    def __init__(self, icon, text, at=None, size=32, **kw):
        super().__init__(at, sfx_kind=kw.pop("sfx_kind", "pop"), anim="rise", **kw); self.icon, self.text, self.fs = icon, text, size
    def build(self, width, dark):
        ic = icon_disc(self.icon, int(self.fs * 1.75), shadow=False)
        tx = G.draw_rich(self.text, "semi", self.fs, width - ic.width - 30, INK)
        h = max(ic.height, tx.height) + 4
        im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
        im.alpha_composite(ic, (0, (h - ic.height) // 2)); im.alpha_composite(tx, (ic.width + 14, (h - tx.height) // 2 + 2))
        self.img = im

class IconTitle(G.Row):
    """big icon disc + big title + subtitle (e.g. ISTJ / The Logistician)"""
    def __init__(self, icon, title, sub, at=None, **kw):
        super().__init__(at, sfx_kind=kw.pop("sfx_kind", "pop"), anim="pop", **kw); self.icon, self.title, self.sub = icon, title, sub
    def build(self, width, dark):
        ic = icon_disc(self.icon, 96, shadow=False)
        f1, f2 = font("black", 58), font("mono", 20)
        im = Image.new("RGBA", (width, 112), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        im.alpha_composite(ic, (0, 8))
        d.text((116, 4), self.title, font=f1, fill=INK)
        tw = f2.getlength(self.sub) + 24
        d.rounded_rectangle([116, 74, 116 + tw, 104], radius=15, fill=GOLD)
        d.text((128, 78), self.sub, font=f2, fill=INK)
        self.img = im

class LogoRow(G.Row):
    def __init__(self, path, h=90, at=None, **kw):
        super().__init__(at, **kw); self.path, self.h = path, h
    def build(self, width, dark):
        lg = ImageOps.exif_transpose(Image.open(self.path)).convert("RGBA")
        # knock out a flat white/grey background so the logo sits cleanly on the card
        a = np.array(lg).astype(np.int16)
        bgc = a[2, 2, :3]
        dist = np.abs(a[..., :3] - bgc).sum(2)
        if a[2, 2, 3] > 200 and bgc.min() > 200:
            a[..., 3] = np.where(dist < 30, 0, a[..., 3])
        lg = Image.fromarray(a.astype(np.uint8), "RGBA")
        bb = lg.getbbox(); lg = lg.crop(bb) if bb else lg
        r = min(self.h / lg.height, (width - 12) / lg.width)
        lg = lg.resize((int(lg.width * r), int(lg.height * r)), Image.LANCZOS)
        im = Image.new("RGBA", (width, self.h), (0, 0, 0, 0)); im.alpha_composite(lg, (0, (self.h - lg.height) // 2))
        self.img = im

# ------------------------------------------------------------------ kinetic text
def toks():
    return G.TOKS[0]
def word_times(text, after):
    words = G.parse_rich(text)
    tk = toks(); cur = next(i for i, x in enumerate(tk) if x[1] >= after - 0.05)
    out, last = [], None
    for w, st in words:
        m = re.match(r"^(.*)@([\d.]+)$", w)
        if m:
            w = m.group(1); t = float(m.group(2)); out.append((w, st, t)); last = t; continue
        n = G.norm(w)
        t = None
        if n:
            for j in range(cur, min(cur + 6, len(tk))):
                if tk[j][0] == n or (len(n) > 4 and tk[j][0][:4] == n[:4]):
                    t = tk[j][1]; cur = j + 1; break
        if t is None: t = (last + 0.14) if last is not None else after
        out.append((w, st, t)); last = t
    return out

def word_sprite(w, st, size, fname="black", tone="light"):
    f = font(fname, size); tw = int(f.getlength(w)) + 2
    asc, desc = f.getmetrics(); hh = asc + desc
    pad = 26
    im = Image.new("RGBA", (tw + 2 * pad, hh + 2 * pad), (0, 0, 0, 0))
    if st in ("gold", "red"):
        px = int(size * 0.2)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad - px, pad + size * .12 + 6, pad + tw + px, pad + hh - size * .02 + 6], radius=int(size * .24), fill=(0, 0, 0, 110))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([pad - px, pad + size * .12, pad + tw + px, pad + hh - size * .02], radius=int(size * .24), fill=GOLD if st == "gold" else RED)
        d.text((pad, pad), w, font=f, fill=INK if st == "gold" else WHITE)
        return im
    col = {"n": WHITE, "red": (255, 92, 96, 255), "strike": (235, 235, 240, 255)}[st] if tone == "light" else {"n": INK, "red": RED, "strike": MUTED}[st]
    glyph = Image.new("L", im.size, 0); ImageDraw.Draw(glyph).text((pad, pad), w, font=f, fill=255)
    shadow_col = (0, 0, 0) if tone == "light" else (255, 255, 255)
    sh = Image.new("RGBA", im.size, shadow_col + (0,)); sh.putalpha(glyph.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.75)))
    im.alpha_composite(sh, (0, 4))
    sh2 = Image.new("RGBA", im.size, shadow_col + (0,)); sh2.putalpha(glyph.filter(ImageFilter.GaussianBlur(2)).point(lambda v: int(v * 0.45)))
    im.alpha_composite(sh2, (0, 2))
    d = ImageDraw.Draw(im); d.text((pad, pad), w, font=f, fill=col)
    if st == "strike":
        y = pad + size * 0.62; d.line([pad - 4, y, pad + tw + 4, y], fill=RED, width=max(5, size // 9))
    return im

class Kinetic:
    """Word-by-word text. Each word pops in on the moment it is spoken."""
    def __init__(self, name, text, after, t_out, size=60, cx=960, y=132, maxw=900, frame_no=None, zone="C", fname="black", tone="light", sfx_gold=True, lh=1.12):
        self.name, self.frame_no, self.zone, self.t_out = name, frame_no, zone, t_out
        self.words = word_times(text, after)
        self.t_in = self.words[0][2]
        sp = font(fname, size).getlength(" ")
        sprites = [(word_sprite(w, st, size, fname, tone), st, t, w) for w, st, t in self.words]
        lines, cur, cw = [], [], 0
        for sp_im, st, t, w in sprites:
            ww = sp_im.width - 52
            if cur and cw + sp + ww > maxw: lines.append((cur, cw)); cur, cw = [], 0
            cur.append((sp_im, st, t, ww)); cw += (sp if len(cur) > 1 else 0) + ww
        if cur: lines.append((cur, cw))
        self.items = []; lhp = int(size * lh)
        for li, (line, lw) in enumerate(lines):
            x = cx - lw / 2
            for sp_im, st, t, ww in line:
                self.items.append((sp_im, int(x) - 26, y + li * lhp - 26, t, st)); x += ww + sp + (size * 0.14 if st in ("gold", "red") else 0)
        self.box = (min(i[1] for i in self.items), min(i[2] for i in self.items), max(i[1] + i[0].width for i in self.items), max(i[2] + i[0].height for i in self.items))
        sfx("whoosh", self.t_in, 0.5, "kinetic: " + name)
        if sfx_gold:
            for sp_im, x, yy, t, st in self.items:
                if st == "gold": sfx("pop", t, 0.7, "kinetic gold word")
        ELEMS.append(self)
    def bbox(self): return self.box
    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        po = clamp((t - (self.t_out - 0.25)) / 0.25)
        for sp_im, x, y, t0, st in self.items:
            p = (t - t0) / 0.28
            if p <= 0: continue
            a = clamp(p / 0.5) * (1 - po)
            if a <= 0.01: continue
            sc = 0.55 + 0.45 * ease_back(p, 2.2) if st in ("gold", "red") else 0.8 + 0.2 * ease_back(p)
            dy = 22 * (1 - ease_back(p)) - 18 * ease_out(po)
            im = sp_im
            if abs(sc - 1) > 0.01:
                im = sp_im.resize((max(1, int(sp_im.width * sc)), max(1, int(sp_im.height * sc))), Image.BILINEAR)
            paste(canvas, with_alpha(im, a), int(x + (sp_im.width - im.width) / 2), int(y + dy + (sp_im.height - im.height) / 2))

# ------------------------------------------------------------------ photo frame with keyframes
class PhotoFrame:
    def __init__(self, name, path, x, y, w, h, t_in, t_out, crop=(0, 0, 1, 1), rot=0.0, kicker=None, label=None,
                 anim="pop", kb=(1.0, 1.08), frame_no=None, zone="R", border=10, label_side="bl", pan=(0, 0)):
        self.name, self.frame_no, self.zone = name, frame_no, zone
        if zone == "R" and x + w > 1300: y = max(y, 250)   # keep clear of the centred kinetic line
        self.x, self.y, self.w, self.h, self.t_in, self.t_out, self.rot, self.anim, self.kb = x, y, w, h, t_in, t_out, rot, anim, kb
        self.border, self.pan = border, pan
        src = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        cx0, cy0, cx1, cy1 = [int(v) for v in (crop[0] * src.width, crop[1] * src.height, crop[2] * src.width, crop[3] * src.height)]
        src = src.crop((cx0, cy0, cx1, cy1))
        # cover-fit to w:h
        ar = w / h
        if src.width / src.height > ar:
            nw = int(src.height * ar); o = (src.width - nw) // 2; src = src.crop((o, 0, o + nw, src.height))
        else:
            nh = int(src.width / ar); o = (src.height - nh) // 3; src = src.crop((0, o, src.width, o + nh))
        self.base = src.resize((int(w * kb[1] * 1.02), int(h * kb[1] * 1.02)), Image.LANCZOS)
        m = Image.new("L", (w * 4, h * 4), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=72, fill=255)
        self.mask = m.resize((w, h), Image.LANCZOS)
        b = border; pad = 40
        fr = Image.new("RGBA", (w + 2 * b + 2 * pad, h + 2 * b + 2 * pad), (0, 0, 0, 0))
        sh = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 14, pad + w + 2 * b, pad + h + 2 * b + 14], radius=26, fill=(0, 0, 0, 105))
        fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
        ImageDraw.Draw(fr).rounded_rectangle([pad, pad, pad + w + 2 * b, pad + h + 2 * b], radius=26, fill=(255, 255, 255, 250))
        self.frame, self.pad = fr, pad
        self.label = None
        if label:
            f1, f2 = font("disp", 30), font("mono", 18)
            tw = max(f1.getlength(label), f2.getlength(kicker or "")) + 44
            lb = Image.new("RGBA", (int(tw) + 40, (88 if kicker else 62) + 40), (0, 0, 0, 0))
            s2 = Image.new("RGBA", lb.size, (0, 0, 0, 0)); ImageDraw.Draw(s2).rounded_rectangle([20, 26, 20 + tw, lb.height - 14], radius=18, fill=(0, 0, 0, 120))
            lb.alpha_composite(s2.filter(ImageFilter.GaussianBlur(10)))
            d = ImageDraw.Draw(lb); d.rounded_rectangle([20, 20, 20 + tw, lb.height - 20], radius=18, fill=(18, 18, 24, 236))
            yy = 30
            if kicker:
                d.ellipse([42, yy + 6, 52, yy + 16], fill=GOLD); d.text((60, yy), kicker.upper(), font=f2, fill=GOLD); yy += 28
            d.text((42, yy), label, font=f1, fill=WHITE)
            self.label = lb
        self.label_side = label_side
        sfx("whoosh" if anim.startswith("slide") else "pop", t_in, 0.8, "photo: " + name)
        ELEMS.append(self)

    def bbox(self):
        m = 60 + (abs(self.rot) * 6)
        lbh = self.label.height - 30 if self.label is not None else 0
        return (int(self.x - m), int(self.y - m), int(self.x + self.w + m), int(self.y + self.h + m + lbh * 0.6))

    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        pi = (t - self.t_in) / 0.42; po = clamp((t - (self.t_out - 0.25)) / 0.25)
        e = ease_back(pi, 1.6)
        a = clamp(pi / 0.4) * (1 - po)
        if a <= 0.01: return
        # ken burns keyframe: slow push over the whole life of the photo
        life = clamp((t - self.t_in) / max(0.5, self.t_out - self.t_in))
        z = self.kb[0] + (self.kb[1] - self.kb[0]) * ease_inout(life)
        bw, bh = self.base.size
        vw, vh = self.w * self.kb[1] * 1.02 / z, self.h * self.kb[1] * 1.02 / z
        cx = bw / 2 + self.pan[0] * (bw - vw) / 2 * ease_inout(life); cy = bh / 2 + self.pan[1] * (bh - vh) / 2 * ease_inout(life)
        vw, vh = min(vw, bw), min(vh, bh)
        x0 = min(max(0, cx - vw / 2), bw - vw); y0 = min(max(0, cy - vh / 2), bh - vh)
        ph = self.base.resize((self.w, self.h), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh)).convert("RGBA")
        ph.putalpha(self.mask)
        im = self.frame.copy(); im.alpha_composite(ph, (self.pad + self.border, self.pad + self.border))
        if self.label is not None:
            pl = clamp((t - self.t_in - 0.25) / 0.3)
            if pl > 0:
                big = Image.new("RGBA", (im.width + 60, im.height + 80), (0, 0, 0, 0)); big.alpha_composite(im, (30, 0))
                lx = 30 + self.pad - 10 if self.label_side == "bl" else 30 + im.width - self.pad - self.label.width + 10
                ly = self.pad + self.h + 2 * self.border - 50 + int(14 * (1 - ease_back(pl)))
                paste(big, with_alpha(self.label, clamp(pl * 2)), lx, ly)
                im = big; offx = -30
            else: offx = 0
        else: offx = 0
        rot = self.rot + (7 if self.anim == "pop" else 0) * (1 - e)
        sc = (0.78 + 0.22 * e) if self.anim == "pop" else 1.0
        sc *= (1 - 0.06 * ease_out(po))
        dx = {"slideL": -170 * (1 - e), "slideR": 170 * (1 - e)}.get(self.anim, 0)
        dy = -40 * (1 - e) if self.anim == "drop" else 0
        cxs, cys = im.width / 2, im.height / 2
        if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        if abs(rot) > 0.05: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        X = self.x - self.pad - self.border + offx + cxs - im.width / 2 + dx
        Y = self.y - self.pad - self.border + cys - im.height / 2 + dy
        paste(canvas, with_alpha(im, a), int(X), int(Y))

# ------------------------------------------------------------------ handwritten annotation with drawn arrow
class Annotation:
    def __init__(self, name, text, tx, ty, pts, t_in, t_out, size=54, frame_no=None, color=WHITE):
        self.name, self.frame_no, self.zone = name, frame_no, "L"
        self.text, self.tx, self.ty, self.pts, self.t_in, self.t_out, self.size, self.col = text, tx, ty, pts, t_in, t_out, size, color
        f = font("hand", size)
        tw = int(f.getlength(text)) + 40
        im = Image.new("RGBA", (tw + 40, size + 60), (0, 0, 0, 0))
        g = Image.new("L", im.size, 0); ImageDraw.Draw(g).text((20, 10), text, font=f, fill=255)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(g.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .8)))
        im.alpha_composite(sh, (0, 3)); ImageDraw.Draw(im).text((20, 10), text, font=f, fill=color)
        self.img = im
        sfx("whoosh", t_in, 0.4, "annotation: " + text)
        ELEMS.append(self)
    def bbox(self):
        xs = [p[0] for p in self.pts] + [self.tx, self.tx + self.img.width]; ys = [p[1] for p in self.pts] + [self.ty, self.ty + self.img.height]
        return (min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20)
    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        po = clamp((t - (self.t_out - 0.25)) / 0.25)
        p = clamp((t - self.t_in) / 0.45)
        a = (1 - po)
        # text writes on (left-to-right wipe)
        wtxt = int(self.img.width * ease_out(p))
        if wtxt > 2: paste(canvas, with_alpha(self.img.crop((0, 0, wtxt, self.img.height)), a), self.tx, self.ty)
        # arrow draws after the text
        q = clamp((t - self.t_in - 0.3) / 0.45)
        if q <= 0: return
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        # quadratic bezier through pts[0] -> pts[1] (control) -> pts[2]
        (x0, y0), (x1, y1), (x2, y2) = self.pts
        N = 40; n = max(2, int(N * ease_out(q)))
        curve = [((1-u)**2*x0 + 2*(1-u)*u*x1 + u*u*x2, (1-u)**2*y0 + 2*(1-u)*u*y1 + u*u*y2) for u in [i / N for i in range(n + 1)]]
        d.line(curve, fill=(0, 0, 0, 90), width=9, joint="curve")
        d.line(curve, fill=self.col, width=6, joint="curve")
        if q >= 1:
            ang = math.atan2(y2 - y1, x2 - x1)
            for s_ in (-1, 1):
                d.line([(x2, y2), (x2 - 26 * math.cos(ang + s_ * 0.5), y2 - 26 * math.sin(ang + s_ * 0.5))], fill=self.col, width=6)
        if a < 1: layer = with_alpha(layer, a)
        bb = layer.getbbox()
        if bb: paste(canvas, layer.crop(bb), bb[0], bb[1])

# ------------------------------------------------------------------ zodiac wheel
class ZodiacWheel:
    SIGNS = [chr(0x2648 + i) for i in range(12)]
    def __init__(self, cx, cy, r, t_in, t_out, frame_no=5):
        self.name, self.frame_no, self.zone = "Zodiac wheel (lands on Capricorn)", frame_no, "R"
        self.cx, self.cy, self.r, self.t_in, self.t_out = cx, cy, r, t_in, t_out
        sfx("pop", t_in, 0.8, "zodiac wheel in"); sfx("whoosh", t_in + 0.1, 0.6, "zodiac spin"); sfx("tick", t_in + 1.45, 0.9, "lands on Capricorn")
        self.cache = {}
        ELEMS.append(self)
    def bbox(self): return (self.cx - self.r - 60, self.cy - self.r - 60, self.cx + self.r + 60, self.cy + self.r + 110)
    def draw(self, ang, hl, ring):
        R = self.r; S2 = 2 * R + 140
        im = Image.new("RGBA", (S2, S2 + 60), (0, 0, 0, 0)); c = S2 / 2
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([c - R, c - R + 14, c + R, c + R + 14], fill=(0, 0, 0, 100))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
        d = ImageDraw.Draw(im)
        d.ellipse([c - R, c - R, c + R, c + R], fill=(255, 255, 255, 246))
        # ring progress
        d.arc([c - R + 14, c - R + 14, c + R - 14, c + R - 14], -90, -90 + 360 * ring, fill=GOLD, width=5)
        d.ellipse([c - R * .52, c - R * .52, c + R * .52, c + R * .52], fill=(20, 20, 26, 240))
        f = font("dejavu", 30)
        for i, g in enumerate(self.SIGNS):
            a = math.radians(ang + i * 30 - 90 - 270)  # capricorn (i=9) at top when ang=0
            x, y = c + math.cos(a) * R * .76, c + math.sin(a) * R * .76
            on = (i == 9 and hl > 0)
            if on:
                rr = 28 * (0.7 + 0.3 * ease_back(hl)); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=GOLD)
            d.text((x, y), g, font=f, fill=INK if on else (150, 150, 160, 255), anchor="mm")
        d.polygon([(c - 12, c - R - 4), (c + 12, c - R - 4), (c, c - R + 16)], fill=GOLD)
        if hl <= 0:
            d.text((c, c), "MY SIGN", font=font("mono", 20), fill=(200, 200, 208, 255), anchor="mm")
        if hl > 0:
            fg = font("dejavu", int(64 * (0.6 + 0.4 * ease_back(hl))))
            d.text((c, c - 14), self.SIGNS[9], font=fg, fill=GOLD, anchor="mm")
            d.text((c, c + 44), "CAPRICORN", font=font("mono", 19), fill=WHITE, anchor="mm")
        if hl > 0.3:
            fl = font("mono", 20); txt = "22 DEC – 19 JAN"; tw = fl.getlength(txt) + 36
            d.rounded_rectangle([c - tw / 2, c + R + 14, c + tw / 2, c + R + 52], radius=19, fill=GOLD)
            d.text((c, c + R + 33), txt, font=fl, fill=INK, anchor="mm")
        return im
    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        pi = (t - self.t_in) / 0.35; po = clamp((t - (self.t_out - 0.25)) / 0.25)
        spin = ease_out((t - self.t_in) / 1.45)
        ang = 300 * (1 - spin)
        hl = clamp((t - self.t_in - 1.45) / 0.3)
        ring = ease_out((t - self.t_in) / 1.45)
        key = (round(ang, 1), round(hl, 2), round(ring, 2))
        im = self.cache.get(key)
        if im is None:
            im = self.draw(ang, hl, ring)
            if len(self.cache) > 120: self.cache.clear()
            self.cache[key] = im
        sc = (0.6 + 0.4 * ease_back(pi)) * (1 - 0.06 * ease_out(po))
        a = clamp(pi / 0.5) * (1 - po)
        if abs(sc - 1) > 0.004: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
        S2 = 2 * self.r + 140
        paste(canvas, with_alpha(im, a), int(self.cx - im.width / 2), int(self.cy - S2 * sc / 2))

# ------------------------------------------------------------------ floating icon disc + label
class IconFloat:
    def __init__(self, name, icon, label, x, y, t_in, t_out, size=104, phase=0.0, frame_no=None, zone="L"):
        self.name, self.frame_no, self.zone = name, frame_no, zone
        self.x, self.y, self.t_in, self.t_out, self.phase = x, y, t_in, t_out, phase
        disc = icon_disc(icon, size, bg=WHITE, fg=INK)
        ring = ImageDraw.Draw(disc); ring.ellipse([24 + 3, 24 + 3, 24 + size - 3, 24 + size - 3], outline=GOLD, width=5)
        f = font("mono", 21); tw = int(f.getlength(label)) + 30
        w = max(disc.width, tw + 20); im = Image.new("RGBA", (w, disc.height + 50), (0, 0, 0, 0))
        im.alpha_composite(disc, ((w - disc.width) // 2, 0))
        d = ImageDraw.Draw(im); lx = (w - tw) // 2
        d.rounded_rectangle([lx, disc.height - 14, lx + tw, disc.height + 24], radius=19, fill=(20, 20, 26, 236))
        d.text((w / 2, disc.height + 5), label, font=f, fill=WHITE, anchor="mm")
        self.img = im
        sfx("pop", t_in, 0.85, "icon: " + label)
        ELEMS.append(self)
    def bbox(self): return (self.x - self.img.width // 2, self.y - 20, self.x + self.img.width // 2, self.y + self.img.height + 20)
    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        pi = (t - self.t_in) / 0.35; po = clamp((t - (self.t_out - 0.25)) / 0.25)
        sc = (0.4 + 0.6 * ease_back(pi, 2.4)) * (1 - 0.1 * ease_out(po))
        a = clamp(pi / 0.4) * (1 - po)
        bob = 9 * math.sin(2 * math.pi * (t - self.t_in) / 2.6 + self.phase)
        im = self.img
        if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        paste(canvas, with_alpha(im, a), int(self.x - im.width / 2), int(self.y + bob + (self.img.height - im.height) / 2))

# ------------------------------------------------------------------ words behind the speaker
MX0, MY0, MCW, MCH = 480, 140, 960, 940
_mask_cache = {}
def person_mask(n):
    if n in _mask_cache: return _mask_cache[n]
    p = S + "/work/masks/%05d.npy" % n
    if not os.path.exists(p): return None
    m = np.load(p).astype(np.float32) / 255
    # crisp edge, slight grow so letters tuck neatly behind the silhouette
    m = np.clip((m - 0.25) / 0.35, 0, 1)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    full = Image.new("L", (W, H), 0); full.paste(mi, (MX0, MY0))
    if len(_mask_cache) > 8: _mask_cache.clear()
    _mask_cache[n] = full
    return full

class BehindWord:
    def __init__(self, name, text, cx, y, size, t_in, t_out, color=WHITE, frame_no=None, outline=False):
        self.name, self.frame_no, self.zone = name, frame_no, "Behind"
        self.cx, self.y, self.t_in, self.t_out = cx, y, t_in, t_out
        f = font("black", size); tw = int(f.getlength(text)); asc, desc = f.getmetrics()
        pad = 30; im = Image.new("RGBA", (tw + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
        g = Image.new("L", im.size, 0); ImageDraw.Draw(g).text((pad, pad), text, font=f, fill=255)
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(g.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .55)))
        im.alpha_composite(sh, (0, 6)); ImageDraw.Draw(im).text((pad, pad), text, font=f, fill=color)
        self.img = im
        sfx("thump", t_in, 0.75, "behind-word: " + text)
        ELEMS.append(self)
    def bbox(self):
        # glyph extent only (shadow excluded) for audit
        return (self.cx - self.img.width // 2 + 30, self.y + 30, self.cx + self.img.width // 2 - 30, self.y + self.img.height - 30)
    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        n = int(round(t * FPS))
        pi = (t - self.t_in) / 0.4; po = clamp((t - (self.t_out - 0.25)) / 0.25)
        a = clamp(pi / 0.4) * (1 - po)
        dy = -14 * ease_out(po)
        sc = 0.8 + 0.2 * ease_back(pi, 1.8)
        im = self.img
        if abs(sc - 1) > 0.004: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
        x = int(self.cx - im.width / 2); y = int(self.y + dy + (self.img.height - im.height) / 2)
        layer = with_alpha(im, a)
        m = person_mask(n)
        if m is not None:
            mm = m.crop((x, y, x + im.width, y + im.height))
            arr = np.array(layer); inv = 1 - np.asarray(mm, np.float32) / 255
            arr[..., 3] = (arr[..., 3] * inv).astype(np.uint8); layer = Image.fromarray(arr, "RGBA")
        paste(canvas, layer, x, y)

# ------------------------------------------------------------------ swinging lanyard ID badge
class Lanyard:
    def __init__(self, px, card_top, t_in, t_out, logo, frame_no=10):
        self.name, self.frame_no, self.zone = "Lanyard ID badge: Head of Media Exco", frame_no, "R"
        self.px, self.top, self.t_in, self.t_out = px, card_top, t_in, t_out
        cw, ch = 330, 400; self.cw, self.ch = cw, ch
        card = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
        sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([40, 54, 40 + cw, 54 + ch], radius=26, fill=(0, 0, 0, 110))
        card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle([40, 40, 40 + cw, 40 + ch], radius=26, fill=(255, 255, 255, 252))
        d.rounded_rectangle([40 + cw / 2 - 34, 56, 40 + cw / 2 + 34, 70], radius=7, fill=(220, 220, 226, 255))
        lr = LogoRow(logo, 70); lr.build(cw - 60, False); card.alpha_composite(lr.img, (70, 92))
        d.text((70, 186), "HEAD OF", font=font("mono", 22), fill=MUTED)
        d.text((70, 212), "Media Exco", font=font("black", 50), fill=INK)
        d.text((70, 280), "Kolej Keris Mas", font=font("semi", 26), fill=INK)
        d.text((70, 314), "ANNUAL EVENT · UKM", font=font("mono", 18), fill=MUTED)
        d.rounded_rectangle([40, 40 + ch - 54, 40 + cw, 40 + ch], radius=26, fill=GOLD)
        d.rectangle([40, 40 + ch - 54, 40 + cw, 40 + ch - 30], fill=GOLD)
        d.text((40 + cw / 2, 40 + ch - 27), "CREW · ACCESS ALL AREAS", font=font("mono", 17), fill=INK, anchor="mm")
        self.card = card
        sfx("whoosh", t_in, 0.8, "lanyard drops in"); sfx("thump", t_in + 0.42, 0.6, "lanyard lands")
        ELEMS.append(self)
    def bbox(self):
        return (self.px - 300, 0, self.px + 300, self.top + self.ch + 60)
    def render(self, canvas, t):
        if t < self.t_in or t >= self.t_out: return
        u = t - self.t_in; po = clamp((t - (self.t_out - 0.25)) / 0.25)
        drop = -520 * (1 - ease_back(u / 0.5, 1.3))
        ang = 13 * math.exp(-1.6 * u) * math.sin(2 * math.pi * u / 1.25)
        a = clamp(u / 0.2) * (1 - po)
        L = self.top + drop  # card top y
        Hh = int(self.top + self.ch + 120)
        layer = Image.new("RGBA", (700, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        ox = 350  # pivot x in layer coords; pivot y = 0
        d.polygon([(ox - 9, 0), (ox + 9, 0), (ox + 64, L + 22), (ox + 46, L + 22)], fill=(20, 20, 26, 255))
        d.polygon([(ox - 9, 0), (ox + 9, 0), (ox - 46, L + 22), (ox - 64, L + 22)], fill=(20, 20, 26, 255))
        d.rounded_rectangle([ox - 22, L + 8, ox + 22, L + 34], radius=6, fill=(170, 170, 178, 255))
        paste(layer, self.card, int(ox - self.card.width / 2), int(L - 20))
        layer = layer.rotate(ang, resample=Image.BICUBIC, center=(ox, 0))
        paste(canvas, with_alpha(layer, a), self.px - ox, 0)

# ------------------------------------------------------------------ chapters (client's exact list)
class TopBar2:
    def __init__(self, bounds, labels):
        self.name, self.frame_no, self.zone = "Top bar: chapter pill + progress", 0, "T"
        self.b, self.labels = bounds, labels
        self.t_in, self.t_out = 0.9, NF / FPS + 1
        for t in bounds[1:-1]: sfx("whoosh", t, 0.45, "chapter change")
        self.cache = {}
        ELEMS.append(self)
    def bbox(self): return (LX - 10, 18, LX + 660, 110)
    def render(self, canvas, t):
        if t < self.t_in: return
        a = clamp((t - self.t_in) / 0.4)
        nc = len(self.labels)
        ci = max(i for i in range(nc) if t >= self.b[i])
        prog = clamp((t - self.b[ci]) / (self.b[ci + 1] - self.b[ci]))
        pc = clamp((t - self.b[ci]) / 0.35) if ci > 0 else 1
        key = (ci, round(prog, 3), round(a, 2), round(pc, 2))
        im = self.cache.get(key)
        if im is None:
            im = Image.new("RGBA", (680, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            sw = 150
            for i in range(nc):
                x = 10 + i * (sw + 8)
                d.rounded_rectangle([x, 12, x + sw, 18], radius=3, fill=(255, 255, 255, 150))
                fill = 1 if i < ci else prog if i == ci else 0
                if fill > 0: d.rounded_rectangle([x, 12, x + max(6, sw * fill), 18], radius=3, fill=GOLD)
            f = font("mono", 21)
            num = "%02d / %02d" % (ci + 1, nc); lab = self.labels[ci].upper()
            nw = f.getlength(num); lw = f.getlength(lab)
            d.rounded_rectangle([10, 32, 10 + nw + lw + 62, 72], radius=20, fill=(20, 20, 26, 215))
            d.rounded_rectangle([10, 32, 10 + nw + 32, 72], radius=20, fill=GOLD)
            d.text((26, 40), num, font=f, fill=INK)
            # label slides in on chapter change
            lab_im = Image.new("RGBA", (int(lw) + 4, 30), (0, 0, 0, 0)); ImageDraw.Draw(lab_im).text((0, 0), lab, font=f, fill=WHITE)
            paste(im, with_alpha(lab_im, ease_out(pc)), int(10 + nw + 46 + 30 * (1 - ease_out(pc))), 40)
            im = with_alpha(im, a)
            if len(self.cache) > 300: self.cache.clear()
            self.cache[key] = im
        paste(canvas, im, LX - 10, 18)

# ------------------------------------------------------------------ picture zoom keyframes (subtitle-free moments only)
ZOOMS = [
    # (t0, t1, z0, z1, cx, cy)   subtitles are absent 0.0-0.9 s and 274.3 s-end
    (0.0, 0.85, 1.18, 1.0, 955, 520),
    (274.35, NF / FPS, 1.0, 1.07, 955, 520),
]
def zoom_at(t):
    for t0, t1, z0, z1, cx, cy in ZOOMS:
        if t0 <= t <= t1 + 1e-6:
            p = (t - t0) / (t1 - t0)
            e = ease_out(p) if z0 > z1 else ease_inout(p)
            return z0 + (z1 - z0) * e, cx, cy
    return None

# ------------------------------------------------------------------ timeline
def build():
    # opening keyframe zoom sound
    sfx("whoosh", 0.02, 1.0, "opening keyframe zoom-out"); sfx("pop", 0.84, 0.7, "zoom lands")
    sfx("whoosh", 274.4, 0.6, "closing keyframe push-in")

    t_lets = T("lets get started", 10)
    Kinetic("Let's get started", "Let's get [started]", t_lets - 0.05, T("let me ask", 11.5) - 0.1, size=72, frame_no=2)

    t_have = T("have you ever", 13.5); t_true = T("true leadership", 17); t_fall = T("fall apart", 20); t_hi = T("hi", 21.5)
    Kinetic("Have you ever planned…", "Have you ever planned your life [so] [carefully]?", t_have - 0.05, t_true - 0.25, size=58, frame_no=3)
    Kinetic("Big idea", "[True] [leadership] begins the moment your [plan] [falls] [apart]", t_true - 0.05, t_hi - 0.1, size=54, frame_no=4)
    # life-plan card with icons instead of ticks (cracks & falls on 'fall apart')
    class PlanIcons(G.PlanCard):
        def __init__(self, t_in, t_crack, t_out, ticks):
            self.name, self.frame_no, self.zone = "My life plan (icons; cracks & falls)", 3, "R"
            self.card = Card("My life plan", "R", 200, t_in, t_out + 10, [
                K("My life plan"),
                IconLine("cap", "Study", at=ticks[0]), IconLine("briefcase", "Career", at=ticks[1]), IconLine("target", "Goals", at=ticks[2])], w=400, frame_no=3)
            ELEMS.remove(self.card)
            self.t_in, self.t_out, self.tc = t_in, t_out, t_crack
            ELEMS.append(self)
    PlanIcons(T("ever", 14), t_fall, t_hi - 0.05, (T("planned", 14.5), T("life", 15), T("carefully", 15.5)))
    sfx("thump", t_fall, 1.0, "PLAN cracks"); sfx("whoosh", t_fall + 0.35, 0.6, "PLAN falls")

    # self-intro: no name card (client). zodiac wheel
    t_cap = T("capricorn", 25); t_blend = T("blending", 27); t_grow = T("growing up", 33)
    ZodiacWheel(1620, 420, 190, t_cap - 0.1, t_blend + 1.9)
    Kinetic("Creativity + detail", "I love blending [creativity] +@%.2f [detail]" % (T("with", 27.8)), t_blend - 0.3, t_grow - 0.15, size=62, frame_no=5)
    IconFloat("icon creativity", "bulb", "CREATIVITY", 640, 300, T("creativity", 27.4), t_grow - 0.15, size=88, phase=0.3, frame_no=15)
    IconFloat("icon detail", "magnifier", "DETAIL", 1280, 300, T("detail", 28.3), t_grow - 0.15, size=88, phase=1.6, frame_no=15)
    IconFloat("icon multimedia", "play", "MULTIMEDIA", 250, 300, T("multimedia", 29), t_grow - 0.15, phase=0.0, frame_no=15)
    IconFloat("icon digital marketing", "megaphone", "DIGITAL MARKETING", 330, 560, T("digital", 30), t_grow - 0.15, phase=2.1, frame_no=15)
    IconFloat("icon IT", "code", "IT", 1670, 300, T("it", 31.5), t_grow - 0.15, phase=1.0, frame_no=15)
    IconFloat("icon journalism", "pen", "JOURNALISM", 1590, 560, T("journalism", 32), t_grow - 0.15, phase=3.0, frame_no=15)

    # ---------------- chapter 2: personality insights
    t_when = T("when i took", 39)
    t_mom = T("my mom", 34)
    PhotoFrame("Me with my mum (teacher)", UP + "mum.bin", 96, 170, 340, 380, t_mom - 0.1, t_when - 0.12, crop=(0.0, 0.2, 1.0, 0.72), rot=-3, anim="pop",
               kicker="A dedicated teacher", label="My mum", frame_no=6, zone="L", kb=(1.0, 1.1))
    Annotation("'This is my mum' arrow", "This is my mum!", 440, 190, [(540, 262), (520, 330), (400, 315)], t_mom + 0.35, t_when - 0.12, size=48, frame_no=6)
    BehindWord("EDUCATION (behind me)", "EDUCATION", 470, 615, 112, T("education", 36.5), t_when - 0.12, color=GOLD, frame_no=6)
    BehindWord("DISCIPLINE (behind me)", "DISCIPLINE", 1490, 615, 112, T("discipline", 37.3), t_when - 0.12, color=WHITE, frame_no=6)

    t_thr = T("i thrive", 46)
    Card("Personality test 1", "L", 170, T("16 personalities", 40) - 0.1, t_thr - 0.12, [
        K("Personality test 1"), Hd("16Personalities", 40), P("Myers-Briggs Type Indicator (MBTI)", size=24),
        IconTitle("clipboard", "ISTJ", "THE LOGISTICIAN", at=T("istj", 42))], w=520, frame_no=7)
    Card("Personality test 2", "R", 170, T("doctors", 41) - 0.1, t_thr - 0.12, [
        K("Personality test 2"), Hd("DOPE Personality Test", 36),
        IconTitle("owl", "OWL", "THE DOPE OWL", at=T("owl", 43))], w=500, frame_no=7)
    Kinetic("Mirror", "…like looking in the [mirror]", T("like looking", 45) - 0.05, t_thr - 0.1, size=50, frame_no=7)

    t_after = T("after finishing", 51)
    Kinetic("Logic → plan → goals", "I thrive on [logic] → a solid [plan] → my [goals]", t_thr - 0.05, t_after - 0.12, size=56, frame_no=8)

    t_later = T("later", 63)
    Card("Diploma · UniKL", "L", 190, T("diploma", 52) - 0.1, t_later - 0.12, [
        LogoRow(UP + "unikl_logo.bin", 96), K("Diploma"), Hd("Multimedia", 44), P("UniKL MIIT", size=24)], w=470, frame_no=9)
    PhotoFrame("Merdeka 118 (PNB)", PH + "merdeka118.jpg", 1460, 150, 300, 440, T("spent", 55) - 0.1, t_later - 0.12, crop=(0.05, 0.0, 0.95, 0.75), rot=2.5,
               kicker="Permodalan Nasional Berhad", label="Marketing · ASNB", anim="slideR", frame_no=9, kb=(1.0, 1.12), pan=(0, -0.6), label_side="br")
    Card("Almost 1 year", "R", 690, T("almost", 56) - 0.05, t_later - 0.12, [
        Chips([("ALMOST 1 YEAR", T("almost", 56)), ("DETAIL-ORIENTED", T("very detailed", 62) - 0.1)], size=22, style="gold")], w=470, anim="pop", padding=16, frame_no=9)

    t_atf = T("at first", 71)
    Card("UKM · Liberal Studies", "L", 190, T("first year", 64) - 0.1, t_atf - 0.12, [
        LogoRow(UP + "ukm_logo.bin", 92), K("Year 1"), Hd("Liberal Studies", 44)], w=470, frame_no=10)
    Lanyard(1560, 220, T("head of the media", 67) - 0.1, t_atf - 0.12, UP + "ukm_logo.bin")

    t_ifelt = T("felt anxious", 74.5) if False else T("i felt", 74.3)
    t_real = T("realizing", 79.5)
    Kinetic("Perfectionism = problem", "My corporate [perfectionism] became a {problem}", T("my corporate", 72) - 0.05, t_ifelt - 0.1, size=56, frame_no=11)
    Kinetic("Anxious, control every design", "Anxious delegating tasks, wanting to {control} {every} {single} {design}", t_ifelt - 0.05, t_real - 0.12, size=50, frame_no=11)

    t_icr = T("i created", 86.5)
    Kinetic("Micromanaging = burning out", "Micromanaging was {burning} {me} {out}", t_real - 0.05, T("i shifted", 83.8) - 0.1, size=56, frame_no=12)
    Card("Controlling to empowering", "R", 230, T("shifted", 84) - 0.2, t_icr - 0.12, [
        K("I shifted from"),
        Strike("Controlling", strike_at=T("controlling", 85), size=44),
        Hd("→ [Empowering]", 50, at=T("empowering", 85.5))], w=480, frame_no=12)

    t_res = T("as a result", 92)
    Card("The fix", "L", 190, t_icr - 0.05, t_res - 0.12, [
        K("The fix"),
        IconLine("clipboard", "Clear creative brief", at=T("clear creative", 87.5)),
        IconLine("play", "Easy templates", at=T("templates", 89)),
        IconLine("id", "Full team ownership", at=T("full ownership", 90.5))], w=520, frame_no=13)

    t_taught = T("that taught", 98.5)
    G.PhoneGrid(T("instagram", 93.5), t_taught - 0.12, T("on time", 94.5))
    Card("Launched on time stamp", "R", 690, T("on time", 94.5) - 0.1, t_taught - 0.12, [
        Chip("✓ LAUNCHED ON TIME", style="gold", size=26, stamp=True, at=T("on time", 94.5))], w=380, anim="pop", sfx_in="pop", padding=16, frame_no=14)
    Kinetic("Team did amazing work", "My team did [amazing] [work] on their own", T("my team did", 95.5) - 0.05, t_taught - 0.12, size=56, frame_no=14)

    t_made = T("that made me", 107)
    Kinetic("Leadership isn't doing everything", "True leadership {isn't} doing everything yourself", T("true leadership", 100) - 0.05, T("it is", 103) - 0.1, size=54, frame_no=15)
    Kinetic("Clear systems + trust", "It is building clear [systems] and [trusting] your team", T("it is", 103) - 0.05, t_made - 0.12, size=54, frame_no=15)

    # ---------------- chapter 3: leadership idols
    t_like = T("like me", 115); t_tome = T("to me", 124)
    Kinetic("Real leadership under pressure", "Real leadership under [pressure]", T("real leadership", 108) - 0.05, T("which brings", 110.3) - 0.1, size=60, frame_no=16)
    t_idol = T("my idol", 111.5)
    PhotoFrame("Syed Saddiq (collage back-left)", UP + "ironman.bin", 1220, 270, 300, 330, t_idol + 0.25, t_tome - 0.12, crop=(0.2, 0.0, 0.8, 1.0), rot=-7, frame_no=16, kb=(1.0, 1.06))
    PhotoFrame("Syed Saddiq (collage back-right)", UP + "debate.bin", 1530, 260, 300, 330, t_idol + 0.45, t_tome - 0.12, crop=(0.62, 0.0, 1.0, 0.92), rot=6, frame_no=16, kb=(1.0, 1.06))
    PhotoFrame("Syed Saddiq (collage front)", PH + "saddiq.jpg", 1390, 330, 330, 400, t_idol, t_tome - 0.12, crop=(0.0, 0.0, 1.0, 0.75), rot=-1.5,
               kicker="My idol", label="Syed Saddiq · 33", frame_no=16, kb=(1.0, 1.08))
    Kinetic("My idol", "My [idol]", t_idol - 0.05, t_like - 0.12, size=64, frame_no=16)
    Card("Not a nepo baby", "L", 180, t_like, t_tome - 0.12, [
        K("Like me"), Strike("Nepo baby", strike_at=T("baby", 116.8), size=48),
        Chip("NOT A NEPO BABY", at=T("baby", 116.8) + 0.25, style="red", size=24, stamp=True)], w=440, frame_no=17)
    Card("His mother a teacher", "L", 470, T("mother", 118.5), t_tome - 0.12, [
        IconLine("cap", "His mother is a [teacher] too", size=30)], w=440, frame_no=17)
    Kinetic("Success must be earned", "Success must be [earned] through [hard] [work]", T("success", 121.3) - 0.05, t_tome - 0.12, size=54, frame_no=17)

    t_ment = T("mentally", 131)
    Kinetic("Corporate Athlete", "A true [Corporate] [Athlete]", T("a true", 125) - 0.05, t_ment - 0.12, size=64, frame_no=18)
    pg = G.PillarGrid(T("trains", 126.5), t_ment - 0.12, [T("mind", 127), T("body", 128), T("emotions", 128.5), T("values", 129.5)]); pg.y = 280

    t_that = T("that is the well", 139)
    BehindWord("MIND (behind me)", "MIND", 520, 610, 170, t_ment, 134.2, color=GOLD, frame_no=19)
    PhotoFrame("Asian Debating Champion", UP + "debate.bin", 1230, 180, 560, 360, T("debate", 135) - 0.6, t_that - 0.12, crop=(0.0, 0.0, 1.0, 0.95), rot=1.5,
               kicker="UIA · 2015", label="Asian Debating Champion", anim="slideR", frame_no=19, kb=(1.0, 1.1), pan=(0.4, 0))
    Card("UIA logo", "L", 200, T("at", 133.5), t_that - 0.12, [LogoRow(UP + "uia_logo.bin", 90), K("International Islamic University Malaysia"),
        Hd("Super [sharp] debater", 40)], w=500, frame_no=19)

    t_ms = T("mental strength", 145)
    Card("My goal at UKM", "L", 190, T("well rounded", 139.5) - 0.1, t_ms - 0.12, [
        LogoRow(UP + "ukm_logo.bin", 80), K("My goal at UKM"), Hd("Well-rounded student", 42),
        IconLine("trophy", "Lead outside class", at=T("leading outside", 142)),
        IconLine("cap", "Keep strong grades", at=T("strong grades", 144))], w=520, frame_no=20)

    t_hon = T("honestly", 151.5)
    Kinetic("Sacrifice", "Mental strength = [sacrifice]", t_ms - 0.05, t_hon - 0.12, size=62, frame_no=21)
    PhotoFrame("Oxford", PH + "oxford.jpg", 1260, 200, 540, 330, T("oxford", 148.5) - 0.1, t_hon - 0.12, rot=-2, kicker="Oxford scholarship", label="Turned down twice",
               anim="slideR", frame_no=21, kb=(1.0, 1.1))
    Card("Declined x2", "L", 230, T("twice", 149.5) - 0.05, t_hon - 0.12, [
        Chip("DECLINED ×2", style="red", size=34, stamp=True, at=T("twice", 149.5)),
        Chip("TO SERVE MALAYSIA", at=T("serve", 150.5), style="gold", size=24)], w=420, anim="pop", frame_no=21)

    t_iwould = T("i would study", 158)
    Kinetic("I'd take it in a heartbeat", "If I got into Oxford, I'd take it in a [heartbeat]", T("if i got", 154.5) - 0.05, t_iwould - 0.12, size=54, frame_no=22)
    G.ECGCard(T("if i got", 154.5), T("heartbeat", 157), t_iwould - 0.12)

    t_why = T("why give", 174.5)
    Card("Logical path", "R", 160, t_iwould, t_why - 0.12, [
        K("The logical path"),
        IconLine("cap", "Study hard at Oxford", at=T("study", 158.5), size=30),
        IconLine("target", "Back to Malaysia", at=T("back to malaysia", 159.5), size=30),
        IconLine("briefcase", "Top management · GLC / MNC", at=T("top management", 161), size=30),
        Chip("= THE LOGICAL PATH", at=T("logical", 165), style="gold", size=24)], w=520, frame_no=23)
    Card("You get", "L", 200, T("you get better", 166), t_why - 0.12, [
        K("You get"),
        Chk("Physical & mental comfort", at=T("mental comfort", 168)),
        Chk("Huge bonuses", at=T("huge bonuses", 169.5)),
        Chk("Way more money", at=T("way more money", 170.5))], w=500, frame_no=23)

    t_img = T("imagine", 180)
    Kinetic("Headache", "Why give yourself a [headache]?", t_why - 0.05, T("fighting", 176) - 0.1, size=60, frame_no=24)
    Kinetic("Zero personal profit", "…for {zero} {personal} {profit}", T("fighting", 176) - 0.05, t_img - 0.12, size=60, frame_no=24)

    t_phys = T("physically", 187)
    Card("Selfish vs selfless", "L", 200, T("chosen", 182), t_phys - 0.12, [
        K("Imagine if he chose"),
        Strike("Selfish", strike_at=T("selfless", 184) - 0.2, size=52, at=T("selfish", 182.8)),
        Hd("→ [Selfless]", 52, at=T("selfless", 184))], w=420, frame_no=25)
    Kinetic("People of Muar", "What would have happened to the people of [Muar]?", T("what would have", 184.8) - 0.05, t_phys - 0.12, size=52, frame_no=25)

    t_also = T("he also used", 201)
    BehindWord("BODY (behind me)", "BODY", 520, 610, 170, t_phys, 190.4, color=GOLD, frame_no=26)
    PhotoFrame("Iron-man fit", UP + "ironman.bin", 1250, 190, 560, 300, T("stamina", 188.8) - 0.3, T("in", 190.4) + 0.2, rot=-1.5, kicker="Physically", label="Incredible stamina",
               anim="slideR", frame_no=26, kb=(1.0, 1.08))
    PhotoFrame("Langkah Muar", UP + "langkah_muar.bin", 1250, 150, 560, 330, T("in", 190.4) + 0.05, t_also - 0.12, crop=(0.25, 0.12, 1.0, 0.6), rot=1.5,
               kicker="Langkah Muar · 2024", label="Muar → Parliament", anim="pop", frame_no=26, kb=(1.0, 1.1), pan=(-0.3, 0))
    Card("200 km route", "L", 190, T("ran", 193) - 0.1, t_also - 0.12, [
        Counter("{n} KM", 0, 200, T("ran", 193), T("parliament", 195.3) + 0.4 - T("ran", 193), size=44, col=GOLD_TXT),
        P("Muar → Parliament, under the hot sun", size=22)], w=420, anim="pop", padding=20, frame_no=26)
    Card("RM160,000 raised", "L", 430, T("raising", 197.5), t_also - 0.12, [
        K("Raised for his people"),
        Counter("RM{n:,}+", 0, 160000, T("160", 198), 1.1, size=58, col=INK)], w=440, frame_no=26)

    t_emo = T("emotionally", 207)
    Kinetic("Image → PrimaValet → funding", "He used his [image] smartly: modelling for PrimaValet to [fund] his political work", t_also - 0.05, t_emo - 0.12, size=48, maxw=980, frame_no=27)

    t_he = T("he deeply", 211)
    BehindWord("EMOTIONS (behind me)", "EMOTIONS", 470, 615, 130, t_emo, t_he - 0.12, color=GOLD, frame_no=28)
    Card("Minister at 26", "R", 220, T("even as a minister", 209) - 0.1, t_he - 0.12, [
        K("Minister at"), Counter("{n}", 0, 26, T("minister", 209.8), 0.5, size=104, col=GOLD_TXT)], w=300, frame_no=28)

    t_dur = T("during the 2020", 218.8)
    PhotoFrame("Syed Saddiq with Tun Dr. Mahathir", UP + "saddiq_mahathir.bin", 1230, 180, 580, 360, T("his idol", 212.5) - 0.1, t_dur - 0.12, crop=(0.0, 0.0, 0.9, 1.0), rot=-1.5,
               kicker="His idol", label="Tun Dr. Mahathir", anim="slideR", frame_no=29, kb=(1.0, 1.1), pan=(0.3, 0))
    PhotoFrame("Tun Dr. Mahathir portrait", PH + "mahathir.jpg", 120, 200, 300, 360, T("his idol", 212.5) + 0.5, t_dur - 0.12, crop=(0, 0, 1, 0.8), rot=-4, frame_no=29, zone="L", kb=(1.0, 1.06))
    Kinetic("Change while honouring veterans", "Push for [change] while honouring [veterans]", T("proving", 214.5) - 0.05, t_dur - 0.12, size=52, frame_no=29)

    t_fin = T("finally", 225)
    PhotoFrame("Sheraton Move press conference", UP + "sheraton.bin", 1230, 190, 580, 360, t_dur - 0.05, t_fin - 0.12, crop=(0.0, 0.0, 0.92, 0.95), rot=1.5,
               kicker="2020", label="Sheraton Move", anim="slideR", frame_no=30, kb=(1.0, 1.1))
    Card("Court trials", "L", 230, T("years of court", 221) - 0.1, t_fin - 0.12, [
        IconLine("clipboard", "Years of court trials", size=32)], w=440, anim="pop", frame_no=30)
    Kinetic("Calm in public", "He stayed [calm] in public", T("he stayed", 223.3) - 0.05, t_fin - 0.12, size=60, frame_no=30)

    t_even = T("even on a personal", 234)
    BehindWord("VALUES (behind me)", "VALUES", 500, 610, 150, t_fin, 227.2, color=GOLD, frame_no=31)
    PhotoFrame("Undi18", UP + "undi18.bin", 1230, 180, 580, 360, T("passing", 226.4), t_even - 0.12, crop=(0.0, 0.0, 0.94, 0.94), rot=-1.5,
               kicker="2019", label="Undi18 law passed", anim="slideR", frame_no=31, kb=(1.0, 1.1), pan=(0.2, 0))
    Card("50% voting power", "L", 220, T("gave young", 229) - 0.1, t_even - 0.12, [
        K("Young people now hold"),
        Counter("{n}%+", 0, 50, T("50", 230.3), 0.8, size=80, col=GOLD_TXT),
        P("of the voting power", size=24), Bar(0.5, T("50", 230.3), 0.8)], w=440, frame_no=31)

    t_asan = T("as an", 250.5)
    PhotoFrame("Wedding: Syed Saddiq & Bella Astillah", UP + "bella.bin", 1230, 180, 580, 390, T("married", 236) - 0.1, t_asan - 0.12, rot=1.5,
               kicker="10 October 2026", label="Married Bella Astillah", anim="slideR", frame_no=32, kb=(1.0, 1.1))
    Card("Broke old traditions", "L", 220, T("broke", 240) - 0.1, T("instead of luxury", 241.5) - 0.12, [
        Chip("BROKE OLD TRADITIONS", style="red", size=28, stamp=True, at=T("broke", 240) - 0.05)], w=470, anim="pop", frame_no=32)
    Card("Hantaran", "L", 190, T("instead of luxury", 241.5), t_asan - 0.12, [
        K("His hantaran"),
        Strike("Luxury bags", strike_at=T("bags", 242.3) + 0.15, size=44),
        Counter("RM{n:,} EPF", 0, 100000, T("100", 243.8), 0.9, size=46, col=INK, at=T("100", 243.8) - 0.05, sfx_kind="tick"),
        IconLine("cap", "Master's degree · Taylor's", at=T("masters", 248))], w=520, frame_no=33)

    # ---------------- chapter 4: conclusion
    t_since = T("since id", 256)
    Card("ISTJ practical", "L", 200, t_asan, t_since - 0.12, [
        K("As an"), IconTitle("clipboard", "ISTJ", "PRACTICAL", at=T("practical", 253.5))], w=440, frame_no=34)
    Card("Owl forward-thinking", "R", 200, T("outward", 252), t_since - 0.12, [
        K("And an"), IconTitle("owl", "OWL", "FORWARD-THINKING", at=T("forward", 254.3))], w=470, frame_no=34)

    t_asi = T("as i build", 262)
    Kinetic("Balance", "True leadership = [balance]", t_since - 0.05, t_asi - 0.12, size=62, frame_no=35)
    G.BalanceCard(T("balancing", 258.5), t_asi - 0.12, [T("mind", 259), T("body", 260), T("emotions", 260.5), T("value", 261)])

    t_lets2 = T("lets not", 266.5)
    Card("My own path @ UKM", "L", 200, t_asi, t_lets2 - 0.12, [
        LogoRow(UP + "ukm_logo.bin", 84), K("My path"), Hd("Building my own path", 42)], w=480, frame_no=36)
    PhotoFrame("Role model (Syed Saddiq)", PH + "saddiq.jpg", 1440, 200, 330, 400, T("he is the role", 264.5) - 0.3, t_lets2 - 0.12, crop=(0.0, 0.0, 1.0, 0.75), rot=2,
               kicker="Role model", label="Syed Saddiq", frame_no=36, kb=(1.0, 1.06))

    t_thank = T("thank you", 273)
    Kinetic("Not just titles", "Let's not just chase ~titles~@%.2f" % (T("scientists", 267.6)), t_lets2 - 0.05, T("focused", 269) - 0.25, size=58, frame_no=37)
    Kinetic("Grow + real skills", "Grow in our [20s] and build the [real] [skills] to lead", T("focused", 269) - 0.2, t_thank - 0.12, size=54, frame_no=37)

    Card("Thank you", "L", 200, t_thank, NF / FPS + 1, [
        K("Thank you"), Hd("Nur Anis Nasuha", 50), P("Liberal Studies · UKM")], w=520, anim="pop", frame_no=38)

    TopBar2([0.0, T("growing up", 33), T("that made me", 107), T("as an", 250.5), NF / FPS],
            ["Self Introduction", "Personality Insights", "Leadership Idols", "Conclusion"])
    G.PillarTracker(T("survive", 129.5) + 0.5, t_asi - 0.12, t_ment, t_phys, t_emo, t_fin, t_since,
                    [T("mind", 259), T("body", 260), T("emotions", 260.5), T("value", 261)])

# ------------------------------------------------------------------ rendering with zoom + guards
def decode_frames(idx):
    out = {}
    if not idx: return out
    for a, b in contiguous(sorted(idx)):
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", "%.4f" % (a / FPS), "-i", S + "/src/raw.mov", "-frames:v", str(b - a + 1), "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
        for n in range(a, b + 1):
            out[n] = Image.frombytes("RGB", (W, H), p.stdout.read(W * H * 3))
        p.stdout.close(); p.wait()
    return out
def contiguous(xs):
    runs = []; s = p = xs[0]
    for x in xs[1:]:
        if x != p + 1: runs.append((s, p)); s = x
        p = x
    runs.append((s, p)); return runs

def render_range(a, b, outpath, faces):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H), "-r", str(FPS),
                            "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", outpath], stdin=subprocess.PIPE)
    zidx = [n for n in range(a, b) if zoom_at(n / FPS) and abs(zoom_at(n / FPS)[0] - 1) > 1e-4]
    src = decode_frames(zidx)
    viol = []
    for n in range(a, b):
        t = n / FPS
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for e in ELEMS: e.render(canvas, t)
        if canvas.crop((0, G.SUB_TOP, W, H)).getextrema()[3][1] > 0:
            viol.append(("subtitle", n)); canvas.paste((0, 0, 0, 0), (0, G.SUB_TOP, W, H))
        fx0, fy0, fx1, fy1 = faces[n]
        box = (max(0, fx0), max(0, fy0), min(W, fx1), min(H, fy1))
        if canvas.crop(box).getextrema()[3][1] > 0:
            viol.append(("face", n)); canvas.paste((0, 0, 0, 0), box)
        if n in src:
            z, cx, cy = zoom_at(t)
            vw, vh = W / z, H / z
            x0 = min(max(cx - vw / 2, 0), W - vw); y0 = min(max(cy - vh / 2, 0), H - vh)
            base = src[n].resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + vw, y0 + vh)).convert("RGBA")
            base.alpha_composite(canvas); canvas = base
        enc.stdin.write(canvas.tobytes())
    enc.stdin.close(); enc.wait()
    return viol

if __name__ == "__main__":
    build()
    mode = sys.argv[1]
    if mode == "plan":
        faces = G.load_faces()
        json.dump(sorted(G.SFX, key=lambda x: x["t"]), open(S + "/work/sfx.json", "w"), indent=0)
        rows = []
        for e in ELEMS:
            txt = ""
            if hasattr(e, "rows"):
                txt = " | ".join(re.sub(r"[\[\]{}~]", "", str(getattr(r, "text", "") or getattr(r, "title", "") or "")) for r in e.rows if getattr(r, "text", None) or getattr(r, "title", None))
            elif hasattr(e, "words"):
                txt = " ".join(w for w, st, t in e.words)
            rows.append({"text": txt, "name": e.name, "frame": e.frame_no, "zone": getattr(e, "zone", ""), "t_in": round(e.t_in, 3), "t_out": round(min(e.t_out, NF / FPS), 3), "bbox": [int(v) for v in e.bbox()]})
        json.dump(rows, open(S + "/work/elements.json", "w"), indent=1)
        bad = 0
        for e in rows:
            x0, y0, x1, y1 = e["bbox"]
            if y1 > G.SUB_TOP + 25: print("BBOX into subtitle band:", e["name"], e["bbox"]); bad += 1
            if e["zone"] == "Behind": continue
            for n in range(int(e["t_in"] * FPS), min(NF, int(e["t_out"] * FPS) + 1)):
                fx0, fy0, fx1, fy1 = faces[n]
                if not (x1 <= fx0 or x0 >= fx1 or y1 <= fy0 or y0 >= fy1):
                    print("BBOX overlaps face:", e["name"], e["bbox"], "frame", n, faces[n]); bad += 1; break
        for i, p in enumerate(rows):
            for q in rows[i + 1:]:
                if p["t_in"] < q["t_out"] and q["t_in"] < p["t_out"] and "Top bar" not in p["name"] + q["name"] and "collage" not in p["name"] + q["name"]:
                    a, b2 = p["bbox"], q["bbox"]
                    ix = min(a[2], b2[2]) - max(a[0], b2[0]); iy = min(a[3], b2[3]) - max(a[1], b2[1])
                    if ix > 60 and iy > 60: print("OVERLAP %-36s %-36s %.2f-%.2f" % (p["name"], q["name"], max(p["t_in"], q["t_in"]), min(p["t_out"], q["t_out"])))
        print("elements", len(rows), "sfx", len(G.SFX), "static issues", bad)
    elif mode == "still":
        out = sys.argv[2]
        for ts in sys.argv[3:]:
            t = float(ts); canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for e in ELEMS: e.render(canvas, t)
            canvas.save("%s/ov_%07.2f.png" % (out, t))
    elif mode == "render":
        a, b, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        faces = G.load_faces()
        v = render_range(a, b, outp, faces)
        json.dump(v, open(outp + ".viol.json", "w"))
        print("done", a, b, "violations", len(v))
