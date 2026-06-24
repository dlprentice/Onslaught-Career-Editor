# Ghidra CDXTexture PNG Row-Transform Tail Wave697 Readiness

Date: 2026-05-21

Wave697 CDXTexture PNG row-transform tail saved nine adjacent PNG row-transform and post-decode helper rows with the `cdxtexture-png-row-transform-tail-wave697` and `wave697-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x00593d0b` | `void __stdcall CDXTexture__PngStrip16BitSamplesTo8Bit(void * png_row_descriptor, void * row_buffer)` |
| `0x00593d51` | `void __stdcall CDXTexture__PngInsertFillerChannel(void * png_row_descriptor, void * row_buffer, uint filler_sample_value, uint layout_flags)` |
| `0x00593f8a` | `void __stdcall CDXTexture__PngApplyRowTransformLuts(void * png_row_descriptor, void * row_buffer, int byte_lut_table, void * word_lut_table, int word_lut_index_shift)` |
| `0x005942da` | `void __stdcall CDXTexture__ExpandIndexedRowToRgbOrRgba(void * png_row_descriptor, void * row_buffer, void * palette_rgb_table, void * palette_alpha_table, int palette_alpha_count)` |
| `0x005944e3` | `void __stdcall CDXTexture__PngExpandTransparentColorToAlpha(void * png_row_descriptor, void * row_buffer, void * transparent_color_record)` |
| `0x00594836` | `void __stdcall CDXTexture__PngConvertRgbRowsToPaletteIndices(void * png_row_descriptor, void * row_buffer, void * rgb_to_palette_lut, void * index_remap_lut)` |
| `0x00594945` | `void __stdcall CDXTexture__BuildPngGammaAndExpandTables(void * png_decode_state)` |
| `0x00594c48` | `void __stdcall CDXTexture__ApplyPngPostDecodeTransforms(void * png_decode_state)` |
| `0x00594d5c` | `void __stdcall CDXTexture__ApplyPngRowTransforms(void * png_decode_state)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `9` metadata rows, `9` tag rows, `9` xref rows, `333` instruction rows, and `9` clean decompile rows.
- Candidate exports covered `17` adjacent PNG row-transform and decode-option rows through `0x005950e0 CDXTexture__ComparePngSignatureBytes`.
- Queue refresh PASS: `6098` total, `4008` commented, `2090` commentless, `1216` exact-undefined signatures, and `318` `param_N` signatures.
- Strict comment-plus-clean-signature proxy from the refreshed TSV is `3952/6098 = 64.81%`.
- Verified backup: `G:\GhidraBackups\BEA_20260521-154041_post_wave697_cdxtexture_png_row_transform_tail_verified`, `19` files, `165120903` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact PNG decode-state layout, row descriptor layout, transform-option enum, color-type enum, palette/tRNS table layout, filler-channel enum, gamma/color-management policy, RGB key packing, transform order, row callback ABI, runtime PNG transform behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x00594ef8 CDXTexture__SetDecodeOptionFloat`.

Probe anchors: `Wave697 CDXTexture PNG row-transform tail`, `cdxtexture-png-row-transform-tail-wave697`, `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`, `0x00594d5c CDXTexture__ApplyPngRowTransforms`, `0x00594ef8 CDXTexture__SetDecodeOptionFloat`.
