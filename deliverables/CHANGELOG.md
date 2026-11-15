# Change log, revision 3: “Leadership Begins When the Plan Falls Apart”

## What changed in revision 3

- **Spacing around every highlight box** (yellow and red), in the text above your head *and* inside cards: 0:11 Let's get started, 0:47 mirror, 0:49 logic / plan / goals, 1:14 perfectionism / problem, 1:18 control every single design, 1:22 burning me out, 1:38 amazing work, 1:42 isn't, and all others.
- **0:54:** card now reads “Diploma in Multimedia” (UniKL MIIT).
- **0:57:** black “Permodalan Nasional Berhad / Marketing · ASNB” label removed from the Merdeka 118 photo.
- **1:14:** “problem” now stays on screen ~1 s before the next line.
- **1:35:** phone and “LAUNCHED ON TIME” stamp centred on the same line.
- **1:54:** only the white-shirt Syed Saddiq photo; the other two removed.
- **2:43:** “Top management” with “GLC / MNC” on its own line below.
- **3:23:** text now reads “He used his image smartly by modelling for PrimaValet to fund his political work”.
- **4:11:** ISTJ and Owl cards enter faster, right as you say “ISTJ” and “Owl”.

## Earlier: what changed in revision 2 (your 20 notes)

- **Opening:** keyframe zoom (1.18× easing out to 1.0×) with whoosh + pop at 0:00, before “Assalamu'alaikum”. Greeting text box removed.
- **Chapters (top left):** now exactly 01/04 Self Introduction (0:00–0:34) · 02/04 Personality Insights (0:34–1:47) · 03/04 Leadership Idols (1:47–4:10) · 04/04 Conclusion (4:11–4:36).
- **S-Log part:** colour-grade slider panel and the S-LOG tag removed.
- **“Let's get started”, “Have you ever planned your life so carefully”, the big idea:** centred above your head, word by word, each word popping in as you say it.
- **My life plan:** icons instead of ticks (graduation cap = Study, briefcase = Career, target = Goals). The card still cracks and falls on “falls apart”.
- **Name:** no name text box.
- **Zodiac:** animated zodiac wheel that spins and lands on Capricorn (22 Dec – 19 Jan).
- **Creativity + detail:** at the top, with a floating icon for every word: bulb (creativity), magnifier (detail), play (multimedia), megaphone (digital marketing), code (IT), pen (journalism).
- **Mum:** your photo pops in with a handwritten “This is my mum!” and an arrow pointing to her, plus a “My mum · A dedicated teacher” label.
- **EDUCATION & DISCIPLINE:** pop one by one *behind* you (person cut-out).
- **Personality tests:** “Personality test 1: 16Personalities · Myers-Briggs Type Indicator (MBTI) → ISTJ · The Logistician” (clipboard icon) and “Personality test 2: DOPE Personality Test → Owl” (owl icon).
- **Diploma:** UniKL logo card. **PNB / ASNB:** Merdeka 118 photo with “Permodalan Nasional Berhad · Marketing · ASNB”. No ASNB logo was supplied, so it's text.
- **Head of Media Exco:** swinging lanyard ID badge (UKM logo, “Media Exco · Kolej Keris Mas”). No Kolej Keris Mas photo was supplied.
- **Fewer boxes:** most sentences are now clean word-by-word text, and the cards that remain carry icons, logos or photos.
- **Many more photos** (yours), with keyframed Ken Burns motion: Syed Saddiq collage, debate (with UIA logo card), Oxford, iron-man photo, Langkah Muar, Syed Saddiq with Tun Dr Mahathir, Sheraton Move, Undi18, wedding with Bella Astillah.
- **Pillar titles** MIND / BODY / EMOTIONS / VALUES appear behind you.
- **No photo credits on screen** (see the caption credits below).

Source: `raw.mov` (HEVC 10-bit, 1920×1080, 30 fps, 8272 frames, 4:35.73). Output: `final.mp4` (H.264 High, 8-bit 4:2:0, BT.709, CRF 16, AAC 256 kb/s 44.1 kHz). Resolution, frame rate, frame count and length are identical to the source.

## The three rules: how they were enforced and checked

1. **No cuts or retiming.** No cuts, trims, speed changes or freezes. At your request there are two keyframe zooms (0:00.00–0:00.85 and 4:34.35–end), placed only where no subtitles are on screen so your subtitles never scale. Audio filters are all sample-for-sample. One filter added a fixed 25 ms (1102-sample) latency, which was removed exactly. Cross-correlation against the original shows **0-sample offset** at 5, 60, 120, 180, 240 and 265 s.
2. **Subtitles untouched.** The burned-in bilingual subtitles sit at y≈875–985 for the whole video. Every graphic is kept above y=850, enforced per frame by a hard guard. No captions were added.
3. **Nothing on the face.** The face was tracked on all 8272 frames (MediaPipe face mesh), then padded (+30 % each side, +45 % above for the hijab and forehead, +25 % below). The renderer checked **every frame** (stricter than every 0.5 s) for any graphic pixel inside that box: **0 violations**. The exported MP4 was then compared with the original **every 0.5 s** (552 checks):

