# Wave1109 CFastVB Current-Risk Head Supersession

Status: complete static supersession accounting
Last updated: 2026-06-04
Scope: `wave1109-cfastvb-current-risk-head-supersession`

Wave1109 reviews the first fifteen rows in the Wave1108 current focused denominator and closes them as superseded by prior Wave1053 read-back evidence. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1109 current focused supersession accounting | `15/1179 = 1.27%` |

## Superseded Head Rows

These rows are the first fifteen Wave1108 focused candidates. Wave1053 (`cfastvb-stacklocked-transform-review-wave1053`) already re-read them with metadata, tags, xrefs, instructions, decompile, context exports, and backup evidence.

| Address | Name | Prior evidence |
| --- | --- | --- |
| `0x005a0f50` | `CFastVB__EvaluateCubicBasisVec3` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a1002` | `CFastVB__EvaluateCubicBasisVec2` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a1087` | `CFastVB__EvaluateCubicBasisVec4` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a112c` | `CFastVB__DispatchOp_CubicBlendVec3_005a112c` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a11df` | `CFastVB__DispatchOp_CubicBlendVec4_005a11df` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a1279` | `CFastVB__EvaluateCubicBasisDerivativeVec2` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a13f7` | `CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a38c0` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a3980` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a40c0` | `CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a4ecf` | `CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a4f5c` | `CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a519e` | `CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a647f` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a7e09` | `CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms` | Wave1053 metadata/tag/xref/decompile read-back |

Wave1053 verified `24` metadata rows, `24` tag rows, `34` xref rows, `4682` instruction rows, `24` decompile rows, `12` context metadata rows, `12` context tag rows, `49` context xref rows, `949` context instruction rows, and `12` context decompile rows. Verified Wave1053 backup: `G:\GhidraBackups\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`.

Latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1109; wave1109-cfastvb-current-risk-head-supersession; 15/1179 = 1.27%; current focused candidates: 1179; Wave1053; cfastvb-stacklocked-transform-review-wave1053; 0x005a0f50 CFastVB__EvaluateCubicBasisVec3; 0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms; G:\GhidraBackups\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This wave closes current-risk accounting for these fifteen rows only. It does not prove runtime math/render correctness, hidden ABI completeness, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
