# Unit Targeting / Active-Reader Proof Plan

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0044e640` → `CFenrirMainGunAI__ScanListsAndSelectSupportTarget` (was `CSquadNormalReader__ScanListsAndSelectSupportTarget_0044e640`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: Unit/BattleEngine targeting and active-reader planning from the saved static contract

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the HUD/frontend overlay proof-plan slice. It converts the static `unit-battleengine-gameplay-static-contract.md` targeting evidence into a bounded proof plan for target acquisition, candidate filtering/scoring, active-reader assignment, heading update, and iterator snapshot behavior. It does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, start Godot work, or claim runtime targeting behavior, squad AI behavior, component behavior, exact layouts, gameplay outcomes, or rebuild parity.

The plan records copied-profile guardrails, candidate-list/reader layout unknowns, and stop conditions before any runtime/proof work can start.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract source: `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md`.

Relevant retained evidence:

- Wave1215 unit-targeting combat residual review (`wave1215-unit-targeting-combat-residual-current-risk-review`): `5` primary targeting rows, `6` xref rows, `794` instruction rows, `5` decompile rows, `425` context xref rows, `1123` context instruction rows, `15` context decompile rows, and `1` data-slot xref row, with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified`.
- Wave927 CUnit active-reader targeting review (`cunit-active-reader-targeting-review-wave927`): `5` active-reader targeting rows, `23` xref rows, `464` instruction rows, and `5` decompile rows, plus context helper `CUnit__ForwardAimTransformAndAttachTargetReader`, with verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`.
- Unit/BattleEngine gameplay static contract anchors for `CUnit`, `CUnitAI`, `CGenericActiveReader`, `CSquadNormal`, and component-targeting rows.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence, not source-body identity. Stuart source labels are useful for planning, but exact source-body identity and concrete layouts remain unproven unless a later proof slice establishes them.

| Surface | Static anchor |
| --- | --- |
| Air-guide target acquisition | `0x004027c0 CAirGuide__AcquireNearestTargetReader` clears reader `+0x2c`, scans mapwho near the owner, excludes owner/flagged entries, and selects the nearest threshold candidate. |
| Dive-bomber target output | `0x00445070 CDiveBomber__SelectTarget` walks the `+0x15c/+0x160` target list, resolves candidate records through `this+4` and `candidate+0x88`, picks highest priority `record+0x40`, or falls back through `CThing__GetCentrePos`. |
| Component targeting boundary | `0x0044e640 ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640` has DATA xref `0x005d96ac`, scans list heads selected by object state, compares range/position against owner at `this+0x08`, and conditionally dispatches `0x004ffdd0`. |
| Normal-squad target scoring | `0x00477cb0 CSquadNormal__SelectBestEngagementTarget` has call xref `0x004e815a`, chooses among `DAT_00855090`, `DAT_008550b0`, and `DAT_008550c0`, then scores candidates with config weights at `squad+0xa0`. |
| Relaxed-squad iterator snapshot | `0x004ea8d0 CRelaxedSquad__CreateIterator` has DATA xref `0x005e3b10`, allocates a `0x10`-byte `CSPtrSet`, walks member nodes at `this+0xa4`, and snapshots non-null members with `CSPtrSet__AddToHead`. |
| Active-reader assignment | `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw` stores the active reader at `this+0x26c`, context at `this+0x270`, relative yaw at `this+0x274`, and mirrors flag `0x100000`. |
| Heading readback | `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset` returns active-reader heading `+0x114` plus relative-yaw offset `this+0x274`, or a zero-heading fallback when no reader exists. |
| Heading update/clamp | `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped` has DATA slot xref `0x005d9660` and loads the UnitAI pointer from `turnContext+0x18` before heading/clamp logic. |
| Formation reader swap | `0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser` compares current and candidate formation offsets before swapping reader cells through `CGenericActiveReader__SetReader`. |
| Side/team compatibility | `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting` gates candidate side/team values through `this+0x138` plus profile field `this+0x164 -> +0x128`. |
| Aim/reader forwarder | `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` null-gates `this+0x140` before forwarding to `OID__UpdateAimTransformAndAttachTargetReader`. |

## Static Field Roles To Preserve

These are static role labels for proof planning. Do not promote them to final C++ field names until exact layout proof exists.

| Offset / slot | Planned role in later proof |
| --- | --- |
| `CAirGuide +0x2c` | Target-reader cell cleared before candidate acquisition. |
| `CDiveBomber +0x15c/+0x160` | Candidate/target list traversal state. |
| `candidate +0x88` | Candidate record pointer used by dive-bomber target selection. |
| `record +0x40` | Candidate priority/score field used by dive-bomber target selection. |
| `component this+0x08` | Owner/context pointer used by component-targeting range checks. |
| `squad +0x7c` | Squad state selector for global target-list choice. |
| `squad +0xa0` | Squad config/weight context used by engagement scoring. |
| `relaxed squad +0xa4` | Member list head for relaxed-squad iterator snapshots. |
| `CUnit +0x26c/+0x270/+0x274` | Active reader, reader context, and relative yaw cache. |
| `CUnitAI turnContext+0x18` | UnitAI pointer slot used by heading update/clamp logic. |
| `CUnit +0x138` and `CUnit +0x164 -> +0x128` | Side/team/profile compatibility inputs. |

## Future Proof Checklist

The first executable proof after this plan should be scoped and copied-profile only. This plan records the expected evidence shape; it does not run that proof.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- | --- |
| 1 | Candidate scenario selection | Identify one copied-profile level/state where a single unit/squad target-selection path can be observed without broad combat proof. | Sanitized level/state description, or a deferred note if no safe candidate is selected. |
| 2 | Static-to-runtime arm points | Choose one or two non-invasive observation anchors, preferably `CSquadNormal__SelectBestEngagementTarget`, `CUnit__SetReaderAndComputeRelativeYaw`, or `CUnitAI__UpdateHeadingTowardTargetClamped`. | VA/function anchor and why it is scoped. |
| 3 | Target-list input boundary | Record which candidate-list family is being observed, without claiming exact list layout until later layout proof exists. | Candidate family label and static role, not raw private memory dumps. |
| 4 | Reader assignment / heading update | Observe whether a selected candidate leads to active-reader assignment and heading update only in a later runtime slice. | Separate planned pass/fail rows for selection, assignment, and heading update. |
| 5 | Component/squad separation | Keep component targeting, squad scoring, air guide, dive bomber, and relaxed-squad iterator snapshots as separable subclaims. | One result row per subclaim, not one broad AI targeting claim. |
| 6 | Layout restraint | Keep offsets as static role labels until runtime/layout evidence proves concrete fields. | Unknown-layout table remains explicit. |
| 7 | Stop conditions | Stop on crash, non-reproducible target, ambiguous unit/squad identity, unstable candidate list, unexpected file mutation, private artifact leakage, or any need to touch the installed game. | Documented blocked/deferred status instead of widening scope. |
| 8 | Rebuild handoff | Translate proven static-only behavior into target-selection pseudocode only after the future proof result says which rows were observed. | Static pseudocode with runtime and layout gaps marked. |

## Copied-Profile Guardrails

Any later runtime/proof execution must:

- Use copied profiles or app-owned artifact roots only.
- Never mutate the installed Steam game directory or the original `BEA.exe`.
- Verify byte/specimen assumptions before any patch candidate is considered.
- Keep screenshots, frames, videos, memory dumps, debugger logs, and patch outputs out of public release scope unless separately sanitized.
- Keep raw CDB/debugger output and private file paths in ignored evidence.
- Use a single selected unit/squad/state target; do not broaden into weapon fire, damage, collision, morph/mode switching, cloak/stealth, full squad AI behavior, or full Unit/BattleEngine runtime proof.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime targeting behavior.
- Runtime squad AI behavior.
- Runtime component behavior.
- Runtime air-guide or dive-bomber behavior.
- Runtime target-list contents or target-list ordering.
- Runtime active-reader lifetime or ownership behavior.
- Runtime heading/steering outcomes.
- Weapon fire, projectile, damage, collision, morph/mode, cloak, or stealth behavior.
- Exact concrete `CUnit`, `CUnitAI`, `CAirGuide`, `CDiveBomber`, `CSquadNormal`, `CRelaxedSquad`, component-targeting, candidate-list, active-reader, or profile layouts.
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
- `reverse-engineering/binary-analysis/unit-battleengine-gameplay-static-contract.md` points to this plan without changing its static claim boundary.
- `release/readiness/unit_targeting_active_reader_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/unit_targeting_active_reader_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
