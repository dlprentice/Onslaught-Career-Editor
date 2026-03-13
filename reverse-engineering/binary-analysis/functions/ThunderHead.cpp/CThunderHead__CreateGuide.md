# CThunderHead__CreateGuide

> Address: 0x004f48a0 | Size: ~96 bytes | Source: ThunderHead.cpp line 49 (source file not present in `references/Onslaught/` snapshot)

## Summary

Creates a guidance/targeting system for the ThunderHead mech. This system likely handles weapon targeting and aim assistance. Stores the result at `this+0x208`.

## Decompiled Code

```c
void __thiscall CThunderHead__CreateGuide(CThunderHead *this)
{
    int guide;

    // Allocate guide struct (48 bytes, pool ID 0x17)
    guide = MemoryManager_Alloc(0x30, 0x17, "ThunderHead.cpp", 0x31);

    if (guide != 0) {
        // Initialize guide with position data from this
        guide = CThunderheadGuide_Init(
            this,
            this->field_0x1c,  // X position?
            this->field_0x20,  // Y position?
            this->field_0x24,  // Z position?
            this->field_0x28   // Rotation?
        );
    } else {
        guide = 0;
    }

    this->mGuide = guide;
}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CThunderHead* | ThunderHead instance |

## Key Constants

| Value | Meaning |
|-------|---------|
| 0x30 (48) | Guide struct size |
| 0x17 (23) | Memory pool ID for guide |
| 0x31 (49) | Source line number |

## Called Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x005490e0 | MemoryManager_Alloc | Allocates memory from pool |
| 0x004f4e00 | CThunderheadGuide_Init | Initializes guidance system |

## Object Fields Read

| Offset | Purpose |
|--------|---------|
| 0x1c | Position X / guidance parameter 1 |
| 0x20 | Position Y / guidance parameter 2 |
| 0x24 | Position Z / guidance parameter 3 |
| 0x28 | Rotation / guidance parameter 4 |

## Object Field Written

- `this+0x208`: Pointer to allocated CThunderheadGuide struct (or NULL if allocation failed)

## Notes

- CThunderheadGuide is a class specific to ThunderHead (see RTTI at 0x00633288)
- The guide system takes position/rotation parameters, suggesting it tracks aim direction
- Smallest of the three subsystems at 48 bytes
- Likely used for:
  - Weapon aim prediction
  - Target leading (for slow projectiles)
  - Guidance for "Thunderhead Main Gun" and "Thunderhead Flamethrower"

## Related Strings

- `"CThunderheadGuide"` class RTTI at 0x00633288
- `"Thunderhead Main Gun"` at 0x006247e0
- `"Thunderhead Flamethrower"` at 0x00633264

---
*Discovered via Ghidra xref analysis (Dec 2025)*
