# The mesa3w wireless

A BLE, battery-powered spin-off of the mesa3.

**Scope, settled 2026-09-13: mesa3w is a rework of the left board only.** The right half
stays exactly as mesa3 already has it — nine keys, nine diodes, RJ-45, nothing else — and
the wired RJ-45 interconnect between the halves stays. Only the left board changes: the
Tiny2040 comes out, and an nRF52840 module, a PMIC and a cell pack go in.

This is a late reversal. The plan was two independently wireless halves in the ZMK style,
and most of the analysis below was done under that assumption. What broke it was wanting
the keyboard to **run from USB**, so that one keyboard serves a wired desk and untethered
travel. USB reaches one half; anything powering the other half is a conductor between
them, which is a cable. And once a cable is granted, a *passive* right half is strictly
better than a smart one:

- The cable carries **no power** — a passive half needs none — so the existing 7-conductor
  RJ-45 pinout carries over untouched. No TRRS, no power distribution, no battery
  paralleling, no hot-plug hazard.
- **mesa3-right needs no redesign at all.** It is already routed and reviewed.
- One module, one PMIC, one cell pack, one USB port, one board to flash.
- The cross-half wake problem, the two-transport firmware and the split pairing work all
  disappear. BLE talks only to the host.
- **The mesa3 "firmware must not be able to tell a Rev B from a Mesa 3" constraint is
  restored.** A wireless split would have broken the single 5 × 4 grid into two local
  5 × 2 matrices and forced a board-specific keymap. Keeping the right half passive keeps
  the one grid, so one keymap still serves the unibody and the split alike.

A wireless mesa2 — unibody, no cable at all — was considered and rejected as too bulky for
travel.

Original notes, kept because they still frame the requirements:

- The firmware will be based off of a zephyr port of the jolt firmware. BLE support will
  come from Zephyr, possibly learning from ZMK.
- An nRF module supporting BLE and USB device (1.1 is fine for a keyboard).
- Nordic's recent PMIC for primary cells; one or two AA NiMH fit my usage better.
- PCB will contain PMIC, LEDs, SWD Tag-Connect, the USB-C connector, and the module
  soldered directly down.
- Assembly by JLC. Key sockets can go either way depending on part availability and
  assembly cost. Hand assembly isn't difficult, just tedious.

## Parts survey — what JLC actually stocks

Checked against JLCPCB's SMT parts library on 2026-09-09. Stock numbers move, but the
*shape* of the answer is unlikely to change soon.

### The headline: nRF52840, not nRF53

The nRF52840 has a **USB 2.0 full-speed device** peripheral, the same as the nRF5340. So
the "BLE plus USB device" requirement does not force the 53 — the 52840 satisfies it, is
$2–3 cheaper, and is the part every open wireless keyboard firmware (ZMK, nrfmicro,
nice!nano) already runs on. That matters for the Zephyr port: `nrf52840` boards are the
best-trodden path in-tree.

That is fortunate, because **JLC stocks no nRF5340 module at all.**

| Part | LCSC | Package | Stock | Price |
|---|---|---|---|---|
| Raytac MDBT53-1M / -P1M / -U1M | C5355663 / C5796572 / C5768063 | LGA-65 / SMD-65P | **0** | $9–15 |
| Minew MS45SF1-nRF5340 | C9900245340 | SMD 12.5×18.5 | **0** | — |
| Holyiot 21069-nRF5340 | C9900280684 | SMD | **0** | — |
| Bare NRF5340-QKAA-R | C3015611 | AQFN-94 7×7 | 9440 | $5.24 |

Every nRF5340 *module* is a catalogue entry with zero stock — JLC would have to buy them
through global sourcing (MOQ, prepay, weeks of lead time, and no guarantee). Only the
bare die is stocked, and a bare die means designing the 2.4 GHz front end, matching
network and antenna, which is exactly what the plan says to avoid.

Same story for the nRF52840 modules that get recommended in keyboard circles: Minew
MS88SF3 (C5291489), all the JLC-Assembly-branded module entries — zero stock.

### nRF52840 modules that are actually in stock

| Part | LCSC | Size | Stock | Price |
|---|---|---|---|---|
| **Ebyte E73-2G4M08S1C** | **C356849** | 13×18 mm, ceramic ant. | **2008** | $7.06 |
| Ebyte E73-2G4M08S1CX | C2764963 | 13×18 mm, IPEX (ext. ant.) | 1542 | $6.18 |
| RF-star RF-BM-ND04 | C5441197 | 24.8×15 mm | 179 | $4.07 |
| RF-star RF-BM-ND05I | C5441194 | 24.8×15 mm | 43 | $5.86 |
| Seeed XIAO nRF52840 | C17209540 | 21×17.8 mm board | 162 | $10.44 |

**Recommendation: E73-2G4M08S1C** (`C356849`). It is the only one with comfortable
stock, it is the module nrfmicro and a pile of ZMK boards already use, and — checked
against Ebyte's user manual — it brings out everything this design needs:

- 43 castellated pads on 1.27 mm pitch, 13.0 × 18.0 mm, 4-layer, built-in ceramic
  antenna, nRF52840-QIAAC0 (aQFN-73), 1 MB flash / 256 KB RAM.
- **`VBUS` (27), `D-` (29), `D+` (31)** — the USB device port is fully exposed, so the
  USB-C receptacle wires straight to the module.
- **`VDD` (19), `VDDH` (23), `DCH`/DCCH (25)** — both the normal and high-voltage supply
  pins are out, which is what makes a USB-versus-battery power path possible at all.
- `SWD` (37), `SWC` (39), `RST` (26) — straight to the Tag-Connect.
- `XL1` (11) / `XL2` (13) for the 32.768 kHz crystal.
- 32 GPIO, of which **15 are unrestricted** — see the pin budget below.

Two things to know about it:

- The **`C` suffix is the ceramic-antenna part; `CX` is the IPEX connector** version
  needing an external antenna. Despite being $0.90 cheaper, `CX` is the wrong one here.
- **The 32.768 kHz crystal is *not* on the module.** `XL1`/`XL2` are brought out so you
  can add one. Without it the LFCLK falls back to the internal RC, which costs roughly
  **8–10 µA of extra average current** — small in absolute terms, but on a design whose
  whole point is running months off an AA, it is worth the two pads. A bare cylindrical
  32.768 kHz can be soldered across XL1/XL2 with no load caps.

The **XIAO nRF52840** deserves a mention as the "Tiny2040 of the BLE world": castellated,
in stock, and it already carries a USB-C jack and a BQ25101 Li-ion charger. That last
part is the problem — it hardwires the board to a LiPo, which is the opposite of the
AA-cell plan. Listed here in case the battery decision goes the other way.

### GPIO budget — the "low frequency I/O" restriction

The nRF52840 marks 21 of its 48 GPIOs "Standard drive, low frequency I/O only". Worth
being precise about what that means, because it is less restrictive than it sounds:

