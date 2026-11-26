# Music analysis for beat-synced motion design: tempo, grid phase, energy per bar, drop candidate, accents (kick/snare).
#   python -I analyze_music.py <track.mp3|wav> [--out audio/] [--start 23.195] [--dur 32.8] [--check 23.195 2.4]
# --start/--dur: list accents for the cut you will use (times printed relative to --start = video time 0).
#   Without --start, the cut starts 2.4 s before the detected drop.
# --check START T: RMS 0.8 s before and after T in the cut that begins at START (confirms the drop lands on T).
# Needs numpy (Blender's bundled python works) and ffmpeg on PATH. Writes <out>/analysis.json and <out>/wave.png.
import argparse, json, os, subprocess, sys, tempfile, wave
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('track'); ap.add_argument('--out', default='.')
ap.add_argument('--start', type=float); ap.add_argument('--dur', type=float, default=33.0)
ap.add_argument('--check', type=float, nargs=2, metavar=('START', 'T'))
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

tmp = os.path.join(tempfile.mkdtemp(), 'mono.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.track, '-ac', '1', '-ar', '22050', '-c:a', 'pcm_s16le', tmp], check=True)
w = wave.open(tmp); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

if a.check:
    st, t = a.check
    def rms(p, q): s = x[int((st + p) * sr):int((st + q) * sr)]; return float(np.sqrt((s ** 2).mean()))
    print(f'RMS before ({t - 0.8:.2f}-{t:.2f}s): {rms(t - 0.8, t):.3f}   after ({t:.2f}-{t + 0.8:.2f}s): {rms(t, t + 0.8):.3f}')
    sys.exit()

# spectral flux envelopes
hop, win = 128, 1024; fps = sr / hop
fr = np.lib.stride_tricks.sliding_window_view(x, win)[::hop] * np.hanning(win)
S = np.log1p(100 * np.abs(np.fft.rfft(fr, axis=1))); f = np.fft.rfftfreq(win, 1 / sr)
def env(m): d = np.maximum(0, np.diff(S[:, m], axis=0)).sum(1); return np.concatenate([[0], d])
full, kick, snare = env(slice(None)), env(f < 150), env((f > 1500) & (f < 6000))
rms = np.sqrt(np.convolve(x ** 2, np.ones(1024) / 1024, 'same'))[::hop][:len(full)]
tt = np.arange(len(full)) / fps

# tempo: autocorrelation of the onset envelope, then comb fit for bpm + phase
o = full - np.convolve(full, np.ones(32) / 32, 'same'); o[o < 0] = 0
n = min(len(o), int(fps * 60)); ac = np.correlate(o[:n], o[:n], 'full')[n - 1:]
lags = np.arange(len(ac)) / fps; bpms = 60 / np.maximum(lags, 1e-9)
bpm0 = 60 / lags[np.argmax(ac * ((bpms > 70) & (bpms < 180)))]
best = (-1, bpm0, 0)
for b in np.arange(bpm0 - 2, bpm0 + 2, 0.02):
    per = 60 / b
    for ph in np.arange(0, per, 0.005):
        idx = np.round(np.arange(ph, tt[-1], per) * fps).astype(int); s = o[idx[idx < len(o)]].sum()
        if s > best[0]: best = (s, b, ph)
_, BPM, PH = best; per = 60 / BPM
beats = np.arange(PH, tt[-1], per)
print(f'BPM {BPM:.2f}  phase {PH:.3f}s  beat {per:.3f}s  half beat {per / 2:.3f}s  (if it feels slow, the real tempo may be {BPM * 2:.1f})')

# energy per 4-beat bar and drop candidate (largest jump of mean RMS across a bar line)
def at(e, t, w=0.05): i = int(t * fps); j = max(1, int(w * fps)); return float(e[max(0, i - j):i + j].max()) if i < len(e) else 0.0
bars = [(float(beats[i]), float(np.mean([at(rms, b, 0.1) for b in beats[i:i + 4]]))) for i in range(0, len(beats) - 4, 4)]
print('\nbar        energy')
for t0, e in bars: print(f'{t0:8.2f}  {e:.3f} ' + '#' * int(e * 120))
# drop candidates: RMS 0.8 s after vs 0.8 s before each half beat; best ratios, at least 4 s apart
def seg(p, q): z = x[max(0, int(p * sr)):int(q * sr)]; return float(np.sqrt((z ** 2).mean())) if len(z) else 0.0
cands = sorted(((seg(h, h + 0.8) / max(seg(h - 0.8, h), 1e-4), float(h)) for h in np.arange(PH + 0.8, tt[-1] - 0.8, per / 2)), reverse=True)
drops = []
for r, h in cands:
    if r < 1.3 or len(drops) == 3: break
    if all(abs(h - d) > 4 for _, d in drops):
        c = np.arange(h - 0.15, h + 0.15, 0.005)                # refine: steepest RMS rise near that half beat
        drops.append((r, float(c[np.argmax([seg(v, v + 0.1) - seg(v - 0.1, v) for v in c])])))
drop = drops[0][1] if drops else 0.0
print('\ndrop candidates (energy after/before): ' + '   '.join(f'{d:.3f}s x{r:.2f}' for r, d in drops) + '   - confirm with --check')

start = a.start if a.start is not None else max(0.0, drop - 2.4)
grid = np.round(np.arange(0, a.dur, per / 4), 3)
K = np.array([at(kick, start + t) for t in grid]); Sn = np.array([at(snare, start + t) for t in grid])
K /= K.max() or 1; Sn /= Sn.max() or 1
acc = []
print(f'\naccents in the cut starting at {start:.3f}s (video time; K=kick S=snare, >0.55)')
for t, k, s in zip(grid, K, Sn):
    m = ('K' if k > 0.55 else '') + ('S' if s > 0.55 else '')
    if m: acc.append({'t': float(t), 'kick': round(float(k), 2), 'snare': round(float(s), 2), 'mark': m}); print(f'{t:6.2f}  {k:4.2f} {s:4.2f}  {m}')

json.dump({'bpm': BPM, 'phase': PH, 'beat': per, 'beats': beats.tolist(), 'bars': bars, 'drop': drop, 'drops': [d for _, d in drops],
           'cut_start': start, 'accents': acc}, open(os.path.join(a.out, 'analysis.json'), 'w'), indent=1)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', a.track, '-filter_complex', 'showwavespic=s=2400x400:split_channels=0:colors=0xff7a1a',
                '-frames:v', '1', os.path.join(a.out, 'wave.png')], check=True)
print(f'\n-> {os.path.join(a.out, "analysis.json")} and wave.png')
