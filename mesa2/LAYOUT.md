# mesa2 — key geometry

20 keys, placed on the board. Derived from `hand-scan-1.pdf` by `layout.py`;
`placement.json` holds the result and `layout-preview.svg` draws it 1:1.

## Method

1. **Mirror and average.** The two hands were marked on one sheet, so the axis
   midway between their centroids (sheet `x = 114.89`) is the real mirror line —
   the hand separation is a measurement, not a choice. The right hand is mirrored
   about it and averaged with the left, mark for mark. The unibody angle survives
   as the average of the two hands' rotations.
2. **Columns.** Centre = the rest mark (m2), the point the finger sits on between
   the two keys. Axis = principal direction of the three marks. Two keys at
   ±8.5 mm along that axis — the 17 mm pitch is fixed by the caps.
3. **Thumbs.** Two keys 18 mm apart on the measured arc, centred on it, caps
   turned across the direction of travel.

## Averaged hand

| finger | centre (sheet mm) | axis | left / right-mirrored | spread |
|---|---|---|---|---|
| pinky  | (28.49, 32.21) | **+57.9°** | +66.6 / +52.2 | 14.4° |
| ring   | (56.04, 26.98) | −2.5° | −1.1 / −3.8 | 2.7° |
| middle | (76.40, 27.30) | −12.2° | −1.2 / −25.2 | **24.0°** |
| index  | (91.14, 50.37) | −37.0° | −38.7 / −35.3 | 3.3° |

Column-centre spacing: pinky→ring 27.55, ring→middle 20.36, middle→index 14.74 mm.
Staggers: −5.23, +0.31, **+23.07** mm.

The middle column is the known left/right disagreement — 24° apart, so the
averaged −12.2° is a genuine compromise rather than a measurement. The index
stagger of +23 mm is the "index closer to my hand" correction, and both hands
agreed on it.

## Placed positions

Board frame, mirror axis at **x = 150**. Rotations are the column axis normalised
to nearest zero, as asked.

| key | x | y | rot | | key | x | y | rot |
|---|---|---|---|---|---|---|---|---|
| SW_LR1  |  54.71 |  43.20 | +57.9 | | SW_RR1  | 245.29 |  43.20 | −57.9 |
| SW_LA1  |  69.10 |  52.24 | +57.9 | | SW_RA1  | 230.90 |  52.24 | −57.9 |
| SW_LS1  |  91.02 |  34.00 |  −2.5 | | SW_RS1  | 208.98 |  34.00 |  +2.5 |
| SW_LO1  |  90.29 |  50.98 |  −2.5 | | SW_RO1  | 209.71 |  50.98 |  +2.5 |
| SW_LN1  | 113.21 |  34.49 | −12.2 | | SW_RN1  | 186.79 |  34.49 | +12.2 |
| SW_LT1  | 109.62 |  51.11 | −12.2 | | SW_RT1  | 190.38 |  51.11 | +12.2 |
| SW_LI1  | 131.27 |  59.08 | −37.0 | | SW_RI1  | 168.73 |  59.08 | +37.0 |
| SW_LE1  | 121.04 |  72.66 | −37.0 | | SW_RE1  | 178.96 |  72.66 | +37.0 |
| SW_LSP1 | 124.67 | 106.56 | +43.4 | | SW_RBK1 | 175.33 | 106.56 | −43.4 |
| SW_LBK1 | 137.03 | 119.65 | +43.4 | | SW_RSP1 | 162.97 | 119.65 | −43.4 |

Key field **190.6 × 85.6 mm**. Every left/right pair sums to exactly 300.00 in x,
shares a y, and has negated rotation — verified on the board, not just in the model.

### Column nudges

Two pairs of caps fouled at the measured spacing, so columns were pushed **outward**
by the minimum that clears 0.5 mm. Angles and staggers are untouched.

| column | nudge |
|---|---|
| pinky | 1.70 mm |
| ring | 0.50 mm |
| middle | 0.10 mm |
| index | 0.10 mm |

The binding pairs were pinky-near vs ring-near (the pinky's 57.9° swings its near
key inboard) and ring-near vs middle-near. After nudging, the worst gap across all
190 cap pairs is exactly +0.50 mm.

## Matrix → finger

