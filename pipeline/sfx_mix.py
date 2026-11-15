"""Synthesise original SFX (no samples, no music) and mix them under the cleaned voice.

Ducking rule: each effect is placed at its cue; its peak is held at least ~16 dB under the
voice's short-term peak level, and every effect is additionally capped at -24 dBFS.
"""
import json, sys, subprocess
import numpy as np

S = sys.argv[1]
SR = 44100
N = 12159936  # exact original sample count
rng = np.random.default_rng(7)

def env(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
    return e

def lp(x, cutoff):  # one-pole lowpass
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y

def whoosh():
    n = int(0.38 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # sweeping band: lowpass cutoff rises then falls, shaped by a soft bell envelope
    cut = 600 + 3400 * np.sin(np.pi * t / t[-1]) ** 2
    y = np.empty(n); s = 0.0
    for i in range(n):
        a = np.exp(-2 * np.pi * cut[i] / SR); s = (1 - a) * x[i] + a * s; y[i] = s
    y = y - lp(y, 250)
    e = np.sin(np.pi * t / t[-1]) ** 1.6
    return y * e

def pop():
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = 950 * np.exp(-t * 28) + 380
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.002, 0.025)

def tick():
    n = int(0.035 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2600 * t) * 0.7 + rng.standard_normal(n) * 0.25) * env(n, 0.0008, 0.008)

def count():
    n = int(0.022 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * env(n, 0.0005, 0.005)

def thump():
    n = int(0.28 * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 52
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.09)
    click = lp(rng.standard_normal(n), 1800) * env(n, 0.001, 0.012) * 0.8
    return body + click

GEN = {"whoosh": whoosh, "pop": pop, "tick": tick, "count": count, "thump": thump}
BASE_DB = {"whoosh": -29, "pop": -27, "tick": -28, "count": -33, "thump": -25}
CACHE = {k: (lambda v: v / np.max(np.abs(v)))(g()) for k, g in GEN.items()}

voice = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", S + "/work/voice_aligned.wav", "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)
assert len(voice) == N, len(voice)
mono = voice.mean(1)
win = int(0.3 * SR)

cues = json.load(open(S + "/work/sfx.json"))
cues.sort(key=lambda c: c["t"])
fx = np.zeros(N)
placed, last = [], {}
for c in cues:
    k = c["kind"]
    # thin out dense clusters: same kind within 70 ms (counters excluded), any kind within 30 ms
    if k != "count" and c["t"] - last.get(k, -9) < 0.07: continue
    s = int(round(c["t"] * SR))
    if s >= N: continue
    snd = CACHE[k]
    gdb = BASE_DB[k] + 20 * np.log10(max(c["gain"], 1e-3))
    vpk = np.max(np.abs(mono[max(0, s - win):s + win])) if s < N else 0
    vdb = 20 * np.log10(vpk + 1e-9)
    if vpk > 0.05: gdb = min(gdb, vdb - 16)
    gdb = min(gdb, -24)
    g = 10 ** (gdb / 20)
    e = min(N, s + len(snd))
    fx[s:e] += snd[:e - s] * g
    last[k] = c["t"]
    placed.append({"t": c["t"], "kind": k, "level_dbfs": round(gdb, 1), "note": c["note"]})

mix = voice + fx[:, None]
pk = np.max(np.abs(mix))
print("sfx placed", len(placed), "of", len(cues), "mix peak dBFS %.2f" % (20 * np.log10(pk)), "fx peak dBFS %.2f" % (20 * np.log10(np.max(np.abs(fx)) + 1e-12)))
if pk > 0.89:
    mix *= 0.89 / pk
json.dump(placed, open(S + "/work/sfx_placed.json", "w"), indent=0)
p = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", S + "/work/final_audio.wav"],
                   input=mix.astype(np.float32).tobytes())
print("wrote final_audio.wav", p.returncode)
