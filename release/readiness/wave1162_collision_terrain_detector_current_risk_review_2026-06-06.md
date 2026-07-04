# Wave1162 Collision / Terrain Detector Current-Risk Review Readiness Note

Status: complete static read-only evidence validated
Date: 2026-06-06
Scope: `wave1162-collision-terrain-detector-current-risk-review`

Wave1162 re-read `14 collision/terrain detector current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra metadata, tag, xref, instruction, and decompile exports showed the saved names, signatures, comments, and tags remain coherent. No Ghidra mutation was performed.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | Checks collision-seeking infantry-bloke mount-state/filter context before falling back to `CCollisionSeekingRound__CheckCollisionFlags`. |
| `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | Triangle-prism signed plane/dot-test helper called from mesh-volume swept-sphere triangle testing. |
| `0x0047ea20 CHeightField__GetHeightSamplePacked16` | Packed height sampler used by world occupancy, landscape, patch, squad, air-guide, and ground-unit clearance paths. |
| `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange` | Heightfield extent and min/max recompute helper tied to battleline mesh/update xrefs. |
| `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0` | Mesh-volume slot 3 swept-sphere/contact candidate path. |
| `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` | Mesh-volume slot 4 segment/line-triangle bucket path. |
| `0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions` | High-level collision detector neighbor-sector scanner. |
| `0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair` | Pair dispatcher that enters immediately or schedules event `2000`. |
| `0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep` | Map/who sector sweep called by the collision-seeking round wrapper. |
| `0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent` | Scheduled collision event handler for event `2000`. |

Read-back evidence:

- Pre exports: `14` metadata rows, `14` tag rows, `41` xref rows, `2104` instruction rows, and `14` decompile rows.
- Queue closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Active current-risk accounting advances to `547/1179 = 46.40%`.
- Current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `632`; current risk candidates: `6166`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- The collision/terrain tranche extends Wave1161's projectile/collision-seeking map into HLCollisionDetector sector traversal, scheduled collision events, terrain heightfield sampling, mesh-volume vfunc slots, and triangle-prism collision tests.
- No Ghidra rename, signature, comment, tag, function-boundary, or executable-byte mutation was needed in this wave.

What remains separate:

- Runtime collision behavior.
- Runtime terrain/heightfield behavior.
- Runtime projectile behavior.
- Exact `CHLCollisionDetector`, `CHeightField`, `CMeshCollisionVolume`, and collision record layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1162; wave1162-collision-terrain-detector-current-risk-review; 547/1179 = 46.40%; 14 collision/terrain detector current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 632; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 41 xref rows; 2104 instruction rows; CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags; CMeshCollisionVolume__IsDirectionInsideTrianglePrism; CHeightField__GetHeightSamplePacked16; CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions; CHLCollisionDetector__ProcessMapWhoCollisionSweep; CHLCollisionDetector__HandleScheduledCollisionEvent; [maintainer-local-ghidra-backup-root]\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
