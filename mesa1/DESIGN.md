# mesa1 — design decisions and setup notes

Companion to `LAYOUT.md`, which holds the recovered geometry. This file holds the decisions
about how mesa1 is built and what changes from proto4.

Status: **libraries built; KiCad projects not yet created.**

## What exists so far

```
mesa1/
  LAYOUT.md                              recovered geometry
  DESIGN.md                              this file
  mesa1.kicad_sym                        project symbols
  mesa1.pretty/
    Kailh_socket_PG1350.kicad_mod        upgraded to KiCad 10 format
    Pimoroni_Tiny2040.kicad_mod          new, built from Pimoroni's Eagle package
  mesa1-left/   fp-lib-table sym-lib-table
  mesa1-right/  fp-lib-table sym-lib-table
```

Both lib tables use `${KIPRJMOD}`-relative URIs, so the projects are self-contained and do
not depend on this machine's global KiCad tables. Drop a new KiCad project into either
directory and the `mesa1` libraries are already wired up.

Verification performed:

- both footprints parse and render under `kicad-cli` 10.0.5 (`fp export svg`)
- the symbol library parses and renders (`sym export svg`)
- all 19 Tiny2040 pad positions match Pimoroni's `.lbr` exactly, after negating Y for
  KiCad's downward axis
- all 19 symbol pin *numbers* match the footprint pad *names* exactly, both directions

Board outlines and all 30 switch placements are done and verified against the actual
`.kicad_pcb` files — 15 sockets per board, no pad off-board, worst clearance +1.147 mm
(mesa1-left, LNUM0) and +1.425 mm (mesa1-right, TS0).

Both schematics are complete and netlist-verified, including a cross-check that the RJ-45
pinout is identical at both ends (straight-through cable is correct).

