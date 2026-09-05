#!/usr/bin/env python3
"""mesa2 key layout, derived from hand-scan-1.

Method:
  1. Mirror the right hand about the axis midway between the two hand centroids.
  2. Average it with the left hand, mark for mark. That is the "average of my
     measurements" and it forces a symmetric board; the unibody angle survives
     as the average of the two hands' rotations.
  3. Each finger column: centre = the rest mark (m2), axis = principal direction
     of its three marks, two keys at +/- rock/2 along that axis.
  4. Thumbs: two keys on the measured arc, centred on it, caps tangent.
  5. Emit the averaged hand and its mirror = 20 keys.

Frame is the measurement sheet's: +X right, +Y toward you.
"""
import math, json

ROCK = 17.0          # row pitch, fixed by the caps (16.5 + 0.5)
THUMB_PITCH = 18.0   # thumb pair separation along the arc

MARKS = {
 'L': {'pinky':  [(15.53,30.50),(29.27,35.07),(32.66,38.48)],
       'ring':   [(55.32,20.48),(55.68,29.34),(54.99,39.07)],
       'middle': [(73.99,20.13),(73.63,28.25),(73.54,40.11)],
       'index':  [(99.18,44.48),(92.72,50.59),(86.81,59.81)],
       'thumb':  [(84.47,85.49),(96.94,94.97),(109.96,110.62)]},
 'R': {'pinky':  [(214.03,21.51),(202.06,29.35),(198.54,34.01)],
       'ring':   [(172.58,17.69),(173.37,24.63),(173.81,35.69)],
       'middle': [(147.31,20.32),(150.60,26.34),(154.55,35.57)],
       'index':  [(132.93,41.01),(140.21,50.14),(145.28,58.50)],
       'thumb':  [(147.08,83.95),(135.69,91.23),(123.95,110.32)]},
}
FINGERS = ['pinky','ring','middle','index']

def centroid(h):
    pts=[p for f in h.values() for p in f]
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))

cL, cR = centroid(MARKS['L']), centroid(MARKS['R'])
AXIS = (cL[0]+cR[0])/2
print(f"left centroid  ({cL[0]:7.2f}, {cL[1]:6.2f})")
print(f"right centroid ({cR[0]:7.2f}, {cR[1]:6.2f})   dy {cR[1]-cL[1]:+.2f} mm")
print(f"mirror axis x = {AXIS:.2f}\n")

# mirror the right hand into left-hand coordinates, then average mark for mark
avg={}
for f in FINGERS+['thumb']:
    avg[f]=[((l[0]+(2*AXIS-r[0]))/2, (l[1]+r[1])/2)
            for l,r in zip(MARKS['L'][f], MARKS['R'][f])]

def axis_angle(pts):
    """principal direction, degrees from +Y (away from you); + leans toward +X"""
    n=len(pts); mx=sum(p[0] for p in pts)/n; my=sum(p[1] for p in pts)/n
    sxx=sum((p[0]-mx)**2 for p in pts); syy=sum((p[1]-my)**2 for p in pts)
    sxy=sum((p[0]-mx)*(p[1]-my) for p in pts)
    th=0.5*math.atan2(2*sxy, sxx-syy)
    vx,vy=math.cos(th),math.sin(th)
    if vy<0: vx,vy=-vx,-vy
    return math.degrees(math.atan2(vx,vy))

print("averaged hand, per finger (L/R disagreement = spread between the two hands):")
cols={}
for f in FINGERS:
    a = axis_angle(avg[f])
    aL, aR = axis_angle(MARKS['L'][f]), -axis_angle(MARKS['R'][f])
    if f=='pinky':
        # the pinky is an elbow, not a line: use the chord through the extremes
        m1,m3 = avg[f][0], avg[f][2]
        a = math.degrees(math.atan2(m1[0]-m3[0], m1[1]-m3[1]))
        if a>90: a-=180
        if a<-90: a+=180
    cols[f]=(avg[f][1], a)                      # centre = rest mark, plus axis
    print(f"  {f:7s} centre ({avg[f][1][0]:7.2f},{avg[f][1][1]:6.2f})  axis {a:+6.1f} deg"
          f"   (L {aL:+6.1f} / R-mirrored {aR:+6.1f}, spread {abs(aL-aR):4.1f})")

print("\nspreads and staggers between averaged column centres (outer -> inner):")
for a,b in zip(FINGERS, FINGERS[1:]):
    pa,pb = cols[a][0], cols[b][0]
    print(f"  {a:6s} -> {b:6s}  dx {pb[0]-pa[0]:+7.2f}  dy {pb[1]-pa[1]:+7.2f}")

json.dump({'axis':AXIS,'avg':{k:[list(p) for p in v] for k,v in avg.items()},
           'cols':{k:[list(v[0]),v[1]] for k,v in cols.items()}}, open('layout.json','w'), indent=1)

# ---------------------------------------------------------------- placement --
# Matrix -> finger, from the netlist. Left COL_A..D = pinky..index; right is
# mirror-ordered COL_A..D = index..pinky, which makes each finger carry the same
# key pair on both hands (pinky R/A, ring S/O, middle N/T, index I/E).
FAR  = {'pinky':'R','ring':'S','middle':'N','index':'I'}   # ROW_A / ROW_C
NEAR = {'pinky':'A','ring':'O','middle':'T','index':'E'}   # ROW_B / ROW_D
THUMB_OUTER = {'L':'SP','R':'BK'}      # LSP sits at mesa1's outer thumb today
THUMB_INNER = {'L':'BK','R':'SP'}

