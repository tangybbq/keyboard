#!/usr/bin/env python3
"""Apply fn-placement.json to the mesa3 boards.

Same route as mesa2/apply-revb.py: KiCAD's own pcbnew module, so each board
goes through KiCAD's object model and serializer rather than being edited as
text. Konnect's IPC path would be the normal route and still segfaults KiCAD
10.0.5 on this machine, on reads as well as writes.

fn-placement.json is keyed by board directory, so this handles both halves in
one pass. A board is only saved if something on it actually moved.

KiCAD must be closed while this runs -- it writes the board files directly.

Run:  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/\
Versions/3.9/bin/python3 apply-fnkey.py [--dry-run]
"""
import json, os, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PLACEMENT = os.path.join(HERE, 'fn-placement.json')
TOL_MM, TOL_DEG = 0.001, 0.01


def norm(a):
    """Angles are equal mod 360; report them in (-180, 180]."""
    return (a + 180) % 360 - 180


def apply_board(name, want, dry):
    """-> number of footprints that changed (or would change) on this board."""
    d = os.path.join(HERE, name)
    board_file = os.path.join(d, name + '.kicad_pcb')
    for lck in (f'~{name}.kicad_pcb.lck', f'~{name}.kicad_pro.lck'):
        if os.path.exists(os.path.join(d, lck)):
            sys.exit(f"{lck} exists -- close KiCAD before running this")

    board = pcbnew.LoadBoard(board_file)
    on_board = {fp.GetReference() for fp in board.GetFootprints()}
    missing = [r for r in want if r not in on_board]
    if missing:
        sys.exit(f"not on {name}: {sorted(missing)} -- add the footprints "
                 f"in KiCAD first, this script only positions them")

    changed = []
    for ref in sorted(want):
        fp = board.FindFootprintByReference(ref)
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

    print(f"{name}:")
    for ref, (cx, cy, crot), (x, y, rot) in changed:
        print(f"  {ref:9} {cx:9.3f},{cy:8.3f} @{norm(crot):+7.1f}"
              f"  ->  {x:9.3f},{y:8.3f} @{norm(rot):+7.1f}")
    print(f"  {len(changed)} footprints {'would change' if dry else 'changed'},"
          f" {len(want) - len(changed)} already correct")

    if not dry and changed:
        pcbnew.SaveBoard(board_file, board)
        print(f"  saved {board_file}")
    return len(changed)


def main():
    dry = '--dry-run' in sys.argv
    placement = json.load(open(PLACEMENT))
    total = sum(apply_board(name, placement[name], dry)
                for name in sorted(placement))
    print(f"\n{total} footprints {'would change' if dry else 'changed'} "
          f"across {len(placement)} boards")


main()
