# vbuftexture.cpp - Vertex Buffer Texture System

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004c8060` comment correction; `0x00500e70` comment correction; `0x00500fa0` comment correction; `0x005010e0` comment correction; `0x00558fb0` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

**Source File:** `[maintainer-local-source-export-root]\vbuftexture.cpp`
**Debug Path Address:** `0x00633d5c`
**Function Range:** `0x005003f0` - `0x005015c0`

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

The CVBufTexture class combines vertex buffers with texture data for efficient rendering. It wraps D3D vertex/index buffers and associates them with textures for batched rendering operations. This is a higher-level abstraction over the raw CVBuffer class (from vbuffer.cpp).

Wave904 (`texture-render-static-review-wave904`) reviews CVBufTexture as part of the `static-coherent texture/resource/decode/render core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The reviewed slice covers `1289` rows across `25` selected families, including `CDXTexture` `366`, `CFastVB` `347`, `CTexture` `233`, and `CVBufTexture` `40`; CVBufTexture anchors include `CVBufTexture__DrawSpriteEx`, `CVBufTexture__Render`, `CVBufTexture__RenderModePass`, and `CVBufTexture__RenderDynamicUnitPass`, with cross-system anchors `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, and `CFastVB__RenderTriangleStripImmediate`. Asset bridge counts include `847/847` loose textures and `352/352` model material/texture-binding rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`.

Wave963 (`cpdsimplesprite-distance-burst-tint-review-wave963`) re-read the CPDSimpleSprite vertex-cursor bridge through `0x00550200 CVBufTexture__GetVertexPtrAt` while reviewing `0x004c35d0 CEngine__ConfigureParticleBurstForDistance`, `0x004c8060 CEngine__ComputeSpriteTintByDistance`, `0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList`, and `0x004c8040 CPDSimpleSprite__VFunc_23_004c8040`. Fresh xrefs preserve the CPDSimpleSprite calls at `0x004c767b` and `0x004c8a09`; no CVBufTexture mutation was needed. Probe token anchor: Wave963; cpdsimplesprite-distance-burst-tint-review-wave963; 0x004c35d0 CEngine__ConfigureParticleBurstForDistance; 0x004c8060 CEngine__ComputeSpriteTintByDistance; 0x004c5d50 CPDSimpleSprite__ProcessAndRenderSpriteList; 0x004c8040 CPDSimpleSprite__VFunc_23_004c8040; 0x004c3645 MOV [ESI + 0x80], ECX; 0x004c3665 CALL 0x004caed0; 0x004c8088 FIDIV [EDI + 0x80]; 0x004c80e7 CALL 0x004c10c0; 0x004c767b CVBufTexture__GetVertexPtrAt; 311/1408 = 22.09%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-135208_post_wave963_cpdsimplesprite_distance_burst_tint_review_verified; no mutation. Runtime particle rendering behavior, exact descriptor/particle/CVBufTexture layouts, exact source-owner or source-body identity, visual output, BEA patching, and rebuild parity remain separate proof.

## 2026-05-26 Wave887 Texture Dispatch/Interpolation Tail Context

Wave887 texture dispatch/interpolation tail (`texture-dispatch-interpolation-tail-wave887`, `wave887-readback-verified`) saved comments/tags for `0x0057600b CVBufTexture__DispatchTextureTransformThunk` and companion texture/math dispatch rows. Probe token anchor: `Wave887 texture dispatch/interpolation tail`; `texture-dispatch-interpolation-tail-wave887`; `0x005759b6 CFastVB__DispatchIndirect_00657014`; `0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3`; `0x00575b47 Math__InterpolateVec2Cubic`; `0x00575dc9 CFastVB__HermiteInterpolateVec3`; `0x0057600b CVBufTexture__DispatchTextureTransformThunk`; `0x00576161 CFastVB__DispatchIndirectByGlobalTable`; dispatch slots `0x00657014` and `0x00656f58`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `6008/6113 = 98.28%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-030217_post_wave887_texture_dispatch_interpolation_tail_verified`.

Static evidence ties `CVBufTexture__DispatchTextureTransformThunk` to dispatch slot `0x00656f34`, `CVBufTexture__RenderDynamicUnitPass`, `CVertexShader__ApplyRenderStateShaderConstants`, `CVertexShader__ApplyCustomRenderStateShaderConstants`, and `CVBufTexture__RenderModePass`. Exact dispatch-table slot targets, exact CPU feature policy, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave876 Texture Core Tail Context

Wave876 texture core tail (`texture-core-tail-wave876`, `wave876-readback-verified`) saved comments/tags/signatures for the CVBufTexture-side connector rows `0x005588f0 CVBufTexture__RenderModePass` and `0x00558ef0 CVBufTexture__SetupSecondaryBlend`, plus texture/engine companions including `0x00556cc0 CTexture__ctor`, `0x00557a90 CDXTexture__LoadTextureFromFile_Core`, `0x00558690 CDXTexture__GetAnimatedFrame`, and `0x0055a0f0 CEngine__TextureFormatIndexToD3D`. Probe token anchor: `Wave876 texture core tail`; `texture-core-tail-wave876`; `0x00556cc0 CTexture__ctor`; `0x00557a90 CDXTexture__LoadTextureFromFile_Core`; `0x00558690 CDXTexture__GetAnimatedFrame`; `0x005588f0 CVBufTexture__RenderModePass`; `0x0055a0f0 CEngine__TextureFormatIndexToD3D`; high-importance texture/resource/render connector rows with low local evidence density, not low-importance filler; `0x0055b0e0 CWaterRenderSystem__ctor`; `5885/6113 = 96.27%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-212045_post_wave876_texture_core_tail_verified`.

