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

**Everything here ends in one fab order.** It was planned as four PCBs — mesa2 Rev B,
mesa2x Rev A, mesa3-left, mesa3-right — and is now **three**: the 2x experiment was
completed, analysed and dropped, because the pairwise matrix cannot resolve chords and no
hardware change short of more pins fixes it. Fab cost is dominated by shipping, so the
remaining three designs must be finished and reviewed before anything is ordered.

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
| ~~mesa2x Rev A~~ | `mesa2/mesa2x` | 18 | pairwise — **not being fabbed**, see below | Tiny2040, unibody |
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

- [x] Copy the mesa2 Rev B dir to mesa2x (it lives at `mesa2/mesa2x`), rename the
  project files and internal refs
- [x] Assign the 18 keys to GPIO pairs — `SCAN_1..7` on GP0-GP4, GP27, GP28. All 21
  pairs available, 18 used, `5-4`/`6-1`/`7-1` spare. GP5, GP6, GP7 and GP29 freed
- [x] Fix the diode polarity convention — as built it is **cathode toward the
  lower-numbered pin**, the opposite of the guess here, applied consistently to all 18
  keys. Recorded in `SCANNING.md`
- [x] Rewire keys (human)
- [x] AI analysis of ghosting with arbitrary chords. **The result is negative and it is
  structural.** Two pressed keys `a→c` and `c→b` forge `a→b` through a two-diode sneak
  path, and **21 two-key chords forge a third real key** — `LA1`+`LBK1` reads as `LT1`,
  and so on. The forged key is electrically identical to a real one, so no scan order or
  timing resolves it. It is not the assignment's fault: 18 keys on 7 pins is 18 edges on
  7 vertices, and Mantel's theorem caps a triangle-free graph there at 12 edges, so
  triangles — and therefore ghosts — are unavoidable. The first pin count that fits 18
  keys triangle-free is **9**, where the optimum is the complete bipartite 4 × 5 graph:
  the conventional matrix mesa2 Rev B already uses. The pin saving and the ghosting are
  the same fact. Full analysis and the chord tables are in `mesa2x/SCANNING.md`
- [x] Write `mesa2x/SCANNING.md` — pin map, key table, the six strobe steps, pull
  configuration, settle and debounce, the ghost tables, and the hardware change that
  would fix it. The algorithm did **not** come out clean on paper, which per this task's
  own terms means the board is wrong rather than the firmware — see the decision below
- [x] Make the silkscreen clearly distinguish this board from the Rev B one
- [x] Reroute (human)
- [x] ERC and DRC — **DRC has no errors**, schematic parity is clean, and the single
  unconnected item is the Tiny2040 GND false positive. ERC carries the inherited noise
  plus four now-unused pins (GP5, GP6, GP7, A3)
- [x] Design review — findings below
- [x] Git commit

### Design review

The board is built correctly and does what it was drawn to do. The experiment answers
its question, and the answer is no.

- **DRC clean, parity clean.** 18 keys, 18 diodes, all on distinct pin pairs with a
  consistent polarity. The LED supply work from Rev B came across intact: `D1`, `JP1`,
  `C1`-`C4`.
- **It buys back four GPIOs** — GP5, GP6, GP7, GP29 — exactly as advertised.
- **It cannot resolve chords**, and cannot be made to in firmware. See above.
- The two-diode voltage difference between a real press and a ghost is real but
  unusable: the RP2040's input thresholds are characterisation data, not guaranteed, and
  a ghost lands in the indeterminate band between V_IL and V_IH.
- **Series resistors do not fix it.** Checked with a DC solve of the real network, not
  by argument. Driving the non-read pins high does block the ghost, but it lifts the
  strobe node by a diode drop for every *other* key pressed on that strobe, and the real
  press rides up out of the low band with it — 1.79 V where it needs to be under 0.8 V.
  Trading a false key for a missed key. Making the strobe stiff instead recovers
  detection and hands the ghost back. The read pin sits one diode drop above the strobe
  for a real press and two for a ghost; resistors move the strobe node but never change
  that the separation is one Vf ≈ 0.6 V, where the RP2040's guaranteed levels need 1.2 V.
  A higher-Vf part raises both sides equally, and the ADC cannot help because the real
  press reads 0.41 V alone and 1.79 V with one more key down.

