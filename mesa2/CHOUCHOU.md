# mesa2 — key positions

**Scope: key positions only.** 10 keys per side, Taipo. Nothing here is about the MCU,
the matrix, diodes or wiring — none of that is decided and none of it constrains the
geometry at this stage.

**chouchou is used for its key positions and nothing else.** Its MCU choice, its diodeless
trick, its matrix, its case and its outline are all out of scope. What is worth having is
the measured arrangement of its ten keys, because you printed it and it felt close.

---

## 1. chouchou's positions, in a hand-local frame

The board's left-half switch angles are −15/−25/−30/−35°. The −30° common term is the
unibody rotation; remove it and what is left is the hand geometry. Rotating the left half
by +30° about the middle column's lower key gives an editable parameter set:

| key | x | y | rot |
|---|---|---|---|
| pinky upper  |  58.42 |  76.68 | **+15°** |
| pinky lower  |  62.82 |  93.11 | +15° |
| ring upper   |  81.48 |  62.49 | **+5°** |
| ring lower   |  82.96 |  79.42 | +5° |
| middle upper | 103.45 |  55.61 | **0°** |
| middle lower | 103.45 |  72.61 | 0° |
| index upper  | 127.93 |  63.68 | **−5°** |
| index lower  | 126.45 |  80.61 | −5° |
| thumb inner  | 139.21 | 115.81 | +88° |
| thumb outer  | 157.19 | 116.44 | +88° |

+X right, +Y toward you. Row pitch is **exactly 17.00 mm** in every column.

As parameters, walking outer → inner:

| junction | spread (Δx) | stagger (Δy) | splay |
|---|---|---|---|
| pinky → ring   | 20.15 | −13.68 | −10° |
| ring → middle  | 20.48 |  −6.81 | −5° |
| middle → index | 23.00 |  +8.00 | −5° |

Two mechanics worth knowing:

- **chouchou's splay pivots on the lower key**, not the column centre — `rows:` lists
  `bottom` first, so that is where ergogen anchors. This is why its pinky's *upper* key sits
  4.40 mm further out than its lower one; all the swing lands in the top row.
  **mesa2 does not copy this** — see the rest-position section below.
- **The thumb line is horizontal in this frame** (+2.0°). The 32° visible on the raw board
  was nothing but the unibody rotation. The two caps are 18.00 mm apart and sit 35.20 mm
  below and 12.76 mm inboard of the index lower key.

---

## 2. The rest position is between the keys

Steno: the finger sits on the ridge **between** a column's two keys, so it can rock onto
either or press both. It does not rest on the upper key. Three consequences, and they run
right through everything else here:

- **The column's anchor is its centre**, not either key. mesa1 and chouchou both parameterise
  from a key; mesa2 should parameterise from the rest point, because that is the thing your
  hand actually locates.
- **Splay must pivot about that centre.** This was an open question earlier and the
  ergonomics settle it: the rest position is where the finger returns to, so it is the point
  that should stay put when a column rotates. chouchou pivoting on the lower key throws its
  whole splay into the top row, which is wrong for a hand that rests in the middle.
- **Row pitch is not a free parameter.** The cap sets a floor — 16.5 mm along the column
  plus 0.5 mm of air is 17.0 mm — and chording both keys of a column with one fingertip
  wants the pitch as *small* as possible. Both constraints push the same way, so the pitch
  sits on its floor. 17.0 mm is not inherited from chouchou by habit; it is forced, which is
  why proto4, mesa1 and chouchou all landed on it independently.

  The consequence for the parameter set: a column is fully described by **three numbers** —
  centre x, centre y, and splay. The two key positions follow.

Re-expressed centre-to-centre, chouchou reads:

| | pinky | ring | middle | index |
|---|---|---|---|---|
| centre (x, y) | (60.62, 84.90) | (82.22, 70.95) | (103.45, 64.11) | (127.19, 72.14) |
| stagger vs middle | +20.79 | +6.84 | 0 | +8.03 |

