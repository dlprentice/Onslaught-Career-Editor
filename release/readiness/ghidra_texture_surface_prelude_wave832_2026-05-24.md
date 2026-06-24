# Ghidra Texture/Surface Prelude Wave832 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `texture-surface-prelude-wave832`

Probe anchors: `Wave832 Texture/Surface Prelude`, `texture-surface-prelude-wave832`, `0x004f2710 CTextureBase__Init`, `void * __fastcall CTextureBase__Init(void * texture_base)`, `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList`, `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`, `DAT_0083d9b0`, `JCLTEX #%d`, `0x00556ce1`, `0x00556e70`, `5654/6098 = 92.72%`, `0x004f5b70 CParticleDescriptor__SetIndexedParam`, `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

Wave832 hardened saved Ghidra comments, tags, and signatures for two adjacent texture/surface lifecycle helpers:

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x004f2710 CTextureBase__Init` | `void * __fastcall CTextureBase__Init(void * texture_base)` | `CTexture__ctor` callsite `0x00556ce1` loads `ECX=this+0x08`; the body records prior `DAT_0083d9b0` at `texture_base+0x98`, links the owner by storing `texture_base-0x08` in `DAT_0083d9b0`, zeroes the name/subobject head, stores observed defaults, formats generated name string `JCLTEX #%d` from `0x00632eb4`, increments `DAT_0083d99c`, and returns `texture_base`. |
| `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` | `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)` | Fresh call-site instruction exports show `CDXSurf__dtor` at `0x00556e70` and unwind rows `0x005d7d30`/`0x005d7d50` load `ECX` with `object+0x08` or null before calling/jumping here. The body walks `DAT_0083d9b0` through `node+0xa0` links, compares each node against `texture_base-0x08`, and unlinks a match by updating either the previous node link or the global head. |

Read-back evidence:

- `ApplyTextureSurfacePreludeWave832.java dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`
- `ApplyTextureSurfacePreludeWave832.java apply`: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`
- `ApplyTextureSurfacePreludeWave832.java final dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 2 metadata rows, 2 tag rows, 4 xref rows, 74 target instruction rows, 2 target decompile rows, 11 context metadata rows, 11 context decompile rows, and 148 xref-site instruction rows.
- Queue after Wave832: 6098 total, 5654 commented, 444 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5654/6098 = 92.72%`, strict clean-signature proxy `5654/6098 = 92.72%`.
- Next raw commentless row: `0x004f5b70 CParticleDescriptor__SetIndexedParam`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`, 19 files, 171772807 bytes, `DiffCount=0`.

What this proves:

- The two target rows exist in the saved Ghidra project.
- The saved signatures match the observed ECX ABI and no longer show the stale cdecl stack-argument spelling for `CDXSurf__UnlinkNodeFromGlobalList`.
- The saved comments and tags include `texture-surface-prelude-wave832` and `wave832-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to fresh metadata, xrefs, instruction exports, decompile exports, string dumps, and xref-site instruction windows.

What remains unproven:

- Exact texture.cpp or DXSurf.cpp source-body identity.
- Concrete `CTextureBase`, `CDXSurf`, or `CTexture` ownership boundary and full field layout.
- Runtime texture/surface lifetime behavior.
- BEA patching behavior.
- Rebuild parity.
