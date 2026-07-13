# VertexShader.cpp Function Analysis

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x005be628` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1207 measured anchor: unique-address accounting governs active current-risk progress. Wave1207 (`wave1207-d3d-render-resource-lifecycle-current-risk-review`) accounts for `6 D3D/render-resource lifecycle current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review made no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1089/1179 = 92.37%`; remaining active focused work: 90; legacy additive counter is deprecated (`1120/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `36 xref rows`, `260 instruction rows`, and `6 decompile rows`. Anchors: `CVertexShader__scalar_deleting_dtor`, `CVertexShader__VFunc_02_00501a10`, `DeviceObject__dtor_body`, `DeviceObject__scalar_deleting_dtor`, `CDXMeshVB__scalar_deleting_dtor`, and `CDXMeshVB__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime shader behavior, runtime render-resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

**Source File:** `[maintainer-local-source-export-root]\VertexShader.cpp`
**Debug String Address:** `0x0063cf78`
**Analysis Date:** December 2025

## Overview
> **Queue status (2026-05-28):** Ghidra export-contract closure **6152/6152** after Wave961 CVertexShader slot-2 boundary recovery (every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

VertexShader.cpp implements the `CVertexShader` class, which manages GPU vertex shader programs for hardware-accelerated 3D rendering in Battle Engine Aquila. The class handles shader creation, compilation, caching, and cloning operations using DirectX 8 shader assembly.

Wave888 texture transform dispatch tail (`texture-transform-dispatch-tail-wave888`, `wave888-readback-verified`) saved comments/tags for CVertexShader dispatch-table thunks used by the texture transform island. Exact anchors include `0x005766a5 CVertexShader__DispatchTableCall_656f38`, `0x00576b47 CVertexShader__DispatchTableCall_656fc4`, and `0x00576e0a CVertexShader__DispatchTableCall_656f78`; companion CFastVB initializer thunks target slots `0x00656f38`, `0x00656fc4`, and `0x00656f78`. Probe token anchor: `Wave888 texture transform dispatch tail`; `texture-transform-dispatch-tail-wave888`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `0x00576286 CDXTexture__DispatchPtr00656f68_WithInit`; `0x00576404 Math__InterpolateVec4Cubic`; `0x00576621 Math__InterpolateVec4ByUV`; `0x005768fe CFastVB__DispatchIndirect_00656f3c`; `0x0057770b CFastVB__BuildTransformMatrixWithOffsets`; `0x00578a20 CTexture__MapNormalizedUvToVolumeCoords`; `0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv`; `0x00578f53 CFastVB__ApplyOptionalTransformPasses`; `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets`; `0x00656f48`; `0x0065715c`; `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser`; `6052/6113 = 99.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-033426_post_wave888_texture_transform_dispatch_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, exact descriptor/matrix/vertex-shader/texture-transform layouts, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Wave889 texture codec surface prelude (`texture-codec-surface-prelude-wave889`, `wave889-readback-verified`) saved comments/tags for the texture codec, surface-node, mapped-resource, vertex-shader parser, and resample prelude tranche. Probe token anchor: Wave889 texture codec surface prelude; texture-codec-surface-prelude-wave889; 0x00579a9a CVertexShader__CompileScriptWithDirectiveParser; 0x00579b39 CDXTexture__LookupNamedFormatDescriptor; 0x00579e08 CDXTexture__DecodeBmpDibFromMemory; 0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs; 0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode; 0x0057cca4 CFastVB__BuildResampleKernelBuckets; 0x0057cf60 CDXTexture__CopyDxtBlockRegion; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 6054/6113 = 99.03%; [maintainer-local-ghidra-backup-root]\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified. Static evidence ties the tranche to directive parsing, descriptor lookup, codec dispatch, surface-node cleanup, mapped texture export, resample bucket setup, and DXT block copying. Exact texture/codec/surface-node/mapped-file/descriptor/parser/resample table layouts, exact source-body identity, runtime texture decode/encode/export/resample/render behavior, BEA patching, and rebuild parity remain deferred.

