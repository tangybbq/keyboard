#!/usr/bin/env python3
"""mesa3 Rev B: derive the FN (mode) key placement from the boards.

The Rev B change is one extra key per hand, immediately inboard of the
near-row index key, used as a layer/mode key. This script computes where it
belongs rather than leaving it where the mouse dropped it.

The boards are the record of truth, as they were for revb.py: SW_LE1 and
SW_RE1 are read out of the two .kicad_pcb files and the FN key on each half is
placed relative to its own anchor.

Placement rule:

  SW_xFN1 sits at a local offset of (PITCH, 0) in SW_xE1's own frame, and
  carries SW_xE1's rotation unchanged. Local +X is the direction the keycap is
  wide in, so this walks one key inboard along the row the index near key sits
  on, keeping both caps parallel.

  PITCH is 18.0 mm and that is not a free parameter: the 1u choc cap is 17.5 mm
  across local X, and the board's clearance target is a 0.5 mm air gap, so
  17.5 + 0.5 = 18.0 is the tightest legal pitch. Anything less overlaps caps.

  The sign matters. Local +X points inboard on the left half and outboard on
  the right, so the right-hand key needs -PITCH to land inboard; getting it
  wrong puts the key off the board, not just off by a bit.

  D_xFN1 follows its switch at DIODE_LOCAL, rotated 180, exactly like every
  other diode on the board. The invariant is verified against the existing keys
  before it is relied on.

Both halves are done here, and because they are done from their own anchors the
two results are independent. That makes the halves' mirror symmetry a real
check rather than a restatement: every existing SW_L*/SW_R* and D_L*/D_R* pair
sums to MIRROR_X in x, shares a y, and has opposite rotations, and the computed
FN pair is held to the same standard at the end of the run.

Run:  python3 fnkey.py
Then: apply-fnkey.py writes it to the boards (KiCAD must be closed).
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'fn-placement.json')

CAP = (-8.75, -8.25, 8.75, 8.25)      # 1u choc keycap, 17.5 x 16.5
DIODE_LOCAL = (0.0, -4.876)           # diode centre in its switch's frame
CLR = 0.5                             # wanted air gap between caps
PITCH = CAP[2] - CAP[0] + CLR         # 18.0 mm -- cap width plus the gap
MIRROR_X = 270.0                      # x_left + x_right for a mirrored pair

# (board, anchor, new key, direction). Direction is +1 where local +X points
# inboard and -1 where it points outboard -- +1 on the left half, -1 on the
# right.
KEYS = [
    ('mesa3-left',  'SW_LE1', 'SW_LFN1', +1),
    ('mesa3-right', 'SW_RE1', 'SW_RFN1', -1),
]


def pcb_path(board):
    return os.path.join(HERE, board, board + '.kicad_pcb')


# ------------------------------------------------------------------ read --
def parse_pcb(s):
    """-> {ref: (x, y, rot)}, {ref: "F.Cu" / "B.Cu"}"""
    out, layer = {}, {}
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
                layer[r.group(1)] = ly.group(1)
    return out, layer


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


def norm(a):
    """Angles are equal mod 360; report them in (-180, 180]."""
    return (a + 180) % 360 - 180


# ----------------------------------------------------------------- main --
boards = {b: parse_pcb(open(pcb_path(b)).read()) for b, _, _, _ in KEYS}
new_refs = {n for _, _, n, _ in KEYS} | {'D_' + n[3:] for _, _, n, _ in KEYS}

# The diode invariant is load-bearing here, so check it before using it.
broken = []
for board, (fps, _layer) in boards.items():
    for k, (sx, sy, st) in fps.items():
        if not k.startswith('SW_'):
            continue
        d = 'D_' + k[3:]
        if d not in fps or d in new_refs:
            continue        # the new ones are what we are here to fix
        want = to_global(sx, sy, st, *DIODE_LOCAL)
        if math.dist(want, fps[d][:2]) > 0.01:
            broken.append((board, d, fps[d][:2], want))
for board, d, got, want in broken:
    print(f"diode invariant broken at {board} {d}: on board {got}, rule says "
          f"({want[0]:.3f}, {want[1]:.3f})")
if broken:
    sys.exit("refusing to place against a board whose diode rule does not hold")

print(f"pitch {PITCH:.3f} mm = {CAP[2]-CAP[0]:.1f} mm cap + {CLR:.1f} mm gap\n")

out = {}
for board, anchor, new, sign in KEYS:
    fps, _layer = boards[board]
    if anchor not in fps:
        sys.exit(f"{anchor} is not on {board}")
    ax, ay, arot = fps[anchor]
    x, y = to_global(ax, ay, arot, sign * PITCH, 0.0)
    rot = arot
    dx, dy = to_global(x, y, rot, *DIODE_LOCAL)
    drot = (rot + 180) % 360

    out.setdefault(board, {})[new] = [round(x, 4), round(y, 4), round(rot, 2)]
    out[board]['D_' + new[3:]] = [round(dx, 4), round(dy, 4), round(drot, 2)]

    print(f"{new} from {anchor} at ({ax:.3f}, {ay:.3f}) @{arot:+.1f}")
    if new in fps:
        cx, cy, crot = fps[new]
        lx, ly = to_local(ax, ay, arot, cx, cy)
        print(f"  on board  ({cx:9.3f}, {cy:8.3f}) @{crot:+6.1f}"
              f"   local ({lx:7.3f}, {ly:+6.3f})")
    print(f"  computed  ({x:9.3f}, {y:8.3f}) @{rot:+6.1f}"
          f"   local ({sign*PITCH:7.3f}, {0.0:+6.3f})")
    if new in fps:
        print(f"  moves     {math.dist((cx, cy), (x, y)):.3f} mm")

# clearance of each new cap against every key on its own board
print()
for board, _anchor, new, _sign in KEYS:
    fps, _layer = boards[board]
    final = {k: v for k, v in fps.items() if k.startswith('SW_')}
    for ref, xyr in out[board].items():
        if ref.startswith('SW_'):
            final[ref] = tuple(xyr)
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
for board, _anchor, new, _sign in KEYS:
    fps, layer = boards[board]
    x, y, _r = out[board][new]
    side = layer.get(new, 'F.Cu')
    others = {k: v for k, v in fps.items()
              if not k.startswith(('SW_', 'D_', 'H'))}
    near = sorted(((math.dist((x, y), (v[0], v[1])), k)
                   for k, v in others.items()))[:6]
    print(f"{new} is on {side} ({board}); nearest non-key parts "
          f"(centre to centre):")
    for dist, k in near:
        other = layer.get(k, '?')
        note = 'same side' if other == side else 'far side, not a clearance issue'
        print(f"    {k:8s} {dist:7.2f} mm  {other:5s}  {note}")

# The halves were placed independently from their own anchors, so their mirror
# symmetry is a genuine cross-check. Hold the new pair to what every existing
# pair already satisfies: x sums to MIRROR_X, y agrees, rotations negate.
print()
mirror = [(l, l.replace('_L', '_R', 1)) for l in sorted(out['mesa3-left'])]
worst = 0.0
for l, r in mirror:
    lx, ly, lr = out['mesa3-left'][l]
    rx, ry, rr = out['mesa3-right'][r]
    dx, dy, dr = lx + rx - MIRROR_X, ly - ry, norm(lr + rr)
    worst = max(worst, abs(dx), abs(dy), abs(dr))
    print(f"mirror {l:8s}/{r:8s}  x-sum {lx+rx:9.4f} (d {dx:+.4f})"
          f"  y {ly:8.4f}/{ry:8.4f} (d {dy:+.4f})  rot sum {norm(lr+rr):+.2f}")
if worst > 0.001:
    sys.exit(f"the two halves are not mirrored: worst deviation {worst:.4f}")

json.dump(out, open(OUT, 'w'), indent=1)
total = sum(len(v) for v in out.values())
print(f"\nwrote {os.path.basename(OUT)} "
      f"({total} footprints across {len(out)} boards)")