- The product spec's own footnote defines it as **"signals with a frequency up to
  10 kHz"** — not the kilohertz-or-less it is often taken for.
- Nordic's answer on DevZone is that it is **not an electrical limit at all**: "They are
  not restricted to 10 kHz, just recommended to not be set higher due to interference
  issues with the radio." These pins sit on the die edges nearest the RF output; the
  concern is desense and RF certification, not the pin's switching ability. Someone in
  that thread ran 8 MHz SPI on them without trouble.
- A key scan is nowhere near the line either way. Even an aggressive 1 kHz full-matrix
  scan toggles each column at about 1 kHz — an order of magnitude under the guideline.

So the matrix would be fine on the restricted pins. But it does not have to be, because
the E73 brings out plenty of unrestricted ones. Classifying all 32 of the module's GPIO
pads against the aQFN-73 pin table:

| | E73 pads |
|---|---|
| **Unrestricted** (18) | `P0.00`/XL1, `P0.01`/XL2, `P0.04`, `P0.05`, `P0.06`, `P0.07`, `P0.08`, `P0.12`, `P0.13`, `P0.15`, `P0.17`, `P0.18`/RESET, `P0.20`, `P0.22`, `P0.24`, `P0.26`, `P1.00`, `P1.09` |
| Low-frequency only (14) | `P0.02`, `P0.03`, `P0.09`/NFC1, `P0.10`/NFC2, `P0.28`, `P0.29`, `P0.30`, `P0.31`, `P1.02`, `P1.04`, `P1.06`, `P1.10`, `P1.11`, `P1.13` |

Three of the unrestricted eighteen are spoken for — `XL1`/`XL2` for the 32.768 kHz
crystal and `P0.18` for RESET — which leaves **15 free unrestricted GPIOs**. (`P0.22` and
`P1.00` are nominally QSPI pins, but there is no external QSPI flash on this board, so
they are ordinary I/O here.)

The left board now drives the **whole** 5 × 4 grid, both halves, over the RJ-45 — so the
matrix costs **5 columns + 4 rows = 9 pins**, not the 7 a local half would need. Add
`SWO` on Tag-Connect pin 6 and that is **10 of the 15 unrestricted pads**, leaving 5
spare. The four or five LEDs sit on the low-frequency pads and cost nothing from this
budget. GPIO is not a constraint, though it is tighter than the two-half plan would have
been.

### The PMIC — nPM2100 is real and stocked

| Part | LCSC | Package | Stock | Price |
|---|---|---|---|---|
| **NPM2100-QEAA-R7** | **C46968654** | QFN-16, 4.0×4.0 mm | 1555 | $0.92 |
| NPM2100-CAAA-R7 | C46968655 | WLCSP-16, 1.9×1.9 mm | 1179 | $0.94 |
| NPM1300-CAAA-R7 | C25346894 | WLCSP-35, 2.4×3.1 mm | 1490 | $1.57 |

**Take the QFN** (`C46968654`). The WLCSP is 0.4 mm pitch — which pushes the board into
JLC's finer-spec tier — and Nordic's datasheet carries an explicit warning that the WLCSP
is sensitive to visible and near-IR light and must be shielded from it in the final
product. Neither is worth it to save 14 mm² on a keyboard.

From the datasheet (v0.7 preliminary / v1.0):

- Boost: **0.7–3.4 V in, 1.8–3.3 V out, 150 mA max**, with automatic pass-through when
  the cell is above the target.
- **`VSET` open = 3.0 V out, `VSET` grounded = 1.8 V out.** Set at power-on-reset by a
  pin, so the 3.0 V rail comes up with no firmware and no I²C traffic at all.
- Separate LDO/load switch, 0.8–3.0 V at up to 50 mA — a natural software-controlled
  supply for the RGB LEDs.
- 150 nA quiescent, 35 nA ship mode (so the board can ship with cells installed), plus
  battery-voltage/temperature measurement feeding Nordic's fuel gauge.
- Externals are trivial: one **2.2 µH inductor (DCR < 150 mΩ, I_sat > 0.55 A)** and five
  ceramics. JLC has dozens of suitable inductors at ~$0.02 (e.g. C2826618, C354563).
- Nordic's own example battery is "two alkaline AA/AAA in series or one CR2032". **Two
  AA NiMH in series is 2.4 V nominal, 1.8–2.9 V over their discharge — dead centre of the
  input range.** A single NiMH cell at 1.2 V also works and is what the part is tuned
  for, it just carries half the energy.

**The catch: the nPM2100 has no charger and no VBUS input.** It is a boost for cells you
replace, not cells you recharge in place. If charging over USB is a requirement, the part
is the **nPM1300** (`C25346894`, in stock) with a Li-ion cell — but that abandons the AA
NiMH idea, since neither Nordic PMIC can charge NiMH.

### The LEDs — plain 3535 LEDs, not SK6812

Two independent reasons the SK6812s go, and it is worth separating them because only one
is about the protocol:

1. **The protocol.** SK6812/WS2812 one-wire is timing-critical bit-banging with no
   peripheral support on Nordic silicon.
2. **The quiescent draw.** An integrated controller is a live IC on every LED, roughly
   1 mA each doing nothing. Four of them is ~4 mA of pure idle drain — enough to flatten
   two AA NiMH in about three weeks with the keyboard never once typed on, against the
   ~30 µA floor worked out further down.

**No integrated I²C-addressable LED exists in a 3535 package.** Every smart LED in that
size (SK6812MINI, WS2812B-MINI, WS2813B-MINI, TZ-3535S2RGB) is one-wire. The **APA102 /
SK9822** family solves reason 1 properly — plain 2-wire SPI, no timing sensitivity, an
in-tree Zephyr driver — and it does exist in 3535 (`SK9822MINI-HB`, `C42457611`), JLC
simply stocks none of them, nor any APA102 including the 2020. Hand assembly would keep
them on the table, and four LEDs is a trivial hand-solder. But reason 2 disqualifies them
regardless of stock: they are still a controller per LED.

**So: plain, dumb 3535 RGB LEDs**, driven from the nRF's own PWM — see *LEDs: at four or
five* further down for that decision and its numbers.

| LED | LCSC | Package | Stock | Price |
|---|---|---|---|---|
| **NationStar RS-3535MWAR** | **C110402** | SMD3535-6P | 518829 | $0.051 |
| NationStar NH-Z3535RGBA-SG | C2874123 | SMD3535-6P | 38208 | $0.013 |
| TCWIN TC3535RGBE07-3CJH-E01 | C784546 | SMD3535-6P | 10958 | $0.031 |

Six-pin parts: three dies with both terminals brought out, so they will wire to anything —
GPIO with series resistors, or a current-sink driver with the anodes commoned. `C110402`
has half a million in stock.

Two notes carried forward:

- **Confirm forward voltages against the 3.0 V rail at schematic time.** Red is
  comfortable; blue and green sit around 3.0–3.2 V and will be marginal. This may end up
  being the real argument for setting the boost to 3.3 V rather than leaving `VSET` open
  for 3.0 V.