Wave850 D3D shader/input tail (`d3d-shader-input-tail-wave850`, `wave850-readback-verified`) added saved static evidence for the engine-side shader connector rows adjacent to the CVertexShader runtime. `0x00513e20 CEngine__SetShaderObject` binds a shader object by sending `CVertexShader__GetVertexDeclarationToken(shader_obj)` to device slot `0x164` and `shader_obj+0x28` to slot `0x170`; `0x00513e90 CEngine__SetVertexShaderHandleCached` and `0x00513ec0 CEngine__SetVertexShaderHandleRaw` manage cached/raw vertex-shader handles; `0x00513f20 CEngine__CreatePixelShaderFromText` compiles text through `CVertexShader__CompileScriptWithDirectiveParser` and calls device slot `0x1a8`; and `0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike` is a bounded shader-create-like wrapper over device slot `0x16c` whose result is tested by shader loader callsites. Probe token anchor: `Wave850 D3D shader/input tail`; `0x00513e20 CEngine__SetShaderObject`; `0x00513f20 CEngine__CreatePixelShaderFromText`; `0x00513ff0 CEngine__DeviceCall16C_CreateVertexShaderLike`; `5704/6098 = 93.54%`; `0x005140e0 CDXEngine__CaptureAviFrame`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-081702_post_wave850_d3d_shader_input_tail_verified`.

This is saved static retail/source-reference evidence only; exact Direct3D interface version, exact COM method names, concrete shader-object/device layouts, runtime shader compilation/creation/binding behavior, BEA patching, and rebuild parity remain deferred.

Current correction note: Wave739 saved `0x005be622 Direct3DCreate9` and `0x005be628 HResultToString`, but its 22-xref aggregate combined one `Direct3DCreate9` reference with 21 direct `HResultToString` calls. Fresh final evidence keeps the mapper name/signature, single `RET 0x4`, and `E_ABORT` evidence; a later read-only 300-second decompile succeeded and confirmed 3,497 unique literal-string returns plus `Unknown`. Runtime graphics/error behavior and table completeness remain unproven.

Wave1121 (`wave1121-mixed-score24-current-risk-review`) refreshed the saved Ghidra comment for `0x005019c0 VFuncSlot_09_005019c0` after fresh pre/post exports showed the old comment still treated `0x00501a10` as unresolved. The new saved comment keeps the Wave841 shared default/false stub evidence and records the Wave961 recovery `0x00501a10 CVertexShader__VFunc_02_00501a10`. No rename, signature change, function-boundary change, or executable-byte change was made. Current focused accounting moves to `122/1179 = 10.35%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`. Runtime shader/frontend behavior, exact source virtual names, concrete layouts, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave840 Shader Capability Init (`shader-capability-init-wave840`, `wave840-readback-verified`) hardened the startup helper `0x005016b0 InitShaderCapabilityFlagsAndCVar` as `void __cdecl InitShaderCapabilityFlagsAndCVar(void)`. It is called from `0x005155b1 PCPlatform__Init` after `"Initting shaders"`, probes Direct3D device caps, writes shader capability global `DAT_00854e6c` from the `0xfffe0101` comparison, and registers `cg_forcevertexshaders` with backing byte `DAT_00854e6d` when `DAT_0063c108` enables vertex shaders. This complements the existing `0x005019d0 CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag` row, which performs the same support-flag comparison from the CVertexShader neighborhood. Queue after Wave840: `5664/6098 = 92.89%` strict clean-signature proxy; next raw commentless row `0x005019c0 VFuncSlot_09_005019c0`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-030308_post_wave840_shader_capability_init_verified`. Exact Direct3D caps field identity, exact console/CVar schema, runtime hardware/driver behavior, runtime shader enablement, BEA patching, and rebuild parity remain deferred.

