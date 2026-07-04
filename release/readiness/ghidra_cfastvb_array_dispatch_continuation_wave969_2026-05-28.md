# Ghidra CFastVB Array Dispatch Continuation Wave969

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `cfastvb-array-dispatch-continuation-wave969`

Wave969 continued the CFastVB dispatch-table boundary review from Wave968 and recovered five previously non-function array-transform targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created five Ghidra function objects, saved names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

Recovered rows:

| Address | Saved signature | Static read-back evidence |
| --- | --- | --- |
| `0x005a3a40 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40` | `int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40(void)` | Dispatch slot `+0xec` stored at `0x005986cf`; starts after `0x005a3980 RET 0x18`, falls back through scalar helper `0x005aa73b`, broadcasts matrix rows into XMM lanes, processes strided Vec2 inputs, applies translation terms, writes transformed Vec4-style output lanes, and ends at `0x005a3c9c RET 0x18` before `0x005a3ca0`. |
| `0x005a3ca0 CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0` | `int CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0(void)` | Dispatch slot `+0xf0` stored at `0x005986d9`; starts after `0x005a3c9c RET 0x18`, falls back through scalar helper `0x005aa7c9`, applies matrix rows plus translation terms to strided Vec2 inputs, refines projected W with `RCPPS`/`SUBPS`/`MULPS`, writes projected Vec2 output lanes, and ends at `0x005a3ee2 RET 0x18` before `0x005a3f00`. |
| `0x005a3f00 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00` | `int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00(void)` | Dispatch slot `+0xf4` stored at `0x005986e3`; starts after `0x005a3ee2 RET 0x18`, falls back through scalar helper `0x005aa790`, batches strided Vec2 inputs across matrix row lanes without translation terms, writes transformed Vec2 output lanes, and ends at `0x005a40b3 RET 0x18` before `0x005a40c0 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0`. |
| `0x005a4160 CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160` | `int CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160(void)` | Dispatch slot `+0xfc` stored at `0x005986bb`; starts after `0x005a40c0 RET 0x18`, falls back through scalar helper `0x005a9f3f`, applies matrix rows plus translation terms to strided Vec3 inputs, refines projected W with `RCPPS`/`SUBPS`/`MULPS`, writes projected Vec3-style output lanes, and ends at `0x005a447a RET 0x18` before `0x005a4480`. |
| `0x005a4480 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480` | `int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480(void)` | Dispatch slot `+0x100` stored at `0x005986c5`; starts after `0x005a447a RET 0x18`, falls back through scalar helper `0x005a99f8`, batches strided Vec3 inputs across matrix row lanes without translation terms, writes transformed Vec3-style output lanes, and ends at `0x005a46f9 RET 0x18` before adjacent target `0x005a46fc`. |

Read-back evidence:

- Pre-candidate exports verified `5` missing metadata rows, `5` DATA xrefs from `CFastVB__InitDispatchOpsFromFeatureFlags`, `805` near instruction rows, `1705` wide instruction rows, and `5` dry-run `would_create` rows.
- Apply dry/apply/final dry: `updated=0 skipped=0 created=0 would_create=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=5 skipped=0 created=5 would_create=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=10 missing=0 bad=0`, then `updated=0 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `691` body-instruction rows, and `5` decompile rows.
- Queue after Wave969: `6166` total functions, `6166` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed and strict clean-signature proxy `6166/6166 = 100.00%`.
- Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `358/1422 = 25.18%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-170703_post_wave969_cfastvb_array_dispatch_continuation_verified`, `19` files, `173607815` bytes, `DiffCount=0`.

What this proves:

- The five dispatch-table targets now exist as saved Ghidra functions with read-back-verified names, signatures, comments, and tags.
- The recovered function boundaries match observed post-`RET` starts and terminal `RET 0x18` instructions, without swallowing neighboring starts.
- The saved Ghidra database remains at static export-contract closure after the function-object count increases to `6166`.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact vector/matrix layout, packed lane order, row/column convention, and hidden SSE/register ABI.
- Exact source identity for the recovered functions.
- Runtime CPU dispatch behavior, runtime math/render behavior, BEA patching behavior, and rebuild parity.

Probe token anchor: Wave969; cfastvb-array-dispatch-continuation-wave969; 0x005a3a40 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40; 0x005a3ca0 CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0; 0x005a3f00 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00; 0x005a4160 CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160; 0x005a4480 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480; 0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags; 344/1408 = 24.43%; 358/1422 = 25.18%; 6166/6166 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-170703_post_wave969_cfastvb_array_dispatch_continuation_verified; function-boundary recovery.
