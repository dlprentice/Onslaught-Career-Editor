# Ghidra World Occupancy Bitplanes Wave819 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `world-occupancy-bitplanes-wave819`

Wave819 world occupancy bitplanes saved comments, tags, and signatures for six adjacent CWorld occupancy/load helpers from `0x004bc2d0 CWorld__ClearDynamicOccupancySet` through `0x004be170 CWorld__ReadOccupancyChunkHeader`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004bc2d0 CWorld__ClearDynamicOccupancySet` | `void __cdecl CWorld__ClearDynamicOccupancySet(void)` | Tail-jumps into `0x004e5c60 CSPtrSet__Clear` for dynamic world-occupancy set `DAT_00809588`; direct xref `0x0050d683 CWorld__ReleaseSubObject_AndMaybeFree`. |
| `0x004bc8d0 CWorld__ClearOccupancyBitsUsingHeightBands` | `void __cdecl CWorld__ClearOccupancyBitsUsingHeightBands(void)` | `CWorld__LoadWorld` callsite `0x0050d456`; scans the heightfield, samples `CHeightField__GetHeightSamplePacked16` and `CMonitor__SampleHeightfieldNormalAtXY`, and clears DAT_00855290/94/98 occupancy-bitplane bits through `CWorld__SetOrClearOccupancyBit`. |
| `0x004bcbf0 CWorld__ApplyStaticMaskToOccupancyBitplanes` | `void __cdecl CWorld__ApplyStaticMaskToOccupancyBitplanes(void)` | `CWorld__LoadWorld` callsite `0x0050d473`; scans static mask `DAT_00807580`, clears matching packed bits in `DAT_00855290`, `DAT_00855294`, and `DAT_00855298`, then sets `DAT_00809598 = 1`. |
| `0x004bcd60 CWorld__RebuildOccupancyGridFromDynamicSet` | `void __cdecl CWorld__RebuildOccupancyGridFromDynamicSet(void)` | `CWorld__LoadWorld` callsite `0x0050d47a`; resets static occupancy mask, iterates dynamic objects from `DAT_00809588` through `CSPtrSet__First`/`CSPtrSet__Next`, samples height/volume evidence, and clears occupancy mask/bitplane neighbors. |
| `0x004bdff0 CWorld__SkipLegacyOccupancyChunk` | `void __thiscall CWorld__SkipLegacyOccupancyChunk(void * this, void * mem_buffer)` | `CWorld__LoadWorld` callsites `0x0050d331`, `0x0050d33d`, and `0x0050d349` load ECX from `DAT_00855290`, `DAT_00855294`, or `DAT_00855298` and push the `CDXMemBuffer` pointer; the body skips mode `1` (`0x8000` one-byte records) or mode `2` (`0x2000` one-byte records), then exits with `RET 0x4`. |
| `0x004be170 CWorld__ReadOccupancyChunkHeader` | `void __cdecl CWorld__ReadOccupancyChunkHeader(void * mem_buffer)` | `CWorld__LoadWorld` callsite `0x0050d386` pushes the `CDXMemBuffer` pointer and cleans one stack argument with `ADD ESP, 0x4`; the body reads five 4-byte fields through `CDXMemBuffer__Read`. |

Read-back evidence:

- `ApplyWorldOccupancyBitplanesWave819.java dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=6 missing=0 bad=0`
- `ApplyWorldOccupancyBitplanesWave819.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=6 missing=0 bad=0`
- `ApplyWorldOccupancyBitplanesWave819.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 6 metadata rows, 6 tag rows, 8 xref rows, 1326 target instruction rows, 204 callsite instruction rows, 8 helper metadata rows, and 6 decompile rows.
- Queue after Wave819: 6098 total, 5612 commented, 486 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5612/6098 = 92.03%`, strict clean-signature proxy `5612/6098 = 92.03%`.
- Next raw commentless row is `0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-164330_post_wave819_world_occupancy_bitplanes_verified`, 19 files, 171412359 bytes, `DiffCount=0`.

What this proves:

- The six target function rows exist in the saved Ghidra project.
- The saved signatures, comments, and tags include `world-occupancy-bitplanes-wave819` and `wave819-readback-verified`.
- The observed helper behavior is static retail Ghidra evidence tied to `CWorld__LoadWorld`/release xrefs, instruction/decompile exports, helper metadata, and read-back logs.

What remains unproven:

- Exact global field names/layouts.
- Exact legacy occupancy chunk schema.
- Runtime world-load/pathing behavior.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
