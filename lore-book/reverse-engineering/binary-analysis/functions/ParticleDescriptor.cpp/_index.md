# ParticleDescriptor.cpp Functions

Wave1214 math/color/screen dispatch current-risk review (`wave1214-math-color-screen-dispatch-current-risk-review`) re-read `Color32__LerpArgb`, `Math__InvLerpClamp01`, and `CPDSelector__ConvertNormalizedToScreenCoords` with fresh static Ghidra exports. The review confirms the packed ARGB interpolation helper, the clamp-to-0..1 inverse-lerp helper, and the selector normalized-to-screen coordinate conversion path without mutation, rename, signature change, comment change, tag change, function-boundary change, or executable-byte change. Verified backup: `G:\GhidraBackups\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified`. Runtime particle rendering behavior, runtime screen-coordinate output, exact descriptor/layout identity, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1191 current-risk update: Wave1191 (`wave1191-cpdsimplesprite-render-residual-current-risk-review`) accounts for `7 CPDSimpleSprite render residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. It updated `CPDSimpleSprite__SetUVFromTileIndex`, `CPDSimpleSprite__CopyTransformMatrix`, `CPDSimpleSprite__BuildUvAtlasBuckets`, `CPDSimpleSprite__ProcessAndRenderSpriteList`, `CPDSimpleSprite__ScaleVec3InPlace`, `CPDSimpleSprite__ReciprocalVec3Magnitude`, and `CPDSimpleSprite__EvaluateCurveDrivenScale`; anchors include `CVBufTexture__GetVertexPtrAt`, `DXParticleTexture__GetIndexBuffer`, `DAT_00829e58`, and `DAT_0082b39c`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0`, then `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0`, then final dry updated=0 skipped=7. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `826/1179 = 70.06%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 353; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `9 xref rows`, `2369 instruction rows`, and `7 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact CPDSimpleSprite/descriptor/particle/CVBufTexture/DXParticleTexture/global-atlas layouts, runtime particle ordering/culling/rendering behavior, visual parity, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1191; wave1191-cpdsimplesprite-render-residual-current-risk-review; 826/1179 = 70.06%; 7 CPDSimpleSprite render residual current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 353; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=100; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__SetUVFromTileIndex; CPDSimpleSprite__CopyTransformMatrix; CPDSimpleSprite__BuildUvAtlasBuckets; CPDSimpleSprite__ProcessAndRenderSpriteList; CPDSimpleSprite__ScaleVec3InPlace; CPDSimpleSprite__ReciprocalVec3Magnitude; CPDSimpleSprite__EvaluateCurveDrivenScale; CVBufTexture__GetVertexPtrAt; DXParticleTexture__GetIndexBuffer; DAT_00829e58; DAT_0082b39c; 0 / 0 / 0; 6411/6411 = 100.00%; 9 xref rows; 2369 instruction rows; 7 decompile rows; G:\GhidraBackups\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

Wave1190 current-risk update: Wave1190 (`wave1190-particle-descriptor-token-archive-current-risk-review`) accounts for `11 particle descriptor token-writer/TokenArchive current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. It updated `CPDSimpleSprite__WriteTokenFields`, `CPDEmitter__WriteTokenFields`, `CPDSelector__WriteTokenFields`, `CPDColourRange__WriteTokenFields`, `CPDShape__WriteTokenFields`, `CPDTrail__WriteTokenFields`, `CPDFunction__WriteTokenFields`, `CPDMesh__WriteTokenFields`, `CPDFoR__WriteTokenFields`, `CPDPMesh__WriteTokenFields`, and `CTokenArchive__BindIndexedFieldPointer`; xrefs include `CParticleDescriptor__Load`. Ghidra dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0`, then `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0`, then final dry updated=0 skipped=11. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt; expanded static surface remains `1560/1560 = 100.00%`; Wave1108 current focused accounting is `819/1179 = 69.47%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `25 xref rows`, `733 instruction rows`, and `11 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference; exact descriptor/TokenArchive layouts, exact source virtual/source-body identity, runtime particle loading/parsing/rendering/linking behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof. Probe token anchor: Wave1190; wave1190-particle-descriptor-token-archive-current-risk-review; 819/1179 = 69.47%; 11 particle descriptor token-writer/TokenArchive current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=11 skipped=0; comment_only_updated=11; tags_added=123; final dry updated=0 skipped=11; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__WriteTokenFields; CPDEmitter__WriteTokenFields; CPDSelector__WriteTokenFields; CPDColourRange__WriteTokenFields; CPDShape__WriteTokenFields; CPDTrail__WriteTokenFields; CPDFunction__WriteTokenFields; CPDMesh__WriteTokenFields; CPDFoR__WriteTokenFields; CPDPMesh__WriteTokenFields; CTokenArchive__BindIndexedFieldPointer; CParticleDescriptor__Load; 0 / 0 / 0; 6411/6411 = 100.00%; 25 xref rows; 733 instruction rows; 11 decompile rows; G:\GhidraBackups\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.