**mesa1-left**: 38 components — 15 switches, 15 diodes, 4 LEDs, Tiny2040, RJ-45 (B.Cu),
Tag-Connect, reset pad. Outline valid (21 segments, incl. A1's cutout).

**mesa1-right**: 31 components — 15 switches, 15 diodes, RJ-45 (B.Cu). Outline is an exact
mirror of the left's plus the mirrored latch notch; 17 segments, closed loop.

Still to do: routing both boards.

### Matrix diodes

`Diode_SMD:D_SOD-123`, cathode (pad 1) to `ROW_n` — the same convention as proto4. Confirmed
the stocked part is SOD-123; the slightly smaller SOD-123W would also solder fine on this
land pattern, so the choice is not critical for hand assembly.

> **Assembly note: the band does not face the same way on both halves.** Grid diodes have the
> cathode toward −X on mesa1-left and +X on mesa1-right; the thumb diodes are the opposite
> again. This follows from the socket rotations (left grid 180°, right grid 0°) and is
> correct, not an error. **Orient by the silkscreen** — the banded end goes into the closed
> end of the three-sided bracket — rather than by copying the pattern from the other half.
>
> Note also that `Device:D` numbers the **cathode as pin 1**, which is the opposite of many
> diode symbols. Re-check the netlist if the symbol is ever swapped.

### Connector placement — mirror the BODY, not the origin

Both the RJ-45 footprint and the notch caught this. The Amphenol footprint's origin is at
pad 1, **4.445 mm off the body centre in Y and 5.1 mm in X**. Two consequences:

- The **latch notch** must be centred on the jack *body*, not the footprint origin.
- **Mirroring the right-hand jack** by mirroring its origin position puts the body in the
  wrong place. Because the right board's jack is rotated 180° from the left's, the
  origin-to-body offset flips sign, so the correction is *twice* the offset — 8.89 mm in Y.

Correct placements: left J1 origin (218.55, 102.77) rot −90; right J1 origin
(114.45, 111.66) rot 90. Both B.Cu. Both put the body centre at y 107.215, mirrored in x
about 166.5 (223.65 / 109.35).

### Outline asymmetry is fine

The left board's top edge carries the Tiny2040 slot; the right has no MCU and no slot, so
the two perimeters are not exact mirrors there. **This is not a problem** — proto4 does the
same and the mirrored 3D-printed stand fits both halves.

Known and deferred: silkscreen DRC warnings originate on **B.Fab**, which is not fabricated.
Cosmetic, no action needed.

### Library provenance — checked against Konnect, keep the current files

Konnect's operating rules say libraries should be built through its MCP tools. These were
hand-generated first, so they were re-checked. Conclusion: **keep them.**

- `Kailh_socket_PG1350.kicad_mod` and `mesa1.kicad_sym` were both rewritten by KiCad's own
  serializer (`kicad-cli fp upgrade` / `sym upgrade`), so the bytes on disk are KiCad's.
- `Pimoroni_Tiny2040.kicad_mod` was forced through a KiCad reserialization round-trip in a
  scratch copy. All 19 pads identical as numbers; Edge.Cuts, F.Fab, F.CrtYd and F.SilkS
  geometry identical segment-for-segment; UUIDs preserved. Only differences were cosmetic
  (`0.0` vs `0`, paste/mask layer ordering).
- The symbol was independently regenerated with `create_symbol` and compared: **all 19 pins
  matched exactly** on number, name, electrical type, position and angle.
- Both project lib tables resolve correctly through Konnect, `${KIPRJMOD}` expanding as
  intended.

Two limitations found in Konnect's library tools, worth knowing before relying on them:

1. **`create_footprint` takes only pads.** There is no parameter for arbitrary graphics, so
   it cannot express Pimoroni's `Edge.Cuts` cutout — the single most important feature of the
   Tiny2040 footprint. Rebuilding through it would silently drop the slot.
2. **`get_footprint_info` mis-parses KiCad-format footprints.** It reports `pad_count: 0` for
   any footprint using KiCad's multi-line pad serialization — including files KiCad itself
   wrote — because it only matches Konnect's own single-line style. Do not use it to validate
   footprints; use `kicad-cli` instead.

Konnect also writes `(version 20240108)` (KiCad 8-era) where KiCad 10 writes `20260206`.
Valid, and KiCad upgrades it on read, but it means round-tripping through Konnect is a
format downgrade.

### Placement rule for the Tiny2040 cutout — read before placing

Pimoroni's cutout is an **open** polyline: five segments, open at the module-end side at
package `x = 0.7`, endpoints `(0.7, ±6.3)`. It is open by design, because the module hangs
off the edge of the host board so the USB port is reachable. **The board outline has to
close it**, or KiCad will report an unclosed board edge.

Concretely: place the footprint so the board's edge passes exactly through `(0.7, ±6.3)` in
footprint coordinates. With the footprint origin at the module end and +X running into the
board, that means the origin sits **0.7 mm outside the board edge**.

Note this differs from proto4, where the board edge sat at package `x = −0.71` — 1.41 mm
further out — because the slot there was hand-drawn to the edge rather than taken from
Pimoroni. Do not copy proto4's placement value directly.

---

## Toolchain

Target **KiCad 10.0.5 only** (`/Applications/KiCad/KiCad.app`, `kicad-cli` 10.0.5). No
attempt at 8.0 compatibility.

### Library plumbing — this needs doing before anything else

Two real blockers, both a consequence of the custom libraries only ever having been
registered under KiCad 8:

1. **KiCad 10's global `fp-lib-table` contains only stock libraries.** None of
   `keyswitches.pretty`, `davidb-keyboard-foot.pretty`, or `Keebio-Parts.pretty` are
   registered. They exist only in `~/Library/Preferences/kicad/8.0/fp-lib-table`, with
   absolute `/Users/davidb/...` URIs.
2. **KiCad 10's global `sym-lib-table` contains no custom libraries at all.**
   `~/Documents/KiCad/8.0/symbols/David Brown Keyboard Parts.kicad_sym` is unregistered, and
   it lives outside this repo.

Plan: give each mesa1 project a **project-local** `fp-lib-table` and `sym-lib-table` using
`${KIPRJMOD}`-relative URIs, and commit them. That makes the projects self-contained and
reproducible instead of depending on this machine's global tables. Example:

```
(lib (name "keyswitches")(type "KiCad")(uri "${KIPRJMOD}/../../keyswitches.pretty")(options "")(descr "Kailh keyswitches and sockets"))
```

Symbols that mesa1 actually needs should be copied into a repo-tracked
`mesa1/mesa1.kicad_sym` rather than referenced from `~/Documents/KiCad/8.0/`.

### Legacy footprint format

Every footprint in `keyswitches.pretty` is in the KiCad 5-era `(module ...)` format.
`kicad-cli fp upgrade` converts them cleanly — verified on a scratch copy, which came back
as `(footprint ...)` with `(version 20260206)`.

Do this on a **copy** committed under mesa1's control, not in place on `keyswitches.pretty`,
so the older projects that still reference it are not disturbed.

---

## Mirroring: mesa1-right

proto4 did *not* mirror — both halves shared identical coordinates (see `LAYOUT.md`). That
was a workaround, not a design choice: mirroring the board was too much trouble, so the
right hand was built by soldering the switches onto the **back** of an identical board.

**That escape hatch is gone in mesa1.** proto4 used through-hole `PG1350` switches, which
can be inserted from either face. `Kailh_socket_PG1350` is SMD with its pads on `B.Cu`
only — the socket can only ever mount on one side. So mirroring is now mandatory rather
than merely tidier.

The transform, about a vertical axis at `x = A`:

```
x' = 2A - x
y' = y
rot' = -rot
```

`A` is TBD because the outline may change. If the outline is kept as-is, the natural choice
is the bounding-box centre, `rel x = 66.5`.

### Socket rotation differs between the hands — and must

The two boards use **opposite grid rotations**: left 180°, right 0° (thumbs −30° and −150°
respectively). This is not an oversight and cannot be tidied up.

`Kailh_socket_PG1350` is asymmetric: pad 2 sits at x = −8.275 with a 2.6 mm pad, reaching
**9.575 mm** from the switch centre on one side and only ~4.6 mm on the other. The pinky
column sits **9 mm** from the board edge. So at one rotation the socket overhangs the edge by
0.575 mm, and at the other it clears comfortably — and because mirroring puts that edge on
the opposite side of the board, the two hands need opposite rotations.

Only 0° and 180° are available. Any other angle physically rotates the keycap; that is why
the thumbs are −30°/−150° (a 180° pair) rather than an angle that scores better on
clearance but sits the keycap wrong.

All 16 rotation combinations were evaluated against the outline. **Exactly one clears**:

```
left grid 180°, left thumbs -30°, right grid 0°, right thumbs -150°   worst +1.147 mm
```

Every other combination puts at least one pad off the board. Expanding the outline does not
create additional options — it only makes the working combination comfortable.

Practical consequence: switches insert rotated 180° relative to each other on the two halves.

**This was checked feature-by-feature against the footprint, not assumed.** Exactly the three
mechanical features are invariant under a half-turn:

| feature | position | invariant under 180°? |
|---|---|---|
| centre boss, ⌀3.429 | (0, 0) | **yes** |
| positioning post, ⌀1.702 | (−5.5, 0) | **yes** |
| positioning post, ⌀1.702 | (+5.5, 0) | **yes** |
| pin holes ⌀3.0 at (0, 5.95) and (−5, 3.75) | — | no — move with the socket |
| pads 1 and 2 | — | no — move with the socket |

So the switch body sits in an identical physical position on both hands, retained by the same
centre boss and the same two posts on the horizontal axis. Everything that moves, moves
*together with the socket*, which is what makes the arrangement sound rather than merely
tolerable.

Keycaps are unaffected: the Choc stem is itself 180°-symmetric, so a cap mounts either way
round independent of switch rotation. The differing rotation is invisible from the top.

**Leftover feature:** the footprint also carries a ⌀0.991 mm NPTH at (5.22, −4.2) which is
neither structural nor electrical — it is one of a symmetric pair in the `_reversible`
variant, so here it is a vestige (probably an in-switch LED leg). It is the only feature that
lands somewhere genuinely different on each hand. Harmless, but a candidate for deletion if
in-switch LEDs are never fitted.

### Why rotations negate rather than the footprints being flipped

The reflection applies to the *arrangement*, never to an individual footprint. Each
footprint is only ever translated and rotated — never mirrored onto the other copper layer.
A Choc switch is a physical part that is the same in both hands; you do not get a
left-handed switch.

The consequence, which is expected and fine: because `Kailh_socket_PG1350` is asymmetric,
the socket bodies point in a rotated — not mirrored — direction on the right half. The two
finished boards will not look like mirror images in the socket area. Electrically and
mechanically this is correct. **The one thing to watch is edge clearance**: the socket
extends to `x = -8.275 + 1.3 ≈ -9.6` on one side and `+4.6` on the other, so a key that
clears the board edge comfortably on the left half may not on the mirrored right half.
Check the column-0 and thumb keys specifically.

### The reversible alternative, and why not

`keyswitches.pretty/Kailh_socket_PG1350_reversible.kicad_mod` carries duplicate pads on both
`F.Cu` and `B.Cu`, so one PCB works either way up. That is the trick that lets a single
design serve both hands. It does not suit mesa1, since the halves are genuinely different
boards — only the left carries the MCU — so the extra pads and the second pair of
`np_thru_hole` alignment holes would be dead weight. Use the plain
`Kailh_socket_PG1350`.

---

## Changes from proto4

### Notches become footprints

Agreed, and it is the idiomatic approach. KiCad footprints may carry `Edge.Cuts` graphics
that contribute to the board outline — confirmed present in stock libraries, e.g.
`Battery.pretty/BatteryHolder_Keystone_1057_1x2032` and
`LED_SMD.pretty/LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount`.

Both outline features have now been identified, and both are exactly the case this is for.

**The 12 × 18 mm feature is the Tiny2040 slot, not a tab.** Traversing the outline, the top
edge dips *down* (into the board) between x = 195 and x = 207, so material is removed. It is
clearance for the components on the underside of the Tiny2040, which bridges the slot and
solders to board material either side. Full detail, including its recovery from the Eagle
source, is in the Tiny2040 section below.

This also explains why the feature is absent from `proto4-right`: no MCU, no slot.

**The 5 × 5 mm notch is RJ-45 relief.** The RJ-45 at `(200.76, 110.02)` rot 90 works out to
board `x 196.1..215.0`, `y 101.1..117.6`. Its outer face lands exactly on the right board
edge at x = 215, and the notch (`x 210..215`, `y 107..112`, centred y = 109.5) sits centred
on the jack (centred y = 109.4). It is the cable-entry / latch relief at the edge.

Rolling both into their footprints is therefore straightforwardly right, and it pays off
immediately: **moving the RJ-45 to the back side moves its edge relief with it**, instead of
requiring a hand-edit of the outline. Same for the Tiny2040 slot if its position shifts.

### RJ-45 3D model

`3dmodels/RJ45_Amphenol_54602-x08_Horizontal.step` — a plain rectangular prism, generated
because KiCad's footprint references a `.step` that the distribution never shipped (only
`RJ45_Amphenol_RJHSE538X.step` exists), leaving a dangling reference.

