# CAirUnit__Init

> Address: 0x00402ad0 | Source: AirUnit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Initialize an air unit by calling the base CUnit constructor and creating aircraft-specific visual effects. Creates "Trail" effects (exhaust contrails) and "Engine" effects (thrust particles) in two separate loops.

## Signature
```c
void __thiscall CAirUnit__Init(void * this, int param_1);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Responsibilities

- **Base class init** - Calls CUnit__Init(param_1) first
- **Trail effects loop** - Creates visual trail effects (line 42)
- **Engine effects loop** - Creates engine glow/thrust effects (line 54)
- **Memory allocation** - Uses OID__AllocObject with debug info
- **Effect registration** - Calls FUN_004cb040, `CSPtrSet__AddToTail` (`0x004e5b20`), CSPtrSet__AddToHead

## Key Observations

- **Two effect types** - "Trail" and "Engine" strings at 0x00622d14 and 0x00622cec
- **Config at 0x3bc** - Reads effect data from configuration offset
- **Exception safe** - Unwind handlers for both effect loops
- **~600 bytes** - Moderately sized function

## Decompiled Pseudocode

```c
void CAirUnit::Init(int param_1) {
    // Call base class constructor
    CUnit__Init(param_1);

    // Initialize air unit-specific properties from config
    void* config = this->config_3bc;

    // First loop: Create Trail effects (line 42)
    for each trail_effect in config->trails {
        void* effect = MemAlloc(size, type, "AirUnit.cpp", 42);
        FUN_004cb040(effect);      // Initialize effect
        CSPtrSet__AddToTail(effect); // Register effect (set pointer is in ECX)
    }

    // Second loop: Create Engine effects (line 54)
    for each engine_effect in config->engines {
        void* effect = MemAlloc(size, type, "AirUnit.cpp", 54);
        FUN_004cb040(effect);      // Initialize effect
        CSPtrSet__AddToHead(effect);      // Final setup
    }
}
```

## Notes

- Discovered via xref to debug path string at 0x00622cf4
- Trail effects create visible exhaust trails behind aircraft
- Engine effects create thrust glow and particle emissions
- Consider finding vtable xrefs to discover more CAirUnit methods

## Related Functions

- [CUnit__Init](../Unit.cpp/CUnit__Init.md) - Base class initialization
- FUN_004cb040 - Effect/particle system initialization
- CSPtrSet__AddToTail - Effect registration (set insert)
- CSPtrSet__AddToHead - Final effect setup
- OID__FreeObject_Callback - Exception cleanup/deallocation

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