**Rev A** numbered the two hands' columns in opposite order, so a shared column
joined *different* fingers — `COL_1` was the left pinky and the right index,
`COL_4` the left index and the right pinky, and `COL_2`/`COL_3` swapped ring and
middle the same way. It worked, since every column still carried four keys and the
firmware maps (column, row) to a key regardless, but it read as a mistake every
time anyone looked at it.

**Rev B pairs the columns by finger**, the same finger on both hands:

| net | keys | Tiny2040 pin |
|---|---|---|
| `COL_1` | pinky `A`, both hands | GP7 |
| `COL_2` | ring `S`/`O`, both hands | GP6 |
| `COL_3` | middle `N`/`T`, both hands | GP5 |
| `COL_4` | index `I`/`E`, both hands | GP4 |
| `COL_5` | thumb `SP`/`BK`, both hands | A3/GP29 |
| `ROW_A` | left far row | A2/GP28 |
| `ROW_B` | left near row | A1/GP27 |
| `ROW_C` | right far row | GP0 |
| `ROW_D` | right near row | GP1 |

The columns run GP7 down to GP4, not GP4 up to GP7: once the columns paired by
finger, that order made the fan-out to the MCU tidier. **GP2 and GP3 are free**, and
their wire stubs already exist at (54.61, 144.78) and (54.61, 147.32) — that is where
a board-ID strap would go. `RGB` is on A0/GP26.

- ROW_A (left) and ROW_C (right) are the **far** row, away from you.
  ROW_B / ROW_D are the **near** row.
- With the outer pinky `R` gone, `COL_1` holds two keys and the far cells
  (`COL_1`, ROW_A) and (`COL_1`, ROW_C) are empty. Every other column holds four.
- LSP/RBK are the outer thumb position, LBK/RSP the inner — LSP inherits mesa1's
  outer thumb position, and the rest follows the mirror.

## Open, in rough priority order

- **The pinky's 57.9° is the thing to check on the mockup.** It comes from
  treating the elbow between the three pinky marks as a straight column axis,
  which is the weakest assumption in the whole derivation. The measured pinky
  travel is also asymmetric — 14.5 mm one way, 4.8 mm the other, on both hands —
  so a column centred on the rest point puts the near key somewhere the finger
  did not actually reach.
- **Diodes are not placed.** They still sit at their mesa1 positions, and the
  left set is on B.Cu while the right set is on F.Cu — worth reconciling.
- **Board outline** is not drawn.
- **Socket edge clearance.** `Kailh_socket_PG1350` is asymmetric: it reaches
  9.575 mm from the switch centre one way and ~4.6 mm the other. With rotations
  now at arbitrary angles rather than 0/180, mesa1's finding that only one
  rotation combination clears does not carry over — the outline has to be fitted
  to these angles.

---

## Board outline

`outline.py` (`uv run --with shapely python outline.py`) -> `outline.json`,
exported by `dxf.py`. Preview: `outline-preview.svg`.

**226.1 x 111.1 mm**, 141.6 cm2, one piece, **33 vertices**, every switch at
2.00 mm.

Built from **convex hulls** of switch clusters, not a morphological closing. The
closing approach was abandoned for two reasons: its 26 mm arcs could not be
straightened into hard corners by any simplify tolerance, and `simplify` broke
mirror symmetry, because Douglas-Peucker walks the ring from an arbitrary start
vertex and so decides differently on each side. Hulls are straight-edged by
definition and symmetric for symmetric input.

Pieces, all unioned then offset by MARGIN with mitre joins:

| piece | what it does |
|---|---|
| hull of all 16 finger switches | both hands *and* a solid centre in one shape |
| hull of each hand's 2 thumbs | |
| hull of {index-near, outer thumb} | the arm joining fingers to thumbs |
| hull of {LBK1, RSP1} | bridge between the thumb clusters |
| MCU body box | solid board for the Tiny2040 |

Then a **V notch** between the thumbs (apex (axis, 120.5), half-width 15.5 at the
bottom edge) and the **MCU channel**, both cut last.

### The footprint envelope has to be symmetric

`Kailh_socket_PG1350` is asymmetric - x -9.575..6.351 - and the two hands'
sockets are **rotated, not mirrored**, so an outline derived from the real extent
is asymmetric by construction. It uses a centred envelope instead:

