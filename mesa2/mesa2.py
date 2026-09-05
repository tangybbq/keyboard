#!/usr/bin/env python3
"""mesa2 geometry generator.

Hand-local parameters -> collision check -> unibody assembly -> 1:1 print sheets.

Hand-local frame: +X right (toward the middle of the keyboard for the LEFT hand),
+Y toward you. Origin is the middle column's lower key. Splay is in degrees,
positive = the column's top swings outward (toward the little finger).

Everything is anchored on the LOWER row, matching chouchou/ergogen, which lists
`bottom` before `top` and therefore pivots splay on the bottom key.

Run:  python3 mesa2.py
"""
import math, itertools, html

CAP  = (17.5, 16.5)          # 1u choc keycap
ROW  = 17.0                  # row pitch
CLR  = 0.5                   # wanted air gap between caps
FING = ['pinky', 'ring', 'middle', 'index']

# ---------------------------------------------------------------- geometry --
def corners(cx, cy, th, cap=CAP):
    w, h = cap
    a = math.radians(th); c, s = math.cos(a), math.sin(a)
    return [(cx+dx*c+dy*s, cy-dx*s+dy*c)
            for dx, dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]

def sat_gap(A, B):
    best = -1e9
    for poly in (A, B):
        for i in range(4):
            x1,y1 = poly[i]; x2,y2 = poly[(i+1)%4]
            nx,ny = -(y2-y1), (x2-x1); L = math.hypot(nx,ny); nx,ny = nx/L, ny/L
            pa = [p[0]*nx+p[1]*ny for p in A]; pb = [p[0]*nx+p[1]*ny for p in B]
            best = max(best, max(min(pb)-max(pa), min(pa)-max(pb)))
    return best

def rot(p, deg, o=(0.0,0.0)):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    x, y = p[0]-o[0], p[1]-o[1]
    return (o[0]+x*c+y*s, o[1]-x*s+y*c)

def hand(P):
    """P: dict with spread{}, stagger{}, splay{}, rock, thumb{}.

    Columns are anchored and splayed about their CENTRE - the point the finger
    rests on in steno, between the two keys - not about either key. `rock` is the
    distance between the two key centres, i.e. how far the finger travels from
    one to the other. Returns [(name,x,y,rot,cap)].
    """
    # column-centre anchors, walking outward from the middle column at x=0
    x = {'middle': 0.0}
    x['ring']  = x['middle'] - P['spread']['ring_middle']
    x['pinky'] = x['ring']   - P['spread']['pinky_ring']
    x['index'] = x['middle'] + P['spread']['middle_index']
    keys = []
    rock = P.get('rock', ROW)
    for f in FING:
        th  = P['splay'][f]
        piv = (x[f], P['stagger'][f])                       # pivot = column centre = rest position
        up  = rot((x[f], P['stagger'][f]-rock/2), th, piv)
        lo  = rot((x[f], P['stagger'][f]+rock/2), th, piv)
        keys.append((f+'-lo', lo[0], lo[1], th, CAP))
        keys.append((f+'-up', up[0], up[1], th, CAP))
    # thumbs: pair on a line through `anchor`, tilted `angle`, `pitch` apart
    t = P['thumb']; ax, ay = t['anchor']; a = math.radians(t['angle'])
    for i, k in enumerate((-0.5, 0.5)):
        keys.append((f'thumb{i+1}', ax + k*t['pitch']*math.cos(a),
                     ay - k*t['pitch']*math.sin(a), t['angle']+90.0, CAP))
    return keys

def check(keys):
    caps = [(n, corners(x, y, r, c)) for n, x, y, r, c in keys]
    worst = min((sat_gap(A, B), na, nb) for (na,A),(nb,B) in itertools.combinations(caps, 2))
    xs = [p[0] for _,c in caps for p in c]; ys = [p[1] for _,c in caps for p in c]
    return worst, (max(xs)-min(xs), max(ys)-min(ys))

# ------------------------------------------------------------------ params --
CHOUCHOU = dict(
    spread  = dict(pinky_ring=21.60, ring_middle=21.23, middle_index=23.74),
    stagger = dict(pinky=20.79, ring=6.84, middle=0.0, index=8.03),
    splay   = dict(pinky=15.0, ring=5.0, middle=0.0, index=-5.0),
    rock    = 17.0,
    thumb   = dict(anchor=(44.65, 51.70), angle=2.0, pitch=18.0))

# Your three corrections, bracketed. Spread down; pinky and index staggered
# further toward the palm; pinky rotated harder. Thumbs 1u and pushed out.
V1 = dict(
    spread  = dict(pinky_ring=19.00, ring_middle=19.50, middle_index=21.00),
    stagger = dict(pinky=24.00, ring=6.84, middle=0.0, index=12.00),
    splay   = dict(pinky=21.0, ring=5.0, middle=0.0, index=-5.0),
    rock    = 17.0,
    thumb   = dict(anchor=(42.00, 56.00), angle=2.0, pitch=18.0))
