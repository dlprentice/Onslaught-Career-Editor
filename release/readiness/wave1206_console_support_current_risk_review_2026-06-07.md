# Wave1206 Console Support Current-Risk Review Readiness Note

Status: complete static read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Scope: `wave1206-console-support-current-risk-review`

Wave1206 reviewed `7 CConsole support current-risk rows` with fresh Ghidra read-back evidence and no mutation. The rows are `CConsole__Init`, `CConsoleVar__GetTypeName`, `CConsole__RegisterCommand`, `FatalError__ExitWithLocalizedPrefix_A`, `FatalError__ExitWithLocalizedPrefix_B`, `CConsole__Printf`, and `CConsole__PrintfNoNewline`.

Read-back evidence:

- `7` metadata rows, `7` tag rows, `426 xref rows`, `630 instruction rows`, and `7 decompile rows`.
- Read-only review: no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.
- Codex read-only consults used; no Cursor/Composer.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-023000_post_wave1206_console_support_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Static closure remains `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`.
- Active current-risk progress is `1083/1179 = 91.86%`; remaining active focused work: 96.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.
- Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.
- Legacy additive counter is deprecated (`1114/1179`), with 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

What this proves:

- The seven target function rows exist in the saved Ghidra project with bounded names, signatures, comments, and tags.
- Fresh xrefs tie the rows to console startup, console menu CVar display, built-in command registration, fatal resource paths, broad diagnostic print callsites, and script print execution.
- The engine/platform support map now has current-risk read-back for the console/fatal/diagnostic support layer.
- README active percentages are not a source of truth; the measurement register and generated ledger own measurable static status.

What remains unproven:

- Runtime console availability.
- Runtime console behavior.
- Runtime fatal behavior.
- Devmode or cheat behavior.
- Exact concrete layouts.
- Exact source-body identity.
- Callback ABI completeness.
- BEA patching behavior.
- Gameplay outcomes, visual QA, rebuild parity, and no-noticeable-difference parity.

Probe token anchor: Wave1206; wave1206-console-support-current-risk-review; 1083/1179 = 91.86%; 7 CConsole support current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 96; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; unique-address accounting; legacy additive counter is deprecated; 1114/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; CConsole__Init; CConsoleVar__GetTypeName; CConsole__RegisterCommand; FatalError__ExitWithLocalizedPrefix_A; FatalError__ExitWithLocalizedPrefix_B; CConsole__Printf; CConsole__PrintfNoNewline; 0 / 0 / 0; 6411/6411 = 100.00%; 426 xref rows; 630 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260607-023000_post_wave1206_console_support_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
