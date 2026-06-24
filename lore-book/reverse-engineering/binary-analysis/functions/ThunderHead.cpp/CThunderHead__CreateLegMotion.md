# CThunderHead__CreateLegMotion

> Address: 0x004f4730 | Size: ~256 bytes | Source: ThunderHead.cpp line 32 (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave519 headless postscript + read-back verified, 2026-05-18)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Creates and initializes the leg motion animation system for the ThunderHead mech. Loads the `"LegMotion"` asset and configures walking animation parameters; stores the resulting controller at `this+0x70`.

## Signature

```c
void __thiscall CThunderHead__CreateLegMotion(void * this, void * init_context);
```

Read-back verified in `subagents/ghidra-static-reaudit/wave519-thunderhead-004f4730/post_metadata.tsv` (`status=OK`).

## Wave519 Read-Back

`CThunderHead` vtable `0x005e11b0` slot 1 points here. The body looks up `"LegMotion"` through the object at `this+0x30`, allocates a `0xf0`-byte motion-controller object from pool `0x1b`, calls `CMCMech__Constructor`, installs the `0x005df890` CMCMech-family vtable, stores the controller at `this+0x70`, and calls `CMCMech__SetParams` with fields from `init_context+0x3bc` plus constants `3.4` and `0.99`.

## Summary

Creates and initializes the leg motion animation system for the ThunderHead mech. Loads the "LegMotion" asset and configures walking animation parameters. Stores the result at `this+0x70`.

## Decompiled Code

```c
void __thiscall CThunderHead__CreateLegMotion(CThunderHead *this, void *init_context)
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
        int posData = *(init_context + 0x3bc);
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
| init_context | void * | Context pointer containing the parameter block pointer at +0x3bc |

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
| Virtual+0x24 | Mesh/controller getter | Returns object used for animation-name lookup |
| 0x004aa630 | CMesh__FindAnimationIndexByName | Looks up animation index by name |
| OID__AllocObject | OID__AllocObject | Allocates memory from pool |
| 0x004983b0 | CMCMech__Constructor | Initializes the motion-controller object |
| 0x00498bf0 | CMCMech__SetParams | Configures motion parameters |

## Object Field Written

- `this+0x70`: Pointer to allocated CLegMotion struct (or NULL if animation not found)

## Notes

- Uses same "LegMotion" asset as player mech (see CMech__InitLegMotion)
- Animation lookup failure is graceful - stores NULL instead of crashing
- The 3.4f and 0.99f constants suggest animation blending parameters
- Position data read through `init_context+0x3bc` appears to be spawn/initial motion parameters

## Claim Boundary

Static retail evidence only. Runtime leg-motion behavior, concrete ThunderHead/init-context/controller layouts, exact source-body identity, BEA patching, and rebuild parity remain unproven.

---
*Discovered via Ghidra xref analysis (Dec 2025)*