- **No MOSFET rail cut is needed.** A GPIO configured as an input is already an open
  circuit, so "off" costs nothing. That was only ever required to tame the SK6812s'
  quiescent draw, which no longer exists.

**Fallback if the LED count grows:** a TI LP50xx constant-current sink driver over I²C —
**LP5009** (9 channels, `C701960`, WQFN-20-EP 3×3, 2455 in stock, $0.43) or **LP5012**
(12 channels, `C1849481`, 1340 in stock, $0.64). Twelve channels is exactly four RGB LEDs
with nothing wasted, per-channel current is set in registers so the ceiling is enforced in
hardware, and shutdown is 0.2 µA. It buys back GPIO and lets the LEDs run while the MCU
sleeps, at the cost of an IC and an I²C bus. The crossover is around six channels.

### Consequences for the rest of the board

- **The 150 mA boost ceiling has stopped being a problem.** Four or five indicator LEDs
  at a milliamp or so apiece is single-digit mA, and the series resistors fix the ceiling
  in hardware. The nRF52840 itself peaks around 17 mA transmitting at +8 dBm. Total peak
  draw now sits an order of magnitude under the boost's limit.
- The module's 13 × 18 mm ceramic-antenna footprint wants keep-out: no copper pour, no
  ground plane and no battery under the antenna end.
- USB-C, Tag-Connect and the reset pad carry over from mesa3 unchanged.

### Rough BOM delta

One board's worth — the right half gains nothing.

| | LCSC | ~$ |
|---|---|---|
| E73-2G4M08S1C | C356849 | 7.06 |
| NPM2100-QEAA-R7 | C46968654 | 0.92 |
| 2.2 µH inductor + 5 ceramics | — | ~0.10 |
| 32.768 kHz crystal | — | ~0.10 |
| 4–5 × 3535 LED + series resistors | C110402 etc. | ~0.25 |
| Ship/power button (SHPHLD) | — | ~0.05 |
| 2 × profiler break point | — | ~0 |
| USB LDO + P-FET switchover | — | ~0.20 |
| | | **~$8.65** |

All of these are extended parts, not basic — so budget JLC's per-unique-extended-part
loading fee on top.

## Sleep, wake, and where the current actually goes

### Wake-on-keypress: drive all columns, sense the rows

The standard trick, and the right one here. Before idling, drive **every column at once**
and configure **every row as an input with its internal pull resistor and `SENSE`
enabled** for the opposite level. Any key closing anywhere in the matrix drags its row to
the driven level, `DETECT` fires, and the part wakes. No scanning, no timer, one event
for the whole matrix. Scanning resumes only once awake.

**Which polarity depends on the diodes, and mesa3's are already committed.** Pulled from
`mesa3-right/production/netlist.ipc`, which is unambiguous:

```
327/ROW_D            SW_RT1-1     switch pin 1  -> ROW_D
327NET-(D_RT1-A)     SW_RT1-2     switch pin 2  -> diode ANODE
327NET-(D_RT1-A)     D_RT1-2      diode pin 2 = A (anode)
327/COL_3            D_RT1-1      diode pin 1 = K (cathode) -> COL_3
```

The path is **row → switch → anode → cathode → column**, so the diodes conduct from row
to column. Current can only flow when the row sits above the column, which means
**columns driven LOW, rows pulled UP, sensing for LOW** — active-low, not active-high.
Driving the columns high with this orientation reverse-biases every diode and detects
nothing, which is the failure mode to avoid.

That is a statement about mesa3 as built, not a law. mesa3w is a new board and the diodes
can be flipped — anode to the column, cathode to the switch — which gives active-high
sensing with pull-downs on the rows. The nRF52840 supports both (`PIN_CNF.SENSE` = 2 for
high, 3 for low) and its pull-up and pull-down are both 11–16 kΩ, so there is no
electrical reason to prefer one. The only requirement is that the diode orientation and
the sense polarity agree. Reusing mesa3's footprints and orientation means active-low;
choosing active-high means deliberately reversing every diode and saying so on the
schematic.

**The one number that matters:** use the GPIO **`PORT` event** (the `SENSE`/`DETECT`
latch), not per-pin `GPIOTE IN` events. From the nRF52840 PS's own measured idle
currents at 3 V:

| Mode | Current |
|---|---|
| System ON, full RAM retention, wake on **GPIOTE `PORT`** | **2.36 µA** |
| System ON, full RAM retention, wake on GPIOTE `IN` | 17.37 µA |
| System ON, full RAM retention, wake on RTC | 3.16 µA |
| System ON, full RAM retention, wake on any event | 2.35 µA |
| System OFF, full RAM retention, wake on reset | 1.86 µA |
| System OFF, no RAM retention, wake on reset | 0.40 µA |

Identical functionality, 7× the current, purely from picking the wrong wake source.
`GPIOTE IN` needs the high-frequency clock running to catch edges; `PORT` is a
level-latch in the always-on domain, which is also why it works from System OFF.

Two things to check against the schematic:

- **A key held down during idle is a real drain.** The internal pull-up is 11–16 kΩ
  (13 kΩ typ), so one closed switch against a driven column sinks about **180 µA at
  3.0 V** once the diode drop is taken off — nearly a hundred times the idle current,
  indefinitely. Something resting on the
  keyboard in a bag will flatten it. Worth a firmware guard: if `DETECT` re-fires
  immediately and the same key is still down after a scan, mask that column out. The
  power button below is the better answer for anything longer than a desk-drawer.

### The power button is already in the PMIC

The Apple-keyboard arrangement — a real off switch alongside the firmware's sleep — comes
free with the nPM2100. Its **`SHPHLD` pin is a multifunction single-button input**:

- Hold ~2 s and release → **Ship mode, 35 nA**, boost off, rail dead. A genuine off.
- Press again → wake, cold start, rail comes back up.
- Hold for `tRST_DEB_L` (default 10 s) → hard reset, for when firmware has wedged.

One button, one net, no firmware involvement, and it works even if the MCU is hung. It
also disposes of the held-key drain: a keyboard going into a bag gets switched off rather
than left to sink ~180 µA through a pull-up.

**Layout caveat:** `SHPHLD` is an analog pin with an absolute maximum of 1.9 V, well under
the 3.0 V rail. The button goes from `SHPHLD` to ground, using the pin's internal pull-up
(both pull-up and pull-down are register-controlled). Do not tie it to the rail.

### Cross-half wake: moot, and worth recording why

**The passive right half removes this problem rather than solving it.** There is one
matrix, driven entirely from the left board over the RJ-45, so a single `PORT` event
covers all eighteen keys. A key on the right pulls a row low through the cable exactly as
a key on the left does. There is no second MCU to wake and no radio involved.

Kept because it was the strongest argument against the two-wireless-halves plan, and
because it still constrains System OFF:

