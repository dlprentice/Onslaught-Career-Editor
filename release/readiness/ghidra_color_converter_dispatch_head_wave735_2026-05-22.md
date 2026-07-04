# Ghidra Color Converter Dispatch Head Wave735 Readiness Note

Status: passed
Date: 2026-05-22

Wave735 color converter dispatch head saved three adjacent CDXTexture JPEG color-converter rows with the `color-converter-dispatch-head-wave735` and `wave735-readback-verified` tags. The pass hardened three visible signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale` | `void __stdcall CDXTexture__ConvertRgbRowsToGrayscale(void * jpeg_codec_state, void * source_row_table, void * output_row_table, int output_start_row, int row_count)` | RET `0x14` callback installed by `CDXTexture__InitColorConverterDispatch` for RGB-family input to one-channel output. The helper reads pixel width from state `+0x1c`, uses the lookup-table pointer at state `+0x168/+8`, combines RGB byte channels through `0x0/0x400/0x800` table bands, and writes one grayscale/luma byte per pixel. |
| `0x005b7480 CDXTexture__CopyInterleavedChannelRows` | `void __stdcall CDXTexture__CopyInterleavedChannelRows(void * jpeg_codec_state, void * source_row_table, void * output_row_table, int output_start_row, int row_count)` | RET `0x14` callback installed for direct-compatible one/three-channel paths. The helper reads pixel width from state `+0x1c`, source channel stride from state `+0x24`, dereferences source and destination row tables, advances by stride per pixel, and writes one channel byte per pixel. |
| `0x005b7580 CDXTexture__InitColorConverterDispatch` | `void __stdcall CDXTexture__InitColorConverterDispatch(void * jpeg_codec_state)` | RET `0x4` caller `CDXTexture__InitializeJpegEncoderPipeline` reaches this helper when state `+0xb0` is zero. It allocates a `0xc`-byte controller at state `+0x168`, installs entry `0x005b0ed0`, validates source fields `+0x28/+0x24` and output fields `+0x40/+0x3c`, reports error ids `9`, `10`, or `0x1b`, and installs callback slot `+4` with `CDXTexture__CopyInterleavedChannelRows`, `CDXTexture__ConvertRgbRowsToGrayscale`, or local labels `0x005b6e70`, `0x005b6f50`, `0x005b7080`, `0x005b7250`, `0x005b7300`, and `0x005b74e0`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `435` instruction rows, and `3` decompile rows; read-only caller/xref-site context exports verified `2` caller decompile rows and `855` xref-site instruction rows.
- Queue refresh passed with `6098` total functions, `4330` commented, `1768` commentless, `1216` exact-undefined signatures, `48` `param_N` signatures, comment-backed proxy `4330/6098 = 71.01%`, and strict clean-signature proxy `4272/6098 = 70.06%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-113700_post_wave735_color_converter_dispatch_head_verified`, `19` files, `166890375` bytes, `DiffCount=0`.

Process note: the first direct pre-metadata export omitted `-noanalysis`, so Ghidra performed a full analysis save before the export was rerun with `-noanalysis`. Read-only comparison against the Wave734 backup showed only the internal database segment name advanced, and a `-noanalysis` quality snapshot immediately after that export still reported `6098` total, `4327` commented, `1771` commentless, `1216` exact-undefined, `51` `param_N`, strict `4269`, and high-signal head `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale`. The Wave735 mutation/read-back gates then proceeded normally.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact color-mode enum, lookup-table schema, channel order, row-table ownership, destination component semantics, controller schema, local helper boundaries, callback ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave735 color converter dispatch head`, `color-converter-dispatch-head-wave735`, `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale`, `0x005b7480 CDXTexture__CopyInterleavedChannelRows`, `0x005b7580 CDXTexture__InitColorConverterDispatch`, `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-113700_post_wave735_color_converter_dispatch_head_verified`.
