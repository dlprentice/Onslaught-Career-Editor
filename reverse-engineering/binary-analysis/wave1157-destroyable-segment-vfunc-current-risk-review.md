# Wave1157 Destroyable Segment VFunc Current-Risk Review

Wave1157 (`wave1157-destroyable-segment-vfunc-current-risk-review`) accounts for `12 destroyable-segment vfunc current-risk rows` from the Wave1108 current focused denominator. It is a fresh Ghidra read-only review with no mutation.

Probe token anchor: Wave1157; wave1157-destroyable-segment-vfunc-current-risk-review; 465/1179 = 39.44%; 12 destroyable-segment vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 714; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 694 instruction rows; CDestroyableSegment__VFunc_03_ApplyDamage; CDestroyableSegment__VFunc_08_HandleSegmentBreak; CDestroyableSegment__VFunc_10_SpawnRubbleEffects; CDestroyableCoreSegment__VFunc_03_ApplyDamage; CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex; CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields; [maintainer-local-ghidra-backup-root]\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

Fresh exports verified `12` metadata rows, `12` tag rows, `23 xref rows`, `694 instruction rows`, and `12` decompile rows. The xrefs include vtable `DATA` refs plus direct break/rubble helper calls. The verified Ghidra project backup is `[maintainer-local-ghidra-backup-root]\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified` from the local Ghidra project root, with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x00442870` | `CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields` | Slot 11 damage-scale helper; DATA refs `0x005db058`, `0x005db0d8`, `0x005db140`, and `0x005db174`; writes fields `+0x0c/+0x10` from `this+0x34`, `scaleFactor`, and `divisor`. |
| `0x00442960` | `CDestroyableSegment__VFunc_03_ApplyDamage` | Base slot 3 damage helper; DATA ref `0x005db038`; subtracts damage from `+0x0c`, records last damage amount/time at `+0x18/+0x14`, and clamps below-zero state to zero. |
| `0x00442b20` | `CDestroyableSegment__VFunc_08_HandleSegmentBreak` | Base slot 8 break handler; DATA ref `0x005db04c`; direct calls from swap/core/shared break paths; marks broken, clears `+0x0c`, updates controller/link state, and dispatches child destruction. |
| `0x00442f60` | `CDestroyableSegment__VFunc_10_SpawnRubbleEffects` | Slot 10 rubble/effects helper; DATA refs `0x005db054`, `0x005db094`, `0x005db13c`, and `0x005db170`; direct call from end-rubble helper; resolves rubble/mesh/effect context, landscape damage, and configured pickup path. |
| `0x004434c0` | `CDestroyableCoreSegment__VFunc_07_GetCoreField48` | Core slot 7 field reader; DATA ref `0x005db088`; returns `this+0x48`. |
| `0x00443590` | `CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields` | Core slot 11 damage-scale helper; DATA ref `0x005db098`; writes `+0x0c/+0x10` unless the `+0x40` special case clears both fields. |
| `0x004435c0` | `CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate` | Core slot 6 parent gate; DATA ref `0x005db084`; checks `+0x4c` and parent `+0x20` before parent slot `+0x18`. |
| `0x004435f0` | `CDestroyableCoreSegment__VFunc_03_ApplyDamage` | Core slot 3 damage helper; DATA ref `0x005db078`; ignores first-core ordinal 1, records damage/time, clamps, then dispatches break/rubble slots when depleted. |
| `0x00443780` | `CDestroyableSwapSegment__VFunc_03_ApplyDamage` | Swap slot 3 damage helper; DATA ref `0x005db154`; samples damage-stage slot `0x10`, records damage/time, dispatches swap/rubble and child-destruction side effects on state transition. |
| `0x00443810` | `CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak` | Swap slot 8 break handler; DATA ref `0x005db168`; runs one-shot swap/rubble side effects while `+0x44` is clear, then delegates to the base break handler. |
| `0x00443830` | `CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex` | Standard/swap slot 4 damage-stage helper; DATA ref `0x005db158`; derives and clamps a stage index from fields `+0x0c`, `+0x10`, and `+0x40`. |
| `0x004439f0` | `CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields` | End slot 11 damage-scale helper; DATA ref `0x005db10c`; special controller component-count path can set `+0x0c` to a small constant, otherwise writes scaled `+0x0c/+0x10`. |

## Boundary

This wave proves fresh static Ghidra read-back coherence for these current-risk destroyable-segment vfunc rows only. Runtime destructable-segment damage, break, cascade, pickup, rubble, component behavior, exact event payload schema, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
