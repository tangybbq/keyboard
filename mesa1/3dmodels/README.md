# mesa1 3D models

Models attached to the `mesa1:Kailh_socket_PG1350` footprint so the switch
stack shows up in the 3D viewer and in `File → Export → STEP`. That footprint
is the whole key: switch on the front, hotswap socket on the back.

All three attach to that one footprint. Add them in Footprint Editor →
Properties → 3D Models, then `Tools → Update Footprints from Library` in each
PCB to push them to the placed instances.

| File | Offset (mm) | Rotation (deg) |
|---|---|---|
| `Kailh_socket_PG1350.step` | 0, 0, 0 | 0, 0, 0 |
| `SW_Kailh_Choc_V1.step` | 0, 0, 0 | 0, 0, **180** |
| `MBK_Keycap_1u.step` | 0, 0, **6.65** | 0, 0, 0 |

Path prefix for all three: `${KIPRJMOD}/../3dmodels/`.

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
