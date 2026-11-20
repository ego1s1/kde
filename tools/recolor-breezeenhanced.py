#!/usr/bin/env python3
"""Recolor BreezeEnhanced macOS buttons with Rosé Pine hues.

Upstream: https://github.com/tsujan/BreezeEnhanced (V6.8, matches KWin 6.8).
Method: copy tree as-is, replace ONLY the hardcoded macOS button RGB
literals in breezebutton.cpp. Light-titlebar branch (qGray>100) gets Dawn
values, dark-titlebar branch gets Main/Moon values. Inactive grey is computed
dynamically upstream -- left untouched.

Usage: python3 tools/recolor-breezeenhanced.py <source-dir>
Fails loudly if any expected literal is missing (upstream drift guard).
"""
import sys
from pathlib import Path

# (file, old, new) -- old must match upstream V6.8 byte-for-byte.
REPLACEMENTS = [
    # --- Close (red -> love) ---
    ("breezebutton.cpp", "QColor(255, 92, 87)", "QColor(0xb4, 0x63, 0x7a)"),    # love Dawn
    ("breezebutton.cpp", "QColor(233, 84, 79)", "QColor(0xa2, 0x57, 0x6d)"),    # love Dawn darker
    ("breezebutton.cpp", "QColor(250, 100, 102)", "QColor(0xeb, 0x6f, 0x92)"),  # love Moon/Main
    ("breezebutton.cpp", "QColor(230, 92, 94)", "QColor(0xd1, 0x55, 0x7c)"),    # love Moon/Main darker
    # --- Maximize/restore (green -> pine; light branch = Dawn, dark = Main) ---
    # checked-state teal -> pine Moon in both branches (primary variant)
    ("breezebutton.cpp", "QColor(67, 198, 176)", "QColor(0x3e, 0x8f, 0xb0)"),   # pine Moon
    ("breezebutton.cpp", "QColor(60, 178, 159)", "QColor(0x38, 0x7f, 0x9e)"),   # pine Moon darker
    ("breezebutton.cpp", "QColor(40, 211, 63)", "QColor(0x28, 0x69, 0x83)"),   # pine Dawn
    ("breezebutton.cpp", "QColor(36, 191, 57)", "QColor(0x24, 0x5e, 0x74)"),    # pine Dawn darker
    ("breezebutton.cpp", "QColor(124, 198, 67)", "QColor(0x31, 0x74, 0x8f)"),   # pine Main
    ("breezebutton.cpp", "QColor(111, 178, 60)", "QColor(0x2c, 0x68, 0x80)"),   # pine Main darker
    # --- Minimize (yellow -> gold) ---
    ("breezebutton.cpp", "QColor(243, 176, 43)", "QColor(0xea, 0x9d, 0x34)"),   # gold Dawn
    ("breezebutton.cpp", "QColor(223, 162, 39)", "QColor(0xd2, 0x8d, 0x2e)"),   # gold Dawn darker
    ("breezebutton.cpp", "QColor(237, 198, 81)", "QColor(0xf6, 0xc1, 0x77)"),   # gold Moon/Main
    ("breezebutton.cpp", "QColor(217, 181, 74)", "QColor(0xdd, 0xad, 0x6b)"),   # gold Moon/Main darker
    # --- OnAllDesktops (blue -> foam) ---
    ("breezebutton.cpp", "QColor(103, 149, 210)", "QColor(0x56, 0x94, 0x9f)"),  # foam Dawn
    ("breezebutton.cpp", "QColor(93, 135, 190)", "QColor(0x4e, 0x8a, 0x94)"),  # foam Dawn darker
    ("breezebutton.cpp", "QColor(135, 166, 220)", "QColor(0x9c, 0xcf, 0xd8)"),  # foam Moon
    ("breezebutton.cpp", "QColor(122, 151, 200)", "QColor(0x8a, 0xb4, 0xc0)"),  # foam Moon darker
]


def main() -> None:
    src = Path(sys.argv[1])
    counts: dict[str, int] = {}
    for fname, old, new in REPLACEMENTS:
        p = src / fname
        text = p.read_text()
        n = text.count(old)
        key = f"{fname}:{old}"
        counts[key] = counts.get(key, 0) + n
        if n == 0:
            print(f"MISSING (upstream drift?): {key}")
            sys.exit(1)
        p.write_text(text.replace(old, new))
    total = sum(counts.values())
    print(f"recolored {total} literals across {len({f for f, _, _ in REPLACEMENTS})} file(s)")
    # guard: no remaining upstream macOS literals
    leftovers = ["QColor(255, 92, 87)", "QColor(40, 211, 63)", "QColor(243, 176, 43)",
                 "QColor(103, 149, 210)", "QColor(135, 166, 220)"]
    rest = (src / "breezebutton.cpp").read_text()
    bad = [lit for lit in leftovers if lit in rest]
    if bad:
        print(f"LEFTOVER upstream literals: {bad}")
        sys.exit(1)
    print("OK: no upstream macOS literals remain")


if __name__ == "__main__":
    main()
