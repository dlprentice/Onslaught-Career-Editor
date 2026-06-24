# Ghidra CFEPMain Menu Review Wave953 Readiness Note

Status: complete read-only static evidence
Date: 2026-05-28
Scope: `cfepmain-menu-review-wave953`

Mutation status: no mutation.

Wave953 re-reviewed the CFEPMain retail main-menu page cluster after the Wave951/Wave952 GameInterface pause-menu work. The pass was read-only: no Ghidra mutation, no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and no BEA launch.

Primary CFEPMain targets:

| Address | Evidence |
| --- | --- |
| `0x004621b0 CFEPMain__Init` | Seeds CFEPMain selection/timer state at observed offsets and returns success from the CFEPMain vtable slice. |
| `0x004621d0 CFEPMain__GetMenuType` | `int __cdecl` no-argument getter returning constant menu type `7`. |
| `0x004621e0 CFEPMain__GetActionCount` | `int __stdcall` stack-only `menu_state` switch with career-in-progress, controller-count, and dialog/memory-card gating. |
| `0x00462250 CFEPMain__ButtonPressed` | Handles main-menu up/down/select and language-cycling input IDs `0x2a`, `0x2b`, `0x2c`, `0x36`, and `0x37`; this is distinct from the Wave952 CGameInterface pause-menu `0x2a..0x39` dispatch. |
| `0x004623e0 CFEPMain__DoAction` | Routes New Game, Continue, Load, Options, Multiplayer, Goodies, Credits/About, and Return actions through page globals and `CFrontEnd__SetPage`. |
| `0x00462640 CFEPMain__Process` | Preserves the FEPMain.cpp debug-path save/defaultoptions path with `CCareer__Save` and `CFEPOptions__WriteDefaultOptionsFile`. |
| `0x00462b70 CFEPMain__RenderPreCommon` | `void __stdcall` stack-only transition/destination pre-render helper for the shared main-menu layer. |
| `0x00462c90 CFEPMain__Update` | `void __stdcall` stack-only menu-state mapper to `FrontEndText` token lookups and fallback token `8`. |
| `0x00462d40 CFEPMain__Render` | Uses selection state, transition/destination arguments, language arrows, pulse state, and state-specific menu rows. |
| `0x004644d0 CFEPMain__TransitionNotification` | Resets transition/timer state and mirrors career-in-progress/selection state. |
| `0x00464520 CFEPMain__ActiveNotification` | Clears active-selection/timer fields; the observed page argument is ignored. |

Context anchors:

- Frontend owner/render context: `0x004662a0 CFrontEnd__Init`, `0x00466ae0 CFrontEnd__SetPage`, `0x004679e0 CFrontEnd__RenderPreCommonFade`, and `0x00468770 CFrontEnd__PlaySound`.
- Adjacent shared/demo frontend context: `0x0044d390 FEMessBox__Create` and `0x00457ee0 CFEPDemoMain__DoAction`.
- Debug path string: `0x00629414` -> `C:\dev\ONSLAUGHT2\FEPMain.cpp`.

Read-back evidence:

- Fresh exports: 17 metadata rows, 17 tag rows, 257 xref rows, 2935 instruction rows, 17 decompile rows, and 56 vtable rows.
- Vtable evidence preserves the Wave401 correction: `0x005dbae4` is the full CFEPMain dispatch slice, `0x005dbaf0` starts with `CFEPMain__ButtonPressed`, and `0x005dbb00` starts with `CFEPMain__ActiveNotification`.
- Existing Wave401 probe continuity: `py -3 tools\ghidra_fepmain_wave401_probe.py --check` returned `status=PASS targets=11 failures=0`.
- Wave911 focused re-audit progress after Wave953 is `280/1408 = 19.89%`.
- Static export-contract function-quality closure remains `6151/6151 = 100.00%`.
- Verified read-only backup: `G:\GhidraBackups\BEA_20260528-093826_post_wave953_cfepmain_menu_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

What remains unproven:

- Exact CFEPMain source-file body identity; `FEPMain.cpp` is absent from the current Stuart source snapshot.
- Concrete CFEPMain object layout beyond observed static offsets.
- Runtime main-menu input/render/save/defaultoptions behavior.
- BEA patching behavior.
- Rebuild parity.
