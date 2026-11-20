#!/usr/bin/env bash
# Install Rose Pine KDE global themes (main/moon/dawn).
# Usage: ./install.sh [main|moon|dawn|all]
set -u
REPO="$(cd "$(dirname "$0")" && pwd)"
VAR="${1:-all}"

install_variant() {
  local v="$1" slug style lfid
  case "$v" in
    main) slug=RosePine; style=rosepine; lfid=com.rosepine.main ;;
    moon) slug=RosePineMoon; style=rosepine-moon; lfid=com.rosepine.moon ;;
    dawn) slug=RosePineDawn; style=rosepine-dawn; lfid=com.rosepine.dawn ;;
  esac
  local aurorae
  case "$v" in
    main) aurorae=RosePine ;; moon) aurorae=RosePineMoon ;; dawn) aurorae=RosePineDawn ;;
  esac
  echo "=== $v ($slug) ==="
  mkdir -p ~/.local/share/color-schemes
  cp "$REPO/color-schemes/$slug.colors" ~/.local/share/color-schemes/
  echo "colorscheme: $slug"
  mkdir -p ~/.local/share/plasma/desktoptheme
  rm -rf ~/.local/share/plasma/desktoptheme/$style
  cp -r "$REPO/desktoptheme/$style" ~/.local/share/plasma/desktoptheme/
  echo "desktoptheme: $style"
  mkdir -p ~/.local/share/aurorae/themes
  rm -rf ~/.local/share/aurorae/themes/$aurorae
  cp -r "$REPO/aurorae/themes/$aurorae" ~/.local/share/aurorae/themes/
  echo "aurorae: $aurorae"
  kpackagetool6 -t Plasma/LookAndFeel -r "$lfid" >/dev/null 2>&1 || true
  kpackagetool6 -t Plasma/LookAndFeel -i "$REPO/look-and-feel/$lfid" 2>&1 | tail -n 2
  echo "look-and-feel: $lfid"
}

if [ "$VAR" = all ]; then
  for v in main moon dawn; do install_variant "$v"; done
else
  install_variant "$VAR"
fi
echo "Apply with: lookandfeeltool -a com.rosepine.<main|moon|dawn>"
