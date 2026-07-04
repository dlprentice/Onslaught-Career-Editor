# CDXSurf__UnlinkNodeFromGlobalList

Wave1213 (`wave1213-render-resource-lifecycle-tail-current-risk-review`) re-read `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` as a current-risk denominator row inside the mesh/resource/render static contract. Fresh xrefs remain `0x00556e70 CDXSurf__dtor`, `0x005d7d36 Unwind@005d7d30`, and `0x005d7d81 Unwind@005d7d50`; instruction evidence still walks `DAT_0083d9b0` through `node+0xa0` and unlinks the node matching `texture_base-0x08`. The wave made no mutation. Active current-risk progress moved to `1125/1179 = 95.42%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified`. Runtime Direct3D/surface lifetime behavior, exact list-node layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave832 Texture/Surface Prelude (`texture-surface-prelude-wave832`, `wave832-readback-verified`) hardened `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` as `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`.

Probe anchors: `Wave832 Texture/Surface Prelude`, `texture-surface-prelude-wave832`, `0x004f2710 CTextureBase__Init`, `void * __fastcall CTextureBase__Init(void * texture_base)`, `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList`, `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`, `DAT_0083d9b0`, `JCLTEX #%d`, `0x00556ce1`, `0x00556e70`, `5654/6098 = 92.72%`, `0x004f5b70 CParticleDescriptor__SetIndexedParam`, `[maintainer-local-ghidra-backup-root]\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

## Static Evidence

Fresh xref-site instruction windows show three ECX-only paths into this helper:

| Site | Evidence |
| --- | --- |
| `0x00556e70 CDXSurf__dtor` | Branches to `LEA ECX, [ESI+0x8]` when the object pointer is non-null, otherwise `XOR ECX, ECX`, then calls `0x004f2790`. |
| `0x005d7d30 Unwind@005d7d30` | Loads `ECX = *(EBP-0x10)+0x08` and jumps to `0x004f2790`. |
| `0x005d7d50 Unwind@005d7d50` | Computes `object+0x08` or null into a local, loads it into `ECX`, then jumps to `0x004f2790`. |

The saved body walks the global texture/surface list head `DAT_0083d9b0` through `node+0xa0` links, compares each node against `texture_base-0x08` or null, and unlinks a match by updating the previous node's `+0xa0` link or the global head. This corrects the stale cdecl stack-argument signature to the observed ECX ABI.

`0x004f2710 CTextureBase__Init` is the paired construction-side row: `CTexture__ctor` callsite `0x00556ce1` passes `this+0x08`, and the initializer links `texture_base-0x08` into `DAT_0083d9b0` while formatting `JCLTEX #%d`.

## Read-Back

`ApplyTextureSurfacePreludeWave832.java` dry/apply/final dry reported clean summaries with `missing=0` and `bad=0`, and post exports verified two metadata rows, two tag rows, four xref rows, 74 target instruction rows, two target decompile rows, 11 context metadata rows, 11 context decompile rows, and 148 xref-site instruction rows.

Post-Wave832 queue telemetry is `6098` total, `5654` commented, `444` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5654/6098 = 92.72%`, and next raw head `0x004f5b70 CParticleDescriptor__SetIndexedParam`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

## Boundary

This proves saved static retail Ghidra metadata only. Exact texture.cpp or DXSurf.cpp source-body identity, concrete `CTextureBase`, `CDXSurf`, or `CTexture` ownership boundary, full field layout, runtime texture/surface lifetime behavior, BEA patching, and rebuild parity remain deferred.
