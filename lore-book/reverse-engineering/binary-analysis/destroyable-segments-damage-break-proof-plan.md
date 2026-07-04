# Destroyable Segments Damage/Break Proof Plan

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: destroyable-segments damage/break planning from the saved static contract

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the PhysicsScript copied-corpus parser/census proof. It converts the static `destroyable-segments-static-contract.md` evidence into a bounded gameplay-contract proof plan with explicit event/layout unknowns, copied-profile guardrails, and stop conditions. It does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, start Godot work, or claim runtime destruction behavior or rebuild parity.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract source: `reverse-engineering/binary-analysis/destroyable-segments-static-contract.md`.

Relevant retained evidence:

- Wave1205 current-risk review (`wave1205-destroyable-segment-current-risk-review`): `5` destroyable-segment rows, `9` xref rows, `96` instruction rows, and `5` decompile rows, with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified`.
- Wave1157 vfunc current-risk review for variant/vtable dispatch context.
- Wave1133 feature/pickup bridge review for `0x00442710 CDestroyableSegment__SpawnConfiguredPickup` and `CWorldPhysicsManager__CreatePickup` linkage.
- Wave1067 controller lookup/damage review for controller threshold/callback state.
- Wave1065 component break owner-callback context for component vtable anchors.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence, not source-body identity. Stuart source-body parity for this subsystem remains unproven.

| Surface | Static anchor |
| --- | --- |
| Child registration | `0x00442700 CDestructableSegment__RegisterChild` adds child segments to the parent child `CSPtrSet` at `this+0x24`. |
| Core-child gate | `0x004433f0 CDestroyableCoreSegment__AreCoreChildrenDestroyed` walks the core child list, preserves the missing-first-child warning path, and returns false while checked child state remains active. |
| Indexed controller damage | `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` is the controller entry for indexed segment damage and threshold/callback state. |
| Base damage | `0x00442960 CDestroyableSegment__VFunc_03_ApplyDamage` subtracts damage from `this+0x0c`, records last damage amount/time in `this+0x18` and `this+0x14`, and clamps depleted state. |
| Core damage | `0x004435f0 CDestroyableCoreSegment__VFunc_03_ApplyDamage` handles core/primary damage, ignores ordinal 1, records damage/time, then dispatches break/rubble slots when depleted. |
| Swap damage | `0x00443780 CDestroyableSwapSegment__VFunc_03_ApplyDamage` compares damage-stage state before/after damage and runs swap/rubble and child-destruction side effects on transition. |
| Base break | `0x00442b20 CDestroyableSegment__VFunc_08_HandleSegmentBreak` marks broken, clears damage state, updates controller/link state, and dispatches child destruction. |
| Swap break | `0x00443810 CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak` runs one-shot swap/rubble side effects while `this+0x44` is clear, then delegates to the base break handler. |
| Parent gate | `0x004435c0 CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate` checks core `+0x4c` and parent `+0x20` before parent slot `+0x18`. |
| Damage telemetry | `0x004442d0` and `0x00444300` expose indexed last-damage time and last-damage amount fields to CUnit-facing callers. |
| Bulk active refresh | `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric` writes the active flag across controller segments and refreshes cached metric `this+0x18` from the root segment. |
| Rubble/effect bridge | `0x00442f60 CDestroyableSegment__VFunc_10_SpawnRubbleEffects` resolves rubble/mesh/effect context, derives spawn count from `this+0x34`, applies landscape damage, and can reach the pickup bridge. |
| Pickup bridge | `0x00442710 CDestroyableSegment__SpawnConfiguredPickup` reaches `CWorldPhysicsManager__CreatePickup` through controller/config context and config field `+0xe8`. |
| End-segment rubble | `0x00443a20 CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects` adds end-segment setup before the base rubble path. |
| Swap damage stage | `0x00443830 CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex` derives a clamped stage index from `+0x0c`, `+0x10`, and `+0x40`. |

## Static Field Roles To Preserve

These are static role labels for proof planning. Do not promote them to final C++ field names until exact layout proof exists.

| Offset / input | Planned role in later proof |
| --- | --- |
| `this+0x0c` | Current damage/health-scale state. |
| `this+0x10` | Total/reference damage-scale state. |
| `this+0x14` | Last damage time or global tick snapshot from `DAT_00672fd0`. |
| `this+0x18` | Last raw damage amount. |
| `this+0x20` | Parent segment pointer for parent-gate checks. |
| `this+0x24` | Child `CSPtrSet` head. |
| `this+0x34` | Segment value/scale input for scale/rubble count paths. |
| `this+0x3c` | Controller/config context for pickup and end-segment scale paths. |
| `scaleFactor`, `divisor` | Slot-11 damage-scale recompute inputs. |

## Future Proof Checklist

The first executable proof after this plan should be scoped and copied-profile only. This plan records the expected evidence shape; it does not run that proof.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Candidate scene/object selection | Identify one copied-profile level/object pair that exercises a small destroyable segment without broad Unit/BattleEngine proof. | Sanitized candidate name/level class, or a deferred note if no safe candidate is selected. |
| 2 | Static-to-runtime arm point | Choose one static anchor for a non-invasive observation point, preferably damage telemetry getters or controller damage entry. | VA/function anchor and why it is scoped. |
| 3 | Event trigger design | Define a reversible way to cause one damage/break attempt in a copied profile. | Input/patch/debugger plan only; no installed-game mutation. |
| 4 | Telemetry fields | Observe `+0x14`, `+0x18`, break flag/state, and child/core gate transitions only when later runtime proof is explicitly started. | Aggregate before/after field changes, not raw memory dumps in public docs. |
| 5 | Rubble/pickup boundary | Treat rubble, landscape damage, pickup spawning, and visual effects as separate subclaims unless directly observed. | Separate pass/fail rows for each side effect. |
| 6 | Layout restraint | Keep offsets as static role labels until runtime/layout evidence proves concrete fields. | Unknown-layout table remains explicit. |
| 7 | Stop conditions | Stop on crash, non-reproducible target, ambiguous object identity, unexpected file mutation, or any need to touch the installed game. | Documented blocked/deferred status instead of widening scope. |
| 8 | Rebuild handoff | Translate proven static-only behavior into pseudocode only after the future proof result says which rows were observed. | Static pseudocode with runtime gaps marked. |

## Copied-Profile Guardrails

Any later runtime/proof execution must:

- Use copied profiles or app-owned artifact roots only.
- Never mutate the installed Steam game directory or the original `BEA.exe`.
- Verify byte/specimen assumptions before any patch candidate is even considered.
- Keep screenshots, frames, memory dumps, logs, and patch outputs out of public release scope unless separately sanitized.
- Keep raw CDB/debugger output and private file paths in ignored evidence.
- Use a single selected object/level target; do not broaden into full Unit/BattleEngine damage, weapon, targeting, or render proof.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

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

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `reverse-engineering/binary-analysis/destroyable-segments-static-contract.md` points to this plan without changing its static claim boundary.
- `release/readiness/destroyable_segments_damage_break_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/destroyable_segments_damage_break_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
