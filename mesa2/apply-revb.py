#!/usr/bin/env python3
"""Apply revb-placement.json to mesa2.kicad_pcb.

Uses KiCAD's own pcbnew module, so the board is loaded and written through
KiCAD's object model and serializer rather than by touching the file as text.
Konnect's IPC path is the normal route for this, but it segfaults KiCAD 10.0.5
on this machine, on writes and on read-only queries alike.

KiCAD must be closed while this runs -- it writes the board file directly.

Run:  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/\
Versions/3.9/bin/python3 apply-revb.py [--dry-run]
"""
import json, os, sys
import pcbnew

BOARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mesa2', 'mesa2.kicad_pcb')
PLACEMENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'revb-placement.json')
TOL_MM, TOL_DEG = 0.001, 0.01

def norm(a):
    """Angles are equal mod 360; report them in (-180, 180]."""
    return (a + 180) % 360 - 180

def main():
    dry = '--dry-run' in sys.argv
    for lck in ('~mesa2.kicad_pcb.lck', '~mesa2.kicad_pro.lck'):
        p = os.path.join(os.path.dirname(BOARD), lck)
        if os.path.exists(p):
            sys.exit(f"{lck} exists -- close KiCAD before running this")

    want = json.load(open(PLACEMENT))
    board = pcbnew.LoadBoard(BOARD)
    on_board = {fp.GetReference() for fp in board.GetFootprints()}

    missing = [r for r in want if r not in on_board]
    if missing:
        print(f"not on the board, skipped: {sorted(missing)}")

    changed = []
    for ref in sorted(want):
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        x, y, rot = want[ref]
        pos = fp.GetPosition()
        cx, cy = pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)
        crot = fp.GetOrientationDegrees()
        dmove = abs(cx - x) > TOL_MM or abs(cy - y) > TOL_MM
        drot = abs(norm(crot - rot)) > TOL_DEG
        if not (dmove or drot):
            continue
        changed.append((ref, (cx, cy, crot), (x, y, rot)))
        if not dry:
            if dmove:
                fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            if drot:
                fp.SetOrientationDegrees(rot)

    for ref, (cx, cy, crot), (x, y, rot) in changed:
        print(f"{ref:9} {cx:9.3f},{cy:8.3f} @{norm(crot):+7.1f}"
              f"  ->  {x:9.3f},{y:8.3f} @{norm(rot):+7.1f}")
    print(f"\n{len(changed)} footprints {'would change' if dry else 'changed'}, "
          f"{len(want) - len(missing) - len(changed)} already correct")

    if not dry and changed:
        pcbnew.SaveBoard(BOARD, board)
        print(f"saved {BOARD}")

main()
