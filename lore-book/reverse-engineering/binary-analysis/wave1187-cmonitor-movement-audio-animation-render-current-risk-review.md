# Wave1187 CMonitor Movement / Audio / Animation / Render Current-Risk Review

Status: complete static current-risk comment/tag normalization; artifact commit `ad48dcdc3def8645e4b717b4beeb645b8e316e40`; state closeout commit `f15722628d73b96e36d851ec7249fc8266c6a87c`; handoff pointer `25cbb46928c123c29519095bd5b36ba245f39bf5`; pushed to origin/main
Date: 2026-06-06
Scope tag: `wave1187-cmonitor-movement-audio-animation-render-current-risk-review`

Wave1187 accounts for `6 CMonitor movement/audio/animation/render current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence:

- `0x00409950 CMonitor__UpdateSoundEventPlaybackForReader`
- `0x00411630 CMonitor__IntegrateMovementAgainstTerrain`
- `0x00411aa0 CMonitor__ComputeTerrainVelocityScalar`
- `0x0044e2c0 CMonitor__CheckSVFAnimationAndAdvanceState`
- `0x0047d3b0 CMonitor__TryQueuePrefireAnimation`
- `0x005078f0 CMonitor__UpdateTrackedRenderPair`

The saved Ghidra names and signatures were already bounded. This wave normalized saved comments and tags only, adding rebuild-grade static-contract anchors and explicit no-noticeable-difference boundary tags.

One Codex read-only consult was used and recommended this monitor movement/audio/animation/render slice as more rebuild-relevant than the initial CRT-tail candidate. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `793/1179 = 67.26%`; current risk candidates: 6166; current focused candidates: 1173; live regenerated current focused candidates: 1173; remaining active focused work: 386; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `6` metadata rows, `6` tag rows, `7 xref rows`, `914 instruction rows`, and `6` decompile rows. Verified backup: `G:\GhidraBackups\BEA_20260606-151617_post_wave1187_cmonitor_movement_audio_animation_render_current_risk_review_verified`.

## Reviewed Rows

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00409950` | `CMonitor__UpdateSoundEventPlaybackForReader` | Call xref from `0x0040963e CMonitor__Process`; coordinates engine/health/energy/lock/walk sound chains through `CSoundManager`, maintains active-reader state at `monitor+0x5e8`, scans `monitor+0x294` sound-event entries, and resets `monitor+0x5d0` when walk-sound gates fail. |
| `0x00411630` | `CMonitor__IntegrateMovementAgainstTerrain` | Call xref from `0x00410e08 CMonitor__UpdateMovementTransitionAndEffects`; samples terrain/static-shadow height through `CStaticShadows__SampleShadowHeightBilinear`, works against movement-object state at `this+0x18`, dispatches movement-object vfunc `+0x74`, and adjusts orientation through vector cross/normalize plus heightfield-normal sampling. |
| `0x00411aa0` | `CMonitor__ComputeTerrainVelocityScalar` | Call xref from `0x00411068 CMonitor__UpdateMovementTransitionAndEffects`; samples terrain height, clamps against `DAT_006fbdfc`, compares deltas against `0x005d8568` / `0x005d8cc0`, queries movement-object vfunc `+0x6c`, and returns a terrain/velocity scalar. |
| `0x0044e2c0` | `CMonitor__CheckSVFAnimationAndAdvanceState` | DATA vtable ref `0x005e051c`; resolves the `SVF` token through `CMesh__FindAnimationIndexByName`, compares linked-object current animation from vfunc `+0x58`, and dispatches monitor vfunc byte offset `+0x38` when the animation matches. |
| `0x0047d3b0` | `CMonitor__TryQueuePrefireAnimation` | DATA ref `0x005e2ad4` at `CGroundVehicle` vtable slot 86; calls `CUnit__UpdateDeployStateAndChargeEffects`, checks `this+0x164` / `this+0x244`, resolves `prefire` through `CMesh__FindAnimationIndexByName`, and dispatches animation vfunc byte offset `+0xf0` when present. |
| `0x005078f0` | `CMonitor__UpdateTrackedRenderPair` | Call xrefs from `0x00410c81 CMonitor__UpdateMovementTransitionAndEffects` and `0x004137a6 CBattleEngineWalkerPart__Move`; `RET 0x4` preserves explicit `update_projected_volume`; updates two render slots at `this+0x18` / `this+0x20`, dispatches owner vfunc byte offset `+300`, copies basis data, and optionally applies projected-volume orientation from `owner+0xa0` / `owner+0x5c`. |

## Mutation Summary

The wave saved comment/tag normalization only: dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=79 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=79 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.

No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation occurred.

## Boundary

This wave strengthens the monitor static contract needed for a rebuild-grade specification and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove concrete monitor/sound-event/active-reader/movement/render layouts, exact source-body identity, runtime audio/gameplay behavior, runtime movement/terrain behavior, runtime animation/state behavior, runtime firing animation behavior, runtime render behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1187; wave1187-cmonitor-movement-audio-animation-render-current-risk-review; 793/1179 = 67.26%; 6 CMonitor movement/audio/animation/render current-risk rows; current focused candidates: 1173; live regenerated current focused candidates: 1173; remaining active focused work: 386; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=6 skipped=0; comment_only_updated=6; tags_added=79; final dry updated=0 skipped=6; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CMonitor__UpdateSoundEventPlaybackForReader; CMonitor__IntegrateMovementAgainstTerrain; CMonitor__ComputeTerrainVelocityScalar; CMonitor__CheckSVFAnimationAndAdvanceState; CMonitor__TryQueuePrefireAnimation; CMonitor__UpdateTrackedRenderPair; CMonitor__Process; CMonitor__UpdateMovementTransitionAndEffects; CBattleEngineWalkerPart__Move; CUnit__UpdateDeployStateAndChargeEffects; CSoundManager; CStaticShadows__SampleShadowHeightBilinear; CMesh__FindAnimationIndexByName; SVF; prefire; update_projected_volume; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 914 instruction rows; 6 decompile rows; G:\GhidraBackups\BEA_20260606-151617_post_wave1187_cmonitor_movement_audio_animation_render_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
