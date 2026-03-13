# GroundAttackAircraft.cpp Functions

> Source File: GroundAttackAircraft.cpp | Binary: BEA.exe
> Debug Path: 0x0062cadc

## Overview

Ground attack aircraft implementation - the player-controllable aircraft/mech hybrid vehicle. Constructor allocates three sub-objects for weapons, targeting, and physics systems.

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0x0047bbf0 | CGroundAttackAircraft__Constructor | Initialize ground attack aircraft | **DEFINED IN GHIDRA** |

**Note:** There is an alignment NOP sled at `0x0047bbe4`; the actual entrypoint used by the vtable is `0x0047bbf0`. Function object recovery at `0x0047bbf0` is now complete in Ghidra.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d2b00 | Unwind@005d2b00 | 27 | Cleanup for sub-object 1 (offset +0x208) |
| 0x005d2b16 | Unwind@005d2b16 | 22 | Cleanup for sub-object 2 (offset +0x70, 0x68 bytes) |
| 0x005d2b34 | Unwind@005d2b34 | 23 | Cleanup for sub-object 3 (offset +0x13C, 0x30 bytes) |

## Key Observations

- **Three sub-objects allocated** at offsets +0x70, +0x13C, +0x208
- **Two vtables assigned**:
  - 0x005dbd4c - Primary CGroundAttackAircraft vtable
  - 0x005dbd20 - Base class vtable (likely CAirUnit)
- **SEH prolog** - `MOV EAX, FS:[0]; PUSH -1; PUSH handler` pattern
- **Source lines** - Constructor references lines 22, 23, 27

## Recovery Notes

- Manual function-object recovery was required at `0x0047bbf0` due to SEH-prolog/disassembly boundary behavior in this cluster.
- Current state: function exists and is named `CGroundAttackAircraft__Constructor`.

## Related Files

- AirUnit.cpp - CAirUnit base class
- Player.cpp - Player mech system
- Mech.cpp - Similar player vehicle type

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
*Note: Constructor function-object recovery completed in Ghidra*
