# CEngine__ClampBurstStartTimeFloorNow

> Address: `0x0040f110` | Source family: `engine.cpp` / burst-progress helper cluster

## Status

- Named in Ghidra: yes
- Saved signature: `void __thiscall CEngine__ClampBurstStartTimeFloorNow(void * this)`
- Fresh read-back: `release/readiness/ghidra_battleengine_transition_config_signature_correction_2026-05-10.md`
- Runtime behavior proof: not yet

## Summary

Small timestamp helper that clamps a burst/progress timestamp field at `this+0x60c` up to the current event-time global when the stored value plus a small floor constant is behind now.

## Evidence

- Decompile and instruction read-back show the `this+0x60c` float load, comparison against `DAT_00672fd0`, and conditional store back to `this+0x60c`.
- Current xrefs come from burst/progress processing helpers.
- Saved signature uses a `this` pointer and removes the old generic `param_1` signature.

## Boundaries

- Does not prove exact source identity for the owner cluster.
- Does not prove concrete owner layout, tags, local variable names, or structure types.
- Does not prove runtime burst behavior.
- Does not mutate `BEA.exe`.
