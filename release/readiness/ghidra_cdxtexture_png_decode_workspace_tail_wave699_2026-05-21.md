# Ghidra CDXTexture PNG Decode-Workspace Tail Wave699 Readiness

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00595220` → `CTexture__InitializeJpegCompressContext` (was `CTexture__InitJpegCompressContextWithDefaults`); `0x00595350` → `CTexture__FinishJpegCompress` (was `CTexture__FinishJpegCompressPass`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-21

Wave699 CDXTexture PNG decode-workspace tail saved eight adjacent PNG workspace, CRC, allocation, and IJG-style JPEG context/table helper rows with the `cdxtexture-png-decode-workspace-tail-wave699` and `wave699-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x0059512b` | `void * __stdcall CDXTexture__AllocZeroedDecodeBuffer(void * allocator_context, uint element_count, uint element_size)` |
| `0x0059517e` | `void __stdcall CDXTexture__FreeDecodeBufferIfPresent(void * decode_state, void * decode_buffer)` |
| `0x00595183` | `void __stdcall CDXTexture__InitDecodeSeedDefault(void * png_decode_state)` |
| `0x0059519a` | `void __stdcall CDXTexture__UpdateChunkCrc(void * png_decode_state, void * source_buffer, uint byte_count)` |
| `0x005951d9` | `void __stdcall CDXTexture__ZeroDecodeWorkspace16Dwords(void * png_decode_state, void * workspace)` |
| `0x005951e9` | `void * __stdcall CDXTexture__AllocZeroedInflateState(int state_required_flag)` |
| `0x00595220` | `void __stdcall CTexture__ResetDecodeContextWithDefaults(void * jpeg_compress_context, int expected_libjpeg_version, int expected_struct_size)` |
| `0x005952e0` | `void __stdcall CTexture__SetDecodeTableEpoch(void * jpeg_compress_context, int sent_table_flag)` |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `13` xref rows, `296` instruction rows, and `8` clean decompile rows.
- Queue refresh PASS: `6098` total, `4024` commented, `2074` commentless, `1216` exact-undefined signatures, and `301` `param_N` signatures.
- Strict comment-plus-clean-signature proxy from the refreshed TSV is `3970/6098 = 65.10%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-163011_post_wave699_cdxtexture_png_decode_workspace_tail_verified`, `19` files, `165219207` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact PNG decode-state layout, allocator ABI, overflow policy, workspace ownership, CRC flag enum, chunk-read contract, zlib/inflate-state layout, JPEG context layout, IJG/libjpeg source identity, runtime PNG behavior, runtime cleanup behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x00595350 CTexture__ProcessDecodeStateMachineStep`.

Probe anchors: `Wave699 CDXTexture PNG decode-workspace tail`, `cdxtexture-png-decode-workspace-tail-wave699`, `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`, `0x005952e0 CTexture__SetDecodeTableEpoch`, `0x00595350 CTexture__ProcessDecodeStateMachineStep`.
