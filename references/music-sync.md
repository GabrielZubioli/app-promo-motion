# Syncing to the music

## Analysis
```
python -I scripts/analyze_music.py track.mp3 --out audio/ [--start 21.6 --dur 34.4]
```
Writes `audio/analysis.json` and `audio/wave.png` and prints: BPM and grid phase; energy per bar; up to 3 drop candidates (biggest
energy ratio 0.8 s after/before each half-beat); and the accents (kick `K`, snare `S`) of the cut, in video time. Without `--start`
the cut starts 2.4 s before the first candidate.

Care:
- The detector may find half the tempo (75 instead of 150). Pick the grid that feels natural; a half-beat grid works well.
- A track can have several "drops": show the candidates and confirm which one is meant. Measure it: `--check START T` prints the RMS
  0.8 s before and after T in the cut that starts at START (a real drop roughly doubles it).
- Strong accents rarely sit only on the grid; use the measured ones for the big moments.

## Deciding the cut
1. Put the brand reveal on the drop. In the template that is scene time 0 and `PROJECT.music.drop` (seconds into the track).
2. Need more time before it (a text intro)? Start the music N beats earlier: `INTRO` grows and everything stays in sync.
3. End at the end of a musical phrase, with a ~0.9 s fade.
4. Music start in the track = drop (track) − video time of the `music.drop` event.

## Mapping events
Write an "accent → event" table before the timings: strong kicks for impacts and screen changes, snares for text entrances, answer
swaps and pops. Then put every time in one object (`B`) on the half-beat grid, nudged to the measured accents.

## Audio
Cut with `atrim`, short fade-in (0.02–0.4 s), ~0.9 s fade-out; music at 0.8; total −14 LUFS / −1.5 dBTP. `mix_final.py` does it,
with effects and narration on top.
