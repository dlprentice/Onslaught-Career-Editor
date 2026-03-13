# CThunderHead__CreateLegMotion

> Address: 0x004f4730 | Size: ~256 bytes | Source: ThunderHead.cpp line 32 (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Creates and initializes the leg motion animation system for the ThunderHead mech. Loads the `"LegMotion"` asset and configures walking animation parameters; stores the resulting controller at `this+0x70`.

## Signature

```c
void __thiscall CThunderHead__CreateLegMotion(void * this, void * param_1);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Summary

Creates and initializes the leg motion animation system for the ThunderHead mech. Loads the "LegMotion" asset and configures walking animation parameters. Stores the result at `this+0x70`.

## Decompiled Code

```c
void __thiscall CThunderHead__CreateLegMotion(CThunderHead *this, int param_1)
{
    int animIndex;
    void *legMotion;

    // Call virtual method to register "LegMotion" animation
    (*this->mController->vtable->RegisterAnimation)(this->mController, "LegMotion");

    // Look up animation index
    animIndex = FindAnimationIndex("LegMotion");

    if (animIndex != -1) {
        // Allocate leg motion struct (240 bytes, pool ID 0x1b)
        legMotion = MemoryManager_Alloc(0xf0, 0x1b, "ThunderHead.cpp", 0x20);

        if (legMotion != NULL) {
            // Initialize leg motion with parent reference
            CLegMotion_Init(legMotion, this + 8);  // this+8 is CUnit base
            legMotion->vtable = &CLegMotion_vtable;
        }

        this->mLegMotion = legMotion;

        // Configure animation parameters from position data
        int posData = *(param_1 + 0x3bc);
        SetAnimationParams(
            *(posData + 0x144),  // X position
            *(posData + 0x148),  // Y position
            *(posData + 0x14c),  // Z position
            3.4f,                // 0x4059999a - speed/scale
            0.99f,               // 0x3f7d70a4 - blend factor
            *(posData + 0x150),  // W rotation
            *(posData + 0x140)   // Additional param
        );
    } else {
        this->mLegMotion = NULL;
    }
}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CThunderHead* | ThunderHead instance |
| param_1 | int | Pointer to parent structure containing position data at +0x3bc |

## Key Constants

| Value | Meaning |
|-------|---------|
| 0xf0 (240) | Leg motion struct size |
| 0x1b (27) | Memory pool ID for leg motion |
| 0x20 (32) | Source line number |
| 0x4059999a | Float 3.4 - animation speed/scale |
| 0x3f7d70a4 | Float 0.99 - blend factor |

## Called Functions

| Address | Name | Purpose |
|---------|------|---------|
| Virtual+0x24 | RegisterAnimation | Registers animation by name |
| 0x004aa630 | FindAnimationIndex | Looks up animation index by name |
| 0x005490e0 | MemoryManager_Alloc | Allocates memory from pool |
| 0x004983b0 | CLegMotion_Init | Initializes leg motion struct |
| 0x00498bf0 | SetAnimationParams | Configures animation parameters |

## Object Field Written

- `this+0x70`: Pointer to allocated CLegMotion struct (or NULL if animation not found)

## Notes

- Uses same "LegMotion" asset as player mech (see CMech__InitLegMotion)
- Animation lookup failure is graceful - stores NULL instead of crashing
- The 3.4f and 0.99f constants suggest animation blending parameters
- Position data read from param_1+0x3bc appears to be spawn/initial position

---
*Discovered via Ghidra xref analysis (Dec 2025)*