Wave841 Shared Default/False VFunc09 (`cvertexshader-shared-vfunc09-wave841`, `wave841-readback-verified`) hardened `0x005019c0 VFuncSlot_09_005019c0` as `int __cdecl VFuncSlot_09_005019c0(void)`. The body is `XOR EAX,EAX; RET`, so this is a shared default/false virtual stub rather than a CVertexShader-only method. CVertexShader vtable `0x005dfbc4` uses it at slots 1 and 4; the former vtable slot-2 no-function-at-pointer boundary at `0x00501a10` was later recovered by Wave961 as a conservative vtable-slot label. The same post-readback evidence found `26 DATA pointer slots` and `49 RTTI-backed owner/slot rows`, including `CControllerDefinition`, destroyable segment/component and motion-controller families, `CVBuffer`, `CVertexShaderMenu`, `CVertexShader`, CDX frontend/media/render helpers, `CDXTexture`, and `CDXTrees`. Queue after Wave841: `5665/6098 = 92.90%` strict clean-signature proxy; next raw commentless row `0x0050ab60 CVBufTexture__RenderAndRestoreStateFlag4`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-032940_post_wave841_cvertexshader_shared_vfunc09_verified`. Exact source virtual method names, caller-specific semantics, concrete class layouts, runtime behavior, BEA patching, and rebuild parity remain deferred.

Wave961 CVertexShader lifecycle review (`cvertexshader-lifecycle-review-wave961`, `wave961-readback-verified`) recovered `0x00501a10 CVertexShader__VFunc_02_00501a10` as CVertexShader vtable `0x005dfbc4 slot 2`. Pre-vtable export reported `NO_FUNCTION_AT_POINTER`; post-readback metadata saved `int __thiscall CVertexShader__VFunc_02_00501a10(void * this)`, and post-vtable export reports the slot as `OK`. Static evidence ties the body to `0x00501890 CVertexShader__scalar_deleting_dtor` continuity, Direct3D globals `DAT_00888c8c` / `DAT_00888a50`, the `0xfffe0101` caps comparison, shader capability global `DAT_00854e6c`, compiled-blob creation through `CEngine__DeviceCall16C_CreateVertexShaderLike`, named-file fallback through `CVertexShader__LoadCompiledShaderBlobFromVSOFile`, and `0x80004005` failure returns. Wave911 focused re-audit progress after Wave961 is `306/1408 = 21.73%`; static export-contract closure is `6152/6152 = 100.00%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260528-125650_post_wave961_cvertexshader_lifecycle_review_verified`. Probe token anchor: Wave961; cvertexshader-lifecycle-review-wave961; 0x00501890 CVertexShader__scalar_deleting_dtor; 0x00501a10 CVertexShader__VFunc_02_00501a10; 0x005dfbc4 slot 2; NO_FUNCTION_AT_POINTER; CEngine__DeviceCall16C_CreateVertexShaderLike; CVertexShader__LoadCompiledShaderBlobFromVSOFile; 0x80004005; 0xfffe0101; DAT_00854e6c; DAT_00888c8c; 306/1408 = 21.73%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-125650_post_wave961_cvertexshader_lifecycle_review_verified; function-boundary recovery. Exact source virtual name, exact `CVertexShader` / `CShaderBase` layout, runtime shader compile/load/bind behavior, graphics-driver behavior, BEA patching, and rebuild parity remain separate proof.

Wave770 unwind continuation saved `void __cdecl Unwind@...(void)` signatures, comments, and tags for VertexShader.cpp allocation-cleanup callbacks `0x005d5710 Unwind@005d5710` and `0x005d5740 Unwind@005d5740`. DATA scope-table xrefs `0x0061df84` and `0x0061dfac` point at the bodies; instruction/decompile evidence calls `OID__FreeObject_Callback` with VertexShader.cpp debug path `0x0063cf78`, line tokens `0x2bd` and `0x99a`, allocation/type value `0x50`, and pointers `*(EBP+0x14)` / `*(EBP-0xd8)`. Tags include `unwind-continuation-wave770` and `wave770-readback-verified`; verified backup is `[maintainer-local-ghidra-backup-root]\BEA_20260523-180835_post_wave770_unwind_continuation_verified`. This is saved static retail Ghidra evidence only. Exact parent source body, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.

Prior saved-correction note: Wave551 corrected the `VSDS` resource handler at `0x005042f0` to `CVertexShader__DeserializeAll`, Wave533 hardened the CVertexShader core lifecycle/factory tranche, Wave534 hardened the adjacent load/compile/render-info/clone tranche, and Wave561 hardened the shared `CShaderBase__Init` / `CShaderBase__UnlinkFromRenderObjectLists` / `DeviceObject__scalar_deleting_dtor` base-list evidence used by CVertexShader and neighboring Direct3D objects. Wave961 recovered vtable slot 2 at `0x00501a10` as a conservative slot label after live `NO_FUNCTION_AT_POINTER` evidence; the downstream stack-cleaning compiled-blob helper at `0x005027f0` still has its saved Wave534 signature/comment.

## Functions Found (18 mapped; vtable slot 2 recovered by Wave961; no weak helpers remain)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00501800` | `CVertexShader__CVertexShader` | Constructor - initializes shader object |
| `0x00501890` | `CVertexShader__scalar_deleting_dtor` | Wave533 corrected scalar-deleting destructor wrapper at vtable slot 0 |
| `0x005018b0` | `CVertexShader__dtor` | Wave533 corrected destructor body for shader/device resource release |
| `0x005019c0` | `VFuncSlot_09_005019c0` | Wave841 shared default/false virtual stub (`XOR EAX,EAX; RET`); used by CVertexShader slots 1 and 4 and other RTTI-backed owner rows |
| `0x00501a10` | `CVertexShader__VFunc_02_00501a10` | Wave961 recovered CVertexShader vtable `0x005dfbc4 slot 2`; conservative label for caps-gated compiled-blob create and `.vso` fallback path |
| `0x00501b60` | `CVertexShader__VFunc_03_00501b60` | Vtable slot 3 device shader release helper; exact source virtual name deferred |
| `0x00502060` | `CVertexShader__Create` | Factory method - creates or retrieves cached shader |
| `0x005022a0` | `CVertexShader__LoadFromFile` | Loads shader code from file or compiled blob |
| `0x00502420` | `CVertexShader__CompileShader` | Compiles shader assembly via D3DXAssembleShader |
| `0x00503f90` | `CVertexShader__Clone` | Deep copies a shader object with all resources |
| `0x005019d0` | `CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag` | Reads device caps and updates global VS-enabled support flag (`DAT_00854e6c`) |
| `0x00502290` | `CVertexShader__DecrementLiveReferenceCount` | Release helper that decrements shader live-reference counter at `+0x30` |
| `0x005027f0` | `CVertexShader__LoadCompiledShaderBlobFromVSOFile` | Opens `Shaders/%s.vso`, loads bytecode blob, and issues device create-shader call |
| `0x00503ac0` | `CVertexShader__BuildAndCreateRenderInfoShader` | Builds dynamic render-state declaration/token stream and creates active render-info shader |
| `0x00503dd0` | `CVertexShader__AppendDeclarationNamesToDebugString` | Debug formatter for declaration-token names during shader declaration dumps |
| `0x00501ba0` | `CVertexShader__GetVertexDeclarationToken` | Maps shader-type field (`+0x2C`) to the device vertex-declaration token used by `CEngine__SetShaderObject` |
| `0x00501cd0` | `CVertexShader__ApplyRenderStateShaderConstants` | Uploads projection/view and render-state constant blocks for the active render-state shader path |
| `0x00502920` | `CVertexShader__ApplyCustomRenderStateShaderConstants` | Expanded/custom constant-upload path used when shader custom-state flag (`+0x34`) is enabled |
| `0x005042f0` | `CVertexShader__DeserializeAll` | Wave551 corrected the `VSDS` chunk handler; reads serialized shader table/count data and clones each shader entry |
| `0x00513e20` | `CEngine__SetShaderObject` | Wave850 engine-side shader-object binding helper using declaration token and shader object pointer |
| `0x00513f20` | `CEngine__CreatePixelShaderFromText` | Wave850 pixel-shader compile/create helper over device slot `0x1a8` |
| `0x00513ff0` | `CEngine__DeviceCall16C_CreateVertexShaderLike` | Wave850 bounded vertex-shader-create-like wrapper over device slot `0x16c` |

