# Ghidra Console Core Status Review Wave937 Readiness

Status: complete read-only static read-back evidence
Date: 2026-05-28
Scope: `console-core-status-review-wave937`

Wave937 re-reviewed the CConsole initialization, built-in command/cvar registration, layout reset, cvar type-name formatting, and status-history print/reset sinks after the Wave911 risk-ranked continuation queue surfaced the cluster. Fresh Ghidra exports matched the saved correction boundary and did not justify a mutation. This wave made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x00429bc0` | `CConsole__Init` | `void __fastcall` console init helper; clears command/variable list heads at `+0x2394/+0x2398`, sets console alpha `+0x2390` to `0xc8`, calls `Registry__SetStringValue_HKCU`, initializes the key-name table, and emits startup console text through `CConsole__AddString`. |
| `0x00429ef0` | `CConsole__RegisterBuiltinCommands` | Registers built-in command nodes via repeated `CConsole__RegisterCommand` calls and registers `cg_consolealpha` through `CConsole__RegisterVariable`; callback identities remain static label-level evidence. |
| `0x0042a410` | `CConsole__ResetLayoutForWindowHeight` | Recomputes console/layout fields from repeated `PLATFORM__GetWindowHeight` reads. |
| `0x0042a540` | `CConsoleVar__GetTypeName` | Maps the cvar type enum at `+0xa0` to printable labels: `DWORD`, string, bool, float, fvector, fmatrix, and fallback. |
| `0x004416e0` | `CConsole__ResetStatusHistoryBuffer` | Clears 30 status-history text/timestamp slots, resets ring cursor `+0x9e4`, writes last-render timestamp `+0x9e8`, and enables `+0x9ec` when `DAT_00662dd0` is set. |
| `0x00441740` | `CConsole__Printf` | Variadic print sink using a 700-byte stack buffer and `vsprintf`; mirrors formatted text/newline through `DebugTrace`, optionally appends to the configured console file, advances the 30-slot status-history ring, and refreshes timestamp fields. |
| `0x004418a0` | `CConsole__PrintfNoNewline` | Variadic no-newline print sink using the same enable/file/ring/timestamp path with a 256-byte stack buffer and no DebugTrace newline mirror. |

Context anchors:

- `0x0040c640 DebugTrace` remains a Steam retail `RET` stub with broad diagnostic callsites, including `CConsole__Printf` and `CConsole__AddString`.
- `0x004419e0 CConsole__RenderStatusHistoryOverlay` is called by `CGame__DrawGameStuff` and draws recent status-history lines through `Text__AsciiToWideScratch` and `CDXFont__DrawText`.
- `0x0042a5f0 CConsoleVar__FormatValueToString` is the paired cvar value-formatting helper.
- `0x0042af80 CConsole__RegisterCommand` and `0x0042b040 CConsole__RegisterVariable` remain the command/cvar node registration helpers used by console init, game init, render/audio/engine setup, and BattleEngine/WalkerPart cvar registration paths.
- `0x0042b840 CConsole__AddString` is the broader variadic line sink used by startup text, status helpers, command handlers, script execution, and graphics/platform reporting paths.
- `0x0042bcf0 CConsole__InitKeyNameTable` seeds bind/list key-name strings, including Backspace/Return/Shift/arrow/num-key style entries.
- `0x00515db0 Registry__SetStringValue_HKCU` is the HKCU `Software\Lost Toys\Battle Engine Aquila` REG_SZ persistence helper called by `CConsole__Init` and `CConsole__AddString`.

Fresh read-back evidence:

- Primary exports: 7 metadata rows, 7 tag rows, 388 xref rows, 872 instruction rows, and 7 decompile rows.
- Context exports: 8 metadata rows, 8 tag rows, 482 xref rows, 1189 instruction rows, and 8 decompile rows.
- Primary xrefs confirm `CConsole__Init` from `CLTShell__InitializeRuntimeAndLoadCoreResources`, `CConsole__RegisterBuiltinCommands` from `CGame__Init`, `CConsole__ResetLayoutForWindowHeight` from `CLTShell__InitializeRuntimeAndLoadCoreResources`, `CConsoleVar__GetTypeName` from two label-level console callsites, `CConsole__ResetStatusHistoryBuffer` from `CLTShell__InitializeRuntimeAndLoadCoreResources`, `CConsole__Printf` from diagnostic/fatal/memory/save/load callsites, and `CConsole__PrintfNoNewline` from `CScriptObjectCode__Run`.
- Context xrefs confirm the console/status/debug/registry join: `DebugTrace` from `CConsole__Printf` and `CConsole__AddString`, status overlay from `CGame__DrawGameStuff`, command/cvar registration from console/game/engine/render/audio/BattleEngine setup, key-name table init from `CConsole__Init`, and HKCU registry persistence from `CConsole__Init` and `CConsole__AddString`.
- Verified read-only backup: `G:\GhidraBackups\BEA_20260528-015348_post_wave937_console_core_status_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave937: `161/1408 = 11.43%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave937; `console-core-status-review-wave937`; `0x00429bc0 CConsole__Init`; `0x00429ef0 CConsole__RegisterBuiltinCommands`; `0x0042a410 CConsole__ResetLayoutForWindowHeight`; `0x0042a540 CConsoleVar__GetTypeName`; `0x004416e0 CConsole__ResetStatusHistoryBuffer`; `0x00441740 CConsole__Printf`; `0x004418a0 CConsole__PrintfNoNewline`; `0x0040c640 DebugTrace`; `0x004419e0 CConsole__RenderStatusHistoryOverlay`; `0x0042a5f0 CConsoleVar__FormatValueToString`; `0x0042af80 CConsole__RegisterCommand`; `0x0042b040 CConsole__RegisterVariable`; `0x0042b840 CConsole__AddString`; `0x0042bcf0 CConsole__InitKeyNameTable`; `0x00515db0 Registry__SetStringValue_HKCU`; `161/1408 = 11.43%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-015348_post_wave937_console_core_status_review_verified`; no mutation.

What this proves:

- The CConsole core/status rows remain present in the saved Ghidra project with the expected names, signatures, comments, xrefs, tags, and decompile outputs.
- The static join between console initialization, built-in command/cvar registration, cvar formatting, status-history reset/overlay/print sinks, DebugTrace mirroring, key-name table initialization, and HKCU registry persistence remains coherent.
- No current Wave937 evidence justifies a rename, signature correction, function-boundary change, or executable-byte change.

What remains unproven:

- Exact source-body identity.
- Complete CConsole, CConsoleCmd, CConsoleVar, status-history, key table, or registry caller layouts.
- Runtime console command behavior.
- Runtime status overlay behavior.
- Runtime registry side effects.
- Runtime file logging behavior.
- BEA patching behavior.
- Rebuild parity.
