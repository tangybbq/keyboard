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
    s = open(path).read()
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
rev_a = read_pcb(PCB)
if 'SW_LR1' not in rev_a:
    sys.exit("SW_LR1 is not on the board, so it is already Rev B. This script "
             "transforms Rev A and is not idempotent -- re-running it would "
             "rotate the pinky another 90 degrees and pull the thumbs in another "
             "millimetre. revb-placement.json is the record; apply-revb.py is "
             "safe to re-run.")
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

# 2. pinky rotation. +90 on the left, -90 on the right, which keeps the
#    negated-rotation convention every other key pair on this board follows and
#    so keeps the diodes mirrored too. The alternative (+90 on both) was checked
#    and rejected: it buys 1.6 mm of board edge on the right, but the socket sits
#    inside the keycap envelope in every option, so the outline is cap-driven and
#    that 1.6 mm is not real. The socket's long reach still lands on opposite
#    sides of the two halves -- same asymmetry mesa1 documents, orient by silk.
for ref, delta in [('SW_LA1', +90), ('SW_RA1', -90)]:
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
