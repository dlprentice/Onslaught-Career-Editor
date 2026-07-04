# Ghidra CMesh Tail Lookup Wave444 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave444 hardened the next CMesh queue-head/tail lookup cluster after fresh metadata/decompile/xref/instruction/tag review. The pass corrected three stale or generic names to mesh-level owners, preserved the existing names that matched the evidence, hardened signatures and proof-boundary comments, and tagged the confirmed lookup/polybucket/random-vertex targets.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004aa3f0` | `void __thiscall CMeshPart__CopyPrimaryAxesToOutVec3Triplet(void * this, void * out_vec3)` | Copies part offsets `+0x00/+0x10/+0x20` into an output vec3 triplet; callers include `CMesh__Load`, recursive root-transform application, and sound-position update. |
| `0x004aa410` | `void * __cdecl CMesh__FindTextureByNameSuffixHint(void * texture_record)` | Validates texture record name pointer at `+0x08`, warns on null, and dispatches suffix-hint texture lookup modes `4`, `2`, and `1`. |
| `0x004aa5a0` | `int __thiscall CMesh__GetPartField40ByFlatIndex(void * this, int flat_part_index)` | Chained part-table lookup subtracts part counts and returns selected part field `+0x40` or `0`. |
| `0x004aa5e0` | `int __thiscall CMesh__FindEntryByInclusiveRangeTable(void * this, int lookup_value)` | Scans 12-byte range records for inclusive start/end bounds and follows chained tables until hit or exhaustion. |
| `0x004aa630` | `int __thiscall CMesh__FindAnimationIndexByName(void * this, char * animation_name)` | Corrected from generic `FindAnimationIndex`; scans 0x24-byte animation records by `stricmp` and returns record `+0x10` or `-1`. |
| `0x004aa680` | `void * __thiscall CMesh__FindEntryByPartId(void * this, int part_id)` | Corrected from stale CMCMech owner wording; generic mesh 0x24-byte entry lookup by record `+0x10` part/id. |
| `0x004aa6e0` | `void * __cdecl CMesh__FindOrCreate(char * mesh_name, void * load_context)` | Scans `g_pMeshList`, increments refcount `+0x170` on hit, otherwise allocates/initializes/loads a 0x174-byte CMesh and tears down on failure. |
| `0x004aa7e0` | `float __thiscall CMesh__FindEntryValueByTypeId(void * this, int type_id, int * out_index)` | Scans typed records, writes the matching index to `out_index`, returns float field `+0x20`, and uses default float `0x005d856c` on miss. |
| `0x004aa820` | `int __thiscall CMesh__FindPartField40ByNameAndOwner(void * this, char * part_name, void * owner_part)` | Corrected from stale CMCMech owner wording; matches part name and owner pointer and returns field `+0x40` or `0`. |
| `0x004aa900` | `void __thiscall CMesh__CreatePolyBucketsForAllParts(void * this)` | Iterates part pointer table `+0x160` for count `+0x15c` and calls `CMeshPart__CreatePolyBucket`. |
| `0x004aa940` | `void * __thiscall CMesh__GetRandomVertexWeightedByPartArea(void * this, void * out_vec3, void * out_part)` | Selects a static mesh part and returns `out_vec3` after `CMesh__GetRandomVertexFromPolyBucket`, with area-weighted sampling for larger meshes and bounded random fallback for smaller meshes. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMeshWave444.java` dry/apply/verify | PASS | Dry reported `skipped=11`, `would_rename=3`; apply reported `updated=11`, `renamed=3`, `missing=0`, `bad=0`; verify dry reported `skipped=11`, `would_rename=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `11` metadata rows, `11` tag rows, `200` xref rows, `3091` instruction rows, and `11` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_cmesh_wave444_probe.py tools\ghidra_cmesh_wave444_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmesh_wave444_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `cmd.exe /c npm run test:ghidra-cmesh-wave444` | PASS | Focused probe returned `PASS` for all `11` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1895` commented functions, `4160` commentless functions, `1749` undefined signatures, and `1724` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1895`
- Commentless function objects: `4160`
- `undefined` signatures: `1749`
- Signatures still using `param_N`: `1724`

Telemetry-only proxies are comment-backed `1895/6055 = 31.30%` and strict clean-signature `1833/6055 = 30.27%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `[maintainer-local-ghidra-backup-root]\BEA_20260516-092018_post_wave444_cmesh_tail_verified`. The backup comparison reported `19` files, `156240775` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime mesh loading/render behavior; concrete `CMesh`/`CMeshPart` layouts; exact field names/types; exact source method identity; BEA launch behavior; game patching; or source-to-retail rebuild parity.
