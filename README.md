# app-promo-motion

<p align="center"><img src="docs/demo.gif" width="240" alt="Demo: a promo for a fictional app made with the template"><br><sub>Made with the neutral template for a fictional app "Budgie" (silent preview; the real output has music, effects and narration).</sub></p>

A Claude skill that makes professional motion-design promo videos for apps - vertical 9:16 for Reels, TikTok and Shorts - entirely
in code, rendered frame by frame and locked to the beats of a song.

What you get: kinetic 3D text, transitions where one element turns into the next, a continuous 3D camera with depth of field and
motion blur, a background grid that travels between screens, mixed typography, a sound effect for every element, optional narration,
and a final mix at the platforms' loudness. Delivered in 1080p, 2K or 4K.

Nothing here generates video with AI: the animation is code you can read and change, using your app's real logo, colours, fonts and
screenshots. A note like "hold the check a bit longer" becomes one changed number and a new render.

## The two non-negotiable rules
1. **Every scene becomes the next through its elements** (a shape, a card, a number, a word, a colour or the device itself turns into
   something in the next scene) - no cuts, fades or plain slides.
2. **Every screen has its own idea and nothing repeats** - a different presentation and a different transition for each scene. The
   template's "phone + headline + push" is only a skeleton to start from. Ideas: `references/design-rules.md` §8.

## Install
Claude Code:

```bash
git clone https://github.com/GabrielZubioli/app-promo-motion ~/.claude/skills/app-promo-motion
```

Or download the repository as a zip and put the folder in your skills directory (Claude Code: `~/.claude/skills/`; claude.ai: upload it
as a skill).

Requirements:
- Node.js 18+, ffmpeg, Google Chrome (or Chromium), Python 3 with `numpy` and `scipy` (`pip install numpy scipy`).
- A GPU that Chrome can use for WebGL (any normal laptop/desktop GPU).
- Optional: an ElevenLabs or OpenAI API key for narration / realistic effects. Without them you can use the free system voice,
  your own recordings or no narration at all.

Run `/app-promo-motion doctor` to check everything.

## Commands
| Command | What it does |
|---|---|
| `/app-promo-motion` | the whole guided flow, with approval stops |
| `help` | lists commands and the project's progress |
| `doctor` | checks the machine and explains how to fix what's missing |
| `new <folder> --name "App"` | creates a project from the neutral template |
| `brief` | collects your app's material and fills the project config (colours, fonts, logo, screenshots, features, music) |
| `storyboard` | proposes the scenes and transitions for approval |
| `music <file>` | finds tempo, beats and the drop; the logo is revealed on the drop |
| `build` | animates the approved storyboard |
| `review` | renders stills of key moments and transitions and checks them |
| `preview` | 1080p video with sound, plus a light copy to share |
| `sound` | sound effects mapped to every element |
| `voice [provider]` | narration: `none`, `files` (your recordings / any TTS), `system`, `elevenlabs`, `openai` |
| `mix` | final audio mix (music + effects + narration) at −14 LUFS |
| `render 1080p\|2k\|4k` | final render, checked frame by frame |
| `notes "..."` | applies a round of notes as a new version |
| `caption [platform]` | writes the post text for the video |

## Configuring a project (no code needed for a first cut)
Everything about your app lives in `video/project.js`: name, tagline, site, store, colours, fonts, logo, music tempo and drop, intro
words and their sizes, the screenshots and their headlines, and the call to action. Open `video/index.html` in Chrome to watch the
animation live while you edit.

## How it works
- `video/index.html` draws every frame on a canvas; `scripts/render.mjs` drives headless Chrome frame by frame and pipes to ffmpeg.
- Three depth planes plus 3D panels are composed by a small WebGL renderer (`gl3d.js`) through one moving camera.
- Every event in the page has a name (`text.title.2`, `swap.screen.3`…); `build_cues.py` turns them into a sound map and `mix.py`
  places each sound to the millisecond.

## Licence
MIT - see `LICENSE`. Bundled fonts (Inter, Kaushan Script) are under the SIL Open Font License; see `THIRD_PARTY_NOTICES.md`.
Music, voices, logos and screenshots you add are under their own licences - see `references/claims-and-licensing.md`.
