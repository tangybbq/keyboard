# Toward the Mesa 3

This document describes a series of design steps to work our way through:
- some improvements to the Mesa 2 keyboard
- an alternate design of the Mesa 2 to test a different scanning technique on the matrix
- the design of the Mesa 3, which will take the physical layout learned from the Mesa 2 and apply it to a split design in the style of the Mesa 1.

The main change to the layout is to eliminate the outermost pinky key. I am now
using a custom layout, called Dosh, that only uses 7 finger keys per side.

Dosh uses the same key names as Taipo for the keys it keeps. Only the outer pinky
key (`R`) goes away, so the surviving refs are unchanged: pinky `A`, ring `S`/`O`,
middle `N`/`T`, index `I`/`E`, thumbs `SP`/`BK`. **9 keys per side, 18 total.**
No ref renaming is needed anywhere — `SW_LR1`, `SW_RR1` and their diodes are simply
deleted.

**Everything here ends in one fab order of four PCBs** — mesa2 Rev B, mesa2x Rev A,
mesa3-left, mesa3-right. Fab cost is dominated by shipping, so all four designs must
be finished and reviewed before anything is ordered. The 2x board is an experiment for
possible future use; the Mesa 3 does **not** wait on its results and uses the same
conventional scanned matrix as Rev B.

## Conventions

- `(human)` — a step I do in the KiCad GUI. `(AI)` — a step done by script or analysis.
  Untagged steps are open to either.
- **Geometry is generated, not hand-nudged.** Key positions come from `mesa2/layout.py`
  → `placement.json` → the PCB, and the outline from `outline.py` → `outline.json` →
  `dxf.py`. Change the scripts and re-emit; don't drag footprints in the editor and let
  the model go stale.
- `mesa2/LAYOUT.md` is the geometry record of truth for humans, and must be updated in
  the same commit as any geometry change.
- Rev letters are per board, in the silkscreen, and bumped when a board is sent to fab.
- **Firmware is my own, in Rust + Embassy.** Not QMK, not ZMK, not KMK. Anything a board
  needs from the firmware side is a spec an agent working in that codebase implements
  from — see below.

## Boards in this batch

| board | dir | keys | matrix | controller |
|---|---|---|---|---|
| mesa2 Rev B | `mesa2/mesa2` | 18 | 5 × 4, per-finger columns | Tiny2040, unibody |
| mesa2x Rev A | `mesa2x/mesa2x` | 18 | pairwise (experiment) | Tiny2040, unibody |
| mesa3-left | `mesa3/mesa3-left` | 9 | the same 5 × 4, spanning both halves | Tiny2040 + RJ-45 |
| mesa3-right | `mesa3/mesa3-right` | 9 | " | passive, RJ-45 only |

Rev B and the two Mesa 3 halves are one matrix as far as the firmware is concerned.

## What the firmware sees

The firmware is mine, in Rust + Embassy, so the board designs answer to it rather than the
other way round. The requirement on this batch:

- **mesa2 Rev B and mesa3 present one identical matrix.** Same five columns, same four
  rows, the same key at every (column, row). The firmware must not be able to tell a
  Rev B from a Mesa 3 — one keymap, one build, no board-specific code. Mesa 3 is copied
  from Rev B, so this holds for free as long as neither board's wiring is changed on its
  own afterwards.
- **Rev A's column pairing is mirrored, and Rev B fixes it.** As wired today the two
  hands number their columns in opposite order, so a shared column joins *different*
  fingers:

  | net | left | right | after the Rev B fix |
  |---|---|---|---|
  | `COL_1` | pinky `A` | index `I`/`E` | pinky `A` both sides |
  | `COL_2` | ring `S`/`O` | middle `N`/`T` | ring both sides |
  | `COL_3` | middle `N`/`T` | ring `S`/`O` | middle both sides |
  | `COL_4` | index `I`/`E` | pinky `A` | index both sides |
  | `COL_5` | thumb `SP`/`BK` | thumb `SP`/`BK` | unchanged |

  It works either way — every column carries four keys and the firmware maps
  (column, row) to a key regardless. It is just confusing, and it is cheap to fix while
  Rev B is being rerouted anyway.
- **Rows are already right**: `ROW_A`/`ROW_B` are the left's far and near rows,
  `ROW_C`/`ROW_D` the right's. Unchanged from Rev A, unchanged in Mesa 3.