```
checks 552 (every 0.5 s)
face zone: worst 99.9th-pct diff 178.0, worst mean diff 41.66  (0-255 scale)
subtitle band: worst 99.9th-pct diff 208.4, worst mean diff 61.38
worst face samples [(275.0, 178.0), (274.5, 111.0), (0.5, 100.0)]
original 1920x1080 30/1 frames 8272 video dur 275.733333 audio dur 275.713741 44100 container 275.733333
final 1920x1080 30/1 frames 8272 video dur 275.733333 audio dur 275.712993 44100 container 275.733333
audio offset vs original (samples) at 5/60/120/180/240/265 s: [0, 0, 0, 0, 0, 0]
excluding the 2 zoom moments: 547 checks; face worst p99.9 16.0 mean 3.82; subtitle worst p99.9 17.0 mean 3.80
```

The large numbers come only from the two zoom moments (0:00–0:00.5 and 4:34.5–4:35), where the whole picture is intentionally scaled. Excluding those, every check is re-encode noise only (mean ~3.8 / 255). The behind-you words (EDUCATION, DISCIPLINE, MIND, BODY, EMOTIONS, VALUES) sit below the face box and are masked by a per-frame person cut-out, so they pass behind your body.

## Step 1: Audio clean-up (your voice only, no re-synthesis)

Chain (ffmpeg), in order:

| Step | Filter | Why |
|---|---|---|
| De-clip | `adeclip` | The original peaked at 0 dBFS with ~13,700 clipped samples, mostly in the first 10 s |
| Plosives / rumble | `highpass 75 Hz` | Removes P/B pops and wind/handling rumble below the voice |
| Noise reduction | `afftdn nr=8 nf=-55` | Light only: the floor between phrases was already ≈ −80 dB |
| Mouth clicks | `adeclick threshold=3` | Removes short impulsive clicks |
| Harsh S | `deesser i=0.35` | Softens sibilance |
| Levelling | `acompressor −22 dB, 2.5:1` | Evens out loud vs soft phrases |
| Loudness | `+4.3 dB` then true-peak limiter (latency-compensated) | Final **−16.0 LUFS integrated, −1.7 dBFS peak** (source was −9.7 LUFS and clipping) |
| Latency fix | shift −1102 samples, pad tail | Re-aligns to the original to the exact sample |

No time-stretching, voice cloning, re-synthesis or replacement. No music, risers, drones or ambience were added.

## Step 1b: Stumble list (for your re-shoot decision)

Method: I transcribed the audio twice (once normally, once primed to keep fillers and repeats), then compared both passes with your script/subtitles and with word timing. A spot is listed when both passes mishear the same word (the delivery really is unclear) or when timing shows a hesitation. **Please confirm by ear before deciding**: automatic transcription can't tell an accent from a slip with certainty. Nothing was removed and no extra sounds were placed on any stumbled word. Where a card already spells out an unclear word on screen (DOPE, Media Exco, Kolej Keris Mas, Sheraton, Nepo baby, PrimaValet, Undi18, Taylor's), that is noted, since the card helps the viewer read past the slip.

| # | Timecode | Priority | Words (script) | What's heard / notes |
|---|---|---|---|---|
| 1 | 0:08.34–0:08.90 | Low | “**Huh?**” (unscripted) | Off-script interjection just before the grade switch. It reads as a natural reaction to the colour gag, so probably keep it. |
| 2 | 0:22.18–0:23.42 | Low | “**Hi,** … I'm Nur Anis…” | “Hi” is held ~1.2 s before the name. A slight hesitation, mostly harmless. |
| 3 | 0:41.56–0:42.40 | Low | “16Personalities and **DOPE** tests” | Both passes hear “doctors”. The on-screen DOPE card covers it. |
| 4 | 1:08.20–1:10.90 | Low | “Head of the **Media Exco** … at **Kolej Keris Mas**” | Fast delivery of names (heard as “media ed school”, “college Christmas”). The on-screen cards spell them out. |
| 5 | 1:12.40–1:13.50 | High | “my corporate **perfectionism** became a problem” | Both transcription passes hear **“professionalism”**. Your subtitle says “perfectionism”, so this looks like a slip that changes the meaning. Strongest re-shoot candidate. |
| 6 | 1:20.12–1:21.20 | Medium | “Realizing **micromanaging** was…” | Swallowed word. Both passes hear “my chromatography”. |
| 7 | 1:39.62–1:40.40 | Low | “That taught me **a big lesson**” | One pass hears “a bit like I said”, the other hears it correctly. Mild slur. |
| 8 | 1:57.00–1:57.50 | Low | “not a **nepo** baby” | Both passes hear “nipple baby”. The on-screen strike card says “Nepo baby”. |
| 9 | 2:58.26–2:59.60 | Medium | “with **zero personal** profit” | “personal” is clipped. Both passes hear “0% of profit”. |
| 10 | 3:01.40–3:01.90 | Medium | “Imagine if **Syed Saddiq** had chosen…” | Name blurred. Both passes hear “sex addict”, an unfortunate mishearing in a talk about him. Also blurred at 1:52.9 (“Saeed Saeed”) and 4:16.4 (“Since ID”). |
| 11 | 3:24.24–3:25.60 | Medium | “modelling for **PrimaValet** to **fund**” | “fund” sounds like “find” (both passes). |
| 12 | 3:40.10–3:40.60 | Low | “2020 **Sheraton** Move” | Both passes hear “chariot move”. The on-screen card spells it out. |
| 13 | 3:44.10–3:44.70 | Medium | “he stayed calm in **public**” | Last word swallowed. Both passes hear “Pamdi”. |
| 14 | 3:47.00–3:47.60 | High | “passing the **Undi18** law” | Both passes hear **“Undi-80”**: “eighteen” lands like “eighty”. Factual risk for anyone who isn't reading the subtitles. |
| 15 | 4:09.24–4:09.95 | Medium | “at **Taylor's** University” | Both passes hear “the U.S. University”. |
| 16 | 4:10.90–4:12.70 | High | “As an **ISTJ** and an **Owl**” | Slurred, with an extra ~0.9 s on “ISTJ”. Passes hear “As I teach and I will” / “an SITJ and outward”. |
| 17 | 4:27.70–4:29.20 | High | “chase **titles. Let's focus** on…” | The two sentences run together with no pause. Both passes hear “chase scientists that's focused”. |
| 18 | 4:31.40–4:32.75 | High | “building the **real skills to lead**” | Rushed final line. Both passes hear “the rarest case to late”. |

