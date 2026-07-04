# Wave1176 Mat34 / Vec3 Owner-Neutral Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1176-mat34-vec3-owner-neutral-current-risk-review`

Wave1176 accounts for `9 Mat34/Vec3 owner-neutral current-risk rows` from the Wave1108 current-risk denominator. Fresh serialized Ghidra exports verified the selected rows and found no Ghidra mutation warranted.

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x0040d320` | `Mat34__MultiplyBasisToOut` | `64` call xrefs; owner-neutral Mat34-style 3x3 basis multiply with ECX lhs basis and stack args `out_basis` / `rhs_basis`. |
| `0x0041ad10` | `Vec3__AddInPlace` | `21` call xrefs; owner-neutral Vec3 in-place add helper with one stack argument and `RET 0x4`. |
| `0x004f8140` | `Mat34__SetFromEulerDegrees` | `5` call xrefs; degree-to-basis helper using `0x005dfb6c`, `Vec3__SetXYZ`, `Mat34__SetRows`, and `Mat34__MultiplyBasisToOut`. |
| `0x0040d1a0` | `Vec3__ElevationOrZero` | `4` call xrefs; length guard, z-over-length divide, and `OID__AcosWrapper` / CRT acos path. Saved tags are blank, but name/signature/comment evidence is coherent. |
| `0x00477ba0` | `Vec3__MagnitudeSquared` | `6` call xrefs; computes `x*x + y*y + z*z` and returns through ST0. |
| `0x00490900` | `Vec3__SubtractInPlace` | `3` call xrefs; owner-neutral Vec3 in-place subtract helper with one `rhs_vector` stack argument. |
| `0x00495ed0` | `Mat34__ScaleByScalar` | `9` call xrefs; Mat34 scale helper with ECX source matrix, output matrix, scalar stack args, and `RET 0x8`. |
| `0x004c7900` | `Vec3__NormalizeInPlace` | `1` call xref; near-zero guarded normalize-in-place helper using `DAT_005d856c` and `DAT_005d8568 / sqrt(length_sq)`. |
| `0x004c7d90` | `Vec3__CopyXYZ` | `9` call xrefs; three-dword copy helper returning the destination pointer. |

Fresh evidence:

- `9` metadata rows, `9` tag rows, `122 xref rows`, `333 instruction rows`, and `9` decompile rows.
- Logs reported `targets=9 found=9 missing=0`, `rows=9 missing=0`, `Wrote 122 rows`, `Wrote 333 instruction rows`, `targets=9 missing=0`, and `targets=9 dumped=9 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-084715_post_wave1176_mat34_vec3_owner_neutral_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Current-risk accounting moved from `683/1179 = 57.93%` to `692/1179 = 58.69%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 487; current risk candidates: 6166.

Mutation status: read-only review; no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Prior context: Wave388, Wave426, Wave446, Wave469, Wave548, Wave973, Wave997, and Wave1062 already saved or re-read the relevant Mat34/Vec3 static evidence. Wave1176 is the current-risk accounting pass over those owner-neutral rows.

Boundary: exact Vec3 layout, exact Mat34 layout, runtime math behavior, runtime render behavior, runtime collision behavior, runtime transform behavior, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1176; wave1176-mat34-vec3-owner-neutral-current-risk-review; 692/1179 = 58.69%; 9 Mat34/Vec3 owner-neutral current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 487; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; Codex root final judgment; prior Wave388/Wave426/Wave446/Wave469/Wave548/Wave973/Wave997/Wave1062 read-back evidence; 0 / 0 / 0; 6411/6411 = 100.00%; 122 xref rows; 333 instruction rows; 0x0040d320 Mat34__MultiplyBasisToOut; 0x0041ad10 Vec3__AddInPlace; 0x004f8140 Mat34__SetFromEulerDegrees; 0x0040d1a0 Vec3__ElevationOrZero; 0x00477ba0 Vec3__MagnitudeSquared; 0x00490900 Vec3__SubtractInPlace; 0x00495ed0 Mat34__ScaleByScalar; 0x004c7900 Vec3__NormalizeInPlace; 0x004c7d90 Vec3__CopyXYZ; [maintainer-local-ghidra-backup-root]\BEA_20260606-084715_post_wave1176_mat34_vec3_owner_neutral_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
