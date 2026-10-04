#!/bin/bash
# Regenerates the help screenshots with demo data (never real user data) using headless Edge on macOS.
# Usage: tools/help-screenshots/make_shots.sh   (run from anywhere; needs python3 + Pillow, Microsoft Edge)
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$(mktemp -d)"; SITE="$WORK/site"; mkdir -p "$SITE"
for f in catalog.json manifest.json icon-192.png icon-512.png help.html astronomy.browser.min.js; do ln -sf "$ROOT/$f" "$SITE/$f"; done
python3 - "$ROOT" "$SITE" <<'PY'
import sys
root,site=sys.argv[1:3]
s=open(root+'/index.html',encoding='utf-8').read()
# index.html contains a second, literal "</body>" inside a JS string (planPrintHTML's
# print template) — a plain .replace() would inject a real </script> tag in the middle
# of the page's main <script> block via that string, which the HTML parser closes early
# regardless of JS string context, silently truncating most of the app's JS. Target only
# the last, real closing tag with rpartition instead.
head, sep, tail = s.rpartition('</body>')
s = head + '<script src="shot.js"></script>' + sep + tail
open(site+'/app.html','w',encoding='utf-8').write(s)
PY
cp "$ROOT/tools/help-screenshots/shot.js" "$SITE/shot.js"
pkill -f "http.server 8090" 2>/dev/null || true
(cd "$SITE" && python3 -m http.server 8090 >/dev/null 2>&1 & echo $! > "$WORK/srv.pid"); sleep 1
EDGE="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
shoot(){ # scene width height
  local out="$WORK/raw_$1.png"
  "$EDGE" --headless=new --disable-gpu --no-first-run --lang=en-US --user-data-dir="$WORK/prof_$1" --window-size=$2,$3 \
    --force-device-scale-factor=2 --virtual-time-budget=40000 --screenshot="$out" "http://localhost:8090/app.html?s=$1" >/dev/null 2>&1 &
  for i in $(seq 1 70); do sleep 2; [ -s "$out" ] && { sleep 2; break; }; done
  pkill -f "user-data-dir=$WORK/prof_$1" || true   # headless Edge does not exit by itself
}
shoot locations 820 700; shoot locform 820 1500; shoot newsearch 820 1800; shoot list 820 1300
shoot detailtop 820 1900; shoot sky 820 1800; shoot mytargets 820 1400; shoot info 820 1500
shoot nightinfo 820 800; shoot settings 820 1300
python3 - "$WORK" "$ROOT/help-img" <<'PY'
import sys
from PIL import Image
work,dest=sys.argv[1:3]
crops=[('locations','locations',0,750,72),('location-mask','locform',1095,2205,72),('new-target-list','newsearch',0,2850,72),
('target-list','list',0,1330,72),('target-detail','detailtop',0,2075,66),
('framing','sky',0,1950,62),('my-targets','mytargets',0,1950,68),('best-season','info',1100,1720,72),('object-info','info',1710,2830,66),
('night-info','nightinfo',0,800,72),('backup','settings',1625,2115,72)]
for name,raw,y0,y1,q in crops:
    im=Image.open(f'{work}/raw_{raw}.png').convert('RGB'); c=im.crop((0,y0,im.width,min(y1,im.height)))
    c=c.resize((900,round(c.height*900/c.width)),Image.LANCZOS); c.save(f'{dest}/{name}.jpg',quality=q,optimize=True)
PY
pkill -f "http.server 8090" 2>/dev/null || true   # $! above is the subshell, not python; a leftover server would serve a stale site on the next run
echo "Done. Review help-img/*.jpg, then bump help version + CACHE_NAME."
