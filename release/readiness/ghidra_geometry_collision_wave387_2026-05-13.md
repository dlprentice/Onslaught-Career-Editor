# Ghidra Geometry / Collision Correction Tranche - 2026-05-13

Status: public-safe static RE evidence

## Summary

Wave 387 saved Ghidra signature/comment/tag metadata for four geometry and mesh-collision helper targets after metadata, decompile, xref, instruction, and tag read-back. The pass preserves the current saved names while hardening proof-boundary comments and signatures for the triangle-prism, triangle-edge closest-point, ray/sphere entry-distance, and AABB-distance helpers used by the MeshCollisionVolume swept-sphere path.

This is static Ghidra evidence only. It does not prove runtime collision behavior, exact Stuart-source method identity, concrete vector/AABB/mesh-collision layouts, concrete local types, BEA launch, game patching, or rebuild parity.

## Saved Targets

| Address | Saved name | Saved signature | Evidence boundary |
| --- | --- | --- | --- |
| `0x00479020` | `CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | `int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)` | Tests a candidate direction against three signed edge/plane dot tests and is called from `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`. |
| `0x00479200` | `Geometry__SelectClosestPointOnTriangleEdges` | `void __cdecl Geometry__SelectClosestPointOnTriangleEdges(void * outClosest, void * vertexA, void * vertexB, void * vertexC, void * queryPoint)` | Computes clamped projections across all three triangle edges, then selects the nearest candidate point to `queryPoint`. |
| `0x00479630` | `Geometry__RaySphereEntryDistance` | `double __cdecl Geometry__RaySphereEntryDistance(void * rayStart, void * rayEnd, float radius)` | Normalizes `rayEnd - rayStart`, solves origin-centered sphere entry distance, and returns the retail sentinel when no positive entry is observed. |
| `0x00479770` | `Geometry__DistanceOutsideAabb` | `double __cdecl Geometry__DistanceOutsideAabb(void * point, void * halfExtents)` | Computes absolute centered AABB overhangs with single-axis and two-axis distance branches; the all-three-axis branch records the retail instruction sequence rather than an idealized formula. |

## Validation

| Check | Result |
| --- | --- |
| Headless `ApplyGeometryCollisionWave387.java` dry run | PASS: `updated=0 skipped=4 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Headless `ApplyGeometryCollisionWave387.java` apply | PASS: `updated=4 skipped=0 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Post-apply read-back exports | PASS: `4` metadata rows, `4` decompile exports, `4` xref rows, `884` instruction rows, and `4` tag rows. |
| `py -3 tools\ghidra_geometry_collision_wave387_probe_test.py` | PASS: `2/2` tests. |
| `cmd.exe /c npm run test:ghidra-geometry-collision-wave387` | PASS: `status=PASS`, `targets=4`, `caller_hits=4`, `instruction_hits=11`. |
| `py -3 -m py_compile tools\ghidra_geometry_collision_wave387_probe.py tools\ghidra_geometry_collision_wave387_probe_test.py` | PASS. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS after refreshing `ExportFunctionQualitySnapshot.java`: `6027` functions, `1439` commented functions, `4588` commentless functions, `1935` undefined signatures, and `1909` `param_N` signatures. |
| Actual Ghidra project backup | PASS: copied `BEA.gpr` and `BEA.rep` to `G:\GhidraBackups\BEA_20260513_193642_post_wave387_geometry_collision_verified`; verified `19` files, `153947015` bytes, `HashDiffCount=0`. |

The current broad comment-backed proxy is `1439/6027 = 23.87%`. The stricter comment-plus-no-`undefined`-or-`param_N` proxy is `1377/6027 = 22.85%`. These values are telemetry only, not completion milestones.

## Not Proven

- Runtime collision behavior.
- Exact source identity for every helper body.
- Concrete `FVector` / `Vec3` / AABB / mesh-collision layouts.
- Concrete local variable names/types for every decompiler temporary.
- BEA launch, game patching, or runtime proof.
- Rebuild parity or gameplay behavior.
