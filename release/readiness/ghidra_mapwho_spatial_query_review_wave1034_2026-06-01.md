# Ghidra MapWho Spatial Query Review Wave1034

Status: complete read-only static review
Date: 2026-06-01
Scope: `mapwho-spatial-query-review-wave1034`

Wave1034 re-read the full 25-function `CMapWho` / `CMapWhoEntry` spatial-query cluster originally hardened by Wave428 and Wave429. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Range | Saved state confirmed by Wave1034 | Fresh evidence |
| --- | --- | --- |
| `0x00491900` through `0x00492020` | Radius-query, init/destroy, add/remove, shared iterator, and sector-bounds helpers keep their Wave428 names/signatures/comments/tags. | Fresh exports verified level-array construction, entry list insert/remove, radius-level setup, shared iterator helpers, and radius-query caller xrefs. |
| `0x00492110` through `0x00492ca0` | Line-query, world-to-sector, sort, debug draw, entry position, invalidate/remove/owner/update helpers keep their Wave429 names/signatures/comments/tags. | Fresh exports verified `RET 0x20` line-query ABI, `RET 0xc` world/position helpers, `RET 0x8` debug-sector helper, and entry-owner `entry - 0x0c` evidence. |

Representative callsite/xref evidence:

- Radius query callers include `CBattleEngine__HandleAutoAim`, `CMonitor__Process`, `CSpawnerThng__IsSpawnPositionClear`, `CUnitAI__IsCachedAnchorPointValid`, `CRepairPadAI__VFunc_11_UpdateDockCandidateReader`, `CAirGuide__AcquireNearestTargetReader`, `CInfantryGuide__SelectNearestTargetReader`, `CMechGuide__SelectNearestHostileTargetReader`, `ProjectileBurstCallerBoundary_004f4920`, and `CRound__FindNearbyHostileWithinProjectileRadius`.
- Shared iterator callers include `CVBufTexture__RenderDynamicUnitPass`, `CDXTrees__BuildTreeGeometry`, and `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`.
- Line-query callers remain `CWorld__FindFirstThingToHitLine` for first/next line entries.
- Debug draw remains routed from `CDXEngine__Render` through `CMapWho__DebugDraw` and `CMapWho__DebugDrawSector` into `CThing__RenderDebugVolumeOverlay`.
- Entry position/update callers include `CThing__Init`, `CDXEngine__UpdateWrappedThingPositionsAndDistance`, `CActor__Move`, and `CAtmospheric__Process`.

Evidence counts:

- Fresh exports: `25` metadata rows, `25` tag rows, `119` xref rows, `1538` body-instruction rows, and `25` decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress after Wave1034: `660/1408 = 46.88%`.
- Expanded static surface progress after Wave1034: `889/1493 = 59.54%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected MapWho rows still have coherent saved names, signatures, comments, tags, xrefs, instruction bodies, and decompile output.
- The Wave428/Wave429 owner and ABI corrections still match current saved Ghidra read-back.
- The cluster is a central static bridge for broad-phase radius queries, line queries, map/who entry tracking, debug-sector rendering, and dynamic-object spatial lookup.

What remains unproven:

- Runtime spatial-query behavior.
- Runtime collision/render/tree/AI targeting behavior.
- Concrete `CMapWho` / `CMapWhoEntry` layouts beyond observed offsets.
- Exact local variable names/types and source-body identity. The retail debug path names `C:\dev\ONSLAUGHT2\mapwho.cpp`, but `mapwho.cpp` is absent from the current Stuart source snapshot.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1034; mapwho-spatial-query-review-wave1034; 0x00491900 CMapWhoEntry__Init; 0x00491d80 CMapWho__SetIteratorFromSectorHead; 0x00491ea0 CMapWho__GetFirstEntryWithinRadius; 0x00492110 CMapWho__GetFirstEntryWithinLine; 0x00492670 CMapWho__WorldToSector; 0x00492860 CMapWho__DebugDrawSector; 0x00492ba0 CMapWhoEntry__SetPosition; 0x00492c90 CMapWhoEntry__GetOwner; 660/1408 = 46.88%; 889/1493 = 59.54%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-054844_post_wave1034_mapwho_spatial_query_review_verified; no mutation.
