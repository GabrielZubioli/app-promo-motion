# The page engine

Starting point: `assets/template/` (neutral, driven by `project.js`). Techniques beyond the template, with code snippets, are in `recipes.md`.

## Contents
1. Contract and clock
2. Depth planes and camera
3. Directed focus and punches
4. 2D helpers
5. Kinetic 3D text
6. Phone and screens
7. Own 3D panels
8. Background grid
9. Versions (patch scripts)
10. Performance and rendering

## 1. Contract and clock
- `canvas#c` 1080×1920 × `?scale`; `window.renderAt(t)`, `window.TOTAL`, `window.ready` (Promise), `window.EVENTS` ([{name, t}] in video time).
- All times in seconds of the **scene clock**, where 0 is the music's drop. `INTRO` = time before the drop: `frame(ts - INTRO)` and
  events shifted by `+INTRO`. Moving the start of the music by whole beats keeps everything in sync. The template computes all
  times from `PROJECT.music.bpm` (beat, half-beat grid).
- Motion blur: 12 sub-frames over a 180° shutter (`SUB`), averaged. Very fast moves (a 180° turn plus growth in 0.45 s) show the
  sub-frames as steps: raise the count only inside that window (`NS = SUB * 4`).

## 2. Depth planes and camera
- Three transparent canvases (`back` z −520, `mid` 0, `front` +210) drawn in screen coordinates with margins (`MX`, `MY`) and 1.25×
  supersampling, each turned into a `gl3d` panel scaled by `(2800 − z)/2800` so it matches the screen at rest.
- The base background (radial gradient) is drawn straight onto the frame, behind the planes, so no edge ever shows.
- `layer(name)` selects a plane; only used planes are uploaded.
- One continuous camera: distance ~2800–3100, small yaw/pitch easing to 0, driven by `CAMF(t)` = normalised integral of a speed
  of 1 plus gaussian bumps at transitions (`camBumps`), braking to a stop at the end (`camStop`). It never reverses.
- Depth of field: aperture ~6, focus near the mid plane; things at other depths blur for real.

## 3. Directed focus and punches
- `FOC = [[t0, t1, x, y, amount], ...]` (screen px; may be functions of t): 0.6 s ramps in and out; the camera moves its target to
  (x, y) and comes closer by `amount` (0.10–0.30 = 10–30 %). Several close-ups in a row become one continuous move.
- `zooms = [[t, a], ...]`: punches (in ~35 ms, out ~0.38 s); a > 0 closer, a < 0 back. Only on strong hits.

## 4. 2D helpers
`circle`, `rrect`, `txt`, `blurF(px)` and `shadow(col, blur, dy)` (already scaled), `mixHex` (returns hex), `rgba(hex, a)`, easings
(`outCubic`, `inOut`, `sine`), `prog(t, a, b)`, `pulse(t)` (1 on each beat, decaying), `words(...)` (small text word by word).

## 5. Kinetic 3D text
`kine(lines, {t, tin, tout, y, size, sizes, lh, align, x, stag, dur, w, depth, noUl, scriptKey, wave})`:
- `*word*` = key word: accent colour, script face 1.2× (`scriptKey: false` to keep it in the sans face; numbers never), glow pulsing on
  the beat, underline that draws itself.
- Extrusion: the glyph drawn N times downwards from the face tone to the side tone, then the face with a gradient.
- Letters rise one by one out of a blur (`stag` ~0.02 s, `dur` 0.5 s; use 0.3 s when words must be readable fast) and leave upwards.

## 6. Phone and screens
- `phone(cx, top, width, alpha, drawScreen)`: body with side thickness, rim, screen clipped in 1082-unit coordinates (a real
  screenshot's measurements work directly), glass reflection, camera notch.
- Screens: real screenshots (`cover` fit) for a first cut; rebuild in vector what the camera will show up close (fields that animate,
  checks that draw themselves, numbers that count). Personal data replaced by a demo account.
- Turning over: `scaleX = |cos θ|`; swap the content at the edge-on instant (logo → phone, phone → logo).

## 7. Own 3D panels
For elements that move in 3D on their own (intro words, cards that flip, a carousel): one canvas per element, `S3.texture(canvas)`
once and `.update()` per sub-frame, pushed as `{tex, w, h, pos, rot, scale, alpha, light, bias}` next to the planes (`bias` > 0
draws over a plane at the same depth). A scene can have its own camera: `camAt(t)` returns another camera (with `up` for roll) and
blends into the normal one over ~0.5 s.

## 8. Background grid
A periodic grid texture (no baked vignette, faded edges) on a panel at z −640; `spaceAt(t)` sums eased `[start, end, dx, dy]` steps
(one per transition, in the direction the content moves) plus a slow constant drift; position modulo the period (`wrapP`) so it
scrolls forever. Keep it subtle (line alphas ~0.03/0.07). No particles.

## 9. Versions (patch scripts)
Don't hand-edit the page for every note. One `_applyNN.js` per round reads the previous version, applies exact replacements with a
`rep(a, b)` that throws if `a` is missing, and writes `vNN.html`. Each round is reproducible and the previous one stays intact.
Then extract the `<script>` and `node --check` it. Pitfalls: back-ticks and `${}` inside a template-string patch must be escaped, and
a `\n` passed through a shell heredoc can become a real line break inside a JS string.

## 10. Performance and rendering
- 1080p with 12 sub-frames: ~3–5 min for 35 s on a common GPU; stills take seconds.
- `node render.mjs stills page.html dir 0.5 1.2 ... --gpu` (times are **video** time = scene time + INTRO) → `bash sheet.sh dir out.jpg 6x3`.
- `node render.mjs video page.html out.mp4 --fps 25 --scale 1 --gpu` (2K: `--scale 1.3333334`; 4K: `--scale 2`).
- Long renders (4K, 2K, anything over ~20 s at 4K) **always with `--chunk 150`**: Chrome piles up GPU memory and, around frame
  ~585 of a 4K render, loses the WebGL context; from there on only 2D (background, flash, vignette) is drawn and the render still
  "succeeds". `--chunk` reopens Chrome every N frames into the same file; `gl3d.js` flags `window.__glLost` and `render.mjs` aborts.
- One 4K render at a time (Chrome's GPU process peaks ~15 GB). Never lower the render's process priority on Windows 11 (efficiency
  mode nearly stops it).
- `--from/--to` render a frame range (resume an interrupted render, or parallel parts at 1080p) and join with `ffmpeg -f concat -c copy`.
- Chain render → mix with `|| exit 1` on each step (bash `set -e` ignores failures inside `&&`).
- After every final render: a contact sheet of 1 frame per second of the whole file, plus resolution, frame count, duration, LUFS.
