# Ghidra CUnitAI Deploy Tracking Residual Review Wave1058 Readiness Note

Status: complete static re-audit tag-normalization evidence
Date: 2026-06-01
Scope: `cunitai-deploy-tracking-residual-review-wave1058`

Wave1058 re-read the old Wave321 CUnitAI/GeneralVolume deploy-tracking residual cluster and saved function-tag normalization for eleven already named/commented rows. The pass made no renames, no signature changes, no comment changes, no function-boundary changes, and no executable-byte changes.

Primary targets:

| Address | Existing saved identity | Fresh evidence |
| --- | --- | --- |
| `0x004247a0 CGeneralVolume__InitRandomizedVelocityOffsets` | `void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int randomRange)` | Called from `CGeneralVolume__RandomizeOffsets4B8_4C0`; still initializes randomized velocity-offset fields and phase context. |
| `0x00424a20 CUnitAI__UpdateDeployAimAndScheduleEvent` | `void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * this)` | Calls target-tracking or neutral-decay helpers, advances deploy phase, and schedules event `0x7d1`. |
| `0x00424be0 CUnitAI__AdvanceDeployAnimationPhase` | `void __fastcall CUnitAI__AdvanceDeployAnimationPhase(void * this)` | Reached from `0x00424a20`; still handles deploy animation phase fields and transition-state clearing. |
| `0x00424ca0 CUnitAI__UpdateDeployTrackingTransformTowardTarget` | `void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(void * this)` | Reached from `0x00424a20`; still builds target-facing tracking transform context. |
| `0x004250f0 CUnitAI__DecayDeployTrackingTransformToNeutral` | `void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(void * this)` | Reached from `0x00424a20`; still damps deploy tracking offsets back toward neutral. |

Context rows tagged by the same normalization pass:

- `0x004244b0 CCockpit__ctor`
- `0x00424920 CGeneralVolume__BeginFlyToWalkTransition`
- `0x00424990 CGeneralVolume__BeginWalkToFlyTransition`
- `0x0040a580 CBattleEngine__Morph`
- `0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation`
- `0x00425760 Mat34__OrthonormalizeAxes`

Read-back evidence:

- Primary pre/post exports: `5` metadata rows, `5` tag rows, `5` xref rows, `802` function-body instruction rows, and `5` decompile rows.
- Context pre/post exports: `10` metadata rows, `10` tag rows, `53` xref rows, `915` function-body instruction rows, and `10` decompile rows.
- Dry run reported `updated=0 skipped=0 tags_added=103 missing=0 bad=0`.
- The first apply added/read-backed `103` tags across `11` rows and reported `updated=11 skipped=0 tags_added=103 missing=0 bad=0`; an explicit script save call then produced a post-summary transaction-lock error. The script was corrected to match the repo's existing headless-save pattern, and subsequent read-back proved the tags had persisted.
- Corrected no-op apply reported `updated=0 skipped=11 tags_added=0 missing=0 bad=0` with `REPORT: Save succeeded`.
- Final dry/read-back reported `updated=0 skipped=11 tags_added=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `804/1408 = 57.10%`.
- Expanded static surface progress advances to `1132/1509 = 75.02%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-192010_post_wave1058_cunitai_deploy_tracking_residual_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The eleven target/context rows exist in the saved Ghidra project with expected names and signatures.
- The saved comments remain coherent with fresh metadata/xref/instruction/decompile evidence.
- The rows now carry `cunitai-deploy-tracking-residual-review-wave1058` and `wave1058-readback-verified` function tags.
- The Wave321 deploy-tracking residual cluster is normalized to current post-closure re-audit tagging standards.

What remains unproven:

- Runtime deploy, morph, animation, cockpit, transform, or math behavior.
- Exact `CUnitAI`, `CGeneralVolume`, `CBattleEngine`, `CCockpit`, or `Mat34` layout completeness.
- Exact parent source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Next candidate note: continue with the next Wave911 focused static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1058; cunitai-deploy-tracking-residual-review-wave1058; 0x004247a0 CGeneralVolume__InitRandomizedVelocityOffsets; 0x00424a20 CUnitAI__UpdateDeployAimAndScheduleEvent; 0x00424be0 CUnitAI__AdvanceDeployAnimationPhase; 0x00424ca0 CUnitAI__UpdateDeployTrackingTransformTowardTarget; 0x004250f0 CUnitAI__DecayDeployTrackingTransformToNeutral; 0x004244b0 CCockpit__ctor; 0x00424920 CGeneralVolume__BeginFlyToWalkTransition; 0x00424990 CGeneralVolume__BeginWalkToFlyTransition; 0x0040a580 CBattleEngine__Morph; 0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation; 0x00425760 Mat34__OrthonormalizeAxes; 804/1408 = 57.10%; 1132/1509 = 75.02%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-192010_post_wave1058_cunitai_deploy_tracking_residual_review_verified; tag normalization.
