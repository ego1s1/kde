#!/usr/bin/env python3
"""Generate Rose Pine Aurorae traffic-light decorations from WhiteSur templates.

Replaces Breeze-arrow fallback buttons with macOS-style traffic lights:
  close    = love  (red)
  minimize = gold  (yellow)
  maximize = pine  (green)

Usage: python3 tools/generate-aurorae.py [--install]
Reads reference/whitesur-aurorae/{close,minimize,maximize,decoration}.svg,
writes aurorae/themes/RosePine{,Moon,Dawn}/
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REF = REPO / "reference" / "whitesur-aurorae"
OUT_BASE = REPO / "aurorae" / "themes"

PALETTES = {
    "RosePine": {
        "display": "Rose Pine",
        "base": "#191724", "surface": "#1f1d2e", "overlay": "#26233a",
        "muted": "#6e6a86", "subtle": "#908caa", "text": "#e0def4",
        "love": "#eb6f92", "gold": "#f6c177", "pine": "#31748f",
        # traffic-light pairs (inner bright, outer darkened ~0.8 like WhiteSur)
        "close_inner": "#eb6f92", "close_outer": "#bc5874",
        "min_inner": "#f6c177", "min_outer": "#c49a5f",
        "max_inner": "#31748f", "max_outer": "#275c72",
        "inactive_outer": "#6e6a86", "inactive_inner": "#908caa",
        # frame recolor (WhiteSur dark greys -> Rose Pine)
        "frame_map": {"#363636": "#191724", "#2d2d2d": "#1f1d2e",
                      "#242424": "#191724", "#1a1a1a": "#191724"},
    },
    "RosePineMoon": {
        "display": "Rose Pine Moon",
        "base": "#232136", "surface": "#2a273f", "overlay": "#393552",
        "muted": "#6e6a86", "subtle": "#908caa", "text": "#e0def4",
        "love": "#eb6f92", "gold": "#f6c177", "pine": "#3e8fb0",
        "close_inner": "#eb6f92", "close_outer": "#bc5874",
        "min_inner": "#f6c177", "min_outer": "#c49a5f",
        "max_inner": "#3e8fb0", "max_outer": "#31728c",
        "inactive_outer": "#6e6a86", "inactive_inner": "#908caa",
        "frame_map": {"#363636": "#232136", "#2d2d2d": "#2a273f",
                      "#242424": "#232136", "#1a1a1a": "#232136"},
    },
    "RosePineDawn": {
        "display": "Rose Pine Dawn",
        "base": "#faf4ed", "surface": "#fffaf3", "overlay": "#f2e9e1",
        "muted": "#9893a5", "subtle": "#797593", "text": "#575279",
        "love": "#b4637a", "gold": "#ea9d34", "pine": "#286983",
        "close_inner": "#b4637a", "close_outer": "#904f61",
        "min_inner": "#ea9d34", "min_outer": "#bb7d29",
        "max_inner": "#286983", "max_outer": "#205468",
        "inactive_outer": "#9893a5", "inactive_inner": "#cecacd",
        "frame_map": {"#363636": "#faf4ed", "#2d2d2d": "#fffaf3",
                      "#242424": "#faf4ed", "#1a1a1a": "#f2e9e1"},
    },
}

# WhiteSur source colors per button file
SRC = {
    "close.svg": {"outer": "#cb4e43", "inner": "#fe6254"},
    "minimize.svg": {"outer": "#caa124", "inner": "#fdc92d"},
    "maximize.svg": {"outer": "#20a932", "inner": "#28d33f"},
}
INACTIVE_SRC = {"outer": "#bababa", "inner": "#cecece"}

METADATA = """[Desktop Entry]
Name={display}
Comment=Rosé Pine traffic lights (love/gold/pine) for KWin Aurorae
X-KDE-PluginInfo-Author=Rosé Pine
X-KDE-PluginInfo-Email=
X-KDE-PluginInfo-Name={slug}
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-Category=
X-KDE-PluginInfo-Depends=
X-KDE-PluginInfo-License=MIT
X-KDE-PluginInfo-EnabledByDefault=true
"""

METADATA_JSON = """{
    "KPackageStructure": "KWin/Aurorae",
    "KPlugin": {
        "Authors": [{"Email": "", "Name": "Rosé Pine"}],
        "Category": "Plasma 6 Window Decorations",
        "ServiceTypes": ["aurorae"],
        "EnabledByDefault": true,
        "Name": "{display}",
        "Description": "Rosé Pine traffic lights (love/gold/pine) for KWin Aurorae",
        "Id": "{slug}",
        "License": "MIT",
        "Version": "1.0"
    }
}
"""
RCFILE = """[General]
ActiveTextColor={text_rgb},255
InactiveTextColor={subtle_rgb},255
TitleAlignment=Center
TitleVerticalAlignment=Center
LeftButtons=XIA
Shadow=true
Animation=1

