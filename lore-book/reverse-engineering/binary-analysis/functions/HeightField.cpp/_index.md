# HeightField.cpp Function Mappings

Wave1166 current-risk update: Wave1166 (`wave1166-cmapwho-heightfield-spatial-query-current-risk-review`) re-read `20 CMapWho / CHeightField spatial-query current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. The HeightField rows are `CHeightField__DeserializeMapAndInitResources`, `CHeightField__BuildCellMinMaxHeightTable`, and `CHeightField__TraceLineAgainstHeightfield`; they bridge resource-backed heightfield initialization, cell min/max table construction, and line trace consumers such as `CWorld__FindFirstThingToHitLine` and `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`. Accounting is `624/1179 = 52.93%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 555; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; `0 / 0 / 0`; `6411/6411 = 100.00%`; `109 xref rows`; `1651 instruction rows`; focused threshold `15`; not Wave911 reconstruction. Static anchors include `CHeightField__TraceLineAgainstHeightfield`, `CMapWho__GetFirstEntryWithinRadius`, `CMapWho__GetFirstEntryWithinLine`, `CMapWho__WorldToSector`, `CMapWhoEntry__SetPosition`, and `CMapWhoEntry__GetOwner`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-043614_post_wave1166_cmapwho_heightfield_spatial_query_current_risk_review_verified`. Runtime spatial-query behavior, terrain collision, line-of-sight, auto-aim, HLCollision behavior, exact CHeightField/minmax layouts, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Wave1162 current-risk update: Wave1162 (`wave1162-collision-terrain-detector-current-risk-review`) re-read HeightField terrain sampling and destructor-thunk context with fresh Ghidra evidence. It covers `CHeightField__GetHeightSamplePacked16`, `CHeightField__RecomputeGridExtentsAndHeightRange`, and `CHeightField__FreeOwnedBuffers_Thunk` alongside collision detector and mesh-volume rows. Accounting advances to `547/1179 = 46.40%` with `14 collision/terrain detector current-risk rows`, current focused candidates: 1178, live regenerated current focused candidates: 1178, remaining active focused work: 632, current risk candidates: 6166, fresh Ghidra export, read-only review, no mutation, `0 / 0 / 0`, `6411/6411 = 100.00%`, `41 xref rows`, and `2104 instruction rows`. Anchors include `CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags`, `CHeightField__GetHeightSamplePacked16`, `CMeshCollisionVolume__IsDirectionInsideTrianglePrism`, `CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions`, `CHLCollisionDetector__ProcessMapWhoCollisionSweep`, and `CHLCollisionDetector__HandleScheduledCollisionEvent`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-021413_post_wave1162_collision_terrain_detector_current_risk_review_verified`; tag `wave1162-collision-terrain-detector-current-risk-review`; source denominator `wave1108-current-risk-rank`; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Runtime terrain/heightfield behavior, exact CHeightField layout, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

> Functions from HeightField.cpp mapped to BEA.exe binary
> Debug path: [maintainer-local-source-export-root]\HeightField.cpp (at 0x0062cbd0)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview
- **Functions Mapped:** 15
- **Status:** NEW (Dec 2025) - discovered via debug string xrefs
- **Classes:** CHeightField

## Discovery Method
Found via cross-references to debug path string at 0x0062cbd0. The CHeightField class manages terrain heightfield data, including loading from level resources and initializing color gradient tables for rendering.

## Wave935 World Footprint Heightfield Review (2026-05-28)

