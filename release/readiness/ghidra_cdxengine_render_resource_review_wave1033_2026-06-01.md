# Ghidra CDXEngine Render Resource Review Wave1033

Status: complete static read-back with two saved comment/tag corrections
Date: 2026-06-01
Scope: `cdxengine-render-resource-review-wave1033`

Wave1033 re-read the CDXEngine render/resource connector cluster and saved two stale-comment corrections where older notes still used the Wave216/Wave217 HUD-specific `CHud__DecrementCounter9C` helper wording after Wave806 had normalized `0x004f27e0` to `CTexture__DecrementRefCountFromNameField`. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Primary targets:

| Address | Saved state confirmed by Wave1033 | Fresh evidence |
| --- | --- | --- |
| `0x0044a640 CDXEngine__SetOverlaySlotVisibilityByPlayerView` | `void __thiscall CDXEngine__SetOverlaySlotVisibilityByPlayerView(void * this, int playerView)` | Called by `CDXEngine__PreRender` and `CDXEngine__Render`; reads the overlay/view object at `this+0x18`, forwards `playerView` to `CDXEngine__SetOverlaySlotsEnabledForActiveViews`, and returns with one stack argument. |
| `0x0053d3a0 CDXEngine__ReleaseDefaultTextureAndMeshRefs` | `void __fastcall CDXEngine__ReleaseDefaultTextureAndMeshRefs(void * this)` | Saved Wave1033 correction now says this calls `CTexture__DecrementRefCountFromNameField(texture+8)`, decrements the default mesh usage counter at `this+0x28 + 0x170`, and clears both slots. |
| `0x00542a50 CDXEngine__BuildDirectionalSampleRing` | `void __cdecl CDXEngine__BuildDirectionalSampleRing(float view_yaw_radians)` | `CDXEngine__Render` calls the one-float helper after camera/view yaw setup; body records yaw at `0x0067a680`, builds sample-ring matrices, derives view direction at `0x008aa780`, and packs sort keys through `CDXEngine__PackVec3AndDepthToSortKey`. |
| `0x00544040 CDXEngine__ClearKempyCubeTextureSlots` | `void * __fastcall CDXEngine__ClearKempyCubeTextureSlots(void * kempy_cube_resources)` | `CEngine__Init` calls this for the `engine+0x498` Kempy cube block; body zeroes five texture slots at `+0x00..+0x10` and returns the same resource pointer. |

Context evidence:

- `0x0044a650 CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite` remains a zero-argument render-state helper called from CDXEngine and HUD render paths.
- `0x0053d3e0 CDXEngine__Shutdown`, `0x0053d5f0 CDXEngine__Init`, and `0x0053d6d0 CDXEngine__InitResources` keep the default texture/mesh, CDXPatchManager, console-variable, resource-load, and vtable-slot context for the corrected default-resource release helper.
- `0x00543300 CDXEngine__RenderImposterBillboardSet` and `0x005438c0 CDXImposter__RenderAll` keep the imposter render context for `CDXEngine__BuildDirectionalSampleRing`.
- `0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` received the second Wave1033 correction: it now says the five texture pointers are decremented through `CTexture__DecrementRefCountFromNameField(texture+8)`, then the global CVBuffer pointer `0x008aa908` is released and cleared.
- `0x005440a0 CDXEngine__InitKempyCubeTexturesAndVertexBuffer`, `0x005441a0 CDXEngine__InitKempyCubeResources`, and `0x005441b0 CDXEngine__RenderKempyCubeFaces` keep the Kempy texture load, wrapper, vertex-buffer, and render-face context.

Evidence counts:

- Pre-correction primary exports: 4 metadata rows, 4 tag rows, 6 xref rows, 312 body-instruction rows, and 4 decompile rows.
- Pre-correction context exports: 10 metadata rows, 10 tag rows, 16 xref rows, 1113 body-instruction rows, and 10 decompile rows.
- Xref call-site windows: 19 call-site targets and 513 around-instruction rows, missing=0.
- Apply logs: dry `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=11 missing=0 bad=0`; apply `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=11 missing=0 bad=0`; final dry `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post-correction primary exports: 4 metadata rows, 4 tag rows, and 4 decompile rows.
- Post-correction context exports: 10 metadata rows, 10 tag rows, and 10 decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1033: `635/1408 = 45.10%`; expanded static surface progress: `864/1493 = 57.87%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-051834_post_wave1033_cdxengine_render_resource_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected CDXEngine render/resource rows still have coherent saved names, signatures, comments, tags, xrefs, instruction bodies, and decompile output.
- The two stale comments were corrected in the saved Ghidra project to use the current Wave806 texture-refcount helper name.
- The correction is bounded to static Ghidra comments/tags for `0x0053d3a0` and `0x00544060`.

What remains unproven:

- Exact CDXEngine/CTexture/Kempy cube/CVBuffer layouts.
- Runtime render output, shutdown behavior, texture lifetime behavior, or resource ownership behavior.
- Exact source-body identity for the reviewed helpers.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1033; cdxengine-render-resource-review-wave1033; 0x0044a640 CDXEngine__SetOverlaySlotVisibilityByPlayerView; 0x0053d3a0 CDXEngine__ReleaseDefaultTextureAndMeshRefs; 0x00542a50 CDXEngine__BuildDirectionalSampleRing; 0x00544040 CDXEngine__ClearKempyCubeTextureSlots; 0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer; CTexture__DecrementRefCountFromNameField; supersedes older CHud__DecrementCounter9C wording; 635/1408 = 45.10%; 864/1493 = 57.87%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-051834_post_wave1033_cdxengine_render_resource_review_verified; two comment/tag corrections.
