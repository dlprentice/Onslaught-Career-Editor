# Wave1181 CFastVB Residual Math / Dispatch / Trig Current-Risk Review

Status: complete read-only static current-risk review; validated and pushed
Date: 2026-06-06
Scope tag: `wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review`

Wave1181 accounts for `21 CFastVB residual math/dispatch/trig current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with a fresh serialized Ghidra export. This was a read-only review: no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Codex read-only consults used; Codex root final judgment kept the exact 21-row residual CFastVB slice after both consults agreed the rows were still active current-risk candidates and not already counted by Wave1109-Wave1180. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `750/1179 = 63.61%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 429; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `21` metadata rows, `21` tag rows, `40 xref rows`, `2013 instruction rows`, and `21` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-111618_post_wave1181_cfastvb_residual_current_risk_review_verified`.

## Reviewed Anchors

| Subcluster | Anchors | Evidence shape |
| --- | --- | --- |
| Cubic/transform helpers | `CFastVB__HermiteInterpolateVec3`, `CFastVB__BuildTransformMatrixWithOffsets` | Prior Wave887/Wave888 static read-back, DATA refs `0x00657114` and `0x006570f4`, fresh metadata/tags/xrefs/instructions/decompile. |
| Scalar endpoint solve | `CFastVB__SolveScalarEndpointPairFromSamples` | Prior Wave701 static read-back, call from `CFastVB__PackScalarBlock_InterpolatedEndpoints` at `0x00597cfb`, hidden EBX mode remains a static ABI caveat. |
| Wave969 array dispatch residual | `CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40`, `CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0`, `CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00`, `CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160`, `CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480` | DATA refs from `CFastVB__InitDispatchOpsFromFeatureFlags`; stack-locked dispatch bodies with bounded vector/matrix/packed-lane caveats. |
| Wave970 quaternion/matrix residual | `CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc`, `CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795`, `CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836`, `CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52` | DATA refs from `CFastVB__InitDispatchOpsFromFeatureFlags`; `0x005a4980` is an internal branch target inside `0x005a4836`, not a counted function. |
| Wave971 dispatch-slot residual | `CFastVB__DispatchOp_SlotB0_005a4fee`, `CFastVB__DispatchOp_SlotE0_005a50f9`, `CFastVB__DispatchOp_Slot0C_005a5bd7`, `CFastVB__DispatchOp_Slot2C_005a5e09`, `CFastVB__DispatchOp_Slot68_005a5ed8`, `CFastVB__DispatchOp_Slot6C_005a5f28`, `CFastVB__DispatchOp_Slot70_005a6013` | Seven early residual Wave971 dispatch-slot rows; later Wave971 tail rows were already counted by Wave1165 and are deliberately not duplicated here. |
| Fast trig helpers | `CFastVB__FastTrigPairApprox_Scalar`, `CFastVB__FastSinApprox_Scalar_005b8da0` | Prior Wave737 static read-back, `14` and `7` call xrefs respectively; unreliable packed-register return and MM0/packed-lane ABI remain explicit caveats. |

## Boundary

This wave strengthens the CFastVB static math/dispatch map needed for rebuild-grade static contracts and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove runtime math/render proof, exact dispatch-table schema, vector/matrix/quaternion concrete layouts, hidden ABI completeness, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1181; wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review; 750/1179 = 63.61%; 21 CFastVB residual math/dispatch/trig current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 429; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; no Cursor/Composer; residual CFastVB; hidden EBX; unreliable packed-register return; 0x005a4980 internal branch target; Wave969; Wave970; Wave971; Wave737; Wave887; Wave888; Wave701; 0 / 0 / 0; 6411/6411 = 100.00%; 40 xref rows; 2013 instruction rows; CFastVB__HermiteInterpolateVec3; CFastVB__BuildTransformMatrixWithOffsets; CFastVB__SolveScalarEndpointPairFromSamples; CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40; CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836; CFastVB__DispatchOp_SlotB0_005a4fee; CFastVB__FastTrigPairApprox_Scalar; CFastVB__FastSinApprox_Scalar_005b8da0; [maintainer-local-ghidra-backup-root]\BEA_20260606-111618_post_wave1181_cfastvb_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
