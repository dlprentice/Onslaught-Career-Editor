# Ghidra Math/Mat34 Vector Review Wave973 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `math-mat34-vector-review-wave973`

Wave973 re-reviewed a compact Vec3/Mat34/FastVB math cluster and recovered one previously missing Ghidra function boundary at `0x0040c990 CBattleEngine__GetLaunchPosition`. Mutation status: function-boundary recovery. The pass created one function object, saved the source-backed name/signature/comment/tags, made no executable-byte change, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0040c990 CBattleEngine__GetLaunchPosition` | New function boundary recovered from the no-function gap after `0x0040c720 CGeneralVolume__ResetAndSetActiveReader` and before `0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks`; SEH prologue at `0x0040c990`, terminal `RET 0x14` at `0x0040d0ed`, and source parity with `references/Onslaught/BattleEngine.cpp` lines 3000-3069. |
| `0x0040d1a0 Vec3__ElevationOrZero` | Called by the recovered launch-position body at `0x0040d090`; computes vector elevation through length guard, z-over-length, and acos context. |
| `0x0040d1f0 Mat34__SetFromEulerAngles` | Called by the recovered launch-position body at `0x0040d0b0`; builds Mat34-style basis lanes from three angle inputs. |
| `0x0040d2c0 Mat34__TransformVec3ByBasisToOut` | Called by the recovered launch-position body at `0x0040cf2d`, `0x0040cf4f`, and `0x0040cfe0`; transforms Vec3 lanes by basis rows. |
| `0x0040d320 Mat34__MultiplyBasisToOut` | Called by the recovered launch-position body at `0x0040cfd9` and `0x0040d0c7`; multiplies Mat34-style bases into an output basis. |
| `0x005b86c0 CFastVB__FastAcosApprox_Scalar` | Re-read as nearby math ABI context only; the locked hidden-MM0/stale-EAX signature boundary from Wave737 remains unchanged. |

Read-back evidence:

- `ApplyMathMat34VectorWave973.java dry`: `updated=0 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- `ApplyMathMat34VectorWave973.java apply`: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0`
- `ApplyMathMat34VectorWave973.java final dry`: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports verified `6` metadata rows, `6` tag rows, `153` xref rows, `777` body-instruction rows, and `6` decompile rows.
- Queue after Wave973: `6210` total functions, `6210` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`; comment-backed and strict clean-signature proxy `6210/6210 = 100.00%`.
- Wave911 focused re-audit progress: `350/1408 = 24.86%`.
- Expanded static surface progress: `408/1466 = 27.83%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-192743_post_wave973_math_mat34_vector_review_verified`, `19` files, `173771655` bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra project contains the recovered `0x0040c990 CBattleEngine__GetLaunchPosition` function object.
- The saved signature is `void __thiscall CBattleEngine__GetLaunchPosition(void * this, void * inWeapon, int inIndex, void * outPos, void * outOrientation, int inNeedOrientation)`.
- The saved comment and tags include `math-mat34-vector-review-wave973` and `wave973-readback-verified`.
- The surrounding Vec3/Mat34/FastVB rows were re-read against fresh metadata, xrefs, instructions, and decompile exports.

What remains unproven:

- Exact retail `CBattleEngine`, `CWeapon`, Vec3, and Mat34 layouts.
- Exact out-vector/out-matrix ABI beyond observed static call/return shape.
- Runtime launch-position behavior.
- Runtime projectile, camera, cockpit emitter, gravity, and auto-aim behavior.
- BEA patching behavior.
- Rebuild parity.
