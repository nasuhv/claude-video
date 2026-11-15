import json, sys
S, OUT = sys.argv[1], sys.argv[2]
els = json.load(open(S + "/work/elements.json"))
sfx = json.load(open(S + "/work/sfx_placed.json"))
ver = open(S + "/work/verify_v2.txt").read().strip()

REV2 = [
 "**Opening:** keyframe zoom (1.18× easing out to 1.0×) with whoosh + pop at 0:00, before “Assalamu'alaikum”. Greeting text box removed.",
 "**Chapters (top left):** now exactly 01/04 Self Introduction (0:00–0:34) · 02/04 Personality Insights (0:34–1:47) · 03/04 Leadership Idols (1:47–4:10) · 04/04 Conclusion (4:11–4:36).",
 "**S-Log part:** colour-grade slider panel and the S-LOG tag removed.",
 "**“Let's get started”, “Have you ever planned your life so carefully”, the big idea:** centred above your head, word by word, each word popping in as you say it.",
 "**My life plan:** icons instead of ticks (graduation cap = Study, briefcase = Career, target = Goals). The card still cracks and falls on “falls apart”.",
 "**Name:** no name text box.",
 "**Zodiac:** animated zodiac wheel that spins and lands on Capricorn (22 Dec – 19 Jan).",
 "**Creativity + detail:** at the top, with a floating icon for every word: bulb (creativity), magnifier (detail), play (multimedia), megaphone (digital marketing), code (IT), pen (journalism).",
 "**Mum:** your photo pops in with a handwritten “This is my mum!” and an arrow pointing to her, plus a “My mum · A dedicated teacher” label.",
 "**EDUCATION & DISCIPLINE:** pop one by one *behind* you (person cut-out).",
 "**Personality tests:** “Personality test 1: 16Personalities · Myers-Briggs Type Indicator (MBTI) → ISTJ · The Logistician” (clipboard icon) and “Personality test 2: DOPE Personality Test → Owl” (owl icon).",
 "**Diploma:** UniKL logo card. **PNB / ASNB:** Merdeka 118 photo with “Permodalan Nasional Berhad · Marketing · ASNB”. No ASNB logo was supplied, so it's text.",
 "**Head of Media Exco:** swinging lanyard ID badge (UKM logo, “Media Exco · Kolej Keris Mas”). No Kolej Keris Mas photo was supplied.",
 "**Fewer boxes:** most sentences are now clean word-by-word text, and the cards that remain carry icons, logos or photos.",
 "**Many more photos** (yours), with keyframed Ken Burns motion: Syed Saddiq collage, debate (with UIA logo card), Oxford, iron-man photo, Langkah Muar, Syed Saddiq with Tun Dr Mahathir, Sheraton Move, Undi18, wedding with Bella Astillah.",
 "**Pillar titles** MIND / BODY / EMOTIONS / VALUES appear behind you.",
 "**No photo credits on screen** (see the caption credits below).",
]
PHOTOS = [
 ("Me with my mum", "You (Drive)"), ("Syed Saddiq debate / UIA 2015", "You"), ("UIA, UniKL, UKM logos", "You"),
 ("Wedding: Syed Saddiq & Bella Astillah", "You"), ("Sheraton Move", "You"), ("Undi18", "You"),
 ("Syed Saddiq with Tun Dr Mahathir", "You"), ("Langkah Muar (headline cropped out)", "You"), ("Syed Saddiq iron-man", "You"),
 ("Syed Saddiq portrait", "Wikimedia Commons, US Embassy KL, public domain"), ("Tun Dr Mahathir portrait", "Wikimedia Commons, kremlin.ru, CC BY 4.0"),
 ("Radcliffe Camera, Oxford", "Wikimedia Commons, Julian Herzog, CC BY 4.0"), ("Merdeka 118", "Wikimedia Commons, Ahmad Ali Karim, CC0"),
]

