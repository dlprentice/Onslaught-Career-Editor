# Ghidra Raw Commentless Head Wave806 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `raw-commentless-head-wave806`

Wave806 raw commentless head saved names, signatures, comments, and tags for five adjacent texture/terrain/file-buffer helpers from `0x0048ddf0` through `0x0048dec0`, plus the shared texture refcount helper at `0x004f27e0`. The pass made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0048ddf0 CDXMemBuffer__Close_Thunk` | `bool __fastcall CDXMemBuffer__Close_Thunk(void * this)` | Single-instruction thunk to `0x00548c00 CDXMemBuffer__Close`; xref from `CParticleSet__LoadParticleSetFile`. |
| `0x0048de90 CDXLandscape__ClearMixerDetailTextureHandle` | `void * __thiscall CDXLandscape__ClearMixerDetailTextureHandle(void * this)` | Clears global texture handle `0x0067a7d0`; supersedes older Wave420 HUD-marker wording because adjacent loader/release evidence identifies the global as the mixer-detail texture handle. |
| `0x0048dea0 CDXLandscape__ReleaseMixerDetailTextureRef` | `void __cdecl CDXLandscape__ReleaseMixerDetailTextureRef(void)` | Releases non-null global `0x0067a7d0` through `CTexture__DecrementRefCountFromNameField(handle+0x08)`, then clears the global; xrefs include `CDXLandscape__Destructor` and `Unwind@005d7980`. |
| `0x0048dec0 CResourceAccumulator__LoadMixerDetailTexture` | `void __cdecl CResourceAccumulator__LoadMixerDetailTexture(int detail_index)` | `CHeightField__DeserializeMapAndInitResources` pushes byte field `this+0x1094`; helper formats `mixers\detail%.2d.tga` at `0x0062d80c` and stores `CTexture__FindTexture(...)` into `0x0067a7d0`. |
| `0x004f27e0 CTexture__DecrementRefCountFromNameField` | `void __thiscall CTexture__DecrementRefCountFromNameField(void * this)` | Decrements `*(this+0x9c)`; observed callers pass `texture+0x08`, so this updates the texture refcount at `texture+0xa4`, matching `CTexture__FindTexture` cache-hit increments and superseding `CHud__DecrementCounter9C`. |

Read-back evidence:

- Initial dry: `updated=0 skipped=5 renamed=0 would_rename=4 signature_updated=5 comment_only_updated=0 missing=0 bad=0`.
- Initial apply preserved for audit: four rows saved, then `0x004f27e0` exposed a read-back signature mismatch because the first script spec named the implicit thiscall receiver as `texture_name_field`; Ghidra materialized `void * this` plus an extra explicit parameter. The saved project was corrected in the same wave.
- Corrective dry/apply/final dry: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=1 skipped=4 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, all with `REPORT: Save succeeded`.
- Post exports: 5 metadata rows, 5 tag rows, 120 xref rows, 525 instruction rows, and 5 decompile rows.
- Queue after Wave806: 6098 total, 5581 commented, 517 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5581/6098 = 91.52%`, strict clean-signature proxy `5581/6098 = 91.52%`.
- Next raw commentless row: `0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The five target function rows exist in the saved Ghidra project with the Wave806 names/signatures/comments/tags.
- The old `CDXLandscape__ClearPendingHudMarkerHandle`, `CDXLandscape__ReleasePendingHudMarker`, and `CHud__DecrementCounter9C` labels are superseded for these rows by the saved static evidence.
- The observed texture global/refcount evidence is static retail Ghidra evidence tied to xrefs, instruction/decompile exports, source-context callsites, and string dump `0x0062d80c`.

What remains unproven:

- Exact source-body identity.
- Exact CDXLandscape/CResourceAccumulator/CTexture field names and full layouts.
- Runtime particle file teardown, terrain rendering, texture lifetime, or resource-loading behavior.
- BEA patching behavior.
- Rebuild parity.