## Wave533 Static Read-Back

Wave533 saved these signatures/comments/tags in Ghidra after dry/apply/read-back:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x00501800` | `void * __thiscall CVertexShader__CVertexShader(void * this)` | Constructor installs vtable `0x005dfbc4`, links into shader list `0x00854e68`, and seeds type/version `+0x2c` to `9`. |
| `0x00501890` | `void * __thiscall CVertexShader__scalar_deleting_dtor(void * this, byte delete_flags)` | `RET 0x4` proves one delete-flags argument after ECX; bit 0 gates object free. |
| `0x005018b0` | `void __thiscall CVertexShader__dtor(void * this)` | Destructor body unlinks from shader/device lists, releases `+0x28`, and frees constant/source/blob buffers. |
| `0x00501b60` | `int __thiscall CVertexShader__VFunc_03_00501b60(void * this)` | Vtable slot 3 releases the device shader-like pointer at `+0x28`; exact source virtual method name remains open. |
| `0x00501ba0` | `int __thiscall CVertexShader__GetVertexDeclarationToken(void * this)` | Maps type/version `+0x2c` to Direct3D declaration-token constants. |
| `0x00501cd0` | `void __thiscall CVertexShader__ApplyRenderStateShaderConstants(void * this)` | Uploads render-state constants and applies the CVBufTexture texture-transform thunk. |
| `0x00502060` | `void * __cdecl CVertexShader__Create(char * shader_name, int shader_id, int shader_type, void * compiled_blob, int compiled_blob_size, int load_flags)` | Cdecl factory searches cache by blob or name/id, allocates `0x5c` bytes on miss, and increments live refcount `+0x30`. |
| `0x00502290` | `void __thiscall CVertexShader__DecrementLiveReferenceCount(void * this)` | Decrements live refcount `+0x30`. |

Static evidence caveat: runtime shader behavior, runtime Direct3D behavior, concrete `CVertexShader` / `CShaderBase` / device-object layouts, and rebuild parity remain unproven. Vtable slot 2 at `0x00501a10` was later recovered by Wave961 as a conservative slot label; raw caller boundaries `0x0055512a` and `0x0055b3e3` remain deferred.

## Wave534 Static Read-Back

Wave534 saved these signatures/comments/tags in Ghidra after dry/apply/read-back:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x00501730` | `void __cdecl CVertexShader__ClearOut(void)` | Walks shader list `0x00854e68`, reports shader leaks/no-leaks, and runs before `CVBufTexture__ClearOut` during `CLTShell` shutdown. |
| `0x005019d0` | `void __cdecl CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag(void)` | Queries device caps and updates support flag `0x00854e6c` from the `0xfffe0101` comparison. |
| `0x005022a0` | `int __thiscall CVertexShader__LoadFromFile(void * this, char * shader_name, void * source_or_blob, int shader_type, int source_or_blob_size)` | Loads/assembles source or copies supplied blob bytes into `+0x50/+0x54`, then finalizes through vtable `+0x08`. |
| `0x00502420` | `void __thiscall CVertexShader__CompileShader(void * this)` | Injects DirectX 8 vertex declarations, blanks `oFog.x`, assembles shader source, stores bytecode, and frees source. |
| `0x005027f0` | `int __stdcall CVertexShader__LoadCompiledShaderBlobFromVSOFile(char * shader_name, int shader_token, void * device_shader_out)` | `RET 0x0c` helper builds `Shaders/%s.vso`, reads bytecode, and calls the device create-shader path; slot-2 caller boundary at `0x00501a10` was later recovered by Wave961. |
| `0x00502920` | `void __thiscall CVertexShader__ApplyCustomRenderStateShaderConstants(void * this)` | Custom render-state constant uploader using fields `+0x40/+0x38`, render globals, and Direct3D device vtable `+0x178`. |
| `0x00503ac0` | `void * __cdecl CVertexShader__BuildAndCreateRenderInfoShader(void)` | Builds render-info declaration/token stream and returns the `CVertexShader__Create` result consumed by `CDXEngine__ApplyPendingRenderState`. |
| `0x00503dd0` | `void __cdecl CVertexShader__AppendDeclarationNamesToDebugString(char * out_buffer, void * declaration_tokens)` | Formats declaration-token names from table `0x00634074..0x00634554`, falling back to `Unknown`. |
| `0x00503f90` | `void * __cdecl CVertexShader__Clone(void * chunk_reader, int shader_index)` | Chunk-reader clone allocates a fresh `0x5c` shader, reads/deep-copies serialized buffers/tables, optionally reloads `shader%03d.i`, recompiles, and returns the new shader. |

