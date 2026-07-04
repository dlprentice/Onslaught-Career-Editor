# Ghidra JPEG Scan Huffman Head Wave725 Readiness Note

Status: passed
Date: 2026-05-22

Wave725 JPEG scan/Huffman head saved eight adjacent CDXTexture JPEG scan, quant-table, color-conversion, Huffman, and entropy-bitstream rows with the `jpeg-scan-huffman-head-wave725` and `wave725-readback-verified` tags.

The pass hardened six visible signatures and left two hidden-register rows comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005aba90 CDXTexture__SelectNextScanTableForProgress` | `void __fastcall CDXTexture__SelectNextScanTableForProgress(void * decode_context)` | Selects/reset the next JPEG scan table progress state through ECX texture/decode context, updates the scan/controller block at context `+0x1b0`, chooses the next scan table count from component descriptor fields under `+0x150/+0x144/+0x98`, and resets scan-progress counters at `+0x14/+0x18`. |
| `0x005ac180 CDXTexture__ValidateAndIndexQuantTables` | `int CDXTexture__ValidateAndIndexQuantTables(void)` | Comment/tag-only. Validates component quantization table availability and copies per-component table indexes into the decode color/scan controller using hidden EBX texture/decode context; allocates the controller table at scan block `+0x70` if needed. |
| `0x005ac930 CDXTexture__SelectColorConvertEntryPoint` | `void __stdcall CDXTexture__SelectColorConvertEntryPoint(void * decode_context)` | Selects the color-conversion entry point, calls the quant-table validator when context `+0x50` is set, installs `LAB_005ac2d0` for the indexed quant-table path or `LAB_005abff0` as fallback, clears context `+0xa0`, and returns with `RET 0x4`. |
| `0x005ac980 CDXTexture__InitColorConversionResources` | `void __stdcall CDXTexture__InitColorConversionResources(void * decode_context)` | Initializes color-conversion resources, allocates a `0x74`-byte controller at context `+0x1b0`, installs setup/select callbacks, and either allocates per-component row resources when hidden EBX mode is nonzero or a shared `0x500`-byte table block. |
| `0x005acac0 CDXTexture__BuildJpegHuffmanDecodeTable` | `void __stdcall CDXTexture__BuildJpegHuffmanDecodeTable(void * decode_context, int table_class, int table_index, void * decode_table_slot)` | Builds a JPEG Huffman decode lookup table from DC/AC table descriptors, validates table index range, allocates a `0x590`-byte table when needed, builds max-code/offset arrays, fills the 8-bit fast lookup and symbol tables, and validates AC run-length symbols. |
| `0x005acd90 CDXTexture__BitstreamReadBitsWithJpegStuffing` | `int __stdcall CDXTexture__BitstreamReadBitsWithJpegStuffing(void * bitstream_state, uint bit_buffer, int bit_count, int min_bits)` | Refills JPEG entropy bitstream state while honoring `0xff` byte-stuffing and marker detection, records nonzero marker bytes at decoder `+0x1a4`, pads after marker/error state when needed, writes back source/bit fields, and returns success/failure. |
| `0x005aceb0 CDXTexture__DecodeHuffmanSymbolFromBitstream` | `uint __stdcall CDXTexture__DecodeHuffmanSymbolFromBitstream(void * bitstream_state, uint bit_buffer, int bit_count, void * huffman_table, int min_bits)` | Decodes one JPEG Huffman symbol, refills through `CDXTexture__BitstreamReadBitsWithJpegStuffing` when needed, grows the code until it is within table max-code entries, returns the symbol from table descriptor offsets, and reports error id `0x76` on invalid code length. |
| `0x005acf90 CDXTexture__FinalizeScanBitstreamState` | `int CDXTexture__FinalizeScanBitstreamState(void)` | Comment/tag-only. Finalizes JPEG scan bitstream state using hidden ESI texture/decode context, advances source byte position by buffered-bit count, clears entropy bit count, calls the scan/source flush callback, zeroes per-component restart/history slots, stores restart state from context `+0x118`, and clears the marker field when context `+0x1a4` is zero. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=2 missing=0 bad=0`; `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=2 missing=0 bad=0`; `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `34` xref rows, `4328` instruction rows, and `8` decompile rows.
- Queue refresh passed: `6098` total, `4268` commented, `1830` commentless, `1216` exact-undefined signatures, `103` `param_N` signatures, comment-backed proxy `4268/6098 = 69.99%`, strict clean-signature proxy `4210/6098 = 69.04%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005ad550 CTexture__InitDecodeCallbackTables`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified`, `19` files, `166595463` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact JPEG/decode context layout, scan table schema, component descriptor schema, quant table descriptor schema, hidden EBX/ESI ABI, callback table contract, color conversion policy, DHT descriptor schema, Huffman decode-table layout, entropy state layout, source/error callback ABI, marker/restart policy, runtime JPEG decode behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave725 JPEG scan/Huffman head`, `jpeg-scan-huffman-head-wave725`, `0x005aba90 CDXTexture__SelectNextScanTableForProgress`, `0x005ac180 CDXTexture__ValidateAndIndexQuantTables`, `0x005ac930 CDXTexture__SelectColorConvertEntryPoint`, `0x005ac980 CDXTexture__InitColorConversionResources`, `0x005acac0 CDXTexture__BuildJpegHuffmanDecodeTable`, `0x005acd90 CDXTexture__BitstreamReadBitsWithJpegStuffing`, `0x005aceb0 CDXTexture__DecodeHuffmanSymbolFromBitstream`, `0x005acf90 CDXTexture__FinalizeScanBitstreamState`, `0x005ad550 CTexture__InitDecodeCallbackTables`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified`.
