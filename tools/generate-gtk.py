#!/usr/bin/env python3
"""Generate Breeze-based GTK 2/3/4 themes from the Rose Pine color schemes.

The vendored breeze-gtk sources live in gtk/breeze-gtk/src. Each variant is
rendered with its matching color-schemes/<slug>.colors file, so the GTK theme
uses the exact same palette as the Plasma theme.

Usage:
  python3 tools/generate-gtk.py            # write gtk/themes/<slug>
  python3 tools/generate-gtk.py main       # only one variant

Requirements:
  - python-cairo (for breeze-gtk's render_assets.py)
  - libsass (pip install libsass) or the sassc/sass CLI
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "gtk" / "breeze-gtk" / "src"
OUT = REPO / "gtk" / "themes"
PALETTE = json.loads((REPO / "palette.json").read_text())
RENDER_PYTHON = os.environ.get("RENDER_PYTHON") or shutil.which("python3") or sys.executable


def compile_scss(src: Path, dst: Path, include_paths: list[Path]) -> None:
    """Compile one SCSS file, preferring libsass and falling back to sassc."""
    try:
        import sass  # type: ignore
    except ImportError:
        sass = None

    if sass is not None:
        css = sass.compile(
            filename=str(src),
            include_paths=[str(p) for p in include_paths],
            output_style="expanded",
        )
        dst.write_text(css)
        return

    for cli in ("sassc", "sass"):
        exe = shutil.which(cli)
        if not exe:
            continue
        cmd = [exe]
        if cli == "sassc":
            for path in include_paths:
                cmd += ["-I", str(path)]
        else:
            for path in include_paths:
                cmd += ["--load-path", str(path)]
        cmd += [str(src), str(dst)]
        subprocess.run(cmd, check=True)
        return

    raise SystemExit(
        "No Sass compiler found. Install libsass (pip install libsass) or sassc."
    )


def build_variant(slug: str) -> None:
    colors = REPO / "color-schemes" / f"{slug}.colors"
    if not colors.exists():
        raise SystemExit(f"Missing color scheme: {colors}")

    target = OUT / slug
    if target.exists():
        shutil.rmtree(target)

    build = Path(tempfile.mkdtemp(prefix=f"rosepine-gtk-{slug}-"))
    try:
        for sub in ("gtk-2.0", "gtk-3.0", "gtk-4.0"):
            (build / sub).mkdir(parents=True)

        shutil.copytree(SRC / "gtk2", build / "gtk-2.0", dirs_exist_ok=True)
        subprocess.run(
            [
                RENDER_PYTHON,
                str(SRC / "render_assets.py"),
                "-c", str(colors),
                "-b", str(colors),
                "-a", str(build / "assets"),
                "-g", str(build / "gtk-2.0"),
                "-G", str(build),
            ],
            check=True,
        )

        includes = [build, SRC, SRC / "gtk3", SRC / "gtk4"]
        compile_scss(SRC / "gtk3" / "gtk.scss", build / "gtk-3.0" / "gtk.css", includes)
        compile_scss(SRC / "gtk4" / "gtk.scss", build / "gtk-4.0" / "gtk.css", includes)

        target.mkdir(parents=True)
        shutil.copytree(build / "gtk-2.0", target / "gtk-2.0")
        shutil.copytree(build / "gtk-3.0", target / "gtk-3.0")
        shutil.copytree(build / "gtk-4.0", target / "gtk-4.0")
        shutil.copytree(build / "assets", target / "assets")
        # Source SVGs referenced by the CSS (titlebar buttons, checkmarks, ...)
        shutil.copytree(SRC / "assets", target / "assets", dirs_exist_ok=True)
        shutil.copy(SRC / "settings.ini", target / "settings.ini")
    finally:
        shutil.rmtree(build, ignore_errors=True)

    print(f"wrote {target.relative_to(REPO)}")


def main() -> None:
    wanted = sys.argv[1:]
    variants = [
        (name, meta) for name, meta in PALETTE["variants"].items()
        if not wanted or name in wanted
    ]
    if not variants:
        raise SystemExit(f"Unknown variant(s): {', '.join(wanted)}")
    for _, meta in variants:
        build_variant(meta["slug"])


if __name__ == "__main__":
    main()
