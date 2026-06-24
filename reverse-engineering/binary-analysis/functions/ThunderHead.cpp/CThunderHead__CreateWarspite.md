# CThunderHead__CreateWarspite

> Address: 0x004f4830 | Size: ~112 bytes | Source: ThunderHead.cpp line 43 (source file not present in `references/Onslaught/` snapshot)

## Summary

Creates a CWarspite AI controller for the ThunderHead mech's combat behavior. The Warspite system handles state machine AI including fighting, waypoint following, and target acquisition. Stores the result at `this+0x13c`.

## Status

- **Signature Set:** Yes (Wave519 headless postscript + read-back verified, 2026-05-18)
- **Evidence Grade:** Static retail Ghidra evidence only

## Signature

```c
void __thiscall CThunderHead__CreateWarspite(void * this, void * init_context);
```

## Wave519 Read-Back

`CThunderHead` vtable `0x005e11b0` slot 2 points here. Instruction read-back confirms `RET 0x4`, so the saved signature has `this` plus one explicit `init_context` argument. The body allocates a `0x60`-byte pool-`0x16` Warspite-style component from the `ThunderHead.cpp` line `0x2b` debug path, calls `CWarspite__Init`, and stores the returned component or NULL at `this+0x13c`.

## Decompiled Code

```c
void __thiscall CThunderHead__CreateWarspite(CThunderHead *this, void *init_context)
{
    int warspite;

    // Allocate Warspite struct (96 bytes, pool ID 0x16)
    warspite = MemoryManager_Alloc(0x60, 0x16, "ThunderHead.cpp", 0x2b);

    if (warspite != 0) {
        // Initialize Warspite AI controller
        warspite = CWarspite__Init(this, init_context);
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
| init_context | void * | Context/configuration pointer passed through to `CWarspite__Init` |

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

## Claim Boundary

Static retail evidence only. Exact Warspite semantics, concrete ThunderHead/Warspite layouts, runtime combat AI behavior, BEA patching, and rebuild parity remain unproven.

---
*Discovered via Ghidra xref analysis (Dec 2025)*
