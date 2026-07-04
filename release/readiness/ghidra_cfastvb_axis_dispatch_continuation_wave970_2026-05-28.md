# Ghidra CFastVB Axis Dispatch Continuation Wave970

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `cfastvb-axis-dispatch-continuation-wave970`

Wave970 continued the CFastVB dispatch-table boundary review from Wave969 and recovered four previously non-function axis/quaternion dispatch targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created four Ghidra function objects, saved stack-locked names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

Recovered rows:

| Address | Saved signature | Static read-back evidence |
| --- | --- | --- |
| `0x005a46fc CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc` | `int CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc(void)` | Dispatch slot `+0x4c` stored at `0x0059850d`; starts after `0x005a46f9 RET 0x18`, consumes two packed qword quaternion-like inputs from stack arguments, uses packed multiply/add/subtract lanes with sign masks at `0x005ef118`, writes two qword output lanes through the first stack argument, runs `FEMMS`, and ends at `0x005a4792 RET 0x0c` before `0x005a4795`. |
| `0x005a4795 CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795` | `int CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795(void)` | Dispatch slot `+0x50` stored at `0x00598514`; starts after `0x005a4792 RET 0x0c`, computes a packed four-float/qword length from input lanes, gates against threshold constant `0x005ef170`, refines reciprocal square root with `PFRSQRT`/`PFRSQIT1`/`PFRCPIT2`, writes normalized qword output lanes, runs `FEMMS`, and ends at `0x005a47ef RET 0x08` before `0x005a47f2`. |
| `0x005a4836 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836` | `int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836(void)` | Default dispatch slot `+0x60` stored at `0x00598530`; starts after `0x005a4833 RET 0x0c`, reads matrix-like diagonal/off-diagonal lanes from the input record, selects largest-diagonal/trace-style branches through internal branch target `0x005a4980`, normalizes with packed reciprocal-square-root refinement and constant `0x005ef168`, writes quaternion-like qword output lanes, and ends through `RET 0x08` terminals at `0x005a4904`, `0x005a497d`, `0x005a49f1`, and `0x005a4a4f` before `0x005a4a52`. |
| `0x005a4a52 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52` | `int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52(void)` | Feature-override dispatch slot `+0x60` stored at `0x005986a6` when feature bits `0x100` and `0x200` are both present; starts after `0x005a4a4f RET 0x08`, mirrors the packed matrix3x3-to-quaternion branch shape with `PMOVMSKB`/`PFCMPGE` mask selection, reciprocal-square-root refinement, constant `0x005ef168` scaling, and qword output writes, then ends before `0x005a4c67`. |

Read-back evidence:

- Pre-candidate exports verified `4` missing metadata rows, `4` DATA xrefs from `CFastVB__InitDispatchOpsFromFeatureFlags`, `4` dry-run `would_create` rows, and dispatch-store evidence around `0x00598474`.
- Apply dry/apply/final dry: `updated=0 skipped=0 created=0 would_create=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=4 skipped=0 created=4 would_create=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=8 missing=0 bad=0`, then `updated=0 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final post exports verified `4` metadata rows, `4` tag rows, `4` xref rows, `342` body-instruction rows, and `4` decompile rows.
- Queue after Wave970: `6170` total functions, `6170` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed and strict clean-signature proxy `6170/6170 = 100.00%`.
- Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `362/1426 = 25.39%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-174057_post_wave970_cfastvb_axis_dispatch_continuation_verified`, `19` files, `173607815` bytes, `DiffCount=0`.

What this proves:

- The four dispatch-table targets now exist as saved Ghidra functions with read-back-verified names, signatures, comments, and tags.
- The recovered function boundaries match observed post-`RET` starts, DATA dispatch-table stores, and terminal `RET` boundaries without swallowing neighboring starts.
- `0x005a4980` is correctly treated as an internal branch target inside the `0x005a4836` function body, not as a separate dispatch-table function.
- The saved Ghidra database remains at static export-contract closure after the function-object count increases to `6170`.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact vector/quaternion/matrix layout, packed lane order, row/column convention, and hidden MMX/register ABI.
- Exact source identity for the recovered functions.
- Runtime CPU dispatch behavior, runtime math/render behavior, BEA patching behavior, and rebuild parity.

Probe token anchor: Wave970; cfastvb-axis-dispatch-continuation-wave970; 0x005a46fc CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc; 0x005a4795 CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795; 0x005a4836 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836; 0x005a4a52 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52; 0x005a4980 internal branch target; 0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags; 344/1408 = 24.43%; 362/1426 = 25.39%; 6170/6170 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-174057_post_wave970_cfastvb_axis_dispatch_continuation_verified; function-boundary recovery.
