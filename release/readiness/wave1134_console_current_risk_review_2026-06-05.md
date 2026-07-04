# Wave1134 Console Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1134-console-current-risk-review`

Wave1134 re-read two console current-risk rows with fresh Ghidra metadata, tag, xref, instruction, and decompile exports: `0x00429ef0 CConsole__RegisterBuiltinCommands` and `0x0042a410 CConsole__ResetLayoutForWindowHeight`.

Probe anchor: Wave1134; `wave1134-console-current-risk-review`; `2 rows`; `186/1179 = 15.78%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 993; console registration/layout cluster; fresh Ghidra export; read-only review; no mutation; static debt `0 / 0 / 0`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`; previous completed backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`.

Read-back evidence:

- Primary exports: `2` metadata rows, `2` tag rows, `2` xref rows, `418` instruction rows, and `2` decompile rows.
- Context exports: `8` metadata rows, `8` tag rows, `470` xref rows, `679` instruction rows, and `8` decompile rows.
- Context rows: `0x00429bc0 CConsole__Init`, `0x0042a540 CConsoleVar__GetTypeName`, `0x004416e0 CConsole__ResetStatusHistoryBuffer`, `0x00441740 CConsole__Printf`, `0x004418a0 CConsole__PrintfNoNewline`, `0x004419e0 CConsole__RenderStatusHistoryOverlay`, `0x0042af80 CConsole__RegisterCommand`, and `0x0042b040 CConsole__RegisterVariable`.
- Current focused accounting: `186/1179 = 15.78%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 993.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Mutation status:

- No Ghidra mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

What this proves:

- The two target rows still exist in the saved Ghidra project with expected saved names and signatures.
- Fresh xrefs, instruction windows, and decompile rows still support the console built-in registration and window-height layout static contracts.
- The project backup was verified after the read-only evidence wave.

What remains separate:

- Runtime console command behavior.
- Runtime cvar behavior.
- Runtime layout/status overlay behavior.
- Exact source-body identity and concrete `CConsole`/`CConsoleCmd`/`CConsoleVar` layouts.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.
