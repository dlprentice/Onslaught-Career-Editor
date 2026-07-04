# Wave1114 Mixed Score-27 Current-Risk Head Supersession Readiness Note

Status: complete static supersession accounting
Date: 2026-06-05
Scope: `wave1114-mixed-score27-current-risk-head-supersession`

Wave1114 accounts for `10 rows` from the Wave1108 current focused denominator: the mixed score-27 current-risk head after prior Wave1109-Wave1113 accounting. The pass made no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Accounting after Wave1114:

- Static Ghidra function-quality closure: `6410/6410 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave1108 current focused candidates: current focused candidates: 1179.
- Wave1108 current focused accounting: `43/1179 = 3.65%`.

Representative anchors:

| Address | Prior evidence |
| --- | --- |
| `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | Wave1059 `collision-seeking-round-tail-review-wave1059`; DATA xref `0x005dbf68`; mount-state compatibility and collision-flag fallback evidence. |
| `0x0042c420 CConsoleMenu__ctor_like_0042c420` | Wave972 `console-menu-constructor-review-wave972`; ConsoleMenu-style constructor fields and `CSoundManager__Init` call evidence. |
| `0x00437490 CPhysicsScriptStatements__CreateStatementType5` | Wave991 `round-config-bridge-review-wave991`; type-5/round value factory ids `0x1` through `0x26`; round-statement load xrefs. |
| `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | Wave1098 `primitive-collision-bridge-review-wave1098`; triangle-prism edge/plane membership helper called from swept-sphere collision core. |
| `0x004799c0 CGillM__VFunc09_InitGroundedSpawnState` | Wave1000 `gillm-grounded-movement-review-wave1000`; CGillM vtable slot 9, static-shadow height, grounded snapshot evidence. |
| `0x0047ea20 CHeightField__GetHeightSamplePacked16` | Wave935 `world-footprint-heightfield-review-wave935`; packed height buffer `+0x1028`, min/max table and occupancy/render xrefs. |
| `0x00487d10 CHud__RenderBattleline` | Wave1004 `hud-render-body-review-wave1004`; `CDXEngine__PostRender`, HUD singleton `0x8aa4e8`, viewport, battleline and influence-overlay evidence. |
| `0x004aa6b0 CMesh__GetNameOrUnknown` | Wave814 `mesh-segment-tail-wave814`; global mesh list `DAT_00704ad8`, name `+0x24`, fallback `0x0062f8d4`. |
| `0x004bff30 CComplexThing__dtor_base_Thunk_004bff30` | Wave1022 `object-lifecycle-dtor-review-wave1022`; jump thunk to `0x004f3f00 CComplexThing__dtor_base`; no standalone cleanup body. |
| `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting` | Wave927 `cunit-active-reader-targeting-review-wave927`; `RET 0x4`, `candidate_side`, side field `this+0x138`, profile field `this+0x164->0x128`. |

Verified prior backups:

- `[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`

Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1114; wave1114-mixed-score27-current-risk-head-supersession; 43/1179 = 3.65%; 10 rows; current focused candidates: 1179; mixed score-27 current-risk head; Wave1059; Wave972; Wave991; Wave1098; Wave1000; Wave935; Wave1004; Wave814; Wave1022; Wave927; 0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags; 0x0042c420 CConsoleMenu__ctor_like_0042c420; 0x00437490 CPhysicsScriptStatements__CreateStatementType5; 0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism; 0x004799c0 CGillM__VFunc09_InitGroundedSpawnState; 0x0047ea20 CHeightField__GetHeightSamplePacked16; 0x00487d10 CHud__RenderBattleline; 0x004aa6b0 CMesh__GetNameOrUnknown; 0x004bff30 CComplexThing__dtor_base_Thunk_004bff30; 0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting; [maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified; [maintainer-local-ghidra-backup-root]\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified; [maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

Boundary: this is static supersession accounting only. Runtime behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
