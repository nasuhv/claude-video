import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8", cpu_threads=4)
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
segs, info = m.transcribe(a, language="en", word_timestamps=True, beam_size=5, temperature=0,
    vad_filter=False, condition_on_previous_text=False,
    initial_prompt="Um, uh, I- I mean, so- so, er, hmm. Uh, like, you know, um, the- the plan.")
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"s":w.start,"e":w.end,"w":w.word,"p":w.probability} for w in s.words]})
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
json.dump(out, open(sys.argv[2],"w"), indent=1)
