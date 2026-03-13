# Dropship.cpp Functions

> Source File: Dropship.cpp | Binary: BEA.exe
> Debug Path: 0x00628a54

## Overview

Dropship transport unit implementation. CDropship handles transport aircraft with thruster effects, landing states, and deployment mechanics.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x00446d70 | CDropship__Init (TODO) | Initialize dropship with thrusters/state | ~700 bytes |
| 0x004b7ab0 | CDropship__SelectPortraitIndex | Chooses portrait slot/text pairing for queued dropship dialog target | ~180 bytes |
| 0x004b7b60 | CDropship__RequestQueueAdvance | Sets queue-advance flag and immediately triggers queue processing | ~20 bytes |
| 0x004b7b80 | CDropship__TryAdvanceQueuedPortrait | Validates/prunes queued portrait entries, promotes next target, and schedules follow-up event | ~380 bytes |

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d22e0 | Unwind@005d22e0 | 44 | Cleanup type 0x1b (20 bytes) |
| 0x005d22f6 | Unwind@005d22f6 | 45 | Cleanup type 0x17 (32 bytes) |
| 0x005d230c | Unwind@005d230c | 46 | Cleanup type 0x16 (100 bytes) |
| 0x005d2322 | Unwind@005d2322 | 55 | Cleanup type 0x10 (8 bytes, thrusters) |

## Key Observations

- **Inherits CAirUnit** - Calls CAirUnit__Init during initialization
- **Thruster system** - Dynamically creates thrusters from "Thruster" attachment points
- **Two animation states** - "wingflat" (landed) and "doorclosed" (flying)
- **"Thruster Dust Effect"** - Loads particle effect for thruster visuals
- **VTable at 0x005e1dfc** - CDropship virtual function table

## Memory Allocations in Init

| Line | Size | Type ID | Purpose |
|------|------|---------|---------|
| 44 | 20 bytes | 0x1b | Component at this[0x1c] |
| 45 | 32 bytes | 0x17 | Component at this[0x82], vtable 0x005db228 |
| 46 | 100 bytes | 0x16 | Component at this[0x4f], vtable 0x005db1f4 |
| 55 | 8 bytes | 0x10 | Thruster objects (multiple) |

## Animation States

| State | Animation | Condition |
|-------|-----------|-----------|
| 0 | "wingflat" | Below height threshold |
| 6 | "doorclosed" | Above height threshold |

## String References

| Address | String | Purpose |
|---------|--------|---------|
| 0x00628a74 | "wingflat" | Wings-down animation |
| 0x00628a80 | "doorclosed" | Doors-closed animation |
| 0x00623080 | "Thruster" | Attachment point name |
| 0x00628a3c | "Thruster Dust Effect" | Particle effect name |

## Class Hierarchy

```
CUnit
  └── CAirUnit
        └── CDropship
```

## Related RTTI Classes

| Address | Class Name |
|---------|------------|
| 0x0063d618 | .?AVCDropship@@ |
| 0x00628a28 | .?AVCDropshipAI@@ |
| 0x00628a08 | .?AVCDropshipGuide@@ |
| 0x00627eb0 | .?AVCDropshipBehaviourType@@ |
| 0x0062dd58 | .?AVCMCDropship@@ |

## Related Files

- AirUnit.cpp - CAirUnit parent class
- Unit.cpp - CUnit base class
- ParticleManager.cpp - Thruster dust effects

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
