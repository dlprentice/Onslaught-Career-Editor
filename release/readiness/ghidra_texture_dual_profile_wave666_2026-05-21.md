# Ghidra Texture Dual-Profile/Upload Wave666 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave666 texture dual-profile/upload saved static Ghidra metadata for ten adjacent texture conversion, profile, and upload rows after Wave665:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x0057fa10` | `CFastVB__BlendWeightTable_scalar_deleting_dtor` | `int * __thiscall CFastVB__BlendWeightTable_scalar_deleting_dtor(void * this, uint delete_flags, int unused_context)` |
| `0x0057fa5c` | `CFastVB__BlendDualProfileBoneWeights` | `int __fastcall CFastVB__BlendDualProfileBoneWeights(void * dual_profile_context)` |
| `0x00580120` | `CFastVB__RunDualProfileConversionStage` | `int __fastcall CFastVB__RunDualProfileConversionStage(void * dual_profile_context)` |
| `0x0058070e` | `CFastVB__InitDualTexelConversionPipeline` | `int __thiscall CFastVB__InitDualTexelConversionPipeline(void * this, void * source_profile_descriptor, void * destination_profile_descriptor, int conversion_flags, uint unused_context)` |
| `0x0058083d` | `CDXTexture__ResetSurfaceCopyContext` | `void __fastcall CDXTexture__ResetSurfaceCopyContext(void * surface_copy_context)` |
| `0x00580850` | `CDXTexture__CopyLockedRectPitchAware` | `int __stdcall CDXTexture__CopyLockedRectPitchAware(void * source_surface, void * destination_surface)` |
| `0x0058092d` | `CDXTexture__FinalizeTextureUploadAndReleaseTemp` | `int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp(void * upload_context)` |
| `0x005809de` | `CFastVB__ShutdownActiveProfile` | `int __fastcall CFastVB__ShutdownActiveProfile(void * active_profile_slot)` |
| `0x00580a00` | `CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate` | `int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(void * upload_context)` |
| `0x00580eef` | `CFastVB__ShutdownActiveProfile_Thunk` | `int __fastcall CFastVB__ShutdownActiveProfile_Thunk(void * active_profile_slot)` |

Tag anchors: `texture-dual-profile-wave666`, `wave666-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`, `0x00580eef CFastVB__ShutdownActiveProfile_Thunk`, and next queue head `0x00581263 CFastVB__TexelUnpackProfile__dtor`.

## Evidence

- Dry mode: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`
- Apply mode: `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `10` metadata rows, `10` tag rows, `22` xref rows, `1060` instruction rows, and `10` clean decompile rows.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260521-014950_post_wave666_texture_dual_profile_verified`, `19` files, `163613575` bytes, `DiffCount=0`.

## Queue

Post-Wave666 queue telemetry:

- Total functions: `6098`
- Commented functions: `3679`
- Commentless functions: `2419`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `638`
- Comment-backed proxy: `3679/6098 = 60.33%`
- Strict clean-signature proxy: `3629/6098 = 59.51%`
- Next queue head: `0x00581263 CFastVB__TexelUnpackProfile__dtor`

## Boundaries

This is static metadata evidence only. Exact profile/layout identity, exact descriptor layout, flag enum naming, callback body semantics, COM/D3D interface contracts, UpdateSurface identity, runtime texture conversion behavior, runtime upload behavior, BEA patching, and rebuild parity remain unproven.
