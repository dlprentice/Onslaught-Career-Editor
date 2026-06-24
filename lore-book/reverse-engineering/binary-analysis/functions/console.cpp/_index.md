# console.cpp - Function Mappings

Source file: `C:\dev\ONSLAUGHT2\console.cpp`
Debug string address: `0x00624d0c`

## Overview
> **Queue status (2026-05-28):** Ghidra export-contract closure **6209/6209** (Wave972: every currently exported function object commented with clean-signature proxy; not evidence-grade semantics or runtime proof). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

The CConsole class implements an in-game developer console system with support for:
- Console commands (with callbacks)
- Console variables (cvars)
- Key bindings
- Command history
- Script execution
- Loading screen progress/range rendering helpers used by `CFrontEnd` and `CGame`

Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`) records the console infrastructure side of a static-coherent engine/platform/math/memory support core. Console anchors include `CConsole__RegisterBuiltinCommands` and `CConsole__ExecuteBufferedCommandSlot`. Verified backup: `G:\GhidraBackups\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`. Runtime console command execution and exact layouts remain separate proof.

Wave937 console core/status review (`console-core-status-review-wave937`) re-read the central CConsole init/register/layout/type/status-history cluster with fresh metadata/tags/xref/instruction/decompile exports and found no mutation warranted. Primary anchors are `0x00429bc0 CConsole__Init`, `0x00429ef0 CConsole__RegisterBuiltinCommands`, `0x0042a410 CConsole__ResetLayoutForWindowHeight`, `0x0042a540 CConsoleVar__GetTypeName`, `0x004416e0 CConsole__ResetStatusHistoryBuffer`, `0x00441740 CConsole__Printf`, and `0x004418a0 CConsole__PrintfNoNewline`; context anchors are `0x0040c640 DebugTrace`, `0x004419e0 CConsole__RenderStatusHistoryOverlay`, `0x0042a5f0 CConsoleVar__FormatValueToString`, `0x0042af80 CConsole__RegisterCommand`, `0x0042b040 CConsole__RegisterVariable`, `0x0042b840 CConsole__AddString`, `0x0042bcf0 CConsole__InitKeyNameTable`, and `0x00515db0 Registry__SetStringValue_HKCU`. Fresh xrefs keep console initialization tied to `CLTShell__InitializeRuntimeAndLoadCoreResources`, built-in registration to `CGame__Init`, status overlay to `CGame__DrawGameStuff`, DebugTrace mirroring to console print/add-string sinks, command/cvar registration to console/game/engine/render/audio/BattleEngine setup, and HKCU registry persistence to init/add-string paths. Wave911 focused re-audit progress after Wave937 is `161/1408 = 11.43%`; static export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-015348_post_wave937_console_core_status_review_verified`. This is static read-only coherence evidence only; exact source-body identity, complete console layouts, runtime console/status/registry/file-log behavior, BEA patching, and rebuild parity remain separate proof. No mutation.


Wave1206 console support current-risk review (`wave1206-console-support-current-risk-review`) re-read `7 CConsole support current-risk rows` with fresh Ghidra export metadata/tag/xref/instruction/decompile evidence and no mutation: `CConsole__Init`, `CConsoleVar__GetTypeName`, `CConsole__RegisterCommand`, `FatalError__ExitWithLocalizedPrefix_A`, `FatalError__ExitWithLocalizedPrefix_B`, `CConsole__Printf`, and `CConsole__PrintfNoNewline`. The read-only review made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Fresh exports verified `426 xref rows`, `630 instruction rows`, and `7 decompile rows`; active current-risk progress is `1083/1179 = 91.86%`, remaining active focused work: 96, current risk candidates: 6166, current focused candidates: 1141, live regenerated current focused candidates: 1141, legacy additive counter is deprecated (`1114/1179`), 26 duplicate-address overcount, Wave1145 arithmetic overcount: 5, static closure `6411/6411 = 100.00%`, static debt `0 / 0 / 0`, static-reaudit-current-risk-ledger.json, current-risk denominator, continuity denominator, focused threshold `15`, not Wave911 reconstruction. Verified backup: `G:\GhidraBackups\BEA_20260607-023000_post_wave1206_console_support_current_risk_review_verified`. Runtime console behavior, runtime fatal behavior, exact layouts, BEA patching behavior, rebuild parity, and no noticeable difference remain separate proof; static target remains rebuild-grade static contracts.

