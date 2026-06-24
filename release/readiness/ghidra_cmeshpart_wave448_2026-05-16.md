# Ghidra CMeshPart Wave448 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag hardening

## Summary

Wave448 continued the CMeshPart queue by hardening eight existing transform, cache, accessor, damaged-variant, and animation-frame helper functions. The pass preserved current function boundaries and names, while correcting stack-cleanup signatures and adding proof-boundary comments/tags.

No installed Steam game files were touched. This wave only saved Ghidra metadata in the working Ghidra project and records public-safe summaries, scripts, and checks. Raw decompile exports remain under ignored `subagents/` evidence.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004b0800` | `void __thiscall CMeshPart__ApplyRootTransformRecursive(void * this, int parent_transform_dword00, int parent_transform_dword01, int parent_transform_dword02, int parent_transform_dword03, int parent_transform_dword04, int parent_transform_dword05, int parent_transform_dword06, int parent_transform_dword07, int parent_transform_dword08, int parent_transform_dword09, int parent_transform_dword10, int parent_transform_dword11, float origin_x, float origin_y, float origin_z, float origin_w, void * frame_override_part)` | `ret 0x44` matches a 12-dword transform block, four origin/offset floats, and an optional frame-override part pointer; the helper recurses through child/material pointers and refreshes cached transform/position blocks. |
| `0x004b0c00` | `void * __thiscall CMeshPart__GetBasisX(void * this, void * out_vec3)` | Writes part offsets `+0x04`, `+0x14`, and `+0x24` into the output vec3 and returns that pointer. |
| `0x004b0c20` | `void * __thiscall CMeshPart__GetBasisY(void * this, void * out_vec3)` | Writes part offsets `+0x08`, `+0x18`, and `+0x28` into the output vec3 and returns that pointer. |
| `0x004b0c40` | `int __thiscall CMeshPart__FindNearestVertexIndex(void * this, float query_x, float query_y, float query_z, float query_w_unused)` | Scans first-frame PVertices through `+0x84`, compares up to `+0xac` vertices against the query position, and keeps the fourth stack float for the observed `ret 0x10` cleanup. |
| `0x004b1a40` | `void __fastcall CMeshPart__CacheFrameData(void * this)` | Chooses cached frame count at `+0x118`, tracks identity/zero-position cache shortcuts at `+0x120/+0x11c`, allocates optional caches at `+0x104/+0x108`, and calls `CMCMech__BuildInterpolatedPoseAndAnchor`. |
| `0x004b1d30` | `void __fastcall CMeshPart__LinkDamagedPartVariantsBySuffix(void * this)` | Scans sibling mesh parts for names sharing the current prefix and `_damaged` suffix, parses optional damage numbers, chains variants through `+0x9c/+0xa0`, and marks linked variants at `+0xa4`. |
| `0x004b1eb0` | `void __thiscall CMeshPart__RebuildPerVertexNormalsAndTangents(void * this, int update_primary_normal)` | Walks DVertices and triangles below the observed `10001` guard, accumulates normalized face vectors from the first PVertex frame, optionally updates primary normals, and writes fallback axes when needed. |
| `0x004b24d0` | `int __thiscall CMeshPart__ResolveWrappedFrameIndexAndLerp(void * this, float frame_delta, int frame_table_index, void * out_lerp, void * frame_adjuster)` | Uses parent mesh frame-table data and frame delta to compute a wrapped animation frame index, optionally routes through `frame_adjuster` vfunc `+0x14`, and writes fractional lerp output. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMeshPartWave448.java` dry/apply/verify | PASS | Dry reported `updated=0`, `skipped=8`, `missing=0`, `bad=0`; apply reported `updated=8`, `skipped=0`, `missing=0`, `bad=0`; verify dry reported `skipped=8`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `8` metadata rows, `8` tag rows, `18` xref rows, focused return-cleanup instruction evidence, and `8` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_cmeshpart_wave448_probe.py tools\ghidra_cmeshpart_wave448_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmeshpart_wave448_probe_test.py` | PASS | Focused tests passed `5/5`. |
| `cmd.exe /c npm run test:ghidra-cmeshpart-wave448` | PASS | Focused probe returned `PASS` for all `8` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6057` total functions, `1929` commented functions, `4128` commentless functions, `1741` undefined signatures, and `1707` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6057`
- Commented function objects: `1929`
- Commentless function objects: `4128`
- `undefined` signatures: `1741`
- Signatures still using `param_N`: `1707`

Telemetry-only proxies are comment-backed `1929/6057 = 31.85%` and strict clean-signature `1866/6057 = 30.81%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `G:\GhidraBackups\BEA_20260516-110512_post_wave448_cmeshpart_transform_cache_verified`. The backup comparison reported `19` files, `156404615` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime animation, rendering, damaged-part swapping, or mesh cache behavior; exact source method identities; concrete `CMeshPart`, transform, cache, frame-table, vertex, or triangle layouts; exact field names/types; BEA launch behavior; game patching; or source-to-retail rebuild parity.
