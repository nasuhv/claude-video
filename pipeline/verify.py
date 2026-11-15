"""End-to-end check of the exported MP4 against the original.
Every 0.5 s: pixel difference (final vs original) inside the face box and inside the subtitle band.
A graphic there would produce large differences; re-encoding noise stays small.
Also: frame count, duration, audio length, audio sync (cross-correlation)."""
import json, subprocess, sys
import numpy as np
S = sys.argv[1]; FIN = sys.argv[2]
W, H, FPS = 1920, 1080, 30
faces = json.load(open(S + "/work/faces.json"))

def probe(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries", "stream=codec_type,width,height,r_frame_rate,nb_read_frames,duration,sample_rate:format=duration", "-of", "json", p], capture_output=True, text=True).stdout
    return json.loads(o)

def frames(p):
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-vf", "select='not(mod(n\\,15))',format=rgb24", "-fps_mode", "passthrough", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(W * H * 3)
        if len(b) < W * H * 3: return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.int16)

sys.path.insert(0, S + "/scripts")
import importlib.util
spec = importlib.util.spec_from_file_location("gfx", S + "/scripts/gfx.py"); gfx = importlib.util.module_from_spec(spec)
import os; os.environ["SCR"] = S; spec.loader.exec_module(gfx)
zones = gfx.load_faces()

res = []
for i, (a, b) in enumerate(zip(frames(S + "/src/raw.mov"), frames(FIN))):
    n = i * 15
    x0, y0, x1, y1 = zones[n]
    x0, y0 = max(0, x0), max(0, y0)
    d = np.abs(a - b).max(2)
    face = d[y0:y1, x0:x1]; sub = d[gfx.SUB_TOP:, :]
    ctrl = d[200:800, 1000:1100] if False else None
    res.append({"t": n / FPS, "face_p999": float(np.percentile(face, 99.9)), "face_mean": float(face.mean()),
                "sub_p999": float(np.percentile(sub, 99.9)), "sub_mean": float(sub.mean())})
fp = max(r["face_p999"] for r in res); sp = max(r["sub_p999"] for r in res)
fm = max(r["face_mean"] for r in res); sm = max(r["sub_mean"] for r in res)
worst = sorted(res, key=lambda r: -r["face_p999"])[:3]
print("checks", len(res), "(every 0.5 s)")
print("face zone: worst 99.9th-pct diff %.1f, worst mean diff %.2f  (0-255 scale)" % (fp, fm))
print("subtitle band: worst 99.9th-pct diff %.1f, worst mean diff %.2f" % (sp, sm))
print("worst face samples", [(round(r["t"], 1), round(r["face_p999"], 1)) for r in worst])
json.dump(res, open(S + "/work/verify_samples.json", "w"))

po, pf = probe(S + "/src/raw.mov"), probe(FIN)
for name, p in (("original", po), ("final", pf)):
    v = [s for s in p["streams"] if s["codec_type"] == "video"][0]; au = [s for s in p["streams"] if s["codec_type"] == "audio"][0]
    print(name, "%sx%s" % (v["width"], v["height"]), v["r_frame_rate"], "frames", v["nb_read_frames"], "video dur", v.get("duration"), "audio dur", au.get("duration"), au["sample_rate"], "container", p["format"]["duration"])

def rd(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", "44100", "-f", "f32le", "-"], capture_output=True).stdout, np.float32).astype(np.float64)
A, B = rd(S + "/src/raw.mov"), rd(FIN)
offs = []
for t0 in (5, 60, 120, 180, 240, 265):
    s = int(t0 * 44100); n = 44100 * 6; x = A[s:s + n]; y = B[s - 3000:s + n + 3000]
    N2 = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    c = np.fft.irfft(np.fft.rfft(y, N2) * np.conj(np.fft.rfft(x, N2)), N2)[:len(y) - len(x) + 1]
    offs.append(int(np.argmax(c)) - 3000)
print("audio offset vs original (samples) at 5/60/120/180/240/265 s:", offs)
