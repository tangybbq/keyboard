#!/usr/bin/env python3
"""Structural comparison: board copy of each footprint vs its library file.

Parses both into a canonical SET of elements (pads, graphics) so element order
and instance-only data (nets, uuids, sheet path, position, reference text) cannot
produce false differences. What is left is what KiCad's 'does not match copy in
library' test is actually reacting to.
"""
import re, os

BOARD='mesa2.kicad_pcb'
LIBS={'mesa1':'/Users/davidb/Documents/Keyboards/mesa1/mesa1.pretty',
 'Connector':'/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector.pretty',
 'Diode_SMD':'/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Diode_SMD.pretty',
 'TestPoint':'/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/TestPoint.pretty',
 'MountingHole':'/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/MountingHole.pretty'}

def sexp(text, start):
    d=0
    for k in range(start,len(text)):
        if text[k]=='(': d+=1
        elif text[k]==')':
            d-=1
            if d==0: return text[start:k+1]
    return None

def children(block):
    """top-level child s-expressions of a block"""
    out=[]; i=block.find('(',1)
    body=block[block.find('(',1):-1] if False else block
    k=1; d=0; start=None
    for k in range(1,len(block)-1):
        if block[k]=='(':
            if d==0: start=k
            d+=1
        elif block[k]==')':
            d-=1
            if d==0 and start is not None: out.append(block[start:k+1]); start=None
    return out

DROP = ('uuid','tstamp','path','net','property','fp_text','attr','descr','tags',
        'sheetname','sheetfile','model','embedded_fonts','version','generator',
        'generator_version','pinfunction','pintype','zone_connect','thermal',
        'solder_mask_margin','clearance','at')
def canon(block):
    els=set()
    for c in children(block):
        tag = re.match(r'\((\w+)', c)
        if not tag: continue
        t = tag.group(1)
        if t in DROP: continue
        s = c
        for d in ('uuid','tstamp','net','pinfunction','pintype'):
            s = re.sub(r'\('+d+r'[^()]*\)', '', s)
        s = re.sub(r'\s+',' ', s).strip()
        els.add(s)
    return els

src=open(BOARD).read()
seen={}
i=0
while True:
    j=src.find('(footprint "', i)
    if j<0: break
    b=sexp(src,j); i=j+len(b)
    lid=re.match(r'\(footprint "([^"]+)"', b).group(1)
    seen.setdefault(lid,b)

print(f"{'footprint':56s} {'result'}")
for lid,b in sorted(seen.items()):
    nick,name = lid.split(':',1)
    p=os.path.join(LIBS.get(nick,''), name+'.kicad_mod')
    if not os.path.exists(p): print(f"{lid:56s} library file not found"); continue
    lib=canon(open(p).read()); brd=canon(b)
    only_lib = lib-brd; only_brd = brd-lib
    if not only_lib and not only_brd:
        print(f"{lid:56s} identical")
    else:
        print(f"{lid:56s} {len(only_lib)} only-in-library, {len(only_brd)} only-on-board")
        for e in sorted(only_lib)[:3]:  print(f"    library only: {e[:110]}")
        for e in sorted(only_brd)[:3]:  print(f"    board   only: {e[:110]}")