| junction | spread, centre-to-centre | vs lower-key anchoring |
|---|---|---|
| pinky → ring   | 21.60 | +1.45 |
| ring → middle  | 21.23 | +0.75 |
| middle → index | 23.74 | +0.74 |

The pinky junction gains most, because chouchou's +15° swing pushes that column's centre
outboard of its lower key.

---

## 3. Your corrections

From typing on the printed board, with 1U caps throughout:

| | direction | knob |
|---|---|---|
| column spacing | less, overall | spread, all three junctions |
| pinky | nearer the palm | pinky stagger, up from 20.49 |
| index | nearer the palm | index stagger, up from 8.00 |
| pinky axis | more rotated | pinky splay, up from +15° |
| thumbs | wrong angle, further out | thumb line angle and reach |

### Cap clearance is not the constraint — say so plainly

`clearance.py` computes the minimum column spread that keeps two 1U caps 0.5 mm apart,
using the real staggers rather than assuming same-row neighbours:

| junction | chouchou | minimum |
|---|---|---|
| pinky → ring (pinky at +22°) | 20.15 | **16.08** |
| ring → middle | 20.48 | **18.16** |
| middle → index | 23.00 | **18.06** |

And more pinky rotation barely costs anything once the stagger is there — at 13.68 mm of
stagger, going from +15° to +30° moves the minimum only 16.31 → 15.97 mm. Increasing the
pinky's stagger, which you want anyway, opens it further: at 22 mm of stagger the minimum
drops to 12.71 mm.

So **the two things that looked like they fight each other do not.** Pick spread from what
your hand wants, not from what the caps allow; the caps are nowhere near binding.

The one junction to watch is ring → middle at 18.16 mm, because it has the least stagger
(6.81 mm) to hide behind. V2 below sits at 18.00 there and comes in at +0.32 mm of air
rather than the 0.5 mm target — buildable, but it is the first thing that will pinch.

### Two candidates, bracketing the amount

All centre-anchored, centre-pivoted, rock 17.0:

| | spread (p→r / r→m / m→i) | stagger (p / r / m / i) | splay (p / r / m / i) | worst cross-column gap |
|---|---|---|---|---|
| chouchou | 21.60 / 21.23 / 23.74 | 20.79 / 6.84 / 0 / 8.03 | +15 / +5 / 0 / −5 | — |
| **V1** modest | 19.00 / 19.50 / 21.00 | 24.00 / 6.84 / 0 / 12.00 | +21 / +5 / 0 / −5 | +1.10 |
| **V2** stronger | 18.00 / 19.20 / 19.50 | 27.00 / 7.00 / 0 / 15.00 | +26 / +6 / 0 / −6 | +0.62 |

**ring → middle is the binding junction**, and it is the only one that is. It has the least
stagger to hide behind (6.84 mm), and under V2's splays it cannot go below **19.08 mm**.
Every other junction has several millimetres of room — pinky → ring clears down to 17.28 mm
even at +21°.

Both apply every correction in the same direction; they differ only in how far. Generated,
collision-checked and drawn 1:1 by `mesa2.py`.

### Thumbs

Angle and reach are both unresolved and both need measuring. Your thumb pivots at the CMC
joint, so its comfortable positions lie on an **arc**; a two-key straight line can be
tangent to that arc but not follow it, and placing the tangent needs the pivot. That is a
measurement, not a guess.

One number that surprised me and is worth keeping in view: chouchou's thumbs already sit
**35.20 mm** below the bottom row where proto4's sit **27.40 mm**. chouchou is the further
of the two and you want further still, so this is not a case of chouchou being tighter than
what you are used to.

---

## 4. Sheets

All A4, 1:1, left hand. Print at 100%, no fit-to-page, and check the 100 mm box.

