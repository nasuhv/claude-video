# Change log: “Leadership Begins When the Plan Falls Apart”

Source: `raw.mov` (HEVC 10-bit, 1920×1080, 30 fps, 8272 frames, 4:35.73). Output: `final.mp4` (H.264 High, 8-bit 4:2:0, BT.709, CRF 16, AAC 256 kb/s 44.1 kHz). Resolution, frame rate, frame count and length are identical to the source.

## The three rules: how they were enforced and checked

1. **No cuts or retiming.** The picture passes through untouched underneath the overlay: no cuts, trims, speed changes, freezes, zooms or crops. Audio filters are all sample-for-sample. One filter added a fixed 25 ms (1102-sample) latency, which was removed exactly. Cross-correlation against the original shows **0-sample offset** at 5, 60, 120, 180, 240 and 265 s.
2. **Subtitles untouched.** The burned-in bilingual subtitles sit at y≈875–985 for the whole video. Every graphic is kept above y=850, enforced per frame by a hard guard. No captions were added.
3. **Nothing on the face.** The face was tracked on all 8272 frames (MediaPipe face mesh), then padded (+30 % each side, +45 % above for the hijab and forehead, +25 % below). The renderer checked **every frame** (stricter than every 0.5 s) for any graphic pixel inside that box: **0 violations**. The exported MP4 was then compared with the original **every 0.5 s** (552 checks):

```
checks 552 (every 0.5 s)
face zone: worst 99.9th-pct diff 15.0, worst mean diff 3.62  (0-255 scale)
subtitle band: worst 99.9th-pct diff 17.0, worst mean diff 3.80
worst face samples [(10.5, 15.0), (11.0, 15.0), (38.5, 15.0)]
original 1920x1080 30/1 frames 8272 video dur 275.733333 audio dur 275.713741 44100 container 275.733333
final 1920x1080 30/1 frames 8272 video dur 275.733333 audio dur 275.712993 44100 container 275.733333
audio offset vs original (samples) at 5/60/120/180/240/265 s: [0, 0, 0, 0, 0, 0]
```

A graphic in those zones would show differences of ~150–255. The ~3–4 mean and 15–17 peak are 10-bit→8-bit re-encode noise only.

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

## Step 2: Graphics (76 elements covering all 38 storyboard frames)

Layout: **Left zone** x 72–760, **Right zone** x 1168–1848, **Top bar** y 18–112. All storyboard “LT” items were moved into the left/right zones; nothing sits in the bottom of the frame. Every graphic is timed to the words as actually spoken (word-level timestamps), not the storyboard's estimates. Style follows your Instagram reference: frosted white rounded cards, soft shadow, mono micro-labels, segmented progress bar and chapter pill top-left. Key words get **gold** pills, problems are **red**, and crossed-out ideas get an animated red strike. Motion: 0.3 s slide-ins from the sides and 0.3 s pop-ins, both with a small overshoot, and a 0.22 s exit before the next sentence.

