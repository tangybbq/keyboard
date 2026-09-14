# mesa3 — reference geometry

Geometry for both halves of the Mesa 3. The keys are inherited wholesale from mesa2
Rev B — this file records where they ended up once the board was cut in two, and what
survived the split unchanged.

Companion to `DESIGN.md`, which holds the decisions rather than the coordinates.

KiCad convention throughout: **+X is right, +Y is down.**

## The frame both halves share

Neither half was re-origined. Both keep **mesa2's coordinate frame**, so the two boards
overlap in coordinate space even though they are separate PCBs — the left spans
x 28..152 and the right x 118..242. That is deliberate and it is what makes the symmetry
checkable: the mirror axis is still **x = 135**, and every left/right pair sums to
exactly 270.000.

Each half is **124.0 × 111.0 mm**.

## Key positions

Nine keys per side, 18 in total in Rev A. Rotations are negated between the halves; y is
identical. Rev B adds the `FN` mode key on the left only, listed separately below because
it is the one key that does not yet have a mirror partner.

| finger | left | x | y | rot | right | x | y | rot |
|---|---|---|---|---|---|---|---|---|
| pinky        | `SW_LA1` |   44.486 |  60.217 |  -27.1 | `SW_RA1` |  225.514 |  60.217 |  +27.1 |
| ring far     | `SW_LS1` |   64.733 |  40.136 |   +2.5 | `SW_RS1` |  205.268 |  40.136 |   -2.5 |
| ring near    | `SW_LO1` |   65.484 |  57.115 |   +2.5 | `SW_RO1` |  204.516 |  57.115 |   -2.5 |
| middle far   | `SW_LN1` |   86.880 |  38.690 |   -7.2 | `SW_RN1` |  183.119 |  38.690 |   +7.2 |
| middle near  | `SW_LT1` |   84.752 |  55.560 |   -7.2 | `SW_RT1` |  185.248 |  55.560 |   +7.2 |
| index far    | `SW_LI1` |  107.014 |  61.613 |  -32.0 | `SW_RI1` |  162.986 |  61.613 |  +32.0 |
| index near   | `SW_LE1` |   98.007 |  76.032 |  -32.0 | `SW_RE1` |  171.993 |  76.032 |  +32.0 |
| thumb outer  | `SW_LSP1` |  105.326 | 110.151 |  +48.4 | `SW_RSP1` |  164.674 | 110.151 |  -48.4 |
| thumb inner  | `SW_LBK1` |  118.032 | 121.450 |  +48.4 | `SW_RBK1` |  151.968 | 121.450 |  -48.4 |

Verified on the boards, not in a model: every pair sums to 270.000 in x, shares a y, and
has negated rotation.

### The FN mode key — Rev B, left half only

| key | ref | x | y | rot |
|---|---|---|---|---|
| mode | `SW_LFN1` | 113.272 | 85.571 | -32.0 |
| its diode | `D_LFN1` | 115.856 | 81.436 | +148.0 |

**Computed, not placed.** `mesa3/fnkey.py` derives it from `SW_LE1` and writes
`fn-placement.json`; `apply-fnkey.py` puts it on the board. The rule is a local offset of
**(18.000, 0) in `SW_LE1`'s own frame**, carrying `SW_LE1`'s rotation unchanged, so the
new cap sits parallel to the index near key and one place inboard of it.

The 18.000 mm is not chosen, it is forced: the 1u choc cap is **17.5 mm across local X**
and the board's air-gap target is **0.5 mm**, so 18.0 is the tightest pitch that does not
overlap. The resulting cap gap against `SW_LE1` is 0.500 mm exactly — the new worst gap on
the board, against the 0.496 mm the thumb pair already had.

`D_LFN1` follows at the same `(0, -4.876)` local offset and 180° rotation as every other
diode, and `fnkey.py` verifies that invariant across the existing keys before it relies
on it.

**No mirror partner yet.** Whether the right half gets one is still open. Until it does,
the "every pair sums to 270.000" invariant simply does not apply to this key — it is not
a violation, it is an absence.

