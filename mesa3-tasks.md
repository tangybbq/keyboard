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
  and Taipo makes sense on it, and Rev B/Mesa 3 have neither. **Already solved in
  software:** each keyboard is flashed with a small CBOR blob naming its model, so the
  firmware reads the model rather than probing the hardware. No board-ID strap, no
  GPIO, nothing to design in — and it works on Rev A, which is already fabbed and could
  not have been changed anyway. GP2 and GP3 simply stay free.
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

**Status:** schematic and PCB both carry the Rev B netlist and placement. What is
left is routing, the outline, and the fab-facing tidying.

**Konnect's IPC path is unusable here** — it segfaults KiCad 10.0.5 on writes *and*
on read-only queries. Footprint placement goes through `apply-revb.py`, which drives
KiCad's own bundled `pcbnew` module (KiCad must be closed). Net changes still come
from *Update PCB from Schematic* in the GUI.

- [x] Remove the outermost pinky key
  - [x] Delete `SW_LR1`, `SW_RR1`, `D_LR1`, `D_RR1` from the schematic — with the
    eight wire stubs that tied those two cells to their row and column buses
  - [x] Update the matrix map in `LAYOUT.md` — the pinky column now carries one key
  - [x] Delete the four footprints from the PCB — via *Update PCB from Schematic*,
    which also re-applied the column nets
- [x] Rotate the pinky keys 90° so that their orientation is similar to the other
  finger keys. **−90 on the left, +90 on the right**: `SW_LA1` +62.9 → −27.1,
  `SW_RA1` −62.9 → +27.1. The direction is not visible in the geometry — the two
  options are 180° apart, so the cap lands identically and every clearance number
  matches; only the socket body and diode change sides. Settled by looking at the
  board, and written down in `LAYOUT.md` so the numbers don't argue for the wrong
  one later
- [x] Move the Sp keys 1mm closer to the Bk key: 18.00 mm → **17.00 mm**. Checked — the
  thumb pair is separated along the cap's 16.5 mm axis, same as the finger rows (the
  caps are rotated across the direction of travel), so Rev A's 18 mm leaves a 1.50 mm
  gap where every finger row has 0.50 mm. 17.00 mm makes the thumbs match everything
  else exactly.
- [x] Fix the mirrored column pairing — one column per finger, the same finger on
  both sides (see *What the firmware sees*). Done by moving the right-hand symbols
  between grid cells, so every wire stayed put: index ↔ pinky and middle ↔ ring
- [x] Decide and implement the Rev A / Rev B distinction — **nothing to do on the
  board.** Each keyboard carries a flashed CBOR blob naming its model, so the firmware
  reads the model directly. GP2 and GP3 stay free
- [x] Adjust the diodes of the moved keys. Mechanical: every diode sits at local
  (0, −4.876) mm in its switch's frame, rotated 180°, verified across all 20 Rev A
  keys — the targets in `revb-placement.json` already preserve it
- [x] Generate the Rev B geometry (AI) — `revb.py` reads Rev A straight out of
  `mesa2.kicad_pcb` and writes `revb-placement.json`. Note `placement.json`,
  `sw.json` and `LAYOUT.md`'s original table all predate the 5° hand rotation and do
  **not** match the board; the PCB is the record of truth
- [x] Apply `revb-placement.json` to the PCB — `apply-revb.py`, via KiCad's bundled
  `pcbnew` module. All 36 footprints verified against the target; board structure
  unchanged (50 footprints, 401 segments, 41 vias, one zone)
- [x] Re-run the cap clearance check over all remaining pairs (AI). Worst gap
  0.494 → 0.496 mm, and it is the ring column, untouched by any of this. The pinky's
  tightest neighbour goes 0.869 → 0.681 mm and the thumbs land on 0.503 mm, matching
  the finger rows. Nothing drops below the 0.5 mm target
- [x] Fix the routing (human)
- [x] Adjust the board outline (human)
- [x] Confirm the six M2 mounting holes are still inside the outline and clear of
  sockets and caps
- [x] Fixup label for Rev B
- [~] Print the 1:1 placement sheet and check it against my hands before fab (human).
  Mockup printing now. Low stakes: Rev A is in daily use and the geometry barely moved
  — one key gone, one cap rotated in place, thumbs in by 1 mm.
- [x] Update `LAYOUT.md` to the Rev B geometry — target positions, the rotation
  reasoning, the diode invariant and the clearance table
