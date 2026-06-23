# Ghidra Vector / Geometry Signature Tranche - 2026-05-09

## Summary

This wave reparsed six saved Ghidra vector/geometry helpers from the static re-audit queue. Fresh metadata, decompile, xref, and instruction exports showed three low-level vector helpers with stale stack-argument names and three owner-scoped labels that were too specific for the observed behavior. A serial headless dry/apply pass saved six corrected signatures/comments and three behavior-scoped names, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040d120` | `void __thiscall Vec3__SubtractToOut(void * this, void * param_1, void * param_2, void * param_3)` | `void __thiscall Vec3__SubtractToOut(void * this, void * outVec, void * rhs)` | Signature hardening: instruction/decompile read-back shows ECX as the lhs vector, stack arg1 as output vector, stack arg2 as rhs vector, three output lane writes, and `ret 0x8`. |
| `0x0040d150` | `void __thiscall Vec3__ScaleToOut(void * this, void * param_1, void * param_2, float param_3)` | `void __thiscall Vec3__ScaleToOut(void * this, void * outVec, float scale)` | Signature hardening: instruction/decompile read-back shows ECX as the input vector, stack arg1 as output vector, stack arg2 as scale, three output lane writes, and `ret 0x8`. |
| `0x0040d180` | `double __thiscall Vec3__Dot(void * this, void * param_1, void * param_2)` | `double __thiscall Vec3__Dot(void * this, void * rhs)` | Signature hardening: instruction/decompile read-back shows ECX as lhs, stack arg1 as rhs, FPU dot-product return, and `ret 0x4`. |
| `0x0040d1a0` | `CMonitor__ComputeVectorLengthOrZero` | `double __fastcall Vec3__ElevationOrZero(void * vec)` | Owner/name correction: body computes vector length, guards near-zero input, divides z over length, and reaches `OID__AcosWrapper` / CRT acos context. Source usage of `FVector::Elevation` supports the behavior-scoped label, but exact source identity remains unproven. |
| `0x0040d1f0` | `OID__BuildOrientationMatrixFromEuler` | `void __thiscall Mat34__SetFromEulerAngles(void * this, float angle0, float angle1, float angle2)` | Owner/name correction: body evaluates cos/sin for three stack float angles, writes matrix/basis lanes through offsets up to `+0x28`, and returns with `ret 0xc`. Broad xrefs keep exact source identity and angle-order semantics provisional. |
| `0x0040d2c0` | `CSquadNormal__TransformVec3ByOrientationMatrix` | `void __thiscall Mat34__TransformVec3ByBasisToOut(void * this, void * outVec, void * vec)` | Owner/name correction: body multiplies a vector by three matrix/basis rows at `+0x0/+0x10/+0x20`, writes output vector lanes, and returns with `ret 0x8`. The checked body does not prove translation semantics. |

## Validation

- Focused TDD red check: `py -3 tools\ghidra_vector_geometry_signature_tranche_probe_test.py` first failed on the missing probe module.
- Focused tests: `py -3 tools\ghidra_vector_geometry_signature_tranche_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_vector_geometry_signature_tranche_probe.py tools\ghidra_vector_geometry_signature_tranche_probe_test.py` passed.
- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `256` rows.
- Fresh instruction read-back: `534` rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-vector-geometry-signature-tranche` passed with `6` signature-hardened targets, `3` renamed targets, `0` `param_N` signature hits, `0` stale-token hits, and `0` overclaim hits.
- Refreshed queue probe: `5866` functions, `489` commented functions, `5377` commentless functions, `2076` undefined signatures, and `2462` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete `Vec3`, `FVector`, `FMatrix`, or `Mat34` layouts; exact Stuart source identity; angle order; translation semantics; Ghidra tags; local variable names; structure types; runtime vector/matrix behavior; BEA launch behavior; game patching; or rebuild parity.
