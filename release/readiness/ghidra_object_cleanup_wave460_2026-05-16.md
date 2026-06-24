# Ghidra Object Cleanup / Destructor Wave460 Evidence

Date: 2026-05-16

## Scope

Wave460 saved Ghidra name/signature/comment/tag corrections for `10` adjacent object cleanup and destructor targets:

`0x004bfe00`, `0x004bfe10`, `0x004bfe70`, `0x004bfed0`, `0x004bff30`, `0x004bff40`, `0x004bffa0`, `0x004c0000`, `0x004f84e0`, and `0x0050ee90`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave460-object-cleanup-current/`
- Apply script: `tools/ApplyObjectCleanupWave460.java`
- Probe: `tools/ghidra_object_cleanup_wave460_probe.py`
- Test alias: `npm run test:ghidra-object-cleanup-wave460`
- Dry summary: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=10 missing=0 bad=0`
- Apply summary: `updated=10 skipped=0 created=0 would_create=0 renamed=10 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `10` metadata rows, `10` tag rows, `68` xref rows, `10` decompile exports plus `index.tsv`, and `1210` focused instruction rows.
- Corrected `CUnit__dtor_base_Thunk_004bfe00`, `CRocket__dtor_base`, `CWaypoint__dtor_base`, `CSpawnerThing__dtor_base`, `CComplexThing__dtor_base_Thunk_004bff30`, `CSphereTrigger__dtor_base`, `CWingmanStart__dtor_base`, `CEscapePod__dtor_base`, `CUnit__dtor_base`, and `CUnit__scalar_deleting_dtor`.
- Preserved that `0x004bfe00` and `0x004bff30` are jump thunks, not standalone cleanup bodies, and left adjacent queued `0x004f84c0` untouched.
- Queue after refresh: `6057` functions, `2045` commented, `4012` commentless, `1727` undefined signatures, `1629` `param_N` signatures.
- Current telemetry proxies: comment-backed `2045/6057 = 33.76%`; strict comment-plus-clean-signature `1981/6057 = 32.71%`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-172857_post_wave460_object_cleanup_verified` (`19` files, `156896135` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime object cleanup/destruction behavior, exact object layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
