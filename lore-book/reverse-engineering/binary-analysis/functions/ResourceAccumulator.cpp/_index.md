# ResourceAccumulator.cpp - Function Mapping

Source file: `[maintainer-local-source-export-root]\ResourceAccumulator.cpp`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`ResourceAccumulator` builds retail resource archive paths and loads chunked `.aya` resource files through `CChunkReader`. Wave490 hardened the two known ResourceAccumulator-owned functions from callsite, decompile, xref, instruction, tag, and read-back evidence. Wave551 corrected the `VSDS` chunk helper at `0x005042f0` to `CVertexShader__DeserializeAll`, so that shader-table deserialize logic now lives on the VertexShader page while this page records the dispatch relationship. This page is static retail-binary documentation only; runtime loading behavior, concrete resource/global layouts, exact source-body identity, and rebuild parity remain open.

Wave852 PC platform/resource tail (`pc-platform-resource-tail-wave852`, `wave852-readback-verified`) adds the adjacent resource-file dispatch edge to `0x00515b10 PCPlatform__DeserializeFontsAndAssets`. `CResourceAccumulator__ReadResourceFile` is the sole exported xref to the row; saved static evidence shows the callee freeing/rebuilding PC font slots, warning `Warning : deserializing font twice!`, allocating CDXBitmapFont-like objects, and calling `CDXBitmapFont__Deserialize` on the chunk reader. Probe token anchor: `Wave852 PC platform/resource tail`; `0x00515b10 PCPlatform__DeserializeFontsAndAssets`; `CResourceAccumulator__ReadResourceFile`; `CDXBitmapFont__Deserialize`; `5736/6098 = 94.06%`; `0x005168d0 CPCSoundManager__dtor`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified`. Exact serialized font/resource chunk schema, runtime loading behavior, BEA patching, and rebuild parity remain deferred.

## Functions Found

| Address | Name | Status |
|---------|------|--------|
| `0x0048dec0` | `CResourceAccumulator__LoadMixerDetailTexture` | Wave806 signature/comment/tag hardened |
| `0x004d6f70` | `CResourceAccumulator__GetResourceFilename` | Wave490 signature/comment/tag hardened |
| `0x004d7200` | `CResourceAccumulator__ReadResourceFile` | Wave490 signature/comment/tag hardened |
| `0x00515b10` | `PCPlatform__DeserializeFontsAndAssets` | Wave852 PC font/resource deserialize dispatch target |

## Function Details

### `CResourceAccumulator__LoadMixerDetailTexture` (`0x0048dec0`)

Saved signature:

```c
void __cdecl CResourceAccumulator__LoadMixerDetailTexture(int detail_index)
```

Wave806 raw commentless head (`raw-commentless-head-wave806`, `wave806-readback-verified`) hardened this row after static read-back evidence showed `0x00491060 CHeightField__DeserializeMapAndInitResources` pushes byte field `this+0x1094` before the call. The helper formats `mixers\detail%.2d.tga` from string `0x0062d80c`, calls `CTexture__FindTexture(local_path, DAT_00662dd4 ? 5 : 0, 0, -1, 1, 1)`, and stores the returned texture handle into global `0x0067a7d0`.

Exact anchor: `0x0048dec0 CResourceAccumulator__LoadMixerDetailTexture`.

This row connects the Wave806 `CDXLandscape__ClearMixerDetailTextureHandle` and `CDXLandscape__ReleaseMixerDetailTextureRef` corrections to the mixer-detail texture path. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`. Exact heightfield field name, texture type semantics, runtime terrain rendering/resource-loading behavior, BEA patching, and rebuild parity remain deferred.

### `CResourceAccumulator__GetResourceFilename` (`0x004d6f70`)

Saved signature:

```c
void __cdecl CResourceAccumulator__GetResourceFilename(char * out_path, int resource_id, int platform_id)
```

Observed callsites push `out_path`, `resource_id`, and `platform_id`, then clean `0x0c` bytes after the call. The internal `ReadResourceFile` call passes platform id `1`, and frontend/goodie callers also pass explicit output buffers and resource ids.

Resource id mapping observed in the decompile/string table:

| ID | Path pattern |
| ---: | --- |
| `-1` | `data\Resources\base_res_<platform>.aya` |
| `-2` | `data\Resources\Frontend_res_<platform>.aya` |
| `-3` | `data\Resources\Loading_res_<platform>.aya` or localized loading variant |
| `>= 0` | `data\Resources\%03d_res_%s.aya` |
| `< -1000` | `data\Resources\goodie_%02d_res_%s.aya` |

