# CThunderHead__CreateWarspite

> Address: 0x004f4830 | Size: ~112 bytes | Source: ThunderHead.cpp line 43 (source file not present in `references/Onslaught/` snapshot)

## Summary

Creates a CWarspite AI controller for the ThunderHead mech's combat behavior. The Warspite system handles state machine AI including fighting, waypoint following, and target acquisition. Stores the result at `this+0x13c`.

## Decompiled Code

```c
void __thiscall CThunderHead__CreateWarspite(CThunderHead *this, undefined4 param_1)
{
    int warspite;

    // Allocate Warspite struct (96 bytes, pool ID 0x16)
    warspite = MemoryManager_Alloc(0x60, 0x16, "ThunderHead.cpp", 0x2b);

    if (warspite != 0) {
        // Initialize Warspite AI controller
        warspite = CWarspite__Init(this, param_1);
    } else {
        warspite = 0;
    }

    this->mWarspite = warspite;
}
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| this (ECX) | CThunderHead* | ThunderHead instance |
| param_1 | undefined4 | Configuration/parent parameter passed to CWarspite__Init |

## Key Constants

| Value | Meaning |
|-------|---------|
| 0x60 (96) | Warspite struct size |
| 0x16 (22) | Memory pool ID for Warspite |
| 0x2b (43) | Source line number |

## Called Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x005490e0 | MemoryManager_Alloc | Allocates memory from pool |
| 0x004fe710 | CWarspite__Init | Initializes AI controller state machine |

## Object Field Written

- `this+0x13c`: Pointer to allocated CWarspite struct (or NULL if allocation failed)

## Notes

- CWarspite is a reusable AI controller also used by naval units
- The AI state machine supports:
  - Fighting mode (combat engagement)
  - Waypoint following (navigation)
  - Custom target acquisition
- See Warspite.cpp documentation for full AI state machine details
- Pool ID 0x16 matches Warspite allocations elsewhere in codebase

---
*Discovered via Ghidra xref analysis (Dec 2025)*
