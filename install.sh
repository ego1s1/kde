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

apply_variant() {
  local v="$1" lfid aurorae
  case "$v" in
    main) lfid=com.rosepine.main; aurorae=RosePine ;;
    moon) lfid=com.rosepine.moon; aurorae=RosePineMoon ;;
    dawn) lfid=com.rosepine.dawn; aurorae=RosePineDawn ;;
  esac
  lookandfeeltool -a "$lfid"
  # lookandfeeltool strips the __aurorae__svg__ prefix KWin needs and may
  # write kwinrc asynchronously: settle, then force v2 engine + prefixed
  # theme, and verify the values stuck before reconfiguring.
  sleep 2
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae.v2
  kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme "__aurorae__svg__$aurorae"
  sleep 1
  cur="$(kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme)"
  if [ "$cur" != "__aurorae__svg__$aurorae" ]; then
    sleep 3
    kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae.v2
    kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme "__aurorae__svg__$aurorae"
    sleep 1
  fi
  qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true
  echo "applied: $lfid + aurorae $aurorae"
}

if [ "$VAR" = all ]; then
  for v in main moon dawn; do install_variant "$v"; done
  apply_variant moon
else
  install_variant "$VAR"
  apply_variant "$VAR"
fi
echo "Verify with: lookandfeeltool -l | grep rose; kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme"
