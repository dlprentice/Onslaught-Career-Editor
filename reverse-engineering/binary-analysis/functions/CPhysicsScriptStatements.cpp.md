# CPhysicsScriptStatements.cpp Functions

> Source File: `CPhysicsScriptStatements.cpp` (debug-path family)
> Binary: `BEA.exe`
> Debug path anchors: `0x00625818` (`CPhysicsScriptStatements.cpp`), allocation-site path refs around `0x00625850`

## Overview

Partial mapping of physics-script statement helpers discovered by deep decompile + caller/xref analysis.

Status: **PARTIALLY MAPPED** (core helper set recovered; full statement family still incomplete).

## Mapped Functions (Current)

| Address | Name | Purpose | Evidence |
|---------|------|---------|----------|
| `0x0042f5f0` | `CWeaponStatement__Create` | Allocates/initializes weapon-statement node and appends to statement set | Called from `CWeaponStatement__VFunc_01_0042f5b0`; allocates object + name string; appends to `DAT_008553e8` |
| `0x0042f750` | `CWeaponStatement__GetSerializedSize` | Recursive byte-size accumulator for weapon-statement tree | Self-recursive; sums child branch sizes with per-node header bytes |
| `0x0042fa80` | `CWeaponModeStatement__Create` | Allocates/initializes weapon-mode statement node and appends to statement set | Called from `CWeaponModeStatement__VFunc_01_0042fa40`; appends to `DAT_008553ec` |
| `0x0042fc70` | `CWeaponModeStatement__GetSerializedSize` | Recursive byte-size accumulator for weapon-mode statement tree | Self-recursive size walk with same pattern as weapon statement sizing |
| `0x0042ffa0` | `CRoundStatement__Create` | Allocates/initializes round-statement node and appends to statement set | Called from `CRoundStatement__VFunc_01_0042ff60`; appends to `DAT_008553f0`; includes stream-name flags (`Stream Laser`, `Gill M Breath`) |
| `0x004301e0` | `CRoundStatement__GetSerializedSize` | Recursive byte-size accumulator for round-statement tree | Self-recursive size helper with per-node overhead |
| `0x00433390` | `CComponentBasedOn__CopyFrom` | Deep-copy helper for component-based statement resource fields | Called by `CComponentBasedOn__VFunc_01_0043db90`; copies many scalar fields and deep-copies multiple owned strings |

## Notes

- This file was previously a stub. The seven helpers above are now verified by read-back after headless rename apply.
- Several former `CConsole__Unk_*` labels in this range were corrected to statement-class names based on caller ownership and behavior.
- This mapping is intentionally conservative: only helpers with multi-signal evidence were promoted.

## Remaining Work

1. Recover additional statement constructors/deserializers in nearby `0x0042f***..0x00433***` ranges.
2. Map serialize/deserialize entrypoints per statement subtype.
3. Resolve class layout/field names for statement structs beyond current coarse naming.