Static evidence ties `CVBufTexture__RenderModePass` to `CVBufTexture__Render`, `CMeshRenderer__RenderMeshWithLayerPasses`, and Wave875 `CVBufTexture__DrawSpriteEx`, with render-mode field `this+0x88`, transform fields `this+0x94/+0x98/+0x8c/+0x90`, D3DStateCache/RenderState modes 0-5, and secondary blend setup. `CVBufTexture__SetupSecondaryBlend` checks `CDXTexture__IsResourceHandleValid(DAT_009cc118)`, `DAT_009cc124`, stage-1 state, and render-state color `0x3c`. Exact CVBufTexture layout, render-mode enum names, runtime visual output, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave875 CVBufTexture DrawSprite Read-Back

Wave875 CVBufTexture DrawSprite static read-back (`cvbuftexture-drawsprite-wave875`, `wave875-readback-verified`) saved the signature/comment/tags for `0x00555be0 CVBufTexture__DrawSpriteEx`. Probe token anchor: `Wave875 CVBufTexture DrawSprite`; `cvbuftexture-drawsprite-wave875`; `0x00555be0 CVBufTexture__DrawSpriteEx`; `void __cdecl CVBufTexture__DrawSpriteEx(float screen_x, float screen_y, float depth_z, void * texture, int anchor_or_blend_mode, int uv_mode, float uv_or_tile_scale, float rotation_radians, float argb_tint_bits, float width_scale, float height_scale, float u0, float u1, float v0, float v1)`; `91 xrefs`; `texture+0xac`; `texture+0xb0`; `texture+0xb2`; `CFastVB__RenderTriangleStripImmediate`; high-importance renderer/HUD/frontend connective infrastructure with low local evidence density, not low-importance filler; `0x00556cc0 CTexture__ctor`; `5873/6113 = 96.07%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-205138_post_wave875_cvbuftexture_drawsprite_verified`.

Static evidence ties this central sprite-quad emitter to loading-screen, game-interface, HUD, briefing-log, message-log, pause-menu, menu item, battle-line, compass, imposter, mouse-cursor, and `CDXSurf__RenderSurface` callers. The body reads texture dimensions/shift fields at `texture+0xac/+0xb0/+0xb2`, applies anchor/alignment cases `1-8`, clamps depth/w, optionally halves RGB tint under `DAT_008557f4 == 5`, builds four 7-float `x/y/z/w/color/u/v` vertices with uv-mode cases `0-4`, optionally rotates by `rotation_radians` using `fcos`/`fsin`, calls the texture vtable slot `+0x20`, applies pending render state, calls `CVBufTexture__RenderModePass`, locks global `CFastVB` `DAT_00897a98`, optionally scales through platform window size, emits via `CFastVB__RenderTriangleStripImmediate`, and restores D3DStateCache slot mode.

Post-Wave875 queue telemetry is `6113` total, `5873` commented, `240` commentless, strict proxy `5873/6113 = 96.07%`; next raw commentless row is `0x00556cc0 CTexture__ctor`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260525-205138_post_wave875_cvbuftexture_drawsprite_verified`. Exact `CVBufTexture` and texture object layouts, exact enum names for anchor/blend mode and uv mode, exact uv/tile semantics, runtime visual output, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave873 Render Multipass Context

Wave873 render multipass (`render-multipass-wave873`, `wave873-readback-verified`) owner-corrected the stale dynamic-pass render-queue targets reached from `CVBufTexture__RenderDynamicUnitPass`. Probe token anchor: `Wave873 render multipass`; `render-multipass-wave873`; `0x00553960 CRenderQueue__RenderMultipassLayerA`; `0x00554170 CRenderQueue__RenderMultipassLayerB`; `0x005545d0 CRenderQueue__BuildProjectedSprites`; `0x00554750 CRenderQueue__EmitBillboardStrip`; `0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle`; `0x009c7550`; `0x004773ab`; `0x004779b3`; `CVBufTexture__RenderDynamicUnitPass`; high-importance, low local-evidence-density renderer infrastructure, not low-importance filler; `0x00554f80 CAtmosphericsProfile__ctor`; `5862/6106 = 96.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-193607_post_wave873_render_multipass_verified`.

The dynamic unit pass no longer points at a CDXEngine-owned projected-sprite helper in the saved Ghidra database. Static callsite evidence at `0x004773ab` and `0x004779b3` loads `ECX=0x009c7550`, the global render queue, before dispatching `CRenderQueue__BuildProjectedSprites(unit)`, which then calls `CRenderQueue__EmitBillboardStrip`. Runtime projected-sprite visuals, exact queue item layout, exact projection math, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave867 CVBufTexture Cursor Read-Back

Wave867 CVBufTexture cursor static read-back (`cvbuftexture-cursor-wave867`, `wave867-readback-verified`) saved comments/tags/signatures for three adjacent vertex-buffer cursor helpers: `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne`, `0x005501e0 CVBufTexture__ReserveOneVertex`, and `0x00550200 CVBufTexture__GetVertexPtrAt`. Probe token anchor: `Wave867 CVBufTexture cursor`; `cvbuftexture-cursor-wave867`; `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne`; `int __thiscall CVBufTexture__GetVertexWriteCursorPlusOne(void * this)`; `0x005501e0 CVBufTexture__ReserveOneVertex`; `void __thiscall CVBufTexture__ReserveOneVertex(void * this, void * vertex_src)`; `0x00550200 CVBufTexture__GetVertexPtrAt`; `void __thiscall CVBufTexture__GetVertexPtrAt(void * this, int vertex_count, void * * out_vertex_ptr, int * out_start_index)`; `CPDSimpleSprite`; low local-evidence-density but important connective renderer infrastructure; `0x005508a0 CDXEngine__ClearMatrixBlock`; `5823/6105 = 95.38%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-165414_post_wave867_cvbuftexture_cursor_verified`.

Static evidence:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x005501d0` | `int __thiscall CVBufTexture__GetVertexWriteCursorPlusOne(void * this)` | Returns `this+0x19c` plus one; xrefs `0x004c970f` and `0x004ca24d` use the value as the next sprite vertex index. |
| `0x005501e0` | `void __thiscall CVBufTexture__ReserveOneVertex(void * this, void * vertex_src)` | `RET 0x4`; loads backing CVBufTexture from `this+0x198`, calls `CVBufTexture__AddVertices(vertex_src, 1)`, and stores the returned starting index at `this+0x19c`. |
| `0x00550200` | `void __thiscall CVBufTexture__GetVertexPtrAt(void * this, int vertex_count, void * * out_vertex_ptr, int * out_start_index)` | `RET 0xc` plus ECX use proves member-helper ABI; forwards to `CVBufTexture__GetVertexPtr(out_vertex_ptr, vertex_count)` and writes the returned starting index through `out_start_index`. |

