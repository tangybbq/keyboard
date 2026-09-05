import json, math
poly=json.load(open('outline.json'))
SW=json.load(open('sw.json'))
A1=(135.715, 57.0)
CAP=(17.5,16.5)
def corners(cx,cy,th):
    w,h=CAP; a=math.radians(th); c,s=math.cos(a),math.sin(a)
    return [(cx+dx*c+dy*s, cy-dx*s+dy*c) for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
M=6; W=max(xs)-min(xs)+2*M; H=max(ys)-min(ys)+2*M
ox,oy=M-min(xs), M-min(ys)
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
   '<rect width="100%" height="100%" fill="white"/>',
   '<polygon points="'+" ".join(f"{x+ox:.2f},{y+oy:.2f}" for x,y in poly)+
   '" fill="#f4f7fa" stroke="#c00" stroke-width="0.5"/>']
for ref,(x,y,r) in SW.items():
    pts=" ".join(f"{px+ox:.2f},{py+oy:.2f}" for px,py in corners(x,y,r))
    col="#39c" if ref[4:-1] in ('SP','BK') else "#333"
    s.append(f'<polygon points="{pts}" fill="none" stroke="{col}" stroke-width="0.35"/>')
    s.append(f'<text x="{x+ox:.2f}" y="{y+oy+1.1:.2f}" font-size="3" text-anchor="middle" '
             f'font-family="sans-serif" fill="{col}">{ref[3:-1]}</text>')
# MCU body (dashed) and its Edge.Cuts cutout (red), which the board edge closes
mb=[(A1[0]-9,A1[1]),(A1[0]+9,A1[1]),(A1[0]+9,A1[1]+20.32),(A1[0]-9,A1[1]+20.32)]
s.append('<polygon points="'+" ".join(f"{x+ox:.2f},{y+oy:.2f}" for x,y in mb)+
         '" fill="none" stroke="#7a3" stroke-width="0.4" stroke-dasharray="2 1.5"/>')
cut=[(A1[0]-6.3,A1[1]+0.7),(A1[0]-6.3,A1[1]+16.62),(A1[0]-5.3,A1[1]+17.62),
     (A1[0]+5.3,A1[1]+17.62),(A1[0]+6.3,A1[1]+16.62),(A1[0]+6.3,A1[1]+0.7)]
s.append('<polyline points="'+" ".join(f"{x+ox:.2f},{y+oy:.2f}" for x,y in cut)+
         '" fill="white" stroke="#c00" stroke-width="0.5"/>')
s.append(f'<text x="{A1[0]+ox:.2f}" y="{A1[1]+oy+24:.2f}" font-size="3.2" text-anchor="middle" '
         f'font-family="sans-serif" fill="#7a3">A1</text>')
s.append(f'<text x="{M}" y="{H-2}" font-size="3.2" font-family="sans-serif" fill="#666">'
         f'mesa2 outline - {len(poly)} vertices, {max(xs)-min(xs):.0f} x {max(ys)-min(ys):.0f} mm</text>')
s.append('</svg>')
open('outline-preview.svg','w').write("\n".join(s))
print(f"{W:.0f} x {H:.0f} mm preview")
