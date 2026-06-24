# Destroyable Segments Damage/Break Proof Plan Readiness Note

Status: gameplay-contract proof plan complete, not runtime proof
Date: 2026-06-08
Scope: destroyable-segments damage/break planning from `destroyable-segments-static-contract.md`

The destroyable-segments damage/break slice adds a public-safe proof plan at `reverse-engineering/binary-analysis/destroyable-segments-damage-break-proof-plan.md`. This is not a new static re-audit wave, not a Ghidra mutation, not a runtime test, not a BEA patch, and not a rebuild parity claim.

Static closeout remains unchanged:

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |

Remaining active focused work: `0`.
Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

Static anchors retained for the proof plan:

- `destroyable-segments-static-contract.md` and Wave1205 `wave1205-destroyable-segment-current-risk-review`.
- Wave1205 evidence: `5` destroyable-segment rows, `9` xref rows, `96` instruction rows, `5` decompile rows, and verified backup `G:\GhidraBackups\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified`.
- `0x00442700 CDestructableSegment__RegisterChild`.
- `0x004433f0 CDestroyableCoreSegment__AreCoreChildrenDestroyed`.
- `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`.
- `0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage`.
- `0x004435f0 CDestroyableCoreSegment__VFunc_03_ApplyDamage`.
- `0x00443780 CDestroyableSwapSegment__VFunc_03_ApplyDamage`.
- `0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak`.
- `0x00443810 CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak`.
- `0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects`.
- `0x00442710 CDestroyableSegment__SpawnConfiguredPickup`.
- Damage telemetry getters `0x004442d0` and `0x00444300`.
- Bulk active refresh `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric`.

What this proves:

- The project has a bounded gameplay-contract proof plan for turning the saved destroyable-segments static contract into a later copied-profile proof slice.
- The plan separates child/core registration, controller damage dispatch, damage telemetry, break handlers, rubble/effect bridge, pickup bridge, field-role unknowns, and stop conditions.
- The plan preserves copied-profile/app-owned guardrails before any later runtime proof, patch candidate, screenshot, memory dump, or rebuild handoff.
- The static percentages and current-risk ledgers are unchanged by this planning slice.

What remains separate proof:

- Runtime destroyable-segment damage behavior.
- Runtime break/rubble/cascade/pickup behavior.
- Runtime landscape damage or visual effects.
- Exact event payload schema.
- Exact concrete C++ layouts or field names.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

No broad Unit/BattleEngine runtime proof, runtime destruction behavior, BEA patching behavior, visual QA, rebuild parity, or no-noticeable-difference parity claim.