Post-Wave867 queue telemetry is `6105` total, `5823` commented, `282` commentless, strict proxy `5823/6105 = 95.38%`; next raw commentless row is `0x005508a0 CDXEngine__ClearMatrixBlock`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260525-165414_post_wave867_cvbuftexture_cursor_verified`. Exact CVBufTexture field names/layouts, exact sprite-particle source-body identity, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave861 Render/HUD/Platform Tail Read-Back

Wave861 render/HUD/platform tail static read-back (`render-hud-platform-tail-wave861`, `wave861-readback-verified`) hardened `0x00523b30 CVBufTexture__DestroyGlobalHudHandle89BD98` as important connective infrastructure. Probe token anchor: `Wave861 render/HUD/platform tail`; `render-hud-platform-tail-wave861`; `0x00523a70 CDXEngine__RenderMouseCursorSprite`; `0x00523b30 CVBufTexture__DestroyGlobalHudHandle89BD98`; `0x00527990 CGame__DrawLocalCoopControllerPrompt`; `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag`; `0x00527f50 PCPlatform__AsyncMusicStreamWorkerMain`; `0x005282b0 PCPlatform__InitAsyncMusicStream`; `0x00528540 PCPlatform__KickAsyncMusicStreamRead`; `0x005285e0 PCPlatform__UpdateAsyncMusicStreamVolume`; important connective infrastructure; `0x0052a830 CD3DApplication__FindDepthStencilFormat`; `5802/6105 = 95.04%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-141443_post_wave861_render_hud_platform_tail_verified`.

Static evidence ties `CVBufTexture__DestroyGlobalHudHandle89BD98` to `CLTShell__ShutdownRuntimeAndReleaseResources`, global cursor/HUD texture handle `DAT_0089bd98`, `CTexture__DecrementRefCountFromNameField(texture+8)`, and final global clear. The same wave keeps the cursor renderer tied to `CVBufTexture__DrawSpriteEx` and the earlier sprite default-texture fallback path. Runtime render output, exact texture/global layouts, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave842 CVBufTexture Render Restore Read-Back

Wave842 CVBufTexture render restore (`cvbuftexture-render-restore-wave842`, `wave842-readback-verified`) hardened `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4` as `void __stdcall CVBufTexture__RenderAndRestoreStateFlag4(void * dynamic_context, int unused_zero_arg, int enable_dynamic_flag_source)`. Static instruction evidence shows `RET 0xc`; sole caller `0x0053e77d CDXEngine__Render` pushes dynamic context from `[EBP+0x470]`, zero, and zero-extended byte `DAT_009c7c56`; the body calls `CVBufTexture__SetStateCacheModeByFlag(1)`, checks `DAT_0089ce54 bit 4` before the `RenderState__Set0x89_Zero` branch, forwards the nonzero third-argument flag to `CVBufTexture__RenderDynamicUnitPass`, and calls `CVBufTexture__SetStateCacheModeByFlag(1)` again before returning.

Queue after Wave842 is `5666/6098 = 92.92%` strict clean-signature proxy; the next raw commentless row is `0x0050b030 OID__TraceLineAndSelectBestTargetHit`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260525-035851_post_wave842_cvbuftexture_render_restore_verified`. Exact source function identity, dynamic-pass parameter semantics, render-state table layout, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-25 Wave841 Shared Default/False VFunc09 Read-Back

Wave841 Shared Default/False VFunc09 (`cvertexshader-shared-vfunc09-wave841`, `wave841-readback-verified`) records that `0x005019c0 VFuncSlot_09_005019c0` is now saved as `int __cdecl VFuncSlot_09_005019c0(void)`. The body is `XOR EAX,EAX; RET`, and broader read-back evidence maps the stub through `26 DATA pointer slots` and `49 RTTI-backed owner/slot rows`, including `CControllerDefinition`, `CVertexShader`, `CDXTrees`, `CVBuffer`, `CVertexShaderMenu`, CDX frontend/media/render helpers, `CDXTexture`, and destroyable/motion-controller owners. Queue after Wave841 is `5665/6098 = 92.90%` strict clean-signature proxy; the next raw commentless row is `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260525-032940_post_wave841_cvertexshader_shared_vfunc09_verified`. Exact source virtual method names, caller-specific semantics, concrete class layouts, runtime behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-24 Wave829 Render-State World Reset Read-Back

