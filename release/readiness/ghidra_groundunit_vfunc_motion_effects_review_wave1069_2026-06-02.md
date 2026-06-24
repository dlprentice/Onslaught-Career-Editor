# Ghidra GroundUnit VFunc Motion Effects Review Wave1069 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `groundunit-vfunc-motion-effects-review-wave1069`

Wave1069 re-read eight existing CMCMech, CMCMine, shared GroundUnit, CMine, and CPod vfunc rows without Ghidra mutation. The pass made no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0` | CMCMech vtable `0x005dc3b4` slot `5`; calls `CMCMech__Reset` on one state path and writes an interpolated/cached value to `out_value`. |
| `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440` | CMCMine vtable `0x005dc3f4` slot `4`; owner-height interpolation path uses owner fields `+0x250/+0x254`. |
| `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820` | Shared GroundUnit slot `9`; calls `CGroundUnit__Init`, dispatches slots `117/118/119`, and resolves a named child through `CDestroyableSegment__FindChildByNameI`. |
| `0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10` | Shared GroundUnit slot `66`; called by `CGillM__UpdateGroundedVerticalDrift` and `ProjectileBurstCallerBoundary_004f4920`, optionally creates pickup state, and calls `CGroundUnit__UpdateLinkedEffectsByHeightClearance`. |
| `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` | Shared GroundUnit slot `71`; vtables `0x005e0684`, `0x005e3074`, `0x005e0fe0`, and `0x005e0b30` point here; body searches `Generic Mesh` and anchors mesh break effects through `CMCMech__BuildInterpolatedPoseAndAnchor`. |
| `0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward` | CMine vtable `0x005e1b84` slot `2`; clears linked particle/effect state through `ParticleEffectLink__SetHandleStateAndClear` and forwards to `VFuncSlot_02_004f95d0`. |
| `0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4` | CMine vtable `0x005e1b84` slot `50`; calls `CGroundUnit__MarkDestroyedAndResetState` then dispatches vfunc `+0x1d4` on success. |
| `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar` | CPod vtable `0x005dff8c` slot `66`; calls `CUnit__UpdateMotionAttachmentsAndEffects`, dispatches vfunc `+0xb4`, and accumulates the returned scalar into `this+0x84`. |

Read-back evidence:

- Primary exports: `8` metadata rows, `8` tag rows, `22` xref rows, `498` instruction rows, and `8` decompile rows.
- Caller exports: `3` metadata rows, `362` instruction rows, and `3` decompile rows for `0x004799c0 CGillM__VFunc09_InitGroundedSpawnState`, `0x00479d10 CGillM__UpdateGroundedVerticalDrift`, and `0x004f4920 ProjectileBurstCallerBoundary_004f4920`.
- Raw context metadata intentionally verified `13` no-function addresses around the motion-controller/ground-unit neighborhood.
- Vtable export verified `1024` rows across `0x005dc3b4`, `0x005dc3f4`, `0x005e0684`, `0x005e3074`, `0x005e0fe0`, `0x005e0b30`, `0x005e1b84`, and `0x005dff8c`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1266/1560 = 81.15%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The current saved Ghidra names, signatures, comments, and tags for the eight primary rows remain internally coherent with fresh metadata, xref, instruction, decompile, and vtable evidence.
- The selected shared GroundUnit rows are intentionally owner-conservative because multiple concrete vtable tables point at the same bodies.
- The selected CMCMech/CMCMine/CMine/CPod rows remain bounded by retail vtable/data xrefs and local decompile evidence.

What remains separate proof:

- Runtime grounded-unit, mine, pod, pickup, mesh-break, particle/effect cleanup, and motion behavior.
- Exact virtual method identities.
- Exact concrete layouts.
- Exact source identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1069; groundunit-vfunc-motion-effects-review-wave1069; 0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0; 0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440; 0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820; 0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10; 0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0; 0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward; 0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4; 0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar; 812/1408 = 57.67%; 1266/1560 = 81.15%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified; read-only review.
