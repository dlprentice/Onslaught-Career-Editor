# Wave1204 Geometry/Terrain Residual Current-Risk Review

Status: complete static current-risk review with tag-only normalization
Date: 2026-06-07
Tag: `wave1204-geometry-terrain-residual-current-risk-review`

Wave1204 measured anchor: unique-address accounting governs active current-risk progress. Wave1204 (`wave1204-geometry-terrain-residual-current-risk-review`) accounts for `9 Geometry/Terrain residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and one tag-only normalization at `0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight`. Dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=11 missing=0 bad=0`, then `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=11 missing=0 bad=0`, then final dry updated=0 skipped=1. No rename, no signature change, no comment change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1071/1179 = 90.84%`; the legacy additive counter is deprecated (`1102/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 108; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `15 xref rows`, `1058 instruction rows`, and `9 decompile rows`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime terrain behavior, runtime collision behavior, runtime shadow behavior, runtime triangulation behavior, exact layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Reviewed Rows

| Address | Function | Static role |
| --- | --- | --- |
| `0x00402dd0` | `ShadowHeightfield__AnyBoundsCornerAboveSampledHeight` | Shadow/heightfield corner sampler using `CStaticShadows__SampleShadowHeightBilinear` plus a vfunc `+0xc0` height callback; Wave1204 added missing static/current-risk tags. |
| `0x00479630` | `Geometry__RaySphereEntryDistance` | Origin-centered sphere entry-distance helper with retail sentinel handling. |
| `0x00479770` | `Geometry__DistanceOutsideAabb` | AABB overhang distance helper. |
| `0x0047f750` | `CHeightField__Load` | Loads heightfield payload blocks, calls `CHeightField__InitColorGradient`, and records the `0x13dc` / `0xa2000` size evidence and 9x9 tile-block context. |
| `0x00490e10` | `CHeightField__Constructor` | Global `MAP` constructor wrapper and reset path through `CHeightField__ResetCoreBuffersAndFlags`. |
| `0x004f74b0` | `Triangulate__SplitTriangleAtPointAndLegalizeEdges` | Splits a triangle at a point, appends two triangle triplets, and runs quality flips. |
| `0x004f7660` | `Triangulate__TryFlipSharedEdgeForQuality` | Finds opposing directed-edge triangles, tests ratio threshold `0x005d85f8`, rewrites the shared edge, and marks mesh dirty. |
| `0x004f78c0` | `Triangulate__FindTriangleByDirectedEdge` | Rotates a matching triangle so the requested edge becomes the first two indices; absent edges return null. |
| `0x004f7940` | `Triangulate__RelaxMeshByEdgeFlips` | Runs up to ten mesh-relaxation passes through `Triangulate__TryFlipSharedEdgeForQuality`. |

## Evidence Counts

| Export | Rows |
| --- | ---: |
| Pre metadata / tags | 9 / 9 |
| Pre xrefs / instructions / decompile | 15 / 1058 / 9 |
| Post metadata / tags | 9 / 9 |
| Post xrefs / instructions / decompile | 15 / 1058 / 9 |

Backup verification: `[maintainer-local-ghidra-backup-root]\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified`, 19 files, 176425863 bytes, `DiffCount=0`, `HashDiffCount=0`.

## Next Candidate Guidance

Read-only consults recommended the destroyable-segment controller cluster and a broader engine/platform support cluster as plausible next slices. Main-agent judgment kept Wave1204 on geometry/terrain because it was already coherent, exported, backed up, and directly useful for the mesh/resource/render static contract.

Probe token anchor: Wave1204; wave1204-geometry-terrain-residual-current-risk-review; 1071/1179 = 90.84%; 9 Geometry/Terrain residual current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 108; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=1 skipped=0; tags_added=11; final dry updated=0 skipped=1; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; ShadowHeightfield__AnyBoundsCornerAboveSampledHeight; Geometry__RaySphereEntryDistance; Geometry__DistanceOutsideAabb; CHeightField__Load; CHeightField__Constructor; Triangulate__SplitTriangleAtPointAndLegalizeEdges; Triangulate__TryFlipSharedEdgeForQuality; Triangulate__FindTriangleByDirectedEdge; Triangulate__RelaxMeshByEdgeFlips; 0 / 0 / 0; 6411/6411 = 100.00%; 15 xref rows; 1058 instruction rows; 9 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; legacy additive counter is deprecated; 1102/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; rebuild-grade static contracts; no noticeable difference; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence.
