# Ghidra YCC Chroma Conversion Head Wave727 Readiness Note

Status: passed
Date: 2026-05-22

Wave727 YCC chroma conversion head saved six adjacent CDXTexture chroma upsample, YCC-to-RGB conversion, and adaptive dispatch rows with the `ycc-chroma-conversion-head-wave727` and `wave727-readback-verified` tags.

The pass hardened six visible signatures/parameter names:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal` | `void __fastcall CDXTexture__UpsampleChromaLinearHorizontal(void * decode_context, void * component_descriptor, void * source_row_table)` | Uses hidden EAX as the output row-pointer table, reads active row count from decode_context `+0x13c`, reads component width/sample count from component_descriptor `+0x28`, and writes first/interior/final horizontal interpolation samples with 3:1 weighted byte blends. |
| `0x005aebb0 CDXTexture__UpsampleAndConvertYccToRgb_Mmx` | `void __thiscall CDXTexture__UpsampleAndConvertYccToRgb_Mmx(void * this, void * decode_context, void * source_row_table, int hidden_edi_tail)` | MMX-shaped helper selected by the adaptive path. The this object supplies component width/sample count at `+0x28`, decode_context `+0x13c` supplies row count, hidden EAX supplies output rows, source_row_table is consumed relative to those rows, and the caller forwards an EDI tail. |
| `0x005aee40 CDXTexture__UpsampleAndConvertYccToRgb_Scalar` | `void __stdcall CDXTexture__UpsampleAndConvertYccToRgb_Scalar(void * decode_context, void * component_descriptor, void * source_row_table)` | Scalar fallback over two-line source-row neighborhoods, using hidden EAX output rows plus component width and decode row count to emit interpolated byte pairs. |
| `0x005aefa0 CDXTexture__ConvertYccBlocksToRgb_Sse` | `void __fastcall CDXTexture__ConvertYccBlocksToRgb_Sse(void * color_context, void * component_descriptor, void * decode_context, void * source_row_table)` | SSE-shaped helper selected by the auto dispatcher. It uses a forwarded color_context, component_descriptor width, decode_context row count, hidden EAX output rows, and current/previous/next source rows with packed conversion constants around `DAT_005f4a20`. |
| `0x005af570 CDXTexture__UpsampleAndConvertScanlineAdaptive` | `void __stdcall CDXTexture__UpsampleAndConvertScanlineAdaptive(void * decode_context, void * component_descriptor, void * source_row_table)` | Checks component width, scans source row flags against decode row count, signals the decode context callback when low flag bits are set, dispatches to the MMX-shaped helper for decode_context `+0x48` values `5` or `6` when every row is clean, otherwise falls back to horizontal chroma upsample. |
| `0x005af5f0 CDXTexture__ConvertYccBlocksToRgb_Auto` | `void __thiscall CDXTexture__ConvertYccBlocksToRgb_Auto(void * this, void * decode_context, void * component_descriptor, void * source_row_table, void * dispatch_tail)` | Checks component width, scans source row flags against decode row count, signals the decode context callback when low flag bits are set, dispatches to the SSE-shaped helper for decode_context `+0x48` values `5` or `6` when every row is clean, otherwise falls back to the scalar helper. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`; `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`; `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `6` metadata rows, `6` tag rows, `6` xref rows, `3246` instruction rows, and `6` decompile rows.
- Queue refresh passed: `6098` total, `4280` commented, `1818` commentless, `1216` exact-undefined signatures, `93` `param_N` signatures, comment-backed proxy `4280/6098 = 70.19%`, strict clean-signature proxy `4222/6098 = 69.24%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005af670 CDXTexture__InitEntropyDecodeResources`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-072249_post_wave727_ycc_chroma_conversion_head_verified`, `19` files, `166628231` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX/EDI/ECX ABI, YCC/RGB coefficient identity, dispatch policy, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave727 YCC chroma conversion head`, `ycc-chroma-conversion-head-wave727`, `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`, `0x005aebb0 CDXTexture__UpsampleAndConvertYccToRgb_Mmx`, `0x005aee40 CDXTexture__UpsampleAndConvertYccToRgb_Scalar`, `0x005aefa0 CDXTexture__ConvertYccBlocksToRgb_Sse`, `0x005af570 CDXTexture__UpsampleAndConvertScanlineAdaptive`, `0x005af5f0 CDXTexture__ConvertYccBlocksToRgb_Auto`, `0x005af670 CDXTexture__InitEntropyDecodeResources`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-072249_post_wave727_ycc_chroma_conversion_head_verified`.