> System OFF means the radio is off, so a keypress on one half cannot reach a
> deep-sleeping other half over BLE. That is physics, not a firmware gap. ZMK's tracker
> position is "key presses on a peripheral keeps the central awake but not the reverse",
> alongside open bugs about the central failing to wake at all — the source of the "press
> a key on each side" behaviour split wireless keyboards are known for.

**System OFF still is not worth it, for the remaining reason.** System ON with full RAM
retention and `PORT` wake is 2.36 µA; System OFF with RAM retention is 1.86 µA. Half a
microamp, against the cost of a sleep state machine, a lost first keypress and a
multi-second BLE reconnect. On a 110 mAh LiPo that trade makes sense, which is why ZMK
takes it; on two AA it is noise.

So the board stays in System ON, idling at ~2.4 µA between keypresses with the BLE link to
the host held up, and duty-cycles the radio with connection parameters rather than power
modes.

### The current budget

The radio, not the CPU, is the whole story — and there is now exactly **one** link, to the
host. Nordic's power profiler and measurements on DevZone put a 20 ms connection interval
with no peripheral latency at roughly **226–320 µA** average just to hold a link up.
Peripheral latency is the knob: skipping *n* of every *n+1* connection events divides that
cost by about *n+1*, so a 20 ms interval with latency 9 behaves like 200 ms when nothing is
being typed and drops into the tens of µA, while snapping back to 20 ms the moment a key
goes down.

Scanning the right half's nine keys over the cable adds essentially nothing: the columns
are driven only during a scan, and in idle they sit driven with no current flowing until a
switch closes. Cat5's ~50 pF/m of capacitance is irrelevant at keyboard scan rates.