Wave829 render-state world reset static read-back (`renderstate-world-reset-wave829`, `wave829-readback-verified`) added bounded render-state/cache evidence that touches the CVBufTexture render-mode setup row `0x00558fb0 CVBufTexture__SetupRenderStates`. Probe token anchor: `Wave829 render-state world reset`; `renderstate-world-reset-wave829`; `0x004eb1e0 D3DStateCache__UseDefaultRenderState`; `D3DStateCache__UseDefaultRenderState`; `STATE.UseDefault()`; `0x00513600 D3DStateCache__ResetSentinelTable`; `0x00513a50 CEngine__SetRenderStateCached`; `0x00513c20 RenderState_SetRaw`; `0x00550d50 CDXEngine__ApplyPendingRenderState`; `0x00558fb0 CVBufTexture__SetupRenderStates`; `5650/6098 = 92.65%`; `0x004ef100 CUnit__RunTransitionStepThreeTimes`; `[maintainer-local-ghidra-backup-root]\BEA_20260524-213733_post_wave829_renderstate_world_reset_verified`.

The CVBufTexture helper uses the texture mode at `this+0x88`, skips mode 5, pushes a texture transform when scale/offset fields differ from identity, and configures stage 0/1 texture-stage state plus render-state toggles for modes 0-4. The same Wave829 tranche corrected `0x004eb1e0` to `D3DStateCache__UseDefaultRenderState`, source-aligned it to `STATE.UseDefault()` callsites, and saved comments/tags for `0x00513600 D3DStateCache__ResetSentinelTable`, `0x00513a50 CEngine__SetRenderStateCached`, `0x00513c20 RenderState_SetRaw`, and `0x00550d50 CDXEngine__ApplyPendingRenderState`. Queue after Wave829: `6098` total, `5650` commented, `448` commentless, strict clean-signature proxy `5650/6098 = 92.65%`; next raw commentless row `0x004ef100 CUnit__RunTransitionStepThreeTimes`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260524-213733_post_wave829_renderstate_world_reset_verified`. Exact state-table/device/engine/texture layouts, exact Direct3D enum names for every numeric state, runtime render behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-24 Wave804 CVBufTexture Render Helpers Read-Back

Wave804 CVBufTexture render helpers static read-back (`cvbuftexture-render-helpers-wave804`, `wave804-readback-verified`) saved comments/tags for `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback` and `0x00476fe0 CVBufTexture__RenderDynamicUnitPass`. It hardened the sprite-wrapper signature to `int __thiscall CVBufTexture__DrawSpriteWithDefaultTextureFallback(void * this, float screen_x, float screen_y, float draw_width, float draw_height, float argb_tint_bits)`, retained the dynamic-unit-pass signature, made no renames, made no function-boundary changes, and made no executable-byte change.

`0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback` is called by `0x00527ba7 CGame__DrawLocalCoopControllerPrompt`. The body reads texture wrapper field `this+0x08`; if that texture is null, it lazily resolves fallback texture `s_meshtex_default_tga_00625498` through `CTexture__FindTexture` into `DAT_0089ce84` and returns 0 if the lookup fails. The success path forwards screen coordinates, fixed depth `0.001`, the texture, blend/anchor constants `4/0`, `argb_tint_bits` or fallback tint `0xff000000`, and width/height-derived UV scale/bounds to `CVBufTexture__DrawSpriteEx`; `RET 0x14` proves five stack arguments after `ECX=this`.

`0x00476fe0 CVBufTexture__RenderDynamicUnitPass` is called by `0x0050ab91 CVBufTexture__RenderAndRestoreStateFlag4`. Wave804 ties the older read-only dynamic-unit-render guard to saved Ghidra comments/tags: the body walks the active unit list through `DAT_00855170`/`DAT_00855178`, dispatches `CDXEngine__BuildProjectedSprites(&DAT_009c7550, unit)`, traverses collision-map owners through `CMapWhoEntry__GetOwner`, and gates `CRenderQueue__InsertSortedByDepth(&DAT_009c7550, unit, depth)` using `DAT_0089d680`, `g_MeshQualityDistance`, and `g_MeshQualityLodTable`.

Queue after Wave804: `6098` total, `5576` commented, `522` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy and strict clean-signature proxy `5576/6098 = 91.44%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-091718_post_wave804_cvbuftexture_render_helpers_verified`. Next raw commentless row: `0x00488f60 CInfantryUnit__VFunc_02_00488f60`.

This remains static retail Ghidra evidence only. Exact source identity, texture wrapper/unit/collision/render-queue/material/shader/skeleton/animation layout parity, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-24 Wave801 Frontend/Render Helper Read-Back

Wave801 static read-back (`frontend-render-helpers-wave801`, `wave801-readback-verified`) saved a current comment/tag on `0x00465f00 CVBufTexture__GetGlobalEnableByte`. Static evidence shows the body returns the low byte from `DAT_00679b40` in `AL`; upper `EAX` preservation remains treated as a decompiler artifact rather than proven semantic state. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-073450_post_wave801_frontend_render_helpers_verified`.

