# Ghidra Early Queue Signature Correction - 2026-05-10

## Summary

Wave 309 completed a saved Ghidra signature/comment correction tranche for `9` early static re-audit queue targets.

The tranche hardened already named early helpers and corrected the particle-manager jump thunk split: `0x00405d80` is now the thunk `CParticleManager__RemoveFromGlobalList_Thunk`, while `0x004cb050` carries the target-body name `CParticleManager__RemoveFromGlobalList`.

## Corrected Targets

| Address | Saved signature |
| --- | --- |
| `0x00402dd0` | `int __thiscall ShadowHeightfield__AnyBoundsCornerAboveSampledHeight(void * this)` |
| `0x00403ff0` | `void __thiscall CDXLandscape__DestroyResourceDescriptorArray_Thunk(void * this)` |
| `0x00404dd0` | `void __thiscall CBattleEngine__Init(void * this, void * init)` |
| `0x00405930` | `int __thiscall CControllerDefinition__VFunc_03_00405930(void * this)` |
| `0x004059a0` | `int __thiscall CCylinder__VFunc_01_004059a0(void * this, void * forwardedA, void * forwardedB, void * dispatchObject, void * forwardedC)` |
| `0x00405d80` | `void __fastcall CParticleManager__RemoveFromGlobalList_Thunk(void * node)` |
| `0x00405db0` | `void __thiscall VFuncSlot_12_00405db0(void * this, void * arg1, void * arg2)` |
| `0x00406da0` | `void * __thiscall CBattleEngine__SelectNearestForwardTargetFromGlobalSet(void * this, void * profile, float originX, float originY, float originZ, float originW, float rangeScale)` |
| `0x004cb050` | `void __fastcall CParticleManager__RemoveFromGlobalList(void * node)` |

## Validation

- Headless correction dry run: `updated=0 skipped=9 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=9 skipped=0 renamed=1 missing=0 bad=0`.
- Metadata read-back: `9/9` targets found.
- Decompile read-back: `9/9` targets dumped.
- Xref read-back: `1088` rows.
- Instruction read-back: `2255` rows.
- Focused probe: `PASS targets=9 renamed=1 failures=0`.
- Whole-database queue snapshot: `5868` functions, `599` commented functions, `5269` commentless functions, `2066` undefined signatures, and `2366` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove exact source identities, concrete structures, tags, local variables, runtime shadow/render/control/cylinder/particle/targeting behavior, runtime cloak activation, fire-while-cloaked behavior, exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, BEA launch behavior, game patching, or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.
