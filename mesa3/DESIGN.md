# mesa3 — design decisions and setup notes

Companion to `LAYOUT.md`, which holds the geometry. This file holds the decisions: what
changes from mesa2, why, and what was checked.

Status: **Rev A ordered 2026-09-07 and in transit. Rev B is open** — see *Rev B* below.
Everything in this file describes Rev A unless a section says otherwise.

## What the Mesa 3 is

The mesa2 Rev B keyboard, cut into two independently-positioned halves in the style of
mesa1. Same 18 keys, same Dosh layout, same key geometry. A single **Tiny2040 on the
left half** runs everything; the right half is passive and reaches the left over one
RJ-45 cable.

```
mesa3/
  3dmodels -> ../mesa1/3dmodels     symlink, so ${KIPRJMOD}/../3dmodels resolves
  mesa3-left/    Tiny2040, 4x SK6812, Tag-Connect, reset pad, RJ-45, 9 keys
  mesa3-right/   9 keys, 9 diodes, RJ-45. Nothing else.
```

Both halves were made by copying the finished mesa2 Rev B project **whole** and deleting
the other side, rather than building each up from parts. That is why the geometry
survives exactly.

## The matrix

**One 5 × 4 grid spanning both halves** — not one matrix per half.

- **5 columns, one per finger, shared across the halves.** The index column carries all
  four index keys: `I`/`E` on the left, then over the cable to `I`/`E` on the right.
- **4 rows, two per half.** `ROW_A`/`ROW_B` are the left's far and near rows,
  `ROW_C`/`ROW_D` the right's.
- 18 keys in 20 slots. The two empty ones are where mesa2's outer pinky keys were.

Column-to-pin assignment, unchanged from Rev B:

| net | keys | Tiny2040 pin |
|---|---|---|
| `COL_1` | pinky `A`, both hands | GP7 |
| `COL_2` | ring `S`/`O` | GP6 |
| `COL_3` | middle `N`/`T` | GP5 |
| `COL_4` | index `I`/`E` | GP4 |
| `COL_5` | thumb `SP`/`BK` | A3/GP29 |
| `ROW_A` | left far | A2/GP28 |
| `ROW_B` | left near | A1/GP27 |
| `ROW_C` | right far | GP0 |
| `ROW_D` | right near | GP1 |

**GP2 and GP3 are spare** and stay that way — see *Which board am I?* below.

### The firmware must not be able to tell a Rev B from a Mesa 3

This is a hard constraint, not a nicety. All 18 keys keep their **exact mesa2 (column,
row)** — verified key by key against Rev B's netlist — so one keymap serves the unibody
and the split alike, and no board-specific code is needed.

## The interconnect

Seven signals cross: **5 columns + `ROW_C` + `ROW_D`**. The columns run straight through
because they are shared by both hands; only the right's two rows are local to it.

| RJ-45 pin | net |
|---|---|
| 1 | *unused* |
| 2 | `COL_1` |
| 3 | `COL_2` |
| 4 | `COL_3` |
| 5 | `COL_4` |
| 6 | `ROW_D` |
| 7 | `ROW_C` |
| 8 | `COL_5` |

**Verified identical at both ends**, which is what makes a straight-through cable
correct. This is the check mesa1 learned to do and the one that fails silently: get it
wrong and the cable quietly becomes a crossover.

The pin *order* runs in opposite directions on the two boards. That is not a mistake —
an RJ-45 cannot be mirrored, so on mirror-image boards the same part necessarily has its
pin 1 at opposite ends. Only the net mapping has to match, and it does.

**Pin 1 is left unconnected on purpose.** It is tempting to run a ground down it, but
there would be nothing to connect it to: the right half has no ground net. The return
path for a scanned row is the column conductor it is switched into, so every loop already
closes through two wires of the same cable. mesa1 runs the same way.

### The right half is genuinely passive

No power, no ground, no LEDs — 23 components and 17 nets, all of it switches, diodes and
the connector. Nothing on it needs a supply, so none crosses the cable.

## The LED supply, inherited from Rev B

Carried across unchanged, and it must not be dropped: **this board needs the diode.**
mesa2 Rev A shipped without one and had to be reworked by hand.

| part | role |
|---|---|
| `D1` (1N4148W) | series diode, `+5V` to the `+4V5` rail |
| `JP1` (SolderJumper, open) | across `D1`; solder to bypass |
| `C1`-`C4` (100nF) | one per LED across `+4V5`/`GND` |

An SK6812 wants data above 0.7 × VDD. At 5.0 V that is 3.5 V and the RP2040 drives 3.3 V;
dropping the LED rail to ~4.3 V moves the threshold to 3.0 V. Only LED1 is actually
marginal — LED2-4 are driven by the previous LED's DOUT, which swings to its own VDD —
but the diode sits in the common feed anyway, because that reproduces the Rev A rework
exactly and keeps all four LEDs at matching brightness. `mesa2/LAYOUT.md` has the longer
version.

## Which board am I?

Nothing on the board answers this, by design. **Each keyboard is flashed with a small
CBOR blob naming its model**, and the firmware reads that. No board-ID strap, no
GPIO burned, and it works on boards already fabbed — which a hardware scheme could not
have done for mesa2 Rev A.

## The RJ-45 part

