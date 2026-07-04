# Ghidra IScript Level/Event Wave585 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave585 hardened 5 adjacent IScript level/event command handlers at `0x00537fd0`, `0x005381a0`, `0x005381c0`, `0x005381e0`, and `0x005383c0`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00537fd0` | `IScript__IsFriendly` |
| `0x005381a0` | `IScript__LevelLost` |
| `0x005381c0` | `IScript__LevelLostString` |
| `0x005381e0` | `IScript__LevelWon` |
| `0x005383c0` | `IScript__ScheduleEvent` |

What is proven:

- The saved functions are registered by `ScriptCommandRegistry__InitBuiltins`.
- `0x00537fd0` was renamed from `CBoolDataType__ctor_like_00537fd0` to `IScript__IsFriendly` because the registry stores `s_IsFriendly_0064f9d4` with this function pointer at command slot `+0x30`.
- Ghidra now records `IScript__IsFriendly` as a script-context ABI row: `__thiscall` implicit `this` plus `script_args`, `unused_state`, and `out_result`; instruction read-back confirms `RET 0xc`.
- Ghidra now records `IScript__LevelLost`, `IScript__LevelLostString`, `IScript__LevelWon`, and `IScript__ScheduleEvent` as fixed three-stack-argument `__stdcall` command handlers; instruction read-back confirms `RET 0xc`.
- Post-save read-back verified 5 metadata rows, 5 tag rows, 5 xref rows, 1845 instruction rows, and 5 decompile rows.
- The queue refresh reports `6093` total functions, `2965` commented, `3128` commentless, `1400` exact-undefined signatures, and `1116` `param_N` signatures.
- The next high-signal queue head is `0x00538470 CScriptEventNB__UpdateWaypointFollowing`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-094217_post_wave585_iscript_level_event_verified` with 19 files, 160664455 bytes, `DiffCount=0`, and manifest hash `db37d71fd718dd6ccc11d7bff29df824dbf777301952a2816c34192743c68cbe`.

What is not proven:

- runtime mission-script behavior remains unproven.
- Script corpus coverage remains separate evidence.
- Exact command descriptor layout, exact flag/team semantics for `IsFriendly`, and exact event payload layout remain unproven.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
