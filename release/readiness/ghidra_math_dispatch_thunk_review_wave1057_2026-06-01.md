# Ghidra Math Dispatch Thunk Review Wave1057 Readiness Note

Status: complete read-only static re-audit evidence
Date: 2026-06-01
Scope: `math-dispatch-thunk-review-wave1057`

Wave1057 re-read twenty-four existing math/CFastVB dispatch and concrete matrix/quaternion/vec4 helpers from older Wave659, Wave660, and Wave661 evidence, with supporting dispatch-table context from Waves678, 701, 702, and 888. The pass made no Ghidra mutation, no renames, no signature changes, no comment/tag changes, no function-boundary changes, and no executable-byte changes.

Primary target groups:

| Group | Addresses | Static read-back evidence |
| --- | --- | --- |
| Matrix builders | `0x005771af`, `0x005771dd`, `0x00577239`, `0x00577267`, `0x0057726d`, `0x005772c9`, `0x005772e5`, `0x0057735f`, `0x0057737b`, `0x005773f6`, `0x00577412`, `0x0057748e`, `0x005774ae`, `0x005775b0`, `0x005775bd`, `0x005775c3` | Runtime dispatch slots `0x00656f98`, `0x00656fa8`, `0x00656fac`, `0x00656fb0`, `0x00656fb4`, `0x00656fc8`, and `0x00656fd8`; paired source/default slots `0x006570b8`, `0x006570c8`, `0x006570cc`, `0x006570d0`, `0x006570d4`, `0x006570e8`, and `0x006570f8`; concrete bodies still match 4x4 scale, translation, X/Y/Z rotation, axis-angle rotation, and quaternion-to-matrix evidence. |
| Quaternion and vec4 helpers | `0x0057798e`, `0x005779ae`, `0x00577a0a`, `0x00577a38`, `0x00577a3e`, `0x00577e80`, `0x00577ea4`, `0x00577eaa` | Runtime dispatch slots `0x00656fa4`, `0x00656f94`, and `0x00656fbc`; paired source/default slots `0x006570c4`, `0x006570b4`, and `0x006570dc`; concrete bodies still match axis-angle quaternion, Euler-to-quaternion, and sine-weighted vec4 interpolation evidence. |

Read-back evidence:

- Primary exports: `24` metadata rows, `24` tag rows, `46` xref rows, `703` function-body instruction rows, and `24` decompile rows.
- Context exports: `24` metadata rows, `24` tag rows, `116` xref rows, `499` function-body instruction rows, and `24` decompile rows.
- Context anchors include `0x00575986 Math__IsFloatDiffOutsideTolerance`, `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit`, `0x0057804e Math__BlendVec4DualWeights`, `0x00579184 CFastVB__NormalizeQuaternionCopy`, `0x0058926b CFastVB__InitDispatchTableByCpuFeature`, `0x00596341 CFastVB__InitMathDispatchTable`, `0x005980be CFastVB__InitDispatchTableVariant_005980be`, `0x0059822c CFastVB__InitDispatchTableVariant_0059822c`, and `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `799/1408 = 56.75%`.
- Expanded static surface progress advances to `1121/1509 = 74.29%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The twenty-four target functions still exist in the saved Ghidra project with expected names, signatures, comments, and tags.
- Incoming DATA xrefs still tie the dispatch wrappers and concrete helpers to the expected active and default math dispatch table slots.
- Fresh decompile still supports the existing scale, translation, rotation, quaternion, and vec4 interpolation comments.
- No fresh evidence required a rename, signature rewrite, boundary recovery, or comment/tag mutation.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact vector, matrix, quaternion, ratio, lane-order, or storage layouts.
- Runtime CPU feature selection and runtime math/render correctness.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Next candidate note: a sidecar read-only reviewer recommended the old Wave321 CUnitAI/GeneralVolume deploy-tracking residual cluster (`0x004247a0`, `0x00424a20`, `0x00424be0`, `0x00424ca0`, `0x004250f0`) as a useful next focused review candidate.

Probe token anchor: Wave1057; math-dispatch-thunk-review-wave1057; 0x005771af Math__BuildScaleMatrix4x4_Dispatch; 0x005771dd Math__BuildScaleMatrix4x4; 0x00577239 Math__BuildTranslationMatrix4x4_Dispatch; 0x005775c3 Math__BuildQuaternionRotationMatrix; 0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch; 0x00577a3e Math__BuildQuaternionFromEulerAngles; 0x00577eaa Math__InterpolateVec4ByRatio; CFastVB__InitDispatchTableByCpuFeature; CFastVB__InitMathDispatchTable; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchOpsFromFeatureFlags; 799/1408 = 56.75%; 1121/1509 = 74.29%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified; no mutation.
