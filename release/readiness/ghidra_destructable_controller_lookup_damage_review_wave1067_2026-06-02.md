# Ghidra Destructable Controller Lookup/Damage Review Wave1067 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-02
Scope: `destructable-controller-lookup-damage-review-wave1067`

Wave1067 re-read sixteen existing `CDestructableSegmentsController__*` lookup, damage, health, cascade, and name-dispatch rows plus twenty adjacent segment/controller/unit context rows. Fresh exports confirmed the existing saved names, signatures, comments, and tags remain coherent with the static retail decompile, instructions, xrefs, and caller context, so the wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

Primary anchors:

| Address | Static evidence |
| --- | --- |
| `0x00443fc0 CDestructableSegmentsController__Ctor` | Called from `0x0047fe99 CHiveBoss__Init`; constructor-like initializer stores caller-provided values and clears segment/root/threshold state. |
| `0x00444000 CDestructableSegmentsController__Dtor` | Called from `0x004f977f CUnit__VFunc02_CleanupWorldLinksAndForward`; frees owned segment array and root segment when present. |
| `0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` | Called from `0x004f9ddc CUnit__ApplyDamage`; indexed segment damage path with threshold/callback update evidence. |
| `0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold` | Called from `0x004f943e CUnit__ApplyRandomDestructibleDamageBurst`; deduplicated random-damage burst pass and shared threshold update logic. |
| `0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex` | Called twice by `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter`; returns tracked segment field `+0x14` or fallback constant. |
| `0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex` | Called by `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter`; returns tracked segment field `+0x18` or zero. |
| `0x00444330 CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive` | Called from `0x004f99fc CUnit__GetCurrentHealthOrSubtreeHealth`; delegates to root active-value sum when any tracked segment is active. |
| `0x00444370 CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive` | Called from `0x004f9a53 CUnit__GetRootSubtreeHealthIfAnyActive`; delegates to root total-health query when any tracked segment is active. |
| `0x004443b0 CDestructableSegmentsController__GetCachedTotalHealthIfAnyActive` | Called from the adjacent CUnit health query path at `0x004f9a1c`; returns cached total-health field when active segments exist. |
| `0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible` | Called from `0x004fd1dc CUnit__MarkDestroyedAndCleanupLinks`; checks root/core child state and can activate/propagate a cascade. |
| `0x00444450 CDestructableSegmentsController__SetSegmentField0CByName` | Called from script/name-dispatch wrapper context at `0x005354b1`; resolves mesh child name and writes segment field `+0x0c`. |
| `0x004444b0 CDestructableSegmentsController__SetSegmentFields0C10ByName` | Called from wrapper context at `0x005354f1`; writes segment fields `+0x0c/+0x10` and refreshes cached active-value metric. |
| `0x00444520 CDestructableSegmentsController__FindSegmentByName` | Called from `0x0047feff CHiveBoss__Init`; resolves a named mesh child to the tracked segment pointer. |
| `0x00444580 CDestructableSegmentsController__SetAllSegmentsField0C` | Called from wrapper context at `0x00535525`; bulk-writes segment field `+0x0c`. |
| `0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName` | Called from wrapper context at `0x00534333`; resolves by name, writes active flag `+0x1c`, and refreshes cached metric. |
| `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric` | Called from wrapper context at `0x005343b7`; bulk-writes active flags and refreshes cached metric. |

Context anchors:

- `0x004425a0 CDestructableSegment__Init`
- `0x00442660 CDestroyableSegment__dtor_base`
- `0x00442710 CDestroyableSegment__SpawnConfiguredPickup`
- `0x00442870 CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields`
- `0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage`
- `0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak`
- `0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects`
- `0x00443460 CDestroyableSegment__VFunc_00_HandleEvent3000Dispatch`
- `0x004436d0 CDestroyableCoreSegment__VFunc_00_HandleEvent3000And3002Dispatch`
- `0x00443890 CDestroyableSegmentVariant__VFunc_03_ApplyDamage`
- `0x00443ea0 CDestroyableSegmentComponent__VFunc_08_HandleComponentBreak`
- `0x00444660 CDestructableSegmentsController__Init`
- `0x004449c0 CDestructableSegmentsController__CreateSegment`
- `0x00444c10 CDestructableSegmentsController__ProcessNode`
- `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter`
- `0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren`
- `0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren`

Read-back evidence:

- Primary exports: `16` metadata rows, `16` tag rows, `17` xref rows, `590` function-body instruction rows, and `16` decompile rows.
- Context exports: `20` metadata rows, `20` tag rows, `142` xref rows, `1757` function-body instruction rows, and `20` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1248/1560 = 80.00%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The sixteen primary destructable-controller lookup/damage/health/name-dispatch rows exist in the saved Ghidra project with expected names, signatures, comments, and existing static-reaudit tags.
- The exported instructions, decompile rows, xrefs, and context rows remain coherent with the existing static mapping from Wave349/Wave350/Wave351 and later re-audit context.
- The review records this cluster in the Wave900+ continuation evidence set without adding new Ghidra mutations.

What remains unproven:

- Runtime destructable-controller damage, random burst, cascade, health-meter, name-dispatch, or segment activation behavior.
- Exact concrete controller, segment, mesh-node, active-reader, or CUnit layouts.
- Exact script wrapper source/body identity for the name-dispatch callers.
- Exact source-body identity beyond static source-aligned mapping evidence.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1067; destructable-controller-lookup-damage-review-wave1067; 0x00443fc0 CDestructableSegmentsController__Ctor; 0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold; 0x00444160 CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold; 0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; 0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x004443f0 CDestructableSegmentsController__TriggerCoreCascadeIfEligible; 0x00444450 CDestructableSegmentsController__SetSegmentField0CByName; 0x00444520 CDestructableSegmentsController__FindSegmentByName; 0x004445b0 CDestructableSegmentsController__SetSegmentActiveFlagByName; 0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 812/1408 = 57.67%; 1248/1560 = 80.00%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-003225_post_wave1067_destructable_controller_lookup_damage_review_verified; read-only review.
