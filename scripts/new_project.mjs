// Creates a new video project from the neutral template.
//   node new_project.mjs <folder> [--name "App name"] [--force]
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2), opt = k => { const i = args.indexOf(k); if (i < 0) return null; const v = args[i + 1]; args.splice(i, 2); return v; };
const force = args.includes('--force'); if (force) args.splice(args.indexOf('--force'), 1);
const name = opt('--name'), dir = args[0];
if (!dir) { console.error('usage: node new_project.mjs <folder> [--name "App name"] [--force]'); process.exit(1); }
const here = dirname(fileURLToPath(import.meta.url)), tpl = join(here, '..', 'assets', 'template'), out = resolve(dir);
if (existsSync(out) && readdirSync(out).length && !force) { console.error(`${out} is not empty (use --force to copy the template into it anyway)`); process.exit(1); }
mkdirSync(out, { recursive: true }); cpSync(tpl, join(out, 'video'), { recursive: true });
cpSync(join(here, 'render.mjs'), join(out, 'video', 'render.mjs'));
mkdirSync(join(out, 'audio'), { recursive: true }); mkdirSync(join(out, 'material'), { recursive: true }); mkdirSync(join(out, 'renders'), { recursive: true });
if (name) { const p = join(out, 'video', 'project.js'); writeFileSync(p, readFileSync(p, 'utf8').replace("name: 'Your App'", `name: ${JSON.stringify(name)}`)); }
writeFileSync(join(out, 'audio', 'vo.json'), JSON.stringify({ provider: 'none', voice: '', language: 'en',
  lines: [{ text: 'Your new favourite app.', t: 0.5, window: 2.5, style: 'warm' }] }, null, 1));
writeFileSync(join(out, 'audio', 'mix.json'), JSON.stringify({ video: '../renders/preview-1080p-silent.mp4', out: '../renders/preview-1080p.mp4', duration: 20,
  music: { file: '../material/music.mp3', start: 0, volume: 0.8, fade_in: 0.4, fade_out: 0.9 }, sfx: { file: 'sfx.wav', volume: 2.15 } }, null, 1));
writeFileSync(join(out, '.gitignore'), '.env.local\nrenders/\naudio/_mix/\n');
writeFileSync(join(out, 'README.md'), `# ${name || 'App'} promo video

- \`video/project.js\`: app name, colours, fonts, logo, music bpm/drop, intro words, screens, call to action.
- \`video/index.html\`: the animation (scenes, timing, camera). Open it in Chrome to preview live.
- \`material/\`: the app's real material (logo, screenshots, music, photos). Copy what the video uses into \`video/assets/\`.
- \`audio/\`: sound effects, narration (\`vo.json\`), mix settings (\`mix.json\`).
- \`renders/\`: previews and final videos.

Keys for narration/effects go in \`.env.local\` (never in code): ELEVENLABS_API_KEY=... / OPENAI_API_KEY=...
`);
console.log(`Project created: ${out}
  video/index.html + project.js   the animation (open index.html in Chrome to watch it live)
  material/                       put the app's logo, screenshots and music here
  audio/vo.json, audio/mix.json   narration and mix settings
Next: fill video/project.js (or run /app-promo-motion brief).`);
