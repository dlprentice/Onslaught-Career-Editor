# Ghidra Decode Dispatch Head Wave710 Readiness

Status: passed
Date: 2026-05-21

Wave710 decode dispatch head saved eight adjacent CTexture/CDXTexture decode-dispatch and callback-context rows with the `decode-dispatch-head-wave710` and `wave710-readback-verified` tags. The pass changed Ghidra metadata only: comments, tags, and signatures. It made no renames, no function-boundary changes, and no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0059aec0 CTexture__CanUseCompactDecodePath` | `int __fastcall CTexture__CanUseCompactDecodePath(int unused_ecx, void * decode_state)` | Plain `RET`, EDX-loaded decode state, and compact-path branch evidence. |
| `0x0059af40 CTexture__ComputeDecodeBlockGeometry` | `void __stdcall CTexture__ComputeDecodeBlockGeometry(void * decode_state)` | `RET 0x4`, block dimension writes, and call into `CTexture__CanUseCompactDecodePath`. |
| `0x0059b370 CTexture__RunDecodeDispatchStage` | `void __stdcall CTexture__RunDecodeDispatchStage(void * decode_state)` | `RET 0x4`, dispatch context at `+0x1a8`, and callback-context progress writes. |
| `0x0059b4d0 CTexture__CreateDecodeDispatchContext` | `void __stdcall CTexture__CreateDecodeDispatchContext(void * decode_state)` | `RET 0x4`, 0x1c-byte dispatch-context allocation, and hidden-register initializer calls. |
| `0x0059b920 CDXTexture__DecodeState_RunPostFrameCallbacks` | `void __stdcall CDXTexture__DecodeState_RunPostFrameCallbacks(void * decode_state)` | `RET 0x4`, post-frame callback dispatch, and helper calls with hidden-register ABI gaps deferred. |
| `0x0059b960 CDXTexture__DecodeState_AdvanceFrame` | `int __stdcall CDXTexture__DecodeState_AdvanceFrame(void * decode_state)` | `RET 0x4`, status return, frame-step state update, and terminal-flag checks. |
| `0x0059ba20 CDXTexture__DecodeState_ResetCallbackContext` | `void __stdcall CDXTexture__DecodeState_ResetCallbackContext(void * decode_state)` | `RET 0x4`, callback-context reset, and clear of the observed `+0xa4` field. |
| `0x0059ba90 CDXTexture__DecodeState_CreateCallbackContext` | `void __stdcall CDXTexture__DecodeState_CreateCallbackContext(void * decode_state)` | `RET 0x4`, 0x1c-byte callback-context allocation, and state words initialized to 0/0/1. |

Evidence:

- Candidate exports before mutation covered 13 metadata rows, 13 tag rows, 17 xref rows, 3133 instruction rows, and 13 decompile rows.
- deferred read-only hidden-ABI candidates: `0x0059b150 CTexture__InitDecodeLookupScratchTables` (`in_EAX`), `0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader` (`unaff_ESI`), `0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout` (`unaff_ESI`), `0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables` (`unaff_ESI`), and `0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks` (`unaff_EBX`).
- Selected pre exports covered 8 metadata rows, 8 tag rows, 12 xref rows, 1928 instruction rows, and 8 decompile rows.
- Dry/apply/final dry summaries: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`; `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`; `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post exports covered 8 metadata rows, 8 tag rows, 12 xref rows, 1928 instruction rows, and 8 clean decompile rows.
- Queue after Wave710: 6098 total, 4125 commented, 1973 commentless, 1216 exact-undefined signatures, 210 `param_N`, comment-backed proxy `4125/6098 = 67.64%`, and strict clean-signature proxy `4071/6098 = 66.76%`.
- Queue heads after Wave710: raw commentless head `0x0042f220 CSPtrSet__Clear`; high-signal head `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-221723_post_wave710_decode_dispatch_head_verified`, 19 files, 165514119 bytes, `DiffCount=0`.

Boundary:

This is static Ghidra metadata/read-back evidence only. Exact decode-state layout, dispatch/callback-context layout, callback ABI, helper hidden-register ABIs, JPEG frame semantics, runtime image decode behavior, runtime image fidelity, BEA patching, source identity, and rebuild parity remain unproven.

Probe anchors: `Wave710 decode dispatch head`, `decode-dispatch-head-wave710`, `0x0059aec0 CTexture__CanUseCompactDecodePath`, `0x0059ba90 CDXTexture__DecodeState_CreateCallbackContext`, `0x0059b150 CTexture__InitDecodeLookupScratchTables`, `0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks`, `0x0042f220 CSPtrSet__Clear`, `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`.
