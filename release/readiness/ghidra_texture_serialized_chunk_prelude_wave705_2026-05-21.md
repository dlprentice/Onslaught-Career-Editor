# Ghidra Texture Serialized-Chunk Prelude Wave705 Readiness

Status: validated
Date: 2026-05-21
Scope: saved Ghidra metadata only; no executable bytes, function boundaries, original game files, copied profiles, runtime proof, or public asset payloads changed.

## What Changed

Wave705 texture serialized-chunk prelude saved signatures, parameter names, comments, and tags for seven adjacent CTexture/CDXTexture/CFastVB serialized-chunk, debug-chunk, node span/stride, constant-register, float-grid, and texture-binding helpers.

Probe anchors: `0x0059902a CDXTexture__RegisterSerializedChunk`, `0x005994c4 CDXTexture__ProcessTextureChunkAndEmitBindings`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005997a5 CFastVB__InitNodeType17`.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059902a` | `int CDXTexture__RegisterSerializedChunk(void)` | Hidden-ECX chunk registry helper validates pointer/length input, handles `0xffffffff` string-length sentinel, deduplicates existing chunk records, appends a 0x14-byte record, and writes an optional output offset; comment/tag-only because Ghidra reports locked storage. |
| `0x00599161` | `int __fastcall CTexture__ComputeDebugChunkDwordCount(void * chunk_builder)` | Computes debug chunk dword count as aligned byte count plus the two-dword header. |
| `0x0059916d` | `int __thiscall CTexture__SerializeDebugChunkSymbolRecords(void * this, uint * out_chunk_dwords, uint max_dword_count)` | Writes the `0xfffe` debug-chunk header, copies record bytes from the builder list, and fills alignment/trailing padding with `0xab`/`0xabababab`; `RET 0x8` removes an unused phantom parameter. |
| `0x00599258` | `int __stdcall CFastVB__ComputeNodeSpanAndStride(void * node_tree, uint * out_span, uint * out_stride)` | Recursively computes span and stride for observed node kinds `8`, `7`, and `1`, using a local stride fallback when the output stride pointer is null. |
| `0x0059930d` | `int __thiscall CTexture__ValidateConstantRegisterDeclarationType(void * this, void * match_template_words32, void * register_decl, uint * out_component_count)` | Copies an eight-dword match template, selects a node-tree match, computes span/stride, and emits diagnostics `0xb54`/`0xb55` when bool/int constant-register declarations do not match the expected node shape; `RET 0xc` removes an unused phantom parameter. |
| `0x00599406` | `int __stdcall CDXTexture__SerializeFloatGridChunk(void * chunk_builder, uint row_count, uint column_count, void * value_source, uint * out_chunk_offset)` | Serializes a temporary row grid of float values, narrows double payloads where needed, registers chunk kind `6`, frees the temp buffer, and restores the fifth stack argument from `RET 0x14`. |
| `0x005994c4` | `int CDXTexture__ProcessTextureChunkAndEmitBindings(void)` | Locked-storage texture binding emitter classifies float/bool/int token globals, selects a node tree, binds register suffixes up to `8191`, optionally serializes a float grid and node-tree bitstream, registers the final binding chunk, and writes output header fields; comment/tag-only because Ghidra reports locked storage. |

Tag anchor: `texture-serialized-chunk-prelude-wave705`; read-back tag: `wave705-readback-verified`.

## Evidence

- Pre-export found all `7` targets: `7` metadata rows, `7` tag rows, `29` xref rows, `847` instruction rows, and `7` decompile rows.
- `ApplyTextureSerializedChunkPreludeWave705.java` accepted dry run: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=2 missing=0 bad=0`.
- Apply run: `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=2 missing=0 bad=0`.
- Final dry run: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- A superseded first dry log failed to compile before target execution because of a local script API typo; it made no target changes and was replaced by the accepted dry/apply/final-dry sequence above.
- Post-export verified all `7` saved signatures/tags/comments with `29` xref rows, `847` instruction rows, and `7` clean decompile rows.
- Queue refresh after Wave705: `6098` total functions, `4095` commented, `2003` commentless, `1216` exact-undefined signatures, `238` `param_N` signatures, comment-backed proxy `4095/6098 = 67.15%`, strict clean-signature proxy `4041/6098 = 66.27%`.
- Earliest raw commentless row: `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row: `0x005997a5 CFastVB__InitNodeType17`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-194929_post_wave705_texture_serialized_chunk_prelude_verified`, `19` files, `165448583` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static retail Ghidra metadata only. Exact chunk-builder layout, chunk/flag enums, record and binding schemas, node/declaration layouts, selected-node ABI, token enum, parser/source identity, runtime shader/texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

The installed Steam game and original `BEA.exe` were not modified.
