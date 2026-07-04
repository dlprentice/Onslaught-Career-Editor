# Ghidra CFastVB Dispatch Continuation Wave968

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `cfastvb-dispatch-continuation-wave968`

Wave968 continued the CFastVB dispatch-table boundary review from Wave967 and recovered five previously non-function targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created five Ghidra function objects, saved names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

Recovered rows:

| Address | Saved signature | Static read-back evidence |
| --- | --- | --- |
| `0x005a6209 CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209` | `void __stdcall CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)` | Dispatch slot `+0x84` stored at `0x00598572`; starts after `0x005a6206 RET 0x8`, writes three stack scalar values into diagonal-like 0x40-byte matrix lanes with zero-fill and constant `0x005ef1c0`, runs `FEMMS`, and ends at `0x005a624d RET 0x10`. |
| `0x005ab06f CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f` | `void __stdcall CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f(void * out_vec4_lanes, void * in_vec4_lanes, void * matrix4x4)` | Dispatch slot `+0x88` stored at `0x0059857c`; starts after `0x005ab06c RET 0x8`, multiplies a packed four-float/qword input pair across matrix-like qword lanes, writes two output qwords, runs `FEMMS`, and ends at `0x005ab0ea RET 0xc` before `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`. |
| `0x005a6250 CFastVB__DispatchOp_TransposeMatrix4x4_005a6250` | `void __stdcall CFastVB__DispatchOp_TransposeMatrix4x4_005a6250(void * out_matrix4x4, void * in_matrix4x4)` | Dispatch slot `+0x94` stored at `0x0059859a`; starts after `0x005a624d RET 0x10`, shuffles eight source qword lanes with `PUNPCKLDQ`/`PUNPCKHDQ`, writes a repacked 0x40-byte matrix-like output block, runs `FEMMS`, and ends at `0x005a62bc RET 0x8`. |
| `0x005a62f8 CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8(void * out_matrix4x4, void * in_quaternion_lanes)` | Default dispatch slot `+0x98` stored at `0x005985a4`; starts after `0x005a62f7 RET`, expands packed quaternion-like qword input through `PFADD`/`PFMUL`/`PFSUBR` against `0x005ef100`, writes a 0x40-byte rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a63c7 RET 0x8`. |
| `0x005a63ca CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca(void * out_matrix4x4, void * in_quaternion_lanes)` | Feature override for the same dispatch slot `+0x98` stored at `0x00598692` when feature bits `0x100` and `0x200` are both present; starts after `0x005a63c7 RET 0x8`, uses `PSWAPD`/`PFPNACC`/`PFACC`/`PFMUL`/`PFSUBR`, writes a 0x40-byte rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a647c RET 0x8` before `0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`. |

Read-back evidence:

- Pre-candidate exports verified `5` missing metadata rows, `5` DATA xrefs from `CFastVB__InitDispatchOpsFromFeatureFlags`, `645` around-address instruction rows, and `5` dry-run `would_create` rows.
- Apply dry/apply/final dry: `updated=0 skipped=0 created=0 would_create=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=5 skipped=0 created=5 would_create=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `190` body-instruction rows, and `5` decompile rows.
- Queue after Wave968: `6161` total functions, `6161` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed and strict clean-signature proxy `6161/6161 = 100.00%`.
- Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `353/1417 = 24.91%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-163203_post_wave968_cfastvb_dispatch_continuation_verified`, `19` files, `173607815` bytes, `DiffCount=0`.

What this proves:

- The five dispatch-table targets now exist as saved Ghidra functions with read-back-verified names, signatures, comments, and tags.
- The recovered function boundaries match observed post-`RET` starts and terminal `RET` instructions, without swallowing neighboring starts.
- The saved Ghidra database remains at static export-contract closure after the function-object count increases to `6161`.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact packed lane order, vector/quaternion/matrix layouts, row/column convention, and hidden MMX/register ABI.
- Exact source identity for the recovered functions.
- Runtime CPU dispatch behavior, runtime math/render behavior, BEA patching behavior, and rebuild parity.

Probe token anchor: Wave968; cfastvb-dispatch-continuation-wave968; 0x005a6209 CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209; 0x005ab06f CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f; 0x005a6250 CFastVB__DispatchOp_TransposeMatrix4x4_005a6250; 0x005a62f8 CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8; 0x005a63ca CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca; 0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags; 344/1408 = 24.43%; 353/1417 = 24.91%; 6161/6161 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-163203_post_wave968_cfastvb_dispatch_continuation_verified; function-boundary recovery.
