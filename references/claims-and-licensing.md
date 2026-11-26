# Truth and licensing

## Claims
- Every number and every sentence (on screen and in the voice) needs a source: the app itself, its code/database, or its store page. Note the source of each.
- A feature the interface hints at but that isn't implemented stays out.
- No promised results, "best", "#1", ratings, testimonials or user counts unless real and provable.
- Demo data must be coherent across screens (the same 48-minute workout everywhere; a streak that ends today; totals that add up) and marked as demo in the storyboard.
- Only name the stores where the app really is. "Free", "no ads", "works offline": confirm in the current version before publishing.

## Images and video
- App screenshots: a demo account with fictitious data (it can be created through the app's own sign-up); never real personal data.
- Third-party images inside screenshots (stock exercise photos, etc.): replace with the client's own material.
- Photos (recipes, products): check the licence in the app's credits; CC0/public domain or owned.
- Stock video with people: many licences forbid implying the person endorses the product; prefer paid stock with model releases.
- No generated realistic humans.
- 3D models, icons, fonts: check the licence (the template's fonts are OFL, licences included in `assets/template/fonts/`).

## Music
- "No copyright" channels don't guarantee advertising use; find the licence at the official source. Don't rip from YouTube.
- Paid libraries (Epidemic Sound, Artlist) or libraries with a commercial licence work; paid ads sometimes need a specific plan.

## Voices and sound effects
- TTS voices: check the provider's terms for commercial use (ElevenLabs: paid plan; OpenAI: follow their usage policies and disclose AI voice where required).
- Sound effects made by `synth_sfx.py` are generated from scratch and free to use.
- Avoid CC BY-SA sounds in ads (attribution + share-alike).

## Store badge
- Use the official Google Play / App Store badge in the final video (follow each store's badge guidelines); the drawn placeholder is for drafts only.
