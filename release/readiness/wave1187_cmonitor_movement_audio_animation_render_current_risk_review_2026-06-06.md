# Wave1187 CMonitor Movement / Audio / Animation / Render Current-Risk Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`); `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`); `0x00411630` → `CBattleEngineJetPart__HandleGroundEffect` (was `CMonitor__IntegrateMovementAgainstTerrain`); `0x00411aa0` → `CBattleEngineJetPart__GetFriction` (was `CMonitor__ComputeTerrainVelocityScalar`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **Owner/name supersession (2026-07-12):** the Wave1187 exports and mutation
> log remain historical evidence. Current static evidence reassigns
> `0x00411630` to `CBattleEngineJetPart__HandleGroundEffect` and `0x00411aa0`
> to `CBattleEngineJetPart__GetFriction`; their caller is
> `0x00410c50 CBattleEngineJetPart__Move`, reached from
> `0x004081c0 CBattleEngine__Move`. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: complete static current-risk comment/tag normalization; artifact commit `ad48dcdc3def8645e4b717b4beeb645b8e316e40`; state closeout commit `f15722628d73b96e36d851ec7249fc8266c6a87c`; handoff pointer `25cbb46928c123c29519095bd5b36ba245f39bf5`; pushed to origin/main
Date: 2026-06-06
Scope: `wave1187-cmonitor-movement-audio-animation-render-current-risk-review`

Wave1187 accounts for `6 CMonitor movement/audio/animation/render current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator:

- `0x00409950 CMonitor__UpdateSoundEventPlaybackForReader`
- `0x00411630 CMonitor__IntegrateMovementAgainstTerrain`
- `0x00411aa0 CMonitor__ComputeTerrainVelocityScalar`
- `0x0044e2c0 CMonitor__CheckSVFAnimationAndAdvanceState`
- `0x0047d3b0 CMonitor__TryQueuePrefireAnimation`
- `0x005078f0 CMonitor__UpdateTrackedRenderPair`

The saved Ghidra names/signatures were already bounded. The pass normalized saved comments and tags only; it made no rename, no signature change, no function-boundary change, and no executable-byte change.

Evidence:

- Ghidra dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=79 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 tags_added=79 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh exports after apply: `6` metadata rows, `6` tag rows, `7 xref rows`, `914 instruction rows`, and `6` decompile rows.
- Queue refresh after apply: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-151617_post_wave1187_cmonitor_movement_audio_animation_render_current_risk_review_verified`, `19` files, `176163719` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `793/1179 = 67.26%`, current focused candidates: 1173, live regenerated current focused candidates: 1173, remaining active focused work: 386, current risk candidates: 6166.

Static contract:

`CMonitor__UpdateSoundEventPlaybackForReader` is called by `CMonitor__Process` and coordinates sound-event playback through `CSoundManager` plus active-reader state. `CMonitor__IntegrateMovementAgainstTerrain` and `CMonitor__ComputeTerrainVelocityScalar` are called by `CMonitor__UpdateMovementTransitionAndEffects` and connect terrain/static-shadow sampling to movement-object velocity/orientation response. `CMonitor__CheckSVFAnimationAndAdvanceState` gates state advancement on the `SVF` animation token through `CMesh__FindAnimationIndexByName`. `CMonitor__TryQueuePrefireAnimation` is a `CGroundVehicle` vtable-slot helper that checks deploy/charge state and queues the `prefire` animation through `CUnit__UpdateDeployStateAndChargeEffects`. `CMonitor__UpdateTrackedRenderPair` is called by both `CMonitor__UpdateMovementTransitionAndEffects` and `CBattleEngineWalkerPart__Move`, preserving the explicit `update_projected_volume` flag while updating tracked render pair state.

One Codex read-only consult was used and recommended this monitor movement/audio/animation/render slice. No Cursor/Composer was used.

Mutation boundary:

- Comment/tag normalization only.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference from the original game.

Not proven here: concrete monitor/sound-event/active-reader/movement/render layouts, exact source-body identity, runtime audio/gameplay behavior, runtime movement/terrain behavior, runtime animation/state behavior, runtime firing animation behavior, runtime render behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1187; wave1187-cmonitor-movement-audio-animation-render-current-risk-review; 793/1179 = 67.26%; 6 CMonitor movement/audio/animation/render current-risk rows; current focused candidates: 1173; live regenerated current focused candidates: 1173; remaining active focused work: 386; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=6 skipped=0; comment_only_updated=6; tags_added=79; final dry updated=0 skipped=6; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CMonitor__UpdateSoundEventPlaybackForReader; CMonitor__IntegrateMovementAgainstTerrain; CMonitor__ComputeTerrainVelocityScalar; CMonitor__CheckSVFAnimationAndAdvanceState; CMonitor__TryQueuePrefireAnimation; CMonitor__UpdateTrackedRenderPair; CMonitor__Process; CMonitor__UpdateMovementTransitionAndEffects; CBattleEngineWalkerPart__Move; CUnit__UpdateDeployStateAndChargeEffects; CSoundManager; CStaticShadows__SampleShadowHeightBilinear; CMesh__FindAnimationIndexByName; SVF; prefire; update_projected_volume; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 914 instruction rows; 6 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-151617_post_wave1187_cmonitor_movement_audio_animation_render_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
