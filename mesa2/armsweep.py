import io, contextlib, json
from shapely.geometry import Polygon
src = open('outline.py').read()
print(f"{'ARM_W':>6s} {'E-SP notch apex x':>18s} {'notch area':>11s}")
for w in (9.0, 7.0, 5.0, 3.0, 1.5):
    s = src.replace("ARM_W   = 9.0", f"ARM_W   = {w}")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(s, 'o', 'exec'), {})
    p = Polygon(json.load(open('outline.json')))
    pockets = p.convex_hull.difference(p)
    gs = pockets.geoms if pockets.geom_type=='MultiPolygon' else [pockets]
    left = [g for g in gs if 60 < g.centroid.x < 95 and 70 < g.centroid.y < 95]
    if left:
        g = max(left, key=lambda q: q.area)
        print(f"{w:6.1f} {max(x for x,y in g.exterior.coords):18.2f} {g.area/100:9.1f} cm2")
