# Wave1134 Console Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1134-console-current-risk-review`

Wave1134 accounts for `2 rows` from the Wave1108 current focused continuity denominator as a console registration/layout cluster. This wave uses fresh Ghidra export evidence as a read-only review and makes no mutation. Current focused accounting moves to `186/1179 = 15.78%` of the continuity denominator. The current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 993. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00429ef0 CConsole__RegisterBuiltinCommands` | Called from `0x0046c385 CGame__Init`; registers/reuses built-in command nodes through `CConsole__FindCommandByName`, allocates `0xac`-byte command records when absent, populates names/descriptions/callbacks/flags/list links, and registers the `cg_consolealpha` cvar through the register-variable path. |
| `0x0042a410 CConsole__ResetLayoutForWindowHeight` | Called from `0x004eff37 CLTShell__InitializeRuntimeAndLoadCoreResources`; calls `PLATFORM__GetWindowHeight` and recomputes console/window layout fields at `this+0x2388`, `this+0x2384`, and `this+0xb3cc`. |

Context rows re-read: `0x00429bc0 CConsole__Init`, `0x0042a540 CConsoleVar__GetTypeName`, `0x004416e0 CConsole__ResetStatusHistoryBuffer`, `0x00441740 CConsole__Printf`, `0x004418a0 CConsole__PrintfNoNewline`, `0x004419e0 CConsole__RenderStatusHistoryOverlay`, `0x0042af80 CConsole__RegisterCommand`, and `0x0042b040 CConsole__RegisterVariable`.

Mutation status:

- Read-only review.
- No Ghidra mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Primary metadata/tag/xref/instruction/decompile exports: `2` / `2` / `2` / `418` / `2`.
- Context metadata/tag/xref/instruction/decompile exports: `8` / `8` / `470` / `679` / `8`.
- Primary logs report `targets=2 found=2 missing=0`, `rows=2 missing=0`, `Wrote 2 rows`, `Wrote 418 function-body instruction rows`, and `targets=2 dumped=2 missing=0 failed=0`.
- Context logs report `targets=8 found=8 missing=0`, `rows=8 missing=0`, `Wrote 470 rows`, `Wrote 679 function-body instruction rows`, and `targets=8 dumped=8 missing=0 failed=0`.
- Final backup after the read-only evidence wave: `G:\GhidraBackups\BEA_20260605-104845_post_wave1134_console_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`.
- Codex read-only consult recommended a later GroundAttack/GillMHead cluster; root kept the already-exported next uncovered current-risk console pair and preserved the consult's cluster as a future-candidate note.

What this proves:

- The two target rows still exist in the saved Ghidra project with expected names and signatures.
- The saved comments, xrefs, instruction windows, and decompile rows remain coherent with the prior console core/status and engine/platform support evidence.
- The wave narrows current-risk accounting for this console registration/layout pair without changing the saved Ghidra project.
- The Ghidra project was backed up and verified after the read-only evidence wave.

What remains separate:

- Runtime console command behavior.
- Runtime cvar behavior.
- Runtime console layout/status overlay behavior.
- Exact source-body identity.
- Concrete `CConsole`, `CConsoleCmd`, `CConsoleVar`, callback, and layout schemas.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
