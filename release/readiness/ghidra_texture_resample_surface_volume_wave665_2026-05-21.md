# Ghidra Texture Resample Surface/Volume Wave665 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave665 texture resample surface/volume saved static Ghidra metadata for nine adjacent texture conversion, copy, downsample, and resample rows after Wave664:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x0057e0c3` | `CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy` | `int __fastcall CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy(void * texture_resample_context)` |
| `0x0057e200` | `CFastVB__BlendEqualDimensionVolumeData` | `int __fastcall CFastVB__BlendEqualDimensionVolumeData(void * texture_resample_context)` |
| `0x0057e2de` | `CFastVB__BlendClampedVolumeData` | `int __fastcall CFastVB__BlendClampedVolumeData(void * texture_resample_context)` |
| `0x0057e4d3` | `CDXTexture__ResampleSurfaceNearestNeighbor` | `int __fastcall CDXTexture__ResampleSurfaceNearestNeighbor(void * texture_resample_context)` |
| `0x0057e6cc` | `CDXTexture__DownsampleSurface2x2_WithFastPaths` | `int __fastcall CDXTexture__DownsampleSurface2x2_WithFastPaths(void * texture_resample_context)` |
| `0x0057eadb` | `CDXTexture__DownsampleVolume2x2x2` | `int __fastcall CDXTexture__DownsampleVolume2x2x2(void * texture_resample_context)` |
| `0x0057ef10` | `CFastVB__BuildResampleKernel1D` | `void * __stdcall CFastVB__BuildResampleKernel1D(int wrap_edges)` |
| `0x0057f002` | `CDXTexture__ResampleSurfaceBilinear` | `int __fastcall CDXTexture__ResampleSurfaceBilinear(void * texture_resample_context)` |
| `0x0057f391` | `CDXTexture__ResampleVolumeTrilinear` | `int __fastcall CDXTexture__ResampleVolumeTrilinear(void * texture_resample_context)` |

Tag anchors: `texture-resample-wave665`, `wave665-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, `comment-hardened`, and `texture-resample`.

Probe anchors: `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`, `0x0057f391 CDXTexture__ResampleVolumeTrilinear`, and next queue head `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`.

## Evidence

- Dry mode: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`
- Apply mode: `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `9` metadata rows, `9` tag rows, `13` xref rows, `333` instruction rows, and `9` clean decompile rows.
- Backup verified: `G:\GhidraBackups\BEA_20260521-012532_post_wave665_texture_resample_verified`, `19` files, `163580807` bytes, `DiffCount=0`.

## Queue

Post-Wave665 queue telemetry:

- Total functions: `6098`
- Commented functions: `3669`
- Commentless functions: `2429`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `648`
- Comment-backed proxy: `3669/6098 = 60.17%`
- Strict clean-signature proxy: `3619/6098 = 59.35%`
- Next queue head: `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`

## Boundaries

This is static metadata evidence only. Exact texture surface/context layout, palette contract, vtable contract, edge-mode naming, resample-kernel layout, CFastVB owner identity, runtime copy behavior, runtime resample/downsample quality, BEA patching, and rebuild parity remain unproven.
