# Ghidra CDXTexture PNG Option Accessors Wave695 Readiness

Date: 2026-05-21

Wave695 CDXTexture PNG option accessors saved twelve adjacent PNG cleanup, option-info, and transform-flag helper rows with the `cdxtexture-png-option-accessors-wave695` and `wave695-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x00593526` | `void __stdcall CDXTexture__ReleasePngDecodeContextHandles(void * png_decode_context_slot, void * primary_row_workspace_slot, void * secondary_row_workspace_slot)` |
| `0x005935a3` | `uint __stdcall CDXTexture__TestDecodeOptionFlagMask(void * png_decode_state, void * png_info_state, uint flag_mask)` |
| `0x005935c0` | `int __stdcall CDXTexture__GetDecodeRowStride(void * png_decode_state, void * png_info_state)` |
| `0x005935d9` | `int __stdcall CDXTexture__GetOutputChannelCount(void * png_decode_state, void * png_info_state)` |
| `0x005935f2` | `int __stdcall CDXTexture__GetOutputGamma(void * png_decode_state, void * png_info_state, double * out_gamma)` |
| `0x0059361e` | `int __stdcall CDXTexture__GetRenderingIntent(void * png_decode_state, void * png_info_state, int * out_rendering_intent)` |
| `0x0059371d` | `int __stdcall CDXTexture__GetPaletteBufferInfo(void * png_decode_state, void * png_info_state, void * out_palette_buffer, int * out_palette_count)` |
| `0x00593753` | `int __stdcall CDXTexture__GetTransparencyInfo(void * png_decode_state, void * png_info_state, void * out_transparency_table, int * out_transparency_count, void * out_transparent_color)` |
| `0x005937bc` | `void __stdcall CDXTexture__EnableByteSwapTransform(void * png_decode_state)` |
| `0x005937c7` | `void __stdcall CDXTexture__EnableSwap16TransformIfNeeded(void * png_decode_state)` |
| `0x005937db` | `void __stdcall CDXTexture__EnableExpandTo8Bit(void * png_decode_state)` |
| `0x005937f6` | `int __stdcall CDXTexture__GetPngPassCountFromInterlace(void * png_decode_state)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0`, then `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `12` metadata rows, `12` tag rows, `14` xref rows, `444` instruction rows, and `12` clean decompile rows.
- Candidate exports covered `20` adjacent PNG option/transform rows through `0x00593b92 CDXTexture__PngShiftPackedSamplesBySigBits`.
- Queue refresh PASS: `6098` total, `3991` commented, `2107` commentless, `1216` exact-undefined signatures, and `335` `param_N` signatures.
- Verified backup: `G:\GhidraBackups\BEA_20260521-150000_post_wave695_cdxtexture_png_option_accessors_verified`, `19` files, `165088135` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact PNG info-state layout, slot ownership, output pointer nullability contracts, palette/tRNS/gamma/sRGB enum identity, transform-flag enum, bit-depth/interlace fields, runtime PNG option behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x00593812 CDXTexture__ConfigureFillerChannel`.

Probe anchors: `Wave695 CDXTexture PNG option accessors`, `cdxtexture-png-option-accessors-wave695`, `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`, `0x005937f6 CDXTexture__GetPngPassCountFromInterlace`, `0x00593812 CDXTexture__ConfigureFillerChannel`.
