# Ghidra CFastVB Stack-Locked Transform Review Wave1053 Readiness Note

Status: complete read-only static re-audit evidence
Date: 2026-06-01
Scope: `cfastvb-stacklocked-transform-review-wave1053`

Wave1053 re-read twenty-four existing CFastVB stack-locked/comment-only transform, curve, quaternion, and optional-composition dispatch helpers from the older Wave717, Wave718, Wave720, and Wave721 CFastVB math surfaces. The pass made no Ghidra mutation, no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Primary target groups:

| Group | Addresses | Static read-back evidence |
| --- | --- | --- |
| Wave717 batch transforms | `0x0059f857`, `0x0059fa5d`, `0x0059fbeb`, `0x0059fd51`, `0x0059fe61`, `0x005a009f`, `0x005a026f`, `0x005a04a0` | DATA xrefs from `CFastVB__InitDispatchTableVariant_005980be` and `_0059822c`; batch matrix/vector work remains tied to `CFastVB__BroadcastMatrix4x4ToSIMDLanes`, scalar tail dispatch, reciprocal projection, and weighted matrix blend evidence. |
| Wave718 cubic / interpolation helpers | `0x005a0f50`, `0x005a1002`, `0x005a1087`, `0x005a112c`, `0x005a11df`, `0x005a1279`, `0x005a13f7` | DATA xrefs from both dispatch-table variants; saved comments/tags still describe cubic basis, cubic blend, derivative, and reciprocal-weighted interpolation helpers with hidden stack context. |
| Wave720 array/quaternion stack-locked rows | `0x005a38c0`, `0x005a3980`, `0x005a40c0`, `0x005a4ecf`, `0x005a4f5c`, `0x005a519e` | DATA xrefs from `CFastVB__InitDispatchOpsFromFeatureFlags`; evidence covers Vec4/Vec3 array transforms and quaternion triple/control/spline blending through visible interpolation/normalization context helpers. |
| Wave721 optional transform / packed angle rows | `0x005a647f`, `0x005a7617`, `0x005a7e09` | DATA xrefs from `CFastVB__InitDispatchOpsFromFeatureFlags`; context exports include visible matrix/quaternion helpers around `0x005a7cf0`, `0x005a8f5d`, and `0x005a9d78` so the optional-composition midpoint is not isolated. |

Read-back evidence:

- Primary exports: `24` metadata rows, `24` tag rows, `34` xref rows, `4682` function-body instruction rows, and `24` decompile rows.
- Context exports: `12` metadata rows, `12` tag rows, `49` xref rows, `949` function-body instruction rows, and `12` decompile rows.
- Primary DATA xrefs tie every target to `CFastVB__InitDispatchTableVariant_005980be`, `CFastVB__InitDispatchTableVariant_0059822c`, or `CFastVB__InitDispatchOpsFromFeatureFlags`.
- Tags preserve the intended `comment-only`, `stack-locked`, `hidden-stack-context`, or `hidden-register-context` boundaries where applicable. This is intentional evidence, not open function-quality debt.
- Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `769/1408 = 54.62%`; expanded static surface progress advances to `1057/1509 = 70.05%`; top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`, `19` files, `174623623` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The twenty-four target functions still exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- Their incoming references still come from the expected CFastVB dispatch-table initializer functions.
- The old `int ...(void)` signatures on stack-locked rows are deliberate bounded signatures where Ghidra still exposes hidden register/stack ABI uncertainty.
- No fresh evidence required a rename, signature rewrite, boundary recovery, or comment/tag mutation.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact vector, matrix, quaternion, stride, lane-order, or optional-input layouts.
- Hidden EBX/EDI/XMM/MMX/stack ABI completeness.
- Runtime CPU feature selection and runtime math/render correctness.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1053; cfastvb-stacklocked-transform-review-wave1053; 0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857; 0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0; 0x005a0f50 CFastVB__EvaluateCubicBasisVec3; 0x005a13f7 CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7; 0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4; 0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e; 0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f; 0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles; 0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchTableVariant_0059822c; CFastVB__InitDispatchOpsFromFeatureFlags; 769/1408 = 54.62%; 1057/1509 = 70.05%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified; no mutation.
