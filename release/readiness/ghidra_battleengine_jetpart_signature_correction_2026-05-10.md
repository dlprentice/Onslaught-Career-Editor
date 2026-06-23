# Ghidra BattleEngineJetPart Signature Correction - 2026-05-10

## Scope

This note records a saved Ghidra source-parity correction tranche for nine `CBattleEngineJetPart` functions. It is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpt is included here.

## Saved Targets

| Address | Previous saved name | Current saved name | Saved signature boundary |
| --- | --- | --- | --- |
| `0x00410210` | `CBattleEngine__InitTargetSetBucketState` | `CBattleEngineJetPart__ctor` | `void * __thiscall ...(void * this, void * mainPart)` |
| `0x004102a0` | `CBattleEngine__DestroySPtrSetElementsAndClear` | `CBattleEngineJetPart__dtor_base` | `void __thiscall ...(void * this)` |
| `0x00410310` | `CGeneralVolume__HandleBoostWindowInput` | `CBattleEngineJetPart__Thrust` | `void __thiscall ...(void * this, float moveY)` |
| `0x00410490` | `CGeneralVolume__ApplyInputDampingToVelocity` | `CBattleEngineJetPart__Turn` | `void __thiscall ...(void * this, float moveX)` |
| `0x00410670` | `CGeneralVolume__DrainLinkedObjectFromVelocity` | `CBattleEngineJetPart__Pitch` | `void __thiscall ...(void * this, float moveY)` |
| `0x00410740` | `CGeneralVolume__HandleAxisPositiveThresholdCross` | `CBattleEngineJetPart__YawLeft` | `void __thiscall ...(void * this, float moveX)` |
| `0x004109d0` | `CGeneralVolume__HandleAxisNegativeThresholdCross` | `CBattleEngineJetPart__YawRight` | `void __thiscall ...(void * this, float moveX)` |
| `0x004114d0` | `CGeneralVolume__GetFlagFCScalar` | `CBattleEngineJetPart__Gravity` | `float __thiscall ...(void * this)` |
| `0x00411500` | `CMonitor__ApplyHostileEnvironmentPenalty` | `CBattleEngineJetPart__HandleSkimming` | `void __thiscall ...(void * this)` |

## Evidence Summary

- Headless dry/apply saved nine corrected names/signatures/comments with dry `updated=0 skipped=9 missing=0 bad=0` and apply `updated=9 skipped=0 missing=0 bad=0`.
- Final metadata and decompile read-back found `9/9` targets.
- Final xref export produced `11` xref rows across the targets.
- Final instruction export produced `1989` instruction rows across the targets.
- The focused probe reports `9` targets, `0` stale old-name hits, `0` stale signature hits, `0` comment overclaims, and return-shape evidence for the stack-argument helpers.
- The correction aligns the selected retail functions with Stuart-source `CBattleEngineJetPart` constructor/destructor, thrust, turn, pitch, yaw-left, yaw-right, gravity, and skimming behavior.
- Post-signature decompile review records remaining local decompiler artifacts for `0x00410490`, `0x00410670`, and `0x00411500`; those are follow-up local/type cleanup work, not a reason to keep the old owner labels.

## Boundary

This tranche improves saved Ghidra names/signatures/comments only. It does not prove runtime jet input, gravity, skimming, hostile-environment behavior, concrete `CBattleEngineJetPart` or `CBattleEngine` layouts, structure types, tags, local names, BEA launch behavior, game patching, or rebuild parity.