X/Y are taken from the footprint's own F.Fab outline, so it registers to the pads with no
offset; Y is negated for KiCad's 3D coordinate convention.

```
X  -3.21 .. 12.10   (15.31 mm)
Y -13.97 ..  3.77   (17.74 mm)
Z   0.00 .. 13.50   (13.50 mm)
```

> **The 13.5 mm height is deliberately oversized.** The real jack measures ~12 mm. This is a
> **clearance proxy for case design**, not an accurate part model — it errs 1.5 mm large on
> purpose. Do not use it for fit or interference checking where the true height matters.

Attach via Footprint Properties → 3D Models with the project-relative path
`${KIPRJMOD}/../3dmodels/RJ45_Amphenol_54602-x08_Horizontal.step`.

Still missing for case work: the **mating plug envelope** (plug + strain relief projects
~25–30 mm beyond the jack face, plus finger room for the latch). That, not the jack body, is
what the case aperture has to clear.

### RJ-45 moves to the back side

proto4 used the Eagle-imported `C-BMJ-0051-RJ45`. Don't carry that forward — jolt3 already
uses the stock **`Connector_RJ:RJ45_Amphenol_54602-x08_Horizontal`**, which is in KiCad 10's
default libraries and needs no library work.

Back-side placement is just placing the footprint on `B.Cu`. Two things to check: that the
jack body clears whatever the board sits on, and that a horizontal jack on the back does not
fight the case or the riser boards.

