import math, json
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
MARGIN=2.0
FP=(-9.575,-7.450,9.575,7.450); CAP=(-8.75,-8.25,8.75,8.25)
SW=json.load(open('sw.json'))
def place(r,x,y,rot):
    x0,y0,x1,y1=r; a=math.radians(rot); c,s=math.cos(a),math.sin(a)
    return Polygon([(x+px*c+py*s, y-px*s+py*c) for px,py in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
def shape(ref):
    x,y,r=SW[ref]; return place(FP,x,y,r).union(place(CAP,x,y,r))
L=unary_union([shape('SW_LSP1'),shape('SW_LBK1')]).convex_hull.buffer(MARGIN,join_style='mitre')
R=unary_union([shape('SW_RSP1'),shape('SW_RBK1')]).convex_hull.buffer(MARGIN,join_style='mitre')
board=Polygon(json.load(open('outline.json')))
AX=(SW['SW_LR1'][0]+SW['SW_RR1'][0])/2
print(f"mirror axis {AX:.3f}; board bottom edge y = {board.bounds[3]:.2f}\n")
print(f"{'y':>7s} {'left thumb ends':>16s} {'right begins':>13s} {'free':>7s}")
for y in [b/2 for b in range(2*100, 2*137)]:
    ln=LineString([(AX-40,y),(AX+40,y)])
    li=ln.intersection(L); ri=ln.intersection(R)
    if li.is_empty or ri.is_empty: continue
    lx=li.bounds[2]; rx=ri.bounds[0]
    if y*2 % 4 == 0:
        print(f"{y:7.1f} {lx:16.2f} {rx:13.2f} {rx-lx:7.2f}")