| SB frame | Start | End | Zone | Graphic | Content |
|---|---|---|---|---|---|
| all | 0:00.40 | 4:35.73 | Top bar | Top bar: chapter pill + progress |  |
| 1 | 0:01.44 | 0:03.64 | Left | Greeting | Salam · 3 languages · Assalamu'alaikum |
| 1 | 0:03.74 | 0:08.67 | Top bar | S-LOG tag | ● S-LOG · UNGRADED |
| 1 | 0:04.56 | 0:10.46 | Right | Colour grade panel | Colour grade · ✓ GRADED |
| 2 | 0:10.58 | 0:12.00 | Left | Let's get started | Let's get started |
| 3 | 0:13.32 | 0:18.05 | Left | Question | Question for you · Have you ever planned your life so carefully? |
| 3 | 0:14.74 | 0:22.13 | Right | My life plan (cracks & falls) |  |
| 4 | 0:18.20 | 0:22.08 | Left | Big idea | The big idea · Leadership begins when the plan falls apart |
| 5 | 0:22.18 | 0:33.45 | Left | Name card | Hi, I'm · Nur Anis Nasuha binti Rosli · Liberal Studies · UKM |
| 5 | 0:25.82 | 0:33.45 | Right | Capricorn | Star sign · Capricorn |
| 5 | 0:27.30 | 0:33.45 | Right | Creativity + detail | I love blending · Creativity + detail |
| 6 | 0:34.32 | 0:39.63 | Left | Mum = teacher | Growing up · Mum = teacher |
| 6 | 0:36.90 | 0:39.63 | Right | Priorities | Top priorities |
| 7 | 0:40.54 | 0:47.24 | Left | 16Personalities | Test 1 · 16Personalities · → ISTJ · “Like looking in a mirror” |
| 7 | 0:41.92 | 0:47.24 | Right | DOPE test | Test 2 · DOPE · → OWL |
| 8 | 0:47.78 | 0:51.22 | Right | Logic-plan-goals | How I work · Logic · → Solid plan · → Goals |
| 9 | 0:52.28 | 1:03.38 | Left | Diploma | Diploma · Multimedia · UniKL MIIT |
| 9 | 0:55.74 | 1:03.38 | Right | PNB / ASNB | Work · almost 1 year · Marketing for ASNB · Permodalan Nasional Berhad (PNB) · DETAIL-ORIENTED |
| 10 | 1:04.34 | 1:11.36 | Left | UKM year 1 | UKM · Year 1 · Liberal Studies |
| 10 | 1:07.30 | 1:11.36 | Right | Head of Media Exco | Annual event · Kolej Keris Mas · Head of Media Exco |
| 11 | 1:12.38 | 1:19.60 | Left | Perfectionism = problem | At first · Corporate perfectionism = problem |
| 11 | 1:15.18 | 1:19.60 | Right | Control every design | Anxious delegating tasks · Control every design |
| 12 | 1:19.72 | 1:27.08 | Left | Burning out | Micromanaging · = burning out · …and holding my team back |
| 12 | 1:24.06 | 1:27.08 | Right | Controlling to empowering | I shifted from · Controlling · → Empowering |
| 13 | 1:27.20 | 1:32.18 | Left | The fix | The fix · Clear creative brief · Easy templates · Full team ownership |
| 14 | 1:34.06 | 1:38.94 | Right | Instagram 3x3 feed (phone) |  |
| 14 | 1:34.68 | 1:38.94 | Right | Launched on time stamp | ✓ LAUNCHED ON TIME |
| 14 | 1:35.90 | 1:38.94 | Left | Team-owned work | Result · Team-owned work · Amazing work, on their own |
| 15 | 1:39.06 | 1:47.34 | Top bar | Lesson learned tag | LESSON LEARNED |
| 15 | 1:40.80 | 1:47.34 | Left | Leadership is not | True leadership · ≠ doing everything yourself |
| 15 | 1:44.06 | 1:47.34 | Right | Systems + trust | It is · Clear systems · + Trust your team |
| 16 | 1:48.86 | 1:55.64 | Left | Real leadership | Real leadership · Under pressure |
| 16 | 1:51.96 | 2:04.34 | Right | Syed Saddiq photo | My idol · Syed Saddiq |
| 17 | 1:55.76 | 2:04.34 | Left | Not a nepo baby | Like me · Nepo baby · NOT A NEPO BABY |
| 17 | 1:58.86 | 2:04.34 | Left | Mother a teacher | His mother · A teacher too · SUCCESS IS EARNED |
| 18 | 2:05.76 | 2:11.56 | Left | Corporate Athlete | To me, he is a true · Corporate Athlete · Trained to survive politics |
| 18 | 2:06.80 | 2:11.56 | Right | Corporate-athlete pillars 2x2 |  |
| 18 | 2:10.84 | 4:22.34 | Top bar | Top bar: pillar tracker |  |
| 19 | 2:11.68 | 2:19.16 | Left | Pillar MIND | Pillar 1 · Mind · Super sharp |
| 19 | 2:15.38 | 2:19.16 | Right | Debating champion | At UIA · Asian Debating Champion |
| 20 | 2:19.76 | 2:25.82 | Left | My goal at UKM | My goal at UKM · Well-rounded student · Lead outside class · Keep strong grades |
| 21 | 2:25.94 | 2:32.04 | Left | Sacrifice | Mental strength · = Sacrifice · TO SERVE MALAYSIA |
| 21 | 2:29.16 | 2:32.04 | Right | Oxford | Oxford scholarship · DECLINED ×2 |
| 22 | 2:32.16 | 2:38.16 | Left | I'd take it | Honestly… · If I got into Oxford, I'd take it in a heartbeat |
| 22 | 2:35.02 | 2:38.16 | Right | Heartbeat | In a heartbeat |
| 23 | 2:38.28 | 2:54.88 | Right | Logical path | The logical path · Oxford · → Back to Malaysia · → Top management · GLC / MNC · = THE LOGICAL PATH |
| 23 | 2:46.54 | 2:54.88 | Left | You get | You get · Physical & mental comfort · Huge bonuses · Way more money · …what most brilliant students choose |
| 24 | 2:55.00 | 3:00.36 | Left | Headache | So why… · Give yourself a headache? |
| 24 | 2:56.62 | 3:00.36 | Right | Personal profit = 0 | Personal profit · = 0 |
| 25 | 3:02.18 | 3:07.82 | Left | Selfish vs selfless | Imagine if he chose · Selfish · → Selfless |
| 25 | 3:05.04 | 3:07.82 | Right | People of Muar | The people of Muar · What would have happened? |
| 26 | 3:07.94 | 3:21.12 | Left | Pillar BODY | Pillar 2 · Body · Incredible stamina |
| 26 | 3:10.78 | 3:21.12 | Right | Langkah Muar route | Langkah Muar · 2024 |
| 26 | 3:17.68 | 3:21.12 | Left | RM160,000 raised | Raised for his people |
| 27 | 3:21.24 | 3:27.12 | Left | Image to funding | Smart move · His image · → Modelling for PrimaValet · → Funds political work |
| 27 | 3:23.62 | 3:27.12 | Right | PrimaValet placeholder | PrimaValet campaign |
| 28 | 3:27.24 | 3:31.64 | Left | Pillar EMOTIONS | Pillar 3 · Emotions · Strength that stands out |
| 28 | 3:29.32 | 3:31.64 | Right | Minister at 26 | Minister at |
| 29 | 3:32.86 | 3:38.98 | Right | Mahathir | His idol · Tun Dr. Mahathir |
| 29 | 3:34.98 | 3:38.98 | Left | Change + respect | Young leaders can · Push for change · + Honour veterans |
| 30 | 3:39.10 | 3:45.04 | Left | Sheraton Move | 2020 · Sheraton Move · + years of court trials |
| 30 | 3:43.58 | 3:45.04 | Right | Calm in public | Stayed calm in public |
| 31 | 3:45.16 | 3:54.44 | Left | Pillar VALUES | Pillar 4 · Values |
| 31 | 3:46.46 | 3:54.44 | Right | Undi18 | Undi18 · 2019 · Voting age lowered to 18 · of the voting power |
| 32 | 3:56.44 | 4:01.72 | Left | 10 Oct 2026 | Personal level · Married Bella Astillah · 10 October 2026 |
| 32 | 4:00.34 | 4:01.72 | Right | Broke old traditions | BROKE OLD TRADITIONS |
| 33 | 4:01.84 | 4:10.78 | Right | Hantaran | His hantaran · Luxury bags · Master's degree · Taylor's |
| 34 | 4:10.90 | 4:16.24 | Left | ISTJ practical | As an · ISTJ ✓ · → Practical |
| 34 | 4:12.48 | 4:16.24 | Right | Owl forward-thinking | And an · Owl ✓ · → Forward-thinking |
| 35 | 4:16.36 | 4:22.34 | Left | Balance | True leadership · = Balance |
| 35 | 4:18.82 | 4:22.34 | Right | Balance pillars | Mind · Body · Emotions · Values |
| 36 | 4:22.46 | 4:26.64 | Left | My own path | My path · Building my own path @ UKM |
| 36 | 4:24.92 | 4:26.64 | Right | Role model | Role model |
| 37 | 4:26.76 | 4:33.02 | Left | Not just titles | Let's not just · Chase titles · Grow in our 20s |
| 37 | 4:31.42 | 4:33.02 | Right | Build real skills | Build real skills to lead |
| 38 | 4:33.14 | 4:35.73 | Left | Thank you | Thank you · Nur Anis Nasuha · Liberal Studies · UKM |

