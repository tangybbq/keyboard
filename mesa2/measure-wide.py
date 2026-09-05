#!/usr/bin/env python3
"""mesa2 two-hand measurement sheet - single landscape page.

258 x 196 mm, so it prints unscaled on landscape US Letter (279.4 x 215.9) and
landscape A4 (297 x 210). One sheet, no tiling, no registration error.

Both hands go on this one sheet in one sitting. That is the point: the unibody
angle is the angle BETWEEN the two hands, so with both marked on the same paper
the reference is internal and no desk-edge datum is needed.

Run:  python3 measure-wide.py
"""
import html

W, H, M = 258, 196, 9
GW, GH  = 240, 136
GX, GY  = M, 54

NOTES = [
 "Both hands down as you would type, paper taped and NOT moved for the whole session. No desk-edge datum is needed: the",
 "angle between your two hands IS the unibody angle, so it is internal to this sheet as long as the paper never moves.",
 "Steno rest position: each finger sits BETWEEN its two keys, not on one of them. Mark three dots per finger -",
 "(a) where it rests, (b) rocked forward, (c) rocked back. (a) is the column centre and (b)-(c) give the column ANGLE.",
 "Do not try to set the row pitch from (b) and (c): it is fixed at 17 mm by the caps. Only note if the rock feels SHORT.",
 "Keep the hand PLANTED and lift one finger at a time; the others hold the posture. Mark with a pen in the other hand.",
 "Thumbs: sweep the comfortable arc and mark 4-5 spots along it - an arc, not two aimed dots. Then mark both palm heels.",
 "Do the left hand this way, then re-place BOTH hands naturally and do the right. Re-placing both is what keeps the angle honest.",
]

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
     '<rect width="100%" height="100%" fill="white"/>',
     f'<text x="{M}" y="10" font-family="sans-serif" font-size="4.6">'
     'mesa2 - two-hand measurement sheet</text>',
     f'<rect x="{M}" y="13" width="100" height="6" fill="none" stroke="#c00" stroke-width="0.25"/>',
     f'<text x="{M+102}" y="17.5" font-family="sans-serif" font-size="3" fill="#c00">'
     '100.0 mm - print at 100%, no scaling, LANDSCAPE</text>']
y = 23
for n in NOTES:
    s.append(f'<text x="{M}" y="{y}" font-family="sans-serif" font-size="2.85" fill="#333">{html.escape(n)}</text>')
    y += 3.6

for i in range(0, GW+1, 5):
    w = 0.35 if i % 20 == 0 else (0.2 if i % 10 == 0 else 0.08)
    col = "#999" if i % 20 == 0 else "#bbb"
    s.append(f'<line x1="{GX+i}" y1="{GY}" x2="{GX+i}" y2="{GY+GH}" stroke="{col}" stroke-width="{w}"/>')
    if i % 20 == 0:
        s.append(f'<text x="{GX+i+0.7}" y="{GY-1.4}" font-family="sans-serif" font-size="2.6" fill="#777">{i}</text>')
for j in range(0, GH+1, 5):
    w = 0.35 if j % 20 == 0 else (0.2 if j % 10 == 0 else 0.08)
    col = "#999" if j % 20 == 0 else "#bbb"
    s.append(f'<line x1="{GX}" y1="{GY+j}" x2="{GX+GW}" y2="{GY+j}" stroke="{col}" stroke-width="{w}"/>')
    if j % 20 == 0:
        s.append(f'<text x="{GX-6.5}" y="{GY+j+1}" font-family="sans-serif" font-size="2.6" fill="#777">{j}</text>')

s.append(f'<line x1="{GX-4}" y1="{GY}" x2="{GX+4}" y2="{GY}" stroke="#c00" stroke-width="0.4"/>')
s.append(f'<line x1="{GX}" y1="{GY-4}" x2="{GX}" y2="{GY+4}" stroke="#c00" stroke-width="0.4"/>')
s.append(f'<text x="{GX+1.5}" y="{GY+GH+5}" font-family="sans-serif" font-size="3" fill="#c00">'
         'origin (0,0) at the red cross - X runs right, Y runs toward you. '
         'Label every dot: hand, finger, and which of rest / forward / back.</text>')
s.append('</svg>')
open('measure-wide.svg','w').write("\n".join(s))
print(f"wrote measure-wide.svg  page {W} x {H} mm, grid {GW} x {GH} mm")
