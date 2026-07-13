# Ghidra CTexture JPEG Compression Defaults Wave700 Readiness

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00595350` → `CTexture__FinishJpegCompress` (was `CTexture__FinishJpegCompressPass`); `0x00595430` comment correction; `0x005954a0` → `CTexture__WriteJpegScanlines` (was `CTexture__ReadJpegCompressInputBytes`); `0x00595930` → `CTexture__SetJpegCompressColorSpace` (was `CTexture__JpegScanScript_SetPreset`); `0x00595c10` → `CTexture__SetDefaultJpegCompressColorSpace` (was `CTexture__ConfigureJpegScanPresetByCompressionMode`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-21

Wave700 CTexture JPEG compression defaults saved nine adjacent IJG-style JPEG compression-default, input/pass, quant-table, Huffman-table, and scan-script rows with the `ctexture-jpeg-compression-defaults-wave700` and `wave700-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x00595350` | `void __stdcall CTexture__ProcessDecodeStateMachineStep(void * jpeg_compress_context)` |
| `0x00595430` | `void __stdcall CTexture__ResetDecodePipelineForNextChunk(void * jpeg_compress_context, int reset_sent_table_flags)` |
| `0x005954a0` | `void __stdcall CTexture__ReadDecodeInputBytes(void * jpeg_compress_context, void * destination_buffer, uint requested_byte_count)` |
| `0x00595550` | `void __stdcall CTexture__LoadAndScaleQuantizationTable(void * jpeg_compress_context, int table_index, void * source_quant_table, int quality_scale_percent, int force_baseline_range)` |
| `0x00595820` | `void __stdcall CTexture__LoadHuffmanTableDefinition(void * jpeg_compress_context, void * huff_values_table)` |
| `0x005958e0` | `void CTexture__LoadDefaultHuffmanTables(void)`; comment/tag-only because Ghidra reports unknown calling convention with locked storage and hidden ESI context |
| `0x00595930` | `void __stdcall CTexture__DeflateConfig_SetPreset(void * jpeg_compress_context, int scan_script_preset)` |
| `0x00595c10` | `void __stdcall CTexture__ConfigureDeflatePresetByCompressionMode(void * jpeg_compress_context)` |
| `0x00595da0` | `void __stdcall CTexture__InitializeJpegCompressionDefaults(void * jpeg_compress_context)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=1 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=1 missing=0 bad=0`, then `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `9` metadata rows, `9` tag rows, `15` xref rows, `333` instruction rows, and `9` clean decompile rows.
- Queue refresh PASS: `6098` total, `4033` commented, `2065` commentless, `1216` exact-undefined signatures, and `293` `param_N` signatures.
- Strict comment-plus-clean-signature proxy from the refreshed TSV is `3979/6098 = 65.25%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-165600_post_wave700_ctexture_jpeg_compression_defaults_verified`, `19` files, `165219207` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact JPEG context layout, controller vtable ABI, source-manager ABI, quant-table descriptor layout, Huffman descriptor layout, hidden-register Huffman helper ABI, scan-script row layout, color-space enum, default table provenance, naming provenance for the existing `Deflate` labels, runtime JPEG encoder behavior, runtime entropy-table behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven. The current decompile evidence for the two existing `Deflate`-named helpers shows JPEG scan-script/component selector setup, not zlib deflate proof.

Next queue head: `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`.

Probe anchors: `Wave700 CTexture JPEG compression defaults`, `ctexture-jpeg-compression-defaults-wave700`, `0x00595350 CTexture__ProcessDecodeStateMachineStep`, `0x00595da0 CTexture__InitializeJpegCompressionDefaults`, `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`.
