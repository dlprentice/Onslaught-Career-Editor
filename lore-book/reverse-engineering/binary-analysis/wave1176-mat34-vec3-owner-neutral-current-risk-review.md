# Wave1176 Mat34 / Vec3 Owner-Neutral Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1176-mat34-vec3-owner-neutral-current-risk-review`

Wave1176 accounts for `9 Mat34/Vec3 owner-neutral current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

| Address | Saved row | Static evidence |
| --- | --- | --- |
| `0x0040d320` | `Mat34__MultiplyBasisToOut` | `64` call xrefs across BattleEngine, MeshPart, CMC, monitor, particle, tree, and render paths; Wave388 saved the owner-neutral Mat34-style 3x3 basis multiply signature where ECX is the lhs basis and stack args are `out_basis` and `rhs_basis`. |
| `0x0041ad10` | `Vec3__AddInPlace` | `21` call xrefs across mesh, buggy, cylinder, tentacle, sprite, and camera-adjacent paths; Wave388 saved the owner-neutral Vec3 in-place add signature with `RET 0x4`. |
| `0x004f8140` | `Mat34__SetFromEulerDegrees` | `5` call xrefs from CUnit construction, CWeapon construction, monitor tracking, and projectile burst spawn; Wave548 saved the integer-degree Mat34/FMatrix-style helper using constant `0x005dfb6c`, `Vec3__SetXYZ`, `Mat34__SetRows`, and `Mat34__MultiplyBasisToOut`. |
| `0x0040d1a0` | `Vec3__ElevationOrZero` | `4` call xrefs including `CBattleEngineWalkerPart__Move`, `CBattleEngine__GetLaunchPosition`, and CMC turret/barrel transform context; computes vector length, guards near-zero input, divides z over length, and calls the `OID__AcosWrapper` / CRT acos path. Current saved row has coherent name/signature/comment but no saved tags; Wave1176 records that as a tag gap, not a mutation trigger. |
| `0x00477ba0` | `Vec3__MagnitudeSquared` | `6` call xrefs through dynamic unit render and mesh-collision geometry; Wave446 superseded the stale `Geometry__NoOpHook` label with an x87-returning `x*x + y*y + z*z` helper. |
| `0x00490900` | `Vec3__SubtractInPlace` | `3` call xrefs; Wave426 saved the owner-neutral Vec3 in-place subtract signature with one `rhs_vector` stack argument and `RET 0x4`. |
| `0x00495ed0` | `Mat34__ScaleByScalar` | `9` call xrefs through CMCMech, component/turret, HiveBoss cylinder, and WarspiteDome transform paths; older CMCMech-only ownership is too narrow. |
| `0x004c7900` | `Vec3__NormalizeInPlace` | `1` direct call xref from `CPDSimpleSprite__ProcessAndRenderSpriteList`; Wave469 saved the near-zero guarded normalize-in-place helper using `DAT_005d856c` and `DAT_005d8568 / sqrt(length_sq)`. |
| `0x004c7d90` | `Vec3__CopyXYZ` | `9` call xrefs through CPDSimpleSprite, CThing debug-volume overlay, and CDXImposter quad geometry; Wave469 saved the three-dword copy helper that returns the destination pointer. |

Fresh evidence:

- `9` metadata rows, `9` tag rows, `122 xref rows`, `333 instruction rows`, and `9` decompile rows.
- Logs reported `targets=9 found=9 missing=0`, `rows=9 missing=0`, `Wrote 122 rows`, `Wrote 333 instruction rows`, `targets=9 missing=0`, and `targets=9 dumped=9 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-084715_post_wave1176_mat34_vec3_owner_neutral_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Current-risk accounting moved from `683/1179 = 57.93%` to `692/1179 = 58.69%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 487; current risk candidates: 6166.

Prior context: Wave388 corrected `0x0040d320 Mat34__MultiplyBasisToOut` and `0x0041ad10 Vec3__AddInPlace`; Wave426 corrected `0x00490900 Vec3__SubtractInPlace`; Wave446 corrected `0x00477ba0 Vec3__MagnitudeSquared`; Wave469 corrected `0x004c7900 Vec3__NormalizeInPlace` and `0x004c7d90 Vec3__CopyXYZ`; Wave548 corrected `0x004f8140 Mat34__SetFromEulerDegrees`; Wave973, Wave997, and Wave1062 re-read the Mat34/Vec3 context. A Codex read-only consult recommended this cluster; Codex root audited it against fresh exports and owns final claims.

Boundary: exact Vec3 layout, exact Mat34 layout, runtime math behavior, runtime render behavior, runtime collision behavior, runtime transform behavior, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1176; wave1176-mat34-vec3-owner-neutral-current-risk-review; 692/1179 = 58.69%; 9 Mat34/Vec3 owner-neutral current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 487; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; Codex root final judgment; prior Wave388/Wave426/Wave446/Wave469/Wave548/Wave973/Wave997/Wave1062 read-back evidence; 0 / 0 / 0; 6411/6411 = 100.00%; 122 xref rows; 333 instruction rows; 0x0040d320 Mat34__MultiplyBasisToOut; 0x0041ad10 Vec3__AddInPlace; 0x004f8140 Mat34__SetFromEulerDegrees; 0x0040d1a0 Vec3__ElevationOrZero; 0x00477ba0 Vec3__MagnitudeSquared; 0x00490900 Vec3__SubtractInPlace; 0x00495ed0 Mat34__ScaleByScalar; 0x004c7900 Vec3__NormalizeInPlace; 0x004c7d90 Vec3__CopyXYZ; [maintainer-local-ghidra-backup-root]\BEA_20260606-084715_post_wave1176_mat34_vec3_owner_neutral_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
