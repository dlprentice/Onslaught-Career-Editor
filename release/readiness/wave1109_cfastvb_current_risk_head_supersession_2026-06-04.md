# Wave1109 CFastVB Current-Risk Head Supersession Readiness Note

Status: complete static supersession accounting
Date: 2026-06-04
Scope: `wave1109-cfastvb-current-risk-head-supersession`

Wave1109 closes the first fifteen Wave1108 current focused rows as superseded by prior Wave1053 (`cfastvb-stacklocked-transform-review-wave1053`) static read-back evidence. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Read-back basis:

- Wave1108 current focused candidates: current focused candidates: 1179.
- Wave1109 accounted head progress: `15/1179 = 1.27%`.
- Covered head anchors include `0x005a0f50 CFastVB__EvaluateCubicBasisVec3`, `0x005a1002 CFastVB__EvaluateCubicBasisVec2`, `0x005a1087 CFastVB__EvaluateCubicBasisVec4`, `0x005a112c CFastVB__DispatchOp_CubicBlendVec3_005a112c`, `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `0x005a4ecf CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf`, `0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, and `0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms`.
- Wave1053 verified `24` metadata rows, `24` tag rows, `34` xref rows, `4682` instruction rows, `24` decompile rows, `12` context metadata rows, `12` context tag rows, `49` context xref rows, `949` context instruction rows, and `12` context decompile rows.
- Wave1053 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`.
- Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

What this proves:

- The first fifteen Wave1108 focused rows are already covered by prior static read-back evidence.
- No fresh evidence in this accounting pass justified a rename, signature rewrite, comment/tag mutation, function-boundary change, or executable-byte change.

What remains separate:

- The rest of the Wave1108 current focused denominator.
- Runtime math/render correctness.
- Hidden ABI completeness.
- Exact vector/matrix/quaternion/stride/layout identity.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
