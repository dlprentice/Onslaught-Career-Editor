# Ghidra CMeshPart Wave449 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag hardening

## Summary

Wave449 continued the CMeshPart queue by hardening eight existing load, deserialize, material, optimize, clone, merge, and random-vertex helper functions. The pass preserved current function boundaries and names, while correcting stack-cleanup signatures and adding proof-boundary comments/tags.

No installed Steam game files were touched. This wave only saved Ghidra metadata in the working Ghidra project and records public-safe summaries, scripts, and checks. Raw decompile exports remain under ignored `subagents/` evidence.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004af470` | `void __thiscall CMeshPart__LoadVerticesAndTriangles(void * this, void * mem_buffer, void * part_table_entry, void * first_part_record, int part_index_limit, int unused_legacy_arg)` | Loads non-skinned DVertex/PVertex/triangle stream data, negates loaded Z components, clamps material/part indices against `part_index_limit`, handles split DVertex remapping, and ends with `ret 0x14`. The `0x004a8f5c` caller preserves an earlier `push 0`, so the unused legacy arg is kept for stack cleanup. |
| `0x004afbb0` | `void __thiscall CMeshPart__LoadVerticesWithBones(void * this, void * mem_buffer, void * parent_mesh, int unused_arg3, int part_index_limit, int unused_arg5, int influence_count, int format_tag)` | Loads skinned vertex/triangle data, resolves indices through `parent_mesh`, processes `influence_count` records per DVertex, handles `format_tag`-specific fields, normalizes/selects bone slots, and ends with `ret 0x1c`. |
| `0x004b25d0` | `void __thiscall CMesh__GetRandomVertexFromPolyBucket(void * this, void * out_vec4)` | Uses polybucket field `+0x100`, calls `CPolyBucket__GetRandomTriangle`, chooses one of three triangle vertices with `Random__NextLCGAbs % 3`, scales/offsets the short coordinates, and `ret 0x4` corrects the stale phantom third argument. |
| `0x004b27a0` | `void * __cdecl CMeshPart__LoadFromStream(void * chunk_reader, void * mesh_part, void * parent_mesh)` | Deserializes a 0x13c part from a chunk reader, back-links parent mesh, allocates optional geometry/cache/bone structures, calls `CMeshPart__LoadMaterial`, optionally loads `CPolyBucket`, and returns `mesh_part`. |
| `0x004b3180` | `void * __cdecl CMeshPart__LoadMaterial(void * chunk_reader, void * existing_material)` | Advances the chunk reader, allocates a 0x28-byte material when needed, reads two 0x10-byte blocks plus trailing dwords at `+0x20/+0x24`, and returns the material pointer. |
| `0x004b31f0` | `void __fastcall CMeshPart__OptimizePolygons(void * this)` | Runs when PVertex count at `+0xac` exceeds 31, allocates scratch arrays, uses threshold `0.2` or `0.3` above 300 vertices, compares triangle neighborhoods/normals, rewrites triangle vertex indices, and reports removed vertices/polys. |
| `0x004b3b70` | `void * __fastcall CMeshPart__Clone(void * this)` | Deep-clones a 0x13c CMeshPart after `CMeshPart__Init`, copying transforms, bounds, material/name/link metadata, geometry arrays, remapped triangle pointers, and optional keyframe/FOV/texcoord/bone/weight/slot data. |
| `0x004b4250` | `void __thiscall CMeshPart__Merge(void * this, void * source_part)` | Merges `source_part` into this part, allocates combined geometry arrays, copies existing geometry, builds/interpolates pose transforms, transforms source geometry through cofactor/determinant matrix math, remaps source triangle pointers, and updates counts/pointers. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMeshPartWave449.java` dry/apply/verify | PASS | Dry reported `updated=0`, `skipped=8`, `missing=0`, `bad=0`; apply reported `updated=8`, `skipped=0`, `missing=0`, `bad=0`; verify dry reported `skipped=8`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/callsite/decompile read-back | PASS | Verified `8` metadata rows, `8` tag rows, `11` xref rows, focused return-cleanup and callsite instruction evidence, and `8` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_cmeshpart_wave449_probe.py tools\ghidra_cmeshpart_wave449_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmeshpart_wave449_probe_test.py` | PASS | Focused tests passed `5/5`. |
| `cmd.exe /c npm run test:ghidra-cmeshpart-wave449` | PASS | Focused probe returned `PASS` for all `8` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6057` total functions, `1937` commented functions, `4120` commentless functions, `1734` undefined signatures, and `1706` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6057`
- Commented function objects: `1937`
- Commentless function objects: `4120`
- `undefined` signatures: `1734`
- Signatures still using `param_N`: `1706`

Telemetry-only proxies are comment-backed `1937/6057 = 31.98%` and strict clean-signature `1874/6057 = 30.94%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `G:\GhidraBackups\BEA_20260516-113946_post_wave449_cmeshpart_load_optimize_verified`. The backup comparison reported `19` files, `156502919` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime mesh loading, skinning, rendering, material behavior, polygon optimization effects, clone/merge ownership, exact source method identities, concrete `CMesh`, `CMeshPart`, DVertex, PVertex, material, or polybucket layouts; exact field names/types; BEA launch behavior; game patching; or source-to-retail rebuild parity.
