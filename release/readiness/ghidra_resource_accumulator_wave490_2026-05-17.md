# Ghidra ResourceAccumulator Wave490 Readiness

Date: 2026-05-17

## Scope

- Hardened the two known `ResourceAccumulator.cpp` functions.
- Set `0x004d6f70` to `void __cdecl CResourceAccumulator__GetResourceFilename(char * out_path, int resource_id, int platform_id)`.
- Set `0x004d7200` to `void __cdecl CResourceAccumulator__ReadResourceFile(int resource_id, void * existing_buffer, int skip_optional_chunks)`.
- Preserved current function names and boundaries; no functions were created and no names were changed.

## Validation

- `py -3 -m py_compile tools\ghidra_resource_accumulator_wave490_probe.py`
- `py -3 tools\ghidra_resource_accumulator_wave490_probe.py --check`
- `cmd.exe /c npm run test:ghidra-resource-accumulator-wave490`
- `py -3 tools\ghidra_static_reaudit_queue_probe.py --check`
- Refreshed static queue: `6068` functions, `3853` commentless, `1674` undefined signatures, `1538` `param_N` signatures.

## Evidence

- Apply/read-back artifacts: `subagents/ghidra-static-reaudit/wave490-resource-accumulator-004d6f70/`
- Clean apply/probe summary: dry `updated=0 skipped=2`, apply `updated=2 skipped=0`, verify dry `updated=0 skipped=2`.
- Read-back exports: `2` metadata rows, `2` tag rows, decompile exports, xref exports, instruction exports, and callsite push/cleanup evidence for three-argument cdecl calls.

## Backup

- `G:\GhidraBackups\BEA_20260517-075159_post_wave490_resource_accumulator_verified`
- Verified: `19` files, `157551495` bytes, missing `0`, extra `0`, hash differences `0`.

## Boundary

Static retail-binary evidence only. Runtime archive loading behavior, full asset/resource-system recovery, concrete resource/global layouts, exact source-body identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
