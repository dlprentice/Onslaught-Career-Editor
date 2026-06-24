# Ghidra CDXTexture JPEG Decode Tail Wave899 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `cdxtexture-jpeg-decode-tail-wave899`

Wave899 CDXTexture JPEG decode tail saved comments/tags for six raw commentless CDXTexture JPEG scan/layout, YCbCr conversion, and inflate Huffman-table rows from `0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout` through `0x005bd53b CDXTexture__BuildInflateHuffmanTable`. The pass preserved existing names and signature displays, made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout` | Called by `CDXTexture__InitJpegScanController` at `0x005b8142`; validates JPEG frame dimensions/precision/component count/sampling factors and fills component MCU geometry. |
| `0x005b7920 CDXTexture__ValidateJpegScanScript` | Called by `CDXTexture__InitJpegScanController` at `0x005b814f`; validates scan count, component references, spectral ranges, successive approximation ranges, and progressive coverage tables. |
| `0x005b7c50 CDXTexture__LoadCurrentJpegScanDescriptor` | Called by `CDXTexture__ProcessJpegScanStateMachine` at `0x005b7f0f`, `0x005b7f4f`, and `0x005b7fb5`; selects default/all-component scan descriptors or active scan-script entries. |
| `0x005b7d30 CDXTexture__BuildCurrentScanMcuLayout` | Called by `CDXTexture__ProcessJpegScanStateMachine` at `0x005b7f14`, `0x005b7f54`, and `0x005b7fba`; computes scan MCU dimensions and selected-component block table rows. |
| `0x005bce60 CDXTexture__ConvertYCbCrToRgb24_Mmx` | Reached from raw callsite `0x005afb05`; uses packed MMX-style arithmetic and constants near `0x005f5000` to convert Y/Cb/Cr planes into RGB24 output. |
| `0x005bd53b CDXTexture__BuildInflateHuffmanTable` | Called by `CDXTexture__InflateDynamicTree_BuildBitLengthTree` and `CDXTexture__InflateDynamicTree_BuildLitDistTrees` at `0x005bd8f6`, `0x005bd982`, and `0x005bd9b9`; builds zlib-style Huffman decode tables with observed status returns `0`, `-3`, and `-5`. |

Read-back evidence:

- `ApplyCDXTextureJpegDecodeTailWave899.java dry`: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCDXTextureJpegDecodeTailWave899.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCDXTextureJpegDecodeTailWave899.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 6 metadata rows, 6 tag rows, 12 xref rows, 1046 instruction rows, and 6 decompile rows.
- Queue after Wave899: 6113 total, 6106 commented, 7 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `6106/6113 = 99.89%`, strict clean-signature proxy `6106/6113 = 99.89%`.
- Next raw commentless row: `0x005d04e6 RtlUnwind`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260526-083306_post_wave899_cdxtexture_jpeg_decode_tail_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The six target function rows exist in the saved Ghidra project.
- The saved names/signature displays match the pre-state names/signatures.
- The saved comments and tags include `cdxtexture-jpeg-decode-tail-wave899` and `wave899-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to post-export metadata, tags, xrefs, instructions, decompiles, queue telemetry, and backup verification.

What remains unproven:

- Exact JPEG state/component/scan descriptor layouts.
- Exact MMX color coefficient identity and lane packing.
- Exact zlib/source identity and Huffman table-entry schema.
- Runtime JPEG/image decode behavior.
- Runtime decompression behavior.
- BEA patching behavior.
- Rebuild parity.