| file | what it is |
|---|---|
| `measure-wide.svg` | **both hands on one 240 x 146 mm grid**, single landscape page. Start here |
| `variants-1to1.svg` | V1 and V2 finger geometry, side by side with their parameters |
| `thumb-1to1.svg` | thumb pair at −15/0/+15°, at two reaches; index column redrawn in every cell so reach is constant across a row |
| `measure-blank.svg` | 5 mm grid, origin cross, desk-edge datum — for free marking and the thumb arc |
| `measure-ghost.svg` | same grid with chouchou's ten keys ghosted in, for marking corrections |

Generators: `mesa2.py` (geometry, collision check, variant and thumb sheets),
`measure.py` and `measure-wide.py` (measurement sheets), `clearance.py`
(spread-vs-splay limits). The portrait sheets are 196 x 268 mm and the two-hand
sheet is 258 x 196 mm landscape, so all of them print unscaled on both A4 and US
Letter; `.pdf` versions sit alongside the `.svg`.

### Marking, with a pen and nothing else

Nothing to acquire. The objection to holding a pen only applies to the hand being *measured* —
so mark each hand with the other one.

**Keep the hand planted and lift one finger at a time.** The remaining three fingers hold the
posture, so the hand does not drift while you mark the spot the lifted finger was resting on.
Put it back, move to the next.

**Three dots per finger, not two**: where it rests, rocked forward, rocked back. The rest dot
is the column centre and the outer two give the column angle. Their *separation* is not the
row pitch — that is fixed at 17 mm by the caps — so treat it as diagnostic only: if a
finger's comfortable rock comes out well under 17 mm, that finger cannot chord its column
and the cap size becomes the problem.

Do the left hand, then **re-place both hands naturally** before doing the right. That
re-placing step is what keeps the angle between the hands honest, and it is the only part of
the procedure that is easy to skip and expensive to get wrong.

If none of this appeals, the coarse loop still works and needs nothing at all: print the
variant sheets, rest your hands on them, and say which is closer and in which direction. That
is exactly what produced the corrections in section 2, and it has the advantage of being the
method you have already shown works.

### The unibody angle is not separable from the spacing

Working hand-local does **not** discard the unibody angle — it separates it from the column
parameters so each can be changed without disturbing the other. The board still carries it.

But the two are genuinely coupled, and the direction is: **narrower spacing puts the hands
closer together, the forearms converge more steeply, and the angle wants to be larger.** So
the angle cannot be measured once and reused across spacings — it has to come out of the
same session as the spacing it belongs to, and be re-taken if the spacing moves materially.

This also disposes of the datum problem. The unibody angle is not an angle relative to the
desk; it is **the angle between the two hands**. Mark both hands on one sheet without moving
the paper and the reference is internal — no desk edge, no external datum, nothing to be
parallel to. The cost is that both hands must be marked in the same sitting.

### Reading the sheets back

**You do not need a ruler.** The sheets carry their own scale — a 5 mm grid, heavier every
10 and labelled every 20, plus a 100 mm calibration box. A photograph that includes the
grid is self-calibrating, and reading against the printed grid beats laying a ruler on top
of it.

What matters in the photo:

- **Shoot straight down**, camera parallel to the paper. Perspective is the only real error
  source here, and it is not recoverable by eye.
- **Get all four corners of the grid in frame**, plus the 100 mm box. Corners let the
  perspective be corrected if it is slightly off; the box confirms the print scaled right.
- Flat, evenly lit, no shadow across the marks. Phone flat-on beats phone at an angle.

Send the photo and I will read the marks off the grid and turn them into geometry.

---

## 5. Method note

`mesa1/LAYOUT.md` already makes the point and it holds here: you acclimatise within days,
so paper tells you reliably what is *wrong* and much less reliably which of two reasonable
options is *better*. Repeat a sheet across sessions and trust what repeats.

---

## Open questions

- How much less spread — V1, V2, or between?
- Where is your thumb's pivot, and what line angle and reach fall out of it?
- Does 17 mm bridge comfortably for a two-key chord on every finger, pinky included? If not,
  the only lever is a physically smaller cap, since 17 mm is already the cap floor.
- Unibody angle and hand separation — deferred until the hand geometry lands.