- **Rev A is the one board it has to tell apart**, because Rev A has the outer pinky `R`
  and Taipo makes sense on it, and Rev B/Mesa 3 have neither. Decide how before fab — a
  compile-time build is free, but if one binary should cover everything, the cheap
  hardware version is a board-ID strap on a spare GPIO. The Tiny2040 breaks out twelve
  (GP0–GP7, A0–A3) and the matrix plus RGB use ten, so two are free. Rev A leaves such a
  pin floating, so *new* boards tie it and the default state reads as "Rev A" — which is
  the only version of this that works, since Rev A is already fabbed and cannot be
  changed.
- **mesa2x is deliberately its own thing** — different scan algorithm, separate build,
  spec'd in `mesa2x/SCANNING.md`.
- The matrix map is written once and shared by Rev B and Mesa 3. Two copies would drift.

## Housekeeping

**Do this first.** Rev A is the board I am typing on right now, and none of it is in git
yet — capture it before anything changes.

- [x] Add necessary .gitignore file(s) and commit the current mesa rev A design.
  `.DS_Store`, `__pycache__/` and `~*.lck` added to the root `.gitignore`;
  `production/` is committed, following mesa1.
- [x] Clean the strays that came along when mesa2 was copied from mesa1:
  `mesa1-left-backups/`, `mesa1-left-unsaved-export-JyNPS8.kicad_prl` and a duplicate of
  mesa1's `production/mesa1-left_A.zip`. All three still exist under `mesa1/`.
- [x] The tracked `.DS_Store` files under `mesa1/` removed from the index, along with a
  tracked `~mesa1-left.kicad_pro.lck`.

## Mesa 2 Rev B

Starting point: mesa2 Rev A — 20 keys, routed (401 segments, 41 vias, one zone),
outline drawn, `production/mesa2_A.zip` already exported.

- [ ] Remove the outermost pinky key
  - [ ] Delete `SW_LR1`, `SW_RR1`, `D_LR1`, `D_RR1` from the schematic
  - [ ] Update the matrix map in `LAYOUT.md` — the pinky column now carries one key
- [ ] Rotate the pinky keys 90° so that their orientation is similar to the other finger keys
- [ ] Move the Sp keys 1mm closer to the Bk key: 18.00 mm → **17.00 mm**. Checked — the
  thumb pair is separated along the cap's 16.5 mm axis, same as the finger rows (the
  caps are rotated across the direction of travel), so Rev A's 18 mm leaves a 1.50 mm
  gap where every finger row has 0.50 mm. 17.00 mm makes the thumbs match everything
  else exactly.
- [ ] Fix the mirrored column pairing — one column per finger, the same finger on both
  sides (see *What the firmware sees*). Clarity fix, not a functional one
- [ ] Decide and implement the Rev A / Rev B distinction — compile-time, or a board-ID
  strap on one of the two spare Tiny2040 GPIOs. It cannot be retrofitted after fab
- [ ] Adjust the diodes of the moved keys
- [ ] Update `layout.py` / `placement.json` for all of the above and re-emit to the PCB (AI)
- [ ] Re-run the cap clearance check (`clearance.py`, `fit.py`) over all remaining pairs.
  Rev A's worst gap was +0.50 mm; the 90° pinky rotation swings a different cap corner
  and the asymmetric `Kailh_socket_PG1350` reaches 9.575 mm one way, so this is not a
  formality (AI)
- [ ] Fix the routing (human)
- [ ] Adjust the board outline (human)
- [ ] Confirm the six M2 mounting holes are still inside the outline and clear of
  sockets and caps
- [ ] Fixup label for Rev B
- [ ] Print the 1:1 placement sheet and check it against my hands before fab (human).
  This is the only physical check — no printed mockup. Rev A is in daily use, so the
  geometry is proven and the Rev B changes are small.
- [ ] Update `LAYOUT.md` to the Rev B geometry
- [ ] Write the shared matrix map — column/row net to key for both Rev B and Mesa 3, plus
  scan order and debounce expectations. This is what the firmware agent implements from
- [ ] ERC clean, DRC clean
- [ ] Design review
- [ ] Git commit Rev B

Rev B keeps `COL_1..5 × ROW_A..D` — 18 keys in 20 slots, the two empty ones being the
deleted pinky `R` keys. Don't re-pack to free a GPIO: the Tiny2040 has pins to spare, and
Mesa 3 needs this exact shape.

## Mesa 2x Rev A

This is an experiment with a new matrix. The idea is to not have a fixed idea of
a grid, but that for GPIOs 1-m, for a given GPIO n, there is a key+diode to each
of n+1..m.