Wave1150 current-risk update: Wave1150 (`wave1150-particle-set-render-tail-current-risk-review`) accounts for `11 current-risk rows` from the Wave1108 current focused current-risk denominator as a particle set/render tail current-risk review. It uses fresh Ghidra export evidence for particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper, and is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and no Codex subagent. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `355/1179 = 30.11%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; focused threshold `15`; not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1150; wave1150-particle-set-render-tail-current-risk-review; 355/1179 = 30.11%; 11 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; current risk candidates: 6166; particle set/render tail current-risk review; fresh Ghidra export; particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CParticle__ApplyParentTransformOrStoreLink; CPDSimpleSprite__VFunc_10_004c14f0; CPDSimpleSprite__VFunc_23_004c8040; CParticleSet__shared_scalar_deleting_dtor; CPDSelector__DispatchChildVFunc20; CParticleSet__InitType11; CParticleSet__InitType12; CParticleSet__InitType13; CParticleSet__FindByNameAndTrackLinkSlot; CParticleSet__LoadParticleSetFile; CParticleManager__UnlinkNodeByOffset3C40; G:\GhidraBackups\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1149 current-risk update: Wave1149 (`wave1149-particle-effects-score20-current-risk-review`) accounts for `15 current-risk rows` from the Wave1108 current focused current-risk denominator as a particle/effects score20 current-risk review. It uses fresh Ghidra export evidence for particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers, and is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, and no Codex subagent. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `344/1179 = 29.18%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; focused threshold `15`; not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified`. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1149; wave1149-particle-effects-score20-current-risk-review; 344/1179 = 29.18%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; current risk candidates: 6166; particle/effects score20 current-risk review; fresh Ghidra export; particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CEngine__ConfigureParticleBurstForDistance; CParticleDescriptor__Update; CParticleDescriptor__Load; CEngine__ComputeSpriteTintByDistance; CParticleManager__SetParticleResource; CParticleManager__CleanupHandles; ParticleEffectLink__SetHandleStateAndClear; CParticleManager__InterpolatePositions; CParticleManager__CreateEffect; CParticleManager__UpdateParticleAndRecycleIfDead; CParticleManager__ProjectPointToTerrainWithRadiusClamp; CParticleManager__ComputeMinCameraDistanceSqForParticle; CParticleManager__DestroyParticleList; CParticleSet__CreateByType; CParticleSet__Init; G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Source File: ParticleDescriptor.cpp | Binary: BEA.exe
> Debug Path: 0x00630cd8

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Particle effect descriptor definitions. The retail binary has a cluster of descriptor vtable entries that serialize token fields, load descriptor parameters, and update particle instances through `CParticleManager`. Source-family labels remain static retail-binary hypotheses unless separately proven by source parity or runtime evidence.

Wave1031 (`particle-cpdsimplesprite-runtime-transform-review-wave1031`) re-reviewed the particle descriptor / CPDSimpleSprite runtime-transform cluster and saved one correction: `0x004f5b70 CParticleDescriptor__SetIndexedParam` is now `0x004f5b70 CTokenArchive__BindIndexedFieldPointer`. The corrected signature is `void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)`. Fresh xref-window evidence shows `CParticleDescriptor__Load` callsites `0x004c57d4` / `0x004c57e9` plus thirteen adjacent particle descriptor token-load callsites push descriptor field addresses, push the parsed slot index, load `ECX` with the TokenArchive receiver, then call this helper. Context included `0x004f5b80 CTokenArchive__RegisterReferenceFixup`, which writes `fixup_record+4` into the same `this+0x0c+(slot_index*4)` table shape. Post-mutation exports verified 5 primary metadata rows, 5 tag rows, 19 xref rows, 539 body-instruction rows, and 5 decompile rows. Wave911 focused re-audit progress is `626/1408 = 44.46%`; expanded static surface progress is `855/1493 = 57.27%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`; queue closure remains `6238/6238 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified`. Exact source symbol, concrete token-slot semantics, runtime particle parsing/linking/rendering/transform behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1031; particle-cpdsimplesprite-runtime-transform-review-wave1031; 0x004f5b70 CTokenArchive__BindIndexedFieldPointer; 0x004c0150 CParticle__ApplyParentTransformOrStoreLink; 0x004c0940 CPDSimpleSprite__SetUVFromTileIndex; 0x004c5280 CPDSimpleSprite__CopyTransformMatrix; 0x004c5410 CParticleDescriptor__Update; 0x004f5b80 CTokenArchive__RegisterReferenceFixup; 626/1408 = 44.46%; 855/1493 = 57.27%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified; one rename/signature/comment correction.

Wave1007 (`particle-descriptor-token-spine-review-wave1007`) re-reviewed the Wave461 particle descriptor token-writer spine with fresh read-only metadata/tag/xref/instruction/decompile/context/vtable evidence. Primary anchors are `0x004c07f0 CPDSimpleSprite__WriteTokenFields`, `0x004c1970 CPDEmitter__WriteTokenFields`, `0x004c2220 CPDSelector__WriteTokenFields`, `0x004c2400 CPDColourRange__WriteTokenFields`, `0x004c2ca0 CPDShape__WriteTokenFields`, `0x004c3440 CPDTrail__WriteTokenFields`, `0x004c4920 CPDFunction__WriteTokenFields`, `0x004c49b0 CPDMesh__dtor_base`, `0x004c4ae0 CPDMesh__scalar_deleting_dtor`, `0x004c4c70 CPDMesh__WriteTokenFields`, `0x004c53b0 CPDFoR__WriteTokenFields`, `0x004c5410 CParticleDescriptor__Update`, `0x004c5730 CParticleDescriptor__Load`, and `0x004c59e0 CPDPMesh__WriteTokenFields`. Fresh exports verified 14 metadata rows, 14 tag rows, 14 xref rows, 1133 body-instruction rows, 14 decompile rows, 7 context metadata rows, 7 context decompile rows, 2370 context body-instruction rows, 480 vtable-slot rows, and 10 RTTI type rows. No Ghidra mutation, rename, signature change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed. Wave911 focused re-audit progress is `499/1408 = 35.44%`; expanded static surface progress is `676/1478 = 45.74%`; Wave911 top-500 risk-ranked coverage is `398/500 = 79.60%`; queue closure remains `6223/6223 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260531-143106_post_wave1007_particle_descriptor_token_spine_review_verified`. Runtime particle loading/update/rendering behavior, exact source virtual names, concrete descriptor/token/particle/effect layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave963 (`cpdsimplesprite-distance-burst-tint-review-wave963`) re-reviewed the CPDSimpleSprite distance/burst/tint bridge around `0x004c35d0 CEngine__ConfigureParticleBurstForDistance`, `0x004c8060 CEngine__ComputeSpriteTintByDistance`, `0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList`, and `0x004c8040 CPDSimpleSprite__VFunc_23_004c8040`. Fresh metadata/tags/xref/instruction/body-instruction/decompile evidence kept the Wave462 simple-sprite resource-count and tint/fade claims intact; no mutation was needed. Key anchors include `0x004c3645 MOV [ESI + 0x80], ECX`, `0x004c3665 CALL 0x004caed0`, `0x004c8088 FIDIV [EDI + 0x80]`, `0x004c80e7 CALL 0x004c10c0`, and `0x004c767b CVBufTexture__GetVertexPtrAt`. Wave911 focused re-audit progress after this slice is `311/1408 = 22.09%`, while export-contract closure remains `6152/6152 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-135208_post_wave963_cpdsimplesprite_distance_burst_tint_review_verified`. The current source snapshot has high-level `CParticleDescriptor` references but no matching CPDSimpleSprite implementation body, so legacy `CEngine__` owner-prefix labels remain static saved labels rather than exact source-owner proof. Runtime particle rendering behavior, concrete descriptor/particle/CVBufTexture layouts, exact source-body identity, visual output, BEA patching, and rebuild parity remain separate proof.

Wave923 (`hud-radar-pause-render-review-wave923`) re-reviewed `0x004c14f0 CPDSimpleSprite__VFunc_10_004c14f0` and `0x004c8040 CPDSimpleSprite__VFunc_23_004c8040` as part of a HUD/radar/pause/sprite/D3D visible-render support slice. Fresh metadata/tags/xref/instruction/decompile evidence kept the Wave462 simple-sprite descriptor vtable-slot claims intact; no mutation was needed. Wave911 focused re-audit progress after this slice is `86/1408 = 6.11%`, while export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified`. Runtime particle-sprite rendering behavior, concrete descriptor/particle layouts, exact source-body identity, patch behavior, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004c0150 | CParticle__ApplyParentTransformOrStoreLink | Applies parent transform/position inheritance to particle basis/position fields or stores the parent link only | ~528 bytes |
| 0x004c0370 | CParticleDescriptor__PushCurrentToHistoryAndSetNow | Shifts/seeds descriptor value-history slots and refreshes the observed timestamp field | ~224 bytes |
| 0x004c0450 | CParticleDescriptor__Load12DwordsAndMarkDirty | Copies a 12-dword source block into the descriptor transform/cache block and marks it dirty | ~112 bytes |
| 0x004c04c0 | CParticleDescriptor__DispatchTimedParticleNodes | Shared RTTI/vtable-backed slot 23 that dispatches linked particle nodes through a time gate | ~80 bytes |
| 0x004c07f0 | CPDSimpleSprite__WriteTokenFields | Vtable slot 7 token writer for simple-sprite descriptor fields | ~400 bytes |
| 0x004c0940 | CPDSimpleSprite__SetUVFromTileIndex | Computes simple-sprite atlas UV rectangle from tile/frame state | ~300 bytes |
| 0x004c0c70 | CPDSimpleSprite__EvalExpressionNode | Recursive x87 expression-node scalar evaluator for simple-sprite channels | ~2,200 bytes |
| 0x004c14f0 | CPDSimpleSprite__VFunc_10_004c14f0 | Vtable slot 10 per-particle sprite state update helper | ~1,000 bytes |
| 0x004c1970 | CPDEmitter__WriteTokenFields | Vtable slot 7 token writer for emitter descriptor fields | ~300 bytes |
| 0x004c2220 | CPDSelector__WriteTokenFields | Vtable slot 7 token writer for selector pointer/int fields | ~200 bytes |
| 0x004c2400 | CPDColourRange__WriteTokenFields | Vtable slot 7 token writer for colour-range float/int fields | ~250 bytes |
| 0x004c2ca0 | CPDShape__WriteTokenFields | Vtable slot 7 token writer for shape fields | ~200 bytes |
| 0x004c3440 | CPDTrail__WriteTokenFields | Vtable slot 7 token writer for trail fields | ~450 bytes |
| 0x004c35d0 | CEngine__ConfigureParticleBurstForDistance | Configures particle resource records and distance-derived burst counts | ~700 bytes |
| 0x004c4920 | CPDFunction__WriteTokenFields | Vtable slot 7 token writer for function-curve fields | ~200 bytes |
| 0x004c49b0 | CPDMesh__dtor_base | CPDMesh destructor-base body that releases the +0x5c resource pointer | ~80 bytes |
| 0x004c4ae0 | CPDMesh__scalar_deleting_dtor | CPDMesh scalar-deleting destructor wrapper | ~40 bytes |
| 0x004c4c70 | CPDMesh__WriteTokenFields | Vtable slot 7 token writer for mesh descriptor fields | ~200 bytes |
| 0x004c5280 | CPDSimpleSprite__CopyTransformMatrix | Copies observed simple-sprite transform/basis fields to an output block | ~160 bytes |
| 0x004c53b0 | CPDFoR__WriteTokenFields | Vtable slot 7 token writer for frame-of-reference pointer fields | ~80 bytes |
| 0x004c5410 | CParticleDescriptor__Update | Update vtable entry for effect handle/list state and fallback particle allocation | ~800 bytes |
| 0x004c5730 | CParticleDescriptor__Load | Load vtable entry for token archive parsing and reference fixups | ~700 bytes |
| 0x004c59e0 | CPDPMesh__WriteTokenFields | Vtable slot 7 token writer for particle-mesh fields | ~400 bytes |
| 0x004c5c50 | CPDSimpleSprite__BuildUvAtlasBuckets | Initializes five UV atlas bucket tables | ~250 bytes |
| 0x004c5d50 | CPDSimpleSprite__ProcessAndRenderSpriteList | Processes active sprite particles and emits quad vertices/indices | ~7,000 bytes |
| 0x004c78b0 | CPDSimpleSprite__ScaleVec3InPlace | Scales a three-float vector in place | ~30 bytes |
| 0x004c78d0 | CPDSimpleSprite__ReciprocalVec3Magnitude | Returns reciprocal vector magnitude for three float components | ~120 bytes |
| 0x004c7950 | CPDSimpleSprite__EvaluateCurveDrivenScale | Evaluates expression-driven scalar/curve output modes for sprite paths | ~1,700 bytes |
| 0x004c7db0 | CPDSimpleSprite__InitNoiseTableOnce | One-shot wrapped 32x32 noise-table initializer for simple-sprite render paths | ~650 bytes |
| 0x004c8040 | CPDSimpleSprite__VFunc_23_004c8040 | Vtable slot 23 noise-init/render-list dispatch wrapper | ~30 bytes |
| 0x004c8060 | CEngine__ComputeSpriteTintByDistance | Computes packed sprite tint/alpha from expression curves and fade context | ~2,800 bytes |
| 0x004cab30 | Color32__LerpArgb | Linearly interpolates packed ARGB bytes | ~250 bytes |
| 0x004cac40 | Math__InvLerpClamp01 | Computes clamped inverse lerp in the 0..1 range | ~60 bytes |
| 0x004cac80 | CPDSelector__ConvertNormalizedToScreenCoords | Converts normalized selector coordinates through screen-scale rounding | ~100 bytes |
| 0x004ccc50 | CPDSelector__DispatchChildVFunc20 | Walks selector child descriptor pointer slots at `+0x5c..+0x68` and dispatches each child vfunc `+0x20` with the caller context | ~96 bytes |
| 0x004f5b70 | CTokenArchive__BindIndexedFieldPointer | TokenArchive indexed field-pointer binder used by particle descriptor token-load paths; stores `field_ptr` at `this+0x0c+(slot_index*4)` | ~16 bytes |

