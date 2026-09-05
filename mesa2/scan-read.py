#!/usr/bin/env python3
"""Marks read off hand-scan-1.pdf, in the sheet's grid frame (mm).

Grid calibration from the printed 20 mm lines: origin px (150, 428),
7.8636 px/mm horizontal, 7.8786 px/mm vertical -> 199.7 dpi. The red origin
cross lands at (-0.03, +0.01) mm, so the sheet printed at true scale.

Marks are listed in the order they appear along the column, smallest Y first.
NO interpretation of which one is the rest position - see the notes.
"""
import math

MARKS = {
 'L-pinky':  [(15.53,30.50),(29.27,35.07),(32.66,38.48)],
 'L-ring':   [(55.32,20.48),(55.68,29.34),(54.99,39.07)],
 'L-middle': [(73.99,20.13),(73.63,28.25),(73.54,40.11)],
 'L-index':  [(99.18,44.48),(92.72,50.59),(86.81,59.81)],
 'L-thumb':  [(84.47,85.49),(96.94,94.97),(109.96,110.62)],
 'R-index':  [(132.93,41.01),(140.21,50.14),(145.28,58.50)],
 'R-middle': [(147.31,20.32),(150.60,26.34),(154.55,35.57)],
 'R-ring':   [(172.58,17.69),(173.37,24.63),(173.81,35.69)],
 'R-pinky':  [(214.03,21.51),(202.06,29.35),(198.54,34.01)],
 'R-thumb':  [(147.08,83.95),(135.69,91.23),(123.95,110.32)],
}

def fit_angle(pts):
    """principal-axis direction, as degrees from +Y (straight away from you).
    Positive = the far end leans toward +X."""
    n=len(pts); mx=sum(p[0] for p in pts)/n; my=sum(p[1] for p in pts)/n
    sxx=sum((p[0]-mx)**2 for p in pts); syy=sum((p[1]-my)**2 for p in pts)
    sxy=sum((p[0]-mx)*(p[1]-my) for p in pts)
    th=0.5*math.atan2(2*sxy, sxx-syy)          # major axis, from +X
    vx,vy=math.cos(th),math.sin(th)
    if vy<0: vx,vy=-vx,-vy                     # point it toward +Y
    return math.degrees(math.atan2(vx,vy)), (mx,my)

def resid(pts):
    a,(mx,my)=fit_angle(pts); r=math.radians(a)
    vx,vy=math.sin(r),math.cos(r)
    return max(abs((p[0]-mx)*vy-(p[1]-my)*vx) for p in pts)

print("finger      m1              m2              m3          gaps mm    span   axis    bow")
for k,p in MARKS.items():
    d1=math.dist(p[0],p[1]); d2=math.dist(p[1],p[2]); sp=math.dist(p[0],p[2])
    a,_=fit_angle(p)
    print(f"{k:9s} "+" ".join(f"({x:6.2f},{y:6.2f})" for x,y in p)
          +f"  {d1:5.2f} {d2:5.2f}  {sp:5.2f}  {a:+6.1f}  {resid(p):4.2f}")

print("\nColumn axis, degrees from straight-away (+ = far end leans toward +X):")
for h,sgn in (('L',1),('R',1)):
    row=[]
    for f in ('pinky','ring','middle','index'):
        a,_=fit_angle(MARKS[f'{h}-{f}']); row.append(f"{f} {a:+6.1f}")
    print(f"  {h}: "+"   ".join(row))

print("\nMiddle mark of each finger, treated as the rest position:")
for h in 'LR':
    mids={f:MARKS[f'{h}-{f}'][1] for f in ('pinky','ring','middle','index')}
    print(f"  {h}: "+"  ".join(f"{f} ({p[0]:6.2f},{p[1]:6.2f})" for f,p in mids.items()))
    order=['pinky','ring','middle','index'] if h=='L' else ['index','middle','ring','pinky']
    for a,b in zip(order,order[1:]):
        dx=mids[b][0]-mids[a][0]; dy=mids[b][1]-mids[a][1]
        print(f"       {a:6s}->{b:6s}  dx {dx:+7.2f}  dy {dy:+7.2f}  dist {math.hypot(dx,dy):6.2f}")

def circle3(p):
    (x1,y1),(x2,y2),(x3,y3)=p
    a=2*(x2-x1); b=2*(y2-y1); c=x2*x2+y2*y2-x1*x1-y1*y1
    d=2*(x3-x2); e=2*(y3-y2); f=x3*x3+y3*y3-x2*x2-y2*y2
    det=a*e-b*d
    if abs(det)<1e-9: return None
    cx=(c*e-b*f)/det; cy=(a*f-c*d)/det
    return (cx,cy), math.hypot(x1-cx,y1-cy)

print("\nThumb arcs (circle through the three marks):")
for k in ('L-thumb','R-thumb'):
    r=circle3(MARKS[k])
    if r:
        (cx,cy),rad=r
        print(f"  {k}: pivot ({cx:7.2f},{cy:7.2f})  radius {rad:6.2f} mm"
              f"   chord m1->m3 {math.dist(MARKS[k][0],MARKS[k][2]):.2f} mm")
