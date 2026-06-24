# CMech__InitTargeting

> Address: 0x0049faa0 | Source: Mech.cpp (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave436 headless apply/read-back, 2026-05-16)
- **Verified vs Source:** Partial static evidence only; the allocation path cites `C:\dev\ONSLAUGHT2\Mech.cpp` line `0x4e`, but the matching source body is not present in the current reference snapshot.

## Purpose

Saved static evidence shows this slot initializes a `CMechGuide` targeting/guide component. It allocates a `0x48` object, calls `CMechGuide__ctor` with `this`, and stores the resulting pointer at `this+0x208`.

## Signature

```c
void __fastcall CMech__InitTargeting(void * this);
```

The function has no stack cleanup and is represented as register-only in the saved Ghidra signature.

## Observed Behavior

- Vtable tables `0x005e0684` and `0x005e3074` both point slot `119` here.
- Allocates `0x48` bytes from pool `0x17` with Mech.cpp line evidence `0x4e`.
- Calls `CMechGuide__ctor(allocated_object, this, ...)` when allocation succeeds.
- Stores the resulting pointer at `this+0x208`.

## Not Proven

Runtime targeting, reticle, guide, or lock-on behavior is not proven by this wave. Exact component semantics, concrete layout, destructor ownership, source-body identity, local variable names/types, and rebuild parity remain unproven.

## Related Functions

- [CMech__InitLegMotion](./CMech__InitLegMotion.md)
- [CMech__InitCockpit](./CMech__InitCockpit.md)
- [../GroundUnit.cpp/_index.md](../GroundUnit.cpp/_index.md) - shared slot-9 caller invokes vtable slots 117/118/119