## Wave867 CVBufTexture Cursor Callsite Context

Wave963 re-read this cursor context as part of the CPDSimpleSprite distance/burst/tint review. The fresh xref/body evidence keeps `0x00550200 CVBufTexture__GetVertexPtrAt` tied to `0x004c767b CPDSimpleSprite__ProcessAndRenderSpriteList` and the second sprite-path callsite at `0x004c8a09`; no CVBufTexture mutation was needed. Probe token anchor: Wave963; cpdsimplesprite-distance-burst-tint-review-wave963; 0x004c35d0 CEngine__ConfigureParticleBurstForDistance; 0x004c8060 CEngine__ComputeSpriteTintByDistance; 0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList; 0x004c8040 CPDSimpleSprite__VFunc_23_004c8040; 0x004c3645 MOV [ESI + 0x80], ECX; 0x004c3665 CALL 0x004caed0; 0x004c8088 FIDIV [EDI + 0x80]; 0x004c80e7 CALL 0x004c10c0; 0x004c767b CVBufTexture__GetVertexPtrAt; 311/1408 = 22.09%; 6152/6152 = 100.00%; G:\GhidraBackups\BEA_20260528-135208_post_wave963_cpdsimplesprite_distance_burst_tint_review_verified; no mutation.

Wave867 CVBufTexture cursor (`cvbuftexture-cursor-wave867`, `wave867-readback-verified`) records CPDSimpleSprite callsite context for three adjacent CVBufTexture vertex-buffer cursor helpers. Probe token anchor: `Wave867 CVBufTexture cursor`; `cvbuftexture-cursor-wave867`; `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne`; `int __thiscall CVBufTexture__GetVertexWriteCursorPlusOne(void * this)`; `0x005501e0 CVBufTexture__ReserveOneVertex`; `void __thiscall CVBufTexture__ReserveOneVertex(void * this, void * vertex_src)`; `0x00550200 CVBufTexture__GetVertexPtrAt`; `void __thiscall CVBufTexture__GetVertexPtrAt(void * this, int vertex_count, void * * out_vertex_ptr, int * out_start_index)`; `CPDSimpleSprite`; low local-evidence-density but important connective renderer infrastructure; `0x005508a0 CDXEngine__ClearMatrixBlock`; `5823/6105 = 95.38%`; `G:\GhidraBackups\BEA_20260525-165414_post_wave867_cvbuftexture_cursor_verified`.

