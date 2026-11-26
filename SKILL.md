---
name: app-promo-motion
description: Makes professional motion-design promo videos for apps (vertical 9:16 for Reels/TikTok/Shorts, 15-45 s), built entirely in code and rendered frame by frame - kinetic 3D text, one element turning into the next, a continuous 3D camera, a background grid that travels between screens, mixed typography, a sound effect for every element, optional narration (any TTS, your own recordings, or none) and everything locked to the beats of a song; delivered in 1080p, 2K or 4K. Use it whenever someone wants a promo video, ad, launch video, app trailer, motion piece or storyboard for an app or SaaS, wants to sync a video to music, add narration or sound effects to an app video, render one in 4K, or gives notes on such a video ("the transition is too fast", "the zoom", "change the sound") - even if they never say "motion design". Commands: help, doctor, new, brief, storyboard, music, build, review, preview, sound, voice, mix, render, notes, caption.
---

# App promo motion

A tested pipeline for app promo videos where every event lands on a beat, every scene change is one element turning into the next,
the camera never stops, the background travels with the content, text is part of the animation, every element has its own sound,
and the narration (optional) complements the screen. Everything is code: a note becomes a few changed numbers and a new render.

`<skill>` below means the folder this file is in. Talk to the user in **their** language (all files here are in English; a
Portuguese guide for people is in `GUIA.pt-BR.md`).

## What's inside

| Path | What it is |
|---|---|
| `assets/template/` | neutral starter page (`index.html` + `project.js`): 3D text intro → the drop reveals the logo → logo turns into the phone → app screens pushed one after another → phone turns back into the logo → call to action. Colours, fonts, logo, screenshots, words and music tempo all come from `project.js` |
| `assets/mix.example.json` | final mix config |
| `scripts/doctor.mjs` | checks Node, ffmpeg, Chrome, Python/numpy/scipy, GPU/WebGL, optional keys and voices |
| `scripts/new_project.mjs` | creates a project from the template |
| `scripts/render.mjs` + `gl3d.js` | renders stills, video (1080p/2K/4K, `--chunk` for long renders, `--from/--to`), events |
| `scripts/analyze_music.py` | tempo, beat grid, drop candidates, accents |
| `scripts/synth_sfx.py` | ~55 sound effects made from scratch |
| `scripts/build_cues.py` | automatic sound map from event names (the sound dictionary) |
| `scripts/mix.py` | places each effect on its event (0 ms offset check) |
| `scripts/narrate.mjs` | narration: `none`, `files` (any TTS / own recording), `system` (free OS voice), `elevenlabs`, `openai` |
| `scripts/sfx_elevenlabs.mjs` | optional realistic sound effects (ElevenLabs) |
| `scripts/mix_final.py` | music + effects + narration (ducked), −14 LUFS, muxed onto the video |
| `scripts/sheet.sh` | contact sheet of stills with times |
| `references/` | `design-rules.md` (taste, from real client notes), `engine.md` (how the page works), `recipes.md` (advanced techniques), `music-sync.md`, `sound-and-voice.md`, `claims-and-licensing.md` |

Requirements: Node 18+, ffmpeg, Chrome/Chromium, Python 3 with numpy + scipy. Narration and realistic effects are optional.
No AI video/image generators and no generated realistic humans: everything comes from code, the client's assets and real screenshots.

## The two non-negotiable rules
1. **Every scene becomes the next through its elements.** A shape, a card, a number, a word, a colour or the device itself
   leaves the current scene and turns into something in the next one. No cuts, no fades, no plain slides between scenes. If a change
   has no element doing the transformation, it isn't designed yet.
2. **Every screen has its own idea and nothing repeats.** Each scene gets a different presentation (layout, what the camera does,
   how the content is shown, how the text enters) and a different transition; no two scenes in a video share the same concept or
   the same transition. Aim for creative, professional work in every screen, not a pattern repeated with new content. The
   template's "phone + headline + push" for each screen is only a working skeleton to replace, never the final design.

## Commands

The user types `/app-promo-motion <command> [args]`. With no command, or with a plain request ("make a promo for my app"), run the
whole flow from `doctor` → `new` → `brief` → `storyboard` → `music` → `build` → `review` → `preview` → `sound` → `voice` → `mix`
→ `render`, stopping for approval after the storyboard and after each preview.

### help
List these commands with one line each and the current project's state (which steps are done).

### doctor
`node <skill>/scripts/doctor.mjs`. Explain each FAIL in plain words with the fix. Optional items (keys, system voice) are fine to miss.

### new [folder] [--name "App"]
`node <skill>/scripts/new_project.mjs <folder> --name "<App>"`. Creates `video/` (template + render.mjs), `material/`, `audio/`,
`renders/`. Then render 3 stills of the template so the user sees it works, and move on to `brief`.

### brief
Collect the app's real material and facts, and fill `video/project.js`:
- name, one-line tagline, site, stores; brand colours (accent, warm, background) - take them from the logo/app if not given; fonts
  (put the files in `video/fonts/`, update `@font-face` and `PROJECT.fonts`);
