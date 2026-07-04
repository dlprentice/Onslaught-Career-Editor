# Ghidra Wave900 Through Wave1058 Recheck

Status: complete local static evidence gate
Date: 2026-06-01
Scope: `wave900-plus-through-wave1058-recheck`

This note extends the Wave900-plus static recheck boundary through Wave1058. Wave900 remains the loaded-Ghidra export-contract function-quality closure point; Wave1058 adds tag normalization for the old Wave321 CUnitAI/GeneralVolume deploy-tracking residual cluster and adjacent context rows.

Wave1058 (`cunitai-deploy-tracking-residual-review-wave1058`) re-read five primary deploy-tracking rows and six adjacent context rows, then saved function tags only: `0x004247a0 CGeneralVolume__InitRandomizedVelocityOffsets`, `0x00424a20 CUnitAI__UpdateDeployAimAndScheduleEvent`, `0x00424be0 CUnitAI__AdvanceDeployAnimationPhase`, `0x00424ca0 CUnitAI__UpdateDeployTrackingTransformTowardTarget`, `0x004250f0 CUnitAI__DecayDeployTrackingTransformToNeutral`, `0x004244b0 CCockpit__ctor`, `0x00424920 CGeneralVolume__BeginFlyToWalkTransition`, `0x00424990 CGeneralVolume__BeginWalkToFlyTransition`, `0x0040a580 CBattleEngine__Morph`, `0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation`, and `0x00425760 Mat34__OrthonormalizeAxes`.

Fresh evidence:

- Primary pre/post exports: `5` metadata rows, `5` tag rows, `5` xref rows, `802` function-body instruction rows, and `5` decompile rows.
- Context pre/post exports: `10` metadata rows, `10` tag rows, `53` xref rows, `915` function-body instruction rows, and `10` decompile rows.
- Dry/read-back sequence: dry `updated=0 skipped=0 tags_added=103 missing=0 bad=0`; first apply added/read-backed `103` tags before a corrected post-summary save-call issue; corrected no-op apply and final dry both reported `updated=0 skipped=11 tags_added=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `804/1408 = 57.10%`.
- Expanded static surface progress advances to `1132/1509 = 75.02%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-192010_post_wave1058_cunitai_deploy_tracking_residual_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1058-recheck
```

Boundary note: this aggregate gate is static documentation/evidence hygiene. Runtime deploy, morph, animation, cockpit, transform, or math behavior; exact object/layout completeness; exact source-body identity; BEA patching behavior; gameplay outcomes; and rebuild parity remain separate proof.

Probe token anchor: Wave1058; cunitai-deploy-tracking-residual-review-wave1058; 0x004247a0 CGeneralVolume__InitRandomizedVelocityOffsets; 0x00424a20 CUnitAI__UpdateDeployAimAndScheduleEvent; 0x00424be0 CUnitAI__AdvanceDeployAnimationPhase; 0x00424ca0 CUnitAI__UpdateDeployTrackingTransformTowardTarget; 0x004250f0 CUnitAI__DecayDeployTrackingTransformToNeutral; 0x004244b0 CCockpit__ctor; 0x00424920 CGeneralVolume__BeginFlyToWalkTransition; 0x00424990 CGeneralVolume__BeginWalkToFlyTransition; 0x0040a580 CBattleEngine__Morph; 0x0040eeb0 CBattleEngine__FinishedPlayingCurrentAnimation; 0x00425760 Mat34__OrthonormalizeAxes; 804/1408 = 57.10%; 1132/1509 = 75.02%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-192010_post_wave1058_cunitai_deploy_tracking_residual_review_verified; tag normalization.