This remains static retail Ghidra evidence only. Exact source-body identity, runtime texture/render behavior, BEA patching, and rebuild parity remain deferred.

## 2026-05-19 Wave594 State-Cache Helper Read-Back

Wave594 saved `CVBufTexture__SetStateCacheModeByFlag` at `0x0053f040` with signature `void __stdcall CVBufTexture__SetStateCacheModeByFlag(int state_cache_mode_flag)`. Two xrefs from `CVBufTexture__RenderAndRestoreStateFlag4` call it around render-state setup/restore. Body read-back shows the nonzero path dispatches `D3DStateCache__ForceSlotMode4or5(0)`, while the zero path dispatches `D3DStateCache__SetStateCached(0,1,4)`, and the helper returns with `RET 0x4`.

The same Wave594 tranche also hardened adjacent FMV rows in `DXFMV.CPP`; queue after Wave594 is `6093` total, `3039` commented, `3054` commentless, `1347` exact-undefined signatures, `1095` `param_N`, with next head `0x0053f730 CDXBitmapFont__ctor_like_0053f730`. This is static retail evidence only; runtime render-state behavior, exact `CVBufTexture`/`D3DStateCache` layouts, BEA patching, and rebuild parity remain unproven.

## 2026-05-23 Wave770 Unwind Continuation Read-Back

Wave770 saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for vbuftexture.cpp allocation-cleanup callbacks `0x005d5670 Unwind@005d5670` and `0x005d56a0 Unwind@005d56a0`. DATA scope-table xrefs `0x0061dee4` and `0x0061df0c` point at the bodies; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with vbuftexture.cpp debug path `0x00633d5c`, line tokens `0xb6` and `0xfb`, and allocation/type values `0x2c` and `0x2f`.

