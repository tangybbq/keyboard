import math, json, io, contextlib
from shapely.geometry import Polygon, LineString, box, MultiPolygon, Point
from shapely.ops import unary_union
src = open('outline.py').read()

def vgap(a1y):
    """V width at the cutout opening line, minus 12.6, with the MCU block removed"""
    s = src.replace("A1      = (135.715, 59.80)", f"A1      = (135.715, {a1y})")
    s = s.replace("CHANNEL = True", "CHANNEL = False")
    s = s.replace("pieces += [box(A1[0]-A1_W/2, A1[1]+0.7+MARGIN, A1[0]+A1_W/2, A1[1]+A1_L)]","")
    g = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(s, 'o', 'exec'), g)
    p = Polygon(json.load(open('outline.json')))
    oy = a1y + 0.7
    ln = LineString([(135.7123-45, oy), (135.7123+45, oy)]).difference(p)
    seg = max(ln.geoms, key=lambda q: q.length) if ln.geom_type=='MultiLineString' else ln
    return (seg.bounds[2]-seg.bounds[0]) - 12.6

lo, hi = 59.0, 61.5
for _ in range(40):
    mid = (lo+hi)/2
    if vgap(mid) > 0: lo = mid
    else: hi = mid
print(f"A1 y giving a V of exactly 12.60 mm at the opening: {hi:.4f}")
print(f"  residual V error: {vgap(hi)*1000:+.1f} um")
