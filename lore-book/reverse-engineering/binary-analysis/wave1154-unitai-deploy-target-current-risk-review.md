# Wave1154 UnitAI Deploy/Target Current-Risk Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`); `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`); `0x00411630` → `CBattleEngineJetPart__HandleGroundEffect` (was `CMonitor__IntegrateMovementAgainstTerrain`); `0x00411aa0` → `CBattleEngineJetPart__GetFriction` (was `CMonitor__ComputeTerrainVelocityScalar`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1154 (`wave1154-unitai-deploy-target-current-risk-review`) accounts for `5 current-risk rows` from the Wave1108 current focused denominator as a UnitAI deploy/target transition current-risk review. It is a fresh Ghidra read-only review with no mutation.

Probe token anchor: Wave1154; wave1154-unitai-deploy-target-current-risk-review; 378/1179 = 32.06%; 5 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 801; current risk candidates: 6166; UnitAI deploy/target transition current-risk review; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; CMonitor__UpdateMovementTransitionAndEffects; TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit; CUnitAI__PlayDeployingAnimationIfState0; CUnitAI__PlayUndeployingAnimation; CUnitAI__HandleDeployUndeployAnimationCompletion; [maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x00410c50` | `CMonitor__UpdateMovementTransitionAndEffects` | Fresh xref remains the checked call from `0x004081c0 CMonitor__Process`. Decompile keeps the monitor-owner boundary and calls `CMonitor__UpdateTrackedRenderPair`, `CBattleEngine__Morph`, `CMonitor__IntegrateMovementAgainstTerrain`, `CMonitor__ComputeTerrainVelocityScalar`, `CBattleEngine__GroundParticleEffect`, and `CBattleEngineJetPart__HandleSkimming`. Prior Wave948 transition/effects review already covered this row; Wave1154 re-reads it against the active current-risk denominator. |
| `0x00414b30` | `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit` | Fresh xrefs remain two calls from `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`. Decompile scans the linked target/unit set and returns true when any linked unit satisfies `CUnit__IsTargetTimeoutBeforeProfileLimit`. |
| `0x00415780` | `CUnitAI__PlayDeployingAnimationIfState0` | DATA slot xref `0x005e23d4`; decompile plays `deploying` only when deploy state `+0x260` is `0`, dispatches the animation index through vfunc slot `+0xf0`, and sets `+0x260` to `1`. Prior Wave928 deploy-state review covered the row; Wave1154 re-reads it against the active current-risk denominator. |
| `0x004157c0` | `CUnitAI__PlayUndeployingAnimation` | DATA slot xref `0x005e23d8`; decompile clears `+0x1f0`, resolves `undeploying`, and dispatches through vfunc slot `+0xf0`. |
| `0x00415970` | `CUnitAI__HandleDeployUndeployAnimationCompletion` | DATA slot xref `0x005e2378`; decompile compares the current animation against `deploying` and `undeploying`, transitions to `deployed` or `normal`, updates `+0x1f0` or `+0x260`, and otherwise falls back to `CUnitAI__HandleDeployAndFireAnimationCompletion`. |

Fresh primary exports verified `5` metadata rows, `5` tag rows, `6` xref rows, `783` body-instruction rows, and `5` decompile rows. The verified Ghidra project backup is `[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified` with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

## Boundary

This wave proves static Ghidra read-back coherence for the selected monitor/target-set/CUnitAI deploy rows only. Runtime deploy/undeploy AI behavior, runtime target selection behavior, runtime movement/morph/effect behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
