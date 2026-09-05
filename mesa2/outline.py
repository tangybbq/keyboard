#!/usr/bin/env python3
"""Derive the mesa2 board outline from the placed switches.

Run:  uv run --with shapely python outline.py

The outline is a MITRE offset of the switch union - i.e. every edge is a line
MARGIN mm from a switch edge, and every corner is where two such lines meet.
No hulls, no fillets, no morphological closing: as tight as the switches allow.

Then, and only then, concave pockets that come out too narrow to be useful are
filled with a straight chord across their mouth. "Too narrow" = the pocket cannot
contain a circle of radius FILL_R. Big deliberate notches survive; the slivers
between splayed columns do not.

The socket footprint is asymmetric (x -9.575..6.351) and the two hands' sockets
are rotated rather than mirrored, so a centred envelope is used instead - that is
what makes the result mirror-symmetric, and it tolerates a socket being spun 180
during routing.
"""
import math, json
from shapely.geometry import Polygon, LineString, box, MultiPolygon
from shapely.ops import unary_union

MARGIN  = 2.0
MITRE   = 100.0    # effectively unlimited: true line-intersection corners
FILL_R  = 6.0      # pockets that cannot hold a circle of this radius get filled
# The finger->thumb connector is a box with a VERTICAL outer edge at ARM_X,
# not a band along LE1->LSP1 - that band ran 6 degrees off vertical, because that
# is the bearing between those two switch centres. The notch wall is the buffered
# edge, so it ends up at ARM_X - MARGIN.
ARM_X   = 110.0
ARM_Y0  = 70.0
ARM_Y1  = 112.0
BRIDGE_W= 15.0     # thumb-to-thumb bridge
# Per-key extension of the envelope along its long (local x) axis, as
# (inward, outward) in mm - inward meaning toward the board centre. The sign is
# resolved per hand, so the result stays mirror-symmetric: a left switch extends
# local +x inward, a right switch extends local -x.
# Widening a switch makes it overlap its neighbours' offsets, closing the little
# nick that otherwise appears between two splayed columns.
WIDEN = {
    'O': (5.0, 7.0),
    'I': (7.0, 7.0),
    'S': (0.0, 3.0),
}
# V notch between the thumb clusters. Its base is taken from the board's own
# bottom-edge corners, so the V starts exactly at the corner instead of leaving a
# horizontal run of bottom edge before it.
NOTCH_APEX  = 120.5
A1      = (135.715, 59.7251)  # solved: the V is exactly 12.60 mm at the cutout opening
A1_W, A1_L = 18.0, 20.32
# The V is within ~0.06 mm of 12.6 mm at the opening, so this cut is essentially
# degenerate - it removes slivers, not tabs - but it forces the two endpoints to
# land exactly on the board edge, which KiCad requires.
CHANNEL = True

# ONE rectangle per switch, covering both the socket envelope and the keycap.
# Using the union of two differently-shaped rects makes their edges cross, and the
# mitre offset then reproduces every one of those crossings as a stair step.
ENV = (-9.575, -8.25, 9.575, 8.25)
SW  = json.load(open('sw.json'))

def place(rect, x, y, rot):
    x0,y0,x1,y1 = rect
    a=math.radians(rot); c,s=math.cos(a),math.sin(a)
    return Polygon([(x + px*c + py*s, y - px*s + py*c)
                    for px,py in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])

def shape(ref):
    x,y,r = SW[ref]
    ein, eout = WIDEN.get(ref[4:-1], (0.0, 0.0))
    x0,y0,x1,y1 = ENV
    if ref[3] == 'L': x0, x1 = x0-eout, x1+ein     # local +x points toward the centre
    else:             x0, x1 = x0-ein,  x1+eout    # mirrored on the right hand
    return place((x0, y0, x1, y1), x, y, r)

def band(a, b, w):
    """straight-sided connector between two switch centres - flat caps, no arcs"""
    return LineString([SW[a][:2], SW[b][:2]]).buffer(
        w/2, cap_style='flat', join_style='mitre', mitre_limit=MITRE)

pieces  = [shape(r) for r in SW]
AXIS0 = (SW['SW_LR1'][0] + SW['SW_RR1'][0]) / 2
pieces += [box(ARM_X, ARM_Y0, AXIS0, ARM_Y1),
           box(2*AXIS0-AXIS0, ARM_Y0, 2*AXIS0-ARM_X, ARM_Y1)]
pieces += [band('SW_LBK1','SW_RSP1',BRIDGE_W)]
# top edge inset by MARGIN so the buffer lands it exactly on the cutout opening
pieces += [box(A1[0]-A1_W/2, A1[1]+0.7+MARGIN, A1[0]+A1_W/2, A1[1]+A1_L)]