[Layout]
BorderTop=0
BorderLeft=0
BorderRight=0
BorderBottom=0
TitleEdgeTop=8
TitleEdgeBottom=8
TitleEdgeLeft=16
TitleEdgeRight=16
TitleBorderLeft=50
TitleBorderRight=50
TitleHeight=16
ButtonWidth=16
ButtonHeight=16
ButtonSpacing=10
ButtonMarginTop=2
ButtonMarginLeft=0
ButtonMarginRight=0
ExplicitButtonSpacer=0
PaddingTop=21
PaddingBottom=0
PaddingRight=41
PaddingLeft=41
TitleEdgeTopMaximized=8
TitleEdgeBottomMaximized=8
TitleEdgeLeftMaximized=16
TitleEdgeRightMaximized=16
"""


def hex_to_rgb(s):
    h = s.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def recolor_button(src_text, outer_src, inner_src, outer_dst, inner_dst,
                   inact_outer_dst, inact_inner_dst):
    out = src_text
    # active/hover/pressed use outer+inner; replace case-insensitively
    for a, b in ((outer_src, outer_dst), (inner_src, inner_dst)):
        out = out.replace(a, b).replace(a.upper(), b).replace(a.lower(), b)
    # inactive states (both inactive-center and deactivated-center use same greys)
    out = out.replace(INACTIVE_SRC["outer"], inact_outer_dst)
    out = out.replace(INACTIVE_SRC["inner"], inact_inner_dst)
    return out


def main(install=False):
    for slug, pal in PALETTES.items():
        d = OUT_BASE / slug
        d.mkdir(parents=True, exist_ok=True)
        # buttons: close/minimize/maximize (+ restore uses maximize art)
        mapping = {
            "close.svg": ("close_inner", "close_outer"),
            "minimize.svg": ("min_inner", "min_outer"),
            "maximize.svg": ("max_inner", "max_outer"),
            "restore.svg": ("max_inner", "max_outer"),
        }
        for fname, (inner_k, outer_k) in mapping.items():
            src_file = REF / fname
            if not src_file.exists():
                # restore falls back to maximize template
                src_file = REF / "maximize.svg"
            src = src_file.read_text()
            src_colors = SRC.get(src_file.name, SRC["maximize.svg"])
            colored = recolor_button(
                src, src_colors["outer"], src_colors["inner"],
                pal[outer_k], pal[inner_k],
                pal["inactive_outer"], pal["inactive_inner"])
            (d / fname).write_text(colored)
        # frame: recolor WhiteSur dark greys to palette base/surface/overlay
        deco = (REF / "decoration.svg").read_text()
        for a, b in pal["frame_map"].items():
            deco = deco.replace(a, b)
        # bottom lip: strip the 12px band to a solid opaque base (no halo seam)
        deco = re.sub(
            r'(d="M 470,27\d[^"]*"\s+fill="#[0-9a-fA-F]{6}"\s+opacity=")0\.75(")',
            r"\g<1>1\g<2>", deco)
        # no bottom lip extension: empty the bottom row + masks, zero bottom hints
        # no bottom lip: neutralize the bottom row + masks (1px no-op keeps
        # FrameSvg geometry valid), zero bottom hints/padding
        for gid in ["decoration-bottom", "decoration-bottomleft",
                    "decoration-bottomright",
                    "decoration-inactive-bottom",
                    "decoration-inactive-bottomleft",
                    "decoration-inactive-bottomright",
                    "mask-bottom", "mask-bottomleft", "mask-bottomright"]:
            deco = re.sub(r'(<g\s+id="%s".*?>).*?(</g>)' % gid,
                          r'\g<1><rect width="1" height="1" fill="none"/>\g<2>',
                          deco, flags=re.S)
        deco = re.sub(r'(<rect\s+id="shadow-hint-bottom-margin"[^>]*?height=")\d+(")',
                      r"\g<1>0\g<2>", deco)
        deco = re.sub(r'(<rect\s+id="hint-bottom-margin"[^>]*?height=")\d+(")',
                      r"\g<1>0\g<2>", deco)
        (d / "decoration.svg").write_text(deco)
        # Plasma 6 KWin/Aurorae package check requires svgz; ship both
        import gzip
        for svg_file in sorted(d.glob("*.svg")):
            raw = svg_file.read_bytes()
            svg_file.with_suffix(".svgz").write_bytes(gzip.compress(raw, mtime=0))
        (d / "metadata.desktop").write_text(
            METADATA.format(display=pal["display"], slug=slug))
        (d / "metadata.json").write_text(
            METADATA_JSON.replace("{display}", pal["display"]).replace("{slug}", slug))
        (d / f"{slug}rc").write_text(RCFILE.format(
            text_rgb=hex_to_rgb(pal["text"]),
            subtle_rgb=hex_to_rgb(pal["subtle"])))
        print(f"wrote {d} ({pal['display']})")
    if install:
        import shutil, os
        target_base = Path(os.path.expanduser("~/.local/share/aurorae/themes"))
        target_base.mkdir(parents=True, exist_ok=True)
        for slug in PALETTES:
            src = OUT_BASE / slug
            dst = target_base / slug
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"installed {dst}")


if __name__ == "__main__":
    main(install="--install" in sys.argv)
