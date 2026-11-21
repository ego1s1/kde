# Rosé Pine for KDE Plasma

Three global themes — Main, Moon and Dawn — with Breeze behavior, Rosé Pine colors and macOS-style traffic-light window buttons.

![Rosé Pine Moon](assets/moon-global-menu-panel.png)

## Install

Arch / Arch-based dependencies:

```bash
sudo pacman -S --needed base-devel cmake extra-cmake-modules
```

Clone and install (builds the window decoration and applies Moon):

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

## Credits

This theme is built on the work of these projects:

- [Rosé Pine](https://github.com/rose-pine/rose-pine-theme) — palette and original theme
- [BreezeEnhanced](https://github.com/tsujan/BreezeEnhanced) by tsujan — window decoration (vendored fork)
- [KDE Breeze](https://invent.kde.org/plasma/breeze) — base decoration and theme behavior
- [WhiteSur](https://github.com/vinceliuice/WhiteSur-kde) by vinceliuice — Aurorae traffic-light templates
- [KDE One Dark](https://github.com/Prayag2/kde_onedark) by Prayag2 — decoration inspiration

Thanks also to [Ash](https://github.com/maybork) and [Cuboid Raptor](https://github.com/CuboidRaptor) for the original work this fork started from.

## License

Theme files: MIT. The vendored BreezeEnhanced decoration keeps its own GPL license — see `kwin/decoration/rose-pine/LICENSE`.
