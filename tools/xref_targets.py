"""Resolve call targets against the current saved-name table.

Usage: python tools/xref_targets.py 0xADDR [0xADDR ...]
Prints: target -> name (or FUN_/UNNAMED), and whether the address is a
known function entry. Read-only.
"""
import sys

NAME_TABLE = ('reverse-engineering/binary-analysis/'
              'ghidra-function-name-table-2026-08-17.tsv')

entries = {}
with open(NAME_TABLE) as f:
    for line in f:
        line = line.rstrip('\n')
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        try:
            va = int(parts[0], 16)
        except ValueError:
            continue
        entries[va] = (parts[1], parts[2] if len(parts) > 2 else '',
                       parts[3] if len(parts) > 3 else '')

for arg in sys.argv[1:]:
    try:
        va = int(arg, 16)
    except ValueError:
        print(f'{arg}: NOT HEX')
        continue
    hit = entries.get(va)
    if hit:
        print(f'0x{va:08x} -> {hit[0]}  (end {hit[2]})')
    else:
        # nearest lower entry, to say what contains it if interior
        lower = [a for a in entries if a <= va]
        near = max(lower) if lower else None
        if near and near != va:
            print(f'0x{va:08x} -> UNNAMED (interior of/next after '
                  f'{entries[near][0]} @ 0x{near:08x})')
        else:
            print(f'0x{va:08x} -> UNNAMED')
