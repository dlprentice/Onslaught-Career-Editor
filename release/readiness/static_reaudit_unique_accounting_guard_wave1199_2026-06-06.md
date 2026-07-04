# Static Re-Audit Unique Accounting Guard Wave1199 Readiness Note

Status: active unique-address accounting guard
Last updated: 2026-06-06
Scope: `static-reaudit-unique-accounting-guard-wave1199`

Wave1199 accounting anchor: `wave1199-gillm-groundunit-ai-motion-effects-current-risk-review` uses the `wave1108-current-risk-rank` current-risk denominator, focused threshold `15`, and unique-address accounting. The corrected active current-risk value is `870/1179 = 73.79%`; remaining active focused work: 309. The legacy additive counter is deprecated (`901/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; not Wave911 reconstruction.

This guard defines the measurable paths for static re-audit progress and prevents anti-churn failures where old wave prose, duplicate-address rows, context rows, or arithmetic mistakes become the active percentage.

## Current Boundary

- Static closure remains `6411/6411 = 100.00%` with debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`.
- Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.
- Active accounting mode: unique-address accounting.
- Active current-risk progress after Wave1199: `870/1179 = 73.79%`.
- Remaining active focused work: `309`.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.

## Authoritative Paths

| Measurement | Authority |
| --- | --- |
| Static function-quality closure | `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json` |
| Active current-risk progress | `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json` |
| Published progress baton | `reverse-engineering/binary-analysis/static-reaudit-progress.json` |
| Live risk-ranked candidates | `subagents/ghidra-static-reaudit/wave1108-current-risk-rank/wave1108-current-focused-candidates.tsv` |
| System map dashboard | `reverse-engineering/binary-analysis/mapped-systems.md` |
| Campaign history | `reverse-engineering/binary-analysis/static-reaudit-campaign.md` |
| Probe gate | `tools/static_reaudit_accounting_guard.py --check` |

## Guarded Corrections

| Issue | Guarded treatment |
| --- | --- |
| Legacy additive counter | Deprecated; after Wave1199 it would read `901/1179`, but it is not the active percentage. |
| Duplicate-address waves | Corrected by `static-reaudit-current-risk-ledger.json`; current duplicate-address overcount is 26 duplicate-address overcount. |
| Wave1145 arithmetic jump | Corrected as Wave1145 arithmetic overcount: 5. |
| Wave1139 boundary recovery | `0x004074d0 CBattleEngine__Gravity` was a function-boundary recovery and is not counted as a Wave1108 denominator row. |
| Wave1192 context row | `0x004daff0 FearGridTrackedObject__LookupFearWeightByArchetype` was a context row and is not counted as a Wave1108 denominator row. |
| Wave911 focused percentage | Retained only as historical-retired/non-reconstructable provenance: `812/1408 = 57.67%`; not Wave911 reconstruction. |

## Boundary

This is no Ghidra export, no Ghidra mutation, no executable-byte change, no BEA launch, no save mutation, and no installed-game/runtime-file mutation. Runtime behavior, exact layouts, patching behavior, gameplay outcomes, visual QA, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1199; wave1199-gillm-groundunit-ai-motion-effects-current-risk-review; 870/1179 = 73.79%; 10 GillM/GillMHead/shared ground-unit AI/motion/effects score16-19 current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 309; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=10 skipped=0; comment_only_updated=10; tags_added=129; final dry updated=0 skipped=10; no rename; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; legacy additive counter is deprecated; 901/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0; CGillMHeadAI__AdvanceOpenAttackCloseState; CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730; CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0; CGillM__InitGillMAIComponent; CGillMAI__ScalarDeletingDestructor; CGillM__InitTerrainGuideComponent; CGillM__UpdateGroundedVerticalDrift; CGillM__TriggerRandomArmHitAnimationIfReady; CGillM__StartState1WithStoredMotionVector; 0 / 0 / 0; 6411/6411 = 100.00%; 13 xref rows; 540 instruction rows; 10 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence.
