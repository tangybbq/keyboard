# mesa2x — how to scan this matrix

The firmware spec for the pairwise-matrix experiment. Written for the Rust + Embassy
firmware; nothing here assumes QMK/ZMK conventions.

**Read the ghosting section before writing any code.** The topology cannot resolve
arbitrary chords, and that is a property of the wiring, not of the scan routine.

## What this board is

18 keys on **7 GPIOs**, one key per pin *pair*, versus the 9 GPIOs the conventional
5 × 4 grid uses on mesa2 Rev B. Same keys, same layout, same Dosh legends — only the
matrix wiring differs.

Each key is a switch in series with a diode between two pins. The switch side is the
**anode**, so a key conducts only from its higher-numbered pin to its lower-numbered
one. Every key follows that convention; there are no exceptions on the board.

## Pin map

| net | RP2040 pin |
|---|---|
| `SCAN_1` | GP0 |
| `SCAN_2` | GP1 |
| `SCAN_3` | GP2 |
| `SCAN_4` | GP3 |
| `SCAN_5` | GP4 |
| `SCAN_6` | GP27 (A1) |
| `SCAN_7` | GP28 (A2) |

`RGB` is on GP26 (A0), unchanged. **GP5, GP6, GP7 and GP29 are free** — the four pins
the pairwise wiring buys back.

## Key table

Each key conducts **anode → cathode**. 18 of the 21 available pairs are used; `5-4`,
`6-1` and `7-1` are empty.

| key | anode | cathode | | key | anode | cathode |
|---|---|---|---|---|---|---|
| `RSP1` | 2 | 1 | | `RA1` | 5 | 3 |
| `RBK1` | 3 | 1 | | `LBK1` | 6 | 2 |
| `RE1` | 3 | 2 | | `LSP1` | 6 | 3 |
| `RI1` | 4 | 1 | | `LE1` | 6 | 4 |
| `RT1` | 4 | 2 | | `LI1` | 6 | 5 |
| `RN1` | 4 | 3 | | `LT1` | 7 | 2 |
| `RO1` | 5 | 1 | | `LN1` | 7 | 3 |
| `RS1` | 5 | 2 | | `LO1` | 7 | 4 |
| | | | | `LS1` | 7 | 5 |
| | | | | `LA1` | 7 | 6 |

## The scan

Idle state: **all seven pins are inputs with pull-ups enabled.**

One scan step strobes a cathode pin and reads the anodes:

1. Set pin `b` to **output, driven low**.
2. Wait for settle.
3. Read every pin that is an anode of some key whose cathode is `b` (the table below).
   A pin reading **low** means that key is down.
4. Return pin `b` to input-with-pull-up.

Six steps cover all 18 keys. Strobing `SCAN_7` is pointless — nothing has it as a
cathode.

| strobe | read these pins | keys detected |
|---|---|---|
| `SCAN_1` | 2, 3, 4, 5 | `RSP1` `RBK1` `RI1` `RO1` |
| `SCAN_2` | 3, 4, 5, 6, 7 | `RE1` `RT1` `RS1` `LBK1` `LT1` |
| `SCAN_3` | 4, 5, 6, 7 | `RN1` `RA1` `LSP1` `LN1` |
| `SCAN_4` | 6, 7 | `LE1` `LO1` |
| `SCAN_5` | 6, 7 | `LI1` `LS1` |
| `SCAN_6` | 7 | `LA1` |

**Rules that are not optional:**

- Only ever drive **one** pin at a time, and only ever drive it **low**. Driving a pin
  high while another is driven low puts a forward-biased diode directly across two
  push-pull drivers — a short limited only by the pin drivers, since this board has no
  series resistors anywhere.
- Never enable pull-downs. A pulled-down pin drags its neighbours through their diodes
  and manufactures presses that are not there.

**Settle time** is set by the pull-up charging the pin and track capacitance. The
internal pull-up is 50-80 kΩ, so with a few tens of pF the RC is well under a
microsecond; 5 µs per step is comfortable and puts a whole scan near 30 µs. Measure it
rather than trusting the arithmetic.

**Debounce** per key, not per pin: the usual 5 ms settle on change is fine, and there is
nothing about this topology that needs more.

## Ghosting — the part that matters

**Two pressed keys can forge a third.** If key `a→c` and key `c→b` are both down, then
while strobing `b` the current path runs `a → c → b` through two diodes, dragging pin
`a` low. That is indistinguishable in kind from key `a→b` being pressed.

There are **21 two-key chords that forge a third real key**:

| chord | forges | | chord | forges |
|---|---|---|---|---|
| `LA1`+`LBK1` | `LT1` | | `RA1`+`RBK1` | `RO1` |
| `LA1`+`LSP1` | `LN1` | | `RA1`+`RE1` | `RS1` |
| `LA1`+`LE1` | `LO1` | | `RN1`+`RBK1` | `RI1` |
| `LA1`+`LI1` | `LS1` | | `RN1`+`RE1` | `RT1` |
| `LE1`+`RT1` | `LBK1` | | `RT1`+`RSP1` | `RI1` |
| `LE1`+`RN1` | `LSP1` | | `RS1`+`RSP1` | `RO1` |
| `LI1`+`RS1` | `LBK1` | | `RE1`+`RSP1` | `RBK1` |
| `LI1`+`RA1` | `LSP1` | | `LN1`+`RE1` | `LT1` |
| `LO1`+`RN1` | `LN1` | | `LO1`+`RT1` | `LT1` |
| `LS1`+`RA1` | `LN1` | | `LS1`+`RS1` | `LT1` |
| `LSP1`+`RE1` | `LBK1` | | | |

A further 8 chords land on the three unused pairs (`6-1`, `7-1`). Those are **useful**:
activity on a pair with no key behind it can only mean a sneak path is conducting, so
the firmware can treat it as a hard signal that the reading is compromised.

| chord | lands on |
|---|---|
| `LBK1`+`RSP1`, `LE1`+`RI1`, `LI1`+`RO1`, `LSP1`+`RBK1` | `6-1` |
| `LN1`+`RBK1`, `LO1`+`RI1`, `LS1`+`RO1`, `LT1`+`RSP1` | `7-1` |

### Why firmware cannot fix it

The forged key is electrically identical to a real one. When the scan reports
`LA1`, `LBK1` and `LT1` all down, there is no measurement that distinguishes "three keys
pressed" from "two keys pressed plus a ghost" — both produce exactly the same readings on
every step. No scan order, no timing trick and no history helps, because both states are
reachable and stable.

### The one physical difference, and why it is not enough to rely on

The ghost path crosses **two** diodes where a real press crosses one, so the forged pin
sits about twice as far above the strobe: roughly 0.5 V for a real press against 1.0-1.4 V
for a ghost, at the ~60 µA the internal pull-ups supply.

It is tempting to lean on that — set the threshold between them and ghosts vanish. Do
not. The RP2040's input thresholds are **characterisation data, not guaranteed**; the
datasheet guarantees only V_IL ≤ 0.8 V and V_IH ≥ 2.0 V, and a ghost at 1.0-1.4 V sits
squarely in the indeterminate band. It is neither guaranteed to read low nor high, and
where it lands varies with part, temperature and diode lot. Designing on it produces
false keys that appear on one board and not another.

### What would actually fix it, in hardware

Add a series resistor (about 1 kΩ) on each of the seven scan pins. Then the scan can
drive every non-read pin **high** instead of leaving it floating, which removes the
intermediate node the sneak path needs, and the resulting diode short becomes
(3.3 − 0.7)/2 kΩ ≈ 1.3 mA instead of tens of milliamps. Seven resistors, and the
topology becomes sound.

### Why no rewiring helps

This is a property of the graph, not the assignment. 18 keys on 7 pins means 18 edges on
7 vertices, and by Mantel's theorem a triangle-free graph on 7 vertices holds at most
⌊49/4⌋ = **12** edges. Triangles are therefore unavoidable, and every triangle is a
ghost. Reshuffling which pairs are used moves the ghosts around — the best possible
choice of three unused pairs yields 20 instead of the current 21 — but cannot remove
them.

Going wider does not help until **9 pins**, where ⌊81/4⌋ = 20 ≥ 18 edges fit
triangle-free — and the graph that achieves it is complete bipartite, 4 × 5. That is the
conventional row/column matrix mesa2 Rev B already uses, which is exactly why the
standard diode matrix has no ghosts at any chord size: every two-step path leaves and
returns to the same side, where no key exists.

So the pin saving and the ghosting are the same fact seen from two directions.

## What to implement now

The board is worth building and typing on, but scope the firmware honestly:

- **Single keys and any chord not in the tables above: correct.** Most of Dosh's chord
  set is unaffected.
- **The 21 listed chords: wrong**, in a way no amount of firmware care will fix.
- Implement the unused-pair check. It is nearly free and it turns an invisible failure
  into a loud one during bring-up.
- If the board is to become more than an experiment, fit the seven series resistors and
  switch the scan to driving non-read pins high. That version is sound, and the spec
  above changes only in step 1.
