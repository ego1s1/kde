#!/usr/bin/env python3
"""Generate Rose Pine KDE colorschemes + desktoptheme colors from palette.json.

Usage:
  python3 tools/generate.py [--check]

- Renders color-schemes/{RosePine,RosePineMoon,RosePineDawn}.colors
- Renders desktoptheme/{rosepine,rosepine-moon,rosepine-dawn}/colors
- --check: fail if committed files drift from generator output.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PALETTE = json.loads((REPO / "palette.json").read_text())


def rgb(role_vals):
    return f"{role_vals[0]}, {role_vals[1]}, {role_vals[2]}"


COLORSCHEME_TEMPLATE = """[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=true
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundAlternate={surface}
BackgroundNormal={base}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:Complementary]
BackgroundAlternate={surface}
BackgroundNormal={base}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={iris}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:Header]
BackgroundAlternate={overlay}
BackgroundNormal={base}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:Header][Inactive]
BackgroundAlternate={overlay}
BackgroundNormal={surface}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:Selection]
BackgroundAlternate={highlightHigh}
BackgroundNormal={highlightMed}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:Tooltip]
BackgroundAlternate={surface}
BackgroundNormal={base}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:View]
BackgroundAlternate={surface}
BackgroundNormal={base}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[Colors:Window]
BackgroundAlternate={surface}
BackgroundNormal={base}
DecorationFocus={iris}
DecorationHover={foam}
ForegroundActive={text}
ForegroundInactive={subtle}
ForegroundLink={iris}
ForegroundNegative={love}
ForegroundNeutral={pine}
ForegroundNormal={text}
ForegroundPositive={rose}
ForegroundVisited={foam}

[General]
ColorScheme={slug}
Name={display}
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={base}
activeBlend={text}
activeForeground={text}
frame={foam}
inactiveBackground={base}
inactiveBlend={base}
inactiveForeground={subtle}
inactiveFrame={highlightHigh}
"""


def render_colorscheme(variant):
    r = PALETTE["variants"][variant]["roles"]
    ctx = {k: rgb(v) for k, v in r.items()}
    ctx["slug"] = PALETTE["variants"][variant]["slug"]
    ctx["display"] = PALETTE["variants"][variant]["display"]
    return COLORSCHEME_TEMPLATE.format(**ctx)


def main():
    check = "--check" in sys.argv
    failed = False
    for variant, meta in PALETTE["variants"].items():
        text = render_colorscheme(variant)
        assert "$" not in text, f"unexpanded var in {variant}"
        for out in [
            REPO / "color-schemes" / f"{meta['slug']}.colors",
            REPO / "desktoptheme" / meta["style_id"] / "colors",
        ]:
            if check:
                if not out.exists() or out.read_text() != text:
                    print(f"DRIFT: {out.relative_to(REPO)}")
                    failed = True
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text)
                print(f"wrote {out.relative_to(REPO)}")
    if check and failed:
        sys.exit(1)
    print("OK: no $vars, all schemes in sync")


if __name__ == "__main__":
    main()
