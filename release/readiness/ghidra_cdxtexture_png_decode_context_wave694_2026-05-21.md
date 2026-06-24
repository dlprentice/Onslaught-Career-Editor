# Ghidra CDXTexture PNG Decode Context Wave694 Readiness

Date: 2026-05-21

Wave694 CDXTexture PNG decode context saved six adjacent PNG decode-context rows with the `cdxtexture-png-decode-context-wave694` and `wave694-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x00592dc2` | `void * __stdcall CDXTexture__CreatePngDecodeContext(void * png_version_string, void * callback_context, void * error_callback, void * warning_callback)` |
| `0x00592eb6` | `void __stdcall CDXTexture__ParsePngHeadersUntilIdat(void * png_decode_state, void * png_image_context)` |
| `0x00593024` | `void __stdcall CDXTexture__PreparePngRowOutputLayout(void * png_decode_state, void * png_image_context)` |
| `0x00593043` | `void __stdcall CDXTexture__DecodePngPassRowsAndPostprocess(void * png_decode_state, void * previous_row_workspace, void * current_row_workspace)` |
| `0x005933c6` | `void __stdcall CDXTexture__DecodePngRowsAcrossPasses(void * png_decode_state, int * row_workspace_pointer_table)` |
| `0x00593411` | `void __stdcall CDXTexture__ResetPngDecodeContext(void * png_decode_state, void * primary_row_workspace, void * secondary_row_workspace)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `630` instruction rows, and `6` clean decompile rows.
- Candidate exports covered `18` adjacent PNG decode rows through `0x005937f6 CDXTexture__GetPngPassCountFromInterlace`.
- Queue refresh PASS: `6098` total, `3979` commented, `2119` commentless, `1216` exact-undefined signatures, and `347` `param_N` signatures.
- Verified backup: `G:\GhidraBackups\BEA_20260521-142452_post_wave694_cdxtexture_png_decode_context_verified`, `19` files, `164989831` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact PNG decode-state layout, callback prototypes, zlib allocator ABI, image-context layout, chunk flag enum, CRC contract, pass-geometry contract, row-workspace ownership, Adam7 table semantics, zlib stream layout, row callback ABI, ownership bits, cleanup ABI, runtime PNG behavior, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`.

Probe anchors: `Wave694 CDXTexture PNG decode context`, `cdxtexture-png-decode-context-wave694`, `0x00592dc2 CDXTexture__CreatePngDecodeContext`, `0x00593411 CDXTexture__ResetPngDecodeContext`, `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`.
