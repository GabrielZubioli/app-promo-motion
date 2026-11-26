# Final audio: music cut + SFX bed + narration (optional), ducked under the voice, -14 LUFS, muxed onto the rendered video.
#   python mix_final.py config.json
# config.json (paths relative to the config file):
# {"video": "Video - teste 1080p.mp4", "out": "Video - final 1080p.mp4", "duration": 32.8,
#  "music": {"file": "musica.mp3", "start": 23.195, "volume": 0.8, "fade_in": 0.4, "fade_out": 0.9},
#  "sfx":   {"file": "audio/sfx.wav", "volume": 1.4},
#  "vo":    {"lines": "vo.json", "dir": "audio/vo", "lufs": -18, "boost": 2.0}}   <- optional: leave "vo" out for no narration
# vo.json lines carry "t" (start, video time) and "window" (seconds until the next line); files are <dir>/tNN.wav or .mp3 (from narrate.mjs, any TTS or your own recordings).
# Only stdlib + ffmpeg/ffprobe. Prints each line's trimmed length against its window.
import json, os, subprocess, sys

cfg_path = sys.argv[1]; base = os.path.dirname(os.path.abspath(cfg_path))
C = json.load(open(cfg_path, encoding='utf-8'))
P = lambda p: os.path.join(base, p)
D = C['duration']; m = C['music']; sfx = C.get('sfx'); vo = C.get('vo')
work = P(os.path.join('audio', '_mix')); os.makedirs(work, exist_ok=True)
ff = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)

inputs = ['-i', P(m['file'])]
fade_out = m.get('fade_out', 0.9)
graph = (f"[0]atrim=start={m['start']}:duration={D},asetpts=PTS-STARTPTS,aresample=48000,"
         f"afade=t=in:d={m.get('fade_in', 0.4)},afade=t=out:st={D - fade_out:.3f}:d={fade_out},volume={m.get('volume', 0.8)}[m];")
bed = '[m]'
if sfx:
    inputs += ['-i', P(sfx['file'])]
    graph += f"[1]atrim=duration={D},aresample=48000,volume={sfx.get('volume', 1.4)}[s];[m][s]amix=inputs=2:normalize=0[bed];"
    bed = '[bed]'

if vo:
    lines = json.load(open(P(vo['lines']), encoding='utf-8'))['lines']
    vin, vf, lab = [], '', ''
    for i, l in enumerate(lines, 1):
        src = next((P(os.path.join(vo['dir'], f't{i:02d}.{e}')) for e in ('wav', 'mp3', 'm4a', 'flac', 'aiff') if os.path.exists(P(os.path.join(vo['dir'], f't{i:02d}.{e}')))), None)
        if not src: sys.exit(f"missing narration file t{i:02d}.wav/.mp3 in {vo['dir']} (run narrate.mjs, or remove 'vo' from the config for no narration)")
        dst = os.path.join(work, f'c{i:02d}.wav')
        trim = 'silenceremove=start_periods=1:start_threshold=-45dB'
        ff('-i', src, '-af', f"{trim},areverse,{trim},areverse,aresample=48000,loudnorm=I={vo.get('lufs', -18)}:TP=-2:LRA=7,aresample=48000", '-ac', '2', dst)
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', dst],
                                 capture_output=True, text=True, check=True).stdout)
        w = l.get('window')
        print(f"t{i:02d} {d:4.2f}s / window {w}s  {'fits' if w is None or d <= w else 'TOO LONG'}")
        ms = int(l['t'] * 1000); vin += ['-i', dst]; vf += f'[{i - 1}]adelay={ms}|{ms}[v{i}];'; lab += f'[v{i}]'
    track = os.path.join(work, 'vo_track.wav')
    ff(*vin, '-filter_complex', f"{vf}{lab}amix=inputs={len(lines)}:normalize=0,apad=whole_dur={D},atrim=duration={D},"
       f"highpass=f=80,acompressor=threshold=-20dB:ratio=3,volume={vo.get('boost', 2.0)}[o]", '-map', '[o]', track)
    k = len(inputs) // 2; inputs += ['-i', track]
    graph += (f"[{k}]asplit=2[vo][sc];{bed}[sc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
              f"[duck][vo]amix=inputs=2:normalize=0,")
else:
    graph += f"{bed}"
graph += 'alimiter=limit=0.9,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[o]'

mix = os.path.join(work, 'final_mix.wav')
ff(*inputs, '-filter_complex', graph, '-map', '[o]', '-ac', '2', mix)
ff('-i', P(C['video']), '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-shortest', P(C['out']))
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', P(C['out']), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print('saved:', C['out'], '|', ' '.join(l.strip() for l in r.split('Summary:')[-1].splitlines() if l.strip().startswith(('I:', 'Peak:'))))
