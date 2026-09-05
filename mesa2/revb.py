#!/usr/bin/env python3
"""mesa2 Rev B placement: derive the Rev B key geometry from the Rev A board.

Rev A's positions are read straight out of mesa2.kicad_pcb -- the board is the
record of truth, not the earlier json snapshots, which stopped being updated
after the 5-degree hand rotation.

Three changes:
  1. the outer pinky keys (SW_LR1/SW_RR1 and their diodes) go away
  2. the surviving pinky keys rotate 90 degrees, so the cap lines up with the
     other finger keys instead of sitting across them
  3. the SP thumb keys move 1 mm toward their BK partner: 18 mm -> 17 mm, the
     same pitch every finger column uses

Diodes ride with their switch at a fixed local offset, which is how Rev A was
built and is verified here before anything is moved.

Run:  uv run --with shapely python revb.py
"""
import json, math, re, sys

PCB = 'mesa2/mesa2.kicad_pcb'
CAP = (-8.75, -8.25, 8.75, 8.25)      # 1u choc keycap, 17.5 x 16.5
FP  = (-9.575, -4.695, 6.351, 7.450)  # Kailh_socket_PG1350 envelope, asymmetric
DIODE_LOCAL = (0.0, -4.876)           # diode centre in its switch's frame
CLR = 0.5                             # wanted air gap between caps

# ------------------------------------------------------------------ read --
def read_pcb(path):
    return parse_pcb(open(path).read())

def parse_pcb(s):
    out = {}
    for m in re.finditer(r'\(footprint[\s"]', s):
        i = m.start(); d = 0
        for j in range(i, len(s)):
            if s[j] == '(': d += 1
            elif s[j] == ')':
                d -= 1
                if d == 0: blk = s[i:j+1]; break
        r = re.search(r'"Reference" "([^"]+)"', blk)
        at = re.search(r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', blk)
        if r and at:
            out[r.group(1)] = (float(at.group(1)), float(at.group(2)),
                               float(at.group(3) or 0))
    return out

# ------------------------------------------------------------- geometry --
def place(rect, x, y, rot):
    """KiCad convention: rotation CCW, +Y down."""
    x0, y0, x1, y1 = rect
    a = math.radians(rot); c, s = math.cos(a), math.sin(a)
    return [(x + px*c + py*s, y - px*s + py*c)
            for px, py in [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]]

def to_global(sx, sy, srot, px, py):
    a = math.radians(srot); c, s = math.cos(a), math.sin(a)
    return (sx + px*c + py*s, sy - px*s + py*c)

def sat_gap(A, B):
    """Separating-axis distance. Positive = clear, negative = overlap."""
    best = -1e9
    for poly in (A, B):
        for i in range(len(poly)):
            x1, y1 = poly[i]; x2, y2 = poly[(i+1) % len(poly)]
            nx, ny = -(y2-y1), (x2-x1)
            L = math.hypot(nx, ny); nx, ny = nx/L, ny/L
            pa = [p[0]*nx + p[1]*ny for p in A]
            pb = [p[0]*nx + p[1]*ny for p in B]
            best = max(best, max(min(pb)-max(pa), min(pa)-max(pb)))
    return best

def worst_cap_gap(sw):
    keys = sorted(sw)
    worst = (1e9, None, None)
    for i, a in enumerate(keys):
        for b in keys[i+1:]:
            g = sat_gap(place(CAP, *sw[a]), place(CAP, *sw[b]))
            if g < worst[0]: worst = (g, a, b)
    return worst

# ----------------------------------------------------------------- main --
def rev_a_from_git():
    """The working board is already Rev B, so recover Rev A from history.

    Walks the board file's commits newest-first and takes the first one that
    still has an outer pinky key. Keeps this script re-runnable without
    hardcoding a commit that will drift.
    """
    import subprocess
    log = subprocess.run(['git', 'log', '--format=%H', '--', PCB],
                         capture_output=True, text=True, check=True).stdout.split()
    for c in log:
        blob = subprocess.run(['git', 'show', f'{c}:mesa2/{PCB}'],
                              capture_output=True, text=True, cwd='..')
        if blob.returncode == 0 and 'SW_LR1' in blob.stdout:
            print(f"working board is already Rev B; reading Rev A from {c[:8]}\n")
            return c, blob.stdout
    sys.exit("no commit of the board still has SW_LR1 on it")

rev_a = read_pcb(PCB)
if 'SW_LR1' not in rev_a:
    _, text = rev_a_from_git()
    rev_a = parse_pcb(text)
sw_a = {k: v for k, v in rev_a.items() if k.startswith('SW_')}

# check the diode invariant before relying on it
for k, (sx, sy, st) in sw_a.items():
    d = 'D_' + k[3:]
    if d not in rev_a: continue
    want = to_global(sx, sy, st, *DIODE_LOCAL)
    got = rev_a[d][:2]
    if math.dist(want, got) > 0.01:
        sys.exit(f"diode invariant broken at {d}: want {want}, got {got}")

DELETE = ['SW_LR1', 'SW_RR1', 'D_LR1', 'D_RR1']
sw_b = {k: list(v) for k, v in sw_a.items() if k not in DELETE}

# 2. pinky rotation. -90 on the left, +90 on the right: -27.1 and +27.1, still
#    negated like every other key pair, so the diodes stay mirrored.
#
#    The two directions give the SAME keycap orientation -- they are 180 apart and
#    the cap is a rectangle -- so no clearance number distinguishes them. What they
#    change is which side the socket body and the diode land on, and that was
#    settled by looking at the board: the other way round put both on the wrong
#    side. Rotating +90/-90 instead is a one-line change here, but do not let the
#    clearance table talk you back into it; it cannot see the difference.
for ref, delta in [('SW_LA1', -90), ('SW_RA1', +90)]:
    x, y, r = sw_b[ref]
    sw_b[ref][2] = r + delta
    print(f"{ref}: rot {r:+.1f} -> {r+delta:+.1f}")

# 3. thumbs: SP moves 1 mm along the line toward BK
for sp, bk in [('SW_LSP1', 'SW_LBK1'), ('SW_RSP1', 'SW_RBK1')]:
    x, y, _ = sw_b[sp]; bx, by, _ = sw_b[bk]
    d = math.hypot(bx-x, by-y)
    sw_b[sp][0] = x + (bx-x)/d
    sw_b[sp][1] = y + (by-y)/d
    nd = math.hypot(bx-sw_b[sp][0], by-sw_b[sp][1])
    print(f"{sp}: thumb pitch {d:.3f} -> {nd:.3f} mm")

# diodes follow their switches
out = {}
for k, (x, y, r) in sw_b.items():
    out[k] = [round(x, 4), round(y, 4), round(r, 2)]
    dx, dy = to_global(x, y, r, *DIODE_LOCAL)
    out['D_' + k[3:]] = [round(dx, 4), round(dy, 4), round((r + 180) % 360, 2)]

print(f"\nRev A: {len(sw_a)} keys   Rev B: {len(sw_b)} keys")
for label, sw in [('Rev A', sw_a), ('Rev B', {k: tuple(v) for k, v in sw_b.items()})]:
    g, a, b = worst_cap_gap(sw)
    flag = '' if g >= CLR - 0.005 else '   <-- BELOW TARGET'
    print(f"{label}: worst cap gap {g:.3f} mm  ({a} vs {b}){flag}")

json.dump(out, open('revb-placement.json', 'w'), indent=1)
print(f"\nwrote revb-placement.json ({len(out)} footprints)")