The same Wave770 tranche also recorded adjacent bounded `DeviceObject__ctor_like_00512d50` jumps at `0x005d56d0 Unwind@005d56d0` and `0x005d56f0 Unwind@005d56f0`, where exact helper semantics remain unproven. Tags include `unwind-continuation-wave770` and `wave770-readback-verified`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260523-180835_post_wave770_unwind_continuation_verified`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

## 2026-05-18 Wave566 Stale Owner Correction

Wave566 superseded the stale CVBufTexture owner label `CVBufTexture__FindListEntryByGlobalId89D94C` at `0x005230e0`. The saved Ghidra row is now `CFEPWingmen__FindCurrentLevelRecord(void * this)` because all current xrefs are deferred FEPWingmen callsites that pass `ECX=&DAT_0089da44`, the body walks `this+0x28` / cursor `this+0x30`, and the returned record fields match the `0x24`-byte records appended by `CFEPWingmen__Load`. Do not count `0x005230e0` as CVBufTexture coverage unless future evidence contradicts the Wave566 owner correction.

## 2026-05-18 Wave567 Source-Ambiguous Reset Correction

Wave567 corrected the misleading `CProfiler__ResetAll` saved label at `0x00523db0` to `Input__ResetMouseTransientState(void)`. Source callsite hints include `CVBufTexture::ResetAll`, but the retail body clears mouse button transient fields, click-ready and cursor-ready flags, wheel accumulator, and `DAT_00640054`, and its xrefs include platform input init/shutdown, frontend process, game main loop, and render-tail no-function callsites that immediately test those mouse transient globals. Do not count `0x00523db0` as CVBufTexture coverage unless a future focused pass proves exact source identity beyond the Wave567 input-state evidence.

## 2026-05-19 Wave570 Render Validation Tail Read-Back

Wave570 saved static signatures/comments/tags for five adjacent render validation record helpers at `0x00527cc0`, `0x00527d20`, `0x00527da0`, `0x00527dd0`, and `0x00527e00`. The current owner prefixes were retained as saved entry names only because xrefs span battle-line, landscape, mesh, surf, water, render-queue, and engine render paths.

The CVBufTexture-named row in this tranche is `CVBufTexture__MarkAccepted(void * this)` at `0x00527da0`. It is an ECX-only render validation record accept helper: if `this+0x10` is clear, it logs `RM: Accepting %s %d` from `this+0x08/this+0x0c`, then sets `this+0x10` to `1`. This is static retail evidence only; exact render-record class/layout, exact CVBufTexture source identity, runtime D3D validation behavior, BEA patching, and rebuild parity remain unproven.

## 2026-05-18 Wave530 Buffer-Management Read-Back

Wave530 saved static Ghidra signatures/comments/tags for the fifteen CVBufTexture buffer-management targets from `0x005003f0` through `0x00500cb0`. The pass covers constructor/destructor, vertex/index format setup, persist flag, vertex/index resize, lock release, append helpers, direct reserve helpers, and primitive-count helpers.

Key saved signatures:

- `CVBufTexture__CVBufTexture(void * this, void * texture)` and `CVBufTexture__dtor(void * this)` cover global-list membership and texture/buffer lifetime cleanup.
- `CVBufTexture__SetVBFormat(..., int fvf_format, int usage_flags, int vertex_stride, int primitive_type, int pool_mode)` and `CVBufTexture__SetIBFormat(..., int index_format, int usage_flags, int reserved, int pool_mode)` are stack-arity verified by `RET 0x14` and `RET 0x10`.
- `CVBufTexture__ResizeVertexBuffer` and `CVBufTexture__ResizeIndexBuffer` round nonzero requests up from `0x400`, recreate backing CVBuffer/CIBuffer objects, and copy existing data when present.
- `CVBufTexture__AddVertices`, `CVBufTexture__AddIndices`, `CVBufTexture__GetIndexPtr`, and `CVBufTexture__GetVertexPtr` are the write/reserve surface. `CVBufTexture__GetVertexPtr` takes `out_vertex_ptr` and returns the starting vertex index.
- `CVBufTexture__GetIndexPrimitiveCount` and `CVBufTexture__GetVertexPrimitiveCount` remain static primitive-count helpers only.

Read-back evidence verified 15 metadata rows, 15 tag rows, 109 xref rows, 1815 instruction rows, 15 target decompile exports, 22 context decompile exports, and 481 representative callsite instruction rows. Runtime rendering behavior, runtime device-loss behavior, exact concrete layouts, local-variable recovery, and rebuild parity remain unproven.

## 2026-05-18 Wave531 Render-Tail Read-Back

Wave531 saved static Ghidra signatures/comments/tags for the eight CVBufTexture render-tail targets from `0x00500d10` through `0x00501280`. The pass covers render batch traversal, global release of unlocked transient buffers, main indexed render, reset, validated/non-validated indexed draw helpers, non-indexed draw, and get-or-create caching.

Key saved signatures:

- `CVBufTexture__RenderBatchList(void * batch_list)` is a caller-cleaned cdecl helper that walks 0x24-byte batch records by priority and calls `CVBufTexture__Render(reset_after_render=1)`.
- `CVBufTexture__ReleaseAllUnlocked(void)` is a no-argument global-list helper reached from `CDXEngine__PostRender`.
- `CVBufTexture__Render(void * this, int reset_after_render)` is the main thiscall indexed path over texture hooks, FVF globals, stream/index binding, and optional reset.
- `CVBufTexture__Reset(void * this)` clears byte cursors and toggles double-buffer slot state.
- `CVBufTexture__RenderIndexed` and `CVBufTexture__RenderIndexedNoValidate` both take `reset_after_render`, `vertex_count_override`, and `primitive_count_override`; the former includes the ValidateDevice branch and failure logging, while the latter skips that validation branch.
- `CVBufTexture__RenderNonIndexed(void * this, int reset_after_render, int primitive_count_override)` binds the stream source and calls Direct3D `DrawPrimitive`.
- `CVBufTexture__GetOrCreate(void * texture, int force_new)` reuses texture field `+0x140` or a matching global-list entry when possible, otherwise allocates a new CVBufTexture.

Read-back evidence verified 8 metadata rows, 8 tag rows, 39 xref rows, 3528 instruction rows, 8 target decompile exports, 8 context decompile exports, and 230 representative callsite instruction rows. This is render-tail static metadata only: runtime rendering behavior, runtime device-loss behavior, exact concrete layouts, Direct3D state semantics, local-variable recovery, and rebuild parity remain unproven.

## 2026-05-18 Wave532 Resource-Tail Read-Back

Wave532 saved static Ghidra signatures/comments/tags for the six VBufTexture resource-tail targets from `0x00501310` through `0x005015c0`. The pass covers resource refcount decrement, `CScreenFx` texture lookup/wrapper creation, end-level and shutdown cleanup of zero-refcount CVBufTexture entries, and post-render/restart/shutdown buffer-pool trimming.

Key saved signatures:

- `CDXEngine__DecrementResourceRefCount(void * resource)` is an ECX-only helper that decrements the resource/CVBufTexture field at `+0x60`.
- `CScreenFx__FindTexture(char * texture_name, int texture_find_arg)` is a caller-cleaned cdecl helper that forwards to `CTexture__FindTexture`, adjusts a texture-side counter through `CTexture__DecrementRefCountFromNameField`, and ensures `CVBufTexture__GetOrCreate(texture,0)`.
- `CWaypoint__CleanupEndLevelVBufTextures(void)` and `CVBufTexture__ClearOut(void)` walk the global list head `0x00854e00`, free zero-refcount entries, and emit leak/no-leak `DebugTrace` text for end-level or shutdown contexts.
- `CDXEngine__ResizeLargestIdleVertexBuffer(void)` scans non-persistent entries under guard byte `0x00633d2c`, selects one largest vertex-buffer shrink opportunity, and calls `CVBufTexture__ResizeVertexBuffer`.
- `CEngine__TrimVbIbPoolCapacitiesPow2(void)` rounds current vertex and index byte cursors to `0x400`-based powers of two and shrinks oversized VB/IB buffers through `CVBufTexture__ResizeVertexBuffer` and `CVBufTexture__ResizeIndexBuffer`.

Read-back evidence verified 6 metadata rows, 6 tag rows, 25 xref rows, 2646 instruction rows, 6 target decompile exports, and 525 representative callsite instruction rows. This is resource-tail static metadata only: runtime cleanup behavior, runtime screen-effect behavior, runtime pool trimming cadence, exact concrete layouts, local-variable recovery, and rebuild parity remain unproven.

## Class Architecture

CVBufTexture maintains:
- **Dual vertex buffers** - For double-buffering (mSlots[0x48] toggles between them)
- **Index buffer** - For indexed primitive rendering
- **Texture association** - Links vertex data to textures
- **Global linked list** - All instances tracked via `DAT_00854e00` for bulk operations

### Key Member Offsets

| Offset | Type | Purpose |
|--------|------|---------|
| 0x00 | int* | Texture pointer |
| 0x04 | int | FVF format / shader |
| 0x08 | uint | VB usage flags |
| 0x0C | int | VB pool type |
| 0x10 | bool | VB locked flag |
| 0x14 | int[2] | VB sizes (double-buffered) |
| 0x1C | int | Current VB data size |
| 0x20 | int | IB format |
| 0x24 | uint | IB usage flags |
| 0x28 | int | IB pool type |
| 0x2C | bool | IB locked flag |
| 0x30 | int | IB size |
| 0x34 | int | Current IB data size |
| 0x38 | void* | VB lock pointer |
| 0x3C | void* | IB lock pointer |
| 0x40 | int[2] | VB D3D objects (double-buffered) |
| 0x48 | int | Current buffer index (0 or 1) |
| 0x4C | int | IB D3D object |
| 0x50 | int | Primitive type (D3DPRIMITIVETYPE) |
| 0x54 | int | Vertex stride |
| 0x58 | int* | Next in linked list |
| 0x5C | bool | Persist flag |
| 0x60 | int | Reference count |
| 0x64 | int | Last vertex count |

### Primitive Type Values (D3DPRIMITIVETYPE)

Used in GetIndexPrimitiveCount/GetVertexPrimitiveCount:
- 1 = D3DPT_POINTLIST
- 2 = D3DPT_LINELIST
- 3 = D3DPT_LINESTRIP
- 4 = D3DPT_TRIANGLELIST
- 5 = D3DPT_TRIANGLESTRIP
- 6 = D3DPT_TRIANGLEFAN

## Functions (29 total)

### Construction / Destruction

| Address | Name | Purpose |
|---------|------|---------|
| `0x005003f0` | `CVBufTexture__CVBufTexture` | Constructor - initializes members, adds to global list |
| `0x00500460` | `CVBufTexture__dtor` | Destructor - releases buffers, removes from global list |

### Configuration

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500540` | `CVBufTexture__SetVBFormat` | Set vertex buffer format (FVF, usage, pool, stride) |
| `0x00500590` | `CVBufTexture__SetIBFormat` | Set index buffer format (format, usage, pool) |
| `0x005005d0` | `CVBufTexture__SetPersist` | Mark buffer as persistent (won't be released) |

### Buffer Management

| Address | Name | Purpose |
|---------|------|---------|
| `0x005005e0` | `CVBufTexture__ResizeVertexBuffer` | Resize/recreate vertex buffer, preserves existing data |
| `0x005007f0` | `CVBufTexture__ResizeIndexBuffer` | Resize/recreate index buffer, preserves existing data |
| `0x005009c0` | `CVBufTexture__UnlockVB` | Unlock vertex buffer after writing |
| `0x005009f0` | `CVBufTexture__UnlockIB` | Unlock index buffer after writing |

### Data Writing

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500a10` | `CVBufTexture__AddVertices` | Copy vertex data to buffer, auto-resize if needed |
| `0x00500ac0` | `CVBufTexture__AddIndices` | Copy index data to buffer, auto-resize if needed |
| `0x00500b40` | `CVBufTexture__GetIndexPtr` | Get raw pointer to index buffer for direct writes |
| `0x00500bb0` | `CVBufTexture__GetVertexPtr` | Get raw pointer to vertex buffer for direct writes |

### Primitive Counting

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500c50` | `CVBufTexture__GetIndexPrimitiveCount` | Calculate primitive count from index data |
| `0x00500cb0` | `CVBufTexture__GetVertexPrimitiveCount` | Calculate primitive count from vertex data |

### Rendering

| Address | Name | Purpose |
|---------|------|---------|
| `0x00500d10` | `CVBufTexture__RenderBatchList` | Render a batch list sorted by texture priority |
| `0x00500d60` | `CVBufTexture__ReleaseAllUnlocked` | Release/unlock non-persistent buffers and warn on leftover cursors |
| `0x00500e70` | `CVBufTexture__Render` | Main render - sets texture, calls DrawIndexedPrimitive |
| `0x00500f80` | `CVBufTexture__Reset` | Reset buffer cursors, toggle double-buffer |
| `0x00500fa0` | `CVBufTexture__RenderIndexed` | Render with indexed primitives (with validation) |
| `0x005010e0` | `CVBufTexture__RenderIndexedNoValidate` | Render indexed without ValidateDevice check |
| `0x005011c0` | `CVBufTexture__RenderNonIndexed` | Render without index buffer (DrawPrimitive) |

### Factory

| Address | Name | Purpose |
|---------|------|---------|
| `0x00501280` | `CVBufTexture__GetOrCreate` | Get existing or create new CVBufTexture for a texture |

### Resource Lifetime / Pool Trimming

| Address | Name | Purpose |
|---------|------|---------|
| `0x00501310` | `CDXEngine__DecrementResourceRefCount` | Decrement resource/CVBufTexture refcount field `+0x60` |
| `0x00501320` | `CScreenFx__FindTexture` | Resolve screen-effect texture and ensure a CVBufTexture wrapper |
| `0x00501360` | `CWaypoint__CleanupEndLevelVBufTextures` | Free zero-refcount CVBufTexture entries at end-level cleanup and report leaks |
| `0x00501450` | `CVBufTexture__ClearOut` | Free zero-refcount CVBufTexture entries during shutdown and report leaks |
| `0x00501540` | `CDXEngine__ResizeLargestIdleVertexBuffer` | Shrink one largest idle non-persistent vertex buffer after render |
| `0x005015c0` | `CEngine__TrimVbIbPoolCapacitiesPow2` | Trim oversized vertex/index buffers to `0x400`-based powers of two |

### Unit Transform Cache Lookup

| Address | Name | Purpose |
|---------|------|---------|
| `0x00511bc0` | `CVBufTexture__FindListEntryByPair` | Wave560 saved signature/comment correction for a two-key cache lookup called by `CUnit__UpdateTransform`; current name is retained, but the comment bounds the evidence to the profile/cache object at `unit+0x164`, list root `this+0x6c`, and iterator `this+0x74`. |

The same queue-tail reference resolver tranche also saved `CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs`; exact cache ownership and runtime transform behavior remain unproven.

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x00854e00` | `g_CVBufTextureList` | Head of linked list of all CVBufTexture instances |
| `0x00854e04` | `g_bDoubleBuffering` | Enable double-buffering (toggle buffer index each frame) |
| `0x00854dec` | `g_bHardwareVP` | Hardware vertex processing enabled flag |
| `0x00854dd8` | `g_bValidateFailed` | ValidateDevice failure flag |
| `0x00854dd9` | `g_bValidateEnabled` | Enable ValidateDevice checks |

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| `0x00633d40` | `"EnsureLockV failed for %s"` | VB lock failure error |
| `0x00633d80` | `"WARNING: CVBufTexture: no texture, has %d verts left over"` | Orphaned vertices warning |
| `0x00633dbc` | `"WARNING: CVBufTexture %s has %d verts left over"` | Vertices not rendered warning |
| `0x00633df0` | `"WARNING: CVBufTexture: no texture, has %d indices left over"` | Orphaned indices warning |
| `0x00633e2c` | `"WARNING: CVBufTexture %s has %d indices left over"` | Indices not rendered warning |
| `0x00633e60` | `"CVBT: DWATS ValidateDevice failed %s"` | D3D validation error |

## Double-Buffering System

The class supports double-buffering of vertex buffers to allow CPU writes while GPU reads:

1. `mSlots[0x48]` tracks current buffer (0 or 1)
2. `mSlots[0x14]` and `mSlots[0x40]` are arrays of size 2
3. After rendering, `Reset()` toggles the buffer index via XOR: `index ^= 1`
4. Controlled by global `g_bDoubleBuffering` at `0x00854e04`

## Rendering Pipeline

1. **Setup:** `SetVBFormat()` / `SetIBFormat()` configure buffer parameters
2. **Fill:** `AddVertices()` / `AddIndices()` copy geometry data
3. **Render:** `RenderIndexed()` or `RenderNonIndexed()` draw primitives
4. **Reset:** `Reset()` clears cursors and toggles double-buffer

## 2026-05-08 Dynamic Unit Render Read-Back Guard

`tools/dynamic_unit_render_readback_probe.py --check` consumes the existing ignored `CVBufTexture__RenderDynamicUnitPass` decompile export at `0x00476fe0`. The guard checks unit-list traversal, collision-map owner traversal, the projected-sprite path through `CDXEngine__BuildProjectedSprites`, sorted render insertion through `CRenderQueue__InsertSortedByDepth`, and distance/LOD gates including `g_MeshQualityDistance` and `g_MeshQualityLodTable`. This is renderer-path evidence only: exact source identity, material/shader/skeleton parity, runtime Goodies model-viewer playback, and native WinUI textured rendering remain separate proof questions.

## 2026-05-14 RenderQueue Depth-Gate Helper Correction

Wave407 corrected the saved Ghidra metadata for `0x00477b70` from the caller-owned `CVBufTexture__QueueRenderIfDepthInRange` label to `CRenderQueue__InsertIfDepthBelowIndexedLimit` with signature `void __thiscall CRenderQueue__InsertIfDepthBelowIndexedLimit(void * this, void * item, float depth)`. The immediate caller remains `CVBufTexture__RenderDynamicUnitPass` at `0x00477250`, but instruction read-back shows that caller sets `ECX` to global render queue `&DAT_009c7550`, pushes the item and computed depth, and reaches a helper that returns with `RET 0x8`. Target read-back gates on `DAT_0089d680`, compares the input depth against an indexed queue limit, and calls `CRenderQueue__InsertSortedByDepth(this,item,depth)`. This is static render-queue metadata correction only; exact `CRenderQueue` layout, `DAT_0089d680` semantics, runtime LOD/render behavior, and rebuild parity remain unproven.

## 2026-05-14 CIBuffer Direct-Lock Correction

Wave414 corrected the saved Ghidra metadata for `0x004885e0` from the stale caller-owned `CVBufTexture__SetTextureStageFilterByFlag200` label to `CIBuffer__LockDirect` with signature `int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)`. CVBufTexture index-buffer callers still reach this helper, but the current callsite/body evidence shows the receiver is the CIBuffer index-buffer object and the helper returns a D3D lock HRESULT. This is a static owner/signature correction only; it does not change the documented CVBufTexture buffer-management model or prove runtime rendering behavior.

## Dependencies

- **CVBuffer** (vbuffer.cpp) - Low-level D3D vertex buffer wrapper
- **CIBuffer** (likely ibuffer.cpp) - Low-level D3D index buffer wrapper
- **IDirect3DDevice8** - D3D device at `DAT_00888a50`

## Notes

- Buffer sizes grow in powers of 2, starting at 0x400 (1024)
- Hardware VP mode affects buffer creation flags (strips certain usage flags)
- ReleaseAllUnlocked() iterates global list to free unused buffers (for device lost recovery)
- Reference counting prevents premature destruction when texture is reused
