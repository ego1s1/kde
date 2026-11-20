#!/bin/sh
# Expose user-local Qt plugins (BreezeEnhanced KWin decoration) to KDE sessions.
# Installed to ~/.config/plasma-workspace/env/ by install.sh.
# Sourced by plasma-workspace at login. Takes effect after re-login.
if [ -d "$HOME/.local/lib/plugins" ]; then
  case ":$QT_PLUGIN_PATH:" in
    *":$HOME/.local/lib/plugins:"*) ;;
    *) export QT_PLUGIN_PATH="$HOME/.local/lib/plugins${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}" ;;
  esac
fi
