# Ghidra MissionScript Object-Code Wave546 Readiness Note

Date: 2026-05-18

## Scope

Wave546 saved a static Ghidra signature/comment/tag hardening pass for one mission-script object-code cleanup helper:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004f7440` | `CMissionScriptObjectCode__FreeObjectIfPresent` | `void __fastcall CMissionScriptObjectCode__FreeObjectIfPresent(void * object_code)` |

The helper is register-only: `ECX` holds the object-code record. The body frees the two owned pointer slots at `object_code+0x00` and `object_code+0x04` through global memory manager `0x009c3df0`, then returns. The only observed xref is `CMissionScriptObjectCode__ClearFields`, which checks its object-code pointer for non-null, calls this helper, frees the enclosing object-code allocation, and clears the owner field.

## Evidence

- Apply script: `tools/ApplyMissionScriptObjectCodeWave546.java`.
- Probe: `tools/ghidra_mission_script_object_code_wave546_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave546-cmission-script-free-object-004f7440/`.
- Dry run: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `1` metadata row, `1` tag row, `1` xref row, `133` instruction rows, `1` target decompile export, and `1` caller decompile export.
- Focused probe: `py -3 tools\ghidra_mission_script_object_code_wave546_probe.py --check` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `G:\GhidraBackups\BEA_20260518-112036_post_wave546_mission_script_object_code_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave546:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2652` |
| Commentless functions | `3437` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1289` |
| Comment-backed proxy | `2652/6089 = 43.56%` |
| Strict comment-plus-clean-signature proxy | `2598/6089 = 42.67%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Exact object-code record layout.
- Exact allocation ownership beyond the observed two pointer slots and enclosing object free.
- Source identity or source-body parity.
- Runtime mission-script behavior.
- BEA launch, executable patching, and rebuild parity.
