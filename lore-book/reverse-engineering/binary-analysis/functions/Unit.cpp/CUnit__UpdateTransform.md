# CUnit__UpdateTransform

> Address: 0x004fc4e0 | Source: Unit.cpp (source file not present in `references/Onslaught/` snapshot)

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes, Wave524
- **Verified vs Source:** No matching source body located in the current `references/Onslaught/` snapshot

## Current Purpose

Emitter-transform/cache output helper. Wave524 corrected the older docs that described this function as general movement, terrain, collision, and animation synchronization. The saved retail body instead resolves or creates a cached emitter transform entry keyed by `emitter_slot_tag` and `cache_key`, maps slot tags through `CUnit__FindEmitterIndexBySlotTag`, and writes output transform buffers.

## Signature

```c
void __thiscall CUnit__UpdateTransform(
    void *this,
    int emitter_slot_tag,
    int cache_key,
    void *out_position4,
    void *out_basis3x4);
```

## Evidence

- `RET 0x10` proves four explicit stack arguments after ECX.
- Decompile read-back shows output writes to `out_position4` and `out_basis3x4`.
- The helper calls `CUnit__FindEmitterIndexBySlotTag` for slot/name resolution.
- Xrefs include `CUnitAI__UpdateActivationStateAndSpawnPickup`; most other references are vtable/data slots.

## Boundaries

This is saved static Ghidra evidence only. Exact cache-entry layout, emitter slot enum names, runtime effect/attachment behavior, concrete types, local names, and rebuild parity remain unproven.

## Related Functions

- `CUnit__FindEmitterIndexBySlotTag` (`0x004fc6e0`) - maps slot tags to attachment names and forwards through the mesh/profile lookup vfunc.
- `CUnit__SpawnComponentEffectsRecursive` (`0x004fc220`) - creates component/effect particle outputs and copies transform/basis context into spawned renderers.
