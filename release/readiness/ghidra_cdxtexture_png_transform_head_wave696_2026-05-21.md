# Ghidra CDXTexture PNG Transform Head Wave696 Readiness

Date: 2026-05-21

Wave696 CDXTexture PNG transform head saved eight adjacent PNG transform-option and row-transform helper rows with the `cdxtexture-png-transform-head-wave696` and `wave696-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x00593812` | `void __stdcall CDXTexture__ConfigureFillerChannel(void * png_decode_state, int filler_sample_value, int place_filler_after_color)` |
| `0x00593861` | `void __stdcall CDXTexture__Swap16BitSampleByteOrder(void * png_row_descriptor, void * row_buffer)` |
| `0x00593890` | `void __stdcall CDXTexture__SwapRgbBgrChannelOrder(void * png_row_descriptor, void * row_buffer)` |
| `0x00593951` | `void __stdcall CDXTexture__SetGammaCorrectionParams(void * png_decode_state, double file_gamma, double display_gamma)` |
| `0x00593989` | `void __stdcall CDXTexture__EnablePaletteExpansion(void * png_decode_state)` |
| `0x00593994` | `void __stdcall CDXTexture__ApplyPngPostprocessLayoutFlags(void * png_decode_state, void * png_info_state)` |
| `0x00593a81` | `void __stdcall CDXTexture__PngExpandPackedSamplesTo8Bit(void * png_row_descriptor, void * row_buffer)` |
| `0x00593b92` | `int __stdcall CDXTexture__PngShiftPackedSamplesBySigBits(void * png_row_descriptor, void * row_buffer, void * significant_bits_table)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `9` xref rows, `296` instruction rows, and `8` clean decompile rows.
- Candidate exports covered `17` adjacent PNG transform rows through `0x00594d5c CDXTexture__ApplyPngRowTransforms`.
- Queue refresh PASS: `6098` total, `3999` commented, `2099` commentless, `1216` exact-undefined signatures, and `327` `param_N` signatures.
- Strict comment-plus-clean-signature proxy from the refreshed TSV is `3943/6098 = 64.66%`.
- Verified backup: `G:\GhidraBackups\BEA_20260521-151249_post_wave696_cdxtexture_png_transform_head_verified`, `19` files, `165088135` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact PNG decode-state layout, row descriptor layout, transform-option enum, color-type enum, filler-channel enum, significant-bits table layout, gamma/color-management policy, packed-sample ordering, row callback ABI, runtime PNG transform behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`.

Probe anchors: `Wave696 CDXTexture PNG transform head`, `cdxtexture-png-transform-head-wave696`, `0x00593812 CDXTexture__ConfigureFillerChannel`, `0x00593b92 CDXTexture__PngShiftPackedSamplesBySigBits`, `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`.