- logo (transparent SVG/PNG) and 3–6 real portrait screenshots, taken with a demo account (never real personal data);
- 3–5 key features in the user's words, each with its source (app/store/code) - read `references/claims-and-licensing.md`;
- music: the track and its licence; narration: yes/no and which provider.
Ask only for what is missing, in one batched message.

### storyboard
A numbered storyboard: per scene the time range, **its concept** (how this screen is presented differently from all the others -
pick from the menu in `references/design-rules.md` §8 or invent), what is on screen, what moves, the headline, **the element that
transforms into the next scene and how** (catalogue in `references/design-rules.md` §2), and the narration line if any. Before showing
it, check the two non-negotiable rules: every change has a transforming element, and no concept or transition appears twice. Wait for
approval. Notes that change scenes or transitions need a new storyboard; timing/size/style notes don't.

### music [file]
`python -I <skill>/scripts/analyze_music.py <track> --out audio/`. Show BPM and the drop candidates, confirm the drop with the user
(`--check`), set `PROJECT.music.bpm` and `.drop`, and plan the cut (`references/music-sync.md`). The logo reveal lands on the drop.

### build
Implement the storyboard in `video/index.html`, starting from the template's scenes and the recipes (`references/recipes.md`, with code
snippets). Keep the page contract (`#c`, `renderAt`, `TOTAL`, `ready`, `EVENTS`). Name events with a category prefix (`text.`,
`tap.`, `ok.`, `swap.`, `flip.`, `count.`, `info.`, `panel.`, `spin.`, `type.`, `brand.`, `mute.`) so `sound` can map them. Every
note round after the first build: a patch script per version (`references/engine.md` §9). Check the script with `node --check`.

### review [times…]
Stills at the key moments **and in the middle of every transition** (`render.mjs stills` takes video time = scene time + INTRO),
contact sheet with `sheet.sh`, then actually look: overlapping/cropped text, empty frames, camera blurring text, counters stuck at 0,
words not formed when the camera arrives, leftovers that vanish, stepped blur - and the two rules: any scene change without a
transforming element, or two screens that look/move alike. Fix before showing. Say that stills aren't playback.

### preview
1080p render with final quality (`render.mjs video … --scale 1 --gpu`), mix (effects, narration if any), and give the user a
compressed copy small enough for chat (`ffmpeg … -crf 22`, aim < 25 MB); the original stays in `renders/`. Report in plain words
what changed and what can only be judged by watching.

### sound
`render.mjs events` → `build_cues.py` → `synth_sfx.py` (once) → `mix.py`; hand-tune special moments (`references/recipes.md` §7).
Follow the sound dictionary in `references/sound-and-voice.md`: one right sound per kind of element, never a pile of unrelated
sounds, a different counter per screen and only where the number is the point. Level ≈ the music's; total −14 LUFS.

### voice [provider]
Narration is optional. Write the script (complements the screen; one line per scene; measured against its window), save it in
`audio/vo.json`, then `node [--env-file=.env.local] <skill>/scripts/narrate.mjs audio/vo.json audio/vo --provider <p>`:
`none` (skip), `files` (the user's own recordings or any other TTS: `t01.wav`, `t02.mp3`…), `system` (free OS voice, good as a guide),
`elevenlabs` / `openai` (key in `.env.local`, never in chat or code). **Ask before spending paid credits.** Change one line with `ONLY=n`.

### mix
`python <skill>/scripts/mix_final.py audio/mix.json` (template `assets/mix.example.json`): music start = track drop − video time of
the `music.drop` event; no narration → no `vo` block. Check LUFS and peak in the output.

### render <1080p|2k|4k>
One render at a time, normal priority. `--scale 1` / `1.3333334` / `2`; **always `--chunk 150` for 2K/4K** (otherwise WebGL can be
lost mid-render and the rest comes out as background only). Chain render → mix with `|| exit 1`. Before delivering: 1 frame per
second contact sheet of the whole file + resolution, frames, duration, LUFS. Reels/TikTok deliver 1080p; 4K is for YouTube and masters.

### notes "<notes>"
Apply all notes of the round as a new version (patch script), generalise each fix to the whole video, review, preview. If a note
teaches a lasting preference, say so and keep applying it.

### caption [platform]
Write the post text for the video (LinkedIn, Instagram, TikTok…) from the verified facts only: hook line, what the app does,
2–4 concrete features with real numbers, where to get it, one specific question or call to action; links go in the first comment
on LinkedIn. No invented metrics or stories.

## Rules that save whole rounds
- Every scene change is a transformation made by an element; every screen has its own concept; nothing repeats.
- Transitions 0.5–0.8 s on the beat; never cross-dissolve.
- Directed zooms of 10–30 % with 0.6 s ramps; no fast sideways pans except a planned intro camera journey.
- Text is animated 3D type, never a static caption; lists one item at a time, held ~1 s.
- Backgrounds stay subtle: the travelling grid, no particles, nothing behind data.
- A pushed screen leaves the frame entirely. A fast turn gets 4× motion-blur sub-frames.
- Sound: the right family per element, no stacks of unrelated sounds; silence is a valid choice.
- Only true claims; demo data coherent; official store badges in the final.
- Keys only in `.env.local`; confirm before paid API calls; one heavy render at a time; check the whole final file.
