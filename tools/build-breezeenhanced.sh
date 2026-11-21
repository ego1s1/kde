#!/usr/bin/env bash
# Build + install BreezeEnhanced with Rosé Pine macOS buttons (user-local).
# Upstream: https://github.com/tsujan/BreezeEnhanced (V6.8 == KWin 6.8).
# Colors: tools/recolor-breezeenhanced.py (Rose Pine love/gold/pine/foam).
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/kwin/decoration/rose-pine"
BUILD="$REPO/.build/breeze-rosepine"
PREFIX="$HOME/.local"

for t in cmake g++ make; do
  command -v "$t" >/dev/null 2>&1 || {
    echo "MISSING: $t -- run: sudo pacman -S cmake extra-cmake-modules"
    exit 1
  }
done
[ -d "$SRC" ] || { echo "MISSING: $SRC (vendored fork)"; exit 1; }
# Guard: the vendored fork must already carry the Rose Pine recolor.
# To refresh from upstream: copy the upstream BreezeEnhanced sources over the
# fork (keep .git out), then run: python3 tools/recolor-breezeenhanced.py <fork>
# and re-apply the KPlugin Id/Name fix below.
if grep -rq "QColor(255, 92, 87)\|QColor(40, 211, 63)\|QColor(243, 176, 43)" "$SRC/breezebutton.cpp"; then
  echo "UPSTREAM COLORS PRESENT in $SRC/breezebutton.cpp -- re-run recolor-breezeenhanced.py on the fork first"
  exit 1
fi
rm -rf "$BUILD"
mkdir -p "$BUILD"
cp -r "$SRC/." "$BUILD/"
python3 - "$BUILD/breezeenhanced.json" <<'EOF'
import json, sys
p = sys.argv[1]
md = json.load(open(p))
# KF6 requires embedded Id to match the .so filename (or be absent).
md["KPlugin"].pop("Id", None)
md["KPlugin"]["Name"] = "Rose Pine Enhanced"
md["KPlugin"]["Description"] = "Breeze-style window decoration with Rosé Pine traffic-light buttons"
json.dump(md, open(p, "w"), indent=4, ensure_ascii=False)
print("metadata: Id dropped, Name set")
EOF

cmake -S "$BUILD" -B "$BUILD/build" \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF \
  -DKDE_INSTALL_USE_QT_SYS_PATHS=OFF || exit 1
cmake --build "$BUILD/build" -j"$(nproc)" || exit 1
cmake --install "$BUILD/build" || exit 1

echo "installed. verify with: kwin-applywindowdecoration --list-themes | grep -i -E 'rose|enhanced|breeze'"
echo "apply with: kwin-applywindowdecoration BreezeEnhanced"