Platform ids currently map to `1=PC`, `2=PS2`, and `3=XBOX` in the saved comment/read-back evidence.

### `CResourceAccumulator__ReadResourceFile` (`0x004d7200`)

Saved signature:

```c
void __cdecl CResourceAccumulator__ReadResourceFile(int resource_id, void * existing_buffer, int skip_optional_chunks)
```

Observed callers push three stack arguments and clean `0x0c` bytes. Core/frontend/game/goodie paths pass ids such as `-1`, `-2`, gameplay level ids, or goodie resource ids; some callers pass a null file buffer path and others pass an existing buffer.

Key static behavior:

1. Allocates a `0x100`-byte path buffer and calls `CResourceAccumulator__GetResourceFilename(out_path, resource_id, 1)`.
2. Opens either the generated file path or an existing buffer through `CChunkReader`.
3. Dispatches recognized chunks including `MESH`, `TEXT`, `ERES`, `WRES`, `IMPS`, `VSDS`, `PLAT`, `SURF`, `SSHD`, `DMKR`, and `GDIE`.
4. Uses `skip_optional_chunks` to gate non-core chunk dispatch in the observed decompile.
5. Updates loading-console progress, logs elapsed load time, and releases temporary allocations/readers.

Representative debug/output strings:

```text
CResourceAccumulator::ReadResources took %f seconds
Unknown chunk ID %s in resource file!
Resource file does not match code (CVertexShader size changed)!
```

Wave551 dispatch note: the `VSDS` branch calls `CVertexShader__DeserializeAll(pcVar6)` at `0x004d7776`. That target now has saved signature `void __cdecl CVertexShader__DeserializeAll(void * chunk_reader)` and is documented under `functions/VertexShader.cpp/_index.md`; exact `VSDS` chunk schema and runtime shader loading behavior remain unproven.

## Wave764 ResourceAccumulator.cpp Unwind Continuation

Wave764 static read-back (`unwind-continuation-wave764`, `wave764-readback-verified`) saved comments/tags/signatures for ResourceAccumulator.cpp-adjacent compiler-generated SEH unwind cleanup callbacks at `0x005d48d0 Unwind@005d48d0` and `0x005d4900 Unwind@005d4900` as `void __cdecl Unwind@...(void)` rows. Evidence includes DATA scope-table xrefs `0x0061d134` and `0x0061d15c`, `OID__FreeObject_Callback(EBP-0x5cc)` with ResourceAccumulator.cpp debug path `0x00631b7c`, line token `0x330`, allocation/type value `0x80`, and `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on the stack-local descriptor array at `EBP-0x434`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-152957_post_wave764_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime resource loading cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave765 Boundary-Adjacent Unwind Continuation

Wave765 static read-back (`unwind-continuation-wave765`, `wave765-readback-verified`) saved comments/tags/signatures for two ResourceAccumulator/Round-boundary-adjacent cleanup callbacks: `0x005d4948 Unwind@005d4948` jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on `(*(EBP-0x10))+0xe0`, and `0x005d4956 Unwind@005d4956` jumps to `CGenericActiveReader__dtor` on `(*(EBP-0x10))+0xe8`. Scope-table DATA xrefs are `0x0061d1b4` and `0x0061d1bc`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-155528_post_wave765_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime resource cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave490 Evidence

- Apply script: `tools/ApplyResourceAccumulatorWave490.java`
- Probe: `tools/ghidra_resource_accumulator_wave490_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave490-resource-accumulator-004d6f70/`
- Dry/apply/verify summaries: dry `updated=0 skipped=2`, apply `updated=2 skipped=0`, verify dry `updated=0 skipped=2`, all with `REPORT: Save succeeded`.
- Read-back verified metadata/comments/signatures, tags, decompile exports, xrefs, instruction rows, and callsite push/cleanup evidence for both functions.
- Refreshed queue after Wave490: `6068` functions, `2215` commented, `3853` commentless, `1674` undefined signatures, and `1538` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-075159_post_wave490_resource_accumulator_verified` (`19` files, `157551495` bytes, missing `0`, extra `0`, hash differences `0`).

## Notes

- The Unwind function at `0x005d48d0` is an exception-handler frame, not a real `ResourceAccumulator` method.
- Wave426 supersedes the older `CResourceAccumulator__DeserializeMapAndInitResources` label at `0x00491060`; saved Ghidra evidence now classifies that helper as `CHeightField__DeserializeMapAndInitResources` in the `CEngine__Deserialize` / `MAP.Deserialize` context.
- This is not proof that the whole asset/resource system is fully reversed. It closes the two currently known `ResourceAccumulator.cpp` functions at the saved signature/comment level only.