If the right key is added, note the **sign**: local +X points *outboard* on the right
half, so the offset there is `SW_RE1` + **(-18, 0)** in that key's frame, not (+18, 0).
Positive would throw the key off the board rather than merely misplace it. With the sign
right it lands at `SW_RFN1` (156.728, 85.571) @ +32.0 and `D_RFN1` (154.144, 81.436),
which sum with the left pair to 270.000 in x for both the switch and the diode.

**Clearance.** The switches are on `F.Cu` and the keycaps stand above that face, so only
same-side parts can foul them. `JP1` passes within 0.52 mm of the new keycap edge in x/y
but sits on `B.Cu`, on the far side of the board, and is not a conflict — nor are `D1`,
`C1`-`C4`, `J1` or the diodes, all of which are back-side. The nearest part that shares
the front face is `LED1` at 15.67 mm centre to centre, well clear of the 12.03 mm cap
half-diagonal. `fnkey.py` reports the layer beside each neighbour so this distinction is
visible rather than inferred.

### What the positions inherit from mesa2 Rev B

None of this was re-derived for the Mesa 3; it is the Rev B geometry, and
`mesa2/LAYOUT.md` explains where it came from.

- **17.00 mm row pitch** in every finger column, and **17.00 mm** between the thumb keys
  as well — Rev B pulled the thumbs in by 1 mm so they match the finger rows. Worst
  keycap gap across the board is 0.496 mm against a 0.5 mm target.
- **The pinky is a single key**, rotated −27.1° on the left and +27.1° on the right, so
  its cap lines up with the other fingers instead of sitting across them. The direction
  is not visible in the geometry — both options are 180° apart and give the same cap
  orientation — it was settled by looking at which side the socket body and diode land on.
- **Diodes ride at a fixed local offset of (0, −4.876) mm** in their switch's frame,
  rotated 180°.

## Outlines

Both halves are **124.0 × 111.0 mm**, closed loops, and mirror images of each other
apart from one deliberate difference.

| | left | right |
|---|---|---|
| Edge.Cuts lines | 21 | 19 |
| closes through | A1's footprint cutout (5 segments) | itself |
| extent | x 28..152, y 26..137 | x 118..242, y 26..137 |

The left board keeps mesa2's trick of leaving the outline **open** where the Tiny2040
sits, letting the A1 footprint's own Edge.Cuts segments close the loop. The right half
has no MCU, so it closes there with a straight inner edge instead. Both were checked
vertex by vertex: every endpoint meets exactly one other.

**The RJ-45 relief notches mirror exactly** — x 147..152 on the left, x 118..123 on the
right, both y 106..111.

## Mounting holes

Four per half, M2, mirrored exactly — every pair sums to 270.0 and shares a y.

| left | x | y | right | x | y |
|---|---|---|---|---|---|
| `H1` | 50.0 | 45.0 | `H2` | 220.0 | 45.0 |
| `H3` | 75.0 | 72.0 | `H4` | 195.0 | 72.0 |
| `H2` | 118.0 | 63.0 | `H5` | 152.0 | 63.0 |
| `H5` | 119.0 | 105.0 | `H6` | 151.0 | 105.0 |

**The designators do not agree between the halves**, because each was made by deleting a
different subset of mesa2's six holes. The same physical hole is `H1` on the left and
`H2` on the right. The positions are right; only the names are confusing, and renumbering
both to H1–H4 is the tidy-up if anyone cares.

## The RJ-45

| | left | right |
|---|---|---|
| position | (137.700, 104.000) | (132.000, 113.120) |
| rotation | −90° | +90° |
| layer | **B.Cu** | **B.Cu** |

Both on the back, following mesa1's finding that putting the jack on B.Cu moves its edge
relief with it.

The anchors look unrelated because **the footprint's origin is pad 1, not the body
centre**, and pin 1 sits at opposite ends of the two mirrored bodies. Comparing the pads
instead: every signal pad on the right is a uniform **0.300 mm** off the mirror of the
left's. Everything else on these boards mirrors to the micron, so that is drift rather
than intent — harmless inside a 5 mm notch, and worth 0.3 mm of nudge only if exact
symmetry matters to you.

## Routing

| | left | right |
|---|---|---|
| track segments | 308 | 118 |
| vias | 40 | 7 |

The right half is that much emptier because it carries nine keys and a connector and
nothing else — no power, no ground, no LEDs.