ORIGIN_X, ORIGIN_Y = 150.0, 34.0       # mirror axis / far-row datum on the board

def unit(a):
    r=math.radians(a); return (math.sin(r), math.cos(r))   # +Y-ward, leans to +X

# Minimum outward nudge per column so no two caps come closer than 0.5 mm.
# Angles and staggers are left exactly as measured; only the outward spacing
# moves, and only as far as the caps demand.
NUDGE = {'pinky':1.7,'ring':0.5,'middle':0.1,'index':0.1}

keys={}
for f in FINGERS:
    (cx,cy), a = cols[f]
    cx -= NUDGE[f]
    ux,uy = unit(a)
    keys[(f,'far')]  = (cx-ux*ROCK/2, cy-uy*ROCK/2, a)
    keys[(f,'near')] = (cx+ux*ROCK/2, cy+uy*ROCK/2, a)

# thumbs: two keys on the measured arc, centred, caps across the travel
t = avg['thumb']
mid = ((t[0][0]+t[2][0])/2, (t[0][1]+t[2][1])/2)
chord = math.degrees(math.atan2(-(t[2][1]-t[0][1]), t[2][0]-t[0][0]))   # CCW from +X, screen
hx = math.cos(math.radians(chord)); hy = -math.sin(math.radians(chord))
keys[('thumb','outer')] = (mid[0]-hx*THUMB_PITCH/2, mid[1]-hy*THUMB_PITCH/2, chord+90)
keys[('thumb','inner')] = (mid[0]+hx*THUMB_PITCH/2, mid[1]+hy*THUMB_PITCH/2, chord+90)
print(f"\nthumb arc: chord {math.dist(t[0],t[2]):.2f} mm at {chord:+.1f} deg from +X;"
      f" pair {THUMB_PITCH} mm apart, caps across the travel")

def norm(a):                       # socket may sit at a or a+180; pick nearest 0
    while a >  90: a -= 180
    while a <= -90: a += 180
    return a

# The hand separation is already in the measurement: both hands were marked on
# one sheet, so AXIS (midway between the two centroids) is the real mirror line.
# Translate that to the board rather than inventing a margin.
ys=[v[1] for v in keys.values()]
sx, sy = ORIGIN_X - AXIS, ORIGIN_Y - min(ys)

place={}
for (f,which),(x,y,a) in keys.items():
    if f=='thumb':
        nm = THUMB_OUTER if which=='outer' else THUMB_INNER
        lref, rref = f'SW_L{nm["L"]}1', f'SW_R{nm["R"]}1'
    else:
        k = FAR[f] if which=='far' else NEAR[f]
        lref, rref = f'SW_L{k}1', f'SW_R{k}1'
    X, Y = x+sx, y+sy
    place[lref] = (X, Y, norm(a))
    place[rref] = (2*ORIGIN_X-X, Y, norm(-a))

print(f"\n{'ref':9s} {'x':>8s} {'y':>8s} {'rot':>7s}   finger / row")
lbl={v:k for k,v in [((f,w),(f,w)) for f,w in keys]}
for (f,which) in sorted(keys, key=lambda k:(FINGERS+['thumb']).index(k[0])):
    for hand in 'LR':
        if f=='thumb':
            nm=(THUMB_OUTER if which=='outer' else THUMB_INNER)[hand]
            ref=f'SW_{hand}{nm}1'
        else:
            ref=f'SW_{hand}{(FAR if which=="far" else NEAR)[f]}1'
        X,Y,R = place[ref]
        print(f"{ref:9s} {X:8.2f} {Y:8.2f} {R:+7.1f}   {f} / {which}")
json.dump(place, open('placement.json','w'), indent=1)
print(f"\nkey field: x {min(v[0] for v in place.values()):.1f}..{max(v[0] for v in place.values()):.1f}"
      f"  y {min(v[1] for v in place.values()):.1f}..{max(v[1] for v in place.values()):.1f}"
      f"   ({max(v[0] for v in place.values())-min(v[0] for v in place.values()):.1f}"
      f" x {max(v[1] for v in place.values())-min(v[1] for v in place.values()):.1f} mm)")

# ------------------------------------------------------- keycap clearance ----
CAP=(17.5,16.5)
def corners(cx,cy,th):
    w,h=CAP; a=math.radians(th); c,s_=math.cos(a),math.sin(a)
    return [(cx+dx*c+dy*s_, cy-dx*s_+dy*c) for dx,dy in
            [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
def gap(A,B):
    best=-1e9
    for poly in (A,B):
        for i in range(4):
            x1,y1=poly[i]; x2,y2=poly[(i+1)%4]
            nx,ny=-(y2-y1),(x2-x1); L=math.hypot(nx,ny); nx,ny=nx/L,ny/L
            pa=[p[0]*nx+p[1]*ny for p in A]; pb=[p[0]*nx+p[1]*ny for p in B]
            best=max(best,max(min(pb)-max(pa),min(pa)-max(pb)))
    return best
import itertools
caps={r:corners(*v) for r,v in place.items()}
bad=[]
for (ra,A),(rb,B) in itertools.combinations(caps.items(),2):
    g=gap(A,B)
    if g < 0.5: bad.append((g,ra,rb))
bad.sort()
print(f"\nkeycap clearance ({len(caps)} caps, {len(caps)*(len(caps)-1)//2} pairs), "
      f"anything under 0.50 mm:")
if not bad: print("   all clear")
for g,ra,rb in bad[:14]:
    print(f"   {g:+6.2f} mm  {ra} / {rb}" + ("   *** OVERLAP ***" if g<0 else ""))