### Tag-Connect replaces the Cortex-M debug header

Matches the jolt3 decision — see `jolt3/README.md`, which notes it needs no components, only
holes and pads, and occupies about the same area as the Cortex-M connector.

Footprint: **`Connector:Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical`**, as used in
`jolt3/j3-mez-2040`. Also stock, also no library work. Being the `-FP` (footprint-only, no
legs) variant it needs retention — check what jolt3 does about holding the cable in place.

### Tiny2040 castellated mount — this is the main piece of new work

**The Tiny2040 did not survive the Eagle conversion.** `proto4-left.kicad_sch` has the
`TINY2040` symbol, but `proto4-left.kicad_pcb` has no matching footprint — 37 footprints,
none of them an MCU. The land pattern exists only in the original Eagle board.

Recovered from `proto4/proto4-left.brd`, where the part is `element A1`,
`library="pimoroni-boards"`, `package="TINY2040"`, at `(56.16, 17.29)` rot `R270`. That is
**Pimoroni's own footprint**, not a hand-drawn one. Downloading the current upstream
`pimoroni-boards.lbr` and diffing confirms it is byte-identical — same 19 SMD pads, same
dimension layer, same silkscreen. Pimoroni has not revised it, so this geometry is
authoritative.

#### Official land pattern

All pads `F.Cu` only, 2.54 mm pitch, each 1.9 mm along the row × 3.0 mm radial.

