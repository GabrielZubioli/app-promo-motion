#!/usr/bin/env bash
# Contact sheet of review stills with the time written on each frame (ffmpeg only, no Pillow).
#   bash sheet.sh <stills dir from render.mjs (files like 1.20.jpg)> <out.jpg> [COLSxROWS, default 6x3]
set -e
DIR="$1"; OUT="$2"; GRID="${3:-6x3}"; C=${GRID%x*}; R=${GRID#*x}
TMP=$(mktemp -d)
FONT=""; for c in /c/Windows/Fonts/arial.ttf /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /System/Library/Fonts/Supplemental/Arial.ttf; do
  [ -f "$c" ] && FONT=":fontfile=${c#/c}" && break; done   # Windows: /Windows/... (current drive) avoids the "C:" colon in the filter
i=0
while read -r t; do
  f="$DIR/$t.jpg"
  ffmpeg -v error -y -i "$f" -vf "scale=360:-2,drawbox=y=0:w=iw:h=44:color=black@0.6:t=fill,drawtext=text='${t}s':x=12:y=8:fontsize=28:fontcolor=white$FONT" "$TMP/$(printf %03d $i).png"
  i=$((i + 1))
done < <(ls "$DIR" | sed -n 's/\.jpg$//p' | sort -g | head -n $((C * R)))
ffmpeg -v error -y -framerate 1 -i "$TMP/%03d.png" -vf "tile=${C}x${R}:padding=6:color=0x111111" -frames:v 1 -q:v 3 "$OUT"
rm -rf "$TMP"; echo "sheet -> $OUT ($i frames)"
