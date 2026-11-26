# Builds the sound-effect map automatically from the page's events, using the sound dictionary (one right sound per kind of element).
#   python build_cues.py events.json cues.json [--map my-map.json]
# Event names start with a category; the first part decides the sound:
#   text.*   words / headlines appearing      -> Text In
#   tap.*    click, tap, selection            -> Click
#   ok.*     something worked (a check)       -> Confirm
#   done.*   a bigger completion              -> Success
#   swap.*   a screen sliding sideways        -> Swipe
#   whoosh.* a bigger move / transition       -> Whoosh 1-3 (rotating)
#   flip.*   a card / logo turning over       -> Card Flip + Whoosh 2
#   land.*   something landing                -> Soft Hit
#   impact.* a big hit                        -> Boom
#   ui.*     an interface element appears     -> Pop
#   info.*   a stat / label rising into place -> Info Up
#   panel.*  a card / indicator landing       -> Panel In
#   count.*  a number counting up             -> Count Digital S
#   spin.*   a carousel / wheel turning       -> Ratchet clicks over 1.2 s
#   type.*   text being typed                 -> keys, 12 strokes
#   brand.*  the brand moment (logo)          -> Chime
#   music.*, mute.*                           -> no sound
# Repeats of the same category vary the pitch a little, so nothing sounds copy-pasted. --map overrides/extends the table.
import json, sys, argparse
from collections import defaultdict

MAP = {
    'text':   [dict(file='Text In', db=-9, align='start')],
    'tap':    [dict(file='Click', db=-6)],
    'ok':     [dict(file='Confirm', db=-6)],
    'done':   [dict(file='Success', db=-5)],
    'swap':   [dict(file='Swipe', db=-7)],
    'whoosh': [dict(file='Whoosh {r}', db=-8, align='start')],
    'flip':   [dict(file='Card Flip', db=-6), dict(file='Whoosh 2', db=-10, align='start')],
    'land':   [dict(file='Soft Hit', db=-5)],
    'impact': [dict(file='Boom', db=-3)],
    'ui':     [dict(file='Pop', db=-9)],
    'info':   [dict(file='Info Up', db=-5, offset=0.18)],
    'panel':  [dict(file='Panel In', db=-5, offset=0.1)],
    'count':  [dict(file='Count Digital S', db=-5, align='start')],
    'spin':   [dict(file='Ratchet', db=-9, repeat=14, every=0.085)],
    'type':   [dict(file='Key {abc}', db=-10, repeat=12, every=0.065)],
    'brand':  [dict(file='Chime', db=-6)],
    'music':  [], 'mute': [],
}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('events'); ap.add_argument('out'); ap.add_argument('--map')
    a = ap.parse_args(); m = dict(MAP)
    if a.map: m.update(json.load(open(a.map, encoding='utf-8')))
    events = json.load(open(a.events, encoding='utf-8')); seen = defaultdict(int); cues = []; unknown = []
    for e in events:
        cat = e['name'].split('.')[0]
        if cat not in m: unknown.append(e['name']); continue
        k = seen[cat]; seen[cat] += 1
        for spec in m[cat]:
            s = dict(spec); rep = s.pop('repeat', 1); every = s.pop('every', 0)
            for j in range(rep):
                c = dict(event=e['name'], file=s['file'].replace('{r}', str(1 + k % 3)).replace('{abc}', 'ABCBAC'[j % 6]), db=s.get('db', -8), align=s.get('align', 'peak'))
                off = s.get('offset', 0) + j * every
                if off: c['offset'] = round(off, 3)
                p = 1 + 0.04 * (k % 4) if rep == 1 else 0.95 + 0.04 * (j % 5)
                if abs(p - 1) > 1e-6: c['pitch'] = round(p, 2)
                cues.append(c)
    json.dump(cues, open(a.out, 'w', encoding='utf-8'), indent=1)
    print(f'{len(cues)} cues from {len(events)} events -> {a.out}')
    if unknown: print('no sound for (unknown category):', ', '.join(unknown))

if __name__ == '__main__':
    main()
