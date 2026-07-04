# Ghidra JPEG Header Parser Tail Wave894 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `jpeg-header-parser-tail-wave894`

Wave894 JPEG header parser tail saved comments/tags for four raw commentless JPEG/image header parser and decode descriptor rows after serialized headless dry/apply/read-back/final dry with the `jpeg-header-parser-tail-wave894` and `wave894-readback-verified` tags. Existing names and signature displays were preserved. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005913b0 CFastVB__JpegParser_ResetFrameState` | Raw no-function callsite xref `0x00592617`; hidden-ESI JPEG parser state reset emits event id `0x66`, conditionally emits `0x3d`, initializes per-component/default lanes, clears frame counters/flags, seeds controller words/flags, writes controller slot `+0x0c` to `1`, and returns `1`. |
| `0x00591720 CFastVB__JpegParser_ParseSOFComponents` | Raw no-function callsite xref `0x0059274a`; hidden EBX/ESI SOF parser validates length/count, stores component count at state `+0x14c`, maps component ids through descriptor table `state+0xdc` with `0x15`-dword stride, splits sampling nibbles, emits ids `0x67/0x68/0x69`, records precision/dimension/sampling, advances the source cursor, and increments state `+0x94`. |
| `0x0059364c CDXTexture__GetImageHeaderInfo` | Called by `CDXTexture__DecodePngFromMemory` at `0x0057ba81`; validates output pointers, copies descriptor width/height/format bytes, derives channel/component count from descriptor byte `+0x19`, checks row-size overflow against `0x7fffffff`, reports warning string/id `0x5eea60`, and returns `1` or `0`. |
| `0x00594f15 CTexture__FinalizeDecodeFormatDescriptor` | Called by `CDXTexture__ParsePngChunk_IHDR` at `0x0059d86d`; writes width/height/bit-depth/format bytes, derives component count at descriptor `+0x1d`, computes bits-per-pixel at descriptor `+0x1e`, checks row-byte overflow against `0x7fffffff`, reports warning string/id `0x5eeaec`, and stores or clears descriptor row-byte state. |

Read-back evidence:

- `ApplyJpegHeaderParserTailWave894.java dry`: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyJpegHeaderParserTailWave894.java apply`: `updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyJpegHeaderParserTailWave894.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 4 xref rows, 422 instruction rows, and 4 decompile rows.
- Queue after Wave894: 6113 total, 6077 commented, 36 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6077/6113 = 99.41%`.
- Next raw commentless row: `0x00598390 CFastVB__DetectCpuFeatureMask`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-062021_post_wave894_jpeg_header_parser_tail_verified`, 19 files, 173149063 bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved comments and tags include `jpeg-header-parser-tail-wave894` and `wave894-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instruction exports, decompile exports, and the refreshed queue.

What remains unproven:

- Exact JPEG parser state layout.
- Exact PNG/JPEG shared descriptor schema.
- Exact color/format/sampling enum names.
- Hidden register ABI completeness.
- Runtime image decode behavior.
- BEA patching behavior.
- Rebuild parity.