Static evidence caveat: runtime shader behavior, runtime Direct3D behavior, exact chunk schema, concrete layouts, and rebuild parity remain unproven. Wave534 verified `9` target xref rows, `8289` instruction rows, `369` representative callsite rows, and at the time the vtable slot-2 pointer `0x00501a10` still had `NO_FUNCTION_AT_POINTER`; Wave961 later recovered that boundary.

## Wave551 Static Read-Back

Wave551 saved this owner/signature/comment/tag correction in Ghidra after dry/apply/read-back:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x005042f0` | `void __cdecl CVertexShader__DeserializeAll(void * chunk_reader)` | Corrected the former `CResourceAccumulator__InitVertexShaderPrograms` label. `CResourceAccumulator__ReadResourceFile` dispatches the `VSDS` chunk here with the active `CChunkReader` pointer. The body reads a 4-byte serialized table size/version into `DAT_00854e74`, reads a 4-byte shader count, copies `0x4e0` bytes into global table `0x00634070`, clears every third dword across `0x00634074..0x00634554`, and calls `CVertexShader__Clone(chunk_reader, shader_index)` for each serialized shader index. |

Static evidence caveat: exact `VSDS` chunk schema, concrete CVertexShader table layout, platform-guard differences from source, runtime shader behavior, runtime Direct3D behavior, and rebuild parity remain unproven. Wave551 verified `1` metadata row, `1` tag row, `1` xref row, `181` target instruction rows, `621` caller instruction rows, `1` target decompile export, and `1` caller decompile export.

## Wave561 CShaderBase / DeviceObject Static Read-Back

Wave561 saved the shared base-list evidence around the CVertexShader constructor/destructor neighborhood:

| Address | Saved signature | Notes |
| --- | --- | --- |
| `0x00512ca0` | `void __thiscall CShaderBase__Init(void * this)` | Called by CVBuffer, CIBuffer, `CVertexShader__CVertexShader`, CDXLandscape, CUMTexture, CDXMeshVB, CDXShadows, CTexture, CDXTrees, and CWaterRenderSystem constructors; prepends the object into `DAT_00889074` via `this+0x04`. |
| `0x00512cc0` | `uint __stdcall CShaderBase__UnlinkFromRenderObjectLists(void * render_object)` | Called by CUMTexture, CDXTrees, CIBuffer, CVBuffer, CVertexShader, CDXSurf, CDXLandscape, CDXShadows, CDXMeshVB, and CWaterRenderSystem destructors/resets; scans and unlinks from `DAT_00889074` and `DAT_00889078`. |
| `0x00512dc0` | `void * __thiscall DeviceObject__scalar_deleting_dtor(void * this, byte flags)` | DeviceObject vtable slot 0 at `0x005e48c8`; restores base table, unlinks from both global lists, optionally frees on `flags & 1`, and returns `this`. |

This is static retail-binary evidence only. Concrete `CShaderBase`/DeviceObject layouts, exact Direct3D resource ownership, runtime device behavior, and rebuild parity remain unproven.

## Detailed Function Analysis

### CVertexShader__CVertexShader (0x00501800)

**Purpose:** Constructor that initializes a new CVertexShader object.

**Key Operations:**
- Sets vtable pointer to `0x005dfbc4`
- Zeroes out member fields (offsets 0x08-0x24)
- Calls `CShaderBase__Init` (base class initialization)
- Links shader into global shader list via `DAT_00854e68` (linked list head)
- Initializes shader version to 9 (offset 0x2C = `in_ECX[0xb]`)

**Global Data:**
- `DAT_00854e68` - Head of global shader linked list

**Object Layout (partial):**
```
+0x00: vtable pointer
+0x04: unknown (saved/restored in Clone)
+0x08-0x24: zeroed fields (8 dwords)
+0x28: ref count (offset 0x0A)
+0x2C: shader version (0x0B) - initialized to 9
+0x30: ref count 2 (offset 0x0C)
+0x34: is_compiled flag (offset 0x0D)
+0x38: compiled_data (offset 0x0E)
+0x3C: compiled_size (offset 0x0F)
+0x40: constant_table_ptrs (offset 0x10)
+0x44: constant_counts (offset 0x11)
+0x48: source_code (offset 0x12)
+0x4C: source_size (offset 0x13)
+0x50: shader_bytecode (offset 0x14)
+0x54: bytecode_size (offset 0x15)
+0x58: next_shader (offset 0x16) - linked list pointer
```

---

### CVertexShader__Create (0x00502060)

**Purpose:** Factory method that creates a new shader or returns a cached existing one.

**Parameters:**
- `param_1` (char*): Shader name/path
- `param_2` (int): Shader ID/handle
- `param_3` (int): Shader version/type
- `param_4` (char*): Pre-compiled shader data (optional)
- `param_5` (uint): Pre-compiled data size
- `param_6` (undefined4): Additional flags

**Key Operations:**
1. Checks `DAT_0063c108` (shaders enabled flag) - returns NULL if disabled
2. Searches global shader list for existing matching shader
3. If pre-compiled data provided (`param_4 != NULL`):
   - Matches by data content and size
4. If loading from file:
   - Matches by name (via `stricmp` (0x00568390, was `FUN_00568390`)) and ID
5. If no match found:
   - Allocates 0x5C bytes for new CVertexShader object
   - Calls constructor at `0x00501800`
   - Calls `LoadFromFile` or sets up pre-compiled data
6. Increments reference count on success

**Return:** Pointer to CVertexShader object or NULL on failure

**Error Code:** Returns `0x80004005` (E_FAIL) on failure

---

### CVertexShader__LoadFromFile (0x005022a0)

**Purpose:** Loads shader source code from a file and prepares it for compilation.

**Parameters:**
- `this` (`void *`): CVertexShader object
- `shader_name` (`char *`): Shader name copied to object field `+0x08`
- `source_or_blob` (`void *`): Source text or pre-compiled blob pointer
- `shader_type` (`int`): Shader type/version stored at `+0x2c`
- `source_or_blob_size` (`int`): Data size; `-1` means assemble source path

**Key Operations:**
1. Calls virtual method at vtable+0x0C (likely `Lock`)
2. Copies shader name to object (offset 0x08, up to 72 bytes)
3. Sets `is_compiled` flag to 0 (offset 0x34)
4. Sets shader version (offset 0x2C)
5. If `param_4 == 0xFFFFFFFF`:
   - Loads from file using `FUN_00579a9a` (D3DXAssembleShaderFromFile wrapper)
   - On failure, logs error via `DebugTrace` and `FatalError_LocalizedStringId`
6. Otherwise:
   - Allocates memory and copies pre-compiled data
7. Calls virtual method at vtable+0x08 (likely `Unlock`)

**Return:** 0 on success, `0x80004005` on failure

---

### CVertexShader__CompileShader (0x00502420)

**Purpose:** Compiles shader assembly source into GPU bytecode using D3DXAssembleShader.

**Key Operations:**
1. Frees existing compiled shader (offset 0x50) if present
2. Detects shader version by searching for "vs.1.1" or "vs.1.0" strings
3. Builds vertex declaration string based on input semantics found:
   - `dcl_position v0` - always added
   - `dcl_blendweight0 v11` - if blend weights used
   - `dcl_normal v3` - if normals used
   - `dcl_color v5` - if vertex colors used
   - `dcl_texcoord v7` - if texture coordinates used
4. Patches shader source to insert declarations after version string
5. Removes fog output references (`oFog.x` replaced with spaces)
6. Calls `FUN_00579a9a` (D3DXAssembleShader wrapper)
7. On failure, logs detailed error via:
   - `HResultToString` (`0x005be628`) - HRESULT to string conversion
   - Error message: "D3DXAssembleShader failed for %s"
8. Copies compiled bytecode to object (offset 0x50)
9. Frees source code buffer

**Shader Version Strings:**
- `0x0063d038`: "vs.1.0"
- `0x0063d040`: "vs.1.1"

**Vertex Declaration Strings:**
- `0x0063d020`: "vs.1.1\ndcl_position v0\n"
- `0x0063d004`: "dcl_blendweight0 v11\n"
- `0x0063cff0`: "dcl_normal v3\n"
- `0x0063cfdc`: "dcl_color v5\n"
- `0x0063cfc8`: "dcl_texcoord v7\n"

**Error String:**
- `0x0063cf9c`: "D3DXAssembleShader failed for %s"

---

### CVertexShader__Clone (0x00503f90)

**Purpose:** Creates a deep copy of a shader object, duplicating all resources.

**Parameters:**
- `chunk_reader` (`void *`): Chunk reader used to restore serialized shader/resource chunks
- `shader_index` (`int`): Shader index used for debug file naming when `DAT_00662f35` is set

**Key Operations:**
1. Allocates new 0x5C byte object
2. Calls constructor
3. Preserves vtable, field[1], and linked list pointer
4. Copies object data via `CChunkReader__Read` (`0x00423960`; Wave983 `cchunkreader-resource-review-wave983`), not a generic `memcpy_wrapper`
5. Deep copies each resource if present:
   - Compiled data (offset 0x38/0x3C)
   - Constant counts array (offset 0x44) - size from `DAT_00854e74`
   - Constant table pointers (offset 0x40)
   - Shader bytecode (offset 0x50/0x54)
   - Source code (offset 0x48/0x4C)
6. If `DAT_00662f35` is set (debug mode):
   - Loads shader from file "shader%03d.i" using `param_2` as index
7. Calls `CompileShader` to rebuild
8. Cleans up temporary source buffer
9. Calls virtual method vtable+0x08 (Unlock)

**Global Data:**
- `DAT_00854e74` - Number of shader constants
- `DAT_00662f35` - Debug/development mode flag

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x00854e68` | g_pShaderList | Head of global CVertexShader linked list |
| `0x00854e74` | g_nShaderConstants | Number of shader constant slots |
| `0x0063c108` | g_bShadersEnabled | Flag to enable/disable vertex shaders |
| `0x00662f35` | g_bDebugMode | Debug mode flag for shader reloading |