### Photos and credits (shown in small text under each photo)

| Photo | Used at | Source and licence |
|---|---|---|
| Syed Saddiq | 1:52–2:04, 4:24–4:26 | “Syed Saddiq (cropped).jpg”, US Embassy Kuala Lumpur, Public domain, Wikimedia Commons |
| Tun Dr. Mahathir | 3:32–3:38 | “Mahathir Mohamad 13112018 (cropped).jpg”, kremlin.ru, CC BY 4.0, Wikimedia Commons |
| Radcliffe Camera, Oxford | 2:29–2:31 | “Radcliffe Camera Oxford 2018 02.jpg”, Julian Herzog, CC BY 4.0, Wikimedia Commons |
| Parliament of Malaysia | 3:10–3:20 | “MalaysianParliament.jpg”, Earth (en.wikipedia), CC BY 2.5, Wikimedia Commons |
| PrimaValet campaign | 3:23–3:27 | **Placeholder card**: no freely licensed photo found. Drop in a licensed image if you have one. |

All four photos are free licences (public domain / Creative Commons) from Wikimedia Commons, chosen over random Google image results so the credits are valid.

## Step 4: Sound effects (227 placed, all synthesised from scratch)

Kinds: soft **whoosh** (slide-ins, strikes, chapter changes), **pop** (cards, chips, tiles), **tick** (check marks), **thump** (stamps such as GRADED, NOT A NEPO BABY, DECLINED ×2, = 0, BROKE OLD TRADITIONS, and the PLAN crack), and **count** ticks during number count-ups. Every effect is capped at −24 dBFS and at least 16 dB under your voice's local peak; the loudest effect is −25 dBFS against voice peaks of about −2 dBFS. 9 cues were dropped where they fell within 70 ms of the same kind.