**Recommendation: drop it from the fab batch.** Reversing the earlier call to fab it
anyway. There is no configuration of this board that resolves chords, so a physical copy
would only demonstrate what the analysis already establishes, and the analysis is
structural rather than empirical. The useful output of the experiment is
`mesa2x/SCANNING.md`. Keep the project in the tree — it is finished, reviewed and
routed — and if the curiosity is ever worth a board, it is one file change to add back.

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
- [ ] Fix `sym-lib-table` in **four** projects: `mesa2/mesa2`, `mesa2/mesa2x`,
  `mesa3/mesa3-left`, `mesa3/mesa3-right`. All four say
  `${KIPRJMOD}/../mesa1.kicad_sym`, inherited from mesa1 where that path is correct —
  mesa1's own projects sit inside `mesa1/`, so `../` finds the symbol file. The copies
  do not, so it resolves to `mesa2/mesa1.kicad_sym` and `mesa3/mesa1.kicad_sym`, neither
  of which exists. That is the long-standing "symbol library 'mesa1' was not found"
  ERC warning.

  The fix is the same one string in all four, matching what `fp-lib-table` already uses:

      ${KIPRJMOD}/../../mesa1/mesa1.kicad_sym

  In the GUI: **Preferences → Manage Symbol Libraries → Project Specific Libraries**,
  edit the `mesa1` row's path. Leave mesa1's own two projects alone — they are correct
- [x] Manually create the split (human) — left keeps the Tiny2040, all four SK6812s, the
  Tag-Connect and the reset pad; right is switches, diodes and the RJ-45 only. The right
  half came out genuinely passive: 23 components, 17 nets, no power, no ground
- [x] Assign the 7 matrix nets to RJ-45 pins, then cross-check the pinout is identical at
  both ends so a straight-through cable is correct (AI, as in `mesa1/DESIGN.md`).
  **Verified identical**: pin 2 `COL_1`, 3 `COL_2`, 4 `COL_3`, 5 `COL_4`, 6 `ROW_D`,
  7 `ROW_C`, 8 `COL_5`, pin 1 spare. Pin order runs opposite between the halves, which
  is what a part that cannot be mirrored does, and does not matter since the nets match
- [x] Manually layout design (human). Both halves kept the mesa2 coordinate frame, so
  every key pair still sums to x = 270.000 with matching y and negated rotation
- [x] Draw new left outline (human) — 124 × 111 mm
- [x] Reflect and generate right outline (human) — also 124 × 111 mm. Both are closed
  loops: the left closes through A1's cutout as mesa2 did, the right closes on its own
  with a straight inner edge where the MCU cutout was. The relief notches mirror exactly
