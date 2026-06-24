# Wave1199 GillM/GroundUnit AI-Motion-Effects Current-Risk Review

Wave1199 measured anchor: unique-address accounting governs active current-risk progress. Wave1199 (`wave1199-gillm-groundunit-ai-motion-effects-current-risk-review`) accounts for `10 GillM/GillMHead/shared ground-unit AI/motion/effects score16-19 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0`, `CGillMHeadAI__AdvanceOpenAttackCloseState`, `CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730`, `CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0`, `CGillM__InitGillMAIComponent`, `CGillMAI__ScalarDeletingDestructor`, `CGillM__InitTerrainGuideComponent`, `CGillM__UpdateGroundedVerticalDrift`, `CGillM__TriggerRandomArmHitAnimationIfReady`, and `CGillM__StartState1WithStoredMotionVector`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=129 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=129 missing=0 bad=0`, then final dry updated=0 skipped=10. It made no rename, no signature change, no function-boundary change, and no executable-byte change. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; corrected active current-risk progress is `870/1179 = 73.79%`; the legacy additive counter is deprecated (`901/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 309; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `13 xref rows`, `540 instruction rows`, and `10 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified`. Active measurement files: `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, and `reverse-engineering/binary-analysis/mapped-systems.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Exact source-body identity, concrete CGillM/CGillMHeadAI/shared ground-unit layouts, runtime AI/animation/movement/effects behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Status: complete static read-back evidence; historical artifact committed
Date: 2026-06-06
Tag: `wave1199-gillm-groundunit-ai-motion-effects-current-risk-review`

Wave1199 saved comment/tag normalization for 10 GillM/GillMHead/shared ground-unit AI, motion, and mesh-effect current-risk rows. It made no rename, no signature change, no function-boundary change, and no executable-byte change.

## Measured Result

| Track | Value | Authority |
| --- | ---: | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` | `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` | `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json` |
| Corrected current-risk reviewed rows | `870/1179 = 73.79%` | `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json` |
| Remaining active focused work | `309` | `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json` |
| Live regenerated current focused candidates | `1141` | `subagents/ghidra-static-reaudit/wave1108-current-risk-rank/wave1108-current-focused-candidates.tsv` |

The active accounting mode is unique-address accounting. The legacy additive counter is deprecated: it would have reported `901/1179`, but that includes a 26 duplicate-address overcount plus a Wave1145 arithmetic overcount: 5.

## Targets

| Address | Function | Static contract |
| --- | --- | --- |
| `0x0049fdb0` | `SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0` | Shared ground-unit slot 71 mesh break-effect dispatcher; Generic Mesh child mesh-part scan, pose anchor, and randomized effect velocity. |
| `0x0047a900` | `CGillMHeadAI__AdvanceOpenAttackCloseState` | GillMHeadAI open/attack/close/idle animation-state helper with linked-unit timeout gate before close transition. |
| `0x0047a730` | `CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730` | GillMHeadAI-adjacent vtable forwarder that forwards arg then requests idle animation token `0x0062ca48`. |
| `0x0047a9c0` | `CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0` | Mode forwarder that skips mode 4 and otherwise calls `CUnit__SetEngagementModeAndMaybeClearTargetReader`. |
| `0x00479b60` | `CGillM__InitGillMAIComponent` | Allocates/initializes CGillMAI-style component and stores it at `this+0x13c`. |
| `0x00479bf0` | `CGillMAI__ScalarDeletingDestructor` | CGillMAI scalar deleting destructor wrapper. |
| `0x00479cb0` | `CGillM__InitTerrainGuideComponent` | Allocates/initializes TerrainGuide-style component and stores it at `this+0x208`. |
| `0x00479d10` | `CGillM__UpdateGroundedVerticalDrift` | Grounded vertical drift helper using `+0x274`, `+0x244`, static-shadow sampling, and drift fields `+0x84/+0xcc`. |
| `0x00479db0` | `CGillM__TriggerRandomArmHitAnimationIfReady` | Cooldown-gated random left/right arm hit-animation helper. |
| `0x0047a160` | `CGillM__StartState1WithStoredMotionVector` | State transition helper that feeds stored vector `+0x278` into vtable `+0xf4` and writes state `+0x244 = 1`. |

## Evidence

- Fresh Ghidra export: `10` metadata rows, `10` tag rows, `13 xref rows`, `540 instruction rows`, and `10 decompile rows`.
- Ghidra dry/apply/final-dry:
  - `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=129 missing=0 bad=0`
  - `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=129 missing=0 bad=0`
  - final dry updated=0 skipped=10.
- Queue closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` static debt.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.
- Verified backup: `G:\GhidraBackups\BEA_20260606-225205_post_wave1199_gillm_groundunit_ai_motion_effects_current_risk_review_verified`.

## Boundary

This is static rebuild-grade static contracts evidence only. Exact source-body identity, concrete CGillM/CGillMHeadAI/shared ground-unit layouts, runtime AI/animation/movement/effects behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