| Time | Kind | Level (dBFS) | Trigger |
|---|---|---|---|
| 0:01.44 | pop | -28.9 | in: Greeting |
| 0:03.74 | pop | -28.9 | in: S-LOG tag |
| 0:04.56 | whoosh | -30.9 | in: Colour grade panel |
| 0:08.67 | thump | -25.9 | Colour grade panel row |
| 0:10.58 | pop | -28.9 | in: Let's get started |
| 0:13.32 | whoosh | -30.9 | in: Question |
| 0:14.74 | whoosh | -30.9 | in: My life plan |
| 0:15.04 | tick | -28.9 | My life plan row |
| 0:15.42 | tick | -28.9 | My life plan row |
| 0:15.96 | tick | -28.9 | My life plan row |
| 0:18.20 | whoosh | -30.9 | in: Big idea |
| 0:21.30 | thump | -25.0 | PLAN cracks |
| 0:21.65 | whoosh | -33.4 | PLAN falls |
| 0:22.18 | whoosh | -30.9 | in: Name card |
| 0:25.82 | pop | -28.9 | in: Capricorn |
| 0:27.30 | whoosh | -30.9 | in: Creativity + detail |
| 0:29.62 | pop | -28.9 | chip: MULTIMEDIA |
| 0:30.70 | pop | -28.9 | chip: DIGITAL MARKETING |
| 0:31.86 | pop | -28.9 | chip: IT |
| 0:32.46 | pop | -28.9 | chip: JOURNALISM |
| 0:34.32 | whoosh | -30.9 | in: Mum = teacher |
| 0:36.90 | pop | -28.9 | chip: EDUCATION |
| 0:36.90 | whoosh | -30.9 | in: Priorities |
| 0:37.60 | pop | -28.9 | chip: DISCIPLINE |
| 0:40.54 | whoosh | -30.9 | in: 16Personalities |
| 0:41.92 | whoosh | -30.9 | in: DOPE test |
| 0:47.78 | whoosh | -30.9 | in: Logic-plan-goals |
| 0:52.28 | whoosh | -30.9 | in: Diploma |
| 0:55.74 | whoosh | -30.9 | in: PNB / ASNB |
| 1:02.18 | pop | -27.9 | PNB / ASNB row |
| 1:04.34 | whoosh | -30.9 | in: UKM year 1 |
| 1:07.30 | whoosh | -30.9 | in: Head of Media Exco |
| 1:12.38 | whoosh | -30.9 | in: Perfectionism = problem |
| 1:15.18 | whoosh | -30.9 | in: Control every design |
| 1:15.72 | pop | -27.9 | Control every design row |
| 1:19.72 | whoosh | -30.9 | in: Burning out |
| 1:24.06 | whoosh | -30.9 | in: Controlling to empowering |
| 1:25.16 | whoosh | -34.2 | strike-through: Controlling |
| 1:27.20 | whoosh | -30.9 | in: The fix |
| 1:27.80 | tick | -28.9 | The fix row |
| 1:29.50 | tick | -28.9 | The fix row |
| 1:30.98 | tick | -28.9 | The fix row |
| 1:34.06 | whoosh | -32.1 | phone slide-in |
| 1:34.14 | pop | -36.1 | feed tile |
| 1:34.26 | pop | -36.1 | feed tile |
| 1:34.38 | pop | -36.1 | feed tile |
| 1:34.50 | pop | -36.1 | feed tile |
| 1:34.62 | pop | -36.1 | feed tile |
| 1:34.78 | thump | -25.9 | Launched on time stamp row |
| 1:35.90 | whoosh | -30.9 | in: Team-owned work |
| 1:39.06 | pop | -28.9 | in: Lesson learned tag |
| 1:40.80 | whoosh | -30.9 | in: Leadership is not |
| 1:44.06 | whoosh | -30.9 | in: Systems + trust |
| 1:48.86 | whoosh | -30.9 | in: Real leadership |
| 1:51.96 | whoosh | -30.9 | in: Syed Saddiq photo |
| 1:53.96 | count | -38.2 | counter AGE 33 |
| 1:54.04 | count | -38.2 | counter AGE 33 |
| 1:54.12 | count | -38.2 | counter AGE 33 |
| 1:54.19 | count | -38.2 | counter AGE 33 |
| 1:54.27 | count | -38.2 | counter AGE 33 |
| 1:54.35 | count | -38.2 | counter AGE 33 |
| 1:54.43 | count | -38.2 | counter AGE 33 |
| 1:54.50 | count | -38.2 | counter AGE 33 |
| 1:54.58 | count | -38.2 | counter AGE 33 |
| 1:54.66 | count | -33.9 | counter AGE 33 |
| 1:55.76 | whoosh | -30.9 | in: Not a nepo baby |
| 1:57.40 | whoosh | -34.2 | strike-through: Nepo baby |
| 1:57.65 | thump | -25.9 | Not a nepo baby row |
| 1:58.86 | whoosh | -30.9 | in: Mother a teacher |
| 2:02.94 | pop | -27.9 | Mother a teacher row |
| 2:05.76 | whoosh | -30.9 | in: Corporate Athlete |
| 2:07.54 | pop | -28.4 | pillar MIND |
| 2:08.26 | pop | -28.4 | pillar BODY |
| 2:08.88 | pop | -28.4 | pillar EMOTIONS |
| 2:10.84 | pop | -31.4 | pillar tracker appears |
| 2:11.68 | whoosh | -30.9 | in: Pillar MIND |
| 2:15.38 | whoosh | -30.9 | in: Debating champion |
| 2:17.96 | count | -38.2 | counter 2015 |
| 2:18.03 | count | -38.2 | counter 2015 |
| 2:18.11 | count | -38.2 | counter 2015 |
| 2:18.19 | count | -38.2 | counter 2015 |
| 2:18.26 | count | -38.2 | counter 2015 |
| 2:18.34 | count | -38.2 | counter 2015 |
| 2:18.41 | count | -38.2 | counter 2015 |
| 2:18.49 | count | -38.2 | counter 2015 |
| 2:18.56 | count | -33.9 | counter 2015 |
| 2:19.76 | whoosh | -30.9 | in: My goal at UKM |
| 2:22.40 | tick | -28.9 | My goal at UKM row |
| 2:24.56 | tick | -28.9 | My goal at UKM row |
| 2:25.94 | whoosh | -30.9 | in: Sacrifice |
| 2:29.16 | whoosh | -30.9 | in: Oxford |
| 2:29.96 | thump | -25.9 | Oxford row |
| 2:30.94 | pop | -27.9 | Sacrifice row |
| 2:32.16 | whoosh | -30.9 | in: I'd take it |
| 2:35.02 | whoosh | -30.9 | in: Heartbeat |
| 2:37.58 | pop | -27.9 | heart pop |
| 2:38.28 | whoosh | -30.9 | in: Logical path |
| 2:45.34 | pop | -27.9 | Logical path row |
| 2:46.54 | whoosh | -30.9 | in: You get |
| 2:48.46 | tick | -28.9 | You get row |
| 2:49.54 | tick | -28.9 | You get row |
| 2:50.84 | tick | -28.9 | You get row |
| 2:55.00 | whoosh | -30.9 | in: Headache |
| 2:56.62 | whoosh | -30.9 | in: Personal profit = 0 |
| 2:58.70 | thump | -25.9 | Personal profit = 0 row |
| 3:02.18 | whoosh | -30.9 | in: Selfish vs selfless |
| 3:04.10 | whoosh | -34.2 | strike-through: Selfish |
| 3:05.04 | whoosh | -30.9 | in: People of Muar |
| 3:07.94 | whoosh | -30.9 | in: Pillar BODY |
| 3:10.78 | whoosh | -30.9 | in: Langkah Muar route |
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
| 3:21.24 | whoosh | -30.9 | in: Image to funding |
| 3:23.62 | whoosh | -30.9 | in: PrimaValet placeholder |
| 3:27.24 | whoosh | -30.9 | in: Pillar EMOTIONS |
| 3:29.32 | whoosh | -30.9 | in: Minister at 26 |
| 3:30.22 | count | -38.2 | counter 26 |
| 3:30.30 | count | -38.2 | counter 26 |
| 3:30.39 | count | -38.2 | counter 26 |
| 3:30.47 | count | -38.2 | counter 26 |
| 3:30.55 | count | -38.2 | counter 26 |
| 3:30.64 | count | -38.2 | counter 26 |
| 3:30.72 | count | -33.9 | counter 26 |
| 3:32.86 | whoosh | -30.9 | in: Mahathir |
| 3:34.98 | whoosh | -30.9 | in: Change + respect |
| 3:39.10 | whoosh | -30.9 | in: Sheraton Move |
| 3:43.58 | pop | -28.9 | in: Calm in public |
| 3:45.16 | whoosh | -30.9 | in: Pillar VALUES |
| 3:45.92 | pop | -28.4 | pillar VALUES |
| 3:46.46 | whoosh | -30.9 | in: Undi18 |
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
| 3:56.44 | whoosh | -30.9 | in: 10 Oct 2026 |
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
| 4:08.24 | tick | -28.9 | Hantaran row |
| 4:10.90 | whoosh | -30.9 | in: ISTJ practical |
| 4:12.48 | whoosh | -30.9 | in: Owl forward-thinking |
| 4:16.36 | whoosh | -30.9 | in: Balance |
| 4:18.82 | whoosh | -30.9 | in: Balance pillars |
| 4:19.54 | tick | -29.9 | balance MIND |
| 4:20.20 | tick | -29.9 | balance BODY |
| 4:20.94 | tick | -29.9 | balance EMOTIONS |
| 4:21.62 | tick | -29.9 | balance VALUES |
| 4:22.46 | whoosh | -30.9 | in: My own path |
| 4:24.92 | whoosh | -30.9 | in: Role model |
| 4:26.76 | whoosh | -30.9 | in: Not just titles |
| 4:28.36 | whoosh | -34.2 | strike-through: Chase titles |
| 4:31.42 | whoosh | -30.9 | in: Build real skills |
| 4:33.14 | pop | -28.9 | in: Thank you |

## References

- Instagram reel (latest reference): **opened and studied**. I matched its look (white rounded UI cards, mono step pill with segmented progress bar, accent-highlighted words, numbered icon tiles) using your gold accent. None of its music or audio was used.
- Threads link: the post page opened (a text tips post), but its video could **not** be downloaded, so I used the fallback brief there: kinetic text, 0.3 s pop/slide with overshoot, flat icons, rounded cards, gold keywords.