The CPDSimpleSprite render-list body calls `CVBufTexture__GetVertexPtrAt` at `0x004c767b` with `vertex_count` 4 plus stack-local output pointers before writing quad vertices. A second sprite-path callsite at `0x004c8a09` has the same `vertex_count` 4 pattern. Additional xrefs at `0x004c970f`, `0x004ca24d`, `0x004ca180`, and `0x004caa6f` use or reserve the cached sprite vertex index. This is static retail Ghidra evidence only; exact sprite-particle source-body identity, exact CVBufTexture field names/layouts, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.

## Wave833 Particle SetIndexedParam Read-Back (superseded by Wave1031 owner correction)

Wave833 particle SetIndexedParam static read-back (`particle-set-indexed-param-wave833`, `wave833-readback-verified`) saved a bounded signature/comment/tag correction for the row then named `0x004f5b70 CParticleDescriptor__SetIndexedParam`. Wave1031 supersedes the owner/name and parameter labels with `0x004f5b70 CTokenArchive__BindIndexedFieldPointer` / `void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)`, while preserving the useful Wave833 arity finding: `RET 0x8` proves two stack arguments after the `thiscall` receiver. Verified Wave833 backup: `G:\GhidraBackups\BEA_20260524-233838_post_wave833_particle_set_indexed_param_verified`. Wave1031 verified backup: `G:\GhidraBackups\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified`.