raw = unary_union(pieces).buffer(MARGIN, join_style='mitre', mitre_limit=MITRE)
raw = Polygon(raw.exterior)

# fill only the pockets that are too narrow to be worth keeping
pockets = raw.convex_hull.difference(raw)
if pockets.geom_type == 'Polygon': pockets = MultiPolygon([pockets])
keep, fill = [], []
for p in pockets.geoms:
    (fill if p.buffer(-FILL_R).is_empty else keep).append(p)
out = unary_union([raw] + fill)
out = Polygon(out.exterior)
# Channel from the board edge down to the MCU cutout's opening, so the slot has a
# way out and the outline can close around it. Cut LAST - anything after refills it.
AXIS = (SW['SW_LR1'][0] + SW['SW_RR1'][0]) / 2
ybot = out.bounds[3]
onbot = [c for c in out.exterior.coords if abs(c[1]-ybot) < 0.01]
lbase = max((c for c in onbot if c[0] < AXIS), key=lambda c: c[0])
rbase = min((c for c in onbot if c[0] > AXIS), key=lambda c: c[0])
print(f"  thumb notch base taken from the bottom-edge corners: "
      f"({lbase[0]:.2f},{lbase[1]:.2f}) and ({rbase[0]:.2f},{rbase[1]:.2f})")
# quad, not a triangle: the sloped edges must reach the corners AT ybot. A
# triangle whose base is below ybot is wider down there and narrower at the
# board edge, which leaves a short horizontal run before the V starts.
out = out.difference(Polygon([(AXIS, NOTCH_APEX),
                              (rbase[0], ybot), (rbase[0], ybot+5),
                              (lbase[0], ybot+5), (lbase[0], ybot)]))
if out.geom_type == 'MultiPolygon':
    print(f"!! thumb notch severed the board into {len(out.geoms)} pieces")
    out = max(out.geoms, key=lambda g: g.area)
out = Polygon(out.exterior)

if CHANNEL:
    out = out.difference(box(A1[0]-6.3, -1000, A1[0]+6.3, A1[1]+0.7))
    if out.geom_type == 'MultiPolygon': out = max(out.geoms, key=lambda g: g.area)
    out = Polygon(out.exterior)
print(f"concave pockets: {len(keep)} kept, {len(fill)} filled as too narrow "
      f"(< {2*FILL_R:.0f} mm across)")
for p in sorted(keep, key=lambda g:-g.area):
    print(f"    kept  {p.area/100:5.1f} cm2  centred ({p.centroid.x:6.1f},{p.centroid.y:5.1f})")

x0,y0,x1,y1 = out.bounds
print(f"\noutline: {len(out.exterior.coords)-1} vertices")
print(f"  bbox  {x0:.2f}..{x1:.2f} x {y0:.2f}..{y1:.2f}   ({x1-x0:.1f} x {y1-y0:.1f} mm)")
print(f"  area  {out.area/100:.1f} cm2   perimeter {out.length:.0f} mm")
cl = sorted((out.exterior.distance(shape(r)), r) for r in SW)
print(f"  every switch inside: {all(out.contains(shape(r)) for r in SW)}"
      f"   tightest {cl[0][0]:.2f} mm ({cl[0][1]})")
AXIS = (SW['SW_LR1'][0] + SW['SW_RR1'][0]) / 2
sym = out.symmetric_difference(Polygon([(2*AXIS-x,y) for x,y in out.exterior.coords])).area
print(f"  mirror residual about x={AXIS:.4f}: {sym:.3f} mm2"
      f"  ({'symmetric' if sym < 1.0 else 'NOT SYMMETRIC'})")

oy = A1[1]+0.7
from shapely.geometry import Point
for ex in (A1[0]-6.3, A1[0]+6.3):
    print(f"  cutout end ({ex:.3f},{oy:.2f}) -> distance to board edge "
          f"{out.exterior.distance(Point(ex,oy)):.3f} mm")
# drop vertices closer than 10 um to the previous one - the channel cut leaves a
# few micron-scale slivers, which would become zero-length DXF segments
ring = [list(c) for c in out.exterior.coords[:-1]]
clean = [ring[0]]
for p in ring[1:]:
    if math.dist(p, clean[-1]) > 0.03: clean.append(p)
if math.dist(clean[0], clean[-1]) <= 0.03: clean.pop()
print(f"  vertices: {len(ring)} -> {len(clean)} after dropping micron slivers")
json.dump([[round(c[0],3), round(c[1],3)] for c in clean], open('outline.json','w'))
json.dump({'a1': list(A1), 'a1_rot': -90,
           'opening_y': A1[1]+0.7, 'opening_w': 12.6,
           'opening_x': [A1[0]-6.3, A1[0]+6.3]}, open('outline-meta.json','w'), indent=1)
print("\nwrote outline.json")
