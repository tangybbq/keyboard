# mesa1 3D models

Models for the parts that stick up off the board, so the 3D viewer and
`File → Export → STEP` show what a case or stand actually has to clear.

| File | Footprint | Offset (mm) | Rotation (deg) |
|---|---|---|---|
| `Kailh_socket_PG1350.step` | `mesa1:Kailh_socket_PG1350` | 0, 0, 0 | 0, 0, 0 |
| `SW_Kailh_Choc_V1.step` | `mesa1:Kailh_socket_PG1350` | 0, 0, 0 | 0, 0, **180** |
| `MBK_Keycap_1u.step` | `mesa1:Kailh_socket_PG1350` | 0, 0, **6.65** | 0, 0, 0 |
| `Pimoroni_Tiny2040.step` | `mesa1:Pimoroni_Tiny2040` | 0, 0, 0 | 0, 0, 0 |
| `RJ45_Amphenol_54602-x08_Horizontal.step` | `Connector_RJ:RJ45_…` | 0, 0, 0 | 0, 0, 0 |

Path prefix for all of them: `${KIPRJMOD}/../3dmodels/`. Use the variable, not
an absolute path, or the references break for anyone who clones the repo.

The first three all hang off the one key footprint — it is the whole key:
switch on the front, hotswap socket on the back. Add them in Footprint Editor →
Properties → 3D Models, then `Tools → Update Footprints from Library` in each
PCB to push them to the placed instances.

The RJ45 model has to go on the PCB instance rather than the library footprint,
since that footprint comes from KiCad's stock `Connector_RJ` library.

## Why those numbers

**Socket.** The transform is baked into the STEP (rotate +90° about X, then
translate 5.0, -3.75, -1.6), so KiCad needs no offset. The -1.6 puts it on the
back face of the board and therefore assumes the 1.6 mm stackup — regenerate if
the board thickness changes. Alignment was checked against the footprint: the
two receptacle collars (r 1.45) land in the 3 mm NPTH at (0, 5.95) and
(-5, 3.75), and the contact tails land inside pads 1 and 2.

**Switch.** Used as published, in KiCad 3D coordinates. The upstream footprint
puts the switch pins at board (0, -5.9) / (5, -3.8); ours has them at
(0, 5.95) / (-5, 3.75), i.e. the switch is turned around, hence the 180° about
Z. With that rotation the pins line up with the socket collars.

**Keycap.** +6.65 in Z seats the cap's stem plate (model z = 1.4) on the
switch's slider top (z = 8.05). Checked for interference against the switch
solid: zero intersection volume. The two stem legs drop into the slider's
slots without bottoming out, and the skirt clears the switch housing by 1.6 mm
at rest, shrouding it on the way down.

## Envelope, per key, relative to the front face of the PCB

| | Z (mm) |
|---|---|
| Socket, lowest point | -3.44 (1.84 below the back face) |
| Board back face | -1.60 |
| Switch housing top | +5.05 |
| Keycap bottom rim | +6.65 |
| Keycap top | +10.80 |

Keycap outline is 17.45 × 16.45 mm against an 18 × 17 mm pitch, so 0.55 mm of
air between neighbours in both directions.

## Tiny 2040 and RJ45

Neither is a real vendor model — both are envelope solids, enough to place a
wall or a cutout against, not enough to render nicely.

**Tiny 2040.** Built here in FreeCAD; see `Pimoroni_Tiny2040.step`. Pimoroni do
not publish a STEP; SnapMagic and TraceParts have one but both want an account.
The XY is exact, lifted from the F.Fab geometry of our own footprint, which came
verbatim from Pimoroni's `pimoroni-boards.lbr`:

- module PCB 20.32 × 18.0, 0.4 mm corner chamfers, from X 0 to 20.32, Y ±9
- USB-C receptacle 7.82 × 8.64, X -2.175 to 5.645, overhanging the module end
- underside components filling the footprint's 16.92 × 12.6 Edge.Cuts relief

The Z split is derived, not measured. Pimoroni quote 22.9 × 18.2 × 6 mm overall;
6.00 is reproduced exactly as 1.84 underside + 1.00 module PCB + 3.16 USB-C
receptacle. Those three are a plausible decomposition of a figure that is only
quoted as a total, so treat the individual numbers as approximate — in
particular check the 1.84 before committing to a pocket depth. Overall L and W
come out 22.50 × 18.00 against their quoted 22.9 × 18.2; the package geometry is
the more trustworthy of the two.

**RJ45.** `RJ45_Amphenol_54602-x08_Horizontal.step` is a plain 6-face box,
15.31 × 17.74 × 13.5, already in this directory. It lines up with the stock
footprint exactly — X -3.210…12.100 against an F.Fab of -3.205…12.095, and Y
mirrored as KiCad's 3D convention requires.

Note that KiCad 10 does **not** ship a model for this connector. Its
`Connector_RJ.3dshapes` has only three RJ45s (`Amphenol_RJHSE538X`,
`Molex_9346520x_Horizontal`, `Pulse_JK0654219NL_Horizontal`), so the
`${KICAD10_3DMODEL_DIR}/…/RJ45_Amphenol_54602-x08_Horizontal.step` reference the
footprint carries can never resolve. Point the instance at the local box
instead. If a proper model is ever wanted, Amphenol's 54602 CAD is on SnapMagic
and TraceParts, behind a signup.

## Keycap colour

The upstream MBK file ships with Fusion's `Opaque(214,14,14)` appearance baked
in — a hard red. Changed to a neutral charcoal by editing the one colour entity
the keycap solid resolves to:

    #6912=COLOUR_RGB('MBK Charcoal',0.235294117647059,0.235294117647059,
    0.250980392156863);

Three RGB floats, 0–1. Geometry is untouched. `#6911` ('Steel - Satin') is
unreferenced upstream leftover — editing it does nothing.

## Sources and licensing

- `Kailh_socket_PG1350.step` — Kailh's own PG1350 socket CAD (`PG1350.STEP`,
  SolidWorks 2018), the copy already in this repo at
  `jolt2/jolt2-verts/PG1350-socket.STEP`, repositioned.
- `SW_Kailh_Choc_V1.step` — from [kiswitch](https://github.com/kiswitch/kiswitch)
  (formerly perigoso/keyswitch-kicad-library),
  `library/3dmodels/3d-library.3dshapes/SW_Kailh_Choc_V1.stp`. Dual licensed
  MIT / CC BY-SA 4.0; taken under the MIT option.
- `MBK_Keycap_1u.step` — MBK reproduction by darryldh,
  [Thingiverse thing:4564253](https://www.thingiverse.com/thing:4564253), via
  [namnlos-io/choc_keycaps](https://github.com/namnlos-io/choc_keycaps).
  **CC BY-NC 4.0.** Published with Max Burger's permission. It is a
  reproduction for rendering, not the production file — close but not exact, so
  do not treat it as a tolerance reference. 1.5u, 2u and homing variants are in
  the same upstream folder if they are ever needed here.

The NC clause matches this repo's own CC BY-NC 3.0 terms, but it does mean the
keycap model cannot travel into anything commercial.
