# hand-scan-1 — what the marks say

Read from `hand-scan-1.pdf`. Extraction and numbers: `scan-read.py`.
Overlay of what was read: `hand-scan-1-read.png`.

## The sheet printed correctly

Calibrating on the printed 20 mm grid lines gives 7.8636 px/mm across and 7.8786 px/mm
down — **199.7 dpi**, isotropic to 0.2%. The red origin cross lands at **(−0.03, +0.01) mm**.
So the print scaled true and every number below is trustworthy to a few tenths.

All 30 marks were located automatically by stroke-crossing density, not by eye.

## What is clean

**Ring and middle columns are straight and mirror well.** Bow (max deviation from the fitted
line) is 0.12–0.34 mm, which is as good as pen marks get.

| | left | right |
|---|---|---|
| ring | −1.1° | +3.8° |
| middle | −1.2° | **+25.2°** |

Angles are degrees from straight-away-from-you, positive = far end leans toward +X.

**Index columns mirror well too** — left −38.7°, right +35.3°.

**Thumb chords agree**: 35.79 mm left, 35.08 mm right, over three marks each.

## Three things I cannot resolve without you

### 1. The pinky is an elbow, not a line

Both hands, same shape, so it is systematic rather than a slip:

| | m1 → m2 | m2 → m3 | bow |
|---|---|---|---|
| left pinky | 14.48 mm | 4.81 mm | 1.01 mm |
| right pinky | 14.31 mm | 5.84 mm | 0.89 mm |

Every other finger runs 7–9 mm then 10–12 mm in a straight line. The pinky puts one mark far
out at a shallow angle and then two marks 5 mm apart. A line fit through all three is
meaningless (+66.6° / −52.2°), and m2→m3 alone is far too short to carry a 17 mm pitch.

**What are those three marks?** If m1 is the extended position and the pinky abducts strongly
as it straightens, that is real and interesting but means the pinky travels on an arc, not a
line — which changes how its two keys should be placed.

### 2. The right middle column does not mirror the left

Left middle is −1.2°, right middle is **+25.2°**. Every other pair mirrors to within a few
degrees. One of the two is not what you meant. The right middle cluster is also the one
carrying two labels, "middle" with something like "rng" written under it.

### 3. The thumb arcs disagree

Chord lengths match, but a circle through three points is very sensitive to small errors:

| | fitted pivot | radius |
|---|---|---|
| left thumb | (42.78, 153.27) | 79.57 mm |
| right thumb | (162.76, 121.03) | 40.26 mm |

A factor of two apart, with bows of 1.33 and 2.45 mm. **Three points is not enough** — the
sheet asks for 4–5 and it matters here more than anywhere else. This one is a re-measure
rather than a question.

## What the numbers say if the middle mark is the rest position

Taking m2 as the rest position throughout:

| | pinky | ring | middle | index |
|---|---|---|---|---|
| left | (29.27, 35.07) | (55.68, 29.34) | (73.63, 28.25) | (92.72, 50.59) |
| right | (202.06, 29.35) | (173.37, 24.63) | (150.60, 26.34) | (140.21, 50.14) |

| junction | left | right | chouchou |
|---|---|---|---|
| pinky ↔ ring   | 26.41 | 28.69 | 21.60 |
| ring ↔ middle  | 17.95 | 22.77 | 21.23 |
| middle ↔ index | 19.09 | 22.77* | 23.74 |

*right middle→index dx is 10.39; the 22.77 above is ring↔middle. See `scan-read.py` output.

Two observations worth carrying forward even before the questions are settled:

- **The index stagger is enormous.** middle→index dy is +22.34 mm left and +23.80 mm right,
  against chouchou's +8.00 and mesa1's +10. Both hands agree, so it is not noise. This is the
  "index closer to my hand" correction, and it is much bigger than the +12 to +15 I guessed
  in V1/V2.
- **The index splay is enormous too**, ~37°, against chouchou's 5°. But ring and middle both
  sit near 0°, so the fan is not smooth — it is flat across three fingers and then jumps at
  the index. A real hand fan usually progresses. This may be the gap between where a hand
  *floats* freehand and where it *lands* on keys, which is the known weakness of paper.

## Method notes for the next sheet

- The sheet used was the older two-dot version; you marked three anyway, which is what the
  current sheet asks for. No harm done.
- Thumbs need **4–5 marks**, not 3.
- The two hands disagree by more than I would like on spreads (ring↔middle 17.95 vs 22.77).
  Repeating the sheet in another session and keeping what repeats is the guard against this.