```
FP = (-9.575, -7.450, 9.575, 7.450)
```

This costs ~3 mm of board on one side of each switch and buys exact symmetry.
It also makes the outline robust to rotating a socket 180 degrees during routing.

Symmetry is asserted, not assumed: the shape is compared against its own mirror
about the switches' axis (x = 135.7123, derived from the switch positions, not
from A1). Residual is 0.36 mm2, all of it A1 sitting 2.7 um off that axis.

### MCU

```
A1 -> (135.715, 57.0) rot -90     (unchanged; the outline is fitted to it)
```

Board is solid between LI1 and RI1 - the 21.55 mm gap takes the 18 mm body with
3.55 mm spare - and the module's own Edge.Cuts cutout is the slot. Pads sit
6.67-9.67 mm from the centreline against board from 6.30 mm, so they land fully
on copper. A 12.6 mm channel is cut from the top edge down to y = 57.70; it is
only ~3 mm deep, and it is also the only route for a USB cable.

### Importing - the outline is an OPEN chain

`dxf.py` **omits the one segment spanning the cutout opening**, so the DXF is an
open chain whose two loose ends are (129.415, 57.70) and (142.015, 57.70). The
footprint's cutout closes the loop. Emitting a closed polygon as well gives KiCad
a T-junction at each endpoint - three edges meeting - which it rejects.

LINE entities, layer `Edge_Cuts`, `$INSUNITS = 4` (mm), **DXF y = -(KiCad y)**,
coordinates relative to the outline's bounding box (KiCad checks the import
against the page, and an absolute offset counts against that budget).

1. Delete the existing Edge.Cuts polygon.
2. File > Import > Graphics, layer **Edge.Cuts**, at the offset `dxf.py` prints.
3. Ungroup afterwards.

Page is **US Letter**, tight for a 226 mm board - set Page Settings to A3 if the
import is refused. The page is only the drawing sheet; it does not affect fab.

### Still outside the outline

LED1-4, J2 and RESET1 are parked at x ~283-311. The solid centre is their home.

---

## Rev B geometry

**The board is the record of truth.** `placement.json`, `sw.json` and the *Placed
positions* table above all predate the 5° hand rotation and no longer match
`mesa2.kicad_pcb`. `revb.py` reads the positions straight out of the board, applies
the Rev B changes and writes `revb-placement.json`; nothing else is authoritative.

Three changes from Rev A:

1. **The outer pinky keys are gone** — `SW_LR1`/`SW_RR1` and `D_LR1`/`D_RR1`.
   18 keys, 9 per side.
2. **The surviving pinky keys rotate 90°**, −90 on the left and +90 on the right,
   landing on −27.1° and +27.1° — still negated like every other key pair, so the
   diodes stay mirrored.

   **The direction cannot be chosen from the geometry.** Both directions give the
   same keycap orientation: they are 180° apart and the cap is a rectangle, so
   every clearance number is identical either way. What changes is which side the
   socket body and the diode land on. That was settled by looking at the board —
   +90/−90 put both on the wrong side. If a future change makes this look
   arbitrary, it is not; the clearance table cannot see the difference.
3. **The SP thumb keys move 1 mm toward BK**, 18.003 → 17.003 mm. The thumb caps
   are turned across the direction of travel, so the pair is separated along the
   cap's 16.5 mm axis exactly as the finger rows are; 18 mm left a 1.50 mm gap
   where every finger row has 0.50 mm.

Diodes ride at a fixed local offset of **(0, −4.876) mm** in their switch's frame,
rotated 180°. `revb.py` verifies that invariant across all 20 Rev A keys before
using it, so "adjust the diodes of the moved keys" is just preserving it.

### Target positions

