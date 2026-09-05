#!/usr/bin/env python3
"""mesa2 hand-measurement sheets.

Writes two 1:1 sheets sized to fit both A4 and US Letter:
  measure-blank.svg  - gridded datum sheet for free-hand marking (fingers + thumb arc)
  measure-ghost.svg  - same grid with chouchou's 10 left-hand keys ghosted in,
                       for marking corrections against a layout you have in hand

Frame matches the design frame: +X right, +Y toward you. Origin is the marked
cross at the top-left of the grid. Read marks straight off the grid in mm.
"""
import math, html

CAPW, CAPH = 17.5, 16.5
W, H = 196, 268                       # fits A4 and US Letter
M   = 8.0                             # margin
GW, GH = 176, 186                     # grid area
GX, GY = M, 68                        # grid origin on the page

# chouchou left hand, hand-local (unibody -30 removed), origin = middle lower key.
# Shifted so the field sits nicely on the grid.
CH = {'pinky' :[(58.42,76.68,15),(62.82,93.11,15)],
      'ring'  :[(81.48,62.49, 5),(82.96,79.42, 5)],
      'middle':[(103.45,55.61,0),(103.45,72.61,0)],
      'index' :[(127.93,63.68,-5),(126.45,80.61,-5)],
      'thumb' :[(139.21,115.81,88),(157.19,116.44,88)]}
SHIFT = (-42.0, -8.0)                 # bring the field to grid coords, palm room below

def corners(cx, cy, th, w=CAPW, h=CAPH):
    a = math.radians(th); c, s = math.cos(a), math.sin(a)
    return [(cx+dx*c+dy*s, cy-dx*s+dy*c)
            for dx, dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]

def head(title, note):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{M}" y="12" font-family="sans-serif" font-size="5">{html.escape(title)}</text>',
         f'<rect x="{M}" y="16" width="100" height="7" fill="none" stroke="#c00" stroke-width="0.25"/>',
         f'<text x="{M+102}" y="21" font-family="sans-serif" font-size="3" fill="#c00">'
         f'100.0 mm - print at 100%, no scaling</text>']
    y = 30
    for line in note:
        s.append(f'<text x="{M}" y="{y}" font-family="sans-serif" font-size="3.1" fill="#333">{html.escape(line)}</text>')
        y += 4.2
    return s

def grid(s):
    for i in range(0, GW+1, 5):
        w = 0.35 if i % 20 == 0 else (0.2 if i % 10 == 0 else 0.08)
        col = "#999" if i % 20 == 0 else "#bbb"
        s.append(f'<line x1="{GX+i}" y1="{GY}" x2="{GX+i}" y2="{GY+GH}" stroke="{col}" stroke-width="{w}"/>')
        if i % 20 == 0:
            s.append(f'<text x="{GX+i+0.7}" y="{GY-1.5}" font-family="sans-serif" font-size="2.6" fill="#777">{i}</text>')
    for j in range(0, GH+1, 5):
        w = 0.35 if j % 20 == 0 else (0.2 if j % 10 == 0 else 0.08)
        col = "#999" if j % 20 == 0 else "#bbb"
        s.append(f'<line x1="{GX}" y1="{GY+j}" x2="{GX+GW}" y2="{GY+j}" stroke="{col}" stroke-width="{w}"/>')
        if j % 20 == 0:
            s.append(f'<text x="{GX-6}" y="{GY+j+1}" font-family="sans-serif" font-size="2.6" fill="#777">{j}</text>')
    # origin cross + axis sense
    s.append(f'<line x1="{GX-4}" y1="{GY}" x2="{GX+4}" y2="{GY}" stroke="#c00" stroke-width="0.4"/>')
    s.append(f'<line x1="{GX}" y1="{GY-4}" x2="{GX}" y2="{GY+4}" stroke="#c00" stroke-width="0.4"/>')
    s.append(f'<text x="{GX+2}" y="{GY+GH+5}" font-family="sans-serif" font-size="3" fill="#c00">'
             f'origin (0,0) at the red cross - X to the right, Y toward you</text>')
    s.append(f'<line x1="{GX}" y1="{GY+GH}" x2="{GX+GW}" y2="{GY+GH}" stroke="#c00" stroke-width="0.6"/>')
    s.append(f'<text x="{GX+GW-72}" y="{GY+GH-2}" font-family="sans-serif" font-size="3" fill="#c00">'
             f'DATUM - line this up with the desk edge</text>')

BLANK_NOTE = [
 "1. Tape this down. Sit as you type. The datum line at the bottom goes parallel to the desk edge.",
 "2. Ink the pad of each fingertip (washable marker). Do NOT hold a pen - it changes the whole posture.",
 "3. Rest the hand naturally, then TAP each finger straight down. That is the home row. Label the dots.",
 "4. Curl each finger one row further and tap again. Two dots per finger = the column's direction.",
 "   The line through a finger's two dots IS its splay angle. That is the measurement worth having.",
 "5. Thumb: sweep it through its comfortable arc and tap 4-5 times along the way. Do not aim for a line -",
 "   the thumb pivots at the base, so those dots fall on an arc, and the arc gives both angle and distance.",
 "6. Mark where the heel of your palm rests. Repeat the whole thing twice more on fresh sheets.",
]
GHOST_NOTE = [
 "Chouchou's 10 left-hand keys, drawn 1:1 with its unibody angle removed (hand-local frame).",
 "This is the layout you already printed - use it to mark CORRECTIONS rather than absolute positions.",
 "1. Tape down. Ink the fingertips. Rest the hand over the ghosted keys as if typing, and tap.",
 "2. Where each dot falls relative to its cap centre is the correction, read straight off the grid.",
 "3. For the thumbs, tap the comfortable arc rather than aiming at the two drawn keys.",
 "Cap centres in this sheet's grid coordinates are listed in CHOUCHOU.md. Leave the palm area below clear.",
]

# ---- blank sheet ----
s = head("mesa2 - hand measurement sheet (LEFT hand; mirror for right)", BLANK_NOTE)
grid(s); s.append('</svg>')
open('measure-blank.svg','w').write("\n".join(s))

# ---- ghost sheet ----
s = head("mesa2 - chouchou reference, hand-local (LEFT hand)", GHOST_NOTE)
grid(s)
print("chouchou left hand in sheet grid coordinates (mm from the red cross):")
for name, keys in CH.items():
    for i, (x, y, r) in enumerate(keys):
        gx, gy = x+SHIFT[0], y+SHIFT[1]
        w, h = CAPW, CAPH        # 1u throughout
        pts = " ".join(f"{px+GX:.2f},{py+GY:.2f}" for px, py in corners(gx, gy, r, w, h))
        s.append(f'<polygon points="{pts}" fill="none" stroke="#39c" stroke-width="0.35" stroke-dasharray="1.6 1.2"/>')
        s.append(f'<circle cx="{gx+GX:.2f}" cy="{gy+GY:.2f}" r="0.6" fill="#39c"/>')
        tag = f"{name}{'' if len(keys)==1 else ('-up' if i==0 else '-lo')}" if name!='thumb' else f"thumb{i+1}"
        s.append(f'<text x="{gx+GX-7:.2f}" y="{gy+GY-9:.2f}" font-family="sans-serif" font-size="2.4" fill="#39c">{tag}</text>')
        print(f"  {tag:11s} ({gx:6.2f}, {gy:6.2f})  rot {r:+5.1f}")
s.append('</svg>')
open('measure-ghost.svg','w').write("\n".join(s))
print("\nwrote measure-blank.svg and measure-ghost.svg (1:1)")
