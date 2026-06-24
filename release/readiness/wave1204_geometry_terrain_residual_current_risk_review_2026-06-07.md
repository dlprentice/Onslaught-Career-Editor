# Wave1204 Geometry/Terrain Residual Current-Risk Review Readiness

Status: complete static read-back evidence with tag-only normalization
Date: 2026-06-07
Scope: `wave1204-geometry-terrain-residual-current-risk-review`

Wave1204 measured anchor: unique-address accounting governs active current-risk progress. Wave1204 (`wave1204-geometry-terrain-residual-current-risk-review`) accounts for `9 Geometry/Terrain residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and one tag-only normalization at `0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight`. Dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=11 missing=0 bad=0`, then `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=11 missing=0 bad=0`, then final dry updated=0 skipped=1. No rename, no signature change, no comment change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1071/1179 = 90.84%`; the legacy additive counter is deprecated (`1102/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 108; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `15 xref rows`, `1058 instruction rows`, and `9 decompile rows`. Verified backup: `G:\GhidraBackups\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified`. Active measurement files include `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime terrain behavior, runtime collision behavior, runtime shadow behavior, runtime triangulation behavior, exact layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Representative anchors:

| Function | Evidence |
| --- | --- |
| `ShadowHeightfield__AnyBoundsCornerAboveSampledHeight` | Post-readback tags include `wave1204-geometry-terrain-residual-current-risk-review` and `wave1204-readback-verified`. |
| `Geometry__RaySphereEntryDistance` | Retail distance helper preserved as static geometry evidence. |
| `Geometry__DistanceOutsideAabb` | Retail AABB distance helper preserved as static collision/geometry evidence. |
| `CHeightField__Load` | Heightfield load path with `CHeightField__InitColorGradient`, `0x13dc`, `0xa2000`, and 9x9 tile-block evidence. |
| `CHeightField__Constructor` | Global `MAP` constructor wrapper and reset path evidence. |
| `Triangulate__SplitTriangleAtPointAndLegalizeEdges` | Triangle split plus legalizing edge flips. |
| `Triangulate__TryFlipSharedEdgeForQuality` | Shared-edge quality flip helper. |
| `Triangulate__FindTriangleByDirectedEdge` | Directed-edge triangle lookup and rotation helper. |
| `Triangulate__RelaxMeshByEdgeFlips` | Ten-pass mesh relaxation loop. |

What this proves:

- The 9 target rows exist in the saved Ghidra project with the expected names and signatures.
- `0x00402dd0` now has the missing Wave1204 static/current-risk tag set.
- Fresh post exports produced 9 metadata rows, 9 tag rows, 15 xref rows, 1058 instruction rows, and 9 decompile rows.
- The verified backup has 19 files, 176425863 bytes, `DiffCount=0`, and `HashDiffCount=0`.

What remains separate proof:

- Runtime terrain behavior.
- Runtime collision behavior.
- Runtime shadow behavior.
- Runtime triangulation behavior.
- Exact layout and exact source identity.
- BEA patching behavior, rebuild parity, and no-noticeable-difference parity.

Probe token anchor: Wave1204; wave1204-geometry-terrain-residual-current-risk-review; 1071/1179 = 90.84%; 9 Geometry/Terrain residual current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 108; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; updated=1 skipped=0; tags_added=11; final dry updated=0 skipped=1; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; ShadowHeightfield__AnyBoundsCornerAboveSampledHeight; Geometry__RaySphereEntryDistance; Geometry__DistanceOutsideAabb; CHeightField__Load; CHeightField__Constructor; Triangulate__SplitTriangleAtPointAndLegalizeEdges; Triangulate__TryFlipSharedEdgeForQuality; Triangulate__FindTriangleByDirectedEdge; Triangulate__RelaxMeshByEdgeFlips; 0 / 0 / 0; 6411/6411 = 100.00%; 15 xref rows; 1058 instruction rows; 9 decompile rows; G:\GhidraBackups\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; legacy additive counter is deprecated; 1102/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; rebuild-grade static contracts; no noticeable difference; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence.
