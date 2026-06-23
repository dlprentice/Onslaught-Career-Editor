# Ghidra Map/Heightfield Resource Wave426 Static Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-14
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave426 serialized headless dry/apply/read-back corrected and hardened twelve map/heightfield/resource-adjacent functions. The pass supersedes older `CUnitAI`, `CGame`, `CWorld`, `CStaticShadows`, and `CResourceAccumulator` owner labels where the retail evidence points to the global MAP/heightfield context and its terrain-load, min/max table, mixer-map, and resource-init helpers.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Previous saved state | Current saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x0047e870` | `CUnitAI__ResetWorkGrid1024AndFlags` | `void * __fastcall CHeightField__ResetCoreBuffersAndFlags(void * this)` | Clears core MAP/heightfield pointers/flags, zeroes `1024` dwords, clears `+0x1028`, and returns `this`. |
| `0x0047e8a0` | `CUnitAI__FreeOwnedObjects_24_1028` | `void __fastcall CHeightField__FreeOwnedBuffers_24_1028(void * this)` | Frees owned buffers at `+0x24` and `+0x1028` through `OID__FreeObject` and clears the slots. |
| `0x0047ea20` | `CWorld__GetHeightSamplePacked16` | `uint __fastcall CHeightField__GetHeightSamplePacked16(void * this, uint x_packed, uint z_packed)` | Reads packed 16-bit terrain height data through `+0x1028` using packed X/Z coordinates. |
| `0x00490900` | `Vec3__SubtractInPlace` with signature debt | `void __thiscall Vec3__SubtractInPlace(void * this, void * rhs_vector)` | `RET 0x4` confirms one stack vector argument and the body subtracts three float components in place. |
| `0x00490a40` | `CStaticShadows__TraceSegmentAgainstHeightfield` | `int __thiscall CHeightField__TraceLineAgainstHeightfield(void * this, void * line, void * hit_out, int stop_at_height_limit)` | `RET 0xc` confirms three stack arguments; body checks heightfield min/max cells and samples interpolated terrain height before writing hit output. |
| `0x00490e10` | `CUnitAI__InitWorkGrid1024` | `void * __fastcall CHeightField__Constructor(void * this)` | Global MAP constructor wrapper calling the reset helper and returning `this`. |
| `0x00490e20` | stale free-buffer duplicate/thunk name | `void __fastcall CHeightField__FreeOwnedBuffers_Thunk(void * this)` | Global MAP destructor thunk tail-calling `CHeightField__FreeOwnedBuffers_24_1028`. |
| `0x00490e30` | `CGame__BuildCellMinMaxHeightTable` | `void __fastcall CHeightField__BuildCellMinMaxHeightTable(void * this)` | Builds the 9x9 heightfield cell min/max table rooted at `+0x13dc` using the packed-height sample helper. |
| `0x00490f10` | `CGame__InitMapLoadStateFlags` | `int __fastcall CHeightField__InitAndClearMapLoadFlags(void * this)` | Source `CGame::Init` / `MAP.Init` context plus retail writes to map-load flag fields `+0x93e0/+0x93e4`; returns TRUE/FALSE. |
| `0x00490f40` | `CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap` | `void __fastcall CHeightField__ShutdownAndDestroyMixerMap(void * this)` | MAP shutdown context; frees owned heightfield buffers and tail-calls `CMixerMap__Destroy`. |
| `0x00490f50` | `CWorld__CanLoadMapSection` | `int __thiscall CHeightField__TraceMapLoadRequestAndCheckLoadedFlags(void * this, int map_number, int load_geometry, int load_properties)` | `RET 0xc` confirms three stack arguments; body traces `Loading map %d` and checks map-load flags. |
| `0x00491060` | `CResourceAccumulator__DeserializeMapAndInitResources` | `void __thiscall CHeightField__DeserializeMapAndInitResources(void * this, void * chunk_reader)` | `CEngine__Deserialize` / `MAP.Deserialize` context; body reads map metadata, calls `CHeightField__Load`, calls `CMixerMap__Init`, and drives engine mixer/sky/water setup. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_map_resource_wave426_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `py -3 -m py_compile tools\ghidra_map_resource_wave426_probe.py tools\ghidra_map_resource_wave426_probe_test.py` | PASS | Both focused Python files compile. |
| Pre-apply `cmd.exe /c npm run test:ghidra-map-resource-wave426` | FAIL, expected red | Probe rejected the missing post-apply artifacts before saved Ghidra apply/read-back existed. |
| Initial headless `ApplyMapResourceWave426.java` dry run | PASS | `updated=0 skipped=12 renamed=0 would_rename=11 missing=0 bad=0`, with `REPORT: Save succeeded`; dry logic made no metadata mutation. |
| Initial headless `ApplyMapResourceWave426.java` apply | PARTIAL, corrected | `updated=11 skipped=0 renamed=10 would_rename=0 missing=0 bad=1`; Ghidra had already saved an intermediate thunk name at `0x00490e20`, so the script gate stopped one target after the earlier writes had landed. |
| Corrective headless dry/apply | PASS | Final dry `updated=0 skipped=12 renamed=0 would_rename=1 missing=0 bad=0`; final apply `updated=12 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Comment-token corrective headless dry/apply | PASS | Two comment-only refreshes preserved names/signatures and ended with `updated=12 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `12` metadata rows, `12` tag rows, `38` xref rows, `3228` instruction rows, and `12` target decompile exports. |
| Post-apply `cmd.exe /c npm run test:ghidra-map-resource-wave426` | PASS | Focused probe accepted the saved names, signatures, comments, tags, stale-owner exclusions, and proof-boundary wording. |
| Headless whole-database quality snapshot | PASS | `total_functions=6043`; `commented_functions=1686`. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6043` functions, `4357` commentless functions, `1861` undefined signatures, `1795` `param_N` signatures, and zero broad uncertain/helper/wrapper debt. |
| Live Ghidra project backup | PASS | Private post-mutation backup verified `19` files, `155224967` bytes, and `HashDiffCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue now reports:

- Total function objects: `6043`
- Functions with non-empty function comments: `1686`
- Commentless function objects: `4357`
- `undefined` signatures: `1861`
- Signatures still using `param_N`: `1795`
- Comment-backed telemetry proxy: `1686/6043 = 27.90%`
- Strict clean-signature telemetry proxy: `1624/6043 = 26.87%`

These are triage proxies only. They are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime terrain behavior, runtime map-load behavior, runtime mixer/audio behavior, exact concrete `CHeightField`/MAP/CMixerMap layouts, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
