// Everything about the app lives here. index.html reads window.PROJECT; a first cut needs no edits to index.html.
// Text marked *like this* is the key word: accent colour, script face, glow and an underline that draws itself.
window.PROJECT = {
  app: {
    name: 'Your App',
    tagline: 'One line that says what it does.',
    url: 'yourapp.com',
    store: 'Google Play',          // 'Google Play' | 'App Store' | 'App Store & Google Play' | '' (no badge)
    badgeLabel: '',                // optional text above the store name (default: GET IT ON / DOWNLOAD ON THE / AVAILABLE ON)
  },
  // Brand colours (hex). accent = main brand colour; warm = a second colour for highlights; bg/glow = dark background and its centre glow.
  colors: { accent: '#01D798', warm: '#F99B45', bg: '#020306', glow: '#0b261c', text: '#ffffff', muted: '#9aa3a0' },
  // Font families declared in index.html (@font-face, files in fonts/). Swap the files and names for the brand's own fonts.
  fonts: { sans: 'Inter', script: 'Kaushan Script' },
  logo: { src: 'assets/logo.svg', width: 560 },      // transparent SVG or PNG
  // Music: bpm and the drop come from `analyze_music.py`. drop = seconds into the TRACK where it hits; the logo is revealed exactly there.
  music: { bpm: 120, drop: 4.0 },
  // Text intro before the drop: each word appears on the beat (with the narration, if any); sizes in px (make them very unequal).
  // Leave words empty ([]) for a short intro with only the falling dot.
  intro: { words: ['Your', '*new*', 'favourite', 'app.'], sizes: [110, 300, 150, 240] },
  // App screens shown inside the phone, in order. Use real portrait screenshots (about 9:19.5). beats = how long each one stays.
  screens: [
    { image: 'assets/screen-1.svg', title: ['Plan your', '*day.*'], beats: 6 },
    { image: 'assets/screen-2.svg', title: ['Track every', '*habit.*'], beats: 6 },
    { image: 'assets/screen-3.svg', title: ['See your', '*progress.*'], beats: 6 },
  ],
  outro: { cta: 'Download *free.*', typeUrl: true },
};
