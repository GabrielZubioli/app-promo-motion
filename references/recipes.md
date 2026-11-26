# Recipes (techniques beyond the template)

Self-contained: each recipe says what works, the numbers that were approved by clients, and a snippet written against the template's
helpers (`kine`, `phone`, `layer`, `panels`, `S3`, `prog`, `inOut`, `outCubic`, `lerp`, `mk`, `SCALE`, `INTRO`, `camAt`).

## Contents
1. Intro: a sentence in 3D space, the camera flying word to word
2. A card that turns over and becomes the next screen
3. A screen pushed fully out
4. Cards on a 3D carousel (roulette)
5. Elements flying into a grid / calendar
6. Indicators born from the motion
7. Rhythm-locked sound for a carousel
8. Changing a narration line without losing sync

## 1. Intro: a sentence in 3D space
Approved after "stacked lines", "messy" and "a justified block" were rejected: the words live spread through 3D space, the camera
flies from one to the next, the sentence never needs to fit the frame; only the last word ends in focus, and a piece of it becomes
the next object (e.g. its full stop turns into a drop that falls on the music's drop).
- Very unequal sizes (90 → 330 px) and two faces (sans + script); pairs where a tiny word leans on a huge one.
- Camera distance from the word's width: `D = 2800 * width / (1080 * fraction)` (close on small words, far on big ones); a slight
  camera roll for a diagonal word; ~0.15 s holds on pairs; letters fast (`dur: 0.3, stag: 0.016`) so the word is formed on arrival.
- Words enter with the voice (measure each word's start in the narration audio).
- When the last word lands, the others dim (alpha 0.45, light 0.4) and blur by depth of field.

```js
// one 3D panel per word: its own canvas, redrawn with kine, placed in the world
const WORDS = [ // text, x, y (world, y up), z, size, rotY, rotZ, tin (scene time)
  ['Your', -700, 1600, 0, 90, 0.2, 0, -3.6], ['new', -300, 1600, -150, 330, 0.2, 0, -3.4], ['favourite', 250, 1000, 200, 260, 0, -0.3, -3.1],
  ['app.', 0, -40, 0, 300, 0, 0, -2.2]];
const WP = WORDS.map(([w, x, y, z, sz]) => { const c = mk(Math.round(sz * w.length * 0.75 * SCALE * 2), Math.round(sz * 1.8 * SCALE * 2)); return { c, ctx: c.getContext('2d'), tex: null }; });
function wordPanels(t) { WORDS.forEach(([w, x, y, z, sz, ry, rz, tin], i) => { if (t < tin - 0.05) return; const P = WP[i], R = SCALE * 2, keep = g;
  g = P.ctx; g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, P.c.width, P.c.height); g.setTransform(R, 0, 0, R, 0, 0);
  kine([w], { t, tin, tout: -0.95 + i * 0.04, x: sz * 0.3, align: 'left', y: sz * 1.15, size: sz, stag: 0.016, dur: 0.3, depth: 0.09 }); g = keep;
  P.tex ? P.tex.update() : (P.tex = S3.texture(P.c)); const dim = i < WORDS.length - 1 ? prog(t, WORDS.at(-1)[7], WORDS.at(-1)[7] + 0.45) : 0;
  panels.push({ tex: P.tex, w: P.c.width / R, h: P.c.height / R, pos: [x, y, z], rot: [0, ry, rz], alpha: 1 - 0.55 * dim, light: 1 - 0.6 * dim }); }); }
// the intro's own camera: keys [time, x, y, z, distance, roll, yaw]; blend into the normal camera over 0.5 s
const KEYS = [[-4.1, -700, 1640, 0, 900, 0, -0.2], [-3.35, -330, 1640, -75, 1750, 0, -0.1], [-3.05, 250, 1050, 200, 2800, -0.3, 0.05],
  [-2.1, 0, 0, 0, 3000, 0, -0.04], [-0.6, 0, 0, 0, 3200, 0, -0.08]];
function introCam(t) { let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++; const a = KEYS[i], b = KEYS[i + 1], e = inOut(prog(t, a[0], b[0])), k = a.map((v, j) => lerp(v, b[j], e));
  const [, x, y, z, D, roll, yaw] = k; return { eye: [x + D * Math.sin(yaw), y + D * 0.04, z + D * Math.cos(yaw)], target: [x, y, z], up: [-Math.sin(roll), Math.cos(roll), 0], fov: FOV, focus: D, aperture: 7 }; }
// in camAt(t): if (t < -0.6) blend introCam(t) with the normal camera by inOut(prog(t, -1.1, -0.6)) (eye, target, up, focus).
```

## 2. A card that turns over and becomes the next screen
A card that links two stories ("calories burned" → the calories screen) comes forward and turns 180°; its back is the next screen's
background and grows **uniformly through the whole turn** until it fills the frame; the rest recedes (scale 0.65) and blurs. No drop
shadow at the edge-on moment. Use 4× motion-blur sub-frames inside this window (`NS = SUB * 4`), or the blur shows steps.

```js
const e = inOut(prog(t, T0, T1)), th = Math.PI * e, cs = Math.cos(th), w = lerp(300, 1900, e), h = lerp(180, 3000, e);
g.save(); g.translate(lerp(cardX, 540, e), lerp(cardY, 960, e) - Math.sin(th) * 90); g.scale(Math.max(0.02, Math.abs(cs)), 1);
if (cs > 0) drawCardFront(w, h); else drawNextScreenBackground(w, h);
g.fillStyle = `rgba(0,0,0,${0.45 * (1 - Math.abs(cs))})`; g.fillRect(-w / 2, -h / 2, w, h); g.restore();
```

## 3. A screen pushed fully out
Translate until it is completely out (−1500 px), slight scale down (0.88), opaque until 85 % of the way; end the scene only after
it is gone. A leftover piece that suddenly vanishes was rejected.

```js
const push = inOut(prog(t, T0, T0 + 0.62)); g.translate(540 - push * 1500, 960); g.scale(1 - 0.12 * push, 1 - 0.12 * push); g.translate(-540, -960);
g.globalAlpha = 1 - prog(push, 0.85, 1);
```

## 4. Cards on a 3D carousel
N cards (e.g. 7 days of a week) on a ring of radius 600 around the camera's axis, spinning (N−1)/N of a turn so each passes the front
once; each card gets its check as it passes; 3D text above. Cards come in by flipping 180° from the previous scene's elements and
swap content at the edge-on instant.

```js
const phase = t => { const l = prog(t, R0, R1); return lerp(l, inOut(l), 0.3); };
function ringPose(j, t, N = 7) { const th = 2 * Math.PI * j / N - 2 * Math.PI * (N - 1) / N * phase(t), fa = 0.5 + 0.5 * Math.cos(th);
  return { pos: [600 * Math.sin(th), 40, -260 + 600 * Math.cos(th)], rot: [0, th, 0], w: 400, h: 520, alpha: lerp(0.22, 1, fa ** 1.5), light: lerp(0.4, 1, fa) }; }
const frontAt = (j, N = 7) => R0 + (R1 - R0) * j / (N - 1);   // when card j passes the front (its check, its sound)
```

## 5. Elements flying into a grid / calendar
Each element flies from its 3D pose to its cell (world `[cx − 540, 960 − cy, 0]`, size → cell size, rotation → 0, a small arc in z),
staggered 0.05 s, landing on a strong beat; cross-fade to the 2D cell in the last 0.1 s. The rest of the grid fills in a wave from
the centre. Calendar layout that read best: centred month card, weekday header, outside days dimmed, future days outlined, today
with a ring and a "today" tag below it. Keep demo data coherent (a streak that ends today; totals that add up).

## 6. Indicators born from the motion
Not cards that pop in a corner: a light runs through the streak dates row by row (no diagonal lines between weeks) with a small
counter, then a spark jumps into the indicator card; each marked day sends a dot into the second card, which counts the dots that
arrive; weekly bars grow inside the third. Wide cards (300×214) with an icon, a 92 px number and a label; one in the warm colour;
a small hop on the beat.

## 7. Rhythm-locked sound for a carousel
A roulette: one `Ratchet` click per third of a card, timed from the carousel's real phase (fast while it speeds up, spaced as it
slows), the third click a little louder. Generate the times in the cue script:

```python
last = 0
for k in range(int((R1 - R0) / 0.0005) + 1):
    t = R0 + k * 0.0005; ph = int(phase(t) * 3 * (N - 1) + 1e-9)
    if ph > last: cues.append(dict(at=round(t + INTRO, 3), file='Ratchet', db=-8 if ph % 3 == 0 else -11)); last = ph
```

## 8. Changing a narration line
Edit `vo.json`, copy the voice folder (keep the previous take), regenerate only that line (`ONLY=n`), measure where its words start
in the new audio and re-time whatever follows the voice.
