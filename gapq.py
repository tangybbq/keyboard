import math, json
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
FP  = (-9.575, -4.695, 6.351, 7.450)
CAP = (-8.75, -8.25, 8.75, 8.25)
def place(rect,x,y,rot):
    x0,y0,x1,y1=rect; a=math.radians(rot); c,s=math.cos(a),math.sin(a)
    return Polygon([(x+px*c+py*s, y-px*s+py*c) for px,py in
                    [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
LI=(112.984547,60.88,-37.0); RI=(158.44,60.88,37.0)
LE=(102.754547,74.46,-37.0); RE=(168.67,74.46,37.0)
def shape(t): return place(FP,*t).union(place(CAP,*t))
print(f"LI1 centre x {LI[0]:.2f}   RI1 centre x {RI[0]:.2f}   centres {RI[0]-LI[0]:.2f} mm apart")
print(f"clear space between the LI1 and RI1 shapes (footprint u keycap): "
      f"{shape(LI).distance(shape(RI)):.2f} mm")
print(f"  ... and between LE1 and RE1: {shape(LE).distance(shape(RE)):.2f} mm")
print(f"\nwith 2 mm of board added on each side, that 21.7 becomes a {shape(LI).distance(shape(RI))-4:.2f} mm notch")

CX=135.715; NEED=13.34; LEN=20.32
print(f"\nThe Tiny2040 needs the notch <= {NEED} mm continuously over {LEN} mm of length.")
print(f"{'index shift':>12s} {'best window':>12s} {'window len':>11s}")
for d in (0,1,2,3,4,5,6,7,8):
    ll=(LI[0]+d,LI[1],LI[2]); rr=(RI[0]-d,RI[1],RI[2])
    le=(LE[0]+d,LE[1],LE[2]); re=(RE[0]-d,RE[1],RE[2])
    u = unary_union([shape(ll),shape(rr),shape(le),shape(re)]).buffer(2.0, join_style='round', quad_segs=6)
    ok=[]
    for i in range(400,900):
        y=i/10.0
        ln=LineString([(100,y),(172,y)]).difference(u)
        if ln.is_empty: ok.append((y,0.0)); continue
        g=max(ln.geoms,key=lambda p:p.length) if ln.geom_type=='MultiLineString' else ln
        x0,_,x1,_=g.bounds
        ok.append((y, x1-x0))
    best=0; run=0
    for y,w in ok:
        run = run+0.1 if w<=NEED else 0
        best=max(best,run)
    narrow=min(w for _,w in ok if w>0) if any(w>0 for _,w in ok) else 0
    print(f"{d:9d} mm {narrow:11.2f} {best:10.1f} mm" + ("   <- fits" if best>=LEN else ""))
