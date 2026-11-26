// Optional: realistic sound effects with ElevenLabs (text to sound effect), for sounds the synth kit can't make convincing (water, real objects).
//   node --env-file=.env.local sfx_elevenlabs.mjs <out dir> "name|description in English" ["name2|..."] [--dur 1.2] [--n 3]
// Writes <name>-1.mp3 ... <name>-N.mp3; pick the one with a single clean event and pass the folder to mix.py as another --lib.
// Needs ELEVENLABS_API_KEY in the environment (commercial use needs a paid plan). No account? Use the synth kit, or any
// sound you have the rights to (drop .wav/.mp3 files in a folder and pass it with --lib).
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); if (i < 0) return d; const v = args[i + 1]; args.splice(i, 2); return v; };
const DUR = +opt('--dur', 1.2), N = +opt('--n', 3), [out, ...jobs] = args, key = process.env.ELEVENLABS_API_KEY;
if (!out || !jobs.length) { console.error('usage: node sfx_elevenlabs.mjs <dir> "name|description" [...] [--dur 1.2] [--n 3]'); process.exit(1); }
if (!key) { console.error('ELEVENLABS_API_KEY not set (run with node --env-file=.env.local). Without it, use the synth kit or your own sound files.'); process.exit(1); }
mkdirSync(out, { recursive: true });
for (const job of jobs) { const [name, text] = job.split('|');
  for (let k = 1; k <= N; k++) {
    const res = await fetch('https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128', { method: 'POST', headers: { 'xi-api-key': key, 'content-type': 'application/json' },
      body: JSON.stringify({ text: `${text}, isolated, no background, no music`, duration_seconds: DUR, prompt_influence: 0.7 }) });
    if (!res.ok) { console.error(`${res.status}: ${(await res.text()).slice(0, 300)}`); process.exit(1); }
    writeFileSync(join(out, `${name}-${k}.mp3`), Buffer.from(await res.arrayBuffer())); console.log('ok', `${name}-${k}`); } }
