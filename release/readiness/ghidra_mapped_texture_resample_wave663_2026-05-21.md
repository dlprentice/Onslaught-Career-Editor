# Ghidra Mapped Texture Resample Wave663 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave663 mapped texture resample setup saved static Ghidra metadata for four adjacent mapped texture/resample setup rows:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x0057c7a4` | `CMeshCollisionVolume__LoadMappedTextureResourcesByMode` | `int __thiscall CMeshCollisionVolume__LoadMappedTextureResourcesByMode(void * this, void * mapped_resource_name_or_path, int output_mode, int open_mode_flags, int unused_arg3)` |
| `0x0057cc7b` | `Math__FloorFloatToDouble` | `double __stdcall Math__FloorFloatToDouble(float value)` |
| `0x0057cc8e` | `CFastVB__ClearTripleDword` | `void __fastcall CFastVB__ClearTripleDword(void * triple_dword)` |
| `0x0057cca4` | `CFastVB__BuildResampleKernelBuckets` | `int * __stdcall CFastVB__BuildResampleKernelBuckets(uint output_count, int source_count, int clamp_edges)` |

Tag anchors: `mapped-texture-resample-wave663`, `wave663-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, and `comment-hardened`.

Probe anchors: `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode`, `0x0057cca4 CFastVB__BuildResampleKernelBuckets`, and next queue head `0x0057d216 CFastVB__DispatchMmxKernel_00657974`.

## Evidence

- Dry mode: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`
- Apply mode: `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `4` metadata rows, `4` tag rows, `9` xref rows, `148` instruction rows, and `4` clean decompile rows.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260521-003649_post_wave663_mapped_texture_resample_verified`, `19` files, `163515271` bytes, `DiffCount=0`.

## Queue

Post-Wave663 queue telemetry:

- Total functions: `6098`
- Commented functions: `3648`
- Commentless functions: `2450`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `669`
- Comment-backed proxy: `3648/6098 = 59.82%`
- Strict clean-signature proxy: `3598/6098 = 59.00%`
- Next queue head: `0x0057d216 CFastVB__DispatchMmxKernel_00657974`

## Boundaries

This is static metadata evidence only. Exact mapped texture output mode enum, mapped-file context layout, resample kernel table layout, runtime texture export behavior, runtime resampling quality, BEA patching, and rebuild parity remain unproven.
