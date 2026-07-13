# Ghidra Decode Feature Tail Wave895 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0059be00` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `decode-feature-tail-wave895`

Wave895 decode feature tail saved comments/tags for nine raw commentless CFastVB/CTexture/CDXTexture rows after serialized headless dry/apply/read-back/final dry with the `decode-feature-tail-wave895` and `wave895-readback-verified` tags. Existing names and signature displays were preserved. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00598390 CFastVB__DetectCpuFeatureMask` | Called by `CFastVB__InitDispatchOpsFromFeatureFlags` at `0x00598474`; CPUID feature-mask helper using `AuthenticAMD`/`UnknownVendr` context and observed feature bits `0x20/0x40/0x80/0x100/0x200`. |
| `0x0059a71a CFastVB__SelectBestNodeTreeMatch` | Called by `CTexture__ValidateConstantRegisterDeclarationType` and `CDXTexture__ProcessTextureChunkAndEmitBindings`; hidden ECX/stack ABI selector scans candidate node-tree lists, scores compatibility, handles diagnostics `0xbbd/0xbfb/0xbbc/0xc06`, and returns observed selector/error values. |
| `0x0059b150 CTexture__InitDecodeLookupScratchTables` | Called by `CTexture__InitializeDecodePipelineFromHeader`; hidden EAX decode-state helper allocates scratch storage, initializes identity/negative/zero tables, and mirrors lookup rows. |
| `0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader` | Called by `CTexture__CreateDecodeDispatchContext`; hidden ESI decode-pipeline initializer sets block geometry, callback events, scanline/color/entropy/output/coefficient/history/conversion resources, and output descriptor state. |
| `0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout` | Called by `CDXTexture__DecodeState_AdvanceFrame`; validates JPEG dimensions/precision/component count/sampling and builds per-component scan layout fields. |
| `0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables` | Called by `CDXTexture__DecodeState_RunPostFrameCallbacks`; builds MCU grid, per-component block layout, and component index table. |
| `0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks` | Called by `CDXTexture__DecodeState_RunPostFrameCallbacks`; validates component template selectors, allocates scratch blocks, copies `0x21` dwords, and stores component `+0x4c`. |
| `0x0059be00 CDXTexture__CreateDecodeJobDescriptor` | DATA callback from `CDXTexture__InitDecodeAllocatorVtable` at `0x0059c563`; allocates and links a `0x248`-byte decode job descriptor into owner list `+0x44`. |
| `0x0059be70 CDXTexture__AllocDecodeBlockAndLink` | DATA callback from `CDXTexture__InitDecodeAllocatorVtable` at `0x0059c56a`; mirrors the descriptor allocation pattern and links into owner list `+0x48`. |

Read-back evidence:

- `ApplyDecodeFeatureTailWave895.java dry`: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyDecodeFeatureTailWave895.java apply`: `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyDecodeFeatureTailWave895.java final dry`: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 9 metadata rows, 9 tag rows, 10 xref rows, 1329 instruction rows, and 9 decompile rows.
- Queue after Wave895: 6113 total, 6086 commented, 27 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6086/6113 = 99.56%`.
- Next raw commentless row: `0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-064920_post_wave895_decode_feature_tail_verified`, 19 files, 173214599 bytes, `DiffCount=0`.

What this proves:

- The nine target function rows exist in the saved Ghidra project.
- The saved comments and tags include `decode-feature-tail-wave895` and `wave895-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to metadata, tags, xrefs, instruction exports, decompile exports, the refreshed queue, and the verified backup.

What remains unproven:

- Exact feature-bit names and SIMD dispatch semantics.
- Exact node-tree layout and compatibility-score semantics.
- Exact decode-state, component-plane, descriptor, and allocator-state layouts.
- Hidden register/stack ABI completeness.
- Runtime parser, texture, JPEG/image decode, and CPU-dispatch behavior.
- BEA patching behavior.
- Rebuild parity.
