# Ghidra Wave900 Through Wave1069 Recheck Readiness Note

Status: complete local validation evidence
Date: 2026-06-02
Scope: `wave900-plus-through-wave1069-recheck`

This note extends the rolling Wave900+ recheck gate through Wave1069 after the read-only `groundunit-vfunc-motion-effects-review-wave1069` pass. It keeps the prior Wave900+ notes as historical evidence and adds the current Wave1069 readiness/probe/backup anchors to the live aggregate gate.

Current anchors:

- Latest operational wave: Wave1069, `groundunit-vfunc-motion-effects-review-wave1069`.
- Latest focused probe: `tools/ghidra_groundunit_vfunc_motion_effects_review_wave1069_probe.py`.
- Latest readiness note: `release/readiness/ghidra_groundunit_vfunc_motion_effects_review_wave1069_2026-06-02.md`.
- Latest verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified`.

Current percentages:

- Static export-contract function-quality closure: `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress: `812/1408 = 57.67%`.
- Expanded static surface progress: `1266/1560 = 81.15%`.
- Wave911 top-500 risk-ranked coverage: `500/500 = 100.00%`.

Representative Wave1069 anchors:

- `0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0`
- `0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440`
- `0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820`
- `0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10`
- `0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0`
- `0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward`
- `0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4`
- `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar`

Validation expectation:

- The aggregate package script is `test:ghidra-wave900-plus-through-wave1069-recheck`.
- The aggregate script accepts the thirteen intentional Wave1069 context no-function rows around the motion-controller/ground-unit neighborhood.
- The focused Wave1069 probe validates the primary/caller/context/vtable exports, docs, ledgers, package scripts, queue closure, and backup summary.

Latest aggregate run:

- `test:ghidra-wave900-plus-through-wave1069-recheck`: PASS.
- Readiness notes: `172`.
- Covered waves: `170`.
- Package probe scripts: `168`.
- Evidence bases: `168`.
- Backup references: `170`.
- Apply scripts: `53`.
- Wave982-Wave1069 direct-probe compatibility scan: `88` result rows, `2` direct PASS, `86` expected current-state/historical-current failures, `0` disallowed failures.
- Current queue: `6246` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status PASS.

Boundary note: this aggregate gate proves local static evidence coverage, backup references, probe/doc wiring, and zero export-contract function-quality debt. It does not prove runtime grounded-unit, mine, pod, pickup, mesh-break, particle/effect cleanup, or motion behavior, exact layouts, exact source identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1069; groundunit-vfunc-motion-effects-review-wave1069; 0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0; 0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440; 0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820; 0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10; 0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0; 0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward; 0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4; 0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar; 812/1408 = 57.67%; 1266/1560 = 81.15%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified; read-only review.