`RJ45_Amphenol_54602-x08_Horizontal`, Amphenol **54602**-908LF. Note it is the 54602;
the 54601 is the RJ12 six-position part and KiCad ships footprints under both numbers.

The part is **Active**, not discontinued — a stock gap against a 22-week lead time is
what makes it look otherwise. The escape hatch, should it ever be needed: that staggered
pin pattern (8 pins at 1.27 mm in two rows 2.54 mm apart, 8.89 mm span, posts 11.43 mm
apart 6.35 mm from the near row) is an industry standard. The TE **1705951-1** matches it
exactly, as do `RJ45_RCH_RC01937` (LCSC C708652), `RJ45_Ninigi_GE` and
`RJ45_HALO_HFJ11-x2450HRL`, all already in KiCad's library. **Not**
`RJ45_Bel_SI-60062-F` — that is a magjack and its magnetics would block the DC the matrix
runs on.

A swap would therefore be a **drill-size change, not a re-layout**: KiCad's 54602
footprint uses 0.76 mm signal holes and 3.2 mm posts where the others use 0.89-0.9 and
3.25.

## Verification performed

- **DRC: no errors on either half.** Schematic parity clean on both. The right half has
  nothing unrouted.
- **Outlines close**, checked vertex by vertex.
- **Every key pair mirrors exactly** — sums to 270.000 in x, matching y, negated rotation.
- **RJ-45 pinout identical at both ends.**
- **All 18 keys keep their mesa2 (column, row).**

### Known and accepted

None of these are being fixed:

- `J1` pin 1 unconnected on both boards, one ERC error each. Deliberate.
- Silkscreen clipped by the board edge in four places — A1's front silk at the left's
  inner edge, `J1`'s back silk on both boards. Cosmetic.
- Mounting hole designators disagree between the halves. Positions are right; see
  `LAYOUT.md`.
- The RJ-45 sits 0.300 mm off exact mirror.
- Four dangling 0.0254 mm wire stubs, in the schematics only.
- Inherited from Rev B on the left: GP2/GP3 floating, `A1` GND2 on no net, `LED4` DOUT,
  `J2` pin 6, `GND` without a `PWR_FLAG`.

**The "unconnected GND" DRC item is a false positive.** The symbol ties the Tiny2040's
three GND pads into one net, so DRC wants copper joining them, but the module commons
them internally and the board does not need to. It appears on mesa2 as well. A DRC
exclusion is the only thing that silences it — do not add copper to satisfy it.

## Rev B

Opened 2026-09-14, the moment Rev A shipped, so the delivered boards keep a stable name.
The bump to Rev B touched the two title blocks, `sch_revision` and the silkscreen on each
half, and nothing else — no geometry, netlist or routing moved with it.

**The change is one extra key per hand, immediately inboard of the near-row index key,
for mode switching.** A layer key, momentary or toggle, deliberately outside the chording
set because the lateral reach from index home is uncomfortable. It was a standing intent
before Rev A was routed and was left out of Rev A on purpose, that board already being on
its way to fab.

It is nearly free, which is why it was worth waiting for a revision rather than
retrofitting. Checked against the Rev A netlists:

| half | pinky `A` occupies | slot left free by dropping `R` |
|---|---|---|
| left | `COL_1` × `ROW_B` | `COL_1` × `ROW_A` |
| right | `COL_1` × `ROW_D` | `COL_1` × `ROW_C` |

No GPIO is consumed, and **no new conductor crosses the cable** — `COL_1` and `ROW_C`
are already two of the seven that make the trip, so the right half's key is free on the
interconnect as well as in the matrix. The pinky column just runs a trace across to the
index side; matrix position and physical position need not agree. Each key still gets its
own diode.

The *firmware must not be able to tell a Rev B from a Mesa 3* constraint above bends
rather than breaks. All 18 existing keys keep their exact mesa2 `(column, row)`, and the
two new slots are ones the older boards never assert — so one keymap still serves every
board, with the mode key simply unreachable where it is absent. What is lost is
feature-identity: a mesa2 Rev B has no mode key, so whatever that key unlocks must stay
reachable another way on boards without it.

**The left half is the mechanically constrained one.** Inboard of `SW_LE1` the left board
already carries `A1`, the reset pad, `J2` and `J1`; the right half's inner region holds
only two mounting holes and its `J1`. Solve the left position first and the right will
follow.

**The interconnect stays RJ-45.** USB-C was considered on 2026-09-14 and set aside. The
requirement never moved off seven conductors, since the new key adds none, and a USB 2.0
C-to-C cable carries about five; a full-featured cable has enough but is not
orientation-safe without a CC-sensing mux, and a USB-C receptacle invites being plugged
into a charger in a way an RJ-45 never is. The real point is that the connector question
is a **topology** question: USB-C only makes sense if the right half gains an MCU, at
which point the link is a two- or three-wire serial one between smart halves rather than
a passive matrix stretched over a cable. Reopen it only if that changes.
`mesa3-tasks.md` has the full argument.

## Still to do

- **Feet.** Reuse `davidb-keyboard-foot.pretty`; standoffs vs. adhesive not yet decided.
- **Case and plate models**, once boards exist.
- The keymap itself. The matrix map above is what the firmware needs to bring the board
  up; the layout on top of it is separate work.