## Step 2: Graphics (89 elements covering all 38 storyboard frames)

Layout: **Left zone** x 72–760, **Right zone** x 1168–1848, **Top bar** y 18–112. All storyboard “LT” items were moved into the left/right zones; nothing sits in the bottom of the frame. Every graphic is timed to the words as actually spoken (word-level timestamps), not the storyboard's estimates. Style follows your Instagram reference: frosted white rounded cards, soft shadow, mono micro-labels, segmented progress bar and chapter pill top-left. Key words get **gold** pills, problems are **red**, and crossed-out ideas get an animated red strike. Motion: 0.3 s slide-ins from the sides and 0.3 s pop-ins, both with a small overshoot, and a 0.22 s exit before the next sentence.

| SB frame | Start | End | Zone | Graphic | Content |
|---|---|---|---|---|---|
| all | 0:00.90 | 4:35.73 | Top bar | Top bar: chapter pill + progress |  |
| 2 | 0:10.58 | 0:12.02 | C | Let's get started | Let's get started |
| 3 | 0:14.32 | 0:17.95 | C | Have you ever planned… | Have you ever planned your life so carefully ? |
| 3 | 0:14.74 | 0:22.13 | Right | My life plan (icons; cracks & falls) |  |
| 4 | 0:18.20 | 0:22.08 | C | Big idea | True leadership begins the moment your plan falls apart |
| 5 | 0:25.72 | 0:29.20 | Right | Zodiac wheel (lands on Capricorn) |  |
| 5 | 0:27.00 | 0:33.45 | C | Creativity + detail | I love blending creativity + detail |
| 15 | 0:27.60 | 0:33.45 | Left | icon creativity |  |
| 15 | 0:28.54 | 0:33.45 | Left | icon detail |  |
| 15 | 0:29.62 | 0:33.45 | Left | icon multimedia |  |
| 15 | 0:30.70 | 0:33.45 | Left | icon digital marketing |  |
| 15 | 0:31.86 | 0:33.45 | Left | icon IT |  |
| 15 | 0:32.46 | 0:33.45 | Left | icon journalism |  |
| 6 | 0:34.22 | 0:39.66 | Left | Me with my mum (teacher) |  |
| 6 | 0:34.67 | 0:39.66 | Left | 'This is my mum' arrow |  |
| 6 | 0:36.90 | 0:39.66 | Behind | EDUCATION (behind me) |  |
| 6 | 0:37.60 | 0:39.66 | Behind | DISCIPLINE (behind me) |  |
| 7 | 0:40.44 | 0:47.24 | Left | Personality test 1 | Personality test 1 · 16Personalities · Myers-Briggs Type Indicator (MBTI) · ISTJ |
| 7 | 0:41.82 | 0:47.24 | Right | Personality test 2 | Personality test 2 · DOPE Personality Test · OWL |
| 7 | 0:45.42 | 0:47.26 | C | Mirror | …like looking in the mirror |
| 8 | 0:47.36 | 0:51.22 | C | Logic → plan → goals | I thrive on logic → a solid plan → my goals |
| 9 | 0:52.18 | 1:03.38 | Left | Diploma · UniKL | UniKL MIIT · Diploma in Multimedia |
| 9 | 0:55.64 | 1:03.38 | Right | Merdeka 118 (PNB) |  |
| 9 | 0:55.99 | 1:03.38 | Right | Almost 1 year |  |
| 10 | 1:04.24 | 1:11.36 | Left | UKM · Liberal Studies | Year 1 · Liberal Studies |
| 10 | 1:07.20 | 1:11.36 | Right | Lanyard ID badge: Head of Media Exco |  |
| 11 | 1:12.38 | 1:15.10 | C | Perfectionism = problem | My corporate perfectionism became a problem |
| 11 | 1:15.18 | 1:19.60 | C | Anxious, control every design | Anxious delegating tasks, wanting to control every single design |
| 12 | 1:19.67 | 1:24.04 | C | Micromanaging = burning out | Micromanaging was burning me out |
| 12 | 1:24.06 | 1:27.08 | Right | Controlling to empowering | I shifted from · Controlling · → Empowering |
| 13 | 1:27.15 | 1:32.18 | Left | The fix | The fix · Clear creative brief · Easy templates · Full team ownership |
| 14 | 1:34.06 | 1:38.94 | Right | Instagram 3x3 feed (phone) |  |
| 14 | 1:34.68 | 1:38.94 | Right | Launched on time stamp | ✓ LAUNCHED ON TIME |
| 14 | 1:35.90 | 1:38.94 | C | Team did amazing work | My team did amazing work on their own |
| 15 | 1:40.80 | 1:43.32 | C | Leadership isn't doing everything | True leadership isn't doing everything yourself |
| 15 | 1:43.42 | 1:47.34 | C | Clear systems + trust | It is building clear systems and trusting your team |
| 16 | 1:48.86 | 1:50.44 | C | Real leadership under pressure | Real leadership under pressure |
| 16 | 1:51.96 | 2:04.34 | Right | Syed Saddiq |  |
| 16 | 1:51.96 | 1:55.64 | C | My idol | My idol |
| 17 | 1:55.76 | 2:04.34 | Left | Not a nepo baby | Like me · Nepo baby · NOT A NEPO BABY |
| 17 | 1:58.86 | 2:04.34 | Left | His mother a teacher | His mother is a teacher too |
| 17 | 2:01.60 | 2:04.34 | C | Success must be earned | Success must be earned through hard work |
| 18 | 2:05.40 | 2:11.56 | C | Corporate Athlete | A true Corporate Athlete |
| 18 | 2:06.80 | 2:11.56 | Right | Corporate-athlete pillars 2x2 |  |
| 18 | 2:10.84 | 4:22.34 | Top bar | Top bar: pillar tracker |  |
| 19 | 2:11.68 | 2:14.20 | Behind | MIND (behind me) |  |
| 19 | 2:14.78 | 2:19.16 | Right | Asian Debating Champion |  |
| 20 | 2:19.66 | 2:25.82 | Left | My goal at UKM | My goal at UKM · Well-rounded student · Lead outside class · Keep strong grades |
| 19 | 2:21.28 | 2:19.16 | Left | UIA logo | International Islamic University Malaysia · Super sharp debater |
| 21 | 2:25.94 | 2:32.04 | C | Sacrifice | Mental strength = sacrifice |
| 21 | 2:29.06 | 2:32.04 | Right | Oxford |  |
| 21 | 2:29.91 | 2:32.04 | Left | Declined x2 | DECLINED ×2 · TO SERVE MALAYSIA |
| 22 | 2:35.02 | 2:38.16 | C | I'd take it in a heartbeat | If I got into Oxford, I'd take it in a heartbeat |
| 22 | 2:35.02 | 2:38.16 | Right | Heartbeat | In a heartbeat |
| 23 | 2:38.28 | 2:54.88 | Right | Logical path | The logical path · Study hard at Oxford · Back to Malaysia · Top management · = THE LOGICAL PATH |
| 23 | 2:46.54 | 2:54.88 | Left | You get | You get · Physical & mental comfort · Huge bonuses · Way more money |
| 24 | 2:55.00 | 2:56.52 | C | Headache | Why give yourself a headache ? |
| 24 | 2:57.44 | 3:00.36 | C | Zero personal profit | …for zero personal profit |
| 25 | 3:02.18 | 3:07.82 | Left | Selfish vs selfless | Imagine if he chose · Selfish · → Selfless |
| 25 | 3:05.04 | 3:07.82 | C | People of Muar | What would have happened to the people of Muar ? |
| 26 | 3:07.94 | 3:10.40 | Behind | BODY (behind me) |  |
| 26 | 3:08.76 | 3:10.86 | Right | Iron-man fit |  |
| 26 | 3:10.71 | 3:21.12 | Right | Langkah Muar |  |
| 26 | 3:13.10 | 3:21.12 | Left | 200 km route | Muar → Parliament, under the hot sun |
| 26 | 3:17.68 | 3:21.12 | Left | RM160,000 raised | Raised for his people |
| 27 | 3:21.24 | 3:27.12 | C | Image → PrimaValet → funding | He used his image smartly by modelling for PrimaValet to fund his political work |
| 28 | 3:27.24 | 3:31.64 | Behind | EMOTIONS (behind me) |  |
| 28 | 3:29.22 | 3:31.64 | Right | Minister at 26 | Minister at |
| 29 | 3:32.76 | 3:38.98 | Right | Syed Saddiq with Tun Dr. Mahathir |  |
| 29 | 3:33.36 | 3:38.98 | Left | Tun Dr. Mahathir portrait |  |
| 29 | 3:36.14 | 3:38.98 | C | Change while honouring veterans | Push for change while honouring veterans |
| 30 | 3:39.05 | 3:45.04 | Right | Sheraton Move press conference |  |
| 30 | 3:41.22 | 3:45.04 | Left | Court trials | Years of court trials |
| 30 | 3:43.54 | 3:45.04 | C | Calm in public | He stayed calm in public |
| 31 | 3:45.16 | 3:47.20 | Behind | VALUES (behind me) |  |
| 31 | 3:46.46 | 3:54.44 | Right | Undi18 |  |
| 31 | 3:49.46 | 3:54.44 | Left | 50% voting power | Young people now hold · of the voting power |
| 32 | 3:56.34 | 4:10.78 | Right | Wedding: Syed Saddiq & Bella Astillah |  |
| 32 | 4:00.34 | 4:01.72 | Left | Broke old traditions | BROKE OLD TRADITIONS |
| 33 | 4:01.84 | 4:10.78 | Left | Hantaran | His hantaran · Luxury bags · Master's degree · Taylor's |
| 34 | 4:10.65 | 4:16.24 | Left | ISTJ practical | As an · ISTJ |
| 34 | 4:12.04 | 4:16.24 | Right | Owl forward-thinking | And an · OWL |
| 35 | 4:17.66 | 4:22.34 | C | Balance | True leadership = balance |
| 35 | 4:18.82 | 4:22.34 | Right | Balance pillars | Mind · Body · Emotions · Values |
| 36 | 4:22.46 | 4:26.64 | Left | My own path @ UKM | My path · Building my own path |
| 36 | 4:24.62 | 4:26.64 | Right | Role model (Syed Saddiq) |  |
| 37 | 4:26.76 | 4:28.95 | C | Not just titles | Let's not just chase titles  |
| 37 | 4:29.00 | 4:33.02 | C | Grow + real skills | Grow in our 20s and build the real skills to lead |
| 38 | 4:33.14 | 4:35.73 | Left | Thank you | Thank you · Nur Anis Nasuha · Liberal Studies · UKM |

