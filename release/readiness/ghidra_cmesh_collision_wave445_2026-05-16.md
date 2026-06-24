# Ghidra CMesh / MeshCollisionVolume Wave445 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave445 hardened the next CMesh queue-head cluster and its MeshCollisionVolume bridge targets after fresh metadata/decompile/xref/instruction/tag review. The pass saved corrected signatures and proof-boundary comments for CMesh deserialization, runtime-id lookup, part optimization, material/resource helpers, VBuf setup, MeshCollisionVolume destructor/body setup, and part bounds setup.

`0x004acde0` remains intentionally signature-deferred: it is saved as `CMeshCollisionVolume__InitContactOutputRecord` with tags/comments, but the signature remains `undefined ... (void)` because EBX/register state is part of the observed calling convention.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004aab90` | `void * __cdecl CMesh__Deserialize(void * primary_reader, void * resource_reader)` | Allocates/initializes a 0x174-byte CMesh, reads mesh metadata/materials/emitters/parts from chunk-reader streams, can open `data\resources\meshes\m_%s.aya`, and recursively loads chained meshes. |
| `0x004ab330` | `void * __cdecl CMesh__FindByRuntimeId(int runtime_id)` | Scans `DAT_00704ad8` / `g_pMeshList` by field `+0x154` and returns the matching mesh pointer or `0`. |
| `0x004ab360` | `void __thiscall CMesh__OptimizeParts(void * this)` | Merges compatible static mesh parts, excludes Nexus/protected dependencies, rewrites child/material lists, and updates optimization counters. |
| `0x004ac0e0` | `void __thiscall CMeshCollisionVolume__dtor_base(void * this)` | Destructor body called by the scalar-deleting wrapper; frees per-part collision data at `+0x24`, clears it, and restores the base vtable. |
| `0x004acde0` | `undefined CMeshCollisionVolume__InitContactOutputRecord(void)` | Comment/tag-only hardening for the contact-output tail block; signature intentionally deferred because EBX/register state is part of the observed calling convention. |
| `0x004ad600` | `void __thiscall CMeshCollisionVolume__SetPartBounds(void * this, void * mesh, int part_index, float bounds_status)` | Lazy allocates `mesh->+0x15c * 0x74` collision entries, validates `mesh->+0x160[part_index]`, writes two 4x3 matrices plus a vec4, and stores `bounds_status` at entry `+0x70`. |
| `0x004adf90` | `void __thiscall CMesh__ReleaseEmbeddedResources(void * this)` | Releases a 0x24-byte mesh material/resource record and decrements the observed resource counters. |
| `0x004ae080` | `void __thiscall CMesh__InitSingleVertexPartDefaults(void * this)` | Initializes a single-vertex record, calls `CMeshPart__SetVertexCount(1)`, and writes default 1.0f values. |
| `0x004ae0d0` | `void __thiscall CMesh__InitPartVBufTextureFormats(void * this)` | Resolves `CVBufTexture__GetOrCreate`, stores the texture at record `+0x04`, and applies observed VB/IB format constants. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMeshWave445.java` dry/apply/verify | PASS | Dry reported `skipped=9`, `would_rename=1`; apply reported `updated=9`, `renamed=1`, `missing=0`, `bad=0`; verify dry reported `skipped=9`, `would_rename=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `9` metadata rows, `9` tag rows, `27` xref rows, `3069` instruction rows, and `9` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_cmesh_wave445_probe.py tools\ghidra_cmesh_wave445_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmesh_wave445_probe_test.py` | PASS | Focused tests passed `5/5`. |
| `cmd.exe /c npm run test:ghidra-cmesh-wave445` | PASS | Focused probe returned `PASS` for all `9` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1904` commented functions, `4151` commentless functions, `1746` undefined signatures, and `1719` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1904`
- Commentless function objects: `4151`
- `undefined` signatures: `1746`
- Signatures still using `param_N`: `1719`

Telemetry-only proxies are comment-backed `1904/6055 = 31.45%` and strict clean-signature `1841/6055 = 30.40%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `G:\GhidraBackups\BEA_20260516-094724_post_wave445_cmesh_collision_verified`. The backup comparison reported `19` files, `156273543` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime mesh loading/render/collision behavior; concrete `CMesh`/`CMeshCollisionVolume` layouts; exact matrix/vector/contact-record layouts; exact field names/types; exact source method identity; BEA launch behavior; game patching; or source-to-retail rebuild parity.
