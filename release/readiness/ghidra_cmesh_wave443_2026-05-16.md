# Ghidra CMesh / CMeshPart Wave443 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra signature/comment/tag correction

## Summary

Wave443 hardened the queue-head `CMesh` cluster and one `CMeshPart` free-resource tail entry after fresh metadata/decompile/xref/instruction/tag review. The pass preserved existing names, corrected formerly weak signatures, added proof-boundary comments, and tagged the confirmed mesh/resource-management targets.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004a5020` | `void * __thiscall CMesh__Init(void * this)` | Constructor-style initializer; zeroes mesh fields, sets `+0x164`, allocates the `+0x150` buffer, and links through `DAT_00704ad8`. |
| `0x004a50b0` | `void __thiscall CMesh__FreeResourcesAndUnlink(void * this)` | Unlinks from the global mesh list, frees material/part/resource arrays, and decrements chained mesh refcount `+0x170`. |
| `0x004a51f0` | `void __thiscall CMeshPart__FreeResources(void * this)` | Public tail entry called by CMesh teardown; jumps into the shared CMeshPart owned-resource free body. |
| `0x004a5200` | `int __cdecl CMesh__InitStatic(void)` | Releases prior default texture state, allocates a 0x24-byte default entry, resolves `meshtex\default.tga`, and returns 1. |
| `0x004a5500` | `void __stdcall CMesh__MapStateNameToId(char * state_name, void * state_record)` | `ret 0x8` state-token mapper for `STAND`, `SHOOT`, `SHOOT1`, `SHOOT2`, `HOVER`, and `SHOOTWALK`; writes id at `state_record+0x10`. |
| `0x004a5670` | `void __thiscall CMesh__OptimizeTextures(void * this)` | Deduplicates 0x24-byte material entries and rewrites CMeshPart dynamic-vertex material slots. |
| `0x004a5970` | `int __thiscall CMesh__LoadByNameWithStatus(void * this, char * mesh_name, void * load_context)` | Builds `data\Meshes\` path from basename, copies basename to `this+0x24`, opens a mem-buffer, and calls `CMesh__Load`. |
| `0x004a5b70` | `int __thiscall CMesh__Load(void * this, void * mem_buffer, void * load_context)` | Main stream loader; validates version tokens, allocates material/part tables, supports old/new part paths, maps states, handles chained loads, then optimizes/link/bounds/cache-refreshes parts. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyCMeshWave443.java` dry/apply/verify | PASS | Dry found `8` targets; apply reported `updated=8`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=8`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `8` metadata rows, `8` tag rows, `15` xref rows, `1352` instruction rows, and `8` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_cmesh_wave443_probe.py tools\ghidra_cmesh_wave443_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmesh_wave443_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `cmd.exe /c npm run test:ghidra-cmesh-wave443` | PASS | Focused probe returned `PASS` for all `8` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1884` commented functions, `4171` commentless functions, `1750` undefined signatures, and `1734` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1884`
- Commentless function objects: `4171`
- `undefined` signatures: `1750`
- Signatures still using `param_N`: `1734`

Telemetry-only proxies are comment-backed `1884/6055 = 31.11%` and strict clean-signature `1819/6055 = 30.04%`. These are not certification and are not completion gates.

## Backup

The actual saved Ghidra project was backed up after read-back at `G:\GhidraBackups\BEA_20260516-085221_post_wave443_cmesh_verified`. The backup comparison reported `19` files, `156240775` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Not Proven

This wave does not prove runtime mesh loading/render behavior; concrete `CMesh`/`CMeshPart` layouts; exact field names/types; exact source method identity; BEA launch behavior; game patching; or source-to-retail rebuild parity.
