// Checks everything the pipeline needs and says how to fix what is missing.
//   node doctor.mjs [--no-gpu-test]
import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url)), os = process.platform, rows = [];
// no shell: on Windows cmd.exe mangles the quotes of `python -c "..."`, which made a working numpy look missing
const run = (cmd, args) => { try { const r = spawnSync(cmd, args, { encoding: 'utf8' }); return r.status === 0 ? (r.stdout || r.stderr || '').trim() : null; } catch { return null; } };
const ok = (name, good, detail, fix, required = true) => rows.push({ name, good, detail, fix, required });

const nodeMajor = +process.versions.node.split('.')[0];
ok('Node.js 18+', nodeMajor >= 18, `v${process.versions.node}`, 'Install Node.js 18 or newer: https://nodejs.org');
const ff = run('ffmpeg', ['-version']), fp = run('ffprobe', ['-version']);
ok('ffmpeg + ffprobe', !!ff && !!fp, ff ? ff.split('\n')[0] : 'not found', os === 'win32' ? 'winget install Gyan.FFmpeg  (or https://ffmpeg.org) and reopen the terminal' : os === 'darwin' ? 'brew install ffmpeg' : 'sudo apt install ffmpeg');
const chrome = process.env.CHROME || ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium',
  'C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].find(p => existsSync(p));
ok('Google Chrome / Chromium', !!chrome, chrome || 'not found', 'Install Google Chrome, or set CHROME=/path/to/chrome');
let py = null; for (const c of os === 'win32' ? ['python', 'py', 'python3'] : ['python3', 'python']) { const v = run(c, ['--version']); if (v) { py = c; break; } }
ok('Python 3', !!py, py ? run(py, ['--version']) : 'not found', 'Install Python 3: https://python.org');
const np = py && run(py, ['-c', 'import numpy, scipy; print(numpy.__version__, scipy.__version__)']);
ok('numpy + scipy (music analysis, sound kit, mixer)', !!np, np ? `numpy/scipy ${np}` : 'missing', `${py || 'python'} -m pip install numpy scipy   (or a virtualenv)`);
const bash = run('bash', ['--version']);
ok('bash (contact sheets)', !!bash, bash ? bash.split('\n')[0] : 'not found', os === 'win32' ? 'Git for Windows includes bash' : 'install bash', false);
// narration / realistic sound effects: all optional
ok('ElevenLabs key (optional: narration + realistic SFX)', !!process.env.ELEVENLABS_API_KEY, process.env.ELEVENLABS_API_KEY ? 'ELEVENLABS_API_KEY set' : 'not set (fine: use another provider or no narration)', 'Put ELEVENLABS_API_KEY in a .env.local and run with node --env-file=.env.local', false);
ok('OpenAI key (optional: narration)', !!process.env.OPENAI_API_KEY, process.env.OPENAI_API_KEY ? 'OPENAI_API_KEY set' : 'not set', 'Put OPENAI_API_KEY in a .env.local', false);
const sysVoice = os === 'win32' ? run('powershell', ['-NoProfile', '-Command', 'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices().Count'])
  : os === 'darwin' ? run('say', ['-v', '?']) : run('espeak-ng', ['--version']);
ok('System voice (optional: free guide narration)', !!sysVoice, sysVoice ? 'available' : 'not found', os === 'linux' ? 'sudo apt install espeak-ng' : 'built into the OS', false);

// GPU / WebGL: render one still of the template
if (!process.argv.includes('--no-gpu-test') && chrome && nodeMajor >= 18) {
  const out = mkdtempSync(join(tmpdir(), 'apm-doctor-')), r = spawnSync(process.execPath, [join(here, 'render.mjs'), 'stills', join(here, '..', 'assets', 'template', 'index.html'), out, '5', '--gpu'], { encoding: 'utf8', timeout: 120000 });
  const good = r.status === 0 && readdirSync(out).length === 1; rmSync(out, { recursive: true, force: true });
  ok('WebGL render test (template, --gpu)', good, good ? 'rendered a frame' : (r.stderr || r.stdout || 'failed').trim().split('\n').pop(), 'Update the GPU driver / Chrome; as a last resort render without --gpu (much slower)');
}
let bad = 0;
for (const r of rows) { const mark = r.good ? 'OK  ' : r.required ? 'FAIL' : 'opt '; if (!r.good && r.required) bad++; console.log(`${mark}  ${r.name.padEnd(52)} ${r.detail}`); if (!r.good) console.log(`      -> ${r.fix}`); }
console.log(bad ? `\n${bad} required item(s) missing.` : '\nReady to make videos.'); process.exit(bad ? 1 : 0);
