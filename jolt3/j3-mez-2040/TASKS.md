# j3-mez-2040 — JLCPCB Assembly Prep

## Footprint changes

- [ ] **U3 (flash):** swap `Package_SON:WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm` → `Package_SO:SOIC-8_5.23x5.23mm_P1.27mm`. Update symbol MPN to `W25Q128JVSIQ`. (Decision: current layout has ~2mm of margin around U3, SOIC-8 fits.)
- [ ] **SW1, SW2 (tactile):** swap `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` → footprint matching TS-1187A-B-A-B (5.1×5.1 mm SMD-4P). Create or import footprint if not already in a library.
- [ ] Re-route U3, SW1, SW2 nets in PCB; verify clearances to neighbors (RP2040, crystal, USB-C).

## Schematic metadata (for every placed component)

Add custom properties so Fabrication Toolkit emits a JLC-ready BOM. `LCSC` is the only one JLC actually requires; the others just become extra columns.

**Bulk workflow (recommended):** `Tools → Edit Symbol Fields Table` in the schematic editor. Add an `LCSC` column, fill in C-numbers in the grid, apply. Much faster than editing each symbol individually.

**Per-symbol workflow:** select symbol → `E` → in Properties dialog, click `+` to add field `LCSC` = `C2040`, etc.

Fields to add:
- [ ] `LCSC` — the C-number (required)
- [ ] `MPN` — manufacturer part number (optional)
- [ ] `Manufacturer` (optional)

Per-part mapping:

| Ref | MPN | LCSC |
|-----|-----|------|
| U1 | RP2040 | C2040 |
| U2 | AP2112K-3.3TRG1 | C51118 |
| U3 | W25Q128JVSIQ | C97521 |
| Y1 | ABM8-272-T3 | C20625731 |
| D1, D2 | SK6812MINI-HS | C2922787 |
| J1 | DF40C-30DS-0.4V(51) | C424642 |
| SW1/SW2 | TS-1187A-B-A-B | C318884 |
| R 10k 0402 | (verify Basic at order time) | C25741 |
| R 1k 0402 | " | C11702 |
| R 27 0402 | " | C25092 |
| R 5.1k 0402 | " | C25905 |
| C 100n 0402 | " | C1525 |
| C 1u 0402 | " | C52923 |
| C 10u 0402 | " | C15525 |
| C 12p 0402 | " | C1548 |

## DNP decisions (resolved)

KiCad's built-in DNP is what Fabrication Toolkit reads (the project's `fabrication-toolkit-options.json` already has `"EXCLUDE DNP": true`). For parts you'll hand-solder, check **both** "Do not populate" **and** "Exclude from BOM" in the symbol properties — that keeps JLC from asking you to confirm a part that isn't being placed.

- [ ] **D1, D2 (SK6812MINI-HS):** JLC places. The -HS variant tolerates standard lead-free reflow. No DNP flag.
- [ ] **J29 (USB-C):** DNP + Exclude from BOM. Hand-solder after.
- Tag-Connect — no action (pads only, no part to place).

## Footprint rotation / pin-1 audit

JLC's part library uses rotations that often differ from KiCad defaults. Audit each SMT part that JLC will place:

- [ ] U1 RP2040 — verify pin-1 marker and rotation match LCSC C2040
- [ ] U2 AP2112K — SOT-23-5 orientation
- [ ] U3 flash (new SOIC-8 footprint) — pin-1 dot placement
- [ ] Y1 crystal — pin-1 / orientation
- [ ] D1, D2 SK6812 — arrow/pin-1
- [ ] J1 DF40C — orientation
- [ ] SW1/SW2 — new footprint, confirm pin mapping

Use Fabrication Toolkit's rotation database, or add per-part rotation offsets in the plugin config.

## Pre-fab checks

- [ ] ERC clean
- [ ] DRC clean
- [ ] Confirm board outline and mounting holes unchanged (38×38 mm, corner holes for standoffs)
- [ ] Add 2–3 fiducials if not already present (JLC requires for fine-pitch SMT)
- [ ] 3D viewer sanity check

## Fabrication outputs

- [ ] Run Fabrication Toolkit → Gerbers, drill, BOM.csv, CPL (positions)
- [ ] Inspect BOM.csv — every placed part has an LCSC number
- [ ] Inspect CPL — rotations look correct

## First-article order

- [ ] Upload to JLCPCB, choose Standard PCB + SMT Assembly
- [ ] Review JLC's part-placement preview; fix any red/yellow flags (unknown parts, rotations)
- [ ] Order qty 5, economy shipping
- [ ] On arrival: hand-solder USB-C (and SK6812 if DNP'd), power up, validate
