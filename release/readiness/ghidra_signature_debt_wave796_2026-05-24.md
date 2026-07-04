# Ghidra Signature Debt Wave796 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave796`

Wave796 signature debt saved comments/tags/signatures for the final eleven `param_N` signature rows in the current Ghidra queue. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0` | `void __thiscall CNamedMesh__VFunc_09_004bbcd0(void * this, void * init_record, void * unused_slot_arg)` | Preserves the CNamedMesh vtable-slot boundary while naming the visible init pointer and unused stack slot; hidden register/thiscall storage remains bounded. |
| `0x00564486 CRT__FmodReduceCore` | `int __cdecl CRT__FmodReduceCore(int divisor_mantissa_low, uint divisor_mid_bits, int divisor_sign_exp_high)` | Names the visible packed divisor words for the custom-stack FPU remainder helper. |
| ``0x00574a99 `vector_constructor_iterator'`` | ``void __stdcall `vector_constructor_iterator'(void * base, uint element_size, int element_count, _func_void_ptr_void_ptr * constructor)`` | Visual Studio 2003 Release library match; preserves the existing constructor function-pointer datatype. |
| `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame` | `int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int sof_marker)` | Names the visible SOF marker/context parameter while preserving hidden EAX/ESI/EBX/EBP ABI caveats. |
| `0x00591fc0 CDXTexture__ParseJfifApp0Header` | `void __fastcall CDXTexture__ParseJfifApp0Header(int segment_start_offset)` | Names the visible APP0 segment start/diagnostic offset parameter. |
| `0x005921a0 CDXTexture__ParseAdobeApp14Header` | `void __thiscall CDXTexture__ParseAdobeApp14Header(void * this, uint segment_start_offset, int unused_context)` | Preserves Ghidra's synthetic `this` payload-length display while naming the visible segment offset and unused context. |
| `0x00592ca0 CDXTexture__FormatChunkTagForDiagnostics` | `void __thiscall CDXTexture__FormatChunkTagForDiagnostics(void * this, int decode_state, int message_text, void * unused_context)` | Names the PNG diagnostic formatter's decode-state, optional message, and unused context slots. |
| `0x0059c070 CTexture__ProcessRowBatchesLinearStride` | `void __stdcall CTexture__ProcessRowBatchesLinearStride(int callback_context, int callback_mode)` | Names the visible callback context and mode for the hidden-ESI linear row-batch walker. |
| `0x0059c110 CTexture__ProcessRowBatchesMcuStride128` | `void __stdcall CTexture__ProcessRowBatchesMcuStride128(int callback_context, int callback_mode)` | Names the visible callback context and mode for the hidden-ESI MCU/0x80-stride row-batch walker. |
| `0x0059e310 CDXTexture__WriteJpegHuffmanTable` | `void __thiscall CDXTexture__WriteJpegHuffmanTable(void * this, int table_index, int unused_context)` | Names the JPEG DHT table index and unused context while preserving the hidden EAX table-class selector. |
| `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * out_matrix4, int packed_angle_pair_low, int packed_angle_pair_high)` | Names the visible output matrix pointer and packed angle-pair dwords while preserving the hidden packed-stack ABI caveat. |

Read-back evidence:

- `ApplySignatureDebtWave796.java dry`: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave796.java apply`: `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplySignatureDebtWave796.java final dry`: `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 11 metadata rows, 11 tag rows, 45 xref rows, 539 instruction rows, and 11 decompile rows.
- Queue after Wave796: 6098 total, 5544 commented, 554 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5544/6098 = 90.92%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The eleven target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags match the Wave796 post-export artifacts.
- The `signature-debt-wave796` and `wave796-readback-verified` tags are present on all eleven targets.
- Current exact-undefined and `param_N` signature debt are both zero in the refreshed queue snapshot.

Probe anchors: Wave796 signature debt; signature-debt-wave796; 0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0; 0x00564486 CRT__FmodReduceCore; 0x00574a99 `vector_constructor_iterator'; 0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame; 0x00591fc0 CDXTexture__ParseJfifApp0Header; 0x005921a0 CDXTexture__ParseAdobeApp14Header; 0x00592ca0 CDXTexture__FormatChunkTagForDiagnostics; 0x0059c070 CTexture__ProcessRowBatchesLinearStride; 0x0059c110 CTexture__ProcessRowBatchesMcuStride128; 0x0059e310 CDXTexture__WriteJpegHuffmanTable; 0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles; 0 exact-undefined signatures; 0 param_N signatures; 0x0042f220 CSPtrSet__Clear; [maintainer-local-ghidra-backup-root]\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified.

What remains unproven:

- Hidden register and custom stack ABI details beyond the bounded static comments.
- Exact source identity and concrete object/decoder/descriptor layouts.
- Runtime texture/JPEG/PNG behavior.
- Runtime C++ array construction behavior.
- Runtime FPU remainder and CFastVB math correctness.
- BEA patching behavior.
- Rebuild parity.