- [ ] Write the shared matrix map — column/row net to key for both Rev B and Mesa 3, plus
  scan order and debounce expectations. This is what the firmware agent implements from
- [x] ERC — no new violations. The 8 errors that remain are byte-identical in
  Rev A (dangling GP2/GP3 stubs, `LED4` DOUT, `J2` pin 6, and the Tiny2040's power
  pins having no driving output pin on a board it powers itself)
- [x] DRC clean — **0 errors**, down from 58 before the reroute. The 9 remaining
  warnings are all the cosmetic "footprint does not match copy in library" note.
  Schematic parity: 0 issues. One unconnected item, A1 pad `GND1`, which Rev A has
  identically
- [x] Design review — findings below
- [x] Git commit Rev B

Both cosmetic loose ends are closed: the LED diode is `D1` now, and `PWR_FLAG`s on
`+5V` and `+4V5` took ERC from 12 entries to 10. What remains is all inherited from
Rev A — `GND` wants a flag of its own, `A1`'s `GND2` is on no net, and `GND1` has no
copper reaching it on the board. See *ERC noise* in `LAYOUT.md`; worth doing before
fab only so a real problem cannot hide in the noise.

Rev B keeps `COL_1..5 × ROW_A..D` — 18 keys in 20 slots, the two empty ones being the
deleted pinky `R` keys. Don't re-pack to free a GPIO: the Tiny2040 has pins to spare, and
Mesa 3 needs this exact shape. The columns ended up on **GP7..GP4** rather than GP4..GP7,
reassigned once they paired by finger to make the fan-out to the MCU tidier.

### Design review

**Verdict: no defects. What is left is decisions, not fixes.**

Checked and clean: DRC 0 errors · schematic parity 0 issues · ERC unchanged from Rev A ·
all 36 footprints still exactly on `revb-placement.json` after routing · outline
214.0 × 111.0 mm, centred on the mirror axis, and closed (it is an open chain by design,
and A1's five Edge.Cuts segments meet both loose ends) · six M2 holes present with no
edge or hole clearance violations · silkscreen carries the rev · track widths
0.25/0.3/0.5 mm on 0.6/0.3 mm vias, all comfortably inside fab limits.

Findings, in priority order:

1. ~~The Rev A / Rev B distinction is undecided.~~ **Resolved in software** — the
   flashed CBOR model blob already identifies the board, so no strap is needed and
   GP2/GP3 stay free.
2. ~~No decoupling on the four SK6812s.~~ **Done** — `C1`-`C4`, one 100 nF per LED
   across `+4V5`/`GND`. Along with it, the LED supply diode Rev A needed as a hand
   rework is now designed in: `D_RE2` in series, `JP1` open across it to bypass.
   See *Rev B — the SK6812 supply* in `LAYOUT.md`.
3. A1's `3V3`/`5V` pins have no decoupling either. Ignorable: the Tiny2040 is a module
   and carries its own.
4. A1 pad `GND1` is unrouted, exactly as in Rev A. The module commons its grounds and
   GND3 is routed, so it is cosmetic — but it sits in the DRC report permanently and
   could mask a real unconnected item later. A short hop clears it.

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

- [x] Make a mesa3 directory — with a `3dmodels` symlink to `../mesa1/3dmodels`, so the
  boards' `${KIPRJMOD}/../3dmodels/…` model paths resolve the same way mesa2's do
- [x] Copy the mesa2 **Rev B** design project to mesa3/mesa3-left and mesa3/mesa3-right,
  renaming projects and refs. Both halves start as the *complete* 18-key board, to be
  cut down rather than built up. Verified identical to mesa2: same 55 components, 43
  nets, 55 footprints at identical positions, 409 segments, 41 vias, 26 outline lines.
  Only the names, the rev (each half starts at Rev A) and the silkscreen differ.
  Not carried over: `production/`, the freerouting `.dsn`/`.ses`, the stale `.step`
  export, `fpdiff.py`
- [ ] Fix `sym-lib-table` in both halves. It says `${KIPRJMOD}/../mesa1.kicad_sym`,
  which resolves to `mesa3/mesa1.kicad_sym` and does not exist — it is wrong in mesa2
  too, and is the source of the long-standing "symbol library 'mesa1' was not found"
  ERC warning. It wants `${KIPRJMOD}/../../mesa1/mesa1.kicad_sym`, the shape
  `fp-lib-table` already uses. Fixing it here stops it propagating further
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
