# Ghidra JPEG Scan Controller Head Wave736 Readiness Note

Status: passed
Date: 2026-05-22

Wave736 JPEG scan controller head saved three adjacent CDXTexture JPEG scan-controller rows with the `jpeg-scan-controller-head-wave736` and `wave736-readback-verified` tags. The pass hardened three visible signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine` | `void __stdcall CDXTexture__ProcessJpegScanStateMachine(void * jpeg_codec_state)` | RET `0x4` callback installed by `CDXTexture__InitJpegScanController` at controller `+0x00`. The helper drives controller phases from state `+0x154`, loads scan descriptors, builds MCU layout, invokes color-converter/upsampler/sample-buffer controllers on the non-direct path, then runs DCT/quant, entropy/scan-script, output, source/writer callbacks, progress mirroring, and error id `0x30` for unexpected phases. |
| `0x005b8060 CDXTexture__AbortJpegScanStateMachine` | `void __stdcall CDXTexture__AbortJpegScanStateMachine(void * jpeg_codec_state)` | RET `0x4` abort callback installed by `CDXTexture__InitJpegScanController` at controller `+0x04`. The helper clears controller `+0xc` and invokes writer/source callbacks at state `+0x164 +4` and `+8`. |
| `0x005b8110 CDXTexture__InitJpegScanController` | `void __stdcall CDXTexture__InitJpegScanController(void * jpeg_codec_state, int scan_controller_start_mode)` | RET `0x8` caller `CDXTexture__InitializeJpegEncoderPipeline` pushes a mode flag then `jpeg_codec_state`. The helper allocates a `0x24`-byte controller at state `+0x154`, installs process/abort/local callback slots at `+0x00/+0x04/+0x08`, validates frame MCU layout and optional scan script, derives controller `+0x14` from `scan_controller_start_mode` and state `+0xb8`, clears controller `+0x18/+0x20`, and stores scan count at `+0x1c`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `3` metadata rows, `3` tag rows, `3` xref rows, `783` instruction rows, and `3` decompile rows; read-only caller/xref-site context exports verified `1` caller decompile row and `340` xref-site instruction rows.
- Queue refresh passed with `6098` total functions, `4333` commented, `1765` commentless, `1216` exact-undefined signatures, `45` `param_N` signatures, comment-backed proxy `4333/6098 = 71.06%`, and strict clean-signature proxy `4275/6098 = 70.11%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-120358_post_wave736_jpeg_scan_controller_head_verified`, `19` files, `166923143` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Exact scan-controller struct, scan script semantics, local callback boundary at `0x005b8090`, callback ABI, JPEG mode enums, runtime JPEG output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave736 JPEG scan controller head`, `jpeg-scan-controller-head-wave736`, `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`, `0x005b8060 CDXTexture__AbortJpegScanStateMachine`, `0x005b8110 CDXTexture__InitJpegScanController`, `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-120358_post_wave736_jpeg_scan_controller_head_verified`.
