#!/usr/bin/env python3
"""Place every diode at the same offset from its switch as D_LR1 has from SW_LR1.

The offset is taken in the SWITCH'S LOCAL FRAME, so it rotates with the column.
That is also what makes it come out mirror-symmetric: the right-hand switches are
already at negated rotations, so an identical local offset lands each right-hand
diode at the mirror image of its left-hand twin.
"""
import math, json

SW = {  # live board state, x, y, rotation
 'SW_LR1':(36.424547,45.0,57.9),   'SW_RR1':(235.0,45.0,-57.9),
 'SW_LA1':(50.814547,54.04,57.9),  'SW_RA1':(220.61,54.04,-57.9),
 'SW_LS1':(72.734547,35.8,-2.5),   'SW_RS1':(198.69,35.8,2.5),
 'SW_LO1':(72.004547,52.78,-2.5),  'SW_RO1':(199.42,52.78,2.5),
 'SW_LN1':(94.924547,36.29,-12.2), 'SW_RN1':(176.5,36.29,12.2),
 'SW_LT1':(91.334547,52.91,-12.2), 'SW_RT1':(180.09,52.91,12.2),
 'SW_LI1':(112.984547,60.88,-37.0),'SW_RI1':(158.44,60.88,37.0),
 'SW_LE1':(102.754547,74.46,-37.0),'SW_RE1':(168.67,74.46,37.0),
 'SW_LSP1':(106.384547,108.36,43.4),'SW_RBK1':(165.04,108.36,-43.4),
 'SW_LBK1':(118.744547,121.45,43.4),'SW_RSP1':(152.68,121.45,-43.4),
}
REF = ('SW_LR1', (36.424547,45.0,57.9), 'D_LR1', (32.3,42.4,57.0))

def to_local(sx,sy,st, dx,dy):
    a=math.radians(st); c,s=math.cos(a),math.sin(a)
    ux,uy = dx-sx, dy-sy
    return (ux*c - uy*s, ux*s + uy*c)

def to_world(sx,sy,st, lx,ly):
    a=math.radians(st); c,s=math.cos(a),math.sin(a)
    return (sx + lx*c + ly*s, sy - lx*s + ly*c)

(sx,sy,st) = REF[1]; (dx,dy,dr) = REF[3]
lx,ly = to_local(sx,sy,st,dx,dy)
drel  = dr - st
print(f"from your {REF[2]} vs {REF[0]}:")
print(f"  local offset  ({lx:+.4f}, {ly:+.4f}) mm   -- laterally centred to {abs(lx)*1000:.0f} um")
print(f"  rotation      diode {dr}  switch {st}  ->  {drel:+.1f} deg relative")
print(f"\nUsing relative rotation 0 (diode aligned with its switch); {drel:+.1f} looks like")
print(f"57 typed for 57.9, and keeping it would break mirror symmetry on rotations.\n")
lx = 0.0 if abs(lx) < 0.05 else lx      # snap the 11 um lateral to exactly centred

out={}
for swref,(x,y,r) in SW.items():
    dref = 'D_' + swref.split('_',1)[1]
    wx,wy = to_world(x,y,r, lx,ly)
    out[dref] = (round(wx,3), round(wy,3), round(r,2))
print(f"{'diode':9s} {'x':>9s} {'y':>8s} {'rot':>7s}")
for k in sorted(out): print(f"{k:9s} {out[k][0]:9.3f} {out[k][1]:8.3f} {out[k][2]:+7.2f}")

AX=135.714547
print("\nmirror check (x pair should sum to 271.429, y equal, rot negated):")
bad=0
for k in sorted(out):
    if not k.startswith('D_L'): continue
    tw = {'D_LSP1':'D_RBK1','D_LBK1':'D_RSP1'}.get(k, 'D_R'+k[3:])
    a,b = out[k], out[tw]
    ok = abs(a[0]+b[0]-2*AX)<0.01 and abs(a[1]-b[1])<0.01 and abs(a[2]+b[2])<0.01
    bad += not ok
    print(f"  {k:8s}/{tw:8s} sum {a[0]+b[0]:9.3f}  dy {a[1]-b[1]:+.3f}  rot {a[2]:+6.2f}/{b[2]:+6.2f}  {'ok' if ok else 'CHECK'}")
print("all mirrored" if not bad else f"{bad} pair(s) off")

# diode-to-diode clearance (SOD-123 body ~ 3.7 x 1.9 mm; land pattern ~ 4.4 x 2.6)
BODY=(4.4,2.6)
def corners(cx,cy,th):
    w,h=BODY; a=math.radians(th); c,s=math.cos(a),math.sin(a)
    return [(cx+dx*c+dy*s, cy-dx*s+dy*c) for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
def gap(A,B):
    best=-1e9
    for poly in (A,B):
        for i in range(4):
            x1,y1=poly[i]; x2,y2=poly[(i+1)%4]
            nx,ny=-(y2-y1),(x2-x1); L=math.hypot(nx,ny); nx,ny=nx/L,ny/L
            pa=[q[0]*nx+q[1]*ny for q in A]; pb=[q[0]*nx+q[1]*ny for q in B]
            best=max(best,max(min(pb)-max(pa),min(pa)-max(pb)))
    return best
cs={k:corners(*v) for k,v in out.items()}
ks=sorted(cs); worst=[]
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        worst.append((gap(cs[ks[i]],cs[ks[j]]), ks[i], ks[j]))
worst.sort()
print(f"\nclosest diode pairs (land pattern {BODY[0]} x {BODY[1]} mm):")
for g,a,b in worst[:4]:
    print(f"   {g:+6.2f} mm  {a} / {b}")
json.dump(out, open('diode-placement.json','w'), indent=1)
