import json
from shapely.geometry import Polygon, LineString
p=Polygon(json.load(open('outline.json')))
AX=135.7123
print("V width with the MCU block removed:")
prev=None; hits={}
for i in range(300,900):
    y=i/10.0
    ln=LineString([(AX-45,y),(AX+45,y)]).difference(p)
    if ln.is_empty: break
    g=max(ln.geoms,key=lambda q:q.length) if ln.geom_type=='MultiLineString' else ln
    if not (g.bounds[0] < AX < g.bounds[2]): break
    w=g.bounds[2]-g.bounds[0]
    if i%25==0: print(f"  y={y:6.1f}  {w:6.2f}")
    for t in (22.0, 12.6):
        if prev and prev[1] > t >= w and t not in hits: hits[t]=y
    prev=(y,w)
for t,y in sorted(hits.items(), reverse=True):
    print(f"\n  V is {t:5.2f} mm wide at y = {y:.2f}")
if 12.6 in hits:
    print(f"  -> cutout opening there means A1 origin y = {hits[12.6]-0.7:.2f}")
