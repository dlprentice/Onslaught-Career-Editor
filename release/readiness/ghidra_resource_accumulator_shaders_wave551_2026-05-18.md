# Ghidra CVertexShader VSDS Deserialize Wave551 Readiness Note

Date: 2026-05-18

## Scope

Wave551 corrected and hardened one static Ghidra function:

| Address | Saved symbol |
| --- | --- |
| `0x005042f0` | `void __cdecl CVertexShader__DeserializeAll(void * chunk_reader)` |

## Evidence

- `CResourceAccumulator__ReadResourceFile` dispatches the `VSDS` chunk to `0x005042f0` with the active `CChunkReader` pointer, then cleans one stack argument.
- Stuart source names the matching resource path as `CVertexShader::DeserializeAll(&c)`, but the saved claim relies on Steam retail Ghidra evidence because the source path is platform-guarded.
- The body reads a 4-byte serialized shader-table size/version into `DAT_00854e74`, reads a 4-byte shader count, copies `0x4e0` bytes into the global CVertexShader table at `0x00634070`, clears every third dword across `0x00634074..0x00634554`, and calls `CVertexShader__Clone(chunk_reader, shader_index)` for each serialized shader index.

## Read-Back

- Dry: `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`.
- Verify dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Ghidra save reported `REPORT: Save succeeded`.
- Post exports verified `1` metadata row, `1` tag row, `1` xref row, `181` target instruction rows, `621` caller instruction rows, `1` target decompile export, and `1` caller decompile export.
- Focused probe: `py -3 tools\ghidra_resource_accumulator_shaders_wave551_probe.py --check` PASS.
- npm wrapper: `cmd.exe /c npm run test:ghidra-resource-accumulator-shaders-wave551` PASS.
- Queue refresh: PASS with `6089` total functions, `2662` commented, `3427` commentless, `1535` exact-undefined signatures, and `1280` `param_N` signatures.
- Backup: `G:\GhidraBackups\BEA_20260518-131733_post_wave551_resource_accumulator_shaders_verified`, `19` files, `159353735` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

- Exact `VSDS` chunk schema or concrete CVertexShader global table layout.
- Runtime shader behavior, including shader loading behavior, or runtime Direct3D behavior.
- Platform-guard equivalence between Stuart source and Steam retail behavior.
- Complete shader/resource system recovery.
- BEA patching or rebuild parity.
