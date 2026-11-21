# Rosé Pine for KDE Plasma

Three global themes — Main, Moon and Dawn — with Breeze behavior, Rosé Pine colors, macOS-style traffic-light window buttons, and matching Breeze-based GTK 2/3/4 themes.

![Rosé Pine Moon](assets/moon-global-menu-panel.png)

## Install

Arch / Arch-based dependencies:

```bash
sudo pacman -S --needed base-devel cmake extra-cmake-modules
```

Clone and install (builds the window decoration, installs the GTK themes, applies Moon):

```bash
git clone https://github.com/ego1s1/kde.git
cd kde
./install.sh
```

Pick a different variant:

```bash
./install.sh main    # or: moon, dawn, all
```

Log out and back in if the window buttons don't appear immediately. Buttons sit on the left in macOS order; change them in *System Settings → Window Decorations → Titlebar Buttons*.

> On other distros install the equivalent of `base-devel`, `cmake` and `extra-cmake-modules`, then run `./install.sh`.

## GTK apps

Each variant ships a Breeze-based GTK theme built from the same color scheme. `install.sh` installs it to `~/.local/share/themes/<variant>` and activates it for GTK 2, 3 and 4 (including the Wayland/GSettings setting).

To switch manually: *System Settings → Application Style → GNOME/GTK Application Style*, or set `gtk-theme-name=RosePineMoon` in `~/.config/gtk-3.0/settings.ini`.

Regenerate the GTK themes after palette changes with:

```bash
python3 tools/generate-gtk.py    # needs python-cairo and libsass or sassc
```

## Credits

This theme is built on the work of these projects:

- [Rosé Pine](https://github.com/rose-pine/rose-pine-theme) — palette and original theme
- [BreezeEnhanced](https://github.com/tsujan/BreezeEnhanced) by tsujan — window decoration (vendored fork)
- [KDE Breeze](https://invent.kde.org/plasma/breeze) — base decoration and theme behavior
- [breeze-gtk](https://github.com/KDE/breeze-gtk) — GTK theme sources (vendored)
- [WhiteSur](https://github.com/vinceliuice/WhiteSur-kde) by vinceliuice — Aurorae traffic-light templates
- [KDE One Dark](https://github.com/Prayag2/kde_onedark) by Prayag2 — decoration inspiration

Thanks also to [Ash](https://github.com/maybork) and [Cuboid Raptor](https://github.com/CuboidRaptor) for the original work this fork started from.

## License

Theme files: MIT. The vendored BreezeEnhanced decoration keeps its GPL license (`kwin/decoration/rose-pine/LICENSE`); the vendored breeze-gtk sources keep their BSD-3-Clause/CC0 licenses (`gtk/breeze-gtk/LICENSES`).
