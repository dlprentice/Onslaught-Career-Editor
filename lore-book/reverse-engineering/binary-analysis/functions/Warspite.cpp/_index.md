# Warspite.cpp Functions

> Source File: Warspite.cpp | Binary: BEA.exe
> Debug Path: 0x0063d12c

## Overview

Naval AI controller implementation. CWarspite manages battleship/capital ship AI behavior including pathfinding (waypoints) and combat engagement. Named after HMS Warspite.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00504460 | CWarspite__Create (TODO) | Factory - allocate and init CWarspite | ~100 bytes |
| 0x004fe710 | CWarspite__Init (TODO) | Initialize AI state machine | ~500 bytes |
| 0x00504510 | CWarspite__Destructor (TODO) | Cleanup resources | ~100 bytes |
| 0x004fef40 | CWarspite__Update (TODO) | Main AI tick - movement, combat | ~600 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d5770 | Unwind@005d5770 | 10 | Cleanup for 96-byte allocation |

## Key Observations

- **Pool ID 0x16** - Uses memory pool 22, object size 96 bytes (0x60)
- **State machine** - Event-driven with 3 modes:
  - Fighting (event 0x7d3/2003)
  - Waypoint following (event 0xbb9/3001)
  - Custom target (event 0xbba/3002)
- **Ship oscillation** - Random parameters for visual bobbing effect
- **VTable at 0x005dfbdc** - CWarspite virtual function table

## AI State Machine

| State Index | Mode | Event | Notes |
|-------------|------|-------|-------|
| -1 | Idle | - | Default state |
| 0 | Fighting | 0x7d3 | Combat engagement, 3000ms delay |
| 1 | Waypoint | 0xbb9 | Navigation mode |
| 2 | Target | 0xbba | Custom target, 10s timeout |

## Debug Strings

- `"%s CANT start fighting cos it already was !!!"`
- `"%s CANT start following waypoints cos it already was !!!"`

## CWarspite Object Layout (96 bytes)

| Offset | Field | Notes |
|--------|-------|-------|
| 0x00 | vtable | Virtual function table |
| 0x08 | mParent | Parent battle engine |
| 0x20 | mStateIndex | Current AI state (-1, 0, 1, 2) |
| 0x44 | mTimeoutTime | Timeout timestamp |
| 0x48-0x5C | mOscillation[6] | Ship oscillation params |

## Related Files

- Unit.cpp - Base unit class
- BattleEngine.cpp - Combat system

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
