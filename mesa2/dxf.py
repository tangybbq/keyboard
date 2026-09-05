#!/usr/bin/env python3
"""Write outline.json to a DXF for KiCad's File > Import > Graphics.

The outline is emitted as an OPEN chain: the one segment that spans the MCU
cutout's opening is omitted, because the Tiny2040 footprint's own Edge.Cuts
polyline closes that gap. Emitting it as well gives KiCad a T-junction at each
endpoint - a closed board edge with the cutout branching off it - which it
rejects as not a valid outline.

Also: a HEADER declaring millimetres, and coordinates relative to the outline's
own bounding box (KiCad checks the import against the page size, and an absolute
offset counts against that budget). Layer "Edge_Cuts", DXF y = -(KiCad y).
"""
import json
pts  = json.load(open('outline.json'))
meta = json.load(open('outline-meta.json'))   # written by outline.py - single source
OPEN_Y = meta['opening_y']
OPEN_W = meta['opening_w']
OPEN_X = meta['opening_x']

n = len(pts)
segs = [(pts[i], pts[(i+1) % n]) for i in range(n)]
gap = [k for k,(a,b) in enumerate(segs)
       if abs(a[1]-OPEN_Y) < 0.05 and abs(b[1]-OPEN_Y) < 0.05
       and abs(abs(a[0]-b[0]) - OPEN_W) < 0.05]
if len(gap) != 1:
    raise SystemExit(f"expected exactly one segment across the cutout opening, found {len(gap)}")
k = gap[0]
dropped = segs.pop(k)

ox = min(p[0] for p in pts); oy = min(p[1] for p in pts)
out = ["0","SECTION","2","HEADER",
       "9","$INSUNITS","70","4", "9","$MEASUREMENT","70","1",
       "0","ENDSEC","0","SECTION","2","ENTITIES"]
for (x1,y1),(x2,y2) in segs:
    out += ["0","LINE","8","Edge_Cuts",
            "10",f"{x1-ox:.4f}","20",f"{-(y1-oy):.4f}","30","0.0",
            "11",f"{x2-ox:.4f}","21",f"{-(y2-oy):.4f}","31","0.0"]
out += ["0","ENDSEC","0","EOF"]
open('mesa2-Edge_Cuts.dxf','w').write("\n".join(out)+"\n")

w = max(p[0] for p in pts)-ox; h = max(p[1] for p in pts)-oy
print(f"wrote mesa2-Edge_Cuts.dxf  {len(segs)} LINE entities (open chain), units = mm")
print(f"  omitted the segment across the cutout opening: "
      f"({dropped[0][0]:.3f},{dropped[0][1]:.2f}) -> ({dropped[1][0]:.3f},{dropped[1][1]:.2f})")
print(f"  the footprint's cutout closes that gap")
print(f"  graphic size {w:.2f} x {h:.2f} mm")
print(f"  IMPORT AT    x = {ox:.3f}   y = {oy:.3f}")
# the chain must be contiguous end to end, and its two loose ends must be the
# cutout's open endpoints
chain = segs[k:] + segs[:k]
assert all(chain[i][1] == chain[i+1][0] for i in range(len(chain)-1)), "chain is broken"
ends = (chain[0][0], chain[-1][1])
print(f"  loose ends:  ({ends[0][0]:.3f}, {ends[0][1]:.2f}) and ({ends[1][0]:.3f}, {ends[1][1]:.2f})")
exp = sorted(OPEN_X)
got = sorted([ends[0][0], ends[1][0]])
print(f"  match the cutout endpoints ({exp[0]:.3f}, {exp[1]:.3f}): "
      f"{all(abs(g-e) < 0.01 for g,e in zip(got,exp)) and all(abs(p[1]-OPEN_Y)<0.01 for p in ends)}")
