# Ghidra Wave913 mesh/collision review (2026-05-27)

Status: read-only static review
Date: 2026-05-27
Branch: `main`
Tag: `mesh-collision-review-wave913`

## Scope

Wave913 reviewed a mesh/collision tranche from the Wave911 focused correction queue.

Reviewed targets:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x00479020` | `CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | Reviewed; no mutation |
| `0x00479200` | `Geometry__SelectClosestPointOnTriangleEdges` | Reviewed; no mutation |
| `0x004ad830` | `CMeshCollisionVolume__VFunc_04_004ad830` | Reviewed; no mutation |
| `0x00478c20` | `Geometry__IntersectSegmentTriangleAndStoreHit` | Reviewed; no mutation |
| `0x00478510` | `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore` | Reviewed; no mutation |
| `0x00477ba0` | `Vec3__MagnitudeSquared` | Reviewed; no mutation |

## Evidence

Private artifacts:

```text
subagents/ghidra-static-reaudit/wave913-mesh-collision-review/addresses.txt
subagents/ghidra-static-reaudit/wave913-mesh-collision-review/metadata.tsv
subagents/ghidra-static-reaudit/wave913-mesh-collision-review/tags.tsv
subagents/ghidra-static-reaudit/wave913-mesh-collision-review/instructions.tsv
subagents/ghidra-static-reaudit/wave913-mesh-collision-review/decompile/
```

Read-back result:

```text
metadata: 6/6 OK
tags: 6/6 OK
instructions: 1813 rows
decompile: 6/6 OK
```

## Review Result

The saved names/signatures/comments remain appropriate for the currently available evidence. This tranche has strong static retail evidence from prior Wave387/Wave446 work, but no tracked source body in `references/Onslaught/` closed the exact source-identity gap.

No Ghidra mutation was performed in Wave913.

## Backup

Read-only post-wave backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260527-102522_post_wave913_mesh_collision_review_verified
files=19
bytes=173247367
```

## Truth boundary

This review confirms static Ghidra coherence for the selected mesh/collision helpers. It does not prove runtime collision behavior, concrete vector/contact/AABB layouts, BEA patch behavior, or rebuild parity.

## Next

Continue Wave914 with either:

- another focused collision tranche (`CMeshCollisionVolume` bounds/contact helpers), or
- a different top Wave911 correction cluster with stronger source parity signals.
