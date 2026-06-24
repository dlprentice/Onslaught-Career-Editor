# Ghidra Vec3 Residual Review Wave997 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `vec3-residual-review-wave997`

Wave997 re-reviewed the remaining Wave911-focused `0x0041ad10 Vec3__AddInPlace` candidate with adjacent owner-neutral Vec3 algebra helpers. Fresh read-only metadata, tag, xref, instruction, and decompile exports matched the already-saved Wave388, Wave426, Wave469, and Wave798 evidence, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary targets:

| Address | Read-back evidence |
| --- | --- |
| `0x0041ad10 Vec3__AddInPlace` | ECX is the destination vector, `[ESP+4]` is `add_vec3`, X/Y/Z lanes are added in place, and the body returns with `RET 0x4`. |
| `0x00490900 Vec3__SubtractInPlace` | ECX is the destination vector, `[ESP+4]` is `rhs_vector`, X/Y/Z lanes are subtracted in place, and the body returns with `RET 0x4`. |
| `0x004404f0 Vec3__NegateToOut` | ECX is the source vector, `[ESP+4]` is the output pointer, X/Y/Z lanes are negated via `FCHS`, and the body returns with `RET 0x4`. |
| `0x004c7d90 Vec3__CopyXYZ` | ECX is the destination vector, `[ESP+4]` is `src_vec3`, three dwords are copied, and EAX returns the destination pointer before `RET 0x4`. |
| `0x004c7900 Vec3__NormalizeInPlace` | ECX is the vector, the body computes squared magnitude, compares against `0x005d856c`, and scales X/Y/Z by `0x005d8568 / sqrt(length_sq)` when above threshold. |

Fresh read-back evidence:

- Exports: `5` metadata rows, `5` tag rows, `45` xref rows, `73` body-instruction rows, and `5` decompile rows.
- Xrefs preserve the owner-neutral call spread: `Vec3__AddInPlace` is reached from `CMeshPart__EvaluateAnimatedTransformCore`, `CMCBuggy__UpdateWheel`, `CCylinder__ResolveCollisionVFunc02`, `CPDSimpleSprite__ProcessAndRenderSpriteList`, and `CMCTentacle` helpers; `Vec3__NegateToOut` is reached from `CDXEngine__BuildDirectionalSampleRing`, `CThing__RenderDebugVolumeOverlay`, `CMCMech__UpdateBone`, and `CCylinder__ResolveCollisionVFunc02`; `Vec3__NormalizeInPlace` remains directly called by `CPDSimpleSprite__ProcessAndRenderSpriteList`.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress is now `465/1408 = 33.03%`.
- Expanded static surface progress is now `581/1478 = 39.31%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-083022_post_wave997_vec3_residual_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave997; `vec3-residual-review-wave997`; `0x0041ad10 Vec3__AddInPlace`; `0x00490900 Vec3__SubtractInPlace`; `0x004404f0 Vec3__NegateToOut`; `0x004c7d90 Vec3__CopyXYZ`; `0x004c7900 Vec3__NormalizeInPlace`; `465/1408 = 33.03%`; `581/1478 = 39.31%`; `6222/6222 = 100.00%`; `G:\GhidraBackups\BEA_20260531-083022_post_wave997_vec3_residual_review_verified`; no mutation.

What this proves:

- The reviewed Vec3 rows exist in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The saved one-stack-argument plus ECX receiver ABI still holds for add, subtract, negate-to-out, and copy helpers.
- The normalize helper still has no explicit stack argument and retains the saved near-zero guard and reciprocal-scale pattern.
- The owner-neutral Vec3 naming remains supported by broad callsite evidence rather than a single gameplay owner.

What remains unproven:

- Exact `Vec3` source type/layout identity beyond the observed X/Y/Z lanes.
- Exact Stuart source-body identity.
- Runtime math, render, collision, camera, or particle behavior.
- BEA patching behavior.
- Rebuild parity.
