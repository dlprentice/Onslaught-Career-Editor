# Ghidra Engine Viewpoint Wave872 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `engine-viewpoint-wave872`

Wave872 engine/viewpoint created one missing CRenderQueue vtable-slot function boundary and saved owner-corrected names, signatures, comments, and tags for three renderer/viewpoint helpers from `0x00552410 CRenderQueue__ResetOrCreateField6C0Resource` through `0x005524a0 CRenderQueue__UpdateViewVectorAndMatrix`. The pass corrected stale `CEngine__...` owner framing to CRenderQueue where the vtable and global render queue evidence support it. It made no executable-byte changes.

These rows are high-importance renderer/viewpoint infrastructure, not low-importance filler.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00552410 CRenderQueue__ResetOrCreateField6C0Resource` | Created from vtable DATA xref `0x005e5134`; releases existing `this+0x6c0`, clears it, and conditionally calls global D3D/device-like object `0x00888a50` vtable slot `+0x74` with `0x40,0x40,0x50` and output `&(this+0x6c0)`. |
| `0x00552470 CRenderQueue__ReleaseField6C0Resource` | Vtable DATA xref `0x005e5138`; releases non-null `this+0x6c0`, clears it, and returns zero. |
| `0x005524a0 CRenderQueue__UpdateViewVectorAndMatrix` | `CEngine__SetupLights` callsite `0x0044a38e` with `ECX=0x009c7550`, the documented global render queue; writes view-vector components and a 16-float matrix block with 100.0 scale constants. |
| `0x005e512c` vtable neighborhood | Starts with `CRenderQueue__scalar_deleting_dtor`; slots include `SharedVFunc__ReturnZero_00405930`, `CRenderQueue__ResetOrCreateField6C0Resource`, and `CRenderQueue__ReleaseField6C0Resource`. |

Read-back evidence:

- `CreateFunctionsFromAddressList.java dry`: `created=0 would_create=1 already_exists=0 renamed=0 would_rename=0 failed=0`
- `CreateFunctionsFromAddressList.java apply`: `created=1 would_create=0 already_exists=0 renamed=1 would_rename=0 failed=0`
- `ApplyEngineViewpointWave872.java dry`: `updated=0 skipped=3 renamed=0 would_rename=3 missing=0 bad=0`
- `ApplyEngineViewpointWave872.java apply`: `updated=3 skipped=0 renamed=3 would_rename=0 missing=0 bad=0`
- `ApplyEngineViewpointWave872.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 3 xref rows, 156 instruction rows, 3 decompile rows, 61 `CEngine__SetupLights` xref-site instruction rows, 1 helper metadata row, 16 vtable rows, and 242 boundary-check instruction rows.
- Queue after Wave872: 6106 total, 5857 commented, 249 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5857/6106 = 95.92%`, strict clean-signature proxy `5857/6106 = 95.92%`.
- Next raw commentless row: `0x00553960 CDXEngine__RenderMultipassLayerA`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-191020_post_wave872_engine_viewpoint_verified`, 19 files, 172460935 bytes, `DiffCount=0`.

What this proves:

- The missing `0x00552410` function boundary exists in the saved Ghidra project after creation and read-back.
- The three target rows have saved owner-corrected names, clean signatures, comments, and tags including `engine-viewpoint-wave872` and `wave872-readback-verified`.
- The CRenderQueue owner correction is supported by the vtable neighborhood, `CRenderQueue__scalar_deleting_dtor`, DATA refs at `0x005e5134/0x005e5138`, and the global render queue call from `CEngine__SetupLights`.
- The observed resource slot and view-vector/matrix bodies are static retail Ghidra evidence tied to post metadata, tags, xrefs, instruction exports, decompiles, vtable exports, and helper metadata.

What remains unproven:

- Exact `CRenderQueue` field layout.
- Exact resource type at `this+0x6c0`.
- Exact D3D/device call contract for vtable slot `+0x74`.
- Runtime render/viewpoint behavior.
- Runtime resource cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
