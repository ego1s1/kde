# GTK themes

Breeze-based GTK 2/3/4 themes generated from the Rose Pine color schemes.

- `breeze-gtk/` — vendored [breeze-gtk](https://github.com/KDE/breeze-gtk) sources (BSD-3-Clause/CC0). `src/render_assets.py` has one small patch so it accepts KDE color values written with spaces (`25, 23, 36`).
- `themes/<variant>/` — generated themes installed to `~/.local/share/themes/` by `install.sh`.

Regenerate after changing `palette.json`:

```bash
python3 tools/generate-gtk.py
```

This needs `python-cairo` and either `libsass` (`pip install libsass`) or the `sassc`/`sass` CLI.
