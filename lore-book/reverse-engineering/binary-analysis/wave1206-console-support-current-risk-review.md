# Wave1206 Console Support Current-Risk Review

Status: complete static read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1206-console-support-current-risk-review`

Wave1206 reviewed `7 CConsole support current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra metadata, tags, xrefs, instructions, and decompile exports. The wave made no mutation: no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

| Address | Static evidence |
| --- | --- |
| `0x00429bc0 CConsole__Init` | Initializes retail console defaults, command/variable list heads, output/history buffers, key-name table, key sink state, startup console text, and HKCU registry persistence path. Xref: `CLTShell__InitializeRuntimeAndLoadCoreResources`. |
| `0x0042a540 CConsoleVar__GetTypeName` | Maps the CConsoleVar type enum at `+0xa0` to printable labels including `DWORD`, `string`, `float`, `fvector`, `fmatrix`, and unknown fallback. Xref: `CConsoleVarMenu__GetEntry`. |
| `0x0042af80 CConsole__RegisterCommand` | Registers or updates a command by case-insensitive name; allocates `0xac` bytes when absent, copies name/description text, stores callback at `+0xa0`, flags at `+0xa4`, and next pointer at `+0xa8`. Xrefs include built-in console, game, sound, render, landscape, shadows, and atmospherics setup. |
| `0x0042c750 FatalError__ExitWithLocalizedPrefix_A` | Builds a fatal message from localization id `0xcc`, separator string `0x00624624`, and caller text, then exits through `FatalError__ExitProcess`; `RET 0x8` still preserves the two-argument wrapper boundary. |
| `0x0042d0b0 FatalError__ExitWithLocalizedPrefix_B` | Same localized-prefix fatal wrapper shape with one message argument; xrefs tie this variant to mesh/resource deserialize paths including `CMesh__Deserialize`. |
| `0x00441740 CConsole__Printf` | Variadic console print sink using a 700-byte stack buffer, `vsprintf`, `DebugTrace` newline mirroring, optional file append, and the 30-slot status/history ring. |
| `0x004418a0 CConsole__PrintfNoNewline` | Variadic no-newline console print sink using a 256-byte stack buffer, optional file append, and the same 30-slot status/history ring without the `DebugTrace` newline mirror. |

Evidence counts:

- Fresh exports: `7` metadata rows, `7` tag rows, `426 xref rows`, `630 instruction rows`, and `7 decompile rows`.
- Verified backup: `G:\GhidraBackups\BEA_20260607-023000_post_wave1206_console_support_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Codex read-only consults used; no Cursor/Composer.
- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Active current-risk progress is `1083/1179 = 91.86%`; remaining active focused work: 96.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.
- Legacy additive counter is deprecated (`1114/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Contract impact:

- `console.cpp/_index.md` now has fresh current-risk read-back for console initialization, CVar type-label formatting, command registration, localized fatal wrappers, and console print sinks.
- These rows strengthen the engine/platform support map because they connect startup diagnostics, fatal-error reporting, console-file/status history, registry persistence, and cross-system debug output.
- The active measurement path remains `static-reaudit-current-risk-ledger.json`, `static-reaudit-progress.json`, `static-reaudit-accounting-guard.md`, `static-reaudit-measurement-register.md`, `mapped-systems.md`, and `wave1108-current-risk-rank.md`.
- `wave1108-current-focused-candidates.tsv` is a live focused-candidate artifact, not the complete active denominator by itself; the `1179` current-risk continuity denominator is enforced by the generated ledger and accounting guard.
- README active percentages are intentionally not an authority; the guard rejects duplicated active `/1179` README counters so the measurement register stays the front door.

Boundary:

This is static retail Ghidra evidence only. Runtime console availability, runtime console behavior, runtime fatal behavior, devmode behavior, cheat behavior, exact concrete layouts, exact source-body identity, callback ABI completeness, BEA patching behavior, gameplay outcomes, visual QA, rebuild parity, and no-noticeable-difference parity remain separate proof. The static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference.

Probe token anchor: Wave1206; wave1206-console-support-current-risk-review; 1083/1179 = 91.86%; 7 CConsole support current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 96; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; unique-address accounting; legacy additive counter is deprecated; 1114/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; CConsole__Init; CConsoleVar__GetTypeName; CConsole__RegisterCommand; FatalError__ExitWithLocalizedPrefix_A; FatalError__ExitWithLocalizedPrefix_B; CConsole__Printf; CConsole__PrintfNoNewline; 0 / 0 / 0; 6411/6411 = 100.00%; 426 xref rows; 630 instruction rows; 7 decompile rows; G:\GhidraBackups\BEA_20260607-023000_post_wave1206_console_support_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