| row | position | pins (in order) |
|---|---|---|
| upper | `y = +8.17`, `x = 1.27 … 19.05` | 0, 1, 2, 3, 4, 5, 6, 7 |
| lower | `y = −8.17`, `x = 1.27 … 19.05` | 5V, GND1, 3V3, A3, A2, A1, A0, GND2 |
| end | `x = 19.49`, `y = +2.54, 0, −2.54` | SWDIO, GND3, SWCLK |

Row spacing is therefore **16.34 mm**, and the origin sits at one end of the module, not at
its centre. Module body is 18 mm wide (silk at `y = ±9`) × 20.32 mm long (silk `x = 0 … 20.32`).
Pads straddle the module edge: centred at 8.17 with 3 mm radial extent, so 6.67 … 9.67 —
2.33 mm under the module and 0.67 mm proud of it for the solder fillet.

#### This settles the footprint question

`davidb-keyboard-foot:Pimoroni-Tiny2040` (untracked, KiCad-native) uses **17.78 mm** row
spacing with 2.54 × 1.524 mm pads and a centred origin. That disagrees with Pimoroni's
official pattern by 1.44 mm on row spacing. **Do not use it** unless there is a known reason
Pimoroni's is wrong. Rebuild the footprint in KiCad from the Eagle package above.

#### The cutout is part of Pimoroni's package

Pimoroni's package carries its recommended milling cutout on Eagle **layer 20 (Dimension)**:

```
(0.7, 6.3) → (16.62, 6.3) → (17.62, 5.3) → (17.62, −5.3) → (16.62, −6.3) → (0.7, −6.3)
```

That is **12.6 mm wide × 16.92 mm long with 1 mm chamfers** at the far end. Its purpose is
clearance for the components on the underside of the module — the module bridges the slot,
resting on 2.7 mm of board material each side, which is where the castellations land.

So the cutout was always meant to travel with the footprint. Folding it into the KiCad
footprint's `Edge.Cuts` restores Pimoroni's original intent rather than inventing anything.

#### Slot width — decided: use Pimoroni's 12.6 mm

Mapping Eagle to KiCad coordinates for proto4-left — verified against two independent parts,
`RESET (48, −10) → (193, 94)` and `CORTEX U$2 (56.96, −10.04) → (201.96, 94.04)`:

```
kicad = (eagle_x + 145, 84 − eagle_y)
```

