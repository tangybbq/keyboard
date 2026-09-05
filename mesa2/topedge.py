import json
from shapely.geometry import Polygon, LineString
p=Polygon(json.load(open('outline.json')))
for x in (129.41, 135.715, 142.02):
    ln=LineString([(x,0),(x,140)]).intersection(p)
    print(f"x={x:7.2f}: board runs y {ln.bounds[1]:.2f}..{ln.bounds[3]:.2f}")
print("\nA1 cutout opening is at y=57.70, so a channel from the top edge")
print("down to it would be that much long at each x above.")
