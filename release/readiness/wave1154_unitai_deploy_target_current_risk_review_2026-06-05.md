# Wave1154 UnitAI Deploy/Target Current-Risk Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`); `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **Owner/name supersession (2026-07-12):** the Wave1154 exports remain valid
> historical read-back evidence, but their owner interpretation does not.
> Current static evidence identifies `0x00410c50` as
> `CBattleEngineJetPart__Move`, called by `0x004081c0 CBattleEngine__Move`.
> See the [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1154-unitai-deploy-target-current-risk-review`

Wave1154 re-read five UnitAI deploy/target transition current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1154; wave1154-unitai-deploy-target-current-risk-review; 378/1179 = 32.06%; 5 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 801; current risk candidates: 6166; UnitAI deploy/target transition current-risk review; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; CMonitor__UpdateMovementTransitionAndEffects; TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit; CUnitAI__PlayDeployingAnimationIfState0; CUnitAI__PlayUndeployingAnimation; CUnitAI__HandleDeployUndeployAnimationCompletion; [maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `5` rows, `targets=5 found=5 missing=0`.
- `pre-tags.tsv`: `5` rows, `missing=0`.
- `pre-xrefs.tsv`: `6` rows.
- `pre-instructions.tsv`: `783` instruction rows, `targets=5 missing=0`.
- `pre-decompile/index.tsv`: `5` rows, `targets=5 dumped=5 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous counted completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified`.
- Codex subagent usage: read-only consults were used for candidate/accounting sanity and static completion-definition review; Codex root selected, exported, audited, and kept the tranche read-only.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x00410c50 CMonitor__UpdateMovementTransitionAndEffects` | Checked caller remains `CMonitor__Process`; body still bridges monitor movement, terrain integration, morph decisions, ground effect dispatch, and skimming context. |
| `0x00414b30 TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit` | Scans linked target/unit set and calls `CUnit__IsTargetTimeoutBeforeProfileLimit`; still called twice by `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`. |
| `0x00415780 CUnitAI__PlayDeployingAnimationIfState0` | DATA slot xref `0x005e23d4`; plays `deploying` through vfunc slot `+0xf0` when `+0x260` is `0`, then advances `+0x260` to `1`. |
| `0x004157c0 CUnitAI__PlayUndeployingAnimation` | DATA slot xref `0x005e23d8`; clears `+0x1f0`, resolves `undeploying`, and dispatches through vfunc slot `+0xf0`. |
| `0x00415970 CUnitAI__HandleDeployUndeployAnimationCompletion` | DATA slot xref `0x005e2378`; transitions from `deploying` to `deployed`, from `undeploying` to `normal`, or falls back to `CUnitAI__HandleDeployAndFireAnimationCompletion`. |

Accounting after Wave1154:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%` historical-retired/non-reconstructable provenance only.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `378/1179 = 32.06%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 801.

This is static Ghidra evidence only. Runtime deploy/undeploy AI behavior, runtime target selection behavior, runtime movement/morph/effect behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