| Address | Saved signature | Static read-back evidence |
| --- | --- | --- |
| 0x004f5b70 | `void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)` | Loads `slot_index` from `ESP+0x4`, loads `field_ptr` from `ESP+0x8`, stores `field_ptr` at `this+0x0c+(slot_index*4)`, and returns with `RET 0x8`; `CParticleDescriptor__Load` callsites `0x004c57d4` and `0x004c57e9` push descriptor field addresses and load `ECX` with the TokenArchive receiver. |
| 0x004f5b80 | `CTokenArchive__RegisterReferenceFixup` context | Exact anchor `0x004f5b80 CTokenArchive__RegisterReferenceFixup`: adjacent helper records a reference fixup and then writes the same indexed slot shape, anchoring the setter in the TokenArchive descriptor load/fixup cluster. |

This is saved static retail Ghidra evidence only. Exact source body identity, concrete descriptor subclass or field enum identity, runtime particle parsing behavior, BEA patching, and rebuild parity remain deferred.

## Wave821 CPDSimpleSprite Expression/Noise Read-Back

Wave821 CPDSimpleSprite expression/noise static read-back (`cpdsimplesprite-expression-noise-wave821`, `wave821-readback-verified`) saved comments/tags/signatures for `0x004c0c70 CPDSimpleSprite__EvalExpressionNode` and `0x004c7db0 CPDSimpleSprite__InitNoiseTableOnce`. Verified backup: `G:\GhidraBackups\BEA_20260524-173755_post_wave821_cpdsimplesprite_expression_noise_verified`. Queue after Wave821 is `6098` total, `5622` commented, `476` commentless, strict proxy `5622/6098 = 92.19%`; next raw commentless row is `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`.

