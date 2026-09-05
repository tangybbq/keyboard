#!/usr/bin/env python3
"""Rotate each hand 5 degrees outward about its inner thumb key.

Left  hand: +5 (CCW on screen) about SW_LBK1's centre
Right hand: -5 (CW)            about SW_RSP1's centre

LBK1 and RSP1 are mirror twins, and the rotations are equal and opposite, so the
layout stays mirror-symmetric. Diodes rotate with their switches, which preserves
the local offset they were placed at.
"""
import json, math

DEG = 5.0
LIVE = {
 'SW_LR1':(36.424547,45.0,57.9), 'SW_LA1':(50.814547,54.04,57.9),
 'SW_LS1':(72.734547,35.8,-2.5), 'SW_LO1':(72.004547,52.78,-2.5),
 'SW_LN1':(94.924547,36.29,-12.2),'SW_LT1':(91.334547,52.91,-12.2),
 'SW_LI1':(112.984547,60.88,-37.0),'SW_LE1':(102.754547,74.46,-37.0),
 'SW_LSP1':(106.384547,108.36,43.4),'SW_LBK1':(118.744547,121.45,43.4),
 'SW_RR1':(235.0,45.0,-57.9), 'SW_RA1':(220.61,54.04,-57.9),
 'SW_RS1':(198.69,35.8,2.5), 'SW_RO1':(199.42,52.78,2.5),
 'SW_RN1':(176.5,36.29,12.2), 'SW_RT1':(180.09,52.91,12.2),
 'SW_RI1':(158.44,60.88,37.0), 'SW_RE1':(168.67,74.46,37.0),
 'SW_RBK1':(165.04,108.36,-43.4),'SW_RSP1':(152.68,121.45,-43.4),
 'D_LR1':(32.293999,42.409,57.9),'D_LA1':(46.684,51.449,57.9),
 'D_LS1':(72.947,30.929,-2.5),'D_LO1':(72.217,47.909,-2.5),
 'D_LN1':(95.955,31.524,-12.2),'D_LT1':(92.365,48.144,-12.2),
 'D_LI1':(115.919,56.986,-37.0),'D_LE1':(105.689,70.566,-37.0),
 'D_LSP1':(103.035,104.817,43.4),'D_LBK1':(115.395,117.907,43.4),
 'D_RR1':(239.13,42.409,-57.9),'D_RA1':(224.74,51.449,-57.9),
 'D_RS1':(198.477,30.929,2.5),'D_RO1':(199.207,47.909,2.5),
 'D_RN1':(175.47,31.524,12.2),'D_RT1':(179.06,48.144,12.2),
 'D_RI1':(155.506,56.986,37.0),'D_RE1':(165.736,70.566,37.0),
 'D_RBK1':(168.39,104.817,-43.4),'D_RSP1':(156.03,117.907,-43.4),
}
PIV = {'L': LIVE['SW_LBK1'][:2], 'R': LIVE['SW_RSP1'][:2]}

def rot(p, deg, o):
    a=math.radians(deg); c,s=math.cos(a),math.sin(a)
    x,y=p[0]-o[0], p[1]-o[1]
    return (o[0]+x*c+y*s, o[1]-x*s+y*c)      # KiCad: +deg = CCW on screen

out={}
for ref,(x,y,r) in LIVE.items():
    hand = ref.split('_')[1][0]
    d = DEG if hand=='L' else -DEG
    nx,ny = rot((x,y), d, PIV[hand])
    out[ref] = (round(nx,3), round(ny,3), round(r+d,2))

print(f"{'ref':9s} {'x':>9s} {'y':>8s} {'rot':>7s}   {'dx':>6s} {'dy':>6s}")
for ref in sorted(out):
    x,y,r = out[ref]; ox,oy,_ = LIVE[ref]
    print(f"{ref:9s} {x:9.3f} {y:8.3f} {r:+7.2f}   {x-ox:+6.2f} {y-oy:+6.2f}")

AX = (out['SW_LR1'][0] + out['SW_RR1'][0]) / 2
print(f"\nmirror axis after rotation: {AX:.4f}  (was 135.7123)")
bad=[]
for ref in out:
    if not ref.split('_')[1].startswith('L'): continue
    k = ref.split('_')[1][1:]
    tw = {'SP1':'BK1','BK1':'SP1'}.get(k, k)
    twin = ref.split('_')[0] + '_R' + tw
    if twin not in out: continue
    a,b = out[ref], out[twin]
    if abs(a[0]+b[0]-2*AX) > 0.01 or abs(a[1]-b[1]) > 0.01 or abs(a[2]+b[2]) > 0.01:
        bad.append((ref,twin,a,b))
print(f"mirror pairs consistent: {not bad}" + (f"  {bad}" if bad else ""))
json.dump(out, open('rotated.json','w'), indent=1)
