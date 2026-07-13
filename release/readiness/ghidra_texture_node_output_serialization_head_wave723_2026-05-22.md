# Ghidra Texture Node Output Serialization Head Wave723 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x005ab14b` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: passed
Date: 2026-05-22

Wave723 texture node output serialization head saved two adjacent texture node output serialization rows, `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits` and `0x005ab14b CTexture__SerializeNodeTreeToBitstream`, with the `texture-node-output-serialization-head-wave723` and `wave723-readback-verified` tags.

The pass hardened two visible signatures/parameter names:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005ab0ed` | `int __stdcall CDXTexture__EvalNodeOutputSizeUnits(void * node_tree)` | Recursive texture/node-tree output-unit count; null input returns zero, kind `1` sums the `+0xc` and `+0x8` child branches, kind `5` follows `+0x18`, kind `7` multiplies the recursive `+0x10` count by `+0x14`, kind `8` multiplies `+0x1c` by `+0x18`, kind `10` follows `+0x20`, and `RET 0x4` restores one stack argument. |
| `0x005ab14b` | `int __stdcall CTexture__SerializeNodeTreeToBitstream(void * chunk_builder, void * node_tree, uint output_unit_scale, uint * out_chunk_offset)` | Four-argument recursive serializer; null `out_chunk_offset` returns zero, unsupported node kinds return `0x80004005`, kind `7` scales while following `+0x10`, kind `8` registers typed payload data through `CDXTexture__RegisterSerializedChunk`, and kind `1` registers child records plus a final `0x10`-byte header. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`; `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`; `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `2` metadata rows, `2` tag rows, `6` xref rows, `666` instruction rows, and `2` decompile rows.
- Queue refresh passed: `6098` total, `4255` commented, `1843` commentless, `1216` exact-undefined signatures, `111` `param_N` signatures, comment-backed proxy `4255/6098 = 69.78%`, strict clean-signature proxy `4197/6098 = 68.82%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified`, `19` files, `166529927` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact chunk-builder layout, node field schema, type/kind enum, output-unit semantics, registry flag contract, runtime texture behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave723 texture node output serialization head`, `texture-node-output-serialization-head-wave723`, `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`, `0x005ab14b CTexture__SerializeNodeTreeToBitstream`, `0x0042f220 CSPtrSet__Clear`, `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified`.
