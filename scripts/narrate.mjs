// Narration with a pluggable provider. Writes one file per line (tNN.wav, 48 kHz) that mix_final.py places on the timeline.
//   node [--env-file=.env.local] narrate.mjs vo.json <out dir> [--provider none|files|system|elevenlabs|openai]   (ONLY=3,5 regenerates just those lines)
// vo.json: { "provider": "system", "voice": "", "language": "en",
//            "lines": [ { "text": "Your new favourite app.", "t": 0.5, "window": 2.5, "style": "warm", "stability": 0.5 }, ... ] }
//   none       no narration: nothing to do (leave "vo" out of mix.json)
//   files      bring your own recordings (any tool, any TTS, your own voice): put t01.wav/.mp3, t02... in <out dir>; this converts and checks them
//   system     free, offline guide voice: Windows SAPI, macOS `say`, Linux `espeak-ng` ("voice" = an installed voice name, optional)
//   elevenlabs ELEVENLABS_API_KEY; "voice" = voice id; "model" (default eleven_multilingual_v2; v3 models understand [warmly]-style tags)
//   openai     OPENAI_API_KEY; "voice" (default alloy); "model" (default gpt-4o-mini-tts); "style" becomes the speaking instruction
// Keys come from the environment only. Never write them in files that get shared.
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';

const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); if (i < 0) return null; const v = args[i + 1]; args.splice(i, 2); return v; };
const forced = opt('--provider'), [cfgPath, outDir] = args;
if (!cfgPath || !outDir) { console.error('usage: node narrate.mjs vo.json <out dir> [--provider none|files|system|elevenlabs|openai]'); process.exit(1); }
const cfg = JSON.parse(readFileSync(cfgPath, 'utf8')), provider = forced || cfg.provider || 'none', L = cfg.lines || [], out = resolve(outDir);
const ONLY = process.env.ONLY ? process.env.ONLY.split(',').map(Number) : null, plain = s => s.replace(/\[[^\]]*\]\s*/g, '').trim();
const n2 = i => String(i + 1).padStart(2, '0'), ff = (...a) => { const r = spawnSync('ffmpeg', ['-v', 'error', '-y', ...a]); if (r.status) throw new Error('ffmpeg: ' + r.stderr); };
const dur = f => +spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], { encoding: 'utf8' }).stdout.trim();
const toWav = (src, i) => { const dst = join(out, `t${n2(i)}.wav`); if (resolve(src) !== dst) ff('-i', src, '-ar', '48000', '-ac', '1', dst); return dst; };
if (provider === 'none') { console.log('provider "none": no narration. Leave "vo" out of mix.json.'); process.exit(0); }
mkdirSync(out, { recursive: true });

async function line(i) {
  const l = L[i], text = l.text, tmp = join(tmpdir(), `apm-vo-${process.pid}-${i}`);
  if (provider === 'files') { const src = ['wav', 'mp3', 'm4a', 'aiff', 'flac'].map(e => join(out, `t${n2(i)}.${e}`)).find(existsSync); if (!src) throw new Error(`missing recording t${n2(i)}.wav/.mp3 in ${out}`); if (!src.endsWith('.wav')) toWav(src, i); return; }
  if (provider === 'system') {
    if (process.platform === 'win32') { const ps = `Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; ${cfg.voice ? `$s.SelectVoice(${JSON.stringify(cfg.voice)});` : `$v = $s.GetInstalledVoices() | ? { $_.VoiceInfo.Culture.Name -like ${JSON.stringify((cfg.language || 'en') + '*')} } | select -First 1; if ($v) { $s.SelectVoice($v.VoiceInfo.Name) };`} $s.SetOutputToWaveFile(${JSON.stringify(tmp + '.wav')}); $s.Speak(${JSON.stringify(plain(text))}); $s.Dispose()`;
      const r = spawnSync('powershell', ['-NoProfile', '-Command', ps], { encoding: 'utf8' }); if (r.status) throw new Error(r.stderr); toWav(tmp + '.wav', i); unlinkSync(tmp + '.wav'); return; }
    if (process.platform === 'darwin') { const r = spawnSync('say', [...(cfg.voice ? ['-v', cfg.voice] : []), '-o', tmp + '.aiff', plain(text)]); if (r.status) throw new Error('say failed'); toWav(tmp + '.aiff', i); unlinkSync(tmp + '.aiff'); return; }
    const r = spawnSync('espeak-ng', ['-v', cfg.voice || cfg.language || 'en', '-w', tmp + '.wav', plain(text)]); if (r.status) throw new Error('espeak-ng failed (sudo apt install espeak-ng)'); toWav(tmp + '.wav', i); unlinkSync(tmp + '.wav'); return;
  }
  let res;
  if (provider === 'elevenlabs') { const key = process.env.ELEVENLABS_API_KEY; if (!key) throw new Error('ELEVENLABS_API_KEY not set (use node --env-file=.env.local)'); if (!cfg.voice) throw new Error('set "voice" to an ElevenLabs voice id');
    const model = cfg.model || 'eleven_multilingual_v2', tags = /v3|v4/.test(model);
    res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${cfg.voice}?output_format=mp3_44100_128`, { method: 'POST', headers: { 'xi-api-key': key, 'content-type': 'application/json' },
      body: JSON.stringify({ text: tags ? text : plain(text), model_id: model, ...(cfg.language ? { language_code: cfg.language } : {}), voice_settings: { stability: l.stability ?? 0.5, similarity_boost: 0.8 },
        previous_text: i > 0 ? plain(L[i - 1].text) : undefined, next_text: i < L.length - 1 ? plain(L[i + 1].text) : undefined }) });
  } else if (provider === 'openai') { const key = process.env.OPENAI_API_KEY; if (!key) throw new Error('OPENAI_API_KEY not set (use node --env-file=.env.local)');
    res = await fetch('https://api.openai.com/v1/audio/speech', { method: 'POST', headers: { authorization: `Bearer ${key}`, 'content-type': 'application/json' },
      body: JSON.stringify({ model: cfg.model || 'gpt-4o-mini-tts', voice: cfg.voice || 'alloy', input: plain(text), response_format: 'mp3', ...(l.style ? { instructions: `Speak ${l.style}. Language: ${cfg.language || 'auto'}.` } : {}) }) });
  } else throw new Error(`unknown provider "${provider}"`);
  if (!res.ok) throw new Error(`${provider} ${res.status}: ${(await res.text()).slice(0, 300)}`);
  writeFileSync(join(out, `t${n2(i)}.mp3`), Buffer.from(await res.arrayBuffer())); toWav(join(out, `t${n2(i)}.mp3`), i);
}
for (let i = 0; i < L.length; i++) { if (ONLY && !ONLY.includes(i + 1)) continue; await line(i);
  const d = dur(join(out, `t${n2(i)}.wav`)), w = L[i].window; console.log(`t${n2(i)}  ${d.toFixed(2)}s${w ? ` / window ${w}s ${d <= w ? 'fits' : 'TOO LONG'}` : ''}  ${plain(L[i].text)}`); }
console.log(`narration (${provider}) -> ${out}`);
