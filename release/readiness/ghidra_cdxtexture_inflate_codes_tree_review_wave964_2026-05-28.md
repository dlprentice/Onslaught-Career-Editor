# Ghidra CDXTexture Inflate Codes Tree Review Wave964

Status: bounded static mutation/read-back PASS
Date: 2026-05-28
Tag: `cdxtexture-inflate-codes-tree-review-wave964`

Wave964 re-reviewed the CDXTexture zlib/inflate stream, block-header, code-state, Huffman-tree, output-window, and fast-decode helper chain after the Wave731, Wave738, and Wave899 CDXTexture inflate hardening. The wave found one stale caveat: `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` still described a prior `extraout_EAX` gap, but fresh decompile now assigns the `CDXTexture__InflateProcessBlockHeader` return directly into the local status variable. The pass refreshed only that function comment/tags. It made no rename, no signature change, no function-boundary change, no executable-byte change, and did not launch BEA.

## Scope

Primary corrected row:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x0059c8c1` | `CDXTexture__InflateStream_ProcessZlibState` | Comment/tag normalization PASS; stale `extraout_EAX` caveat resolved by fresh decompile and body-instruction evidence at `0x0059c9ce CALL 0x005b1e94`. |

Context anchors re-read: `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`, `0x005b1e94 CDXTexture__InflateProcessBlockHeader`, `0x005bcfa0 CDXTexture__InflateCodesState_Create`, `0x005bcfd3 CDXTexture__InflateCodesState_Process`, `0x005bd52a CDXTexture__InvokeReleaseCallback`, `0x005bd53b CDXTexture__BuildInflateHuffmanTable`, `0x005bd8ba CDXTexture__InflateDynamicTree_BuildBitLengthTree`, `0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees`, `0x005bda2d CDXTexture__InflateFixedTrees_InitDescriptors`, `0x005bda5e CDXTexture__InflateOutputWindowFlush`, and `0x005be360 CDXTexture__InflateFast_DecodeBlockStream`.

## Evidence

Fresh serialized Ghidra exports under `subagents/ghidra-static-reaudit/wave964-cdxtexture-inflate-codes-tree-review`:

- Pre/post exports both verified `12` metadata rows, `12` tag rows, `23` xref rows, `1740` around-address instruction rows, `2271` function-body instruction rows, and `12` decompile-index rows.
- `ApplyCDXTextureInflateCodesTreeWave964.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`.
- `ApplyCDXTextureInflateCodesTreeWave964.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyCDXTextureInflateCodesTreeWave964.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post-readback tags for `0x0059c8c1` include `cdxtexture-inflate-codes-tree-review-wave964`, `wave964-readback-verified`, and `extraout-eax-gap-resolved`; stale tag `extraout-eax-gap` is absent.
- Decompile readback for `0x0059c8c1` contains the actual call assignment `iVar4 = CDXTexture__InflateProcessBlockHeader(...)` rather than an `extraout_`-based caller status gap.
- Xrefs and body instructions tie the chain through `0x0059c9ce CALL 0x005b1e94`, `0x005b2455 CALL 0x005bcfd3`, `0x005b245a CMP EAX, 0x1`, `0x005bd067 CALL 0x005be360`, `0x005bd8f6 CALL 0x005bd53b`, `0x005bd982 CALL 0x005bd53b`, `0x005bd9b9 CALL 0x005bd53b`, `0x005b23f3 CALL 0x005bd933`, and output-window flush calls `0x005b1f00`, `0x005b20a6`, and `0x005b2574` to `0x005bda5e`.

Verified Ghidra backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260528-141856_post_wave964_cdxtexture_inflate_codes_tree_review_verified
```

Backup summary: `19` files, `173542279` bytes, `DiffCount=0`.

Wave911 focused re-audit progress after Wave964: `323/1408 = 22.94%`.
Static export-contract function-quality closure remains `6152/6152 = 100.00%`.

Probe anchor: Wave964; cdxtexture-inflate-codes-tree-review-wave964; 0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState; 0x0059c9ce CALL 0x005b1e94; 0x005b1e94 CDXTexture__InflateProcessBlockHeader; 0x005bcfd3 CDXTexture__InflateCodesState_Process; 0x005bd53b CDXTexture__BuildInflateHuffmanTable; 0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees; 0x005be360 CDXTexture__InflateFast_DecodeBlockStream; extraout-eax-gap-resolved; 323/1408 = 22.94%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-141856_post_wave964_cdxtexture_inflate_codes_tree_review_verified; comment/tag mutation only.

## Boundary

This wave proves only saved static retail Ghidra evidence tying the CDXTexture inflate stream and tree/code helpers into a coherent zlib-style decompression chain. Exact `z_stream` layout, inflate-state layout, table-entry schemas, callback ABI, exact zlib/source identity, runtime inflate/decode behavior, BEA patching, and rebuild parity remain separate proof.
