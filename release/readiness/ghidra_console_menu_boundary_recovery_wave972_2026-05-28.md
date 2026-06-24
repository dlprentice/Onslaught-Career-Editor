# Ghidra Console Menu Boundary Recovery Wave972 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `console-menu-boundary-recovery-wave972`

Wave972 re-reviewed the console menu constructor/menu-navigation cluster and recovered eleven previously non-function console-menu vtable targets. Mutation status: function-boundary recovery. The pass created function objects, saved names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00401480 SharedVFunc__ReturnTrue_00401480` | Shared console-menu vtable target from slots `0x005d96fc`, `0x005d971c`, and `0x005d973c`; returns true via `MOV AL, 0x1; RET`. |
| `0x00429e30 CConsoleRootMenu__GetName` | Root-menu name vtable target at `0x005d972c`; copies string `0x00624d3c` (`Onslaught`) to caller output. |
| `0x00429e60 CConsoleRootMenu__GetEntry` | Root-menu entry vtable target at `0x005d9734`; copies fallback string `0x00624d48` (`???`) to caller output. |
| `0x00429e90 CConsoleCommandMenu__GetName` | Command-menu name vtable target at `0x005d970c`; copies string `0x00624d4c` (`Console commands`) to caller output. |
| `0x0042c460 CConsoleMenu__UnlinkChild` | Shared unlink target at slots `0x005d9704`, `0x005d9724`, `0x005d9744`, and `0x005d9764`; unlinks child nodes and clears child `+0x8/+0xc`. |
| `0x0042c4b0 CConsoleCommandMenu__GetNumEntries` | Command-menu count target at `0x005d9710`; walks global command head `0x0066582c` via next-link `+0xa8`. |
| `0x0042c4d0 CConsoleCommandMenu__GetEntry` | Command-menu entry target at `0x005d9714`; formats command name/description or fallback `0x00624d48`. |
| `0x0042c530 CConsoleCommandMenu__OnClick` | Command-menu click target at `0x005d9718`; writes selected command text to `0x0066529c`, toggles `0x00665824`, and calls `PLATFORM__SetKeySink`. |
| `0x0042c5e0 CConsoleVarMenu__GetNumEntries` | Cvar-menu count target at `0x005d96f0`; walks global cvar head `0x00665830` via next-link `+0xac`. |
| `0x0042c600 CConsoleVarMenu__GetEntry` | Cvar-menu entry target at `0x005d96f4`; uses `CConsoleVar__FormatValueToString`, `CConsoleVar__GetTypeName`, and format string `0x00625480`. |
| `0x0042c6a0 CConsoleVarMenu__OnClick` | Cvar-menu click target at `0x005d96f8`; formats `set %s ` through `0x00625490`, writes `0x0066529c`, toggles `0x00665824`, and calls `PLATFORM__SetKeySink`. |

Existing primary rows re-read cleanly: `0x0042c420 CConsoleMenu__ctor_like_0042c420`, `0x0042c440 CConsoleMenu__LinkChildAtHead`, `0x0042ba90 CConsole__MenuUp`, `0x0042bac0 CConsole__MenuDown`, and `0x0042bb30 CConsole__MenuSelect`.

Read-back evidence:

- `ApplyConsoleMenuBoundaryRecoveryWave972.java dry`: `updated=0 skipped=0 created=0 would_create=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- `ApplyConsoleMenuBoundaryRecoveryWave972.java apply`: `updated=11 skipped=0 created=11 would_create=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=22 missing=0 bad=0`
- `ApplyConsoleMenuBoundaryRecoveryWave972.java final dry`: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Primary pre-review exports: 5 metadata rows, 5 tag rows, 15 xref rows, 112 instruction rows, and 5 decompile rows.
- Boundary evidence included pre-apply vtable slots reporting `NO_FUNCTION_AT_POINTER` for the recovered targets and direct DATA vtable pointers from `0x005d96f0`, `0x005d9720`, and `0x005d974c`.
- Post exports: 11 metadata rows, 11 tag rows, 83 xref rows, 283 body-instruction rows, 11 decompile rows, and 36 post-vtable-slot rows.
- Queue after Wave972: 6209 total functions, 6209 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, 0 uncertain-owner names, 0 address-suffixed helper names, and 0 address-suffixed wrapper names.
- Static closure: `6209/6209 = 100.00%`.
- Re-audit progress: Wave911 focused queue `345/1408 = 24.50%`; expanded static surface progress `402/1465 = 27.44%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified`, 19 files, 173771655 bytes, `DiffCount=0`.

What this proves:

- The 11 target addresses are saved Ghidra function entries with comments, tags, and signatures.
- The recovered rows are tied to console-menu vtable DATA pointers, string dumps, xrefs, instruction rows, and decompile read-back.
- Static queue closure remains complete after the recovered function objects were added.

What remains unproven:

- Exact source-body identity.
- Complete `CConsole`, `CConsoleMenu`, `CConsoleCmd`, or `CConsoleVar` layouts.
- Runtime console menu behavior.
- Runtime key-sink side effects.
- BEA patching behavior.
- Rebuild parity.
