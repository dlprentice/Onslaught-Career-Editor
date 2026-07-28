# CInfantryUnit__Init

> Source File: `Infantry.cpp` — named by the debug-path string at `0x0062d4a8`, not present in the `references/Onslaught/` snapshot | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x00488bb0`
> Status: name corrected 2026-07-28
> Last updated: 2026-07-28
> The **filename** is retained at the withdrawn name so historical links resolve.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).

| Address | Superseded label | Current name | Correction |
| --- | --- | --- | --- |
| `0x00488bb0` | `CInfantry__Init` | `CInfantryUnit__Init` | class prefix moved; suffix unchanged |

Only the class prefix moved, so nothing below about allocation sizes, offsets,
flags or the heading calculation is affected. Two other places carried the
withdrawn label and now read the current one: the H1 and the saved signature.
The pseudocode block still spells the class `CInfantry::` because it is a
transcript of the decompiler's output at the time it was taken, not an assertion
about the current database.

---

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave416 headless postscript + read-back verified, 2026-05-14)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Initialize an infantry unit by allocating three child component objects and configuring movement parameters. Infantry are foot soldiers with smaller scale and angle-based heading.

## Signature
```c
void __thiscall CInfantryUnit__Init(void * this, void * infantryInit);
```

Saved metadata, decompile, xref, tag, and instruction exports support this boundary.

## Responsibilities

- **First allocation** - Allocates 0x38 byte object (type 0xb) at line 28
- **Second allocation** - Allocates 0x48 byte object (type 0x17) at line 70
- **Third allocation** - Allocates 0x60 byte object (type 0x16) at line 71
- **State flags** - Sets this+0x80 to 1, this+0x70 to 0x2000010
- **Scale factor** - Sets this+0x260 to 4.0f (or 1.0f with special flag)
- **Velocity init** - Zeros velocity fields at this+0x4c, this+0x48
- **Heading calc** - Uses fpatan() to compute initial facing direction
- **Position read** - Gets spawn position from parent object at offset 0x3bc

## Key Observations

- **Three component objects** - More complex than Carrier (2 objects)
- **Smaller scale** - Infantry rendered at 4.0f scale factor
- **Angle-based movement** - Uses atan2 for heading from X/Y components
- **VTable references** - 0x5dbf48 and 0x5dbf14
- **Exception safe** - Three unwind handlers for each allocation
- **~1000 bytes** - Larger function than typical Init

## Decompiled Pseudocode

```c
void CInfantry::Init(int param_1) {
    this->state_80 = 1;
    this->flags_70 = 0x2000010;
    this->velocity_4c = 0;
    this->velocity_48 = 0;

    // Scale factor (4.0f default, 1.0f if special)
    if (special_flag) {
        this->scale_260 = 1.0f;
    } else {
        this->scale_260 = 4.0f;  // 0x40800000
    }

    // Calculate heading from spawn position
    float x = parent->pos_3bc.x;
    float y = parent->pos_3bc.y;
    this->heading = fpatan(y, x);

    // Allocate components (lines 28, 70, 71)
    this->component_e = MemAlloc(0x38, 0xb, "Infantry.cpp", 28);
    this->component_82 = MemAlloc(0x48, 0x17, "Infantry.cpp", 70);
    this->component_4f = MemAlloc(0x60, 0x16, "Infantry.cpp", 71);
}
```

## Notes

- Discovered via xref to debug path string at 0x0062d4a8
- Infantry kills tracked at TK_INFANTY (index 3) - thresholds 40/80/160 (no standalone 120-based goodie in this build)
- Wave416 corrected the adjacent InfantryAI and collision-seeking helper lifecycle labels; runtime infantry/collision behavior and concrete layouts remain unproven.
- Parent object at 0x3bc likely holds spawn/level data

## Related Functions

- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization
- [CUnit__ApplyDamage](../Unit.cpp/CUnit__ApplyDamage.md) - Infantry damage handling

---
*Discovered via Phase 1 xref analysis (Dec 2025); signature refreshed by Wave416 static read-back (2026-05-14).*