Branches from **Rev B**, so the two boards share one geometry and only the wiring
differs. 18 keys needs the smallest m with m(m−1)/2 ≥ 18, which is **m = 7** (21 pairs,
3 spare) — down from the 9 pins the grid uses.

- [ ] Copy the mesa2 Rev B dir to mesa2x, rename the project files and internal refs,
  and check the `${KIPRJMOD}`-relative lib tables still resolve
- [ ] Assign the 18 keys to GPIO pairs, chosen to keep the routing sane (AI)
- [ ] Fix the diode polarity convention (cathode toward the higher-numbered pin) and
  record it in the design notes and on the silkscreen
- [ ] Rewire keys (human)
- [ ] AI analysis, especially checking for ghosting with arbitrary chords.
  Dosh is a chorded layout, so multi-key presses are the normal case, not the corner
  case — the analysis has to cover arbitrary N-key chords, the scan sequence, and the
  pull direction on the read pins.
- [ ] Write `mesa2x/SCANNING.md` — the spec the Rust + Embassy firmware gets implemented
  from. It has to state the pin roles, which pin drives and which read at each step, the
  full scan order, pull configuration, settling time, the pair → key table, and how a
  chord is decoded. Write it before the board goes to fab: if the algorithm doesn't come
  out clean on paper, the board is wrong, not the firmware.
- [ ] Make the silkscreen clearly distinguish this board from the Rev B one
- [ ] Reroute
- [ ] ERC clean, DRC clean
- [ ] Design review
- [ ] Git commit

## Mesa 3

Split, in the style of the Mesa 1: a single **Tiny2040 on the left half**, RJ-45 on
B.Cu at each end with a straight-through cable, and a **passive right half** — no power,
no LEDs, not even a ground. Mesa 1 set the precedent: its right half carried eight matrix
nets and nothing else.

### The matrix

One 5 × 4 grid spanning both halves, the same shape mesa2 uses, so the two boards behave
alike from the firmware's point of view.

- **5 columns, one per finger, shared across the halves.** The index column carries all
  four index keys: `I`/`E` on the left, then out over the RJ-45 to `I`/`E` on the right.
  Same for the other four columns.
- **4 rows, two per half.** `ROW_A`/`ROW_B` are the left's far and near rows,
  `ROW_C`/`ROW_D` the right's.
- **7 signals between the halves**: 5 columns + `ROW_C` + `ROW_D`. One of the RJ-45's
  eight conductors is spare.
- 18 keys in 20 slots; the two empty ones are where the deleted pinky `R` keys were.

Per column: pinky 2 keys, ring 4, middle 4, index 4, thumb 4.

- [ ] Make a mesa3 directory
- [ ] Copy the mesa2 **Rev B** design project to mesa3/mesa3-left and mesa3/mesa3-right,
  renaming projects and refs
- [ ] Manually create the split (human) — left keeps the Tiny2040, all four SK6812s, the
  Tag-Connect and the reset pad; right is switches, diodes and the RJ-45 only
- [ ] Assign the 7 matrix nets to RJ-45 pins, then cross-check the pinout is identical at
  both ends so a straight-through cable is correct (AI, as in `mesa1/DESIGN.md`)
- [ ] Manually layout design (human). The unibody rotation and the fixed hand separation
  stop mattering — each half is positioned independently on the desk — so the only thing
  left to choose is how the outline sits around the keys
- [ ] Draw new left outline (human)
- [ ] Reflect and generate right outline (AI)
- [ ] Place the RJ-45 and its edge relief notch (mesa1 learned to put it on B.Cu so the
  relief moves with it)
- [ ] Mounting holes and feet — reuse `davidb-keyboard-foot.pretty`; decide standoffs
  vs. adhesive feet
- [ ] Reroute
- [ ] ERC clean, DRC clean on both halves
- [ ] Write `mesa3/LAYOUT.md` and `mesa3/DESIGN.md` in the mesa1 style
- [ ] Check the built halves against the shared matrix map from Rev B — same net at the
  same key, no board-specific exceptions
- [ ] Design review
- [ ] Git commit

Deferred until the boards exist: the case/plate models, and the keymap itself.

## Fab batch

One order, four boards, after every design above is reviewed.

- [ ] Same `.kicad_dru` and stackup across all four boards
- [ ] Each board's silkscreen carries its name and rev, so the bare boards are
  distinguishable on arrival
- [ ] Fabrication Toolkit outputs for each board; bare PCBs, not assembly — the sockets
  and 1N4148Ws are hand-soldered (confirm at order time)
- [ ] 3D viewer sanity check on each board
- [ ] Place the order
- [ ] Git commit the production outputs with the order date
