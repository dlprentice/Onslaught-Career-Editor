# Ghidra Collision / Geometry Wave446 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra function-boundary/name/signature/comment/tag correction

## Summary

Wave446 continued the MeshCollisionVolume collision cluster after Wave445. The pass recovered two missing `CMeshCollisionVolume` vtable target function boundaries, hardened six existing collision/geometry helper signatures, and corrected the stale `Geometry__NoOpHook` label at `0x00477ba0` to `Vec3__MagnitudeSquared`.

The `Vec3__MagnitudeSquared` correction removes the stale void/no-op interpretation from the swept-sphere triangle helper; post-apply decompile now shows `Vec3__MagnitudeSquared(sweep_delta)` instead of `Geometry__NoOpHook()` plus an `extraout_ST0` artifact.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004262e0` | `int __thiscall CMeshCollisionVolume__VFunc_05_004262e0(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)` | Vtable slot 5 forwarder from `0x005d95dc`; forwards four stack arguments plus the current object into the delegate object's vtable slot `+0x04`, then returns with `RET 0x10`. |
| `0x00426320` | `int __thiscall CSphere__VFunc_01_00426320(void * this, void * query_arg0, void * query_arg1, void * delegate_object, void * query_arg3)` | CSphere-adjacent forwarder reached from the `0x005d95e8` / `0x005d95fc` table region; forwards to delegate vtable slot `+0x0c` and returns with `RET 0x10`. |
| `0x00477ba0` | `double __fastcall Vec3__MagnitudeSquared(void * this)` | Renamed from stale `Geometry__NoOpHook`; computes `x*x + y*y + z*z` from the three floats at `ECX`, `ECX+4`, and `ECX+8`. |
| `0x00478160` | `int __cdecl Geometry__ClipSegmentAgainstAABB3D(float * start_x, float * start_y, float * start_z, float * end_x, float * end_y, float * end_z, float * bounds_minmax)` | Clips six scalar endpoint pointers against a six-float AABB ordered `minX, minY, maxX, maxY, minZ, maxZ`, updating endpoints or rejecting overlapping outcodes. |
| `0x00478510` | `int __cdecl CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * sphere_start, void * sweep_delta, float sphere_radius, void * contact_record)` | Tests a swept sphere against one triangle, uses `Vec3__MagnitudeSquared`, `Geometry__RaySphereEntryDistance`, and closest-edge fallback, then writes contact point/normal/time/status fields. |
| `0x00478c20` | `int __cdecl Geometry__IntersectSegmentTriangleAndStoreHit(void * triangle_vertex0, void * triangle_vertex1, void * triangle_vertex2, void * segment_start, void * segment_end, void * contact_record)` | Intersects a segment with a triangle plane, checks time in `[0,1]`, applies three edge-side tests, and stores nearer hit details when a contact record is supplied. |
| `0x004ac6e0` | `int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)` | Newly recovered vtable slot 3 body from `0x005d95d4`; scans mode-specific mesh parts, refreshes per-part bounds, dispatches swept-sphere tests, accumulates contact candidates, and updates motion/contact records. |
| `0x004ad830` | `int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)` | Newly recovered vtable slot 4 body from `0x005d95d8`; scans line-triangle bucket candidates, calls `Geometry__IntersectSegmentTriangleAndStoreHit`, and transforms the winning hit/normal back through the part basis. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `CreateFunctionsFromAddressList.java` dry/apply | PASS | Dry reported `would_create=2`; apply reported `created=2`, `renamed=2`, `failed=0` for `0x004ac6e0` and `0x004ad830`. |
| Headless `ApplyCollisionGeometryWave446.java` dry/apply/verify | PASS | Initial dry reported `skipped=8`, `would_rename=1`; apply reported `updated=8`, `renamed=1`, `missing=0`, `bad=0`; verify dry reported `skipped=8`, `would_rename=0`. |
| Post-apply metadata/tag/xref/decompile read-back | PASS | Verified `8` metadata rows, `8` tag rows, `16` xref rows, and `8` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_collision_geometry_wave446_probe.py tools\ghidra_collision_geometry_wave446_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_collision_geometry_wave446_probe_test.py` | PASS | Focused tests passed `5/5`. |
| `cmd.exe /c npm run test:ghidra-collision-geometry-wave446` | PASS | Focused probe returned `PASS` for all `8` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6057` total functions, `1912` commented functions, `4145` commentless functions, `1746` undefined signatures, and `1719` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6057`
- Commented function objects: `1912`
- Commentless function objects: `4145`
- `undefined` signatures: `1746`
- Signatures still using `param_N`: `1719`

Telemetry-only proxies are comment-backed `1912/6057 = 31.57%` and strict clean-signature `1849/6057 = 30.53%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `[maintainer-local-ghidra-backup-root]\BEA_20260516-101600_post_wave446_collision_geometry_verified`. The backup comparison reported `19` files, `156339079` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime collision behavior; concrete vector, AABB, mesh-part, or contact-record layouts; exact source method identity; exact owner split for the CSphere-adjacent table region; BEA launch behavior; game patching; or source-to-retail rebuild parity.
