# Ghidra CFastVB Fast-Trig ABI Review Wave967

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `cfastvb-fast-trig-abi-review-wave967`

Wave967 re-reviewed the Wave737 CFastVB fast-trig tail and recovered four previously non-function dispatch-table targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created four Ghidra function objects, saved names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

Recovered rows:

| Address | Saved state | Static read-back evidence |
| --- | --- | --- |
| `0x005a4c67 CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67` | `void __stdcall CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67(void * out_quaternion_lanes, int packed_lane_arg2, int packed_lane_arg3, int packed_lane_arg4)` | Dispatch slot `+0x64` stored at `0x00598537`; starts after `0x005a4c64 RET`, calls `0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar` at `0x005a4c89`, `0x005a4c9a`, and `0x005a4ca9`, writes two qword quaternion-like output lanes, runs `FEMMS`, and ends at `0x005a4d29 RET 0x10`. |
| `0x005a60ef CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef(void * out_matrix4x4, float angle_radians)` | Dispatch slot `+0x78` stored at `0x0059855a`; starts after `0x005a60ec RET`, loads the angle argument into `MM0`, calls `0x005b8ca0`, writes a 0x40-byte X-axis rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a614f RET 0x8`. |
| `0x005a6152 CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152(void * out_matrix4x4, float angle_radians)` | Dispatch slot `+0x7c` stored at `0x00598561`; starts after `0x005a614f RET`, loads the angle argument into `MM0`, calls `0x005b8ca0`, writes a 0x40-byte Y-axis rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a61ad RET 0x8`. |
| `0x005a61b0 CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0(void * out_matrix4x4, float angle_radians)` | Dispatch slot `+0x80` stored at `0x00598568`; starts after `0x005a61ad RET`, loads the angle argument into `MM0`, calls `0x005b8ca0`, writes a 0x40-byte Z-axis rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a6206 RET 0x8`. |

Read-back evidence:

- Pre-review exports verified `13` primary/context metadata rows, `13` tag rows, `28` primary xref rows, `1413` body-instruction rows, `930` xref-site instruction rows, `13` decompile rows, and `32` constant xref rows.
- Orphan-target pre-state verified `4` missing metadata rows, `4` DATA xrefs from `0x00598474`, `356` orphan instruction rows, `89` dispatch-context body rows, `125` around-dispatch instruction rows, and `5` dispatch-context decompile index rows.
- Creation dry/apply/final-dry: `updated=0 skipped=0 created=0 would_create=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=4 skipped=0 created=4 would_create=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Conservative signature-label correction dry/apply/final-dry: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=1 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final post exports verified `4` metadata rows, `4` tag rows, `4` xref rows, `131` body-instruction rows, and `4` decompile rows. Body-boundary readback confirms the new functions did not absorb adjacent starts `0x005a4d2c`, `0x005a6152`, `0x005a61b0`, or `0x005a6209`.
- Queue after Wave967: `6156` total functions, `6156` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed and strict clean-signature proxy `6156/6156 = 100.00%`.
- Wave911 focused re-audit progress after Wave967: `344/1408 = 24.43%`; expanded static surface progress including the four newly recovered dispatch targets is `348/1412 = 24.65%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-160046_post_wave967_cfastvb_fast_trig_abi_review_verified`, `19` files, `173575047` bytes, `DiffCount=0`.

What this proves:

- The four dispatch-table targets now exist as saved Ghidra functions with read-back-verified names, signatures, comments, and tags.
- The recovered function boundaries match observed post-`RET` starts and terminal `RET` instructions, without swallowing neighboring dispatch targets.
- The saved Ghidra database remains at static export-contract closure after the function-object count increases to `6156`.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact packed lane order, vector/quaternion/matrix layouts, and hidden MMX/register ABI.
- Exact source identity for the recovered functions.
- Runtime CPU dispatch behavior, runtime math behavior, BEA patching behavior, and rebuild parity.
- The broader `CFastVB__InitDispatchOpsFromFeatureFlags` dispatch-table target set still has additional no-function labels that should be reviewed in a later focused wave instead of folded into Wave967.

Probe token anchor: Wave967; cfastvb-fast-trig-abi-review-wave967; 0x005a4c67 CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67; 0x005a60ef CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef; 0x005a6152 CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152; 0x005a61b0 CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0; 0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags; 0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar; 344/1408 = 24.43%; 348/1412 = 24.65%; 6156/6156 = 100.00%; G:\GhidraBackups\BEA_20260528-160046_post_wave967_cfastvb_fast_trig_abi_review_verified; function-boundary recovery.
