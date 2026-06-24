# Wave1214 Math Color Screen Dispatch Current-Risk Review

Status: complete static current-risk read-only review; validation passed; artifact commit recorded
Date: 2026-06-07
Tag: `wave1214-math-color-screen-dispatch-current-risk-review`

Wave1214 re-read `8 math/color/screen transform dispatch current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This is a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk progress is `1133/1179 = 96.10%`; remaining active focused work: 46. The legacy additive counter is deprecated (`1164/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

## Targets

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x004cab30` | `Color32__LerpArgb` | CALL xref `0x004ca15d` from the CPDSimpleSprite expression/tint no-function island; linearly interpolates packed ARGB lanes from two colors using `t` and `(1.0 - t)`, then rounds and repacks without an internal clamp. |
| `0x004cac40` | `Math__InvLerpClamp01` | CALL xref `0x004ca14c` from the same particle/tint island; computes `(value - min) / (max - min)`, clamps to `0..1`, and still has no visible retail divide-by-zero guard. |
| `0x004cac80` | `CPDSelector__ConvertNormalizedToScreenCoords` | CALL xrefs `0x004c9f2a` and `0x004c9f43`; scales a normalized selector pair by the screen/global scalar and rounds through `CRT__RoundDoubleWithFpuChecks`, but the decompiler still does not expose a stable return/output convention. |
| `0x0055dcb0` | `CRT__AcosDispatch_ST0` | `58 xref rows` include `41` broad world/gameplay/math callsites such as `CBattleEngine__HandleAutoAim`, `CBattleEngine__UpdateAutoAim`, `Vec3__ElevationOrZero`, `CPanCamera__Update`, `OID__CanFireAtTarget_BallisticArcA`, `OID__UpdateAimTransformAndAttachTargetReader`, `CRound__SpawnConfiguredProjectile`, and `CWorld__RasterizeFootprintIntoOccupancyBitplanes`; body marshals x87 `ST0`, calls `CRT__ExtractFiniteExponentMaskOrPassThrough`, then calls `CRT__Acos`. |
| `0x00577267` | `Math__BuildTranslationMatrix4x4_Dispatch_Thunk` | CALL xrefs `0x0054af55` and `0x0054af7a` from `CMeshRenderer__RenderMeshCore`; one-instruction `JMP [0x00656f98]` thunk into the CPU-selected translation-matrix dispatch slot. |
| `0x005775bd` | `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk` | CALL xrefs from `CFastVB__BuildTransformMatrixWithOffsets`, `Math__BuildMatrix4x4FromEulerAngles`, and `CTexture__BuildTransformMatrixWithOptionalOffsets`; one-instruction `JMP [0x00656fc8]` thunk into the quaternion-to-matrix dispatch slot. |
| `0x00577a38` | `Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk` | CALL xref `0x0057925b` from `Math__BuildMatrix4x4FromEulerAngles`; one-instruction `JMP [0x00656f94]` thunk, preserving the Wave661 correction that this is Euler-to-quaternion, not Euler-matrix. |
| `0x00577ea4` | `Math__InterpolateVec4ByRatio_Dispatch_Thunk` | CALL xrefs from `Math__BezierBlendVec4` and `Math__BlendVec4DualWeights`; one-instruction `JMP [0x00656fbc]` thunk into the vec4 interpolation dispatch slot. |

Context exports covered `CPDSimpleSprite__EvalExpressionNode`, `CEngine__ConfigureParticleBurstForDistance`, `CEngine__ComputeSpriteTintByDistance`, `CMeshRenderer__RenderMeshCore`, `Math__BuildTranslationMatrix4x4_Dispatch`, `Math__BuildTranslationMatrix4x4`, `Math__BuildQuaternionRotationMatrix_Dispatch`, `Math__BuildQuaternionRotationMatrix`, `CFastVB__BuildTransformMatrixWithOffsets`, `Math__BuildQuaternionFromEulerAngles_Dispatch`, `Math__BuildQuaternionFromEulerAngles`, `Math__InterpolateVec4ByRatio_Dispatch`, `Math__InterpolateVec4ByRatio`, `Math__BezierBlendVec4`, `Math__BlendVec4DualWeights`, `Math__BuildMatrix4x4FromEulerAngles`, and `CTexture__BuildTransformMatrixWithOptionalOffsets`.

Fresh Ghidra export counts: `8` metadata rows, `8` tag rows, `58 xref rows`, `175 instruction rows`, and `8 decompile rows`. Context export counts: `20` metadata rows, `20` tag rows, `43 context xref rows`, `3821 context instruction rows`, and `20 context decompile rows`.

Codex read-only consults used; no Cursor/Composer. The central accounting paths are `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `mesh-resource-render-static-contract.md`, and `wave1108-current-risk-rank`.

Verified backup: `G:\GhidraBackups\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified` (`19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`).

Boundary: this wave strengthens rebuild-grade static contracts and the rebuild-grade specification aiming at no noticeable difference for particle tint/color helpers, selector screen-coordinate conversion, x87 acos dispatch, and mesh/texture/CFastVB math dispatch thunks. Runtime particle rendering behavior, runtime screen-coordinate output, runtime x87/CRT edge cases, runtime CPU feature dispatch, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