## Related Functions (Called)

| Address | Likely Name | Purpose |
|---------|-------------|---------|
| `0x005490e0` | MemAlloc | Memory allocation with debug info |
| `0x00549220` | MemFree | Memory deallocation |
| `0x00579a9a` | D3DXAssembleShader | DirectX shader assembly wrapper |
| `0x00568390` | strcmp | String comparison |
| `0x00512ca0` | CShaderBase__Init | Base class initialization |
| `0x00423960` | `CChunkReader__Read` | Shared tagged-chunk payload reader verified by Wave983; forwards to `CDXMemBuffer__Read` and tracks `ReadSinceChunk` |
| `0x0042d080` | Assert | Debug assertion |
| `0x0040c640` | DebugPrint | Debug output logging |

Wave983 CChunkReader resource review (`cchunkreader-resource-review-wave983`) verified `CChunkReader__GetNext`, `CChunkReader__Read`, and `CChunkReader__Skip` with `6222/6222 = 100.00%` live closure, Wave911 progress `384/1408 = 27.27%`, expanded static surface `443/1478 = 29.97%`, and backup `[maintainer-local-ghidra-backup-root]\BEA_20260531-001624_post_wave983_cchunkreader_resource_review_verified`. Exact CChunkReader structure layout, runtime archive/resource I/O behavior, exact archive schema coverage, BEA patching, and rebuild parity remain separate proof. The next slice is a Wave900+ recheck before any new candidate cluster.
| `0x005be628` | HResultToString | Convert HRESULT to error string |

