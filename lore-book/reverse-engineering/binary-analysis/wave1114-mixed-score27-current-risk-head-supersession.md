# Wave1114 Mixed Score-27 Current-Risk Head Supersession

Status: complete static supersession accounting
Last updated: 2026-06-05
Scope: `wave1114-mixed-score27-current-risk-head-supersession`

Wave1114 accounts for `10 rows` from the Wave1108 current focused denominator: the mixed score-27 current-risk head after Wave1109 through Wave1113 are subtracted. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1114 current focused supersession accounting | `43/1179 = 3.65%` |

## Superseded Rows

| Address | Saved row | Prior evidence |
| --- | --- | --- |
| `0x00425a10` | `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | Wave1059 `collision-seeking-round-tail-review-wave1059` re-read the infantry-bloke collision filter, DATA xref `0x005dbf68`, mount-state compatibility fallback, and `CCollisionSeekingRound__CheckCollisionFlags` fallback. |
| `0x0042c420` | `CConsoleMenu__ctor_like_0042c420` | Wave972 `console-menu-constructor-review-wave972` re-read the ConsoleMenu-style constructor, calls from `CSoundManager__Init` and raw constructor sites, vtable initialization, and zeroed first-child/next-sibling/parent/count fields. |
| `0x00437490` | `CPhysicsScriptStatements__CreateStatementType5` | Wave991 `round-config-bridge-review-wave991` re-read the type-5/round value factory, observed value ids `0x1` through `0x26`, and xrefs from `CRoundStatement__LoadFromMemBuffer` plus `CPhysicsRoundValueList__LoadFromMemBuffer`. |
| `0x00479020` | `CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | Wave1098 `primitive-collision-bridge-review-wave1098` re-read the triangle-prism edge/plane membership test called from `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`. |
| `0x004799c0` | `CGillM__VFunc09_InitGroundedSpawnState` | Wave1000 `gillm-grounded-movement-review-wave1000` re-read CGillM vtable `0x005e0b30` slot 9, spawn-state field writes, shared grounded-motion dispatch, static-shadow height sampling, and grounded snapshot fields. |
| `0x0047ea20` | `CHeightField__GetHeightSamplePacked16` | Wave935 `world-footprint-heightfield-review-wave935` re-read the packed 16-bit height sampler, xrefs from min/max table, world occupancy, landscape, patch, and support-clearance paths, and buffer `+0x1028` edge cases including `0xa1ffe`. |
| `0x00487d10` | `CHud__RenderBattleline` | Wave1004 `hud-render-body-review-wave1004` re-read the HUD battleline body, `CDXEngine__PostRender` call at `0x0053ed79`, HUD singleton `0x8aa4e8`, viewport argument, battleline/message-box sprites, and influence-overlay path. |
| `0x004aa6b0` | `CMesh__GetNameOrUnknown` | Wave814 `mesh-segment-tail-wave814` saved the owner/signature correction: global mesh list `DAT_00704ad8`, next-link `+0x158`, mesh name `+0x24`, and fallback string `0x0062f8d4` (`unknown mesh name`). |
| `0x004bff30` | `CComplexThing__dtor_base_Thunk_004bff30` | Wave1022 `object-lifecycle-dtor-review-wave1022` re-read the Wave460 thunk correction: this row jumps to canonical `CComplexThing__dtor_base` at `0x004f3f00` and is reached from unwind cleanup plus `SharedComplexThing__ScalarDeletingDestructor`. |
| `0x004fd3d0` | `CUnit__IsCandidateSideCompatibleForTargeting` | Wave927 `cunit-active-reader-targeting-review-wave927` re-read the Wave540 owner/signature correction: `RET 0x4`, one explicit `candidate_side` argument, target-selection callers, side field `this+0x138`, and profile field `this+0x164->0x128`. |

Prior verified backups:

- Wave1059: `G:\GhidraBackups\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`
- Wave972: `G:\GhidraBackups\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified`
- Wave991: `G:\GhidraBackups\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified`
- Wave1098: `G:\GhidraBackups\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified`
- Wave1000: `G:\GhidraBackups\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`
- Wave935: `G:\GhidraBackups\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`
- Wave1004: `G:\GhidraBackups\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`
- Wave814: `G:\GhidraBackups\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified`
- Wave1022: `G:\GhidraBackups\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`
- Wave927: `G:\GhidraBackups\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`

Latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1114; wave1114-mixed-score27-current-risk-head-supersession; 43/1179 = 3.65%; 10 rows; current focused candidates: 1179; mixed score-27 current-risk head; Wave1059; Wave972; Wave991; Wave1098; Wave1000; Wave935; Wave1004; Wave814; Wave1022; Wave927; 0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags; 0x0042c420 CConsoleMenu__ctor_like_0042c420; 0x00437490 CPhysicsScriptStatements__CreateStatementType5; 0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism; 0x004799c0 CGillM__VFunc09_InitGroundedSpawnState; 0x0047ea20 CHeightField__GetHeightSamplePacked16; 0x00487d10 CHud__RenderBattleline; 0x004aa6b0 CMesh__GetNameOrUnknown; 0x004bff30 CComplexThing__dtor_base_Thunk_004bff30; 0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting; G:\GhidraBackups\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified; G:\GhidraBackups\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified; G:\GhidraBackups\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified; G:\GhidraBackups\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified; G:\GhidraBackups\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified; G:\GhidraBackups\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified; G:\GhidraBackups\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified; G:\GhidraBackups\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified; G:\GhidraBackups\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified; G:\GhidraBackups\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This wave closes current-risk accounting for these ten rows only. It does not prove runtime collision behavior, runtime console behavior, runtime physics-script behavior, runtime terrain behavior, runtime HUD behavior, runtime mesh behavior, runtime cleanup behavior, runtime targeting behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
