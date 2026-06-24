# Ghidra Destroyable Segment VFunc Review Wave1065 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-01
Scope: `destroyable-segment-vfunc-review-wave1065`

Wave1065 re-read the existing destructable-segments vtable/vfunc surface around damage, break, rubble/effect, event-dispatch, core, swap, end, and component segment handlers. Fresh exports confirmed the saved Wave348-Wave353 names, signatures, comments, tags, function boundaries, and vtable DATA xrefs remain coherent, so the wave made no Ghidra mutation.

The pass made no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

Primary anchors:

| Address | Static evidence |
| --- | --- |
| `0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields` | Four DATA vtable refs at `0x005db058`, `0x005db0d8`, `0x005db140`, and `0x005db174`; body writes fields `+0x0c/+0x10` from `this+0x34`, `scaleFactor`, and `divisor`. |
| `0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage` | DATA vtable ref `0x005db038`; subtracts `damageAmount` from `+0x0c`, records damage/time at `+0x18/+0x14`, and clamps below-zero health to zero. |
| `0x00442b00 CDestroyableSegment__VFunc_06_CheckParentBreakGate` | Five DATA vtable refs; follows parent at `+0x20`, checks parent `+0x38`, and jumps through parent vtable slot `+0x18` when eligible. |
| `0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak` | DATA vtable ref `0x005db04c` plus direct calls from core/swap/shared break helpers; marks the segment broken, clears `+0x0c`, updates controller/link state, and dispatches child destruction events. |
| `0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects` | Four DATA vtable refs plus direct call from the end-segment rubble helper; resolves Generic Mesh/rubble context, applies landscape damage, and can call `CDestroyableSegment__SpawnConfiguredPickup`. |
| `0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch` | Five DATA vtable refs at base/component/end/leaf/standard vtables; checks event code `3000`/`0x0bb8` and dispatches vfunc slot `+0x20`. |
| `0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch` | DATA vtable ref `0x005db06c`; handles event `3000` and `3002`/`0x0bba`, accumulates core fields, and can schedule/dispatch break handling. |
| `0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage` | DATA vtable refs `0x005db0ec` and `0x005db120`; shared leaf/end damage-style body records damage context and dispatches slot `+0x20` when newly broken. |
| `0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak` | DATA vtable ref `0x005db0cc`; component break helper marks component state and invokes owner callback at `owner+0xc8` slot `+0x40`. |

Context anchors:

- `0x004425a0 CDestructableSegment__Init`
- `0x00442660 CDestroyableSegment__dtor_base`
- `0x00442710 CDestroyableSegment__SpawnConfiguredPickup`
- `0x00442d40 CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09`
- `0x004433f0 CDestroyableCoreSegment__AreCoreChildrenDestroyed`
- `0x00443fc0 CDestructableSegmentsController__Ctor`
- `0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`
- `0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible`
- `0x00444660 CDestructableSegmentsController__Init`
- `0x004449c0 CDestructableSegmentsController__CreateSegment`
- `0x00444c10 CDestructableSegmentsController__ProcessNode`

Read-back evidence:

- Primary exports: `20` metadata rows, `20` tag rows, `41` xref rows, `1253` function-body instruction rows, and `20` decompile rows.
- Context exports: `38` metadata rows, `38` tag rows, `73` xref rows, `1948` function-body instruction rows, and `38` decompile rows.
- No `LockException`, missing, bad, failed, or unresolved rows were observed in the Wave1065 export logs.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1219/1560 = 78.14%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The fifty-eight target/context rows exist in the saved Ghidra project with expected names and signatures.
- The twenty primary destroyable-segment vfunc rows retain coherent static evidence across metadata, tags, vtable DATA refs, direct helper calls, instruction bodies, and decompile comments.
- The Wave348-Wave353 destructable-segment vtable/function-boundary evidence still fits the current saved database after the post-100 re-audit expansion.

What remains unproven:

- Runtime destructable-segment damage, break, cascade, pickup, rubble, or component behavior.
- Exact event payload schema.
- Exact concrete segment/controller/component layouts.
- Exact source-body identity; `DestructableSegmentsController.cpp` remains missing from the current Stuart-source CSV.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1065; destroyable-segment-vfunc-review-wave1065; 0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields; 0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage; 0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak; 0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects; 0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch; 0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch; 0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage; 0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak; 812/1408 = 57.67%; 1219/1560 = 78.14%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-232711_post_wave1065_destroyable_segment_vfunc_review_verified; no mutation.
