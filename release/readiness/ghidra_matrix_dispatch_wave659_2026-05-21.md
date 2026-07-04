# Ghidra Matrix Dispatch Wave659 Readiness Note

Status: complete
Date: 2026-05-21

## Scope

Wave659 matrix dispatch hardening covered sixteen adjacent matrix dispatch and concrete builder rows:

| Address | Saved signature |
| --- | --- |
| `0x005771af` | `void __stdcall Math__BuildScaleMatrix4x4_Dispatch(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)` |
| `0x005771dd` | `void __stdcall Math__BuildScaleMatrix4x4(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)` |
| `0x00577239` | `void __stdcall Math__BuildTranslationMatrix4x4_Dispatch(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)` |
| `0x00577267` | `void __stdcall Math__BuildTranslationMatrix4x4_Dispatch_Thunk(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)` |
| `0x0057726d` | `void __stdcall Math__BuildTranslationMatrix4x4(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)` |
| `0x005772c9` | `void __stdcall Math__BuildRotationMatrixX_Dispatch(void * out_matrix4x4, float angle_radians)` |
| `0x005772e5` | `void __stdcall Math__BuildRotationMatrixX(void * out_matrix4x4, float angle_radians)` |
| `0x0057735f` | `void __stdcall Math__BuildRotationMatrixY_Dispatch(void * out_matrix4x4, float angle_radians)` |
| `0x0057737b` | `void __stdcall Math__BuildRotationMatrixY(void * out_matrix4x4, float angle_radians)` |
| `0x005773f6` | `void __stdcall Math__BuildRotationMatrixZ_Dispatch(void * out_matrix4x4, float angle_radians)` |
| `0x00577412` | `void __stdcall Math__BuildRotationMatrixZ(void * out_matrix4x4, float angle_radians)` |
| `0x0057748e` | `void __stdcall Math__BuildAxisAngleRotationMatrix_Dispatch(void * out_matrix4x4, void * axis_vec3, float angle_radians)` |
| `0x005774ae` | `void __stdcall Math__BuildAxisAngleRotationMatrix(void * out_matrix4x4, void * axis_vec3, float angle_radians)` |
| `0x005775b0` | `void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch(void * out_matrix4x4, void * quaternion_xyzw)` |
| `0x005775bd` | `void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch_Thunk(void * out_matrix4x4, void * quaternion_xyzw)` |
| `0x005775c3` | `void __stdcall Math__BuildQuaternionRotationMatrix(void * out_matrix4x4, void * quaternion_xyzw)` |

The pass created three missing function boundaries (`0x005771dd`, `0x0057726d`, `0x005775c3`), renamed five stale dispatch rows away from `CFastVB`/`CDXTexture` labels, and added bounded comments/tags with the `matrix-dispatch-wave659` tag. It made no executable-byte changes, no installed-game changes, and no runtime claims.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave659-matrix-dispatch/pre-all-metadata.tsv`, `pre-all-tags.tsv`, `pre-all-xrefs.tsv`, `pre-all-instructions.tsv`, `decompile-pre-all/`, `dispatch-runtime-table-pre.tsv`, and `dispatch-source-table-pre.tsv`.
- Apply script: `tools/ApplyMatrixDispatchWave659.java`.
- Dry/apply/final dry:
  - Dry: `updated=0 skipped=16 created=0 would_create=3 body_set=0 would_set_body=3 renamed=0 would_rename=5 signature_updated=13 missing=0 bad=0`.
  - Apply: `updated=16 skipped=0 created=3 would_create=0 body_set=3 would_set_body=0 renamed=5 would_rename=0 signature_updated=11 missing=0 bad=0`.
  - Final dry: `updated=0 skipped=16 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post-state exports verified `16` metadata rows, `16` tag rows, `28` xref rows, `2416` instruction rows, `16` clean decompile rows, and two `71`-row dispatch-table snapshots.
- Runtime dispatch table `0x00656f30` and source/default dispatch table `0x00657050` now resolve the scale, translation, X/Y/Z rotation, quaternion, and axis-angle matrix slots to the saved names above.
- Queue refresh passed with `6096` total functions, `3602` commented, `2494` commentless, `1217` exact-undefined signatures, and `711` `param_N` signatures.
- Comment-backed proxy: `3602/6096 = 59.09%`.
- Strict clean-signature proxy: `3552/6096 = 58.27%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-221700_post_wave659_matrix_dispatch_verified` (`19` files, `163285895` bytes, `DiffCount=0`).
- Next high-signal queue head: `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit`.

## Bounded Claim

This proves saved static retail Ghidra metadata for the matrix dispatch island above: 4x4 scale, translation, X/Y/Z rotation, axis-angle rotation, and quaternion rotation matrix builders plus their runtime dispatch wrappers.

It does not prove exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, or rebuild parity.