- [x] Place the RJ-45 and its edge relief notch — B.Cu on both halves, notches mirrored
  exactly (147-152 on the left, 118-123 on the right, y 106-111)

  **On the jack.** It is `54602`, not `54601` — 54601 is the RJ12 6P6C part, and KiCad
  ships footprints under both numbers. `54602-908LF` is **Active**, not discontinued;
  what looked like an EOL was a stock gap, with 3,120 landing at DigiKey on 16 Sep 2026
  and thousands more on Marketplace. Standard lead time is 22 weeks, so it is worth
  knowing the escape hatch:

  Its pin pattern is an industry standard — 8 pins staggered 1.27 mm in two rows 2.54 mm
  apart, 8.89 mm span, two posts 11.43 mm apart sitting 6.35 mm from the near row. The
  TE **1705951-1** matches it exactly (checked against TE's customer drawing), as do
  `RJ45_RCH_RC01937` (LCSC C708652), `RJ45_Ninigi_GE` and `RJ45_HALO_HFJ11-x2450HRL`,
  all already in KiCad's library. Not `RJ45_Bel_SI-60062-F` — that one is a magjack, and
  its magnetics would block the DC the matrix needs.

  So a jack swap is **not a layout change**: same pins, same posts, same position. The
  only difference is drill size. KiCad's 54602 footprint uses 0.76 mm signal holes and
  3.2 mm posts; every other footprint in that list uses 0.89-0.9 and 3.25, and TE's
  drawing asks for 0.9 ±0.1. If the Amphenol ever does go away, widening the drills is
  the whole migration. The shielded options additionally want two 1.6 mm tab holes —
  at y 9.4 for RCH and Ninigi, y 3.3 for HALO, so those two cannot both be covered.
- [x] Mounting holes — four per half, mirrored exactly (every pair sums to 270.0)
- [ ] Feet — reuse `davidb-keyboard-foot.pretty`; decide standoffs vs. adhesive feet
- [x] Reroute (human)
- [x] ERC and DRC on both halves — **DRC has no errors on either board**, schematic
  parity is clean on both, and the right half has nothing unrouted
- [x] Write `mesa3/LAYOUT.md` and `mesa3/DESIGN.md` in the mesa1 style — geometry and
  verification in the first, decisions in the second
- [x] Check the built halves against the shared matrix map from Rev B — **all 18 keys
  keep their exact mesa2 (column, row)**, so one keymap still serves Rev B and both
  halves and the firmware cannot tell them apart
- [x] Design review — findings below
- [x] Git commit

### Design review — findings, all accepted as-is

Nothing blocking, and none of it is being fixed: reviewed and deliberately left.

- **`J1` pin 1 unconnected on both boards**, one ERC error each. Deliberate — 7 signals
  over 8 conductors, and the eighth has no job to do. Running GND down it would achieve
  nothing: the right half has no ground net, so the wire would terminate in nothing. The
  return path for a scanned row is the column conductor it is switched into, so every
  loop already closes through two wires of the same cable. mesa1 runs the same way.
- **Silkscreen clipped by the board edge in 4 places** — A1's front silk at the left's
  inner edge, `J1`'s back silk on both boards. Cosmetic.
- **Mounting hole designators disagree between the halves** — H1/H2/H3/H5 on the left,
  H2/H4/H5/H6 on the right, left over from deleting different subsets of mesa2's six.
  The holes themselves are mirrored exactly; only the names differ.
- **The RJ-45 sits 0.300 mm off exact mirror**, uniformly, where the keys, holes and
  notches mirror to the micron. Harmless inside a 5 mm relief notch.
- **Four dangling 0.0254 mm wire stubs** — three on the left, one on the right. They are
  in the *schematic*, not on the boards, so they cost an ERC line each and nothing more.
- Inherited from mesa2 Rev B on the left: GP2/GP3 floating, `A1` GND2 on no net,
  `LED4` DOUT, `J2` pin 6, and `GND` without a `PWR_FLAG`.

**The "unconnected GND" DRC item is a false positive — do not chase it.** The symbol
ties the Tiny2040's GND pads into one net, so DRC wants copper between them, but the
module commons them internally and the board does not need to. The same item appears on
mesa2. A DRC exclusion is the only thing that would silence it.

Deferred until the boards exist: the case/plate models, and the keymap itself.

## Fab batch — ordered

**Ordered 2026-09-07**, immediately after the export, and the boards are in transit.
Three boards, not four: mesa2x was dropped before the order.

- [x] Same `.kicad_dru` and stackup across all boards — the three `.kicad_dru` files are
  byte-identical, and all three are 1.6 mm two-layer
- [x] Each board's silkscreen carries its name and rev, so the bare boards are
  distinguishable on arrival — `Mesa2/Rev B`, `Mesa3-left/Rev A`, `Mesa3-right/Rev A`
- [x] Fabrication Toolkit outputs for each board; bare PCBs, not assembly — the sockets
  and 1N4148Ws are hand-soldered (confirm at order time)
- [ ] 3D viewer sanity check on each board — done or skipped at order time, not recorded
- [x] Place the order
- [x] Git commit the production outputs with the order date — `mesa2_B.zip`,
  `mesa3-left_A.zip` and `mesa3-right_A.zip` are committed

Note that `mesa2x`'s silkscreen still reads `Mesa2 / Rev B` rather than naming itself.
It was never fabbed, so nothing came of it, but a revival would have to fix that first.

## Mesa 3 Rev B

Opened 2026-09-14, once Rev A had shipped. The letter was bumped on both halves before
any design change, so the boards arriving from the fab stay identifiable as Rev A.

### The change: a mode key per hand

**One extra key per half, immediately inboard of the near-row index key** (`SW_LE1` /
`SW_RE1`), for mode switching. It is a layer key, momentary or toggle, and it is
explicitly **not** part of chording — the lateral reach from the index home position is
too uncomfortable to chord from. This is the standing intent for every future board,
recorded before Rev A was routed and deliberately left out of it.

**It costs no GPIO and no cable conductor.** The Dosh layout dropped mesa2's outer pinky
`R`, leaving one empty slot per half in the 5 × 4 grid — 18 keys in 20 slots. Checked
against the Rev A netlists rather than assumed:

| half | pinky `A` sits at | free slot | conductors added |
|---|---|---|---|
| left | `COL_1` × `ROW_B` | **`COL_1` × `ROW_A`** | none — both local to the left |
| right | `COL_1` × `ROW_D` | **`COL_1` × `ROW_C`** | none — `COL_1` and `ROW_C` already cross |

Physical position and matrix position need not agree; the pinky column simply runs a
trace over to the index side. The right half's new key is free across the cable because
every net it needs is already one of the seven that cross.

Each new key still needs **its own diode**. "Does not chord" is a statement about chord
resolution in firmware, not licence to skip ghosting isolation.

### What this does to the firmware invariant

Rev A's hard constraint was that *the firmware must not be able to tell a mesa2 Rev B
from a Mesa 3* — one keymap, one build, no board-specific code. Adding these keys does
**not** break it, but it does bend it, and the distinction is worth stating:

- The grid is still 5 × 4, and all 18 existing keys keep their exact mesa2 `(column,
  row)`. Nothing is renumbered and no existing key moves.
- The two new keys land in slots that mesa2 Rev B and Mesa 3 Rev A simply **never
  assert**. One keymap therefore still serves every board; the mode key is unreachable
  on the boards that lack it, rather than wrong.
- So the invariant survives in the direction that matters (one build), but the keyboards
  are no longer feature-identical. A mesa2 Rev B has no mode key and whatever the mode
  key unlocks has to stay reachable some other way, or that board loses the function.

Decide this before routing, not after.

### Open before anything is routed

- [ ] **Name the key.** Every other ref follows the Dosh key name (`SW_LA1`, `SW_LE1`).
  Reusing `R` would be actively confusing — that was the outer pinky the layout deleted.
- [ ] **One hand or both.** Symmetry argues for both, and both are free; the input method
  may only want one. If only one, the other half's slot stays empty and mirroring breaks.
- [ ] **Placement, generated not nudged.** Geometry comes from the layout script, and the
  `LAYOUT.md` invariant (every left/right pair sums to 270.000 in x, shares a y, negates
  rotation) has to hold for the new pair too.
- [ ] **Mechanical clearance — the left half is the constrained one.** Inboard of
  `SW_LE1` at (98.007, 76.032) the left board already carries `A1` at (135, 59.7), the
  reset pad at (130, 85), `J2` at (139.835, 95.83) and `J1` at (137.7, 104). The right
  half's inner region is nearly empty by comparison — only `H5` (152, 63), `H6`
  (151, 105) and `J1` (132, 113.12) — so a position that clears the left will clear the
  right, and the left is what to solve first.
- [ ] Keycap gap against the 0.5 mm target, as for every other key pair.

### The interconnect stays RJ-45 — settled 2026-09-14

**The signal count does not change.** Seven still cross — five columns plus `ROW_C` and
`ROW_D` — because the new right-hand key reuses nets that already make the trip. Any
replacement connector therefore still needs **seven usable conductors**, the same bar
RJ-45 clears today with one pin spare.

**Decision: RJ-45 stays for Rev B.** USB-C was considered and set aside. The reasoning
below is kept because it is the argument, not just the answer, and because mesa3w will
have to make the same call.

The deciding point is not the pin count at all — it is **what is on the other end**. A
USB-C cable only starts to make sense if the right half gains an MCU of its own, because
then the link becomes a serial one between two smart halves, needing two or three
conductors rather than seven, and orientation stops mattering. Carrying a passive matrix
over USB-C is using a connector for something it was never shaped for. So the connector
question is really a topology question, and it should be reopened only if the right half
stops being passive.

The pin analysis, for when that question comes back:

- **A USB 2.0 C-to-C cable carries about five usable conductors** — `VBUS`, `GND`, `D+`,
  `D-` and one `CC`, plus shield. That is **fewer than the seven needed**, so if the
  cable is USB 2.0 the idea is dead on arrival regardless of how nice it is. Most cables
  sold for split keyboards are USB 2.0, because carrying one serial link is all they are
  asked to do.
- **A full-featured USB 3.x C-to-C cable** adds `SBU1`, `SBU2` and two SuperSpeed lanes
  (four pairs, eight wires), so conductors are not the constraint — there are well over
  seven.
- **Reversibility is the real problem.** A USB-C plug goes in either way up. The
  receptacle ties `A6/A7` to `B6/B7`, so `D+`/`D-` survive a flip, but `CC1`/`CC2` swap
  and the SuperSpeed lanes land on different pins depending on orientation. Devices
  normally resolve this with a CC-sensing mux. Without one, a passive matrix wired to
  those pins is a **different circuit depending on which way the user plugged it in** —
  and a matrix has no way to detect or correct that.
- **The failure mode is worse than RJ-45's.** A USB-C receptacle on a keyboard half
  invites plugging it into a real host or charger, which would put 5 V, or a PD
  negotiation, straight onto matrix lines. Nobody plugs an RJ-45 into a charger. This is
  the strongest argument for staying put.

On sourcing: Keebio is not a useful supplier for this kind of question. They publish no
datasheets to speak of — their surface-mount USB-C connector is listed with no part
number at all — because they are selling to people building from published kits rather
than designing boards. Anything of theirs would have to be characterised by continuity
test before it could be designed against, which is a poor foundation for an interconnect.

- [x] Determine what the candidate cable actually connects, then decide — moot; RJ-45
  stays, and the question is deferred to whether the right half ever gains an MCU
