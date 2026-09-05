#!/usr/bin/env python3
"""Minimum column spread vs splay, for the real chouchou-derived staggers.

Two 1u choc caps in adjacent columns, each column being two keys at 17 mm pitch.
Checks all four cap pairs across the junction, not just the same-row pair.
"""
import math, itertools

CAPW, CAPH, ROW, CLR = 17.5, 16.5, 17.0, 0.5

def corners(cx, cy, th, w=CAPW, h=CAPH):
    a=math.radians(th); c,s=math.cos(a),math.sin(a)
    return [(cx+dx*c+dy*s, cy-dx*s+dy*c)
            for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]

def sat_gap(A,B):
    best=-1e9
    for poly in (A,B):
        for i in range(4):
            x1,y1=poly[i]; x2,y2=poly[(i+1)%4]
            nx,ny=-(y2-y1),(x2-x1); L=math.hypot(nx,ny); nx,ny=nx/L,ny/L
            pa=[p[0]*nx+p[1]*ny for p in A]; pb=[p[0]*nx+p[1]*ny for p in B]
            best=max(best,max(min(pb)-max(pa),min(pa)-max(pb)))
    return best

def col(x, y_lower, th, pivot_below=0.0):
    """two keys, splay th about a point pivot_below mm under the lower key"""
    a=math.radians(th); c,s=math.cos(a),math.sin(a)
    piv=(x, y_lower+pivot_below); out=[]
    for p in [(x,y_lower-ROW),(x,y_lower)]:
        dx,dy=p[0]-piv[0],p[1]-piv[1]
        out.append((piv[0]+dx*c+dy*s, piv[1]-dx*s+dy*c, th))
    return out

def min_spread(th_a, th_b, stagger, pivot_below=0.0):
    """stagger = how much col B's lower key sits AWAY from you vs col A's (mm)"""
    lo,hi=10.0,45.0
    for _ in range(70):
        mid=(lo+hi)/2
        A=col(0,0,th_a,pivot_below); B=col(mid,-stagger,th_b,pivot_below)
        g=min(sat_gap(corners(*a),corners(*b)) for a in A for b in B)
        if g>=CLR: hi=mid
        else: lo=mid
    return hi

print("Pivot = LOWER key (chouchou / ergogen default)\n")
print("PINKY -> RING   (ring sits 13.68 mm further from you; ring splay +5)")
print("  pinky splay | min spread | vs chouchou's 20.15")
for tp in [15,18,20,22,25,28,30]:
    m=min_spread(tp,5,13.68)
    print(f"      +{tp:2d} deg   |   {m:5.2f}    | {m-20.15:+5.2f}")

print("\nRING -> MIDDLE  (middle 6.81 further; splays +5 / 0)")
print(f"  min spread {min_spread(5,0,6.81):5.2f}   vs chouchou's 20.48  ({min_spread(5,0,6.81)-20.48:+.2f})")

print("\nMIDDLE -> INDEX (index 8.00 nearer you; splays 0 / -5)")
print(f"  min spread {min_spread(0,-5,-8.00):5.2f}   vs chouchou's 23.00  ({min_spread(0,-5,-8.00)-23.00:+.2f})")

print("\n\nPivot = COLUMN CENTRE (8.5 mm above the lower key)\n")
print("PINKY -> RING")
print("  pinky splay | min spread | vs chouchou's 20.15")
for tp in [15,18,20,22,25,28,30]:
    m=min_spread(tp,5,13.68,-8.5)
    print(f"      +{tp:2d} deg   |   {m:5.2f}    | {m-20.15:+5.2f}")

print("\nHow much does the pinky->ring stagger buy? (pinky splay +22, pivot lower key)")
for st in [8,11,13.68,16,19,22]:
    print(f"   stagger {st:5.2f} mm -> min spread {min_spread(22,5,st):5.2f}")
