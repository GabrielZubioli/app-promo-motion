# Makes a free sound kit from scratch (nothing downloaded): ~40 distinct effects so a busy video doesn't repeat the same sound.
#   python synth_sfx.py <folder>      then pass the folder to mix.py with --lib
# Names are unique substrings, so a cue's "file" can be just the name ("Count Mid", "Pluck Hi"...).
# Families: movement (Whoosh 1-3, Swish, Swoosh Low, Swipe, Air Pass, Reverse Swell), impacts (Soft Hit, Thump, Boom, Stamp, Clack, Sub Drop),
# interface (Pop, Tick, Click, Muted Tap, Blip Up, Blip Down, Bubble, Key A-C, Digit), musical (Ding, Chime, Sparkle, Success, Pluck Lo/Mid/Hi, Coin),
# counting (Count Short / Mid / Long: accelerating ticks rising in pitch with a small bell at the end), other (Glitch, Card Flip, Shutter, Build Up, Air Bed),
# Text In (words/headlines appearing) and Confirm (check marks, something that worked).
# Use one family per kind of element (see references/sound-and-voice.md, "Dicionário de sons"), not a mix of everything.
import numpy as np, sys, os, wave
from scipy.signal import butter, sosfilt
SR = 48000
def save(name, x, folder, pan=None):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    if pan is None: s = np.stack([x, np.roll(x, 12)], 1)
    else: p = np.linspace(pan[0], pan[1], len(x)); s = np.stack([x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)], 1) * 1.4
    w = wave.open(os.path.join(folder, name + '.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(s, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def env(n, a, d): t = np.arange(n) / SR; return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)
def band(x, lo, hi): return sosfilt(butter(2, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band', output='sos'), x)
def low(x, f): return sosfilt(butter(2, f / (SR / 2), 'low', output='sos'), x)
def tone(f, n, f2=None): ph = 2 * np.pi * np.cumsum(np.geomspace(f, f2, n) if f2 else np.full(n, float(f))) / SR; return np.sin(ph)
def sec(d): return int(d * SR)
def whoosh(dur, lo, hi, seed):
    n = sec(dur); rng = np.random.default_rng(seed); x = rng.standard_normal(n); b = np.zeros(n); seg = 256
    for i in range(0, n - seg, seg): u = i / n; f = lo + (hi - lo) * np.sin(np.pi * u); b[i:i + seg * 2] += band(x[i:i + seg * 2], max(f * 0.6, 40), min(f * 1.4, 20000)) * np.hanning(min(seg * 2, n - i))
    return b * np.sin(np.pi * np.arange(n) / n) ** 2
def bell(f, d, parts=((1, 1), (2.76, 0.45), (5.4, 0.25), (8.9, 0.1))):
    n = sec(d); return sum(a * tone(f * r, n) * env(n, 0.001, d / (1.5 + r)) for r, a in parts if f * r < SR / 2 - 500)
def pluck(f, d, seed=0):   # Karplus-Strong string
    n = sec(d); p = int(SR / f); rng = np.random.default_rng(seed); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n): j = i % p; out[i] = buf[j]; buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % p])
    return out
def click(d=0.012, lo=2500, hi=9000, seed=0): n = sec(d); return band(np.random.default_rng(seed).standard_normal(n), lo, hi) * env(n, 0.0003, d / 4)
def add(x, y, at): i = sec(at); m = min(len(y), len(x) - i); x[i:i + m] += y[:m]
def count(dur, seed):   # accelerating ticks rising in pitch, then a small bell
    x = np.zeros(sec(dur + 0.4)); t, k = 0.0, 0
    while t < dur: u = t / dur; f = 1100 * 2 ** (u * 1.1); m = sec(0.018); add(x, (tone(f, m) * 0.7 + click(0.018, 3000, 9000, seed + k) * 0.5) * env(m, 0.0004, 0.004), t); t += 0.055 - 0.03 * u; k += 1
    add(x, bell(1880, 0.35) * 0.5, dur); return x
def count_roll(dur):      # mechanical counter: dry wooden ticks speeding up, ending on a soft low thud (no bell)
    x = np.zeros(sec(dur + 0.3)); t, k = 0.0, 0
    while t < dur: u = t / dur; m = sec(0.02); add(x, band(np.random.default_rng(70 + k).standard_normal(m), 500 + 900 * u, 2200 + 1500 * u) * env(m, 0.0004, 0.005) + tone(420 + 260 * u, m) * env(m, 0.0004, 0.006) * 0.35, t); t += 0.05 - 0.028 * u; k += 1
    m = sec(0.25); add(x, tone(130, m, 70) * env(m, 0.001, 0.05) * 0.9, dur); return x
def count_digital(dur):   # data readout: square blips climbing fast, ending on a two-tone chirp
    x = np.zeros(sec(dur + 0.25)); t = 0.0
    while t < dur: u = t / dur; m = sec(0.014); add(x, np.sign(tone(1400 * 2 ** (u * 1.3), m)) * env(m, 0.0003, 0.005) * 0.45, t); t += 0.032 - 0.012 * u
    for k, f in enumerate([2350, 3135]): m = sec(0.06); add(x, np.sign(tone(f, m)) * env(m, 0.0005, 0.03) * 0.4, dur + 0.055 * k)
    return x
def count_marimba(dur):   # mallet notes walking up a pentatonic scale, the last one ringing
    scale = [523, 587, 659, 784, 880, 1047, 1175, 1319, 1568, 1760, 2093]; x = np.zeros(sec(dur + 0.6)); n = 9
    for k in range(n): f = scale[k]; last = k == n - 1; m = sec(0.5 if last else 0.18); nt = tone(f, m) * env(m, 0.001, 0.12 if last else 0.045) + tone(f * 4, m) * env(m, 0.001, 0.012) * 0.3; add(x, nt * (1.0 if last else 0.75), dur * (k / (n - 1)) ** 0.85)
    return x
def main(folder):
    os.makedirs(folder, exist_ok=True); rng = np.random.default_rng(1)
    for i, (d, lo, hi) in enumerate([(0.35, 500, 5000), (0.6, 300, 3500), (1.0, 200, 2500)]): save(f'Synth Whoosh {i + 1}', whoosh(d, lo, hi, i), folder)
    n = sec(0.18); save('Synth Pop', tone(620, n, 180) * env(n, 0.002, 0.035), folder); save('Synth Tick', band(rng.standard_normal(n // 3), 2500, 9000) * env(n // 3, 0.0005, 0.006) + tone(1800, n // 3) * env(n // 3, 0.0005, 0.01) * 0.5, folder)
    n = sec(0.9); save('Synth Soft Hit', tone(120, n, 42) * env(n, 0.002, 0.2), folder); save('Synth Shutter', band(rng.standard_normal(sec(0.08)), 1500, 8000) * env(sec(0.08), 0.001, 0.015), folder)
    n = sec(2.5); u = np.arange(n) / n; save('Synth Build Up', (band(rng.standard_normal(n), 800, 7000) * 0.5 + tone(110, n, 440) * 0.5) * u ** 2.5, folder)
    n = sec(4); save('Synth Air Bed', band(rng.standard_normal(n), 1200, 9000) * np.minimum(np.minimum(np.arange(n), n - np.arange(n)) / (0.5 * SR), 1), folder)
    # movement
    save('Synth Swish', whoosh(0.22, 1500, 9000, 11), folder); save('Synth Swoosh Low', low(whoosh(0.9, 120, 1200, 12), 1500), folder)
    save('Synth Swipe', whoosh(0.4, 700, 6000, 13), folder, pan=(-0.9, 0.9)); save('Synth Air Pass', whoosh(0.7, 400, 4000, 14) * np.linspace(0.6, 1, sec(0.7)), folder, pan=(0.7, -0.7))
    w = whoosh(0.7, 300, 5000, 15); save('Synth Reverse Swell', w * np.linspace(0.02, 1, len(w)) ** 3, folder)
    # impacts
    n = sec(0.4); x = tone(95, n, 38) * env(n, 0.001, 0.09); add(x, click(0.01, 200, 1500, 3) * 0.6, 0); save('Synth Thump', x, folder)
    n = sec(1.6); save('Synth Boom', tone(70, n, 30) * env(n, 0.002, 0.35) + low(rng.standard_normal(n), 900) * env(n, 0.002, 0.25) * 0.6, folder)
    n = sec(0.5); x = tone(160, n, 60) * env(n, 0.001, 0.07); add(x, click(0.04, 400, 3000, 4) * 0.9, 0); save('Synth Stamp', x, folder)
    n = sec(0.25); save('Synth Clack', band(rng.standard_normal(n), 900, 3200) * env(n, 0.0005, 0.02) + tone(880, n) * env(n, 0.0005, 0.03) * 0.5, folder)
    n = sec(1.1); save('Synth Sub Drop', tone(110, n, 28) * env(n, 0.01, 0.4), folder)
    # interface
    save('Synth Click', click(0.012, 3000, 11000, 5), folder); m = sec(0.03); save('Synth Muted Tap', low(click(0.03, 300, 2500, 6), 1800) + tone(240, m) * env(m, 0.0005, 0.008) * 0.6, folder)
    n = sec(0.09); save('Synth Blip Up', tone(700, n, 1500) * env(n, 0.001, 0.035), folder); save('Synth Blip Down', tone(1400, n, 650) * env(n, 0.001, 0.035), folder)
    n = sec(0.08); save('Synth Bubble', tone(280, n, 1100) * env(n, 0.001, 0.025), folder)
    for k, (lo, hi) in enumerate([(1200, 5000), (900, 4000), (1600, 7000)]): m = sec(0.025); save(f'Synth Key {"ABC"[k]}', click(0.025, lo, hi, 20 + k) + tone(300 + 80 * k, m) * env(m, 0.0004, 0.006) * 0.4, folder)
    n = sec(0.03); save('Synth Digit', np.sign(tone(2100, n)) * env(n, 0.0003, 0.006) * 0.5 + np.pad(click(0.01, 4000, 12000, 30), (0, n - sec(0.01))) * 0.5, folder)
    # musical
    save('Synth Ding', bell(1320, 1.3), folder)
    x = np.zeros(sec(0.9)); [add(x, bell(f, 0.7) * 0.7, 0.06 * k) for k, f in enumerate([1047, 1319, 1568, 2093])]; save('Synth Chime', x, folder)
    x = np.zeros(sec(0.7)); [add(x, bell(2400 + rng.uniform(0, 3200), 0.25) * rng.uniform(0.3, 0.8), rng.uniform(0, 0.42)) for _ in range(9)]; save('Synth Sparkle', x, folder)
    x = np.zeros(sec(0.75)); [add(x, bell(f, 0.6), 0.11 * k) for k, f in enumerate([784, 1175])]; save('Synth Success', x, folder)
    for nm, f in [('Lo', 196), ('Mid', 330), ('Hi', 523)]: save(f'Synth Pluck {nm}', pluck(f, 0.7, int(f)), folder)
    x = np.zeros(sec(0.5)); add(x, tone(1568, sec(0.08)) * env(sec(0.08), 0.0005, 0.03), 0); add(x, tone(2093, sec(0.4)) * env(sec(0.4), 0.0005, 0.12), 0.07); save('Synth Coin', x, folder)
    # counting
    for nm, d, s in [('Short', 0.4, 40), ('Mid', 0.6, 41), ('Long', 0.9, 42)]: save(f'Synth Count {nm}', count(d, s), folder)
    # other
    x = np.zeros(sec(0.28))
    for _ in range(7): m = sec(rng.uniform(0.008, 0.03)); add(x, np.repeat(rng.uniform(-1, 1, m // 40 + 1), 40)[:m] * 0.8, rng.uniform(0, 0.24))
    save('Synth Glitch', band(x, 300, 9000), folder)
    x = np.zeros(sec(0.16)); add(x, click(0.03, 1800, 7000, 50), 0); add(x, click(0.03, 2500, 9000, 51) * 0.8, 0.05); save('Synth Card Flip', x, folder)
    # three more counters with their own character, so screens that count don't all sound alike
    for nm, d in [('S', 0.42), ('M', 0.62)]:
        save(f'Synth Count Roll {nm}', count_roll(d), folder); save(f'Synth Count Digital {nm}', count_digital(d), folder); save(f'Synth Count Marimba {nm}', count_marimba(d), folder)
    # a real water drop hitting a surface: the resonant "plink" (pitch sweeps up fast) plus a tiny splash
    n = sec(0.35); t = np.arange(n) / SR; f = 700 + 1900 * (1 - np.exp(-t / 0.012)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.minimum(t / 0.0015, 1) * np.exp(-t / 0.045); add(x, band(np.random.default_rng(80).standard_normal(sec(0.06)), 3000, 11000) * env(sec(0.06), 0.0005, 0.012) * 0.35, 0)
    t2 = np.arange(sec(0.2)) / SR; add(x, np.sin(2 * np.pi * np.cumsum(1300 + 1500 * (1 - np.exp(-t2 / 0.01))) / SR) * np.minimum(t2 / 0.001, 1) * np.exp(-t2 / 0.03) * 0.35, 0.07)
    save('Synth Water Drop', x, folder)
    # info appearing (a stat/label rising into place): airy rising swish ending on a soft blip
    n = sec(0.24); u = np.arange(n) / n; x = np.zeros(n); seg = 256; nz = np.random.default_rng(90).standard_normal(n)
    for i in range(0, n - seg, seg): f = 1500 + 4500 * (i / n); x[i:i + seg * 2] += band(nz[i:i + seg * 2], f * 0.7, f * 1.3) * np.hanning(min(seg * 2, n - i))
    x *= np.sin(np.pi * np.minimum(u / 0.8, 1)) ** 2 * 0.6; add(x, tone(900, sec(0.06), 1300) * env(sec(0.06), 0.001, 0.02) * 0.7, 0.17); save('Synth Info Up', x, folder)
    # panel appearing (a card/indicator landing in place): light glassy tap with a little body
    n = sec(0.2); x = tone(1850, n) * env(n, 0.0008, 0.03) * 0.7 + tone(2900, n) * env(n, 0.0008, 0.012) * 0.3; add(x, tone(320, sec(0.08), 220) * env(sec(0.08), 0.001, 0.025) * 0.8, 0); add(x, click(0.01, 3000, 9000, 91) * 0.3, 0); save('Synth Panel In', x, folder)
    # ratchet: one peg of a spinning wheel / roulette (fire it many times, faster then slower)
    n = sec(0.05); x = tone(3200, n) * env(n, 0.0003, 0.004) * 0.5; add(x, click(0.006, 2000, 7000, 92), 0); add(x, tone(900, sec(0.02)) * env(sec(0.02), 0.0003, 0.005) * 0.3, 0); save('Synth Ratchet', x, folder)
    # text appearing: a soft, airy swish (the one sound for every word/headline that comes in)
    n = sec(0.3); x = band(np.random.default_rng(60).standard_normal(n), 2200, 9000) * np.sin(np.pi * np.minimum(np.arange(n) / (0.22 * SR), 1)) ** 2 * np.exp(-np.maximum(0, np.arange(n) - sec(0.12)) / (0.06 * SR))
    add(x, low(np.random.default_rng(61).standard_normal(n), 700) * env(n, 0.03, 0.06) * 0.25, 0); save('Synth Text In', x, folder)
    # something worked: two short rising notes (check marks, a completed set, a confirmed day)
    x = np.zeros(sec(0.35)); [add(x, tone(f, sec(0.16)) * env(sec(0.16), 0.002, 0.05) * a, 0.065 * k) for k, (f, a) in enumerate([(1047, 0.8), (1568, 1.0)])]; add(x, click(0.008, 3000, 9000, 62) * 0.3, 0); save('Synth Confirm', x, folder)
    print('Wrote', len([f for f in os.listdir(folder) if f.endswith('.wav')]), 'sounds to', folder)
main(sys.argv[1])