Wave935 static re-audit (`world-footprint-heightfield-review-wave935`) re-reviewed `0x0047ea20 CHeightField__GetHeightSamplePacked16` beside CWorld footprint occupancy context and found no mutation was needed. Fresh exports tie the packed-height sampler to `0x00490e30 CHeightField__BuildCellMinMaxHeightTable`, `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes`, and `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet`; context read-back also verified `0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY`, `0x004bdf70 CWorld__SetOrClearOccupancyBit`, and `0x004bd440 CWorld__ClearCrossNeighborsInBitplane`. Wave911 focused re-audit progress after Wave935 is `148/1408 = 10.51%`; export-contract function-quality closure remains `6113/6113 = 100.00%`. Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`. This remains static Ghidra evidence only; runtime terrain sampling, runtime occupancy/pathing/static-shadow behavior, exact layouts, and rebuild parity remain unproven.

Probe token anchor: Wave935; `world-footprint-heightfield-review-wave935`; `0x0047ea20 CHeightField__GetHeightSamplePacked16`; `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes`; `0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY`; `0x004bdf70 CWorld__SetOrClearOccupancyBit`; `0x004bd440 CWorld__ClearCrossNeighborsInBitplane`; `0x00490e30 CHeightField__BuildCellMinMaxHeightTable`; `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet`; `148/1408 = 10.51%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`; no mutation.

## Wave1009 Geometry / Guide / Heightfield Spine Review (2026-05-31)

Wave1009 static re-audit (`geometry-guide-heightfield-spine-review-wave1009`) re-read `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange` and `0x0047eb80 CStaticShadows__SampleShadowHeightBilinear` while recovering ten DATA-backed static-shadow caller boundaries. Queue closure is `6233/6233 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`. Runtime terrain/static-shadow behavior, exact source method identity, concrete heightfield/static-shadow layouts, BEA patching, and rebuild parity remain separate proof.

## Wave1131 HeightField Current-Risk Review (2026-06-05)

Wave1131 static current-risk review (`wave1131-heightfield-current-risk-review`) re-read and tag-normalized `7 rows` from the HeightField MAP current-risk cluster with fresh Ghidra export evidence and tag-only normalization. Covered anchors are `0x0047e870 CHeightField__ResetCoreBuffersAndFlags`, `0x0047e8a0 CHeightField__FreeOwnedBuffers_24_1028`, `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange`, `0x00490e20 CHeightField__FreeOwnedBuffers_Thunk`, `0x00490f10 CHeightField__InitAndClearMapLoadFlags`, `0x00490f40 CHeightField__ShutdownAndDestroyMixerMap`, and `0x00490f50 CHeightField__TraceMapLoadRequestAndCheckLoadedFlags`. Current focused accounting is `168/1179 = 14.25%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1011; static debt remains `0 / 0 / 0`. Dry/apply/final-dry added `40 tags` with no rename, signature, comment, function-boundary, executable-byte, installed-game, or runtime-file mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`; previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`. This is static Ghidra evidence only; runtime terrain behavior, runtime map-load behavior, exact layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x0047f750 | CHeightField__Load | NAMED | [View](CHeightField__Load.md) |
| 0x0047e870 | CHeightField__ResetCoreBuffersAndFlags | SIGNED | Wave426 corrected stale `CUnitAI` ownership; clears core MAP/heightfield buffers and flags. |
| 0x0047e8a0 | CHeightField__FreeOwnedBuffers_24_1028 | SIGNED | Wave426 corrected stale `CUnitAI` ownership; frees owned buffers at `+0x24` and `+0x1028`. |
| 0x0047e8e0 | CHeightField__InitColorGradient | SIGNED | [View](CHeightField__InitColorGradient.md) |
| 0x0047ea20 | CHeightField__GetHeightSamplePacked16 | SIGNED | Wave426 corrected provisional `CWorld` ownership; reads packed height data through `+0x1028`. |
| 0x0047eb00 | CHeightField__SampleInterpolatedHeight | SIGNED | Wave394 hardened the saved `void * this, uint x_packed, uint z_packed` signature/comment for the 9x9-tile bilinear height sampler. |
| 0x0047ef20 | CHeightField__RecomputeGridExtentsAndHeightRange | SIGNED | [View](CHeightField__RecomputeGridExtentsAndHeightRange.md) |
| 0x00490a40 | CHeightField__TraceLineAgainstHeightfield | SIGNED | Wave426 corrected stale `CStaticShadows` ownership; traces a line against heightfield min/max cells and writes hit output. |
| 0x00490e10 | CHeightField__Constructor | SIGNED | Wave426 corrected stale `CUnitAI` ownership; global MAP constructor wrapper. |
| 0x00490e20 | CHeightField__FreeOwnedBuffers_Thunk | SIGNED | Wave426 names the global MAP destructor thunk that tail-calls the owned-buffer free helper. |
| 0x00490e30 | CHeightField__BuildCellMinMaxHeightTable | SIGNED | Wave426 corrected stale `CGame` ownership; builds the 9x9 min/max table rooted at `+0x13dc`. |
| 0x00490f10 | CHeightField__InitAndClearMapLoadFlags | SIGNED | Wave426 corrected stale `CGame` ownership; source `CGame::Init` / `MAP.Init` context plus map-load flag writes. |
| 0x00490f40 | CHeightField__ShutdownAndDestroyMixerMap | SIGNED | Wave426 corrected stale `CUnitAI` ownership; MAP shutdown path and `CMixerMap__Destroy` tail-call. |
| 0x00490f50 | CHeightField__TraceMapLoadRequestAndCheckLoadedFlags | SIGNED | Wave426 corrected stale `CWorld` ownership; checks map-load flags for a map request. |
| 0x00491060 | CHeightField__DeserializeMapAndInitResources | SIGNED | Wave426 corrected stale `CResourceAccumulator` ownership; `CEngine__Deserialize` / `MAP.Deserialize` context with heightfield load, mixer init, and engine resource setup. |