| Address | Saved signature | Static read-back evidence |
| --- | --- | --- |
| 0x004c0c70 | `double __cdecl CPDSimpleSprite__EvalExpressionNode(float base_value, void * post_scale_node, void * pre_scale_node, void * pre_offset_node, void * post_offset_node, int operator_id, int output_mode, float time_scale)` | Returns through x87 ST0; self-recursive calls at `0x004c0d2c`, `0x004c0ddf`, `0x004c0f3a`, and `0x004c0fec`; optionally bridges nested nodes through `CPDSimpleSprite__EvaluateExpressionRecursive`; observed operator cases include square, exp-style x87 `f2xm1`/`fscale`, sin, cos, reciprocal, ln2-scale, and rand jitter before clamp/wrap-style output handling. |
| 0x004c7db0 | `void __cdecl CPDSimpleSprite__InitNoiseTableOnce(void)` | One-shot initializer gated by `DAT_0082b398`; clears the `0x400`-dword `DAT_0082a358` table; fills a wrapped `32x32` float grid from `_rand` midpoint/diamond-style blends; direct xrefs include `0x004c5d5e`, `0x004c8043`, and orphan block `0x004c900c`. |

The initial dry compile failure is preserved in evidence and came from a Java API signature mismatch before mutation. Accepted dry/apply/final-dry then completed with `missing=0 bad=0`. Exact expression-node layout, exact operator names, exact procedural-noise source algorithm, runtime particle rendering behavior, exact source-body identity, BEA patching, and rebuild parity remain deferred.

## Wave761 Unwind Continuation Read-Back

Wave761 static read-back (`unwind-continuation-wave761`, `wave761-readback-verified`) saved `0x005d4040 Unwind@005d4040` as a `void __cdecl Unwind@005d4040(void)` compiler-generated SEH unwind allocation-cleanup callback tied to the ParticleDescriptor.cpp debug path at `0x00630cd8`. DATA scope-table xref `0x0061cbe4` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback(*(EBP-0xa4))` with line token `0x10` and allocation/type value `0x7e9`. Verified backup: `G:\GhidraBackups\BEA_20260523-140318_post_wave761_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime particle-descriptor cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave476 Read-Back

Wave476 saved the `0x004c0150` owner/signature/comment/tag correction in Ghidra on 2026-05-17.

- Apply script: `tools/ApplyParticleParentTransformWave476.java`
- Probe: `tools/ghidra_particle_parent_transform_wave476_probe.py`
- Evidence directory: `subagents/ghidra-static-reaudit/wave476-particle-boundary-004c0150/`
- Dry/apply/verify-dry summaries: dry `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`; apply `updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified the target metadata/signature/comment, expected tags, raw caller xref from `0x004c524f`, target decompile export, allocation/push/call evidence in the raw caller range, `RET 0x0c` callee epilogues at `0x004c016b` and `0x004c035f`, and focused probe status `PASS`.
- The function is now `CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)`. Nonzero `link_parent_only` stores `parent_particle` at `particle+0x58`; otherwise the helper composes particle basis/position fields through the parent transform when present and then adds parent position into the particle position fields.
- The surrounding raw caller boundary remains deferred. Wave476 did not create a function for the `0x004c51f7..0x004c5274` region and does not prove exact particle layout, source identity, runtime particle behavior, or rebuild parity.

## Wave468 Read-Back

Wave468 saved three adjacent descriptor/list helper signatures/comments/tags in Ghidra on 2026-05-16.

- Apply script: `tools/ApplyParticleDescriptorWave468.java`
- Probe: `tools/ghidra_particle_descriptor_wave468_probe.py`
- Evidence directory: `subagents/ghidra-static-reaudit/wave468-cunitai-particle-current/`
- Dry/apply/verify-dry summaries: dry `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`; apply `updated=5 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified `5` metadata rows, `5` tag rows, `22` xref rows, `5` decompile exports plus `index.tsv`, `1105` instruction rows, `13` RTTI type rows, `416` vtable-slot rows, and focused probe status `PASS`.
- The shared slot-23 dispatch is present in the RTTI/vtable slices for `CParticleDescriptor`, `CPDMesh`, `CPDFunction`, `CPDMover`, `CPDTrail`, `CPDShape`, `CPDTimeline`, `CPDColourRange`, `CPDSelector`, `CPDModifier`, `CPDEmitter`, `CPDFoR`, and `CPDPMesh`.
- Candidate `0x004c0150` was left unchanged in Wave468 because its then-current `CUnitAI` ownership looked suspicious beside the particle/CPD region. Wave476 later corrected it to `CParticle__ApplyParentTransformOrStoreLink`; the raw caller boundary remains deferred.

