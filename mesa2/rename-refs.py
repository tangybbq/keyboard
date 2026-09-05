#!/usr/bin/env python3
"""Rename schematic reference designators in mesa2.kicad_sch.

Konnect's edit_schematic_component updates only the symbol's Reference
*property* and leaves the `instances` block alone. From KiCAD 6 on, the
instances reference is the authoritative one -- it drives netlisting and PCB
sync -- so a property-only rename half-lands: the schematic looks right and the
netlist disagrees. This does both, together.

Scope of the edit, deliberately narrow:
  * (property "Reference" "X" ...)  on symbol instances
  * (reference "X")                 inside instances blocks
Nothing else is touched: no UUIDs, no geometry, no ordering, no reserialisation.
The lib_symbols block is excluded by paren-matching so the library defaults
(A, D, J, SW, TP) survive.

One simultaneous mapping is applied against the original text, so renames that
would collide in sequence (D_LS0->D_LS1 while a different D_LS1 exists) are a
non-issue.

Usage:  python3 rename-refs.py [map.csv] [--apply]   (default is a dry run)

Pure swaps are safe: the mapping is applied in one pass against the original
text, so A->B and B->A cannot chase each other.
"""
import csv, re, sys, pathlib

SCH = pathlib.Path(__file__).parent / 'mesa2' / 'mesa2.kicad_sch'
MAP = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].endswith('.csv') \
      else pathlib.Path(__file__).parent / 'rename-refs.csv'

mapping = {}
with open(MAP) as f:
    for row in csv.DictReader(f):
        if row['current'] != row['new']:
            mapping[row['current']] = row['new']

src = SCH.read_text()

# exclude lib_symbols: its symbols carry the library default Reference prefixes
start = src.index('(lib_symbols')
depth = 0
for end in range(start, len(src)):
    if src[end] == '(':   depth += 1
    elif src[end] == ')':
        depth -= 1
        if depth == 0: break
head, body = src[:end+1], src[end+1:]

hits = {'property': 0, 'instances': 0}
unknown = set()

def sub_property(m):
    old = m.group(1)
    if old in mapping:
        hits['property'] += 1
        return f'(property "Reference" "{mapping[old]}"'
    unknown.add(old)
    return m.group(0)

def sub_instance(m):
    old = m.group(1)
    if old in mapping:
        hits['instances'] += 1
        return f'(reference "{mapping[old]}")'
    unknown.add(old)
    return m.group(0)

body = re.sub(r'\(property "Reference" "([^"]+)"', sub_property, body)
body = re.sub(r'\(reference "([^"]+)"\)',          sub_instance, body)

print(f"mapping        : {len(mapping)} renames")
print(f"property hits  : {hits['property']}")
print(f"instances hits : {hits['instances']}")
print(f"left unchanged : {len(unknown)} refs -> {sorted(unknown)}")

if hits['property'] != len(mapping) or hits['instances'] != len(mapping):
    sys.exit(f"ABORT: expected {len(mapping)} hits in each location")

out = head + body
if len(out) - len(src) != sum(len(v) - len(k) for k, v in mapping.items()) * 2:
    sys.exit("ABORT: byte-delta does not match the expected rename delta")

if '--apply' in sys.argv:
    SCH.write_text(out)
    print(f"\nWROTE {SCH}")
else:
    print("\ndry run - pass --apply to write")
