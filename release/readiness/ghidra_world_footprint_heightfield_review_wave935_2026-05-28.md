# Ghidra World Footprint Heightfield Review Wave935 Readiness

Status: complete read-only static read-back evidence
Date: 2026-05-28
Scope: `world-footprint-heightfield-review-wave935`

Wave935 re-reviewed the terrain-height sampling and world-footprint occupancy join after the Wave911 risk-ranked continuation queue surfaced `0x0047ea20 CHeightField__GetHeightSamplePacked16` and `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes` as high-value remaining candidates. Fresh Ghidra exports matched the saved Wave426, Wave457, and Wave819 evidence chain, so this wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x0047ea20` | `CHeightField__GetHeightSamplePacked16` | `uint __fastcall` packed X/Z height sample; reads the height buffer through `this+0x1028`, branches around the `0x200` and `0xa1ffe` edge cases, and is called by heightfield min/max, world occupancy, landscape vertex, ground-clearance, and squad-support paths. |
| `0x004bd5c0` | `CWorld__RasterizeFootprintIntoOccupancyBitplanes` | `void __cdecl` five-argument footprint rasterizer; clamps world bounds to `0..511`, samples height through `CHeightField__GetHeightSamplePacked16`, samples normals through `CMonitor__SampleHeightfieldNormalAtXY`, clears unsafe occupancy bits through `CWorld__SetOrClearOccupancyBit` and `CWorld__ClearCrossNeighborsInBitplane`, and optionally rebuilds tracked-unit static shadows. |

Context anchors:

- `0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY` supplies terrain normals used by the footprint rasterizer and many movement/camera/round paths.
- `0x004bdf70 CWorld__SetOrClearOccupancyBit` and `0x004bd440 CWorld__ClearCrossNeighborsInBitplane` are the packed-bit helpers used by the rasterizer and dynamic occupancy rebuild.
- `0x00490e30 CHeightField__BuildCellMinMaxHeightTable` calls the packed height sampler during MAP post-load min/max table construction.
- `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet` is the Wave819 dynamic-set rebuild context that also uses the occupancy bit helpers and height evidence.

Fresh read-back evidence:

- Primary exports: 2 metadata rows, 2 tag rows, 12 xref rows, 422 instruction rows, and 2 decompile rows.
- Context exports: 5 metadata rows, 5 tag rows, 110 xref rows, 905 instruction rows, and 5 decompile rows.
- Primary xrefs confirm calls to `0x0047ea20 CHeightField__GetHeightSamplePacked16` from `CHeightField__BuildCellMinMaxHeightTable`, `CWorld__ClearOccupancyBitsUsingHeightBands`, `CWorld__RebuildOccupancyGridFromDynamicSet`, `CWorld__RasterizeFootprintIntoOccupancyBitplanes`, `CDXLandscape__BuildVertexBuffer`, `CDXPatch__RebuildHeightGridVertexBuffer`, `CGroundUnit__UpdateLinkedEffectsByHeightClearance`, `CAirGuide__UpdateGroundClearanceCache`, and `CSquadNormal__IsValidLinkedSupportForTarget`.
- Primary xrefs confirm calls to `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes` from `CWorld__RemoveUnitFromOccupancyGrid` and `CWorld__AddUnitToOccupancyGridAndRebuildShadows`.
- Context xrefs confirm `0x004bd88d CWorld__RasterizeFootprintIntoOccupancyBitplanes -> CMonitor__SampleHeightfieldNormalAtXY`, `0x004bd7b7 CWorld__RasterizeFootprintIntoOccupancyBitplanes -> CWorld__SetOrClearOccupancyBit`, `0x004bd93a CWorld__RasterizeFootprintIntoOccupancyBitplanes -> CWorld__ClearCrossNeighborsInBitplane`, `0x0046d244 CGame__PostLoadProcess -> CHeightField__BuildCellMinMaxHeightTable`, and `0x0050d47a CWorld__LoadWorld -> CWorld__RebuildOccupancyGridFromDynamicSet`.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave935: `148/1408 = 10.51%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave935; `world-footprint-heightfield-review-wave935`; `0x0047ea20 CHeightField__GetHeightSamplePacked16`; `0x004bd5c0 CWorld__RasterizeFootprintIntoOccupancyBitplanes`; `0x0047ec60 CMonitor__SampleHeightfieldNormalAtXY`; `0x004bdf70 CWorld__SetOrClearOccupancyBit`; `0x004bd440 CWorld__ClearCrossNeighborsInBitplane`; `0x00490e30 CHeightField__BuildCellMinMaxHeightTable`; `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet`; `148/1408 = 10.51%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified`; no mutation.

What this proves:

- The terrain packed-height sampler, world footprint rasterizer, and five context helpers remain present in the saved Ghidra project with the expected names, signatures, comments, and tags.
- The fresh xrefs preserve the existing static chain from MAP post-load min/max sampling through dynamic/object footprint occupancy bitplanes.
- The saved owner boundary still favors `CHeightField` for the packed height sampler and `CWorld` for the occupancy rasterizer.

What remains unproven:

- Exact source-body identity.
- Complete CHeightField, CWorld, occupancy-bitplane, or dynamic-object layouts.
- Runtime terrain sampling behavior.
- Runtime occupancy/pathing/static-shadow behavior.
- BEA patching behavior.
- Rebuild parity.
