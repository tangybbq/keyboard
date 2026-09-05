import math
from shapely.geometry import Polygon
FP  = (-9.575,-4.695,6.351,7.450); CAP=(-8.75,-8.25,8.75,8.25)
def place(r,x,y,rot):
    x0,y0,x1,y1=r; a=math.radians(rot); c,s=math.cos(a),math.sin(a)
    return Polygon([(x+px*c+py*s, y-px*s+py*c) for px,py in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])
LI=(112.984547,60.88,-37.0); RI=(158.44,60.88,37.0)
sh=lambda t: place(FP,*t).union(place(CAP,*t))
clear = sh(LI).distance(sh(RI))
CX=135.715
print(f"clear space between the LI1 and RI1 shapes: {clear:.2f} mm  (+/- {clear/2:.2f} from centre)")
print(f"\nIf the board is SOLID there rather than notched:")
print(f"  Pimoroni cutout      12.60 mm wide  -> board starts  6.30 mm from centre")
print(f"  board available out to               {clear/2:.2f} mm from centre")
print(f"  pads sit at 6.67 .. 9.67 mm from centre")
ok = 6.67 >= 6.30 and 9.67 <= clear/2
print(f"  -> pads fully on copper: {ok}   (inner {6.67-6.30:+.2f} mm clear of the slot,"
      f" outer {clear/2-9.67:+.2f} mm inside the switch gap)")
print(f"  module body is 18.00 mm wide -> {clear-18.0:.2f} mm spare in a {clear:.2f} mm gap")
A1=(135.715, 57.0)
print(f"\nA1 now at {A1} rot -90:")
print(f"  cutout opening (board edge must meet it) at y = {A1[1]+0.7:.2f}, x {CX-6.3:.2f}..{CX+6.3:.2f}")
print(f"  cutout closed end at y = {A1[1]+0.7+16.92:.2f}; module body ends y = {A1[1]+0.7+20.32:.2f}")