## Technical Notes

1. **Shader Caching:** Shaders are cached in a global linked list (`0x00854e68`) to avoid recompilation. The `Create` function searches this list before creating new shaders.

2. **DirectX 8 Shaders:** The code targets DirectX 8 vertex shader assembly (vs.1.0/vs.1.1), not the later HLSL format.

3. **Vertex Declaration Patching:** The compiler automatically inserts vertex input declarations based on which registers are referenced in the shader source.

4. **Fog Output Removal:** The `.oFog.x` output is explicitly disabled by replacing it with spaces - possibly due to hardware compatibility issues.

5. **Reference Counting:** Shaders use reference counting (offset 0x30) to manage lifetime. The `Create` function increments this on each use.

6. **Debug Shader Loading:** When `DAT_00662f35` is set, `Clone` can reload shader source from numbered files (shader000.i, shader001.i, etc.) for runtime modification.

## Cross-References Summary

The VertexShader.cpp debug string at `0x0063cf78` is referenced 15 times:
- 2 refs from `CVertexShader__Create` (allocation)
- 1 ref from `CVertexShader__LoadFromFile` (allocation)
- 2 refs from `CVertexShader__CompileShader` (allocations)
- 8 refs from `CVertexShader__Clone` (multiple allocations)
- 2 refs from unwind handlers (exception handling)
