import json, math
from shapely.geometry import Polygon
SW=json.load(open('sw.json'))
p=Polygon(json.load(open('outline.json')))
ENV=(-9.575,-8.25,9.575,8.25)
def place(rect,x,y,rot):
    x0,y0,x1,y1=rect; a=math.radians(rot); c,s=math.cos(a),math.sin(a)
    return Polygon([(x+px*c+py*s, y-px*s+py*c) for px,py in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
le=place(ENV,*SW['SW_LE1'])
print(f"LE1 envelope reaches x = {le.bounds[2]:.2f};  + 2 mm margin = {le.bounds[2]+2:.2f}")
pk=p.convex_hull.difference(p)
gs=pk.geoms if pk.geom_type=='MultiPolygon' else [pk]
g=[q for q in gs if 60<q.centroid.x<95 and 70<q.centroid.y<95]
if g:
    q=max(g,key=lambda z:z.area)
    print(f"E-SP notch apex x = {max(x for x,y in q.exterior.coords):.2f}   area {q.area/100:.1f} cm2")
