#!/usr/bin/env bash
# Build KDE Store release tarballs into dist/ (gitignored).
# Layout per kpackagetool: tarball root == single top-level dir (the plugin Id),
# or the bare .colors file for color schemes.
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$REPO/dist"
rm -rf "$DIST"
mkdir -p "$DIST"
cd "$REPO" || exit 1

# 1. Global themes (Plasma/LookAndFeel)
for id in com.rosepine.main com.rosepine.moon com.rosepine.dawn; do
  tar czf "$DIST/$id.tar.gz" -C look-and-feel "$id" || exit 1
done
# 2. Plasma styles (desktoptheme/<style-id> as top dir)
for s in rosepine rosepine-moon rosepine-dawn; do
  tar czf "$DIST/desktoptheme-$s.tar.gz" -C desktoptheme "$s" || exit 1
done
# 3. Color schemes (bare .colors files)
for f in color-schemes/*.colors; do
  cp "$f" "$DIST/" || exit 1
done
# 4. Aurorae window decorations (<Theme> as top dir)
for t in RosePine RosePineMoon RosePineDawn; do
  tar czf "$DIST/aurorae-$t.tar.gz" -C aurorae/themes "$t" || exit 1
done
# 5. GTK themes (<Theme> as top dir)
for t in RosePine RosePineMoon RosePineDawn; do
  tar czf "$DIST/gtk-$t.tar.gz" -C gtk/themes "$t" || exit 1
done
echo "=== dist/ ==="
ls -l "$DIST"
