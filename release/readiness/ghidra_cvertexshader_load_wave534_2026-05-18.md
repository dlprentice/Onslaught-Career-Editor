# Ghidra CVertexShader Load/Compile Wave534 Readiness

Date: 2026-05-18

## Scope

Wave534 hardened the static Ghidra signatures, comments, and tags for nine adjacent CVertexShader load/compile/render-info helpers:

- `0x00501730` `CVertexShader__ClearOut`
- `0x005019d0` `CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag`
- `0x005022a0` `CVertexShader__LoadFromFile`
- `0x00502420` `CVertexShader__CompileShader`
- `0x005027f0` `CVertexShader__LoadCompiledShaderBlobFromVSOFile`
- `0x00502920` `CVertexShader__ApplyCustomRenderStateShaderConstants`
- `0x00503ac0` `CVertexShader__BuildAndCreateRenderInfoShader`
- `0x00503dd0` `CVertexShader__AppendDeclarationNamesToDebugString`
- `0x00503f90` `CVertexShader__Clone`

## Evidence

- Dry run: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back exports verified `9` metadata rows, `9` tag rows, `9` target xref rows, `8289` instruction rows, `9` decompile exports, `369` representative callsite instruction rows, and `4` CVertexShader vtable-slot rows.
- Focused probe: `py -3 tools\ghidra_cvertexshader_load_wave534_probe.py --check`.
- Queue refresh: `6083` functions, `2598` commented, `3485` commentless, `1550` exact-undefined signatures, and `1316` `param_N` signatures.
- Current telemetry proxies: comment-backed `2598/6083 = 42.71%`; strict comment-plus-clean-signature `2544/6083 = 41.82%`.
- Backup: `G:\GhidraBackups\BEA_20260518-055139_post_wave534_cvertexshader_load_verified`, verified `19` files, `159189895` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Caveats

This is static retail Ghidra evidence only. It does not prove runtime shader behavior, runtime Direct3D behavior, exact source-body identity, concrete `CVertexShader` / `CShaderBase` / device-object layouts, BEA patching, or rebuild parity.

The CVertexShader vtable slot 2 pointer at `0x00501a10` remains a deferred no-function boundary. Wave534 only hardened the downstream stack-cleaning compiled-blob helper at `0x005027f0` and documented the unresolved slot-2 caller context.
