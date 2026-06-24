# Wave1122 HLCollisionDetector Current-Risk Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1122-hlcollisiondetector-current-risk-review`

Wave1122 re-read `7 rows` from the next Wave1108 current focused candidates: 1179, as a score-23 HLCollisionDetector cluster. Current focused accounting moves to `129/1179 = 10.94%`; static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Representative anchors: `0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `0x00480c90 CHLCollisionDetector__HandleCollisionEnter`, `0x00480db0 CHLCollisionDetector__HandleCollisionExit`, `0x00480e10 CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions`, `0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair`, `0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep`, and `0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent`.

Mutation status:

- Fresh read-only Ghidra export only.
- No mutation.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.

Evidence:

- Metadata/tag/xref/instruction/decompile exports: `7` / `7` / `24` / `752` / `7`.
- Probe anchor wording: fresh read-only Ghidra export; no mutation.
- Backup: `G:\GhidraBackups\BEA_20260605-043957_post_wave1122_hlcollisiondetector_current_risk_review_verified`, `19` files, `175672199` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`.
- Prior context: Wave398 corrected the HLCollisionDetector owner/signature/comment evidence, Wave916 reviewed all seven helpers read-only, and Wave1018 re-read the event/sweep spine read-only.

What this proves:

- The seven target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows remain coherent with the saved static evidence.
- The current-risk accounting advances from `122/1179 = 10.35%` to `129/1179 = 10.94%`.

What remains separate:

- Runtime collision behavior.
- Event timing behavior.
- Exact detector/component/source layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
