# Ghidra CDXTexture PNG Decode-Option Tail Wave698 Readiness

Date: 2026-05-21

Wave698 CDXTexture PNG decode-option tail saved eight adjacent PNG decode-option, source-read, and signature-check helper rows with the `cdxtexture-png-decode-option-tail-wave698` and `wave698-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x00594ef8` | `void __stdcall CDXTexture__SetDecodeOptionFloat(void * png_decode_state, void * png_info_state, double option_value)` |
| `0x00594fb6` | `void __stdcall CTexture__SetDecodeScanParameters(void * png_decode_state, void * png_info_state, void * scan_parameter_table, int scan_parameter_count)` |
| `0x00594fdc` | `void __stdcall CDXTexture__SetDecodeOptionByte(void * png_decode_state, void * png_info_state, int option_byte_value)` |
| `0x00594ff9` | `void __stdcall CDXTexture__SetDecodeOptionByteWithDefaultFloat(void * png_decode_state, void * png_info_state, int option_byte_value)` |
| `0x00595030` | `void __stdcall CDXTexture__SetDecodeOptionParams(void * png_decode_state, void * png_info_state, void * parameter_table, int parameter_count, void * parameter_record)` |
| `0x00595079` | `void __stdcall CDXTexture__ReadFromSource(void * png_decode_state, void * destination_buffer, uint requested_byte_count)` |
| `0x005950a2` | `void __stdcall CDXTexture__SetReadFunction(void * png_decode_state, void * read_context, void * read_callback)` |
| `0x005950e0` | `int __stdcall CDXTexture__ComparePngSignatureBytes(void * signature_buffer, uint start_offset, uint bytes_to_check)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `18` xref rows, `296` instruction rows, and `8` clean decompile rows.
- Queue refresh PASS: `6098` total, `4016` commented, `2082` commentless, `1216` exact-undefined signatures, and `310` `param_N` signatures.
- Strict comment-plus-clean-signature proxy from the refreshed TSV is `3962/6098 = 64.97%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-160619_post_wave698_cdxtexture_png_decode_option_tail_verified`, `19` files, `165186439` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact PNG decode-state layout, info-state layout, option enum, PLTE/tRNS record layout, gamma/sRGB policy, read callback ABI, buffered-read state layout, source-stream behavior, PNG signature acceptance policy, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`.

Probe anchors: `Wave698 CDXTexture PNG decode-option tail`, `cdxtexture-png-decode-option-tail-wave698`, `0x00594ef8 CDXTexture__SetDecodeOptionFloat`, `0x005950e0 CDXTexture__ComparePngSignatureBytes`, `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`.
