# CTextureBase__Init

Wave832 Texture/Surface Prelude (`texture-surface-prelude-wave832`, `wave832-readback-verified`) hardened `0x004f2710 CTextureBase__Init` as `void * __fastcall CTextureBase__Init(void * texture_base)`.

Probe anchors: `Wave832 Texture/Surface Prelude`, `texture-surface-prelude-wave832`, `0x004f2710 CTextureBase__Init`, `void * __fastcall CTextureBase__Init(void * texture_base)`, `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList`, `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`, `DAT_0083d9b0`, `JCLTEX #%d`, `0x00556ce1`, `0x00556e70`, `5654/6098 = 92.72%`, `0x004f5b70 CParticleDescriptor__SetIndexedParam`, `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

## Static Evidence

`CTexture__ctor` callsite `0x00556ce1` loads `ECX=this+0x08` and calls this helper. The saved body records the prior global texture/surface list head `DAT_0083d9b0` at `texture_base+0x98`, links the owning object into that global by storing `texture_base-0x08`, zeroes the 0x80-byte name/subobject head, clears observed fields at `+0x9c`, `+0xaa`, and `+0xac`, stores `-1` at `+0x94`, formats the generated name string `JCLTEX #%d` from `0x00632eb4` using counter `DAT_0083d99c`, increments the counter, and returns `texture_base`.

Read-back verified `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` as the paired ECX-only global-list unlink helper from `0x00556e70 CDXSurf__dtor` and unwind rows. Together these rows document important connective/static infrastructure for texture-base construction and surface-list teardown.

## Read-Back

`ApplyTextureSurfacePreludeWave832.java` dry/apply/final dry reported clean summaries with `missing=0` and `bad=0`, and post exports verified two metadata rows, two tag rows, four xref rows, 74 target instruction rows, two target decompile rows, 11 context metadata rows, 11 context decompile rows, and 148 xref-site instruction rows.

Post-Wave832 queue telemetry is `6098` total, `5654` commented, `444` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5654/6098 = 92.72%`, and next raw head `0x004f5b70 CParticleDescriptor__SetIndexedParam`. Verified backup: `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

## Boundary

This proves saved static retail Ghidra metadata only. Exact texture.cpp or DXSurf.cpp source-body identity, concrete `CTextureBase`, `CDXSurf`, or `CTexture` ownership boundary, full field layout, runtime texture/surface lifetime behavior, BEA patching, and rebuild parity remain deferred.
