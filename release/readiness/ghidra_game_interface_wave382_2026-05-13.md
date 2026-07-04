# Ghidra GameInterface Wave382 Readiness Note

Status: public-safe static RE evidence
Date: 2026-05-13

## Summary

Wave382 serialized a focused headless dry/apply/read-back pass over `8` saved Ghidra targets in the GameInterface / pause-menu area. The pass corrected stale generic or owner-biased labels, hardened signatures/comments/tags, and narrowed the prior `0x00472b40` signature to one explicit controller parameter after callsite instruction review. This is saved static retail Ghidra evidence only.

## Saved Targets

| Address | Saved signature | Evidence summary |
| --- | --- | --- |
| `0x004729d0` | `void __fastcall CGameInterface__ctor_base(void * this)` | Constructor-style base body for the global GameInterface object; installs the `0x005dbc2c` vtable and initializes monitor/control state. |
| `0x004729e0` | `void __fastcall CGameInterface__ResetMenuState(void * this)` | Resets fade/selection/menu-active fields, enables six menu entries, enables background rendering, and sets menu mode `1`; called from CGame init paths. |
| `0x00472a10` | `void __fastcall CGameInterface__InitResources(void * this)` | Source-parity resource init loads `Interface_Joypad.tga` and `hud\\Menu_background.tga` into GameInterface texture slots. |
| `0x00472a50` | `void __fastcall CGameInterface__Shutdown(void * this)` | Source-parity shutdown releases texture references, clears slots, and runs monitor shutdown core logic. |
| `0x00472a90` | `void __fastcall CGameInterface__ToggleMenuDisplay(void * this)` | Source-parity menu toggle flips menu-active state, selects the first enabled entry, clears opening state, and switches mouse input state. |
| `0x00472ad0` | `void __fastcall CGameInterface__AdvanceMenuSelectionWithWrap(void * this)` | Corrects older `UISelectionList__AdvanceToNextEnabledWithWrap` label; advances selected menu entry with wrap-around and disabled-entry checks, then plays move SFX when selection changes. |
| `0x00472b40` | `void __thiscall CGameInterface__HandleMenuSelection(void * this, void * controller)` | Corrects older `CDXEngine__HandlePauseOptionsSelection` label; handles resume, message focus transfer, frontend quit/configuration paths, option submenu transitions, god-option notification, and `DAT_008a9ab8` toggle. Callsite evidence shows one explicit controller parameter; the older third parameter was a decompiler artifact. |
| `0x00472f10` | `void __fastcall CGameInterface__Render(void * this)` | Corrects older `CDXEngine__RenderAndProcessPauseOptionsOverlay` label; renders and processes the pause/menu overlay from `CDXEngine::PostRender`, including joypad art, background, localized text, cursor/click selection, and dispatch to the selected controller. |

## Validation

- `py -3 tools\ghidra_game_interface_wave382_probe_test.py` passed with `2/2` tests.
- `cmd.exe /c npm run test:ghidra-game-interface-wave382` passed with status `PASS`, `8` targets, `6` xref evidence hits, `10` instruction evidence hits, and `7` callsite evidence hits.
- `py -3 -m py_compile tools\ghidra_game_interface_wave382_probe.py tools\ghidra_game_interface_wave382_probe_test.py` passed.
- Headless dry/apply reported dry `updated=0 skipped=8 renamed=0 would_rename=8 missing=0 bad=0` and apply `updated=8 skipped=0 renamed=8 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back verified `8` metadata rows, `8` decompile exports, `11` xref rows, `840` instruction rows, `8` tag rows, and `369` callsite-instruction rows.
- The refreshed live queue reports `6026` functions, `1410` commented functions, `4616` commentless functions, `1939` undefined signatures, and `1917` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1410/6026 = 23.40%`, strict clean-signature `1348/6026 = 22.37%`.
- The live Ghidra project backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_164352_post_wave382_game_interface_verified` with `19` files, `153684871` bytes, and `HashDiffCount=0`.

## Not Proven

- Runtime pause-menu, input, text, option, god-toggle notification, texture lifetime, or visual rendering behavior is not proven by this static pass.
- Exact source file body, concrete GameInterface layout, local variable names, and structure types remain open.
- The ambiguous neighboring `0x0046c210` / `0x0046c2b0` / `0x0046c2d0` constructor/destructor-shaped functions remain deferred because current xref context overlaps CGame and CFrontEndVideo-style ownership.
- BEA launch behavior, executable patching, packaged-app behavior, and rebuild parity remain unproven.
