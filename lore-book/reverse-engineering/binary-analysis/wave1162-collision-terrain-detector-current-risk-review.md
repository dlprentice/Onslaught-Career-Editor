# Wave1162 Collision / Terrain Detector Current-Risk Review

Status: complete static read-only evidence validated
Date: 2026-06-06
Tag: `wave1162-collision-terrain-detector-current-risk-review`

Wave1162 re-read `14 collision/terrain detector current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. The pass is read-only: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags` | Collision-seeking infantry-bloke filter helper; checks tracked thing flags, mount-state compatibility, then falls back to `CCollisionSeekingRound__CheckCollisionFlags`. |
| `0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism` | Signed edge/plane dot-test helper called by `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`. |
| `0x0047ea20 CHeightField__GetHeightSamplePacked16` | Packed 16-bit heightfield sampler used by world occupancy, landscape, patch, squad, air-guide, and ground-unit clearance paths. |
| `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange` | Heightfield grid extent and min/max height recompute helper called by battleline mesh/update paths. |
| `0x00490e20 CHeightField__FreeOwnedBuffers_Thunk` | Map/heightfield destructor thunk that tail-calls `CHeightField__FreeOwnedBuffers_24_1028`. |
| `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0` | CMeshCollisionVolume slot 3 scans mode-specific mesh parts, refreshes bounds, runs swept-sphere tests, and accumulates contact records. |
| `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` | CMeshCollisionVolume slot 4 builds segment endpoints, scans line-triangle buckets, and writes the winning hit/normal path when present. |
| `0x00480a30 CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions` | High-level collision detector neighbor-sector scanner called from `CCollisionSeekingRound__InitWithSound`. |
| `0x00480c90 CHLCollisionDetector__HandleCollisionEnter` | Enter-event callback for candidate collision components and immediate/scheduled follow-up handling. |
| `0x00480db0 CHLCollisionDetector__HandleCollisionExit` | Exit-event callback that applies mutual filters and dispatches or clears collision-pair state. |
| `0x00480e10 CHLCollisionDetector__TraverseQuadNodeAndDispatchCollisions` | Recursive quad/map-who traversal and candidate collision-pair dispatch helper. |
| `0x00480ed0 CHLCollisionDetector__DispatchCollisionEventForPair` | Pair dispatcher that estimates delay, calls enter handling, or schedules event `2000`. |
| `0x00481060 CHLCollisionDetector__ProcessMapWhoCollisionSweep` | Map/who sector sweep called by `CCollisionSeekingRound__ProcessMapWhoCollisionSweep`. |
| `0x004812d0 CHLCollisionDetector__HandleScheduledCollisionEvent` | Scheduled collision event handler for event number `2000`; reuses event data pointer as candidate collision component. |

Fresh read-back evidence:

- Pre exports: `14` metadata rows, `14` tag rows, `41` xref rows, `2104` instruction rows, and `14` decompile rows.
- Xref mix: `37` `UNCONDITIONAL_CALL` rows and `4` `DATA` rows.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting advances to `547/1179 = 46.40%`; remaining active focused work: `632`.
- Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed collision, terrain, mesh-volume, and HLCollisionDetector rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- Wave1162 extends the Wave1161 projectile/collision-seeking map into HLCollisionDetector sector traversal, scheduled collision events, terrain heightfield sampling, mesh-volume vfunc slots, and triangle-prism collision tests.
- No saved Ghidra correction was needed for this tranche.

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

Probe token anchor: Wave1162; wave1162-collision-terrain-detector-current-risk-review; 547/1179 = 46.40%; 14 collision/terrain detector current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 632; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 41 xref rows; 2104 instruction rows; CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags; CMeshCollisionVolume__IsDirectionInsideTrianglePrism; CHeightField__GetHeightSamplePacked16; CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions; CHLCollisionDetector__ProcessMapWhoCollisionSweep; CHLCollisionDetector__HandleScheduledCollisionEvent; G:\GhidraBackups\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
