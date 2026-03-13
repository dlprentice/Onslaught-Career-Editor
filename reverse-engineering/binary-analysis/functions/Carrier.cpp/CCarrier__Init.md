# CCarrier__Init

> Address: 0x00421a80 | Source: Carrier.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Initialize a carrier object by allocating and configuring two child component objects. The carrier appears to be a transport vessel or aircraft carrier that holds other units.

## Signature
```c
void __thiscall CCarrier__Init(void * this, int param_1);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Responsibilities

- **First allocation** - Allocates 0x20 byte object (type 0x17) at line 26
- **First vtable** - Sets vtable pointer to 0x005d940c
- **Store first child** - Saves pointer at this+0x208
- **Second allocation** - Allocates 0x60 byte object (type 0x16) at line 27
- **Second vtable** - Sets vtable pointer to 0x005d93d4
- **Store second child** - Saves pointer at this+0x13c
- **State flags** - Sets flags at this+0x7c, this+0x80
- **Flag OR** - ORs this+0x70 with 0xa100100

## Key Observations

- **Two component objects** - 0x20 and 0x60 byte allocations
- **Different vtables** - Each child has its own virtual method table
- **Exception safe** - Unwind handlers at 0x005d1840 and 0x005d1856
- **Called via FUN_0044d6f0** - Likely BattleEngine menu/UI initialization
- **Thiscall convention** - ECX = this pointer

## Decompiled Pseudocode

```c
void CCarrier::Init(int param_1) {
    this->flags_7c = ...;
    this->flags_80 = ...;
    this->flags_70 |= 0xa100100;

    // First child allocation (line 26)
    void* child1 = MemAlloc(0x20, 0x17, "Carrier.cpp", 26);
    if (child1 != NULL) {
        FUN_0047e290(this);
        *(DWORD*)child1 = 0x005d940c;  // vtable
    }
    this->component_208 = child1;

    // Second child allocation (line 27)
    void* child2 = MemAlloc(0x60, 0x16, "Carrier.cpp", 27);
    if (child2 != NULL) {
        FUN_004fe710(this, param_1);
        *(DWORD*)child2 = 0x005d93d4;  // vtable
        this->component_13c = child2;
    }
}
```

## Notes

- Discovered via xref to debug path string at 0x006243bc
- FUN_0047e290 and FUN_004fe710 are component initialization helpers
- Carrier likely holds units/aircraft in game (aircraft carrier mechanics)
- Consider finding vtable xrefs to discover more CCarrier methods

## Related Functions

- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization
- [CBattleEngine__Init](../BattleEngine.cpp/CBattleEngine__Init.md) - Calls carrier init

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
