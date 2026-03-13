# Cannon.cpp Functions

> Source File: Cannon.cpp | Binary: BEA.exe
> Debug Path: 0x00623dd4

## Overview

Cannon weapon/turret implementation. CCannon handles stationary weapon systems with activation states, firing conditions, and visual states.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x0041b1a0 | CCannon__Init | Initialize cannon with state/effects | ~450 bytes |
| 0x0041b370 | CCannon__UpdateState (TODO) | Update activation state based on conditions | ~220 bytes |
| 0x0041b450 | CCannon__Destructor (TODO) | Cleanup cannon resources | ~30 bytes |
| 0x0041b470 | CCannon__SetState (TODO) | Process animation state transitions | ~200 bytes |
| 0x0041b540 | CCannon__GetMidpoint (TODO) | Calculate cannon center position | ~80 bytes |
| 0x0041b590 | CCannon__CanFire (TODO) | Check if cannon can fire | ~50 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d1760 | Unwind@005d1760 | 34 | Cleanup for 32-byte allocation |
| 0x005d1776 | Unwind@005d1776 | 35 | Cleanup for 96-byte allocation |
| 0x005d178c | Unwind@005d178c | 38 | Cleanup for 20-byte allocation |

## State Machine

CCannon uses a 4-state machine for activation:

| Value | State | Description |
|-------|-------|-------------|
| 0 | Active | Cannon is operational and can fire |
| 1 | Inactive | Cannon is disabled |
| 2 | Deactivating | Transitioning to inactive (10s timeout) |
| 3 | Activating | Transitioning to active |

**State Strings:**
- `"Active"` at 0x00623e00
- `"Inactive"` at 0x00623e08
- `"Activate"` at 0x00623e14
- `"Deactivate"` at 0x00623e20

## Key Observations

- **VTable at 0x005e24fc** - CCannon virtual function table
- **State at offset 0x260** - Current state (0-3)
- **Timestamp at offset 0x264** - Last state change time
- **Fire controller at 0x208** - Controls weapon firing
- **10.0 second timeout** - Deactivation delay

## Class Structure (Partial)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0x00 | 4 | vtable | CCannon vtable pointer |
| 0x08 | 4 | pAnimController | Animation controller |
| 0x1c-0x24 | 12 | boundMin | Min bounding box (float[3]) |
| 0x70 | 4 | flags | Various flags |
| 0x13c | 4 | pTarget | Target/linked object |
| 0x208 | 4 | mFireController | Fire controller |
| 0x214 | 4 | mIsEnabled | Enable flag |
| 0x260 | 4 | mState | Current state (0-3) |
| 0x264 | 4 | mLastStateChangeTime | Timestamp |

## Related Files

- Unit.cpp - Base unit class
- BattleEngine.cpp - Weapon firing system

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