Against two AA NiMH (2000 mAh at 2.4 V = 4.8 Wh, ≈1.44 Ah at the 3.0 V rail after the
boost's ~90%):

| Average rail current | Runtime, 2×AA | Runtime, 1×AA |
|---|---|---|
| 50 µA (idle, long effective interval) | ~26 months | ~13 months |
| 250 µA (link held tight, no latency) | ~7 months | ~3.5 months |
| 500 µA (busy typing) | ~4 months | ~2 months |

One cell pack now runs the entire keyboard, both halves — but it also only feeds one
radio link instead of two, so the figures above are the whole keyboard rather than one
half of it.

### The finding that reorders everything: use Eneloop-class cells

**Ordinary NiMH self-discharges at 0.5–1 % per day.** On a 2000 mAh cell that is
~14 mAh/day, equivalent to a continuous **~580 µA** draw — several times the entire
circuit, including the radio. A mesa3w on plain NiMH would go flat in weeks while sitting
untouched, and no amount of firmware power tuning would touch it.

**Low-self-discharge cells (Eneloop and equivalents) retain ~85 % over a year**, about
300 mAh, equivalent to **~34 µA**. That is a quarter of a 100 µA circuit — acceptable,
and it sets a hard floor: **there is no point engineering the board below roughly 30 µA
average**, because the cells leak faster than that regardless.

Two consequences worth stating plainly:

1. The cell chemistry is a *design constraint*, not a user preference. The build sheet
   should say low-self-discharge NiMH.
2. Combined with the System OFF result above, this closes the case: an always-connected
   design at a few hundred µA runs for months on AA, and the entire deep-sleep/cross-half
   wake problem never has to be solved.

### The idle state draws no static current — the pull-ups only conduct through a closed key

Worth working through, because the intuition that a pulled-high line and a driven-low line
must be burning current is the natural one, and here it is wrong.

In the idle configuration the columns are outputs driven low and the rows are
high-impedance inputs with a 13 kΩ pull-up to the rail. Between them sits an **open
switch**. The pull-up has nowhere to source current *to*: the row pin is an input, and the
only path onward is through a switch that is not closed. The circuit is broken. Static
current is zero.

Current appears the instant a key closes and not before — rail → 13 kΩ pull-up → switch →
diode → column at 0 V, about 180 µA. That is the wake event doing its job, and it is also
the held-key drain already noted.

So the **2.36 µA in the table is the whole idle figure**, with `DETECT` already armed;
there is nothing to add to it for the matrix. The only genuine leakage is 1N4148W reverse
current and GPIO input leakage, both single-digit nanoamps at 3 V — four orders of
magnitude under the MCU's own idle draw and not worth modelling.

**The consequence: a deeper sleep is not needed to eliminate matrix current, because there
is none to eliminate.** The reason to want a deeper state is storage, and that is what the
`SHPHLD` button is for.

### Three power states, and why there is no useful fourth

| State | Leave it by | Draw | |
|---|---|---|---|
| **Active** | — | 3.3 mA CPU + radio | typing; CoreMark @64 MHz from flash |
| **Idle** | any keypress, via `PORT` | 2.4 µA + radio duty cycle | link held up, wakes instantly, no reconnect |
| **Off** | the `SHPHLD` button | **35 nA**, rail dead | travel and storage |

System OFF would sit between Idle and Off, and it is worse than both. Against Idle it
saves about half a microamp and costs the BLE link, the reconnect delay and the
cross-half wake problem. Against Off it is fifty times worse — 1.86 µA with RAM retention
against Ship mode's 35 nA — and Ship mode is already on a button that works when firmware
is wedged. There is no gap left for it to fill.

One consequence of Ship mode to design for: **it discharges `VOUT`**, so the nRF loses
power completely and cold-boots on wake. BLE bonding keys therefore have to live in
flash — Zephyr `settings` over NVS — not in retained RAM. That is where they want to be
anyway, but it becomes mandatory rather than merely tidy.

### The periodic tick is the expensive part, not the timer

This is the real power question in the firmware, and the numbers are lopsided enough to
settle it. From the PS:

| | Current |
|---|---|
| One TIMER instance @ 1 MHz, HFINT | **418 µA** |
| One TIMER instance @ 1 MHz, HFXO | 646 µA |
| One TIMER instance @ 16 MHz, HFXO | 823 µA |
| System ON + RAM retention, wake on **RTC** | 3.16 µA |
| System ON + RAM retention, wake on any event | 2.35 µA |
| LFXO (32.768 kHz crystal) run current | 0.23 µA |
| LFRC (internal RC) run current | 0.7 µA |

A tick built on a high-frequency `TIMER` costs **400–800 µA** — the same order as the
entire BLE link, and two hundred times the idle floor. The same deadline expressed on the
**RTC** costs the difference between those two System ON rows: about **0.8 µA**. Roughly
a five-hundred-fold difference for the same functionality.

And the RTC is running regardless, because the BLE stack needs it for connection timing.
So arming an RTC compare for the decoder is, in practice, free.

**The fix is the one already identified: let the decoder declare its own next wake instead
of being ticked.** The shape that does this is a step function returning a deadline
alongside its output — something like:

```
enum Wake { Idle, At(Instant) }          // Idle = nothing pending

fn on_key(&mut self, ev: KeyEvent, now: Instant) -> (Reports, Wake)
fn on_deadline(&mut self, now: Instant)  -> (Reports, Wake)
```

`Wake::Idle` means no timer is armed at all and the system drops to the 2.4 µA GPIO-sense
wait. `Wake::At` arms one RTC compare for exactly that instant. Zephyr's tickless kernel
already works this way — `k_work_schedule` with a computed delay, and the PM policy
chooses the deepest state that still meets the next deadline — so this is expressing the
decoder in the idiom the kernel already wants, not fighting it.

The key observation about Taipo specifically: **deadlines only exist mid-chord.** A chord
timeout is only pending while keys are actually being assembled, which is to say while
the user is typing and the CPU is awake regardless. Between words, and certainly between
sessions, the decoder has nothing pending and returns `Idle`. Done this way the decoder
stops being a power consideration at all — it costs nothing in the state the keyboard
spends 99 % of its life in.

### Instrumenting the board: profiler header, PMIC, or both

**Both, because they measure different things and only one of them is a development
tool.**

The nPM2100 cannot do power profiling. Its ADC is **8-bit and measures battery voltage
and die temperature only** — no current sense, no coulomb counting. Nordic's fuel gauge
for it is an algorithm fitted to a cell's discharge curve, which is the right approach for
a primary cell but gives state-of-charge, not microamps. You cannot tune a 2.4 µA idle
state or a connection-interval policy from it, and you cannot see the difference between
`PORT` and `GPIOTE IN` wake sources with an 8-bit voltage reading. What it *is* good for
is the shipped keyboard reporting a battery percentage over the BLE HID battery service —
which is wanted anyway, and costs nothing extra since the PMIC is already there.

So add a profiler point as well. A **Power Profiler Kit II** covers 200 nA to 1 A at
100 ksps with 100 nA resolution — comfortably enough to resolve the idle floor — and it
works two ways, both of which want the same pads:

- **Ampere-meter mode**: cells stay in, PPK2 goes in series, DUT supply 0.8–5 V.
- **Source-meter mode**: cells come out, PPK2 supplies 0.8–5 V directly. This covers both
  1×AA (1.2 V) and 2×AA (2.4 V), so it can replace the pack entirely and give repeatable
  measurements without the cells' own state drifting under you.

| Break point | What it measures |
|---|---|
| Cell + → `VBAT` | True battery drain: MCU, radio, LEDs *and* the boost's own quiescent and efficiency loss. The number that predicts runtime. |
| `VOUT` → module `VDD` | The 3.0 V load alone, with the boost's efficiency curve taken out. The number to tune firmware against, and the bring-up power injection point. |

#### Jumper or solder bridge? Both — as a stuffing option

**There is no measurement-quality objection to a physical jumper here.** A 0.1" header and
shunt is maybe 20–50 mΩ of contact resistance; at the 15–20 mA peak of a radio burst that
is a 1 mV drop against a 3.0 V rail, and at 2.4 µA idle the contact noise works out around
tens of nanovolts against a PPK2 floor of 200 nA. Neither is detectable. The objections
are mechanical, and they are real:

- **It sits in the main power path.** Every microamp the keyboard ever draws goes through
  it. A shunt that works loose is an intermittent reset, which is a miserable fault to
  have designed in on purpose.
- **It is 8.5 mm tall with the shunt on.** On a board that lives between a switch plate
  and a baseplate, that fights the case.
- Shunts get lost.

So: **series 0805 pads as the normal state, with a 2-pin 0.1" footprint in parallel across
the same break, unpopulated.** Stuff one or the other, never both:

| Build | Fit | |
|---|---|---|
| Development | 2-pin header | PPK2's female flying leads plug straight on; shunt fitted for normal running |
| "Production" | 0Ω 0805 (or a closed solder bridge) | flat, solid, nothing to lose or work loose |

A 0805 and a header footprint in parallel is a few square millimetres and costs nothing to
carry. Put both on the **bottom side**, where the cell holder, the `SHPHLD` button and the
reset button already live.

One asymmetry worth planning around: the two break points get used differently. `VOUT` →
`VDD` is the one that will be opened repeatedly during bring-up, because it doubles as the
way to feed the module from the ORBTrace's VTRef or the PPK2 in source mode with the PMIC
out of circuit. That one wants the header populated on the first boards. Cell + → `VBAT`
is measured in bursts during power tuning and then never again, so it can go straight to
0Ω once the numbers are known.

Two details that are easy to omit and annoying to retrofit:

- **A GND pad beside each break.** Ampere-meter mode needs the meter's ground tied to the
  board's, and clipping onto a random ground via is how measurements get noisy.
- **Keep the bulk capacitance on the board side of each break.** The nPM2100's input and
  output caps already do this, so the point is simply not to skimp on them: a radio burst
  should be supplied by a local capacitor, not drawn through a meter. The PPK2 switches
  between five current ranges on the fly and the transitions are visible on fast load
  steps; local bulk keeps that artefact off the rail rather than merely off the graph.

### LEDs: at four or five, drive them from the nRF directly

The case for an I²C driver is a routing case: three traces instead of one per channel.
That argument is decisive at twelve channels and **worthless at four or five**, which is
the count actually planned here.

The nRF52840 has **four PWM instances of four channels each, 16 in total**, each channel
with its own duty cycle. Four or five LEDs uses two instances and leaves eleven channels
spare. Drive strength is ample: standard drive sources ~2 mA typ at VDD−0.4 V, high drive
~9 mA, against the fraction of a milliamp a dim indicator wants. And LED PWM runs at a few
hundred Hz to a few kHz, well under the 10 kHz guideline — so **the LEDs belong on the 14
restricted pads**, leaving every unrestricted pad for the matrix.

| | Direct nRF PWM | LP5009 / LP5012 |
|---|---|---|
| GPIO used | 4–5 (restricted pads) | 3 (SDA, SCL, `EN`) |
| Extra parts | 4–5 resistors | 1 IC + the same resistorless LEDs |
| Off-state current | 0 (pin as input) | 0.2 µA |
| Lit while MCU sleeps | no — HFCLK must run | yes, autonomous |

**Recommendation: direct PWM.** For "brief flash on wake, blink while pairing" the CPU is
awake anyway, so the driver's autonomy buys nothing, and four resistors is less board
than a QFN plus an I²C bus. The nPM2100's 50 mA LDO/load switch can feed the LED rail if
a hard cutoff is ever wanted, though pins configured as inputs already draw nothing.

**The threshold, if the LED count moves:** count *channels*, not packages — an RGB is
three. Under about six channels, direct PWM. Above that, the LP5009 (9 channels,
`C701960`, $0.43) or LP5012 (12, `C1849481`, $0.64) starts earning its place again, and
past twelve it is clearly right. All three options drive the same dumb LEDs, so this
stays a late decision as long as the footprints sit where either could reach them.

## Flashing and debug

### SWD is mandatory, exactly once per board

There is no way around it for the first flash. Ebyte's manual is explicit that the E73
ships blank — "the module is not programmed, users need to carry out secondary
development" — and a virgin nRF52840 has **no ROM bootloader of any kind**: no USB DFU, no
serial recovery, nothing to talk to. The first image has to arrive over SWD.

**Expect the module to arrive APPROTECT-locked.** This is no longer speculative. OpenOCD's
own `target/nrf52.cfg` — already installed here at
`$(brew --prefix)/share/openocd/scripts/target/nrf52.cfg` — carries this comment above its
recovery routine:

```tcl
# Mass erase and unlock the device using proprietary nRF CTRL-AP (AP #1)
# http://www.ebyte.com produces modules with nRF52 locked by default,
# use nrf52_recover to enable flashing and debug.
```

Ebyte is named by name, in an upstream OpenOCD config, as a vendor whose nRF52 modules
ship locked. So budget the recovery step as a certainty for the first flash of every
module, not a contingency. It is one command and it costs nothing but the erase; it is
only a problem if it is a surprise.

The mechanism is the CTRL-AP sequence described earlier, and the config is a readable
worked example of it: read `IDR` at AP1 `0xFC` and check for `0x02880000`, write
`ERASEALL` at `0x004`, poll `ERASEALLSTATUS` at `0x008`, then pulse the `RESET` register
at `0x000`. Separately, the same config warns that **high-level adapters cannot do this**
— an ST-Link cannot reach CTRL-AP at all — so the probe has to be a J-Link or a CMSIS-DAP
class adapter.

One corroboration of an earlier decision: recovery needs a real reset, which is a second
independent reason `nRESET` belongs on the Tag-Connect.

### Tooling: no second J-Link required

**`nrfjprog` is a wrapper over SEGGER's J-Link DLL and works with nothing else.** Its own
version output says so:

```
$ nrfjprog --version
nrfjprog version: 10.24.2 external
JLinkARM.dll version: 9.72
```

and the Homebrew cask declares `Required (1): segger-jlink (cask)`. So the question is not
whether Segger is supported — Segger is the *only* thing nrfjprog supports.

The way out is to not need nrfjprog. **OpenOCD does the same job with any CMSIS-DAP
probe**, including `nrf52_recover`, and a Raspberry Pi Debug Probe or a spare Pico running
`debugprobe` firmware is exactly that — convenient, given how much RP2040 hardware is
already lying around here. `probe-rs` is a second option in the same class.

Homebrew status, checked on this machine:

| Package | Kind | State |
|---|---|---|
| `nordic-nrf-command-line-tools` (nrfjprog) | cask | installed, 10.24.2 — depends on `segger-jlink` |
| `segger-jlink` | cask | installed, 9.72 (9.76 available) |
| `nrfutil` | cask | installed 1.4.0, but **the cask was disabled 2026-09-01** for failing the macOS Gatekeeper check |
| `open-ocd` | formula | installed, 0.12.0 — has `nrf5` driver, `nrf52.cfg`, `cmsis-dap.cfg` |
| `probe-rs-tools` | formula | available, 0.32.0, not installed |
| `nrf-connect` | cask | installed, 5.3.2 |
| `pyocd` | — | not in Homebrew; pip only |

The `nrfutil` line matters because Nordic is pushing nrfutil as nrfjprog's replacement, so
the supported path is currently the one Homebrew has disabled. Another reason to keep the
OpenOCD route working rather than depending on Nordic's own tooling.

**One board means one probe.** Either the J-Link or the ORBTrace covers it outright, and
the second is spare. The ORBTrace is the better choice of the two here, for the SWO and
the switchable target supply rather than for the SWD.

### After that, a bootloader carries everything

Install one in the same SWD session and SWD becomes a recovery tool rather than a
workflow.

| | MCUboot | Adafruit nRF52 UF2 |
|---|---|---|
| Update path | `mcumgr` / serial recovery over USB CDC-ACM, or USB DFU | drag a `.uf2` onto a mass-storage volume |
| Entry | firmware request, or serial-recovery pin | double-tap reset |
| Zephyr fit | native, in-tree | works — Zephyr emits `.uf2` via `CONFIG_BUILD_OUTPUT_UF2` |
| Signed images, rollback | yes | no |
| Leads to BLE DFU | yes, SMP builds on it | no |

**Recommendation: MCUboot**, on the grounds that it is the thing wireless DFU is built on
later. UF2 is the friendlier day-to-day experience and a perfectly defensible choice if
dragging a file beats running a tool.

### The ORBTrace covers it, and brings trace with it

An ORBTrace mini is a **CMSIS-DAP v1 and v2** probe implementing SWD and JTAG natively in
gateware, validated against OpenOCD, Black Magic and pyOCD. Because it is a proper
CMSIS-DAP adapter and not a high-level one, it reaches CTRL-AP — so `nrf52_recover` works
and it can do the Ebyte unlock unaided. With only one board to program, that covers the
whole keyboard and the J-Link is spare.

It also solves the bring-up power problem from the section above. It carries **two
programmable supplies — VTRef switchable 1V8/3V3 at 300 mA, and VTPwr switchable 3V3/5V at
300 mA — plus voltage and current measurement on both.** So it can power the module
through the Tag-Connect or the `VOUT` → `VDD` jumper with the PMIC entirely out of
circuit, and give a coarse current reading while doing it. Not PPK2-grade for a 2 µA
idle, but more than enough for "is this board alive and roughly how hungry is it".

**Trace: SWO yes, 2-bit parallel maybe, 4-bit no.** The nRF52840 has an ETM and no ETB, so
trace has to stream off-chip, which is exactly what the ORBTrace is for. Mapping the
trace signals onto the module's pads:

| Signal | nRF52840 pin | E73 pad |
|---|---|---|
| `TRACECLK` | P0.07 | 22 |
| `TRACEDATA0` / **`SWO`** | P1.00 | **36** |
| `TRACEDATA1` | P0.12 | 20 |
| `TRACEDATA2` | P0.11 | **not bonded out** |
| `TRACEDATA3` | P1.09 | 17 |

P0.11 never reaches a pad, so **4-bit parallel trace is impossible on this module** no
matter what the probe can do. One- and two-bit parallel remain possible, but claiming
`TRACECLK`, `TRACEDATA0/1` and the mux's other pins would take four of the fifteen free
unrestricted GPIOs and contort the pin map for a capability a keyboard is unlikely to
need.

**What is worth doing is free: put `SWO` on the Tag-Connect.** Standard TC2030-CTX pin 6
*is* SWO/TDO, and the six-pin footprint already carried over from mesa3 has the pad
sitting unused next to VTref, GND, `SWDIO`, `SWDCLK` and `nRESET`. One net from module pad
36 and it is done, at a cost of one GPIO from the budget of fifteen.

The payoff is specific to this project. The open power questions — what is waking the CPU,
whether the Taipo decoder is still ticking, how often the radio actually runs — are
exactly what ITM output and DWT PC-sampling and exception trace answer. **The PPK2 shows
the shape of the current; SWO shows which code caused each bump.** Together they are the
right pair of instruments for tuning this design, and one of them costs a single wire.

### Routine updates: one board, one cable

**There is only one MCU in the keyboard.** The right half is passive, so there is nothing
on it to flash, nothing to debug, and no second probe or second Tag-Connect. The
awkwardness that started this whole line of questioning has been designed out rather than
worked around.

An update is: plug USB-C into the left board, flash, done.

### DFU over BLE, if wanted

MCUboot plus SMP gives wireless DFU, and with a single MCU it is straightforward: your
computer or phone connects to the keyboard directly, which is the easy case. The
peripheral-side complication that made this awkward under the two-wireless-halves plan is
gone with it.

Not needed for a first board, but it is the reason to pick MCUboot now rather than regret
it later.

### The board has to be powered, and USB alone will not do it

A consequence of the simple power path that deserves stating plainly, because it lands
right on this workflow. From the PS's USB supply section:

> The USB peripheral has a dedicated internal voltage regulator for converting the VBUS
> supply to 3.3 V used by the USB signalling interface (D+ and D- lines, and pull-up on
> D+). The rest of the USB peripheral (USBD) is supplied through the main supply like any
> other on-chip feature. **As a consequence, both VBUS and either VDDH or VDD supplies are
> required for USB peripheral operation.**

`VBUS` powers the D+/D− signalling and nothing else. With cells feeding `VDD` and `VBUS`
wired only to the module's `VBUS` pad, **a board with no cells in it is dead, and cannot
be flashed over USB.** Normal flashing therefore happens with cells installed, which is
fine and already accounted for.

Bring-up is the case that needs an answer, because that is exactly when the PMIC is not
yet trusted. It already has one, for free: **the `VOUT` → module `VDD` profiler jumper is
also the power injection point.** Cut it and feed `VDD` from the PPK2 in source-meter mode
(0.8–5 V, up to 1 A) or any bench supply, and the module runs with the boost entirely out
of the picture. The same two pads that measure the load also power it.

If USB-only operation with no cells ever turns out to matter, the fallback is the power
path rejected earlier: OR the boost output and `VBUS` into `VDDH` and let REG0 generate
`VDD` internally. Note that this is all-or-nothing — the PS says high voltage mode
requires that "the VDD pin is not connected to any voltage supply" — so it is a different
board, not a stuffing option.

### What the board must provide

0. **`SWO` on Tag-Connect pin 6** — module pad 36 (`P1.00`). One wire, one GPIO, and the
   pad already exists. See the ORBTrace section for why it earns its place.
1. **`nRESET` on the Tag-Connect.** Not optional on a design that idles at 2.4 µA: a
   sleeping core with its debug power domain down often cannot be attached to at all, and
   connect-under-reset is the way in. It is also required for the APPROTECT recovery
   above. **Good news — this carries over unchanged:** mesa3-left already uses
   `Tag-Connect_TC2030-IDC-FP_2x03_P1.27mm_Vertical`, the six-pin footprint, which has
   room for VTref, GND, `SWDIO`, `SWDCLK`, `nRESET` and a spare. The module brings
   `SWD` (37), `SWC` (39) and `RST` (26) out to dedicated pads, so nothing competes with
   the matrix.
2. **A reset button, not just a pad.** mesa3 has a reset *pad*, which is fine when a
   board is on the bench. Double-tap-to-bootloader and serial recovery both want something
   pressable, and on a wireless board that lives away from the desk it is the recovery
   path when firmware is wedged. It sits alongside the `SHPHLD` power button on the
   underside. The everyday path stays a key combo bound to "reboot to bootloader".

### Board identity: the CBOR blob already answers it

mesa3 deliberately has no board-ID strap — "each keyboard is flashed with a small CBOR
blob naming its model, and the firmware reads that". With a single MCU there is no
left-versus-right question any more, but the blob still earns its place: it is how the
firmware tells a mesa3w from a mesa3 or a mesa2 Rev B, which matters precisely because the
**matrix is deliberately identical across all three**.

One requirement it puts on the flash map: **the blob needs its own partition**, outside
the MCUboot slots, so that an application update does not disturb which half a board
thinks it is. Worth fixing in the partition layout before the first image is built rather
than after.

## Decisions

**Left board only; right half and RJ-45 unchanged.** mesa3w replaces the Tiny2040 with an
nRF52840 module, a PMIC and a cell pack. mesa3-right is reused as designed. The cable
carries the same seven matrix signals it does today and no power.

**The single 5 × 4 grid survives, and with it the keymap constraint.** All eighteen keys
keep their exact mesa2 (column, row), so one keymap serves mesa2 Rev B, mesa3 and mesa3w
alike. This was the constraint the two-wireless-halves plan would have broken, and
recovering it is a large part of why this scope is better.

**Runs from USB or from cells, interchangeably.** This is the requirement that drove the
rescope: one keyboard for a wired desk and untethered travel. It means abandoning the
"`VBUS` to the module's `VBUS` pad only" arrangement — see *Running from USB* below — in
favour of normal voltage mode with a USB LDO and a P-FET switchover. With USB connected the
keyboard runs with no cells fitted at all.

**E73-2G4M08S1C module** (`C356849`), **nPM2100 QFN-16** (`C46968654`) with a 2.2 µH
inductor and five ceramics, `VSET` open for a 3.0 V rail, and a 32.768 kHz crystal on
`XL1`/`XL2`.

**A hardware power button on the PMIC's `SHPHLD`.** Hold two seconds for Ship mode at
35 nA — an Apple-style off switch needing no firmware, working when firmware is wedged,
and disposing of the held-key drain that idle mode cannot.

**Four or five plain 3535 LEDs on nRF PWM.** No SK6812s: the one-wire protocol has no
Nordic peripheral support, and integrated controllers draw ~1 mA each doing nothing. LEDs
live on the low-frequency pads; an LP5009/LP5012 is the fallback past about six channels.

**No deep sleep; Eneloop-class cells.** System ON, idling at ~2.4 µA on a `PORT`-event
wake, radio duty-cycled by connection interval and peripheral latency. Ordinary NiMH leaks
~580 µA-equivalent and would swamp the design; low-self-discharge cells leak ~34 µA and
set a floor below which tuning is pointless.

**Active-low matrix.** Columns driven low, rows pulled up, sensing low — forced by the
mesa3 diode orientation, which is now carried over unchanged along with the right board.

**SWD once, then USB.** Tag-Connect with `nRESET` and `SWO`, MCUboot installed in that
session, every update after that over USB-C. Expect the Ebyte APPROTECT unlock on first
flash. One board, one probe — the ORBTrace covers it.

**Profiler break points** at cell + → `VBAT` and `VOUT` → module `VDD`, as parallel 0805
and 2-pin footprints so development boards get headers and later ones get 0Ω.

## Running from USB — the constraint this forces

**Reopened 2026-09-13.** Wanting the keyboard to run from USB — one board for a wired desk
and untethered travel — invalidates the "simple power path" decision, and is what drove
the rescope to a single smart half.

The PS is unambiguous: `VBUS` feeds only the USB signalling regulator, and "both VBUS and
either VDDH or VDD supplies are required for USB peripheral operation". So USB power means
the boost output and `VBUS` have to be combined somewhere. Two shapes:

**High voltage mode** — OR both into `VDDH`, let REG0 generate `VDD` internally. Elegant
on paper, but the REG0 specs bite:

| | |
|---|---|
| `VDDOUT` | 1.8–3.3 V, set by `REGOUT0` |
| `VREG0,DROP` | **VDDH must exceed VDD by ≥ 0.3 V** |
| `IEXT,OFF` | 1 mA external draw in System OFF |
| `IEXT,LOW` | **5 mA** when radio TX > +4 dBm |
| `IEXT,HIGH` | 25 mA when radio TX ≤ +4 dBm |

External draw is "the sum of all GPIO currents and the current drawn from VDD" — so
**the LEDs count against it.** At the E73's +8 dBm that is a 5 mA ceiling for four or five
LEDs plus every other pin, which is tight to the point of being a constraint on
brightness. Running the radio at ≤ +4 dBm buys the 25 mA budget and is ample range for a
keyboard, so that becomes a design decision rather than a default.

The drop rule also stacks badly on battery: boost at 3.0 V through a Schottky is 2.7 V at
`VDDH`, which caps `VDD` at 2.4 V — worse for the LED forward-voltage question, not
better. It needs ideal-diode ORing rather than Schottkys to work at all.

**Normal voltage mode with a USB LDO** — keep `VDDH` tied to `VDD`, add a small 5 V → 3.3 V
LDO on `VBUS`, and switch between it and the boost with a P-FET whose gate sits on the USB
rail (USB present ⇒ battery path off, ~0 V drop when on battery). More parts, but no
`IEXT` ceiling, no `VREG0,DROP`, no REG0 arithmetic, and the LDO's quiescent current only
exists when plugged in, which is exactly when it does not matter.

**Leaning: normal voltage mode.** The high-voltage route trades two cheap parts for a set
of constraints that land directly on the two things already awkward here — LED current and
LED forward voltage.

## The inner index layer key

Carried here so it is not lost between boards, not because it is settled. A
**syllable-oriented input method** under investigation as of 2026-09-11 would want **one
extra key immediately inboard of the near-row ("lower") index key** — the inner-index
column position.

Its character matters for the design: it is a **layer key**, momentary or toggle, and it
**does not participate in chords with that hand**, because the lateral reach from the
index home position is uncomfortable. That rules out nothing electrically, but it means
the key is pressed on its own or alongside the *other* hand, never as part of a same-hand
chord.

**It is free in the matrix.** Dosh dropped mesa2's outer pinky key (`R`), which is exactly
why mesa3 carries "18 keys in 20 slots" — eighteen keys in a 5 × 4 grid, with one slot
empty on each half. The new key reuses that vacated slot:

- Wire it to **`COL_1`** — the pinky column — and whichever row does not carry pinky `A`.
- Physical position and matrix position do not have to agree. Sitting next to the index
  finger while living electrically on the pinky column is just a trace, and on a board
  this size a short one.
- **No new GPIO, no new column, no new row.** The mesa3w pin budget is untouched: still
  5 columns + 2 rows against 15 free unrestricted pads.

Two things not to get wrong:

- **It still needs its own diode.** "Does not chord" is a statement about firmware chord
  resolution, not permission to skip ghosting isolation — two keys can be physically down
  at once whatever the decoder thinks of the combination.
- **Place it before the module and the cells, not after.** The inner-index position is at
  the board's inner edge, which on a wireless build is precisely where the E73's 13 × 18 mm
  body, its ceramic-antenna keep-out and the AA holder are all competing for room. This is
  the one part of this that is genuinely hard to retrofit, and it is a layout ordering
  problem rather than a schematic one.

**The rescope changes what this costs.** The grid is one 5 × 4 again, so there are two
free slots — one per half — but the halves are no longer symmetric in how much work they
are:

- **On the left it is free**, and mesa3w is being laid out anyway. Wire it to `COL_1` and
  whichever of `ROW_A`/`ROW_B` does not carry pinky `A`.
- **On the right it is not.** mesa3-right is reused precisely because it needs no
  redesign, and adding a key means revising and re-fabbing that board. The free slot is
  there (`COL_1` with `ROW_C`/`ROW_D`), so it is cheap *whenever* that board is next
  touched — just not free today.

So if the input method needs it on one hand only, mesa3w gets it for nothing. If it needs
both, that is a right-board revision to schedule deliberately rather than discover late.

Deliberately **not** added to mesa3, which is routed and heading for fab.

## Sequencing

**Only one board gets designed.** mesa3-right is finished and reused as-is; mesa3w is a
left board that keeps mesa3's key geometry, matrix assignment and RJ-45 pinout, and
replaces everything in the middle.

The one thing that must be resolved *before* layout rather than after is the **USB power
path**, because it decides whether the module runs in normal or high voltage mode, and
that changes which pins carry what. Everything else on the open list is either a stuffing
option or firmware.

Nothing in the firmware power work gates the hardware. The board only has to *permit* the
right answers — which it does, via the `PORT`-event wake configuration, the `SHPHLD`
button, the 32.768 kHz crystal pads, `SWO` on the Tag-Connect and the two profiler break
points. The sleep-state policy, the connection-parameter ramp and the decoder deadline
conversion all get settled once the Zephyr port is running and the PPK2 has something real
to measure.

## Still open

1. **One AA or two.** Electrically identical; decide it against the case, the weight and
   how long a charge should last. Now a single pack for the whole keyboard, which makes
   two cells more attractive than it was when each half carried its own.
2. **Cell holder and its footprint.** A AA holder is through-hole and almost certainly
   hand-soldered, so it does not need to be in the JLC parts library — but it needs a
   footprint, and a keep-out away from the module's ceramic antenna.
3. **USB power path details.** Normal voltage mode is the lean, but the LDO part, the
   P-FET switchover and the rail voltage (3.0 V from `VSET`, or 3.3 V configured over I²C
   after boot) are unpicked. The LED forward voltages decide the rail.
4. **Radio TX power.** Only binding if high voltage mode comes back, where +8 dBm caps
   external draw at 5 mA against 25 mA at ≤ +4 dBm. Worth deciding anyway: ≤ +4 dBm is
   ample for a keyboard and cheaper on the battery.
5. **Decoder deadline API.** Converting the Taipo decoder from a periodic tick to a
   next-deadline return value — the single largest firmware lever on battery life.
   Deferred until the Zephyr port is running.
6. **Bootloader choice and flash partition map.** MCUboot versus UF2, and where the
   board-identity blob lives so updates cannot clobber it.
7. **Inner index layer key.** Free in the left matrix; needs a right-board revision to
   have it on both hands. See below.