A1 therefore lands at KiCad **(201.16, 66.71)**, and Pimoroni's cutout maps to
`x 194.86 … 207.46`, `y 67.41 … 84.33`. The Edge.Cuts actually in `proto4-left.kicad_pcb` is
`x 195 … 207`, `y 66 … 84` — a plain rectangle, chamfers dropped, snapped to the mm grid,
and **12.0 mm wide against Pimoroni's 12.6 mm**.

Someone redrew it by hand and tightened it 0.3 mm per side. **On the built board that is
quite tight**, so mesa1 goes back to Pimoroni's specified 12.6 mm, chamfers included.

Consequence: the slot no longer lands on the mm grid. That is fine — once the cutout lives
inside the footprint, only the footprint's placement needs to be on grid, and the cutout
follows it. This is a second reason to fold the cutout into the footprint rather than draw
it into the outline by hand.

#### Reset wire pad — keep as-is

`RESET`, a single-pad `SMD1,27-2,54` wirepad at KiCad `(193, 94)`. A wire runs from it to
the reset button on the Tiny2040 itself. This exists because the RP2040 does not reset
peripherals on a soft reset over SWD, so the J-Link needs a real reset line. It is intended
to be permanent, not a bodge.

There is no better option available on the board side: **the Tiny2040 brings out no RUN or
RESET castellation.** Its 19 pads are 0–7, 5V, GND1–3, 3V3, A0–A3, SWCLK, SWDIO — reset
appears only as the physical button. So the wire has to be hand-run to the button whatever
the board does, and a single wirepad is the correct board-side answer. Carry it forward
unchanged; just place it where the wire run is short and mechanically sensible.

#### Side note

The module mounts on `F.Cu`, the same face as the keycaps, while the sockets are on `B.Cu`.
That is only tolerable because it drops into the slot, so the slot is not optional.

### MCU choice — Tiny2040, and why not the alternatives

**Tiny2350: ruled out.** Verified against Pimoroni's current `pimoroni-boards.lbr` — the
`TINY2350` package has **16 pads to the Tiny2040's 19**, and the three missing ones are
exactly `SWCLK`, `SWDIO`, and `GND3`. Pimoroni brought SWD out to castellations on the 2040
and then dropped it on the 2350. With no debug access it is not usable here, regardless of
the newer silicon.

```
TINY2040 (19): 0-7, 5V, GND1, GND2, GND3, 3V3, A0-A3, SWCLK, SWDIO
TINY2350 (16): 0-7, 5V, GND1, GND2,       3V3, A0-A3
```

**PGA2350: wrong shape for this board.** It is 25.4 × 25.4 mm with 64 PGA holes in two
rings around the edge. Using it would mean adding a socket *and* providing the USB connector
on the keyboard PCB, since the module has neither. That is a significant amount of extra
board area and BOM for a 15-key half — overkill here even setting aside the extra design
work. Not for mesa1.

It is not in Pimoroni's `.lbr` either, which ships only `PGA2040_PTH_NO_SLOT`,
`PGA2040_PTH_WITH_SLOT`, and `PGA2040_SMT_WITH_SLOT`. The repo's untracked
`davidb-keyboard-foot.pretty/PIMORONI-PGA2035-PM722.kicad_mod` **is** this part despite the
name: 64 through-hole pads spanning 22.86 × 22.86 mm in a ~26.5 × 27.2 mm body. The `2035`
looks like a transposition of `2350`. Worth renaming if it is ever used.

This is worth writing down because it constrains the future: the debug story depends on the
module exposing SWD on castellations, and that is not a given across Pimoroni's range. Any
substitute MCU module has to be checked for SWD castellations first.

### Outline changes

Open. The recovered outline in `LAYOUT.md` is the proto4 shape and is a reasonable starting
point, but nothing depends on keeping it. Note that changing it changes the mirror axis `A`
above.

---

## Open questions

- Where does the thumb cluster anchor? Its 18 mm / 30° spacing is exact but its origin is
  off-grid; pick a clean anchor for mesa1 rather than importing proto4's.
- Where does the reset wirepad go, now that the RJ-45 and debug header are moving? Its only
  constraint is a short, sensible wire run to the module's button.
- Do the LEDs from proto4-left (4 × SK6812-MINI-HS) carry forward?