| key | x | y | rot | | key | x | y | rot |
|---|---|---|---|---|---|---|---|---|
| SW_LA1 |   44.486 |  60.217 |  -27.1 | | SW_RA1 |  225.514 |  60.217 |  +27.1 |
| SW_LS1 |   64.733 |  40.136 |   +2.5 | | SW_RS1 |  205.268 |  40.136 |   -2.5 |
| SW_LO1 |   65.484 |  57.115 |   +2.5 | | SW_RO1 |  204.516 |  57.115 |   -2.5 |
| SW_LN1 |   86.880 |  38.690 |   -7.2 | | SW_RN1 |  183.119 |  38.690 |   +7.2 |
| SW_LT1 |   84.752 |  55.560 |   -7.2 | | SW_RT1 |  185.248 |  55.560 |   +7.2 |
| SW_LI1 |  107.014 |  61.613 |  -32.0 | | SW_RI1 |  162.986 |  61.613 |  +32.0 |
| SW_LE1 |   98.007 |  76.032 |  -32.0 | | SW_RE1 |  171.993 |  76.032 |  +32.0 |
| SW_LSP1 |  105.326 | 110.151 |  +48.4 | | SW_RSP1 |  164.674 | 110.151 |  -48.4 |
| SW_LBK1 |  118.032 | 121.450 |  +48.4 | | SW_RBK1 |  151.968 | 121.450 |  -48.4 |

### Clearance

Worst keycap gap over all pairs: **Rev A 0.494 mm → Rev B 0.496 mm** (ring column,
untouched by any of this). The pairs the changes actually affect:

| pair | Rev A | Rev B |
|---|---|---|
| pinky `A` vs ring `O` | 0.869 | 0.681 |
| pinky `A` vs ring `S` | 6.854 | 7.354 |
| thumb `SP` vs `BK` | 1.503 | **0.503** |

Nothing drops below the 0.5 mm target, and the thumbs now match the finger rows.

---

## Rev B — the SK6812 supply

**The LED chain needs a series diode, and this board is the one that proves it.**
Rev A shipped without one and had to be reworked by hand: cut the +5 V feed, solder a
diode in. A dozen other boards of mine with the same trick have not needed it, so do
not carry "it'll be fine" over from them — this combination of the -HS part, this 5 V
source and a 3.3 V data line does not work without the drop.

Why: an SK6812 wants its data high above **0.7 × VDD**. At 5.0 V that is 3.5 V, and the
RP2040 drives 3.3 V — under the threshold. Dropping VDD to ~4.3 V puts the threshold at
3.0 V and the 3.3 V logic clears it.

Only **LED1** is actually marginal. LED2-4 are driven by the previous LED's DOUT, which
swings to its own VDD, so they are in spec either way. The diode still sits in the
common feed rather than LED1's alone, because that reproduces the Rev A rework exactly
and keeps all four LEDs at matching brightness.

As built in Rev B:

| part | role |
|---|---|
| `D1` (1N4148W) | series diode, anode on `+5V`, cathode on the new `+4V5` rail |
| `JP1` (SolderJumper_2_Open) | across the diode; **open by default**, so the diode is in circuit. Solder it closed to bypass |
| `C1`-`C4` (100nF) | one per LED, across `+4V5`/`GND` |

The jumper defaults to the configuration that is known to work here, and the escape
hatch is for a future LED lot that does not need the drop.

**Mesa 3 inherits this circuit**, LEDs and all, on its left half. Carry the diode, the
jumper and the caps across with it.

### ERC noise, and what is left of it

The LED diode is `D1`, renamed out of the matrix-diode naming it first landed in, and
`PWR_FLAG`s on `+5V` and `+4V5` cleared the "Input Power pin not driven" reports that
inserting a series element in a rail produces. ERC is down from 12 entries to 10.

What still reports, all of it inherited from Rev A and none of it electrical:

- **`A1` `GND1`: "Input Power pin not driven".** `GND` is the one rail with no
  `PWR_FLAG` on it. One more flag clears this.
- **`A1` `GND2`: unconnected, twice** (once as a floating pin, once as undriven power).
  The pad is not on any net. Tying it to `GND` clears both — the Tiny2040 commons its
  grounds internally, so it is free to do.
- **`A1` `GND1` again, in DRC**: the pad is on `GND` but has no copper reaching it. A
  short hop from the existing `GND` track clears the board's only unconnected item.
- `GP2`/`GP3` floating with their 0.0254 mm stubs — spare pins, and they stay spare: the
  firmware identifies the board from a flashed CBOR model blob, not from the hardware,
  so no board-ID strap is needed. `LED4` DOUT and `J2` pin 6 are chain-end and
  no-connect respectively.

Doing the three `GND` items together would take ERC to six and DRC to zero unconnected,
which is worth it mainly so a real problem cannot hide in the noise later.
