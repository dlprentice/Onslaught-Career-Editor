# Wave1166 CMapWho / CHeightField Spatial-Query Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Scope: `wave1166-cmapwho-heightfield-spatial-query-current-risk-review`

Wave1166 accounts for `20 CMapWho / CHeightField spatial-query current-risk rows` from the active `wave1108-current-risk-rank` denominator. Fresh Ghidra read-back verified the saved Wave426 HeightField/MAP treatment plus the Wave428/Wave429/Wave1034 MapWho spatial-query treatment for terrain min/max tables, heightfield line tracing, MapWho radius/line broad-phase iterators, sector conversion/sort, and entry position/owner lifecycle helpers.

The pass is read-only. It made no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00491060 CHeightField__DeserializeMapAndInitResources` | Wave426 MAP deserialize/resource-init row; one fresh xref row. |
| `0x00490e30 CHeightField__BuildCellMinMaxHeightTable` | Wave426 min/max-table row; one fresh xref row. |
| `0x00490a40 CHeightField__TraceLineAgainstHeightfield` | Wave426 line-trace row; `15` fresh xref rows, including `CWorld__FindFirstThingToHitLine` context. |
| `0x00491ea0 CMapWho__GetFirstEntryWithinRadius` | Wave428 radius-query row; `16` fresh xref rows across targeting, repair/spawn, monitor, and projectile caller families. |
| `0x00492110 CMapWho__GetFirstEntryWithinLine` | Wave429 line-query row; line-query entry point used by world trace context. |
| `0x00492670 CMapWho__WorldToSector` | Wave429 sector-conversion row; `5` fresh xref rows. |
| `0x00492ba0 CMapWhoEntry__SetPosition` | Wave429 entry-position row. |
| `0x00492c90 CMapWhoEntry__GetOwner` | Wave429 entry-owner row; `30` fresh xref rows. |

Evidence:

- Fresh metadata rows: `20`
- Fresh tag rows: `20`
- Fresh xref rows: `109`
- Fresh instruction rows: `1651`
- Fresh decompile rows: `20`
- Representative xref callers include `CStaticShadows__BuildShadowMaps`, `CCarverAI__CheckNearbyEnemies`, `CWorld__FindFirstThingToHitLine`, `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `CRepairPadAI__VFunc_11_UpdateDockCandidateReader`, `CRound__FindNearbyHostileWithinProjectileRadius`, and `CSpawnerThng__IsSpawnPositionClear`.
- Verified backup: `G:\GhidraBackups\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified`, `19` files, `176032647` bytes, `DiffCount=0`, `HashDiffCount=0`.

Accounting after Wave1166:

- Static function-quality closure remains `6411/6411 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt remains `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.
- Wave911 top-500 remains `500/500 = 100.00%`.
- Wave1108 current focused accounting is `624/1179 = 52.93%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 555.
- Focused threshold `15`; not Wave911 reconstruction.

Boundary:

This proves static Ghidra coherence for the saved terrain-heightfield and MapWho spatial-query rows only. Runtime spatial-query behavior, terrain collision, line-of-sight, auto-aim, HLCollision behavior, debug rendering, exact `CMapWho` / `CMapWhoEntry` / `CHeightField` / sector/minmax layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. The `mapwho.cpp` and `HeightField.cpp` evidence here is binary/debug-path led; source-body parity remains limited.

Probe token anchor: Wave1166; wave1166-cmapwho-heightfield-spatial-query-current-risk-review; 624/1179 = 52.93%; 20 CMapWho / CHeightField spatial-query current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 555; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 109 xref rows; 1651 instruction rows; CHeightField__TraceLineAgainstHeightfield; CMapWho__GetFirstEntryWithinRadius; CMapWho__GetFirstEntryWithinLine; CMapWho__WorldToSector; CMapWhoEntry__SetPosition; CMapWhoEntry__GetOwner; CWorld__FindFirstThingToHitLine; CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions; G:\GhidraBackups\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