### Photos used (no credits on screen, as you asked)

| Photo | Source |
|---|---|
| Me with my mum | You (Drive) |
| Syed Saddiq debate / UIA 2015 | You |
| UIA, UniKL, UKM logos | You |
| Wedding: Syed Saddiq & Bella Astillah | You |
| Sheraton Move | You |
| Undi18 | You |
| Syed Saddiq with Tun Dr Mahathir | You |
| Langkah Muar (headline cropped out) | You |
| Syed Saddiq iron-man | You |
| Syed Saddiq portrait | Wikimedia Commons, US Embassy KL, public domain |
| Tun Dr Mahathir portrait | Wikimedia Commons, kremlin.ru, CC BY 4.0 |
| Radcliffe Camera, Oxford | Wikimedia Commons, Julian Herzog, CC BY 4.0 |
| Merdeka 118 | Wikimedia Commons, Ahmad Ali Karim, CC0 |

**Put these credits in your post caption or description** (the free licences ask for it): Tun Dr Mahathir photo: kremlin.ru, CC BY 4.0. Oxford photo: Julian Herzog, CC BY 4.0. Syed Saddiq portrait: US Embassy Kuala Lumpur, public domain. Merdeka 118: Ahmad Ali Karim, CC0. All via Wikimedia Commons. The photos you supplied are news/official images: fine for a class assignment, but they're copyrighted if you post publicly.