V2 = dict(
    spread  = dict(pinky_ring=18.00, ring_middle=19.20, middle_index=19.50),
    stagger = dict(pinky=27.00, ring=7.00, middle=0.0, index=15.00),
    splay   = dict(pinky=26.0, ring=6.0, middle=0.0, index=-6.0),
    rock    = 17.0,
    thumb   = dict(anchor=(40.00, 60.00), angle=2.0, pitch=18.0))

VARIANTS = [('chouchou (as printed, 1u caps)', CHOUCHOU), ('V1 modest', V1), ('V2 stronger', V2)]

# ------------------------------------------------------------------ report --
for name, P in VARIANTS:
    keys = hand(P); (g, na, nb), (w, h) = check(keys)
    print(f"\n### {name}")
    print(f"    spread  {P['spread']['pinky_ring']:.2f} / {P['spread']['ring_middle']:.2f} / "
          f"{P['spread']['middle_index']:.2f}     "
          f"stagger {P['stagger']['pinky']:.2f} / {P['stagger']['ring']:.2f} / 0 / {P['stagger']['index']:.2f}")
    print(f"    splay   {P['splay']['pinky']:+.0f} / {P['splay']['ring']:+.0f} / 0 / {P['splay']['index']:+.0f}"
          f"   rock {P.get('rock', ROW):.1f}"
          f"        min cap gap {g:+.2f} mm ({na}/{nb})   hand envelope {w:.1f} x {h:.1f} mm")
    for n, x, y, r, _ in keys:
        print(f"      {n:9s} ({x:7.2f}, {y:7.2f})  rot {r:+6.1f}")

# --------------------------------------------------------------- unibody ----
print("\n\n### unibody assembly (chouchou-style: each half rotated, then mirrored)")
print("  angle | inner-column gap | board W x H (+11 mm margin) | pinky forward of index")
for P, tag in [(V1, 'V1'), (V2, 'V2')]:
    print(f"  -- {tag} --")
    for th in (20, 25, 30):
        L = [(n, *rot((x, y), -th), r-th, c) for n, x, y, r, c in hand(P)]
        pts = [p for n,x,y,r,c in L for p in corners(x, y, r, c)]
        x1 = max(p[0] for p in pts)
        for gap in (8.0,):
            axis = x1 + gap/2
            R = [(n, 2*axis-x, y, -r, c) for n,x,y,r,c in L]
            allp = pts + [p for n,x,y,r,c in R for p in corners(x, y, r, c)]
            W = max(p[0] for p in allp)-min(p[0] for p in allp)+22
            H = max(p[1] for p in allp)-min(p[1] for p in allp)+22
            pk = [k for k in L if k[0]=='pinky-up'][0]; ix = [k for k in L if k[0]=='index-up'][0]
            print(f"   {th:3d}  |     {gap:4.1f} mm      |   {W:6.1f} x {H:5.1f}          | {ix[2]-pk[2]:5.1f} mm")

# ------------------------------------------------------------ print sheets --
W, H, M = 196, 268, 10   # fits A4 and US Letter

def sheet(path, title, notes, blocks, fan=None):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{M}" y="12" font-family="sans-serif" font-size="5">{html.escape(title)}</text>',
         f'<rect x="{M}" y="16" width="100" height="7" fill="none" stroke="#c00" stroke-width="0.25"/>',
         f'<text x="{M+102}" y="21" font-family="sans-serif" font-size="3" fill="#c00">'
         '100.0 mm - print at 100%, no fit-to-page</text>']
    y = 30
    for n in notes:
        s.append(f'<text x="{M}" y="{y}" font-family="sans-serif" font-size="3.1" fill="#333">{html.escape(n)}</text>')
        y += 4.2
    yoff = y + 12
    for label, keys in blocks:
        pts = [p for n,kx,ky,r,c in keys for p in corners(kx, ky, r, c)]
        ox = M - min(p[0] for p in pts); oy = yoff - min(p[1] for p in pts)
        s.append(f'<text x="{M}" y="{yoff-4:.2f}" font-family="sans-serif" font-size="3.8">{html.escape(label)}</text>')
        for n, kx, ky, r, c in keys:
            poly = " ".join(f"{p[0]+ox:.2f},{p[1]+oy:.2f}" for p in corners(kx, ky, r, c))
            s.append(f'<polygon points="{poly}" fill="none" stroke="#222" stroke-width="0.35"/>')
            s.append(f'<circle cx="{kx+ox:.2f}" cy="{ky+oy:.2f}" r="0.5" fill="#888"/>')
        yoff += (max(p[1] for p in pts) - min(p[1] for p in pts)) + 16
    if fan:
        anchor, pitch, angles = fan
        s.append(f'<text x="{M}" y="{yoff-4:.2f}" font-family="sans-serif" font-size="3.8">'
                 'thumb-pair angle fan - rest the thumb across a pair and pick the one that lies square</text>')
        cx, cy = M + 60, yoff + 22
        for a in angles:
            for k in (-0.5, 0.5):
                kx = cx + k*pitch*math.cos(math.radians(a)); ky = cy + k*pitch*math.sin(math.radians(a))
                poly = " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in corners(kx, ky, a+90.0))
                s.append(f'<polygon points="{poly}" fill="none" stroke="#39c" stroke-width="0.3"/>')
            lx = cx + 0.5*pitch*math.cos(math.radians(a)) + 12*math.cos(math.radians(a))
            ly = cy + 0.5*pitch*math.sin(math.radians(a)) + 12*math.sin(math.radians(a))
            s.append(f'<text x="{lx:.2f}" y="{ly:.2f}" font-family="sans-serif" font-size="2.8" fill="#39c">{a:+d} deg</text>')
        s.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="0.8" fill="#c00"/>')
    s.append('</svg>')
    open(path, 'w').write("\n".join(s))

