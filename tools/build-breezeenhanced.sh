#!/usr/bin/env bash
# Build + install BreezeEnhanced with Rosé Pine macOS buttons (user-local).
# Upstream: https://github.com/tsujan/BreezeEnhanced (V6.8 == KWin 6.8).
# Colors: tools/recolor-breezeenhanced.py (Rose Pine love/gold/pine/foam).
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
REF="$REPO/reference/BreezeEnhanced"
BUILD="$REPO/.build/breeze-rosepine"
PREFIX="$HOME/.local"

for t in cmake g++ make; do
  command -v "$t" >/dev/null 2>&1 || {
    echo "MISSING: $t -- run: sudo pacman -S cmake extra-cmake-modules"
    exit 1
  }
done
[ -d "$REF" ] || { echo "MISSING: $REF (reference clone)"; exit 1; }

rm -rf "$BUILD"
mkdir -p "$BUILD"
cp -r "$REF/." "$BUILD/"
python3 "$REPO/tools/recolor-breezeenhanced.py" "$BUILD" || exit 1
# KPluginFactory (KF6): embedded KPlugin Id must match the .so filename.
# breezeenhanced.json carries "Id": "org.kde.breezeenhanced" but the module
# installs as breezeenhanced.so -> factory refuses to create the instance.
# Sanctioned fix per the error message: drop the Id field (upstream bug).
python3 - "$BUILD/breezeenhanced.json" <<'EOF'
import json, sys
p = sys.argv[1]
md = json.load(open(p))
md["KPlugin"].pop("Id", None)
json.dump(md, open(p, "w"), indent=4)
print("stripped embedded KPlugin.Id")
EOF

cmake -S "$BUILD" -B "$BUILD/build" \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF \
  -DKDE_INSTALL_USE_QT_SYS_PATHS=OFF || exit 1
cmake --build "$BUILD/build" -j"$(nproc)" || exit 1
cmake --install "$BUILD/build" || exit 1

echo "installed. verify with: kwin-applywindowdecoration --list-themes | grep -i -E 'rose|enhanced|breeze'"
echo "apply with: kwin-applywindowdecoration org.kde.breezeenhanced"
