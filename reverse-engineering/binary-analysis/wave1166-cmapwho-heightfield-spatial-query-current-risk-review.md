# Wave1166 CMapWho / CHeightField Spatial-Query Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1166-cmapwho-heightfield-spatial-query-current-risk-review`

Wave1166 re-read twenty active Wave1108 focused rows in the terrain/spatial-query substrate: three CHeightField rows and seventeen CMapWho / CMapWhoEntry rows. The saved comments, signatures, and tags still match the prior Wave426 HeightField/MAP evidence and Wave428/Wave429/Wave1034 MapWho spatial-query evidence.

| Address | Name | Static role |
| --- | --- | --- |
| `0x00491060` | `CHeightField__DeserializeMapAndInitResources` | MAP deserialize/resource-init row. |
| `0x00490e30` | `CHeightField__BuildCellMinMaxHeightTable` | Heightfield min/max quick-collision table builder. |
| `0x00490a40` | `CHeightField__TraceLineAgainstHeightfield` | Heightfield line trace row used by world line-hit context. |
| `0x00491930` | `CMapWho__Destroy` | MapWho level-grid teardown. |
| `0x004919b0` | `CMapWho__Init` | MapWho level-grid initialization. |
| `0x00491c50` | `CMapWho__GetLevelForRadius` | Radius-to-level selector. |
| `0x00491cd0` | `CMapWho__AddEntry` | Entry list insertion. |
| `0x00491d20` | `CMapWho__RemoveEntry` | Entry list removal. |
| `0x00491ea0` | `CMapWho__GetFirstEntryWithinRadius` | Radius broad-phase query start. |
| `0x00492020` | `CMapWho__GetNextEntryWithinRadius` | Radius broad-phase iterator. |
| `0x00492110` | `CMapWho__GetFirstEntryWithinLine` | Line broad-phase query start. |
| `0x004922f0` | `CMapWho__SetupLineLevel` | Line-query level setup. |
| `0x004924b0` | `CMapWho__AdvanceLineIterator` | Line iterator advance. |
| `0x004925a0` | `CMapWho__GetNextEntryWithinLine` | Line broad-phase iterator. |
| `0x00492670` | `CMapWho__WorldToSector` | World-position to sector conversion. |
| `0x004926e0` | `CMapWho__Sort` | Sector list validation/sort pass. |
| `0x00492ba0` | `CMapWhoEntry__SetPosition` | Entry position/owner/radius setup. |
| `0x00492c70` | `CMapWhoEntry__RemoveFromMap` | Entry removal wrapper. |
| `0x00492c90` | `CMapWhoEntry__GetOwner` | Entry-owner pointer helper. |
| `0x00492ca0` | `CMapWhoEntry__UpdatePosition` | Entry position refresh. |

Evidence counts: `20` metadata rows, `20` tag rows, `109` xref rows, `1651` instruction rows, and `20` decompile rows. Verified backup: `G:\GhidraBackups\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified` (`19` files, `176032647` bytes, `DiffCount=0`, `HashDiffCount=0`).

Wave1166 is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. Codex read-only consult used for candidate/accounting sanity; Codex root performed the live exports, backup verification, and final judgment.

System-map note: this is the static bridge between terrain heightfield load/minmax/line trace, world line tracing, MapWho radius and line broad-phase iteration, HLCollisionDetector sweeps, targeting, repair/spawn candidate checks, entry ownership/update/remove lifecycle, and static-shadow/render/debug consumers. It should be treated as a spatial-query substrate map, not as runtime collision or line-of-sight proof.

Current accounting: `624/1179 = 52.93%` Wave1108 current focused reviewed, remaining active focused work: 555, current risk candidates: 6166, current focused candidates: 1178, live regenerated current focused candidates: 1178, focused threshold `15`, not Wave911 reconstruction. Static quality remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.

Boundary: static Ghidra coherence only. Runtime spatial-query behavior, terrain collision, line-of-sight, auto-aim, HLCollision behavior, debug rendering, exact `CMapWho` / `CMapWhoEntry` / `CHeightField` / sector/minmax layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. The `mapwho.cpp` and `HeightField.cpp` evidence here is binary/debug-path led; source-body parity remains limited.

Probe token anchor: Wave1166; wave1166-cmapwho-heightfield-spatial-query-current-risk-review; 624/1179 = 52.93%; 20 CMapWho / CHeightField spatial-query current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 555; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 109 xref rows; 1651 instruction rows; CHeightField__TraceLineAgainstHeightfield; CMapWho__GetFirstEntryWithinRadius; CMapWho__GetFirstEntryWithinLine; CMapWho__WorldToSector; CMapWhoEntry__SetPosition; CMapWhoEntry__GetOwner; CWorld__FindFirstThingToHitLine; CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions; G:\GhidraBackups\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