## Wave464 Read-Back

Wave464 saved the `CPDSelector__DispatchChildVFunc20` name/signature/comment/tags in Ghidra on 2026-05-16.

- Apply script: `tools/ApplyParticleSetTailWave464.java`
- Probe: `tools/ghidra_particleset_tail_wave464_probe.py`
- Evidence directory: `subagents/ghidra-static-reaudit/wave464-particleset-tail-current/`
- Dry/apply/verify-dry summaries: dry `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`; apply `updated=8 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `21` xref rows, `8` decompile exports plus `index.tsv`, `1448` instruction rows, and focused probe status `PASS`.

## Wave462 Read-Back

Wave462 saved the signatures/comments/tags for the particle sprite/render helper rows above in Ghidra on 2026-05-16.

- Apply script: `tools/ApplyParticleSpriteRenderWave462.java`
- Probe: `tools/ghidra_particle_sprite_render_wave462_probe.py`
- Evidence directory: `subagents/ghidra-static-reaudit/wave462-particle-sprite-render-current/`
- Dry/apply/verify-dry summaries: dry `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; apply `updated=14 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified `14` metadata rows, `14` tag rows, `18` xref rows, `14` decompile exports plus `index.tsv`, `798` instruction rows, and focused probe status `PASS`.

## Wave461 Read-Back

Wave461 saved the token-writer and lifecycle names/signatures/comments/tags in Ghidra on 2026-05-16.

- Apply script: `tools/ApplyParticleDescriptorWave461.java`
- Probe: `tools/ghidra_particle_descriptor_wave461_probe.py`
- Evidence directory: `subagents/ghidra-static-reaudit/wave461-particle-descriptor-current/`
- Dry/apply/verify-dry summaries: dry `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=12 missing=0 bad=0`; apply `updated=14 skipped=0 created=0 would_create=0 renamed=12 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Post exports verified `22` metadata rows, `22` tag rows, `24` xref rows, `22` decompile exports plus `index.tsv`, `2662` instruction rows, and focused probe status `PASS`.

## Unresolved Xrefs

Two additional xrefs to the debug path exist at addresses without defined functions:

| From Address | Context | Notes |
|--------------|---------|-------|
| 0x004c05cd | Inside undefined code region | Likely CParticle class method |
| 0x004c312d | Inside undefined code region | Likely CParticle class method |
| 0x005d4040 | Unwind@005d4040 | Exception handler for Update |

## Key Observations

