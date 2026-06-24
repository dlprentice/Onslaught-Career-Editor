# Ghidra Wave900 Through Wave1068 Recheck Readiness Note

Status: complete local validation evidence
Date: 2026-06-02
Scope: `wave900-plus-through-wave1068-recheck`

This note extends the rolling Wave900+ recheck gate through Wave1068 after the read-only `rtbuilding-rtmesh-lifecycle-review-wave1068` pass. It keeps the prior Wave900+ notes as historical evidence and adds the current Wave1068 readiness/probe/backup anchors to the live aggregate gate.

Current anchors:

- Latest operational wave: Wave1068, `rtbuilding-rtmesh-lifecycle-review-wave1068`.
- Latest focused probe: `tools/ghidra_rtbuilding_rtmesh_lifecycle_review_wave1068_probe.py`.
- Latest readiness note: `release/readiness/ghidra_rtbuilding_rtmesh_lifecycle_review_wave1068_2026-06-02.md`.
- Latest verified backup: `G:\GhidraBackups\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified`.

Current percentages:

- Static export-contract function-quality closure: `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress: `812/1408 = 57.67%`.
- Expanded static surface progress: `1258/1560 = 80.64%`.
- Wave911 top-500 risk-ranked coverage: `500/500 = 100.00%`.

Representative Wave1068 anchors:

- `0x004db850 CRTBuilding__Destructor`
- `0x004db8d0 CRTBuilding__ScalarDeletingDestructor`
- `0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry`
- `0x004dc370 CRTMesh__Init`
- `0x004dc950 CRTMesh__Destructor`
- `0x004dd0c0 CRTMesh__CleanupAllEffects`
- `0x004dd6b0 CRTMesh__SetQualityLevel`
- `0x004dd770 CRTMesh__GetQualityLevel`

Validation expectation:

- The aggregate package script is `test:ghidra-wave900-plus-through-wave1068-recheck`.
- The aggregate script accepts the seven intentional Wave1068 context no-function rows from raw CRTBuilding/CRTMesh vtable pointers.
- The focused Wave1068 probe validates the primary/context/vtable exports, docs, ledgers, package scripts, queue closure, and backup summary.

Latest aggregate run:

- `test:ghidra-wave900-plus-through-wave1068-recheck`: PASS.
- Readiness notes: `171`.
- Covered waves: `169`.
- Package probe scripts: `167`.
- Evidence bases: `167`.
- Backup references: `169`.
- Apply scripts: `53`.
- Wave982-Wave1068 direct-probe compatibility scan: `87` result rows, `1` direct PASS, `86` expected current-state/historical-current failures, `0` disallowed failures.
- Current queue: `6246` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status PASS.

Boundary note: this aggregate gate proves local static evidence coverage, backup references, probe/doc wiring, and zero export-contract function-quality debt. It does not prove runtime render behavior, runtime LOD/effect cleanup, exact layouts, exact source identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1068; rtbuilding-rtmesh-lifecycle-review-wave1068; 0x004db850 CRTBuilding__Destructor; 0x004db8d0 CRTBuilding__ScalarDeletingDestructor; 0x004dba40 CRTBuilding__VFuncSlot10_PickRandomLinkedEntry; 0x004dc370 CRTMesh__Init; 0x004dc950 CRTMesh__Destructor; 0x004dd0c0 CRTMesh__CleanupAllEffects; 0x004dd6b0 CRTMesh__SetQualityLevel; 0x004dd770 CRTMesh__GetQualityLevel; 812/1408 = 57.67%; 1258/1560 = 80.64%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-010648_post_wave1068_rtbuilding_rtmesh_lifecycle_review_verified; read-only review.