## Step 4: Sound effects (260 placed, all synthesised from scratch)

Kinds: soft **whoosh** (slide-ins, strikes, chapter changes), **pop** (cards, chips, tiles), **tick** (check marks), **thump** (stamps such as GRADED, NOT A NEPO BABY, DECLINED ×2, = 0, BROKE OLD TRADITIONS, and the PLAN crack), and **count** ticks during number count-ups. Every effect is capped at −24 dBFS and at least 16 dB under your voice's local peak; the loudest effect is −25 dBFS against voice peaks of about −2 dBFS. 9 cues were dropped where they fell within 70 ms of the same kind.

| Time | Kind | Level (dBFS) | Trigger |
|---|---|---|---|
| 0:00.02 | whoosh | -29.0 | opening keyframe zoom-out |
| 0:00.84 | pop | -30.1 | zoom lands |
| 0:10.58 | whoosh | -35.0 | kinetic: Let's get started |
| 0:11.00 | pop | -30.1 | kinetic gold word |
| 0:14.32 | whoosh | -35.0 | kinetic: Have you ever planned… |
| 0:14.74 | whoosh | -30.9 | in: My life plan |
| 0:15.04 | pop | -27.9 | My life plan row |
| 0:15.42 | pop | -27.9 | My life plan row |
| 0:15.70 | pop | -30.1 | kinetic gold word |
| 0:15.96 | pop | -30.1 | kinetic gold word |
| 0:18.20 | whoosh | -35.0 | kinetic: Big idea |
| 0:18.20 | pop | -30.1 | kinetic gold word |
| 0:18.56 | pop | -30.1 | kinetic gold word |
| 0:20.78 | pop | -30.1 | kinetic gold word |
| 0:21.30 | pop | -30.1 | kinetic gold word |
| 0:21.30 | thump | -25.0 | PLAN cracks |
| 0:21.65 | whoosh | -33.4 | PLAN falls |
| 0:21.84 | pop | -30.1 | kinetic gold word |
| 0:25.72 | pop | -28.9 | zodiac wheel in |
| 0:25.82 | whoosh | -33.4 | zodiac spin |
| 0:27.00 | whoosh | -35.0 | kinetic: Creativity + detail |
| 0:27.17 | tick | -28.9 | lands on Capricorn |
| 0:27.60 | pop | -30.1 | kinetic gold word |
| 0:28.54 | pop | -30.1 | kinetic gold word |
| 0:29.62 | pop | -28.4 | icon: MULTIMEDIA |
| 0:30.70 | pop | -28.4 | icon: DIGITAL MARKETING |
| 0:31.86 | pop | -28.4 | icon: IT |
| 0:32.46 | pop | -28.4 | icon: JOURNALISM |
| 0:33.60 | whoosh | -35.9 | chapter change |
| 0:34.22 | pop | -28.9 | photo: Me with my mum (teacher) |
| 0:34.67 | whoosh | -37.0 | annotation: This is my mum! |
| 0:36.90 | thump | -27.5 | behind-word: EDUCATION |
| 0:37.60 | thump | -27.5 | behind-word: DISCIPLINE |
| 0:40.44 | whoosh | -30.9 | in: Personality test 1 |
| 0:41.82 | whoosh | -30.9 | in: Personality test 2 |
| 0:43.18 | pop | -27.9 | Personality test 1 row |
| 0:44.26 | pop | -27.9 | Personality test 2 row |
| 0:45.42 | whoosh | -35.0 | kinetic: Mirror |
| 0:46.60 | pop | -30.1 | kinetic gold word |
| 0:47.36 | whoosh | -35.0 | kinetic: Logic → plan → goals |
| 0:47.88 | pop | -30.1 | kinetic gold word |
| 0:49.52 | pop | -30.1 | kinetic gold word |
| 0:50.52 | pop | -30.1 | kinetic gold word |
| 0:52.18 | whoosh | -30.9 | in: Diploma · UniKL |
| 0:55.64 | whoosh | -30.9 | photo: Merdeka 118 (PNB) |
| 0:55.99 | pop | -28.9 | in: Almost 1 year |
| 1:02.18 | pop | -28.9 | chip: DETAIL-ORIENTED |
| 1:04.24 | whoosh | -30.9 | in: UKM · Liberal Studies |
| 1:07.20 | whoosh | -30.9 | lanyard drops in |
| 1:07.62 | thump | -29.4 | lanyard lands |
| 1:12.38 | whoosh | -35.0 | kinetic: Perfectionism = problem |
| 1:12.64 | pop | -30.1 | kinetic gold word |
| 1:15.18 | whoosh | -35.0 | kinetic: Anxious, control every design |
| 1:19.67 | whoosh | -35.0 | kinetic: Micromanaging = burning out |
| 1:24.06 | whoosh | -30.9 | in: Controlling to empowering |
| 1:25.16 | whoosh | -34.2 | strike-through: Controlling |
| 1:27.15 | whoosh | -30.9 | in: The fix |
| 1:27.80 | pop | -27.9 | The fix row |
| 1:29.50 | pop | -27.9 | The fix row |
| 1:30.98 | pop | -27.9 | The fix row |
| 1:34.06 | whoosh | -32.1 | phone slide-in |
| 1:34.14 | pop | -36.1 | feed tile |
| 1:34.26 | pop | -36.1 | feed tile |
| 1:34.38 | pop | -36.1 | feed tile |
| 1:34.50 | pop | -36.1 | feed tile |
| 1:34.62 | pop | -36.1 | feed tile |
| 1:34.78 | thump | -25.9 | Launched on time stamp row |
| 1:35.90 | whoosh | -35.0 | kinetic: Team did amazing work |
| 1:36.78 | pop | -30.1 | kinetic gold word |
| 1:37.36 | pop | -30.1 | kinetic gold word |
| 1:40.80 | whoosh | -35.0 | kinetic: Leadership isn't doing everything |
| 1:43.42 | whoosh | -35.0 | kinetic: Clear systems + trust |
| 1:44.84 | pop | -30.1 | kinetic gold word |
| 1:45.76 | pop | -30.1 | kinetic gold word |
| 1:47.46 | whoosh | -35.9 | chapter change |
| 1:48.86 | whoosh | -35.0 | kinetic: Real leadership under pressure |
| 1:50.08 | pop | -30.1 | kinetic gold word |
| 1:51.96 | pop | -28.9 | photo: Syed Saddiq |
| 1:51.96 | whoosh | -35.0 | kinetic: My idol |
| 1:52.20 | pop | -30.1 | kinetic gold word |
| 1:55.76 | whoosh | -30.9 | in: Not a nepo baby |
| 1:57.40 | whoosh | -34.2 | strike-through: Nepo baby |
| 1:57.65 | thump | -25.9 | Not a nepo baby row |
| 1:58.86 | whoosh | -30.9 | in: His mother a teacher |
| 2:01.60 | whoosh | -35.0 | kinetic: Success must be earned |
| 2:02.94 | pop | -30.1 | kinetic gold word |
| 2:03.64 | pop | -30.1 | kinetic gold word |
| 2:03.88 | pop | -30.1 | kinetic gold word |
| 2:05.40 | whoosh | -35.0 | kinetic: Corporate Athlete |
| 2:05.76 | pop | -30.1 | kinetic gold word |
| 2:06.08 | pop | -30.1 | kinetic gold word |
| 2:07.54 | pop | -28.4 | pillar MIND |
| 2:08.26 | pop | -28.4 | pillar BODY |
| 2:08.88 | pop | -28.4 | pillar EMOTIONS |
| 2:10.84 | pop | -31.4 | pillar tracker appears |
| 2:11.68 | thump | -27.5 | behind-word: MIND |
| 2:14.78 | whoosh | -30.9 | photo: Asian Debating Champion |
| 2:19.66 | whoosh | -30.9 | in: My goal at UKM |
| 2:21.28 | whoosh | -30.9 | in: UIA logo |
| 2:22.40 | pop | -27.9 | My goal at UKM row |
| 2:24.56 | pop | -27.9 | My goal at UKM row |
| 2:25.94 | whoosh | -35.0 | kinetic: Sacrifice |
| 2:27.36 | pop | -30.1 | kinetic gold word |
| 2:29.06 | whoosh | -30.9 | photo: Oxford |
| 2:29.91 | pop | -28.9 | in: Declined x2 |
| 2:29.96 | thump | -25.9 | Declined x2 row |
| 2:30.94 | pop | -27.9 | Declined x2 row |
| 2:35.02 | whoosh | -35.0 | kinetic: I'd take it in a heartbeat |
| 2:37.58 | pop | -30.1 | kinetic gold word |
| 2:38.28 | whoosh | -30.9 | in: Logical path |
| 2:38.66 | pop | -27.9 | Logical path row |
| 2:39.86 | pop | -27.9 | Logical path row |
| 2:41.20 | pop | -27.9 | Logical path row |
| 2:45.34 | pop | -27.9 | Logical path row |
| 2:46.54 | whoosh | -30.9 | in: You get |
| 2:48.46 | tick | -28.9 | You get row |
| 2:49.54 | tick | -28.9 | You get row |
| 2:50.84 | tick | -28.9 | You get row |
| 2:55.00 | whoosh | -35.0 | kinetic: Headache |
| 2:56.38 | pop | -30.1 | kinetic gold word |
| 2:57.44 | whoosh | -35.0 | kinetic: Zero personal profit |
| 3:02.18 | whoosh | -30.9 | in: Selfish vs selfless |
| 3:04.10 | whoosh | -34.2 | strike-through: Selfish |
| 3:05.04 | whoosh | -35.0 | kinetic: People of Muar |
| 3:07.02 | pop | -30.1 | kinetic gold word |
| 3:07.94 | thump | -27.5 | behind-word: BODY |
| 3:08.76 | whoosh | -30.9 | photo: Iron-man fit |
| 3:10.71 | pop | -28.9 | photo: Langkah Muar |
| 3:13.10 | pop | -28.9 | in: 200 km route |
| 3:13.20 | count | -38.2 | counter 200 KM |
| 3:13.28 | count | -38.2 | counter 200 KM |
| 3:13.35 | count | -38.2 | counter 200 KM |
| 3:13.43 | count | -38.2 | counter 200 KM |
| 3:13.50 | count | -38.2 | counter 200 KM |
| 3:13.58 | count | -38.2 | counter 200 KM |
| 3:13.66 | count | -38.2 | counter 200 KM |
| 3:13.73 | count | -38.2 | counter 200 KM |
| 3:13.81 | count | -38.2 | counter 200 KM |
| 3:13.89 | count | -38.2 | counter 200 KM |
| 3:13.96 | count | -38.2 | counter 200 KM |
| 3:14.04 | count | -38.2 | counter 200 KM |
| 3:14.12 | count | -38.2 | counter 200 KM |
| 3:14.19 | count | -38.2 | counter 200 KM |
| 3:14.27 | count | -38.2 | counter 200 KM |
| 3:14.34 | count | -38.2 | counter 200 KM |
| 3:14.42 | count | -38.2 | counter 200 KM |
| 3:14.50 | count | -38.2 | counter 200 KM |
| 3:14.57 | count | -38.2 | counter 200 KM |
| 3:14.65 | count | -38.2 | counter 200 KM |
| 3:14.72 | count | -38.2 | counter 200 KM |
| 3:14.80 | count | -38.2 | counter 200 KM |
| 3:14.88 | count | -38.2 | counter 200 KM |
| 3:14.95 | count | -38.2 | counter 200 KM |
| 3:15.03 | count | -38.2 | counter 200 KM |
| 3:15.10 | count | -38.2 | counter 200 KM |
| 3:15.18 | count | -38.2 | counter 200 KM |
| 3:15.26 | count | -38.2 | counter 200 KM |
| 3:15.33 | count | -38.2 | counter 200 KM |
| 3:15.41 | count | -38.2 | counter 200 KM |
| 3:15.49 | count | -38.2 | counter 200 KM |
| 3:15.56 | count | -38.2 | counter 200 KM |
| 3:15.64 | count | -38.2 | counter 200 KM |
| 3:15.72 | count | -38.2 | counter 200 KM |
| 3:15.79 | count | -38.2 | counter 200 KM |
| 3:15.87 | count | -38.2 | counter 200 KM |
| 3:15.94 | count | -38.2 | counter 200 KM |
| 3:16.02 | count | -33.9 | counter 200 KM |
| 3:17.68 | whoosh | -30.9 | in: RM160,000 raised |
| 3:18.38 | count | -38.2 | counter RM160,000+ |
| 3:18.46 | count | -38.2 | counter RM160,000+ |
| 3:18.54 | count | -38.2 | counter RM160,000+ |
| 3:18.62 | count | -38.2 | counter RM160,000+ |
| 3:18.69 | count | -38.2 | counter RM160,000+ |
| 3:18.77 | count | -38.2 | counter RM160,000+ |
| 3:18.85 | count | -38.2 | counter RM160,000+ |
| 3:18.93 | count | -38.2 | counter RM160,000+ |
| 3:19.01 | count | -38.2 | counter RM160,000+ |
| 3:19.09 | count | -38.2 | counter RM160,000+ |
| 3:19.17 | count | -38.2 | counter RM160,000+ |
| 3:19.24 | count | -38.2 | counter RM160,000+ |
| 3:19.32 | count | -38.2 | counter RM160,000+ |
| 3:19.40 | count | -38.2 | counter RM160,000+ |
| 3:19.48 | count | -33.9 | counter RM160,000+ |
| 3:21.24 | whoosh | -35.0 | kinetic: Image → PrimaValet → funding |
| 3:22.28 | pop | -30.1 | kinetic gold word |
| 3:25.06 | pop | -30.1 | kinetic gold word |
| 3:27.24 | thump | -27.5 | behind-word: EMOTIONS |
| 3:29.22 | whoosh | -30.9 | in: Minister at 26 |
| 3:30.22 | count | -38.2 | counter 26 |
| 3:30.30 | count | -38.2 | counter 26 |
| 3:30.39 | count | -38.2 | counter 26 |
| 3:30.47 | count | -38.2 | counter 26 |
| 3:30.55 | count | -38.2 | counter 26 |
| 3:30.64 | count | -38.2 | counter 26 |
| 3:30.72 | count | -33.9 | counter 26 |
| 3:32.76 | whoosh | -30.9 | photo: Syed Saddiq with Tun Dr. Mahathir |
| 3:33.36 | pop | -28.9 | photo: Tun Dr. Mahathir portrait |
| 3:36.14 | whoosh | -35.0 | kinetic: Change while honouring veterans |
| 3:36.86 | pop | -30.1 | kinetic gold word |
| 3:38.18 | pop | -30.1 | kinetic gold word |
| 3:39.05 | whoosh | -30.9 | photo: Sheraton Move press conference |
| 3:41.22 | pop | -28.9 | in: Court trials |
| 3:43.54 | whoosh | -35.0 | kinetic: Calm in public |
| 3:43.82 | pop | -30.1 | kinetic gold word |
| 3:45.16 | thump | -27.5 | behind-word: VALUES |
| 3:45.92 | pop | -28.4 | pillar VALUES |
| 3:46.46 | whoosh | -30.9 | photo: Undi18 |
| 3:49.46 | whoosh | -30.9 | in: 50% voting power |
| 3:50.60 | count | -38.2 | counter 50%+ |
| 3:50.68 | count | -38.2 | counter 50%+ |
| 3:50.76 | count | -38.2 | counter 50%+ |
| 3:50.84 | count | -38.2 | counter 50%+ |
| 3:50.92 | count | -38.2 | counter 50%+ |
| 3:51.00 | count | -38.2 | counter 50%+ |
| 3:51.08 | count | -38.2 | counter 50%+ |
| 3:51.16 | count | -38.2 | counter 50%+ |
| 3:51.24 | count | -38.2 | counter 50%+ |
| 3:51.32 | count | -38.2 | counter 50%+ |
| 3:51.40 | count | -33.9 | counter 50%+ |
| 3:56.34 | whoosh | -30.9 | photo: Wedding: Syed Saddiq & Bella Astillah |
| 4:00.34 | pop | -28.9 | in: Broke old traditions |
| 4:00.39 | thump | -25.9 | Broke old traditions row |
| 4:01.84 | whoosh | -30.9 | in: Hantaran |
| 4:02.79 | whoosh | -34.2 | strike-through: Luxury bags |
| 4:04.03 | tick | -28.9 | Hantaran row |
| 4:04.08 | count | -38.2 | counter RM100,000 EPF |
| 4:04.16 | count | -38.2 | counter RM100,000 EPF |
| 4:04.23 | count | -38.2 | counter RM100,000 EPF |
| 4:04.31 | count | -38.2 | counter RM100,000 EPF |
| 4:04.38 | count | -38.2 | counter RM100,000 EPF |
| 4:04.46 | count | -38.2 | counter RM100,000 EPF |
| 4:04.53 | count | -38.2 | counter RM100,000 EPF |
| 4:04.60 | count | -38.2 | counter RM100,000 EPF |
| 4:04.68 | count | -38.2 | counter RM100,000 EPF |
| 4:04.75 | count | -38.2 | counter RM100,000 EPF |
| 4:04.83 | count | -38.2 | counter RM100,000 EPF |
| 4:04.91 | count | -38.2 | counter RM100,000 EPF |
| 4:04.98 | count | -33.9 | counter RM100,000 EPF |
| 4:08.24 | pop | -27.9 | Hantaran row |
| 4:10.65 | whoosh | -30.9 | in: ISTJ practical |
| 4:10.90 | whoosh | -35.9 | chapter change |
| 4:11.03 | pop | -27.9 | ISTJ practical row |
| 4:12.04 | whoosh | -30.9 | in: Owl forward-thinking |
| 4:12.38 | pop | -27.9 | Owl forward-thinking row |
| 4:17.66 | whoosh | -35.0 | kinetic: Balance |
| 4:18.82 | pop | -30.1 | kinetic gold word |
| 4:18.82 | whoosh | -30.9 | in: Balance pillars |
| 4:19.54 | tick | -29.9 | balance MIND |
| 4:20.20 | tick | -29.9 | balance BODY |
| 4:20.94 | tick | -29.9 | balance EMOTIONS |
| 4:21.62 | tick | -29.9 | balance VALUES |
| 4:22.46 | whoosh | -30.9 | in: My own path @ UKM |
| 4:24.62 | pop | -28.9 | photo: Role model (Syed Saddiq) |
| 4:26.76 | whoosh | -35.0 | kinetic: Not just titles |
| 4:29.00 | whoosh | -35.0 | kinetic: Grow + real skills |
| 4:30.44 | pop | -30.1 | kinetic gold word |
| 4:31.84 | pop | -30.1 | kinetic gold word |
| 4:31.98 | pop | -30.1 | kinetic gold word |
| 4:33.14 | pop | -28.9 | in: Thank you |
| 4:34.40 | whoosh | -33.4 | closing keyframe push-in |

## References (revision 1)

- Instagram reel (latest reference): **opened and studied**. I matched its look (white rounded UI cards, mono step pill with segmented progress bar, accent-highlighted words, numbered icon tiles) using your gold accent. None of its music or audio was used.
- Threads link: the post page opened (a text tips post), but its video could **not** be downloaded, so I used the fallback brief there: kinetic text, 0.3 s pop/slide with overshoot, flat icons, rounded cards, gold keywords.