sheet('variants-1to1.svg',
      'mesa2 - finger variants, LEFT hand, hand-local (unibody angle removed)',
      ["Columns are anchored and splayed about their CENTRE - the point the finger rests on between",
       "the two keys - not about either key. Rest a finger on the ridge between a column's two caps.",
       "Both are chouchou with your corrections applied, bracketing the amount: spread down, pinky and",
       "index staggered toward the palm, pinky rotated harder. 1u caps. Thumb pairs are placeholders -",
       "use thumb-1to1 for those. You already have chouchou printed; compare against that."],
      [('V1 modest   spread 19.0/19.5/21.0   stagger 24.0/6.8/0/12.0   splay +21/+5/0/-5   rock 17', hand(V1)),
       ('V2 stronger spread 18.0/19.2/19.5   stagger 27.0/7.0/0/15.0   splay +26/+6/0/-6   rock 17', hand(V2))])

# thumb sheet: three angles side by side, each with its own index-column
# reference so the reach from the fingers is identical across them.
def thumb_sheet(path):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{M}" y="12" font-family="sans-serif" font-size="5">'
         'mesa2 - thumb angle and reach, LEFT hand, hand-local</text>',
         f'<rect x="{M}" y="16" width="100" height="7" fill="none" stroke="#c00" stroke-width="0.25"/>',
         f'<text x="{M+102}" y="21" font-family="sans-serif" font-size="3" fill="#c00">'
         '100.0 mm - print at 100%, no fit-to-page</text>']
    notes = ["Within a row only the ANGLE of the line through the two thumb keys changes.",
             "Between rows only the REACH changes. The index column is redrawn in each cell so the",
             "distance from finger to thumb is identical across a row - register your index on it every time.",
             "Lay the thumb across a pair: the right one is reached without moving the wrist and lands",
             "square on both keys. If none fits, use measure-blank.svg - sweep and tap 4-5 dots on the arc."]
    y = 30
    for n in notes:
        s.append(f'<text x="{M}" y="{y}" font-family="sans-serif" font-size="3.1" fill="#333">{html.escape(n)}</text>')
        y += 4.2
    idx = [k for k in hand(V1) if k[0].startswith('index')]
    ax0, ay0 = V1['thumb']['anchor']
    top = y + 12
    for row, extra in enumerate((0.0, 8.0)):
        yb = top + row*98
        s.append(f'<text x="{M}" y="{yb-5:.2f}" font-family="sans-serif" font-size="3.8">'
                 f'{"reach as V1" if extra==0 else "reach 8 mm further from the fingers"}</text>')
        for cell, a in enumerate((-15, 0, 15)):
            keys = list(idx)
            for i, k in enumerate((-0.5, 0.5)):
                keys.append((f't{i}', ax0 + k*18*math.cos(math.radians(a)),
                             ay0 + extra - k*18*math.sin(math.radians(a)), a+90.0, CAP))
            pts = [p for n,kx,ky,r,c in keys for p in corners(kx, ky, r, c)]
            ox = M + cell*59 - min(p[0] for p in pts)
            oy = yb + 6 - min(p[1] for p in pts)
            s.append(f'<text x="{M+cell*59:.2f}" y="{yb+2:.2f}" font-family="sans-serif" '
                     f'font-size="3.2" fill="#39c">{a:+d} deg</text>')
            for n, kx, ky, r, c in keys:
                col = "#222" if n.startswith('index') else "#39c"
                poly = " ".join(f"{p[0]+ox:.2f},{p[1]+oy:.2f}" for p in corners(kx, ky, r, c))
                s.append(f'<polygon points="{poly}" fill="none" stroke="{col}" stroke-width="0.35"/>')
                s.append(f'<circle cx="{kx+ox:.2f}" cy="{ky+oy:.2f}" r="0.5" fill="#999"/>')
    s.append('</svg>')
    open(path, 'w').write("\n".join(s))

thumb_sheet('thumb-1to1.svg')
print("\nwrote variants-1to1.svg and thumb-1to1.svg")
