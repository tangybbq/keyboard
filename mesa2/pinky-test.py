#!/usr/bin/env python3
"""1:1 comparison sheet: left-hand fingers with the pinky at four splay angles.

Everything except the pinky is identical between blocks, and each block carries
the small inward spacing correction that angle allows, so what you feel is the
angle and nothing else.

Angles span what the measurement actually permits:
  40  the near half of the arc (m2->m3), i.e. the local direction at rest
  50  close to the right hand's chord (51.1)
  58  the averaged chord - what is on the board now
  66  close to the left hand's chord (65.0), and the extended half (64.2)
"""
import math, json, html

CAP=(17.5,16.5); ROCK=17.0
d=json.load(open('layout.json'))
cols={k:(tuple(v[0]),v[1]) for k,v in d['cols'].items()}
NUD={'pinky':1.7,'ring':0.5,'middle':0.1,'index':0.1}
EXTRA=json.load(open('pinky-nudge.json'))
ANGLES=[40,50,58,66]
ORDER=['pinky','ring','middle','index']

def corners(cx,cy,th):
    w,h=CAP; a=math.radians(th); c,s=math.cos(a),math.sin(a)
    return [(cx+dx*c+dy*s, cy-dx*s+dy*c) for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]

def hand(pang):
    ex=EXTRA[str(pang)]
    out=[]
    for f in ORDER:
        (cx,cy),a = cols[f]
        cx -= NUD[f] + (ex if f=='pinky' else 0)
        if f=='pinky': a=pang
        u=(math.sin(math.radians(a)), math.cos(math.radians(a)))
        out.append((f,'far', cx-u[0]*ROCK/2, cy-u[1]*ROCK/2, a))
        out.append((f,'near',cx+u[0]*ROCK/2, cy+u[1]*ROCK/2, a))
    return out

blocks=[(a,hand(a)) for a in ANGLES]
allp=[p for _,ks in blocks for _,_,x,y,r in ks for p in corners(x,y,r)]
BW=max(p[0] for p in allp)-min(p[0] for p in allp)
BH=max(p[1] for p in allp)-min(p[1] for p in allp)
X0=min(p[0] for p in allp); Y0=min(p[1] for p in allp)

W,H,M = 258,196,8
GAP=6
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
   '<rect width="100%" height="100%" fill="white"/>',
   f'<text x="{M}" y="9" font-family="sans-serif" font-size="4.4">'
   'mesa2 - pinky splay comparison, LEFT hand, 1:1 (landscape)</text>',
   f'<rect x="{M}" y="12" width="100" height="6" fill="none" stroke="#c00" stroke-width="0.25"/>',
   f'<text x="{M+102}" y="16.5" font-family="sans-serif" font-size="3" fill="#c00">'
   '100.0 mm - print at 100%, no scaling</text>',
   f'<text x="{M}" y="23" font-family="sans-serif" font-size="3" fill="#333">'
   'Only the pinky differs. Ring, middle and index are identical in all four. '
   'Rest your hand on each and rock each finger between its two keys.</text>']
top=34
for i,(a,ks) in enumerate(blocks):
    col,row = i%2, i//2
    ox = M + col*(BW+GAP) - X0
    oy = top + row*(BH+11) - Y0
    s.append(f'<text x="{ox+X0:.1f}" y="{oy+Y0-2.5:.1f}" font-family="sans-serif" font-size="3.6">'
             f'pinky {a} deg' + ('   (on the board now)' if a==58 else '') + '</text>')
    for f,which,x,y,r in ks:
        pts=" ".join(f"{px+ox:.2f},{py+oy:.2f}" for px,py in corners(x,y,r))
        stroke = "#c00" if f=='pinky' else "#222"
        s.append(f'<polygon points="{pts}" fill="none" stroke="{stroke}" stroke-width="0.4"/>')
        s.append(f'<circle cx="{x+ox:.2f}" cy="{y+oy:.2f}" r="0.5" fill="#999"/>')
s.append('</svg>')
open('pinky-test-1to1.svg','w').write("\n".join(s))
print(f"block {BW:.1f} x {BH:.1f} mm -> sheet {W} x {H} mm, 2x2")
for a in ANGLES:
    print(f"  pinky {a} deg: spacing {EXTRA[str(a)]:+.2f} mm vs the board")
