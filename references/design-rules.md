# Design rules (each one came from a real client note)

## Contents
1. Rhythm
2. Transitions by transformation (catalogue)
3. Camera and zoom
4. Text and typography
5. Screens, background and composition
6. Opening and ending
7. Review checklist

## 1. Rhythm
- Transitions between 0.5 and 0.8 s, locked to the beat. ~0.35 s felt "too fast", ~1 s "too slow".
- One event per beat or half-beat inside a scene.
- Anything that must be read holds still at least ~0.9 s after it lands (lists: one category at a time, ~1 s each).
- Something always moves: camera drift, the background grid, letters breathing, pulses on the beat. A still frame looks frozen.

## 2. Transitions by transformation
Clients ask for "one element turning into the next, or moving to form it". Never cross-dissolve one scene into another.

| From → to | How |
|---|---|
| word → object | a piece of the last intro word (its full stop as a brand-coloured dot) comes loose, rises leaving a trail, becomes a drop and falls exactly on the music's drop |
| drop → logo | the drop hits, splashes (rings, droplets), bounces and at the top of the bounce becomes the dot of the logo; mark and name appear together with a flash |
| logo → phone | the logo turns 180° (scaleX = cos θ); at the edge-on instant it swaps, and its back is the phone, which finishes the turn with content already coming in |
| progress bar → loading ring | the bar leaves the phone, arcs to the centre, curves (radius ∞ → R, log interpolation), two glowing heads pull the ends; on closing: flash + shock wave + check |
| dot → button → colour | a dot grows to the centre, becomes the button, gets a tap (squashes 8 %) and bursts into the next scene's colour |
| colour flood → next screen | the colour that filled the frame **is** the next screen seen up close: the phone starts huge and the camera pulls back to reveal it |
| check → coin → stamp | the last check spins like a coin (swap colour edge-on) and lands as the big completion check |
| card → next screen (3D) | a card that links both stories comes forward and turns 180°; its back is the next screen's background and grows uniformly through the whole turn until it fills the frame, while the rest recedes and blurs |
| screen → strips | rows of cards slide in over the screen and push it out completely (opaque until it is gone) |
| cards → weekday cards → calendar | cards flip like playing cards and are weekday cards after the turn; they spin past the camera in a 3D carousel (3D text above it), then fly to their dates and land in a centred month calendar |
| cells → drop → logo | the calendar cells are pulled into one point, become a drop that falls and reveals the logo on the drop |

Give anticipation (squash ~8 % before growing) and make the viewer follow one object at a time. A pushed screen leaves the frame
**entirely**; a leftover piece that suddenly vanishes was rejected.

## 3. Camera and zoom
- One continuous camera over depth planes: turns slowly one way, speeds up at transitions, stops on the end card.
- **Directed** zooms: the camera leans into the element that matters (a field being tapped, the ring, the button, the number) and
  lets go. 10–30 % closer; 36 % was "too strong". 0.6 s ramps; short ramps with big sideways moves blur everything.
- Consecutive close-ups become one continuous move. Punches only on strong hits (impact, stamp, biggest kick, the drop).
- Exception: a planned camera journey through 3D text in the intro (see `recipes.md`), with short holds so each word reads.

## 4. Text and typography
- Extruded 3D text, letters rising out of a blur, key word in the accent colour with glow and an underline that draws itself.
- Mixed typography: a heavy sans (e.g. Inter Black) + a hand-written script (e.g. Kaushan Script) on the key word of every headline;
  numbers always in the sans. In the intro, very unequal sizes (one word 3–4× its neighbour).
- Text belongs to the scene (a giant word behind the phone scrolling like a marquee, a number counting inside a ring), never a
  static caption at the top.
- Short lines, sentence case, full stop. A small supporting line helps dense screens.

## 5. Screens, background and composition
- The real app rebuilt in vector where the camera gets close; personal data replaced by a demo account.
- Data screens like a well-designed dashboard: a hero panel (title, subtitle, labels, legend), the "now" highlighted, indicators
  below. Indicators are part of the motion: born from the screen's own movement (a light running through the days, dots flying into
  the card, bars growing), large, with an icon; never just popping into a corner.
- Calendar/record screens: everything centred - headline, month, indicators.
- Background on every screen: a subtle grid fixed in space that **travels with each transition**, in the direction the content
  moves, so each screen feels like a different place in one space. Particles were rejected. Backgrounds never compete with data.
- Phone with side thickness, glass reflection and notch. Strips of cards as real tilted 3D planes at different depths.
- Keep the call to action out of the bottom ~23 % covered by Reels/TikTok UI.

## 6. Opening and ending
- Approved opening: the brand line as 3D words spread through space, word by word with the narration, the camera flying between
  them; only the last word ends in focus, and a piece of it becomes the next object.
- The music's drop reveals the brand. The ending echoes the opening (the drop / the logo again), with the name, tagline, the call to
  action in 3D, the official store badge and the site being typed; camera at rest on the last frame.

## 7. Review checklist
Look at every transition at 3–4 points, not only the holds: overlapping or cropped text, an empty frame for an instant, camera
blurring the text, a counter sitting at 0, a word not formed when the camera arrives, a piece of a screen that vanishes, stepped
motion blur, and, on every final render, the whole file at 1 frame per second.
