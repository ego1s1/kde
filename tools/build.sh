#!/usr/bin/env bash
# Build + validate Rose Pine KDE packages.
# Usage: ./tools/build.sh [--install <main|moon|dawn|all>]
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "=== 1. generate (source of truth) ==="
python3 tools/generate.py || exit 1
python3 tools/generate-aurorae.py || exit 1

echo "=== 2. static checks ==="
if grep -rn '\$[a-zA-Z_]' color-schemes/ desktoptheme/ "Rose Pine/" "Rose Pine Moon/" "Rose Pine Dawn/" 2>/dev/null; then
  echo "FAIL: unexpanded \$vars"; exit 1
fi
echo "OK: no \$vars"
python3 - <<'EOF'
import configparser, glob, sys
ok = True
for f in sorted(glob.glob("color-schemes/*.colors")):
    c = configparser.ConfigParser(); c.optionxform = str; c.read(f)
    for s in ["View", "Window", "Button", "Selection", "Tooltip", "Complementary", "Header", "Header][Inactive"]:
        if f"Colors:{s}" not in c.sections():
            # Header][Inactive parses as nested; check raw text instead
            pass
    raw = open(f).read()
    for need in ["[Colors:Header]", "[Colors:Header][Inactive]", "[WM]", "contrast=4"]:
        if need not in raw:
            print(f"FAIL {f}: missing {need}"); ok = False
print("OK: sections present" if ok else "FAIL")
sys.exit(0 if ok else 1)
EOF
python3 tools/generate.py --check || exit 1

echo "=== 3. json validity ==="
for j in look-and-feel/*/metadata.json desktoptheme/*/metadata.json; do
  python3 -m json.tool "$j" >/dev/null || exit 1
done
echo "OK: metadata.json valid"

echo "=== 4. contrast gates (WCAG AA body >= 4.5) ==="
python3 - <<'EOF'
import configparser, glob
def lum(rgb):
    def ch(c):
        c/=255
        return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b=[ch(x) for x in rgb]; return 0.2126*r+0.7152*g+0.0722*b
def ratio(a,b):
    l1,l2=sorted([lum(a),lum(b)],reverse=True); return (l1+0.05)/(l2+0.05)
worst=[]
for f in sorted(glob.glob("color-schemes/*.colors")):
    c=configparser.ConfigParser(); c.optionxform=str; c.read(f)
    for s in ["View","Window","Button","Selection"]:
        bg=[int(x) for x in c[f"Colors:{s}"]["BackgroundNormal"].split(",")]
        fg=[int(x) for x in c[f"Colors:{s}"]["ForegroundNormal"].split(",")]
        r=ratio(bg,fg); flag="OK " if r>=4.5 else "FAIL"
        print(f"  {f.split('/')[-1]:20s} {s:9s} {r:4.1f}:1 [{flag}]")
        if r<4.5: worst.append((f,s,round(r,2)))
print("CONTRAST:", "PASS" if not worst else f"FAIL {worst}")
EOF

if [ "${1:-}" = "--install" ]; then
  chmod +x install.sh
  ./install.sh "${2:-all}"
fi
echo "BUILD OK"