Wave1134 console current-risk review (`wave1134-console-current-risk-review`) re-read `0x00429ef0 CConsole__RegisterBuiltinCommands` and `0x0042a410 CConsole__ResetLayoutForWindowHeight` with fresh metadata/tag/xref/instruction/decompile evidence as a read-only review with no mutation. Context rows are context `0x00429bc0 CConsole__Init`, context `0x0042a540 CConsoleVar__GetTypeName`, context `0x004416e0 CConsole__ResetStatusHistoryBuffer`, context `0x00441740 CConsole__Printf`, context `0x004418a0 CConsole__PrintfNoNewline`, context `0x004419e0 CConsole__RenderStatusHistoryOverlay`, context `0x0042af80 CConsole__RegisterCommand`, and context `0x0042b040 CConsole__RegisterVariable`. Exact probe tokens: 2 rows; context 0x00429bc0 CConsole__Init; context 0x0042a540 CConsoleVar__GetTypeName; context 0x004416e0 CConsole__ResetStatusHistoryBuffer; context 0x00441740 CConsole__Printf; context 0x004418a0 CConsole__PrintfNoNewline; context 0x004419e0 CConsole__RenderStatusHistoryOverlay; context 0x0042af80 CConsole__RegisterCommand; context 0x0042b040 CConsole__RegisterVariable. Fresh primary exports verified `2` metadata rows, `2` tag rows, `2` xref rows, `418` instruction rows, and `2` decompile rows; context exports verified `8` metadata rows, `8` tag rows, `470` xref rows, `679` instruction rows, and `8` decompile rows. Current focused accounting is `186/1179 = 15.78%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 993; static debt `0 / 0 / 0`; console registration/layout cluster; fresh Ghidra export; read-only review; no mutation. Verified backup: `G:\GhidraBackups\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`; previous completed backup: `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`. Runtime console command/cvar/layout/status behavior, exact layouts, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

Wave972 console menu boundary recovery (`console-menu-boundary-recovery-wave972`, `wave972-readback-verified`) recovered eleven previously non-function console-menu vtable targets while re-reading `0x0042c420 CConsoleMenu__ctor_like_0042c420`, `0x0042c440 CConsoleMenu__LinkChildAtHead`, `0x0042ba90 CConsole__MenuUp`, `0x0042bac0 CConsole__MenuDown`, and `0x0042bb30 CConsole__MenuSelect`. Recovered anchors include `0x00401480 SharedVFunc__ReturnTrue_00401480`, `0x00429e30 CConsoleRootMenu__GetName`, `0x0042c460 CConsoleMenu__UnlinkChild`, `0x0042c530 CConsoleCommandMenu__OnClick`, and `0x0042c6a0 CConsoleVarMenu__OnClick`. Fresh evidence ties the rows to console-menu vtable DATA pointers from `0x005d96f0`, `0x005d9720`, and `0x005d974c`, string anchors `0x00624d3c Onslaught`, `0x00624d48 ???`, `0x00624d4c Console commands`, and `0x00625490 set %s `, command/cvar list heads `0x0066582c` and `0x00665830`, and key-sink handoff through `PLATFORM__SetKeySink`. Final post exports verified `11` metadata rows, `11` tag rows, `83` xref rows, `283` body-instruction rows, `11` decompile rows, and `36` post-vtable-slot rows. Wave911 focused re-audit progress after Wave972 is `345/1408 = 24.50%`; expanded static surface progress is `402/1465 = 27.44%`; static export-contract closure is `6209/6209 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified`. This is static function-boundary recovery evidence only; exact source-body identity, complete `CConsole`/`CConsoleMenu`/`CConsoleCmd`/`CConsoleVar` layouts, runtime console menu behavior, runtime key-sink side effects, BEA patching, and rebuild parity remain separate proof.

Wave998 static read-back (`fatal-error-spine-review-wave998`, `wave998-readback-verified`) saved no-return signature/comment/tag corrections for the localized fatal wrappers `0x0042c750 FatalError__ExitWithLocalizedPrefix_A` and `0x0042d0b0 FatalError__ExitWithLocalizedPrefix_B`. The saved signatures are `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)` and `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)`. Context rows are `0x0042cfa0 FatalError__ExitProcess` and `0x0042d080 FatalError_LocalizedStringId`. Verified backup: `G:\GhidraBackups\BEA_20260531-091151_post_wave998_fatal_error_spine_review_verified`. Wave911 focused progress is `467/1408 = 33.17%`; expanded static surface progress is `585/1478 = 39.58%`; queue closure remains `6222/6222 = 100.00%`. Runtime fatal UI/error presentation, exact source-body identity, exact source layout/type identity, full format/resource ownership for every caller, BEA patching, and rebuild parity remain separate proof.

## 2026-05-25 Wave852 PC Platform/Resource Tail Read-Back

Wave852 PC platform/resource tail (`pc-platform-resource-tail-wave852`, `wave852-readback-verified`) adds saved static evidence for the PC registry persistence helper called by `CConsole__Init` and `CConsole__AddString`: `0x00515db0 Registry__SetStringValue_HKCU`. Probe token anchor: `Wave852 PC platform/resource tail`; `0x00515db0 Registry__SetStringValue_HKCU`; `Software\Lost Toys\Battle Engine Aquila`; `RegSetValueExA`; `5736/6098 = 94.06%`; `0x005168d0 CPCSoundManager__dtor`; `G:\GhidraBackups\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified`.

The saved helper opens/creates `HKEY_CURRENT_USER\Software\Lost Toys\Battle Engine Aquila`, computes the NUL-terminated value length, writes `REG_SZ` value data through `RegSetValueExA`, and closes the key. Runtime registry side effects, exact caller value contract, BEA patching, and rebuild parity remain deferred.

## CConsole Class Layout (Partial)

Based on member access patterns in the decompiled code:

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x0004 | char[60][128] | Command history buffer | 60 entries, 128 chars each |
| 0x1E84 | char[10][128] | Recent commands | 10 entries, 128 chars each |
| 0x238C | byte | Unknown flag | |
| 0x238D | byte | Unknown flag | |
| 0x2390 | int | Console alpha | Background transparency (default: 200) |
| 0x2394 | CConsoleCmd* | Command list head | Linked list of registered commands |
| 0x2398 | CConsoleVar* | Variable list head | Linked list of registered variables |
| 0x239C | void* | Unknown pointer | |
| 0x23A0 | void* | Unknown pointer | |
| 0x23A4 | void* | Unknown pointer | |
| 0x23B0 | void* | Unknown pointer | |
| 0x23B4 | int | Unknown (-1 init) | |
| 0x23B8 | int | Unknown (1 init) | |
| 0x23BC | char[256][128] | Output line buffer | 256 lines, 128 chars each |
| 0xB3C0 | int | Unknown (-1 init) | |
| 0xB3C4 | byte | Unknown flag | |
| 0xB3C5 | byte | Unknown (set to 1) | |
| 0xB3C6 | byte | Unknown flag | |
| 0xB3C8 | int | Unknown | |
| 0xB3D0 | int | Unknown | |
| 0xB3D8 | float | mLoadingRangeMin | Loading progress range start (%) |
| 0xB3DC | float | mLoadingRangeMax | Loading progress range end (%) |
| 0xB3E0 | float | mLoadingCurrent | Current loading progress (%) |

## CConsoleCmd Structure (0xAC bytes)

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x00 | char[32] | Name | Command name |
| 0x20 | char[128] | Description | Help text |
| 0xA0 | void* | Callback | Function pointer for command handler |
| 0xA4 | char | Flags | Command flags |
| 0xA8 | CConsoleCmd* | Next | Linked list pointer |

## CConsoleVar Structure (0xB0 bytes)

| Offset | Type | Member | Notes |
|--------|------|--------|-------|
| 0x00 | char[32] | Name | Variable name |
| 0x20 | char[128] | Description | Help text |
| 0xA0 | int | Type | Variable type |
| 0xA4 | void* | ValuePtr | Pointer to actual value storage |
| 0xA8 | char | Flags1 | |
| 0xA9 | char | Flags2 | |
| 0xAC | CConsoleVar* | Next | Linked list pointer |

## Wave1146 Current-Risk Recheck

Wave1146 (`wave1146-mixed-engine-score20-current-risk-review`) re-read the mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk slice with fresh Ghidra exports: damage sentinel, console status-history, debug-marker shutdown, and engine resource/view/light helpers. It accounts for `8 current-risk rows`, moves Wave1108 current focused accounting to `306/1179 = 25.95%`, keeps static closure at `6411/6411 = 100.00%` with `0 / 0 / 0` debt, and verified backup `G:\GhidraBackups\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified`; previous completed backup `G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified`. This was a read-only review with no mutation and no Codex subagent; runtime behavior, exact layouts, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Probe token anchor: Wave1146; wave1146-mixed-engine-score20-current-risk-review; 306/1179 = 25.95%; 8 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 873; current risk candidates: 6166; mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk review; fresh Ghidra export; damage sentinel; console status-history; debug-marker shutdown; engine resource/view/light helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CDamage__ctor_clear_head_and_init_flag; CConsole__ResetStatusHistoryBuffer; CDebugMarkers__Shutdown; CEngine__InitResources; CEngine__LoadAllNamedMeshes; CEngine__GetViewMatrixFromCamera; CEngine__ResetPos; CEngine__SetupLights; G:\GhidraBackups\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

The console-row anchor is `0x004416e0 CConsole__ResetStatusHistoryBuffer`: fresh metadata, tag, xref, instruction, and decompile exports preserve the status-history reset, the 30-slot buffer clear, `+0x9e4/+0x9e8`, and the `DAT_00662dd0` gate. The same slice rechecked `0x00441e50 CDebugMarkers__Shutdown` for the debug-marker shutdown path.

## Functions (56 tracked mappings)

| Address | Name | Description |
|---------|------|-------------|
| 0x004416e0 | CConsole__ResetStatusHistoryBuffer | Wave 364 owner correction; resets 30 status-history text slots and ring-buffer fields |
| 0x004419e0 | CConsole__RenderStatusHistoryOverlay | Wave 364 owner correction; renders recent status-history lines via text conversion and font draw calls |
| 0x0040c640 | DebugTrace | Wave 386 signature/comment hardening; retail trace call target is currently a `RET` stub/no-op but has broad diagnostic xrefs |
| 0x0042cfa0 | FatalError__ExitProcess | Wave 386 no-return fatal exit path: console print, mouse shutdown, localized text formatting, fallback helper, and `ExitProcess(1)` |
| 0x0042d080 | FatalError_LocalizedStringId | Wave 386 guard-gated localized fatal wrapper around `FatalError__ExitProcess` |
| 0x00441740 | CConsole__Printf | Wave 386 variadic console print sink with `DebugTrace` mirror, console-file append, 30-slot status-history ring update, and timestamp refresh |
| 0x004418a0 | CConsole__PrintfNoNewline | Wave 386 variadic no-newline print sink sharing file/history/timestamp handling without newline trace mirror |
| 0x00429bc0 | CConsole__Init | Initializes the console system |
| 0x00515db0 | Registry__SetStringValue_HKCU | Wave852 HKCU `REG_SZ` registry persistence helper called by console init/add-string paths |
| 0x00429ef0 | CConsole__RegisterBuiltinCommands | Wave1134 re-read: registers built-in commands and `cg_consolealpha`; no mutation |
| 0x004655d0 | con_fmv_play | Wave404 console command handler for `fmv_play <filename>`; dispatches frontend video playback through the noninteractive gate |
| 0x0042a410 | CConsole__ResetLayoutForWindowHeight | Wave1134 re-read: recomputes layout metrics from `PLATFORM__GetWindowHeight`; no mutation |
| 0x0042af80 | CConsole__RegisterCommand | Registers a single console command |
| 0x0042b040 | CConsole__RegisterVariable | Registers a single console variable |
| 0x0042ad30 | CConsole__ExecScript | Loads and executes a console script file line-by-line |
| 0x0042a460 | CConsole__ListBinds | Enumerates key->bind mappings and prints formatted bind lines |
| 0x0042a540 | CConsoleVar__GetTypeName | Converts cvar type enum to printable type label |
| 0x0042a5f0 | CConsoleVar__FormatValueToString | Formats cvar value text by type and value pointer |
| 0x0042a770 | CConsole__FindCommandByName | Searches command list head (`this+0x2394`) via `stricmp` |
| 0x0042a4f0 | CConsole__ExecuteBufferedCommandSlot | Executes a buffered command/output line slot (`this+0x23BC`) when non-empty |
| 0x0042a7b0 | CConsole__SetVariableByName | Resolves a variable by name and writes parsed typed value text |
| 0x0042ae70 | CConsole__ShutdownAndFreeAllLists | Full teardown helper for command/var lists and owned aux pointers |
| 0x0042af20 | CConsole__ClearCommandAndVariableLists | Clears/frees command and variable lists only |
| 0x0042b9c0 | CConsole__ExecuteCommandLine | Tokenizes and dispatches a single console command line |
| 0x0042b120 | CConsole__HandleBind | Console input/bind key handler (toggle/history/tab-complete/dispatch paths) |
| 0x0042ba90 | CConsole__MenuUp | Console menu cursor up (selection decrement + clamp) |
| 0x0042bac0 | CConsole__MenuDown | Console menu cursor down (selection increment + clamp) |
| 0x0042bb30 | CConsole__MenuSelect | Console menu selection execute/apply path |
| 0x00401480 | SharedVFunc__ReturnTrue_00401480 | Wave972 shared console-menu vtable target that returns true |
| 0x00429e30 | CConsoleRootMenu__GetName | Wave972 root-menu name vtable target; copies `Onslaught` |
| 0x00429e60 | CConsoleRootMenu__GetEntry | Wave972 root-menu fallback entry target; copies `???` |
| 0x00429e90 | CConsoleCommandMenu__GetName | Wave972 command-menu name target; copies `Console commands` |
| 0x0042c420 | CConsoleMenu__ctor_like_0042c420 | Initializes ConsoleMenu-style object fields; exact source constructor identity remains deferred |
| 0x0042c440 | CConsoleMenu__LinkChildAtHead | Links a child menu node at the head of a parent child list |
| 0x0042c460 | CConsoleMenu__UnlinkChild | Wave972 shared console-menu unlink target; removes child links and clears child parent/sibling fields |
| 0x0042c4b0 | CConsoleCommandMenu__GetNumEntries | Wave972 command-menu count target walking command list head `0x0066582c` |
| 0x0042c4d0 | CConsoleCommandMenu__GetEntry | Wave972 command-menu entry text formatter |
| 0x0042c530 | CConsoleCommandMenu__OnClick | Wave972 command-menu click target; writes selected command text and calls `PLATFORM__SetKeySink` |
| 0x0042c5e0 | CConsoleVarMenu__GetNumEntries | Wave972 cvar-menu count target walking cvar list head `0x00665830` |
| 0x0042c600 | CConsoleVarMenu__GetEntry | Wave972 cvar-menu entry formatter using `CConsoleVar__FormatValueToString` and `CConsoleVar__GetTypeName` |
| 0x0042c6a0 | CConsoleVarMenu__OnClick | Wave972 cvar-menu click target; formats `set %s ` and calls `PLATFORM__SetKeySink` |
| 0x0042b840 | CConsole__AddString | Core variadic console text sink (format + append/split to rolling buffers) |
| 0x00472240 | CConsole__AppendToStatusBufferV | Wave 381 owner correction; appends formatted status/debug overlay text through `vsprintf` and the `console+0x2710` write cursor |
| 0x0042b500 | CConsole__Status | Begins a nested status section (`...` suffix) and increments status depth |
| 0x0042b650 | CConsole__StatusUpdateLine | Internal status-line rewrite helper used by status/progress completion flows |
| 0x0042b800 | CConsole__StatusDone | Completes a status section (success/fail) and decrements status depth |
| 0x0042bbc0 | CConsole__SetLoading | Enables/disables loading-screen mode and manages loading-screen texture lifecycle |
| 0x0042bcf0 | CConsole__InitKeyNameTable | Initializes key-name lookup table strings (Backspace/Return/Shift/arrows/num keys) |
| 0x0042c810 | CConsole__RenderLoadingScreen | Renders/updates loading screen and progress overlays |
| 0x0042cf40 | CConsole__SetLoadingRange | Sets loading progress interpolation range |
| 0x0042cf70 | CConsole__SetLoadingFraction | Sets loading progress fraction inside active range |
| 0x0042c750 | FatalError__ExitWithLocalizedPrefix_A | Wave998 no-return fatal wrapper variant A: pops message plus second callerContext/status argument, builds localized prefix (`id 0xCC`) + message, and exits through `FatalError__ExitProcess` |
| 0x0042d0b0 | FatalError__ExitWithLocalizedPrefix_B | Wave998 no-return single-message fatal wrapper variant used by mesh/resource deserialization failures |
| 0x0042d310 | PlatformInput__InitMouse | Creates/acquires DirectInput mouse device and resets cursor/profiler state |
| 0x0042d3b0 | PlatformInput__ShutdownMouse | Unacquires/releases mouse device and snapshots cursor position |
| 0x0042d420 | PlatformInput__PollMouseMotion | Polls device state, updates cursor deltas/position, reacquires on loss |
| 0x0042d4d0 | PlatformInput__PollMouseState | Polls motion + button edge/hold states (`left/right/middle`) into globals |

### Options Entry Init Helpers (Recovered 2026-02-25)

Recovered from the previously deferred constructor-like trio after deeper caller disassembly on 0x00453420..0x00453840 and 0x00514180..0x00514660 showed repeated options-entry initialization patterns.

| Address | Final Name | Notes |
|---------|------------|-------|
| 0x0042d260 | OptionsEntries__InitSingleBindingEntry | `void * __thiscall`: initializes one options-entry binding slot (`active` byte, `entry_id`, slot-0 device/scan/vk) and returns `this`. |
| 0x0042d2b0 | OptionsEntries__InitDualBindingEntry | `void * __thiscall`: initializes dual-binding entry variants (slot-0 + slot-1 metadata) and returns `this`. |
| 0x0042d300 | OptionsEntries__InitSentinelEntry | `void __thiscall`: sentinel/reset helper used in the same options-entry initialization sequences. |
| 0x00453460 | OptionsEntries__InitDefaultDualBindingsTable | `void __cdecl`: table builder that writes default dual-binding entries into `DAT_00677af0` and appends sentinels. |
| 0x00514210 | OptionsEntries__InitDefaultSingleBindingsTable | `void __cdecl`: table builder that writes default single-binding entries into `DAT_008892d8` and appends a sentinel. |

---

## Wave 386 Diagnostic / Fatal / Console Correction (2026-05-13)

Serialized headless dry/apply/read-back hardened five diagnostic, fatal-error, and console-print saved Ghidra targets. The saved names were preserved; this pass saved comments/tags, set `FatalError__ExitProcess` no-return metadata, and saved variadic signatures for the two `CConsole` print sinks. This is static Ghidra evidence only; it does not prove runtime console/debug/fatal behavior, concrete `CConsole` layout recovery, locals/types, BEA launch behavior, game patching, or rebuild parity.

| Address | Current saved Ghidra state | Evidence summary |
|---------|----------------------------|------------------|
| `0x0040c640` | `DebugTrace` | Retail trace target is a `RET` stub/no-op with `323` xrefs. |
| `0x0042cfa0` | `FatalError__ExitProcess` | No-return fatal path prints through the console, shuts down mouse input, formats localized fatal text, runs fallback helper context, and calls `ExitProcess(1)`. |
| `0x0042d080` | `FatalError_LocalizedStringId` | Calls the no-return fatal exit body when the guard byte is clear. |
| `0x00441740` | `CConsole__Printf` | Variadic print sink with stack-buffer formatting, `DebugTrace` mirror, optional file append, 30-slot status-history ring update, and timestamp refresh. |
| `0x004418a0` | `CConsole__PrintfNoNewline` | Variadic no-newline print sink sharing the file/history/timestamp path without the newline trace mirror. |

Validation read-back produced `5` metadata rows, `5` decompile exports, `757` xref rows, `605` instruction rows, `5` tag rows, and a focused probe `PASS` with `11` instruction hits. The whole-database queue now reports `6027` functions, `1435` commented functions, `4592` commentless functions, `1935` undefined signatures, and `1913` `param_N` signatures; the broad `23.81%` comment-backed proxy is telemetry only.

## Wave 363 Options / Platform Input Comment Refresh (2026-05-13)

Serialized headless dry/apply/read-back saved proof-boundary comments/tags on seven options-entry and platform-input targets. The saved names and signatures were already aligned with current evidence; this pass is static Ghidra evidence only, not runtime input proof, concrete global-layout recovery, exact source-body identity, BEA launch behavior, game patching, or rebuild parity.

| Address | Current saved Ghidra state | Evidence summary |
|---------|----------------------------|------------------|
| `0x0042d260` | `OptionsEntries__InitSingleBindingEntry` | Active byte, entry id, slot-0 device/scan/virtual-key fields, slot-1 defaults, and `RET 0x14`. |
| `0x0042d2b0` | `OptionsEntries__InitDualBindingEntry` | Active byte, entry id, slot-0 and slot-1 metadata fields, and `RET 0x20`. |
| `0x0042d300` | `OptionsEntries__InitSentinelEntry` | Cleared active byte and `-1` sentinel entry id. |
| `0x0042d310` | `PlatformInput__InitMouse` | DirectInput mouse-device creation, data format/cooperative level setup, zeroed state, profiler reset, cursor centering, and enabled global input state. |
| `0x0042d3b0` | `PlatformInput__ShutdownMouse` | Mouse-device unacquire/release, disabled global state, non-dev-mode cursor-position snapshot, and profiler reset. |
| `0x0042d420` | `PlatformInput__PollMouseMotion` | DIMOUSESTATE-style global zeroing, device-state read, reacquire on `0x8007001e`, and non-dev-mode delta/wheel accumulation. |
| `0x0042d4d0` | `PlatformInput__PollMouseState` | Shared state/reacquire path, delta/wheel update, and left/right/middle held/edge masks `0x80`, `0x8000`, and `0x800000`. |

Validation read-back produced `7` metadata rows, `7` decompile exports, `99` xref rows, `847` focused instruction rows, `7` tag rows, and a focused probe `PASS` with `0` stale-signature or overclaim hits. The whole-database queue now reports `6008` functions, `1250` commented functions, `4758` commentless functions, `1948` undefined signatures, and `2019` `param_N` signatures; the broad `20.81%` comment-backed proxy is telemetry only.

---

## Wave 364 Status-History Owner Correction (2026-05-13)

Serialized headless dry/apply/read-back corrected two early status-history helpers that had stale non-console owner labels:

| Address | Current saved Ghidra state | Evidence summary |
|---------|----------------------------|------------------|
| `0x004416e0` | `CConsole__ResetStatusHistoryBuffer` | Corrected from stale `CUnit__ResetPerSlotCooldownTables`; resets 30 0x50-byte text slots and the `+0x9e4` / `+0x9e8` ring-buffer fields. |
| `0x004419e0` | `CConsole__RenderStatusHistoryOverlay` | Corrected from stale frontend-cheat wording; draws up to six recent ring-buffer lines through `Text__AsciiToWideScratch` and `CDXFont__DrawText`. |

Validation read-back produced matching metadata/decompile/xref/instruction/tag evidence as part of the Wave 364 probe. This is saved static Ghidra evidence only; runtime console/status-overlay behavior, exact source method identity, concrete layout/type recovery, locals, BEA launch behavior, game patching, and rebuild parity remain unproven.

---

## Wave 326 Saved-Ghidra Signature Refresh (2026-05-12)

Serialized headless dry/apply/read-back hardened the following saved signatures, proof-boundary comments, and tags in Ghidra. This pass is static Ghidra evidence only; it does not prove runtime console/menu behavior, concrete layouts, local-variable/type recovery, exact source-body identity, BEA launch behavior, game patching, or rebuild parity.

| Address | Current saved Ghidra signature | Evidence summary |
|---------|--------------------------------|------------------|
| 0x00429bc0 | `void __fastcall CConsole__Init(void * this)` | Console initialization, buffer clearing, default state, key-name table setup, and startup text. |
| 0x00429ef0 | `void __fastcall CConsole__RegisterBuiltinCommands(void * this)` | Built-in command/cvar registration including `cg_consolealpha`. |
| 0x0042a410 | `void __fastcall CConsole__ResetLayoutForWindowHeight(void * this)` | Window-height-driven layout recomputation. |
| 0x0042a4f0 | `void __thiscall CConsole__ExecuteBufferedCommandSlot(void * this, char slotIndex, int bankSelector)` | Buffered command/output slot execution when non-empty. |
| 0x0042a540 | `void __stdcall CConsoleVar__GetTypeName(void * var, char * outTypeName)` | Cvar type-label formatting. |
| 0x0042a5f0 | `void __stdcall CConsoleVar__FormatValueToString(void * var, char * outValueText)` | Cvar value formatting by type and storage pointer. |
| 0x0042a770 | `char * __thiscall CConsole__FindCommandByName(void * this, char * commandName)` | Command list search by case-insensitive name. |
| 0x0042ae70 | `void __fastcall CConsole__ShutdownAndFreeAllLists(void * this)` | Full command/variable list and owned auxiliary pointer teardown. |
| 0x0042af20 | `void __fastcall CConsole__ClearCommandAndVariableLists(void * this)` | Command/variable list-only cleanup. |
| 0x0042af80 | `void __thiscall CConsole__RegisterCommand(void * this, char * name, char * description, void * callback, char flags)` | Command node allocation, field copy, and head insertion. |
| 0x0042b040 | `void __thiscall CConsole__RegisterVariable(void * this, char * name, char * description, int varType, void * valuePtr, char flags1, char flags2)` | Cvar node allocation, field copy, and head insertion. |
| 0x0042ba90 | `bool __fastcall CConsole__MenuUp(void * this)` | Menu selection decrement with clamp. |
| 0x0042bac0 | `bool __fastcall CConsole__MenuDown(void * this)` | Menu selection increment with clamp. |
| 0x0042bb30 | `bool __fastcall CConsole__MenuSelect(void * this)` | Current menu entry execute/apply path. |
| 0x0042c420 | `void * __fastcall CConsoleMenu__ctor_like_0042c420(void * this)` | ConsoleMenu-style object field initialization. |
| 0x0042c440 | `void __thiscall CConsoleMenu__LinkChildAtHead(void * this, void * child)` | Behavior-backed rename from `VFuncSlot_05_0042c440`; writes child parent pointer, links the old first child, updates the parent child head, and increments child count. |

Final read-back verified `16/16` metadata rows, `16/16` decompile exports, `118` xref rows, `1680` instruction rows, `16` tag rows, and queue totals of `5884` functions, `789` commented functions, `5095` commentless functions, `1989` undefined signatures, and `2276` `param_N` signatures.

---

## Wave 327 Fatal Signature Split (2026-05-12)

The next serialized tranche revisited the two localized fatal-error wrappers while correcting adjacent controller/input ownership. This fatal sub-slice is static Ghidra evidence only; it does not prove runtime fatal handling, caller recovery beyond the checked callsites, concrete layouts, local-variable/type recovery, BEA launch behavior, game patching, or rebuild parity.

| Address | Current saved Ghidra signature | Evidence summary |
|---------|--------------------------------|------------------|
| 0x0042c750 | `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_A(char * message, int callerContext)` | Caller instruction review shows two stack arguments and `RET 0x8`; Wave998 read-back shows the body builds the localized fatal prefix (`id 0xCC`) and unconditionally calls `FatalError__ExitProcess`. The second argument is preserved as caller-context/status because no semantic use was observed. |
| 0x0042d0b0 | `noreturn void __stdcall FatalError__ExitWithLocalizedPrefix_B(char * message)` | Mesh/resource failure callsites, `RET 0x4`, and Wave998 read-back support the single-message localized fatal wrapper variant ending through `FatalError__ExitProcess`. |

Final read-back for the full fatal/controller tranche verified `7/7` metadata rows, `7/7` decompile exports, `42` xref rows, `735` instruction rows, `7` tag rows, and queue totals of `5884` functions, `796` commented functions, `5088` commentless functions, `1989` undefined signatures, and `2269` `param_N` signatures.

---

## Function Details

### CConsole__Init (0x00429bc0)

**Current saved Ghidra signature:** `void __fastcall CConsole__Init(void * this)`

**Purpose:** Initializes the CConsole object, setting up member variables, allocating command/variable list nodes, and clearing buffers.

**Key Operations:**
1. Initializes member variables to default values (alpha=200, various flags)
2. If `DAT_00662f30` is set, initializes 20 "Console Line %d" entries (debug mode)
3. Allocates and initializes 3 linked list nodes (purpose unclear)
4. Clears 256-entry output line buffer (0x80 bytes each)
5. Clears 60-entry command history buffer (0x80 bytes each)
6. Clears 10-entry recent commands buffer (0x80 bytes each)
7. Calls `CConsole__InitKeyNameTable` (`0x0042bcf0`) and `CConsole__AddString` (`0x0042b840`) for table/init output setup.

**Xrefs to console.cpp:** 3 (lines 0xF2, 0xF7, 0xF8 - memory allocations)

---

### CConsole__RegisterBuiltinCommands (0x00429ef0)

**Current saved Ghidra signature:** `void __fastcall CConsole__RegisterBuiltinCommands(void * this)`

**Purpose:** Registers all built-in console commands and variables.

**Registered Commands:**

| Command | Description | Handler |
|---------|-------------|---------|
| `?` | Displays a list of console commands | 0x00VhLKb (obfuscated) |
| `ShowCmds` | Displays a list of console commands | (same as ?) |
| `ShowVars` | Displays a list of console variables | LAB_004296b0 |
| `Get` | Displays the value of a console variable | LAB_00429720 |
| `Set` | Sets the value of a console variable | LAB_004297e0 |
| `Bind` | Binds a command to a key | LAB_00429850 |
| `ListBinds` | Lists the current key bindings | LAB_00429a40 |
| `Echo` | Echos text to the console | LAB_00429a50 |
| `Exec` | Executes a console script from disk | LAB_00429a80 |
| `UseConfiguration` | Switches the Battle Engine to the specified configuration | LAB_00429ad0 |
| `Exit` | Exits the game | LAB_00429ab0 |
| `Quit` | Exits the game | LAB_00429ab0 |
| `ToggleMenu` | Toggle menu | LAB_00429b30 |
| `MemStats` | Output current memory stats to file | LAB_00429b50 |
| `DumpMem` | Dump memory map data | LAB_00429b90 |

**Registered Variables:**

| Variable | Description | Default | Storage |
|----------|-------------|---------|---------|
| `cg_consolealpha` | Alpha of the console background | 0 | this+0x2390 |

**Xrefs to console.cpp:** 7 (all line 0x325 - command/variable allocations)

---

### CConsole__RegisterCommand (0x0042af80)

**Current saved Ghidra signature:** `void __thiscall CConsole__RegisterCommand(void * this, char * name, char * description, void * callback, char flags)`

**Purpose:** Registers a console command by name with a callback function.

**Parameters:**
- `name` - Command name (max 32 chars)
- `description` - Help text (max 128 chars)
- `callback` - Function pointer called when command is executed
- `flags` - Command flags (purpose varies)

**Key Operations:**
1. Searches existing command list for duplicate name (using `stricmp` (0x00568390, was `FUN_00568390`))
2. If not found, allocates new CConsoleCmd (0xAC bytes) via `OID__AllocObject`
3. Links new command to head of command list at `this+0x2394`
4. Copies name to offset 0x00
5. Copies description to offset 0x20
6. Sets callback at offset 0xA0
7. Sets flags at offset 0xA4

**Xrefs to console.cpp:** 1 (line 0x325)

---

### CConsole__RegisterVariable (0x0042b040)

**Current saved Ghidra signature:** `void __thiscall CConsole__RegisterVariable(void * this, char * name, char * description, int varType, void * valuePtr, char flags1, char flags2)`

**Purpose:** Registers a console variable (cvar) with storage pointer.

**Parameters:**
- `name` - Variable name (max 32 chars)
- `description` - Help text (max 128 chars)
- `type` - Variable type identifier
- `valuePtr` - Pointer to the actual value storage
- `flags1` - First flag byte
- `flags2` - Second flag byte

**Key Operations:**
1. Searches existing variable list for duplicate name (using `stricmp` (0x00568390, was `FUN_00568390`))
2. If not found, allocates new CConsoleVar (0xB0 bytes) via `OID__AllocObject`
3. Links new variable to head of variable list at `this+0x2398`
4. Copies name to offset 0x00
5. Copies description to offset 0x20
6. Sets type at offset 0xA0
7. Sets valuePtr at offset 0xA4
8. Sets flags at offsets 0xA8 and 0xA9

**Xrefs to console.cpp:** 1 (line 0x33E)

---

### CConsole__ExecScript (0x0042ad30)

**Signature:** `void CConsole__ExecScript(void *this, char *script_path)`

**Purpose:** Implements `Exec` command behavior by reading a script file and executing each parsed line.

**Key Operations:**
1. Logs script execution start text (`"Executing script %s"`).
2. Opens script via `DXMemBuffer__OpenRead(...)`.
3. Reads file line-by-line until EOF.
4. Dispatches each line through `CConsole__ExecuteCommandLine`.
5. Logs file-not-found and completion paths.

---

### CConsole__ExecuteCommandLine (0x0042b9c0)

**Signature:** `void CConsole__ExecuteCommandLine(void *this, char *line)`

**Purpose:** Parses command token and dispatches to the matching registered callback in command list `this+0x2394`.

**Notes:**
- Uses `stricmp` against each command entry.
- On no match, emits `"Unknown command"`.

---

### CConsole__AddString (0x0042b840)

**Signature:** `void CConsole__AddString(void *this, char *format)`

**Purpose:** Core variadic string sink used across console/status/game systems to append text into rolling console buffers.

**Notes:**
- Splits newline-delimited formatted text into line entries.
- Mirrors to `DebugTrace` when console trace flag is enabled.
- Used by status/reporting helpers and command handlers.

---

### CConsole__Status (0x0042b500)

**Signature:** `void CConsole__Status(void *this, char *status_line)`

**Purpose:** Starts a nested status section, emits a `"<indent><status> [...]"` style line, and increments nesting depth.

---

### CConsole__StatusDone (0x0042b800)

**Signature:** `void CConsole__StatusDone(void *this, char *status_line, char success)`

**Purpose:** Completes an active status section by updating its line to success/failure text and decrementing nesting depth.

---

### CConsole__SetLoading (0x0042bbc0)

**Signature:** `void CConsole__SetLoading(void *this, char enabled, int load_texture)`

**Purpose:** Toggles loading-screen mode.

**Notes:**
- Enable path stamps start time, optionally loads `loadingscreen.tga`, and resets loading progress fields.
- Disable path releases loading-screen texture and logs elapsed loading time.

---

### CConsole__RenderLoadingScreen (0x0042c810)

**Signature:** `void CConsole__RenderLoadingScreen(void *this, int render_now, char mode)`

**Purpose:** Draws and refreshes loading-screen state using the active loading range/fraction fields and localized loading text.

**Notes:**
- Called by `CConsole__SetLoadingRange` and `CConsole__SetLoadingFraction`.
- Widely used by `CFrontEnd__Init`, `CGame__LoadResources`, `CGame__RestartLoopRunLevel`, and `CGame__RunLevel`.

---

### CConsole__SetLoadingRange (0x0042cf40)

**Signature:** `void CConsole__SetLoadingRange(void *this, float min_percent, float max_percent)`

**Purpose:** Updates loading interpolation endpoints (`this+0xB3D8`, `this+0xB3DC`), resets current value to min, and refreshes the loading screen.

---

### CConsole__SetLoadingFraction (0x0042cf70)

**Signature:** `void CConsole__SetLoadingFraction(void *this, float t)`

**Purpose:** Interpolates `mLoadingCurrent` between range endpoints and refreshes the loading screen.

---

## Wave404 FMV Play Console Command Hardening (2026-05-14)

Wave404 preserved the `con_fmv_play` name at `0x004655d0` and saved the signature `void __cdecl con_fmv_play(char * command_line)` with a proof-boundary comment and tags. Fresh read-back records a command-table DATA xref from `0x004656b5`, the `fmv_play <filename>` prefix-length guard, `DAT_006630cc` mirrored into `DAT_0089d69c`, the `CController__SetNonInteractiveSection` enter/leave gate, a call through frontend video object pointer `0x0089d690` vtable slot `+0x2c`, and syntax fallback through `CConsole__AddString`.

This is saved static Ghidra metadata and instruction/decompile/xref evidence. It does not prove runtime playback behavior, the exact frontend video object type/layout, exact source-body identity, BEA launch behavior, game patching, or rebuild parity.

---

## Additional Helper Mappings (2026-02-25)

These were mapped from behavior + caller/xref evidence during the headless deep pass:

| Address | Name | Summary |
|---------|------|---------|
| 0x0042a410 | CConsole__ResetLayoutForWindowHeight | Recomputes console geometry/layout fields from current window height |
| 0x0042a540 | CConsoleVar__GetTypeName | Converts cvar type enum to printable type name |
| 0x0042a5f0 | CConsoleVar__FormatValueToString | Converts cvar value to text using enum-guided formatting |
| 0x0042a770 | CConsole__FindCommandByName | Searches command list (`this+0x2394`) by case-insensitive name |
| 0x0042ae70 | CConsole__ShutdownAndFreeAllLists | Full list/aux-pointer cleanup path |
| 0x0042af20 | CConsole__ClearCommandAndVariableLists | Command/variable list-only cleanup path |
| 0x0042ba90 | CConsole__MenuUp | Moves console menu selection up (with clamp) |
| 0x0042bac0 | CConsole__MenuDown | Moves console menu selection down (with clamp) |
| 0x0042bb30 | CConsole__MenuSelect | Executes/applies current console menu selection |
| 0x00401480 | SharedVFunc__ReturnTrue_00401480 | Wave972 shared console-menu vtable target that returns true |
| 0x00429e30 | CConsoleRootMenu__GetName | Wave972 root-menu name vtable target; copies `Onslaught` |
| 0x00429e60 | CConsoleRootMenu__GetEntry | Wave972 root-menu fallback entry target; copies `???` |
| 0x00429e90 | CConsoleCommandMenu__GetName | Wave972 command-menu name target; copies `Console commands` |
| 0x0042c420 | CConsoleMenu__ctor_like_0042c420 | Initializes ConsoleMenu-style fields; exact source constructor identity remains deferred |
| 0x0042c440 | CConsoleMenu__LinkChildAtHead | Links a child menu node at the parent child-list head |
| 0x0042c460 | CConsoleMenu__UnlinkChild | Wave972 shared console-menu unlink target; removes child links and clears child parent/sibling fields |
| 0x0042c4b0 | CConsoleCommandMenu__GetNumEntries | Wave972 command-menu count target walking command list head `0x0066582c` |
| 0x0042c4d0 | CConsoleCommandMenu__GetEntry | Wave972 command-menu entry text formatter |
| 0x0042c530 | CConsoleCommandMenu__OnClick | Wave972 command-menu click target; writes selected command text and calls `PLATFORM__SetKeySink` |
| 0x0042c5e0 | CConsoleVarMenu__GetNumEntries | Wave972 cvar-menu count target walking cvar list head `0x00665830` |
| 0x0042c600 | CConsoleVarMenu__GetEntry | Wave972 cvar-menu entry formatter using `CConsoleVar__FormatValueToString` and `CConsoleVar__GetTypeName` |
| 0x0042c6a0 | CConsoleVarMenu__OnClick | Wave972 cvar-menu click target; formats `set %s ` and calls `PLATFORM__SetKeySink` |

---

## Related Functions (Not in console.cpp)

These functions are called by console.cpp functions:

| Address | Likely Name | Purpose |
|---------|-------------|---------|
| 0x005490e0 | OID__AllocObject | Memory allocation wrapper (with debug info) |
| 0x00568390 | stricmp | Case-insensitive string compare |
| 0x0055de9b | sprintf | String formatting |
| 0x00515db0 | Registry__SetStringValue_HKCU | Wave852 HKCU string persistence helper |
| 0x005159c0 | PLATFORM__SetKeySink | Key-sink handoff called by Wave972 command/cvar menu click targets |
| 0x0042bcf0 | CConsole__InitKeyNameTable | Initializes key-name table entries (Backspace/Return/Shift/num keys/etc.) |
| 0x0042b650 | CConsole__StatusUpdateLine | Internal status-line replacement helper used by `CConsole__StatusDone` and progress updates |

## Notes

1. **Debug String Usage:** The console.cpp path string is used for memory allocation tracking, appearing in calls to `OID__AllocObject` with line numbers (0xF2, 0xF7, 0xF8, 0x325, 0x33E).

2. **Linked List Pattern:** Both commands and variables use a singly-linked list pattern with the "next" pointer at the end of the structure.

3. **Global Flag:** `DAT_00662f30` controls debug console initialization - when set, creates numbered debug console lines.

4. **Console Alpha:** The `cg_consolealpha` variable controls background transparency, stored at offset 0x2390 with default 200.

5. **Command Handlers:** Many command handlers are at addresses like `LAB_004296b0` which are likely small thunks or direct implementations.
