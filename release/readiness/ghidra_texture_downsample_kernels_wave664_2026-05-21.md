# Ghidra Texture Downsample Kernels Wave664 Readiness

Status: ready for public-safe release accounting
Date: 2026-05-21

## Scope

Wave664 texture downsample kernels saved static Ghidra metadata for twelve adjacent texture downsample helper rows called by `0x0057e6cc CDXTexture__DownsampleSurface2x2_WithFastPaths`:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x0057d216` | `CFastVB__DispatchMmxKernel_00657974` | `void __fastcall CFastVB__DispatchMmxKernel_00657974(void * downsample_context)` |
| `0x0057d4ad` | `CFastVB__DispatchMmxKernel_00657978` | `void __fastcall CFastVB__DispatchMmxKernel_00657978(void * downsample_context)` |
| `0x0057d4db` | `CDXTexture__Average2x2Block_RGB565` | `int __fastcall CDXTexture__Average2x2Block_RGB565(void * downsample_context)` |
| `0x0057d62b` | `CDXTexture__Average2x2Block_RGB555` | `int __fastcall CDXTexture__Average2x2Block_RGB555(void * downsample_context)` |
| `0x0057d74f` | `CDXTexture__Average2x2Block_ARGB1555` | `int __fastcall CDXTexture__Average2x2Block_ARGB1555(void * downsample_context)` |
| `0x0057d89e` | `CDXTexture__Average2x2Block_A4R4G4B4` | `int __fastcall CDXTexture__Average2x2Block_A4R4G4B4(void * downsample_context)` |
| `0x0057d9f1` | `CFastVB__Downsample2x1_R5G6B5` | `int __fastcall CFastVB__Downsample2x1_R5G6B5(void * downsample_context)` |
| `0x0057db30` | `CFastVB__Downsample2x1_L8` | `int __fastcall CFastVB__Downsample2x1_L8(void * downsample_context)` |
| `0x0057dbcb` | `CFastVB__Downsample2x1_A1R5G5B5` | `int __fastcall CFastVB__Downsample2x1_A1R5G5B5(void * downsample_context)` |
| `0x0057dd17` | `CDXTexture__Average2x2Block_RGB444` | `int __fastcall CDXTexture__Average2x2Block_RGB444(void * downsample_context)` |
| `0x0057de38` | `CDXTexture__Average2x2Block_A8L8` | `int __fastcall CDXTexture__Average2x2Block_A8L8(void * downsample_context)` |
| `0x0057df84` | `CDXTexture__Average2x2Block_A4L4` | `int __fastcall CDXTexture__Average2x2Block_A4L4(void * downsample_context)` |

Tag anchors: `texture-downsample-wave664`, `wave664-readback-verified`, `static-reaudit`, `retail-binary-evidence`, `signature-hardened`, `comment-hardened`, and `texture-downsample`.

Probe anchors: `0x0057d216 CFastVB__DispatchMmxKernel_00657974`, `0x0057df84 CDXTexture__Average2x2Block_A4L4`, and next queue head `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`.

## Evidence

- Dry mode: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`
- Apply mode: `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`
- Final dry mode: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- All three passes reported `REPORT: Save succeeded`.
- Post exports verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows.
- Backup verified: `[maintainer-local-ghidra-backup-root]\BEA_20260521-005813_post_wave664_texture_downsample_verified`, `19` files, `163548039` bytes, `DiffCount=0`.

## Queue

Post-Wave664 queue telemetry:

- Total functions: `6098`
- Commented functions: `3660`
- Commentless functions: `2438`
- Exact-undefined signatures: `1217`
- `param_N` signatures: `657`
- Comment-backed proxy: `3660/6098 = 60.02%`
- Strict clean-signature proxy: `3610/6098 = 59.20%`
- Next queue head: `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`

## Boundaries

This is static metadata evidence only. Exact surface/context layout, CPU dispatch pointer identity, packed format contracts, retained CFastVB owner identity, runtime downsample behavior, runtime filter quality, BEA patching, and rebuild parity remain unproven.