## CHeightField Structure (Partial)

Based on decompilation analysis, the CHeightField class has these known member offsets:

| Offset | Type | Name | Notes |
|--------|------|------|-------|
| 0x0024 | void* | pUnknown1 | Freed in Load, purpose unknown |
| 0x1028 | void* | pHeightData | 0xa2000 (663,552) bytes allocated |
| 0x1030 | byte | unknown1030 | |
| 0x1038 | int | xShift | Bit shift for X dimension |
| 0x103c | int | zShift | Bit shift for Z dimension |
| 0x107c | uint | colorBase | Base color (ARGB) |
| 0x108c | uint | colorMod | Color modifier (ARGB) |
| 0x1090 | byte | unknown1090 | |
| 0x1091 | byte | unknown1091 | |
| 0x1094 | byte | unknown1094 | |
| 0x1095 | byte | unknown1095 | |
| 0x10bc | int | xSize | 1 << xShift |
| 0x10c0 | int | zSize | 1 << zShift |
| 0x10c4 | int | xMask | xSize - 1 |
| 0x10c8 | int | zMask | zSize - 1 |
| 0x10cc | int | xzMask | zMask << xShift |
| 0x10d0 | int[192] | colorGradient | 64 RGB triplets for terrain shading |
| 0x13c4 | int[3] | fogColorSrc | Source fog colors |
| 0x13d0 | int[3] | fogColorDst | Destination fog colors (copied from src) |

**Struct Size:** 0x13dc (5084) bytes - validated in Load function

## Related Strings

| Address | String | Usage |
|---------|--------|-------|
| 0x0062cbd0 | "[maintainer-local-source-export-root]\HeightField.cpp" | Memory allocation debug tag |
| 0x0062cbf4 | "Got size %d, expected %d" | Size validation error |
| 0x006319f4 | "Resource file does not match code (CHeightfield size changed)!" | Version mismatch |

## Notes
- Height data is stored as 16-bit values (shorts)
- The 0xa2000 byte allocation suggests 331,776 height samples
- Nested loops read 9x9 blocks (81 values) repeatedly
- Color gradient table uses 64 entries with RGB565-like packing
- Wave394 saved signature/comment evidence hardens `CHeightField__InitColorGradient` and `CHeightField__SampleInterpolatedHeight`; Wave396 corrected `0x0047ef20` from the older CDXBattleLine owner label to heightfield ownership and corrected the saved `CHeightField__Load` signature.
- Wave426 corrected the adjacent MAP/heightfield init/load/shutdown tranche and supersedes older `CUnitAI`, `CGame`, `CWorld`, `CStaticShadows`, and `CResourceAccumulator` owner labels for the checked helpers from `0x0047e870` through `0x00491060`.
- These waves do not prove concrete class layouts, exact local types, or runtime terrain behavior.
- Related to CResourceAccumulator for level loading

## Related
- Source: Not present in our `references/Onslaught/` snapshot; current mapping is binary-only via debug-path xrefs.
- Called by: Map deserialization (`CHeightField__Load`) and CDXBattleLine battle-line mesh/heightmap helpers (`CHeightField__RecomputeGridExtentsAndHeightRange`)
- Parent: [../README.md](../README.md)
