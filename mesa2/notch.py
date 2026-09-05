import json
from shapely.geometry import Polygon, LineString
poly = Polygon(json.load(open('outline.json')))
def notch(y):
    ln = LineString([(100,y),(172,y)]).difference(poly)
    if ln.is_empty: return None
    g = max(ln.geoms, key=lambda p: p.length) if ln.geom_type=='MultiLineString' else ln
    x0,_,x1,_ = g.bounds
    return x0, x1

CX = 135.715
PAD_IN, PAD_OUT = 6.67, 9.67    # Tiny2040 pad radial extent from the module centreline

print("Board exists OUTSIDE the notch walls. For a pad to land on board, the notch")
print(f"half-width must be <= {PAD_IN} mm, i.e. notch <= {2*PAD_IN:.2f} mm.")
print(f"Pimoroni's slot is 12.60 mm, which puts the whole 3 mm pad on copper.\n")
print(f"{'y':>6s} {'notch':>7s} {'half':>6s} {'pad on board':>13s}")
best=None
for y in range(48, 116, 2):
    n = notch(y)
    if not n:
        print(f"{y:6d} {'solid':>7s}"); continue
    half = min(CX-n[0], n[1]-CX)
    ov = max(0.0, PAD_OUT - max(PAD_IN, half))
    if best is None or half < best[1]: best=(y,half)
    print(f"{y:6d} {n[1]-n[0]:7.2f} {half:6.2f} {ov:11.2f} mm"
          + ('   <- MCU was here' if y==60 else ''))
print(f"\nnarrowest point in the finger region: y={best[0]}, half-width {best[1]:.2f} mm")
print(f"needed {PAD_IN:.2f} mm  ->  short by {best[1]-PAD_IN:.2f} mm on each side")
