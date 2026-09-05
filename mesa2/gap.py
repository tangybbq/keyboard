import math
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
exec(open('outline.py').read().split('parts=[]')[0].split('"""')[2])
parts_L=[]; parts_R=[]
for ref,(x,y,r) in SW.items():
    tgt = parts_L if '_L' in ref else parts_R
    tgt += [place(FP,x,y,r), place(CAP,x,y,r)]
L = unary_union(parts_L).buffer(MARGIN, join_style='round', quad_segs=16)
R = unary_union(parts_R).buffer(MARGIN, join_style='round', quad_segs=16)
print(f"left half  bbox {L.bounds[0]:.1f}..{L.bounds[2]:.1f} x {L.bounds[1]:.1f}..{L.bounds[3]:.1f}")
print(f"right half bbox {R.bounds[0]:.1f}..{R.bounds[2]:.1f} x {R.bounds[1]:.1f}..{R.bounds[3]:.1f}")
print(f"\nminimum gap between the two halves: {L.distance(R):.2f} mm")
print(f"\ngap profile by row (free corridor between the halves):")
print(f"{'y':>6s} {'left edge':>10s} {'right edge':>11s} {'gap':>7s}")
for y in range(24, 132, 6):
    ln = LineString([(0,y),(300,y)])
    li = ln.intersection(L); ri = ln.intersection(R)
    if li.is_empty or ri.is_empty:
        print(f"{y:6d} {'-':>10s} {'-':>11s} {'-':>7s}")
        continue
    lx = li.bounds[2]; rx = ri.bounds[0]
    print(f"{y:6d} {lx:10.1f} {rx:11.1f} {rx-lx:7.1f}")
