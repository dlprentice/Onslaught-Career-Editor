# Ghidra Decode Callback Entropy Head Wave726 Readiness Note

Status: passed
Date: 2026-05-22

Wave726 decode callback/entropy head saved six adjacent CTexture/CDXTexture/CFastVB decode callback, coefficient-resource, scanline-output, and entropy-input-window rows with the `decode-callback-entropy-head-wave726` and `wave726-readback-verified` tags.

The pass hardened four visible signatures and left two hidden-register/locked-ABI rows comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005ad550 CTexture__InitDecodeCallbackTables` | `void __stdcall CTexture__InitDecodeCallbackTables(void * decode_context)` | Initializes the texture decode callback table, allocates a `0xe8`-byte callback/controller table through the context allocator at decode_context `+4`, stores it at decode_context `+0x1c0`, seeds callback entries including `LAB_005ad410` and `LAB_005ad000`, clears four callback/data slots, and returns with `RET 0x4`. |
| `0x005ad590 CFastVB__JpegEntropy_CommitAndResetBlockState` | `int CFastVB__JpegEntropy_CommitAndResetBlockState(void)` | Comment/tag-only. Commits and resets JPEG entropy block state using hidden EBX texture/decode context, advances source byte position by the buffered bit count rounded to bytes, clears bit count, calls the source flush callback, zeroes per-component history slots, stores restart state from context `+0x118`, and clears the marker flag when context `+0x1a4` is zero. |
| `0x005ae190 CDXTexture__InitBlockCoefficientHistory` | `void __stdcall CDXTexture__InitBlockCoefficientHistory(void * decode_context)` | Initializes block coefficient history resources, allocates a `0x40`-byte controller at decode_context `+0x1c0`, installs `LAB_005adf50`, clears controller slots, allocates a component-count-scaled coefficient/history buffer at decode_context `+0xa4`, fills active dwords with `0xffffffff`, and returns with `RET 0x4`. |
| `0x005ae600 CDXTexture__InitPerComponentCoefficientBuffers` | `void __stdcall CDXTexture__InitPerComponentCoefficientBuffers(void * decode_context)` | Initializes per-component coefficient buffers, allocates a `0x54`-byte controller at decode_context `+0x1c4`, installs `LAB_005ae1f0`, allocates one `0x100`-byte buffer per component, stores each pointer in the component descriptor at `+0x50`, zeroes `0x40` dwords per component, seeds controller slots to `0xffffffff`, and returns with `RET 0x4`. |
| `0x005ae780 CDXTexture__InitScanlineOutputStage` | `void __stdcall CDXTexture__InitScanlineOutputStage(void * decode_context)` | Initializes the scanline output stage, allocates a `0x1c`-byte stage at decode_context `+0x1b4`, installs `LAB_005ae700`, clears stage slots, optionally stores decode_context `+0x13c`, dispatches through the stage callback when hidden ESI mode is nonzero, or allocates a row buffer sized from decode_context `+0x78` and `+0x70`, then returns with `RET 0x4`. |
| `0x005ae810 CDXTexture__RefillEntropyInputWindow` | `int CDXTexture__RefillEntropyInputWindow(void)` | Comment/tag-only. Refills/copies from the entropy input window using locked stack parameters and hidden EBP progress state, invokes per-component callbacks at row/span boundaries, clamps copy size by context span, window remaining count, and output cursor/end, dispatches the copy/fill callback at decode_context `+0x1cc +4`, advances output/window offsets, and increments hidden progress at span boundaries. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0`; `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0`; `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `6` metadata rows, `6` tag rows, `9` xref rows, `3246` instruction rows, and `6` decompile rows.
- Queue refresh passed: `6098` total, `4274` commented, `1824` commentless, `1216` exact-undefined signatures, `99` `param_N` signatures, comment-backed proxy `4274/6098 = 70.09%`, strict clean-signature proxy `4216/6098 = 69.14%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified`, `19` files, `166595463` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact decode context layout, callback table schema, allocator ownership, component descriptor schema, coefficient/history buffer layout, hidden EBX/ESI/EBP ABI, entropy input-window schema, copy/fill callback contract, runtime JPEG/decode behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave726 decode callback/entropy head`, `decode-callback-entropy-head-wave726`, `0x005ad550 CTexture__InitDecodeCallbackTables`, `0x005ad590 CFastVB__JpegEntropy_CommitAndResetBlockState`, `0x005ae190 CDXTexture__InitBlockCoefficientHistory`, `0x005ae600 CDXTexture__InitPerComponentCoefficientBuffers`, `0x005ae780 CDXTexture__InitScanlineOutputStage`, `0x005ae810 CDXTexture__RefillEntropyInputWindow`, `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified`.
