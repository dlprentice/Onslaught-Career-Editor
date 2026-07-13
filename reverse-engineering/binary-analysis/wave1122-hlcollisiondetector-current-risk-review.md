# Wave1122 HLCollisionDetector Current-Risk Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00480ed0` comment correction; `0x00481060` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: validated static read-only evidence
Date: 2026-06-05
Tag: `wave1122-hlcollisiondetector-current-risk-review`

Wave1122 accounts for `7 rows` from the Wave1108 current focused denominator as a score-23 HLCollisionDetector cluster, moving current focused accounting to `129/1179 = 10.94%` of current focused candidates: 1179. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

This is a fresh read-only Ghidra export of the Wave398/Wave916/Wave1018 HLCollisionDetector evidence spine. No mutation was needed: no rename, no signature change, no function-boundary change, and no executable-byte change.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions` | Called from `CCollisionSeekingRound__InitWithSound`; stores the collision component, clears detector fields, scans MapWho sectors, traverses quad children, and dispatches candidate pairs. |
| `0x00480c90 CHLCollisionDetector__HandleCollisionEnter` | Enter callback path; applies `0x100` collision-filter checks, calls the current component callback, and can dispatch follow-up pair handling. |
| `0x00480db0 CHLCollisionDetector__HandleCollisionExit` | Exit callback path; rejects null/self candidates, applies mutual filters, warns on unexpected collision-change state, dispatches the pair, and clears the flag. |
| `0x00480e10 CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions` | Recursive quad/MapWho traversal; resolves candidate persistent collision-seeking components and dispatches qualifying pairs. |
| `0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair` | Pair dispatcher; computes separation/time context with `DAT_00672fd0`, can call enter immediately, or schedules `EVENT_MANAGER` event `2000`. |
| `0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep` | MapWho sweep bridge from `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`; handles exits from previous sectors and entries into newly scanned cells. |
| `0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent` | Vtable DATA xref `0x005dbf78`; handles scheduled event number `2000`, saves/reuses the event pointer, calls `HandleCollisionEnter`, and clears detector fields. |

Evidence:

- Fresh metadata/tag/xref/instruction/decompile exports: `7` / `7` / `24` / `752` / `7`.
- Existing tags remain anchored to `collision-hl-wave398`, `hlcollision`, and `static-reaudit`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-043957_post_wave1122_hlcollisiondetector_current_risk_review_verified`, `19` files, `175672199` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`.
- Prior context: Wave398 corrected older owner labels, Wave916 reviewed all seven rows read-only, and Wave1018 re-read the event/sweep spine with no mutation.

Boundary:

This is static Ghidra/source-reference evidence. It does not prove runtime collision behavior, event timing behavior, exact detector/component/source layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
