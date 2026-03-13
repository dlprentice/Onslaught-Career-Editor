# Tentacle.cpp Functions

> Source File: Tentacle.cpp | Binary: BEA.exe
> Debug Path: 0x00632ccc

## Overview

CTentacle is a boss enemy class representing the giant mechanical tentacles that emerge from the ground/water. This file contains factory methods for creating tentacle-related components including the visual guide, AI controller, and integration with the Warspite battleship boss.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004f0760 | CTentacle__CreateTentacleGuide | Allocate CTentacleGuide component (0xEC bytes) | ~128 bytes |
| 0x004f07e0 | CTentacle__CreateTentacleAI | Allocate CTentacleAI controller (0x20 bytes) | ~128 bytes |
| 0x004f0860 | CTentacle__CreateWarspiteAI | Allocate CWarspiteAI for tentacle boss (0x60 bytes) | ~128 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d5050 | Unwind@005d5050 | 0x2f (47) | Cleanup for CTentacleGuide allocation |
| 0x005d5070 | Unwind@005d5070 | 0x35 (53) | Cleanup for CTentacleAI allocation |
| 0x005d5090 | Unwind@005d5090 | 0x3c (60) | Cleanup for CWarspiteAI allocation |

## Key Observations

- **Pool ID 0x1b (27)** - CTentacleGuide uses memory pool 27, object size 0xEC (236) bytes
- **Pool ID 0x17 (23)** - CTentacleAI and CWarspiteAI both use memory pool 23
- **Component storage offsets**:
  - CTentacleGuide stored at `this+0x70` (offset 112)
  - CTentacleAI stored at `this+0x208` (offset 520)
  - CWarspiteAI stored at `this+0x13c` (offset 316)
- **Factory table at 0x005e4170** - Function pointers referenced by vtable-like structure

## Class Relationships

```
CTentacle (main boss class)
  +0x70  -> CTentacleGuide  (visual/animation component, 236 bytes)
  +0x13c -> CWarspiteAI     (combat AI, 96 bytes)
  +0x208 -> CTentacleAI     (tentacle-specific AI, 32 bytes)
```

## RTTI Strings

| Address | String | Class |
|---------|--------|-------|
| 0x0063d968 | `.?AVCTentacle@@` | Main tentacle class |
| 0x00632cf8 | `.?AVCTentacleGuide@@` | Visual guide component |
| 0x00632d18 | `.?AVCTentacleAI@@` | AI controller |
| 0x00627968 | `.?AVCComponentTentacle@@` | Component base class |
| 0x0062dfe0 | `.?AVCMCTentacle@@` | Motion controller |

## VTables

| Address | Class | Notes |
|---------|-------|-------|
| 0x005df46c | CTentacleAI | Set in CreateTentacleAI |
| 0x005df498 | CWarspiteAI | Set in CreateWarspiteAI |
| 0x005dc450 | CTentacleGuide | Set via FUN_0049cad0 initializer |

## Debug Strings

- `"tentacle"` at 0x0062e02c
- `"Got %d bones in tentacle\n"` at 0x0062e048
- `"Tentacle Activation Effect"` at 0x00632d38

## Memory Allocation Pattern

All three functions follow the same pattern:
1. Call `OID__AllocObject(size, pool_id, debug_path, line_number)` to allocate
2. If allocation succeeds, initialize component via constructor
3. Set vtable pointer on the new object
4. Store component pointer at appropriate offset in parent CTentacle
5. If allocation fails, store NULL at the offset

## Related Files

- Warspite.cpp - Naval AI (CWarspite__Init called from CreateWarspiteAI)
- MCTentacle.cpp - Motion controller (debug path at 0x0062e06c)
- Unit.cpp - Base unit class

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
