# CMech__InitCockpit

> Address: 0x0049fa30 | Source: Mech.cpp (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave436 headless apply/read-back, 2026-05-16)
- **Verified vs Source:** Partial static evidence only; the allocation path cites `[maintainer-local-source-export-root]\Mech.cpp` line `0x48`, but the matching source body is not present in the current reference snapshot.

## Purpose

Saved static evidence shows this vtable slot initializes a `CMechAI` component. It allocates a `0x64` object, calls `CMechAI__ctor` with `this` and the one stack initialization argument, and stores the returned pointer at `this+0x13c`.

## Signature

```c
void __thiscall CMech__InitCockpit(void * this, void * init_context);
```

`RET 0x4` confirms one stack argument after `this`.

## Observed Behavior

- Vtable `0x005e3074` slot `118` points here.
- Allocates `0x64` bytes from pool `0x16` with Mech.cpp line evidence `0x48`.
- Calls `CMechAI__ctor(allocated_object, this, init_context, ...)` when allocation succeeds.
- Stores the resulting pointer at `this+0x13c`.

## Not Proven

The historical cockpit/camera interpretation is not runtime-proven by this wave. Exact cockpit/AI semantics, concrete layout, destructor ownership, source-body identity, local variable names/types, and rebuild parity remain unproven.

## Related Functions

- [CMech__InitLegMotion](./CMech__InitLegMotion.md)
- [CMech__InitTargeting](./CMech__InitTargeting.md)
- [Shared grounded-motion initialization](../GroundUnit.cpp/SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820.md) - shared slot-9 caller context