def tc(t):
    m = int(t // 60); s = t - 60 * m
    return "%d:%05.2f" % (m, s)

ZONE = {"L": "Left", "R": "Right", "T": "Top bar"}
STUMBLES = [
    # (start, end, priority, words, what happened)
    (72.40, 73.50, "High", "“my corporate **perfectionism** became a problem”", "Both transcription passes hear **“professionalism”**. Your subtitle says “perfectionism”, so this looks like a slip that changes the meaning. Strongest re-shoot candidate."),
    (227.00, 227.60, "High", "“passing the **Undi18** law”", "Both passes hear **“Undi-80”**: “eighteen” lands like “eighty”. Factual risk for anyone who isn't reading the subtitles."),
    (250.90, 252.70, "High", "“As an **ISTJ** and an **Owl**”", "Slurred, with an extra ~0.9 s on “ISTJ”. Passes hear “As I teach and I will” / “an SITJ and outward”."),
    (267.70, 269.20, "High", "“chase **titles. Let's focus** on…”", "The two sentences run together with no pause. Both passes hear “chase scientists that's focused”."),
    (271.40, 272.75, "High", "“building the **real skills to lead**”", "Rushed final line. Both passes hear “the rarest case to late”."),
    (80.12, 81.20, "Medium", "“Realizing **micromanaging** was…”", "Swallowed word. Both passes hear “my chromatography”."),
    (181.40, 181.90, "Medium", "“Imagine if **Syed Saddiq** had chosen…”", "Name blurred. Both passes hear “sex addict”, an unfortunate mishearing in a talk about him. Also blurred at 1:52.9 (“Saeed Saeed”) and 4:16.4 (“Since ID”)."),
    (178.26, 179.60, "Medium", "“with **zero personal** profit”", "“personal” is clipped. Both passes hear “0% of profit”."),
    (204.24, 205.60, "Medium", "“modelling for **PrimaValet** to **fund**”", "“fund” sounds like “find” (both passes)."),
    (224.10, 224.70, "Medium", "“he stayed calm in **public**”", "Last word swallowed. Both passes hear “Pamdi”."),
    (249.24, 249.95, "Medium", "“at **Taylor's** University”", "Both passes hear “the U.S. University”."),
    (41.56, 42.40, "Low", "“16Personalities and **DOPE** tests”", "Both passes hear “doctors”. The on-screen DOPE card covers it."),
    (220.10, 220.60, "Low", "“2020 **Sheraton** Move”", "Both passes hear “chariot move”. The on-screen card spells it out."),
    (68.20, 70.90, "Low", "“Head of the **Media Exco** … at **Kolej Keris Mas**”", "Fast delivery of names (heard as “media ed school”, “college Christmas”). The on-screen cards spell them out."),
    (117.00, 117.50, "Low", "“not a **nepo** baby”", "Both passes hear “nipple baby”. The on-screen strike card says “Nepo baby”."),
    (8.34, 8.90, "Low", "“**Huh?**” (unscripted)", "Off-script interjection just before the grade switch. It reads as a natural reaction to the colour gag, so probably keep it."),
    (22.18, 23.42, "Low", "“**Hi,** … I'm Nur Anis…”", "“Hi” is held ~1.2 s before the name. A slight hesitation, mostly harmless."),
    (99.62, 100.40, "Low", "“That taught me **a big lesson**”", "One pass hears “a bit like I said”, the other hears it correctly. Mild slur."),
]

L = []
L.append("# Change log, revision 2: “Leadership Begins When the Plan Falls Apart”\n")
L.append("## What changed in revision 2 (your 20 notes)\n")
for x in REV2: L.append("- " + x)
L.append("")
L.append("Source: `raw.mov` (HEVC 10-bit, 1920×1080, 30 fps, 8272 frames, 4:35.73). Output: `final.mp4` (H.264 High, 8-bit 4:2:0, BT.709, CRF 16, AAC 256 kb/s 44.1 kHz). Resolution, frame rate, frame count and length are identical to the source.\n")
L.append("## The three rules: how they were enforced and checked\n")
L.append("1. **No cuts or retiming.** No cuts, trims, speed changes or freezes. At your request there are two keyframe zooms (0:00.00–0:00.85 and 4:34.35–end), placed only where no subtitles are on screen so your subtitles never scale. Audio filters are all sample-for-sample. One filter added a fixed 25 ms (1102-sample) latency, which was removed exactly. Cross-correlation against the original shows **0-sample offset** at 5, 60, 120, 180, 240 and 265 s.")
L.append("2. **Subtitles untouched.** The burned-in bilingual subtitles sit at y≈875–985 for the whole video. Every graphic is kept above y=850, enforced per frame by a hard guard. No captions were added.")
L.append("3. **Nothing on the face.** The face was tracked on all 8272 frames (MediaPipe face mesh), then padded (+30 % each side, +45 % above for the hijab and forehead, +25 % below). The renderer checked **every frame** (stricter than every 0.5 s) for any graphic pixel inside that box: **0 violations**. The exported MP4 was then compared with the original **every 0.5 s** (552 checks):\n")
L.append("```\n" + ver + "\n```\n")
L.append("The large numbers come only from the two zoom moments (0:00–0:00.5 and 4:34.5–4:35), where the whole picture is intentionally scaled. Excluding those, every check is re-encode noise only (mean ~3.8 / 255). The behind-you words (EDUCATION, DISCIPLINE, MIND, BODY, EMOTIONS, VALUES) sit below the face box and are masked by a per-frame person cut-out, so they pass behind your body.\n")

L.append("## Step 1: Audio clean-up (your voice only, no re-synthesis)\n")
L.append("Chain (ffmpeg), in order:\n")
L.append("| Step | Filter | Why |\n|---|---|---|")
L.append("| De-clip | `adeclip` | The original peaked at 0 dBFS with ~13,700 clipped samples, mostly in the first 10 s |")
L.append("| Plosives / rumble | `highpass 75 Hz` | Removes P/B pops and wind/handling rumble below the voice |")
L.append("| Noise reduction | `afftdn nr=8 nf=-55` | Light only: the floor between phrases was already ≈ −80 dB |")
L.append("| Mouth clicks | `adeclick threshold=3` | Removes short impulsive clicks |")
L.append("| Harsh S | `deesser i=0.35` | Softens sibilance |")
L.append("| Levelling | `acompressor −22 dB, 2.5:1` | Evens out loud vs soft phrases |")
L.append("| Loudness | `+4.3 dB` then true-peak limiter (latency-compensated) | Final **−16.0 LUFS integrated, −1.7 dBFS peak** (source was −9.7 LUFS and clipping) |")
L.append("| Latency fix | shift −1102 samples, pad tail | Re-aligns to the original to the exact sample |")
L.append("\nNo time-stretching, voice cloning, re-synthesis or replacement. No music, risers, drones or ambience were added.\n")

L.append("## Step 1b: Stumble list (for your re-shoot decision)\n")
L.append("Method: I transcribed the audio twice (once normally, once primed to keep fillers and repeats), then compared both passes with your script/subtitles and with word timing. A spot is listed when both passes mishear the same word (the delivery really is unclear) or when timing shows a hesitation. **Please confirm by ear before deciding**: automatic transcription can't tell an accent from a slip with certainty. Nothing was removed and no extra sounds were placed on any stumbled word. Where a card already spells out an unclear word on screen (DOPE, Media Exco, Kolej Keris Mas, Sheraton, Nepo baby, PrimaValet, Undi18, Taylor's), that is noted, since the card helps the viewer read past the slip.\n")
L.append("| # | Timecode | Priority | Words (script) | What's heard / notes |\n|---|---|---|---|---|")
for i, (a, b, p, w, n) in enumerate(sorted(STUMBLES, key=lambda x: x[0]), 1):
    L.append("| %d | %s–%s | %s | %s | %s |" % (i, tc(a), tc(b), p, w, n))
L.append("")

L.append("## Step 2: Graphics (%d elements covering all 38 storyboard frames)\n" % len(els))
L.append("Layout: **Left zone** x 72–760, **Right zone** x 1168–1848, **Top bar** y 18–112. All storyboard “LT” items were moved into the left/right zones; nothing sits in the bottom of the frame. Every graphic is timed to the words as actually spoken (word-level timestamps), not the storyboard's estimates. Style follows your Instagram reference: frosted white rounded cards, soft shadow, mono micro-labels, segmented progress bar and chapter pill top-left. Key words get **gold** pills, problems are **red**, and crossed-out ideas get an animated red strike. Motion: 0.3 s slide-ins from the sides and 0.3 s pop-ins, both with a small overshoot, and a 0.22 s exit before the next sentence.\n")
L.append("| SB frame | Start | End | Zone | Graphic | Content |\n|---|---|---|---|---|---|")
for e in sorted(els, key=lambda e: (e["t_in"], e["frame"])):
    L.append("| %s | %s | %s | %s | %s | %s |" % (e["frame"] if e["frame"] else "all", tc(e["t_in"]), tc(e["t_out"]), ZONE.get(e["zone"], e["zone"]), e["name"], (e.get("text") or "").replace("|", "·")))
L.append("")
L.append("### Photos used (no credits on screen, as you asked)\n")
L.append("| Photo | Source |\n|---|---|")
for a,b in PHOTOS: L.append("| %s | %s |" % (a,b))
L.append("\n**Put these credits in your post caption or description** (the free licences ask for it): Tun Dr Mahathir photo: kremlin.ru, CC BY 4.0. Oxford photo: Julian Herzog, CC BY 4.0. Syed Saddiq portrait: US Embassy Kuala Lumpur, public domain. Merdeka 118: Ahmad Ali Karim, CC0. All via Wikimedia Commons. The photos you supplied are news/official images: fine for a class assignment, but they're copyrighted if you post publicly.\n")
L.append("## Step 4: Sound effects (%d placed, all synthesised from scratch)\n" % len(sfx))
L.append("Kinds: soft **whoosh** (slide-ins, strikes, chapter changes), **pop** (cards, chips, tiles), **tick** (check marks), **thump** (stamps such as GRADED, NOT A NEPO BABY, DECLINED ×2, = 0, BROKE OLD TRADITIONS, and the PLAN crack), and **count** ticks during number count-ups. Every effect is capped at −24 dBFS and at least 16 dB under your voice's local peak; the loudest effect is −25 dBFS against voice peaks of about −2 dBFS. 9 cues were dropped where they fell within 70 ms of the same kind.\n")
L.append("| Time | Kind | Level (dBFS) | Trigger |\n|---|---|---|---|")
for c in sfx:
    L.append("| %s | %s | %.1f | %s |" % (tc(c["t"]), c["kind"], c["level_dbfs"], c["note"]))
L.append("")
L.append("## References (revision 1)\n")
L.append("- Instagram reel (latest reference): **opened and studied**. I matched its look (white rounded UI cards, mono step pill with segmented progress bar, accent-highlighted words, numbered icon tiles) using your gold accent. None of its music or audio was used.")
L.append("- Threads link: the post page opened (a text tips post), but its video could **not** be downloaded, so I used the fallback brief there: kinetic text, 0.3 s pop/slide with overshoot, flat icons, rounded cards, gold keywords.")
open(OUT, "w").write("\n".join(L) + "\n")
print("wrote", OUT, len(L), "lines")
