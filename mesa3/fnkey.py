#!/usr/bin/env python3
"""mesa3 Rev B: derive the FN (mode) key placement from the board.

The Rev B change is one extra key per hand, immediately inboard of the
near-row index key, used as a layer/mode key. This script computes where it
belongs rather than leaving it where the mouse dropped it.

The board is the record of truth, as it was for revb.py: SW_LE1 is read out of
mesa3-left.kicad_pcb and the FN key is placed relative to it.

Placement rule:

  SW_LFN1 sits at a local offset of (PITCH, 0) in SW_LE1's own frame, and
  carries SW_LE1's rotation unchanged. Local +X is the direction the keycap is
  wide in, so this walks one key inboard along the row the index near key sits
  on, keeping both caps parallel.

  PITCH is 18.0 mm and that is not a free parameter: the 1u choc cap is 17.5 mm
  across local X, and the board's clearance target is a 0.5 mm air gap, so
  17.5 + 0.5 = 18.0 is the tightest legal pitch. Anything less overlaps caps.

  D_LFN1 follows its switch at DIODE_LOCAL, rotated 180, exactly like every
  other diode on the board. The invariant is verified against the existing keys
  before it is relied on.

Only the left half is done here. Whether the right half gets one too is still
open -- see "Open before anything is routed" in mesa3-tasks.md. If it does, add
('SW_RE1', 'SW_RFN1', -1) to KEYS: the sign matters, because local +X points
outboard on the right half, so a right-hand key needs -PITCH to land inboard.
With the sign right the new pair sums to 270.000 in x like every other, switch
and diode alike.

Run:  python3 fnkey.py
Then: apply-fnkey.py writes it to the board (KiCAD must be closed).
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(HERE, 'mesa3-left', 'mesa3-left.kicad_pcb')
OUT = os.path.join(HERE, 'fn-placement.json')

CAP = (-8.75, -8.25, 8.75, 8.25)      # 1u choc keycap, 17.5 x 16.5
DIODE_LOCAL = (0.0, -4.876)           # diode centre in its switch's frame
CLR = 0.5                             # wanted air gap between caps
PITCH = CAP[2] - CAP[0] + CLR         # 18.0 mm -- cap width plus the gap

# (anchor, new key, direction). Direction is +1 where local +X points inboard and
# -1 where it points outboard -- which is to say +1 on the left half, -1 on the
# right. Getting it wrong puts the key outside the board, not just off by a bit.
KEYS = [('SW_LE1', 'SW_LFN1', +1)]


# ------------------------------------------------------------------ read --
LAYER = {}                            # ref -> "F.Cu" / "B.Cu", filled by parse_pcb


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
        ly = re.search(r'\(layer "([^"]+)"', blk)
        if r and at:
            out[r.group(1)] = (float(at.group(1)), float(at.group(2)),
                               float(at.group(3) or 0))
            if ly:
                LAYER[r.group(1)] = ly.group(1)
    return out


# ------------------------------------------------------------- geometry --
def to_global(sx, sy, srot, px, py):
    """KiCad convention: rotation CCW, +Y down."""
    a = math.radians(srot); c, s = math.cos(a), math.sin(a)
    return (sx + px*c + py*s, sy - px*s + py*c)


def to_local(sx, sy, srot, gx, gy):
    """Inverse of to_global -- what local offset puts a point where it is."""
    a = math.radians(srot); c, s = math.cos(a), math.sin(a)
    dx, dy = gx - sx, gy - sy
    return (dx*c - dy*s, dx*s + dy*c)


def place(rect, x, y, rot):
    x0, y0, x1, y1 = rect
    a = math.radians(rot); c, s = math.cos(a), math.sin(a)
    return [(x + px*c + py*s, y - px*s + py*c)
            for px, py in [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]]


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


# ----------------------------------------------------------------- main --
board = parse_pcb(open(PCB).read())
sw = {k: v for k, v in board.items() if k.startswith('SW_')}

# The diode invariant is load-bearing here, so check it before using it.
bad = []
for k, (sx, sy, st) in sw.items():
    d = 'D_' + k[3:]
    if d not in board:
        continue
    want = to_global(sx, sy, st, *DIODE_LOCAL)
    if math.dist(want, board[d][:2]) > 0.01:
        bad.append((d, board[d][:2], want))
for d, got, want in bad:
    if d in ('D_' + n[3:] for _, n, _s in KEYS):
        continue            # the new one is what we are here to fix
    print(f"diode invariant broken at {d}: on board {got}, rule says "
          f"({want[0]:.3f}, {want[1]:.3f})")
if [d for d, _, _ in bad if d not in ('D_' + n[3:] for _, n, _s in KEYS)]:
    sys.exit("refusing to place against a board whose diode rule does not hold")

print(f"pitch {PITCH:.3f} mm = {CAP[2]-CAP[0]:.1f} mm cap + {CLR:.1f} mm gap\n")

out = {}
for anchor, new, sign in KEYS:
    if anchor not in sw:
        sys.exit(f"{anchor} is not on the board")
    ax, ay, arot = sw[anchor]
    x, y = to_global(ax, ay, arot, sign * PITCH, 0.0)
    rot = arot
    dx, dy = to_global(x, y, rot, *DIODE_LOCAL)
    drot = (rot + 180) % 360

    out[new] = [round(x, 4), round(y, 4), round(rot, 2)]
    out['D_' + new[3:]] = [round(dx, 4), round(dy, 4), round(drot, 2)]

    print(f"{new} from {anchor} at ({ax:.3f}, {ay:.3f}) @{arot:+.1f}")
    if new in sw:
        cx, cy, crot = sw[new]
        lx, ly = to_local(ax, ay, arot, cx, cy)
        print(f"  on board  ({cx:9.3f}, {cy:8.3f}) @{crot:+6.1f}"
              f"   local ({lx:7.3f}, {ly:+6.3f})")
    print(f"  computed  ({x:9.3f}, {y:8.3f}) @{rot:+6.1f}"
          f"   local ({sign*PITCH:7.3f}, {0.0:+6.3f})")
    if new in sw:
        print(f"  moves     {math.dist((cx, cy), (x, y)):.3f} mm")

# clearance of the new caps against every key on the board
print()
final = dict(sw)
for ref, (x, y, r) in out.items():
    if ref.startswith('SW_'):
        final[ref] = (x, y, r)
for _, new, _sign in KEYS:
    worst = (1e9, None)
    for other in sorted(final):
        if other == new:
            continue
        g = sat_gap(place(CAP, *final[new]), place(CAP, *final[other]))
        if g < worst[0]:
            worst = (g, other)
    flag = '' if worst[0] >= CLR - 0.005 else '   <-- BELOW TARGET'
    print(f"{new}: worst cap gap {worst[0]:.3f} mm (vs {worst[1]}){flag}")

# Non-key neighbours. Only same-side parts can foul a keycap or the switch
# body -- a part on the other copper layer is on the far side of the board and
# is not a mechanical conflict however close it looks in x/y. Both are listed,
# because the far side still matters for routing, but only the near side is
# flagged.
print()
others = {k: v for k, v in board.items()
          if not k.startswith(('SW_', 'D_', 'H'))}
for _, new, _sign in KEYS:
    x, y, _r = final[new]
    side = LAYER.get(new, 'F.Cu')
    near = sorted(((math.dist((x, y), (v[0], v[1])), k)
                   for k, v in others.items()))[:6]
    print(f"{new} is on {side}; nearest non-key parts (centre to centre):")
    for dist, k in near:
        other = LAYER.get(k, '?')
        note = 'same side' if other == side else 'far side, not a clearance issue'
        print(f"    {k:8s} {dist:7.2f} mm  {other:5s}  {note}")

json.dump(out, open(OUT, 'w'), indent=1)
print(f"\nwrote {os.path.basename(OUT)} ({len(out)} footprints)")
