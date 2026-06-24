# Ghidra MeshCollisionVolume Swept-Sphere Query Review Wave939 Readiness

Status: complete static read-back evidence with one comment-only normalization
Date: 2026-05-28
Scope: `meshcollisionvolume-swept-sphere-query-review-wave939`

Wave939 re-reviewed the MeshCollisionVolume swept-sphere query dispatch layer selected from the Wave911 risk-ranked continuation queue after a Composer 2.5 adversarial consult and fresh Ghidra exports. The cluster ties the vtable slot-2 wrapper, vtable slot-3 swept-sphere dispatch body, bounds test, mesh-part test, contact-normal/plane resolver, SetPartBounds refresh path, and the Wave913 triangle/geometry context.

The fresh evidence found no rename, signature, or function-boundary correction. It did identify one bounded comment overclaim at `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds`: the old Wave535 comment said "24 direction-table triangle faces"; live instruction evidence supports a 24-entry direction-pointer table used as 8 triangle tests. Wave939 normalized that comment and added Wave939 read-back tags. No executable bytes were changed.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x004ac6e0` | `CMeshCollisionVolume__VFunc_03_004ac6e0` | Vtable slot 3 at `0x005d95d4`; scans mode-specific mesh parts, calls `CMeshCollisionVolume__SetPartBounds`, dispatches either bounds or mesh-part swept-sphere tests, accumulates up to six contact candidates, and calls `CMeshCollisionVolume__ResolveContactNormalAndPlane`. |
| `0x004abe50` | `CMeshCollisionVolume__VFunc_02_004abe50` | Vtable slot 2 at `0x005d95d0`; builds a local `0x005d95e8` record from the source sphere/line-style record and forwards through this object's vtable slot `+0x0c`. |
| `0x004ac000` | `CMeshCollisionVolume__InitDirectionLookupTable` | Lazily populates the global direction lookup table at `0x00704bf8..0x00704c54` and sets initialization flag `0x00704cc8`. |
| `0x004ac140` | `CMeshCollisionVolume__TestSweptSphereAgainstBounds` | Comment normalized: bounds swept-sphere helper uses a 24-entry direction-pointer table as 8 triangle tests when `contact_record+0xcc` is set, otherwise falls back to `Geometry__DistanceOutsideAabb`. |
| `0x004ac4a0` | `CMeshCollisionVolume__TestSweptSphereAgainstMeshPart` | Iterates mesh-part triangle candidates and calls `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`. |
| `0x004acf30` | `CMeshCollisionVolume__ResolveContactNormalAndPlane` | Resolves contact normal/plane output after candidate selection; exact contact-record layout remains unproven. |
| `0x004ad600` | `CMeshCollisionVolume__SetPartBounds` | Lazily allocates/refreshes per-part 0x74-byte collision bounds records, with standard and interpolated-pose paths. |

Context anchors:

- `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `0x00478c20 Geometry__IntersectSegmentTriangleAndStoreHit`, `0x00479200 Geometry__SelectClosestPointOnTriangleEdges`, and `0x00477ba0 Vec3__MagnitudeSquared` preserve the Wave913 triangle/geometry context.
- `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` preserves the adjacent line/segment query vtable slot 4 context.
- `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord` remains the intentionally bounded hidden-EBX/caller-frame contact-output tail reached by a conditional jump from `0x004acd22`, not a proven clean source-level callable boundary.
- `0x004262e0 CMeshCollisionVolume__VFunc_05_004262e0` and `0x0043fe20 CCylinder__ResolveCollisionVFunc02` remain adjacent vtable/delegate/cylinder context only.

Fresh read-back evidence:

- Pre-mutation primary exports: 7 metadata rows, 7 tag rows, 14 xref rows, 1747 instruction rows, and 7 decompile rows.
- Context exports: 10 metadata rows, 10 tag rows, 18 xref rows, 2743 instruction rows, and 10 decompile rows.
- `ApplyMeshCollisionVolumeSweptSphereQueryWave939.java dry`: `updated=0 would_update=1 skipped=0 missing=0 bad=0`.
- `ApplyMeshCollisionVolumeSweptSphereQueryWave939.java apply`: `updated=1 would_update=0 skipped=0 missing=0 bad=0`.
- `ApplyMeshCollisionVolumeSweptSphereQueryWave939.java final dry`: `updated=0 would_update=0 skipped=1 missing=0 bad=0`.
- Post exports: 7 metadata rows, 7 tag rows, 14 xref rows, 1747 instruction rows, and 7 decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260528-024426_post_wave939_meshcollisionvolume_swept_sphere_query_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave939: `173/1408 = 12.29%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave939; `meshcollisionvolume-swept-sphere-query-review-wave939`; `0x004abe50 CMeshCollisionVolume__VFunc_02_004abe50`; `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0`; `0x004ac140 CMeshCollisionVolume__TestSweptSphereAgainstBounds`; `0x004ac4a0 CMeshCollisionVolume__TestSweptSphereAgainstMeshPart`; `0x004acf30 CMeshCollisionVolume__ResolveContactNormalAndPlane`; `0x004ad600 CMeshCollisionVolume__SetPartBounds`; `0x00478510 CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`; `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`; `24-entry direction-pointer table as 8 triangle tests`; `173/1408 = 12.29%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-024426_post_wave939_meshcollisionvolume_swept_sphere_query_review_verified`; comment-only mutation.

What this proves:

- The selected MeshCollisionVolume swept-sphere dispatch rows remain present in the saved Ghidra project with coherent names, signatures, xrefs, tags, instructions, and decompile outputs.
- The saved `0x004ac140` comment now matches the observed direction-table loop boundary more tightly.
- The static join from vtable wrapper through swept-sphere bounds/mesh-part tests, triangle core, contact resolve, and SetPartBounds remains coherent.

What remains unproven:

- Exact source-body identity.
- Complete MeshCollisionVolume, mesh-part, bounds, motion, and contact-record layouts.
- Runtime collision correctness.
- Runtime swept-sphere behavior.
- BEA patching behavior.
- Rebuild parity.
