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
  mkdir -p ~/.local/share/themes
  rm -rf ~/.local/share/themes/$slug
  cp -r "$REPO/gtk/themes/$slug" ~/.local/share/themes/
  echo "gtk: $slug"
  kpackagetool6 -t Plasma/LookAndFeel -r "$lfid" >/dev/null 2>&1 || true
  kpackagetool6 -t Plasma/LookAndFeel -i "$REPO/look-and-feel/$lfid" 2>&1 | tail -n 2
  echo "look-and-feel: $lfid"
}

set_ini_key() {
  local file="$1" key="$2" value="$3"
  if command -v kwriteconfig6 >/dev/null 2>&1; then
    kwriteconfig6 --file "$file" --group Settings --key "$key" "$value"
  elif command -v python3 >/dev/null 2>&1; then
    python3 - "$file" "$key" "$value" <<'PY'
import configparser, sys
path, key, value = sys.argv[1:4]
cfg = configparser.ConfigParser()
cfg.optionxform = str
cfg.read(path)
if not cfg.has_section("Settings"):
    cfg.add_section("Settings")
cfg.set("Settings", key, value)
with open(path, "w") as f:
    cfg.write(f, space_around_delimiters=False)
PY
  else
    echo "warning: cannot update $file (need kwriteconfig6 or python3)"
  fi
}

apply_gtk() {
  local v="$1" slug dark
  case "$v" in
    main) slug=RosePine; dark=true ;;
    moon) slug=RosePineMoon; dark=true ;;
    dawn) slug=RosePineDawn; dark=false ;;
  esac
  if [ ! -d "$HOME/.local/share/themes/$slug" ]; then
    echo "gtk: $slug not installed (skipping)"
    return 0
  fi
  mkdir -p "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0"
  for ver in 3.0 4.0; do
    local ini="$HOME/.config/gtk-$ver/settings.ini"
    set_ini_key "$ini" gtk-theme-name "$slug"
    set_ini_key "$ini" gtk-application-prefer-dark-theme "$dark"
  done
  # GTK2 has no prefer-dark support; point it at the variant directly.
  if [ -f "$HOME/.gtkrc-2.0" ] && grep -q '^gtk-theme-name' "$HOME/.gtkrc-2.0"; then
    sed -i "s|^gtk-theme-name.*|gtk-theme-name=\"$slug\"|" "$HOME/.gtkrc-2.0"
  else
    printf 'gtk-theme-name="%s"\n' "$slug" >> "$HOME/.gtkrc-2.0"
  fi
  # GTK4/Wayland reads the theme from GSettings, not settings.ini.
  if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.interface gtk-theme "$slug" 2>/dev/null || true
    if [ "$dark" = true ]; then
      gsettings set org.gnome.desktop.interface color-scheme prefer-dark 2>/dev/null || true
    else
      gsettings set org.gnome.desktop.interface color-scheme default 2>/dev/null || true
    fi
  fi
  echo "gtk applied: $slug"
}

apply_variant() {
  local v="$1" lfid aurorae
  case "$v" in
    main) lfid=com.rosepine.main; aurorae=RosePine ;;
    moon) lfid=com.rosepine.moon; aurorae=RosePineMoon ;;
    dawn) lfid=com.rosepine.dawn; aurorae=RosePineDawn ;;
  esac
  lookandfeeltool -a "$lfid"
  apply_gtk "$v"
  # Preferred deco: BreezeEnhanced (C++, Rose Pine buttons).
  export QT_PLUGIN_PATH="$HOME/.local/lib/plugins${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}"
  if /usr/lib/kwin-applywindowdecoration BreezeEnhanced >/dev/null 2>&1; then
    echo "applied: $lfid + BreezeEnhanced"
    return 0
  fi
  # Fallback: bundled Aurorae traffic lights. lookandfeeltool strips the
  # __aurorae__svg__ prefix KWin needs and may write kwinrc asynchronously:
  # settle, then force v2 engine + prefixed theme, and verify before reconfig.
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
  echo "applied: $lfid + aurorae $aurorae (fallback)"
}

install_breezeenhanced() {
  # C++ deco (BreezeEnhanced, Rose Pine buttons): build once, incremental after.
  "$REPO/tools/build-breezeenhanced.sh" || return 1
  mkdir -p ~/.config/plasma-workspace/env
  cp "$REPO/breeze-enhanced-qt-plugins.sh" ~/.config/plasma-workspace/env/
  chmod +x ~/.config/plasma-workspace/env/breeze-enhanced-qt-plugins.sh
  export QT_PLUGIN_PATH="$HOME/.local/lib/plugins${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}"
}

if [ "$VAR" = all ]; then
  install_breezeenhanced
  for v in main moon dawn; do install_variant "$v"; done
  apply_variant moon
else
  install_breezeenhanced
  install_variant "$VAR"
  apply_variant "$VAR"
fi
echo "Verify with: lookandfeeltool -l | grep rose; kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme"
