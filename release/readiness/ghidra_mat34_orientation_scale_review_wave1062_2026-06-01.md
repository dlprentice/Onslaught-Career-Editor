# Ghidra Mat34 Orientation/Scale Review Wave1062 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-01
Scope: `mat34-orientation-scale-review-wave1062`

Wave1062 re-read two older pre-Wave900 Mat34 corrections plus adjacent Mat34/vector context, then saved a narrow comment/tag normalization for two already named/commented matrix helpers. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

Primary targets:

| Address | Existing saved signature | Evidence |
| --- | --- | --- |
| `0x00495ed0 Mat34__ScaleByScalar` | `void __thiscall Mat34__ScaleByScalar(void * this, void * outMatrix, float scalar)` | Fresh decompile/instructions preserve the source-matrix ECX receiver, output matrix stack pointer, scalar stack float, scaled rows at offsets `+0x0..+0x28`, and `RET 0x8`. |
| `0x004f8140 Mat34__SetFromEulerDegrees` | `void __thiscall Mat34__SetFromEulerDegrees(void * this, int yaw_deg, int pitch_deg, int roll_deg)` | Fresh decompile/instructions preserve the destination ECX receiver, three integer degree arguments, degree-to-radian constant `0x005dfb6c`, row construction through `Vec3__SetXYZ`/`Mat34__SetRows`, and `Mat34__MultiplyBasisToOut`. |

Normalized context rows:

| Address | Normalization |
| --- | --- |
| `0x0040d1f0 Mat34__SetFromEulerAngles` | Added `mat34-orientation-scale-review-wave1062`, `wave1062-readback-verified`, and related Mat34/basis/euler tags; replaced the stale comment wording that listed tags as unproven with fresh xref-backed static evidence. |
| `0x0040d2c0 Mat34__TransformVec3ByBasisToOut` | Added `mat34-orientation-scale-review-wave1062`, `wave1062-readback-verified`, and related Mat34/basis/Vec3-transform tags; replaced the stale comment wording that listed tags as unproven with fresh xref-backed static evidence. |

Context anchors:

- `0x0040d320 Mat34__MultiplyBasisToOut`
- `0x004f7e90 CUnit__ctor_base`
- `0x005b86c0 CFastVB__FastAcosApprox_Scalar`

Fresh evidence highlights:

- `0x0040d1f0 Mat34__SetFromEulerAngles` xrefs include `CBattleEngine__GetLaunchPosition`, `OID__CanFireAtTarget_BallisticArcA`, `CMCComponent__VFunc_04_UpdateTurretBarrelTransform`, `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`, and `CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0`.
- `0x0040d2c0 Mat34__TransformVec3ByBasisToOut` xrefs include `CBattleEngine__GetLaunchPosition`, `CMCMech__BuildInterpolatedPoseAndAnchor`, `CVBufTexture__RenderDynamicUnitPass`, `CMCBuggy__UpdateWheel`, `CParticle`/`CPDSimpleSprite`/`CDXEngine` render paths, `CSquadNormal` formation helpers, and `CMeshCollisionVolume__VFunc_04_004ad830`.
- The two primary Mat34 rows remain coherent with their older Wave356/Wave548 names/signatures and with the Wave973 Mat34/vector context.

Read-back evidence:

- Pre primary exports: `2` metadata rows, `2` tag rows, `14` xref rows, `306` function-body instruction rows, and `2` decompile rows.
- Pre context exports: `5` metadata rows, `5` tag rows, `168` xref rows, `418` function-body instruction rows, and `5` decompile rows.
- `ApplyMat34OrientationScaleReviewWave1062.java dry`: `updated=0 skipped=0 tags_added=22 comment_updated=2 missing=0 bad=0`.
- `ApplyMat34OrientationScaleReviewWave1062.java apply`: `updated=2 skipped=0 tags_added=22 comment_updated=2 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyMat34OrientationScaleReviewWave1062.java final dry`: `updated=0 skipped=2 tags_added=0 comment_updated=0 missing=0 bad=0`.
- Post exports: `7` metadata rows, `7` tag rows, `182` xref rows, `724` function-body instruction rows, and `7` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`; the Wave1062 primary rows were selected from the broader visible risk-ranked Mat34 surface rather than the materialized focused top slice.
- Expanded static surface progress advances to `1170/1531 = 76.42%` after adding two newly re-audited primary Mat34 rows outside the prior expanded denominator.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-215617_post_wave1062_mat34_orientation_scale_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The seven post target rows exist in the saved Ghidra project with expected names and signatures.
- `0x0040d1f0` and `0x0040d2c0` now have Wave1062 static re-audit tags and refreshed comments.
- The Mat34 scale/orientation/basis-transform helper surface is current against fresh metadata, tags, xrefs, body instructions, and decompile-index evidence.

What remains unproven:

- Exact Mat34/Vec3/FMatrix source type identity and concrete layout.
- Exact source-body identity.
- Runtime transform/orientation/render/formation behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next focused static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1062; mat34-orientation-scale-review-wave1062; 0x00495ed0 Mat34__ScaleByScalar; 0x004f8140 Mat34__SetFromEulerDegrees; 0x0040d1f0 Mat34__SetFromEulerAngles; 0x0040d2c0 Mat34__TransformVec3ByBasisToOut; 0x0040d320 Mat34__MultiplyBasisToOut; 0x004f7e90 CUnit__ctor_base; 0x005b86c0 CFastVB__FastAcosApprox_Scalar; 812/1408 = 57.67%; 1170/1531 = 76.42%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-215617_post_wave1062_mat34_orientation_scale_review_verified; comment/tag normalization.
