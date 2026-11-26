# Sound effects and narration

## Contents
1. Sound effects: pipeline
2. The sound dictionary (one right sound per element)
3. Levels
4. Narration: script
5. Narration: providers (none, files, system, ElevenLabs, OpenAI)
6. Final mix

## 1. Sound effects: pipeline

1. Kit: `python scripts/synth_sfx.py audio/sfx-kit` (about 55 sounds made from scratch; list at the top of the script). Nothing is downloaded.
2. Events: `node scripts/render.mjs events video/index.html audio/events.json --gpu`.
3. Map: `python scripts/build_cues.py audio/events.json audio/cues.json` gives every event the right sound from its name prefix
   (`text.`, `tap.`, `ok.`, `swap.`, `flip.`, `count.`, …). For hand-tuned moments add extra cues (e.g. roulette clicks that follow a carousel's real rotation: `recipes.md` §7).
4. Mix: `python scripts/mix.py audio/cues.json audio/sfx.wav --lib audio/sfx-kit [--lib more/] --events audio/events.json --len <video seconds>`.
   Check "worst offset 0.0 ms". A cue is `{"event" | "at", "file", "db", "align": "peak|start|end", "pitch", "offset", "dur"}`.
5. Whenever events move or are renamed: regenerate `events.json` and the map (the mixer stops on an unknown event name).

Realistic sounds (water, a real object): the synth kit is not convincing there. With an ElevenLabs key,
`node --env-file=.env.local scripts/sfx_elevenlabs.mjs audio/sfx-real "drop|a single water drop hitting a hard floor"` makes 3 variations;
pick the one with a single clean transient and pass the folder as another `--lib`. Without a key, use any sound file you have the rights to.

## 2. The sound dictionary

Each kind of element always gets the same family of sound, the way a sound designer would do it. Never stack unrelated sounds on
one moment (guitar pluck + click + bubble on letters appearing was rejected). When an element repeats, vary only the pitch a little.

| Element | Sound | Event prefix |
|---|---|---|
| words, headlines, captions appearing | Text In | `text.` |
| click, tap, selection | Click | `tap.` |
| something worked (a check, a set done, a day done) | Confirm | `ok.` |
| a bigger completion (ring closing, trophy) | Success | `done.` |
| a screen sliding sideways | Swipe | `swap.` |
| a bigger move between screens | Whoosh 1-3 (by size of the move) | `whoosh.` |
| a card or logo turning over | Card Flip (+ a soft whoosh) | `flip.` |
| something landing | Soft Hit / Stamp | `land.` |
| a big hit | Boom | `impact.` |
| an interface element appearing | Pop (low) | `ui.` |
| a stat/label rising into place (one per item) | Info Up | `info.` |
| a card/indicator landing | Panel In | `panel.` |
| a number counting up (only where the climbing number is the point) | Count Digital / Roll / Marimba (a different counter per screen) | `count.` |
| a carousel/wheel turning | Ratchet clicks like a roulette (fast → slow, following the rotation) | `spin.` |
| typing | Key A-C | `type.` |
| the brand moment | Chime (+ Build Up into it) | `brand.` |
| moments that should stay silent | nothing | `mute.`, `music.` |

Approved choices worth repeating: the background travelling between screens gets no sound of its own (the screen transition already
has one); where a number is just information appearing, use Info Up / Panel In instead of a counter; a drop of water turning into the
logo can be silent and let the music carry it.

## 3. Levels

`mix.py` normalises the effects track to a −1 dBFS peak, so the real level is `sfx.volume` in the mix config. Measure:
`ffmpeg -i audio/sfx.wav -af volume=2.15,ebur128 -f null -` and compare with the music cut at 0.8.
Reference: effects about level with the music (≈ −10.6 LUFS each). Clients usually ask for louder effects than the first
mix; raise in steps of ~2 dB. The final mix stays at −14 LUFS integrated (the platforms' target; louder masters just get turned down).

## 4. Narration: script

- Complements the screen instead of reading it ("Log every set in seconds." over the session screen).
- One line per scene; arc: close and warm at the start, energy in the middle, confident brand line + call to action at the end.
- Only true claims. Never repeat an expression in consecutive lines.
- Each line gets a start time `t` (video time) and a `window` (until the next line); measure that it fits.
- Keep the script in a `.md` with time, scene, line and delivery notes.
- Text that appears with the voice (an intro word by word): measure where each word starts in the generated audio (10 ms RMS
  envelope of the trimmed file) and time the words to it.

## 5. Narration: providers

`node [--env-file=.env.local] scripts/narrate.mjs audio/vo.json audio/vo [--provider ...]` writes `tNN.wav` per line. Set `"provider"`
in `vo.json`. `ONLY=3,5` regenerates just those lines (keep the old take in another folder first).

| Provider | What it needs | Use it for |
|---|---|---|
| `none` | nothing | no narration (music + effects only); leave `vo` out of the mix config |
| `files` | your own `t01.wav/.mp3`… in the folder | any other TTS (Azure, Google, Play.ht, …) or a real voice recording |
| `system` | the OS voice (Windows SAPI, macOS `say`, Linux `espeak-ng`) | free guide track to approve text and timing |
| `elevenlabs` | `ELEVENLABS_API_KEY`, `voice` = voice id, optional `model` | natural final voice; v3-type models read `[warmly]`-style tags |
| `openai` | `OPENAI_API_KEY`, optional `voice`, `model` | natural final voice; a line's `style` becomes the speaking instruction |

Rules: keys only in `.env.local` / the environment, never in code or chat. ElevenLabs: library voices through the API and
commercial use need a paid plan. Avoid whisper/soft deliveries (they come out too quiet even after normalising). Make a `system`
guide first, then spend credits.

## 6. Final mix

`python scripts/mix_final.py audio/mix.json` (template in `assets/mix.example.json`; paths relative to the config): music cut
(`start` = the track's drop − the video time of the `music.drop` event), effects, narration (trimmed, each line to −18 LUFS,
placed on its time, music + effects ducked under it with a sidechain compressor), total to −14 LUFS / −1.5 dBTP, muxed onto the
silent video without re-rendering. No narration: remove the `vo` block.