- **UV atlas helpers** - `CPDSimpleSprite__SetUVFromTileIndex` writes the observed UV rectangle at `+0xb8..+0xc4`, and `CPDSimpleSprite__BuildUvAtlasBuckets` initializes the five global atlas bucket tables under `DAT_00829e58`.
- **Sprite render list** - `CPDSimpleSprite__ProcessAndRenderSpriteList` walks active sprite particles, applies noise/expression/visibility/distance paths, and emits quad vertices plus six indices through `CVBufTexture` / `DXParticleTexture` buffers.
- **Expression/noise helpers** - Wave821 hardens `CPDSimpleSprite__EvalExpressionNode` as the recursive x87 scalar evaluator and `CPDSimpleSprite__InitNoiseTableOnce` as the `DAT_0082b398`-gated initializer for the wrapped `DAT_0082a358` 32x32 noise table.
- **Vector and curve math** - Wave462 records in-place vec3 scaling, reciprocal magnitude, expression-driven scalar evaluation, packed ARGB interpolation, and inverse-lerp clamping as static helper evidence.
- **Tint and coordinate helpers** - `CEngine__ComputeSpriteTintByDistance` computes a packed sprite tint/alpha value from expression colour curves and fade context; `CPDSelector__ConvertNormalizedToScreenCoords` scales normalized selector coordinates through CRT rounding without a proven stable output contract.
- **Value-history helpers** - `CParticleDescriptor__PushCurrentToHistoryAndSetNow` shifts or seeds the observed current/history slots around a `10000.0` first-sample sentinel and refreshes a timestamp/age field from `DAT_00672fd0` unless the `-1.0` sentinel disables it.
- **Transform/cache helper** - `CParticleDescriptor__Load12DwordsAndMarkDirty` copies twelve dwords into the descriptor-owned block at `+0x10` and marks the block dirty/active at `+0xa0` when present.
- **Timed node dispatch** - `CParticleDescriptor__DispatchTimedParticleNodes` walks the linked particle-node list at `this+0x54` and dispatches node vfunc `+0x2c` when the caller disables the time gate or the observed node timestamp passes the comparison against `DAT_005d856c`.
- **Token writer family** - Slot-7 descriptor helpers serialize observed fields with `CTokenArchive__WriteInt`, `WriteFloat`, `WriteFloatPointer`, `WritePointer`, and `WriteString`.
- **Indexed TokenArchive setters** - Wave833 hardens `CParticleDescriptor__SetIndexedParam` as the shared descriptor slot setter that stores a token-loaded value at `this+0x0c+(field_index*4)`; adjacent `CTokenArchive__RegisterReferenceFixup` uses the same indexed-slot shape after recording a fixup pointer.
- **Linked to ParticleManager** - `CParticleDescriptor__Update` calls `CParticleManager__CreateEffect` and `CParticleManager__AllocateParticle`.
- **Memory allocation** - `CParticleDescriptor__Update` and `CParticleDescriptor__Load` use `OID__AllocObject` with debug path `C:\dev\ONSLAUGHT2\ParticleDescriptor.cpp`.
- **Effect handle system** - Update creates effect handles stored at particle offset `0x88` when the `0x7e` flag is clear.
- **Position inheritance** - Update can inherit position/transform data from parent particle offset `0x58`; Wave476 identifies `0x004c0150` as the parent-transform/link helper that stores that parent pointer or composes child particle basis/position fields through the parent transform.
- **Flag copying** - Update copies the observed `0xb6` word between related particles when parent/effect state is available.
- **Reference fixups** - Load loops `CTokenArchive__ReadNextToken` and registers pointer/reference fixups for token ids `0x6b` through `0x7b` where the descriptor stores indexed vector-like fields.

## Descriptor Structure (Partial)

Based on `CParticleDescriptor__Load` switch cases. Field labels below are descriptive placeholders, not source-proven names.

| Offset | Field | Case ID | Notes |
|--------|-------|---------|-------|
| 0x5c | mEffectType | 0x3f | Primary effect type |
| 0x60 | mSecondaryType | 0x1b | Secondary effect |
| 0x64 | mResource | 0x0b | Resource array |
| 0x68 | mResourceCount | 0x0d | Number of resources |
| 0x6c | mName | 0x10 | String name |
| 0x70 | mTextureName | 0x74 | Texture string |
| 0x74-0x7c | mColorStart | 0x6b | Start color (RGB?) |
| 0x7c-0x84 | mColorEnd | 0x6c | End color (RGB?) |
| 0x84-0x8c | mScaleStart | 0x6d | Start scale |
| 0x8c-0x94 | mScaleEnd | 0x6e | End scale |
| 0x94 | mLifetime | 0x6f | Effect duration |
| 0x98 | mSpawnRate | 0x70 | Particle spawn rate |
| 0x9c-0xa4 | mVelocity | 0x71 | Initial velocity |
| 0xa4-0xac | mAcceleration | 0x72 | Acceleration |
| 0xac-0xb4 | mRandomness | 0x73 | Random variation |
| 0xb4 | mGravity | 0x75 | Gravity multiplier |
| 0xb8 | mDrag | 0x76 | Air resistance |
| 0xbc-0xc4 | mRotation | 0x78 | Rotation params |
| 0xc4-0xcc | mRotationRate | 0x79 | Angular velocity |
| 0xcc-0xd4 | mSpin | 0x7a | Spin params |
| 0xd4-0xdc | mSpinRate | 0x7b | Spin velocity |
| 0xdc-0xe4 | mBlendMode | 0x77 | Blend/alpha mode |

## Update Function Analysis

`CParticleDescriptor__Update` (`0x004c5410`):
1. Copies visibility flag (0xB6) from parent to child particle
2. Calls virtual function at offset 0x30 on resource (position update?)
3. On first call (flag at 0x7E == 0), allocates effect handle
4. Iterates effect type list at offset 0x5C to create effects
5. Updates position by adding parent position to local offset
6. Copies transform matrix (12 floats) from source
7. If effect handle allocation fails, allocates fallback particle via AllocateParticle

## Boundary

This page documents static retail-binary evidence only. Runtime particle rendering/loading behavior, exact descriptor and particle layouts, exact Stuart-source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Related Files

- ParticleManager.cpp - Manages particle instances created from descriptors
- BattleEngine.cpp - Creates combat particle effects
- Unit.cpp - Unit destruction effects

---
*Updated via Wave476 static read-back (2026-05-17).*
