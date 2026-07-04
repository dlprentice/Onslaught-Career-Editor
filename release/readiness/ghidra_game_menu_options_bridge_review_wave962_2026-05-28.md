# Ghidra Game Menu Options Bridge Review Wave962

Status: bounded static read-only review PASS
Date: 2026-05-28
Tag: `game-menu-options-bridge-review-wave962`

Wave962 re-reviewed the game-menu/options bridge after the Wave952 `CGameInterface` menu-control boundary recovery. The wave checked three primary Wave911 focused candidates and adjacent GameInterface/PauseMenu context with fresh serialized Ghidra exports. No mutation was needed: the earlier Wave465/Wave486 saved names, signatures, comments, and tags still match the current static evidence. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, and did not launch BEA.

## Scope

Primary Wave911 candidates:

| Address | Saved name | Result |
| --- | --- | --- |
| `0x004d0290` | `CControllerBackMenuItem__RenderBindingCapacityWarning` | Read-only PASS; still checks binding capacity, localized warning ids `0xe8`/`0xe9`, and forwards to `CMenuItem__RenderWithColor`. |
| `0x004d0e40` | `CGameMenu__InitBase` | Read-only PASS; still clears `+0x04` and installs compact vtable pointer `0x005dc72c`. |
| `0x004d3020` | `CEngine__SetOptionValueAndNotifyTarget` | Read-only PASS; still has one explicit `option_value` argument, writes `this+0x20`, mirrors through `0x00662ab0`, notifies optional target vfuncs `+0xe0` and `+0x154`, and ends with `RET 0x4`. |

Context anchors re-read: `0x0046c360 CGame__Init`, `0x004729e0 CGameInterface__ResetMenuState`, `0x00472b40 CGameInterface__HandleMenuSelection`, `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput`, `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions`, `0x004d0810 CPauseMenu__ButtonPressed`, `0x004d0db0 CPauseMenu__InitBindingPromptAction`, `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText`, and `0x004d0ff0 CPauseMenu__InitPauseSession`.

## Evidence

Fresh serialized Ghidra exports under `subagents/ghidra-static-reaudit/wave962-game-menu-options-bridge-review`:

- `12` metadata rows, `12` tag rows, `25` xref rows, `444` around-address instruction rows, `956` function-body instruction rows, `12` decompile-index rows, and `120` vtable-slot rows.
- Xrefs tie `0x004d0e40` to `0x004d0917 CPauseMenu__ButtonPressed`, `0x004d0de0` to `0x004d087d CPauseMenu__ButtonPressed`, `0x004d3020` to `0x00472d09 CGameInterface__HandleMenuSelection` plus `0x004d0b3a` and `0x004d0b55 CPauseMenu__ButtonPressed`, and `0x00472d50` to CGameInterface vtable data at `0x005dbc38`.
- Vtable evidence preserves `0x005dbc2c slot 3 -> 0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput`, compact menu-item vtable `0x005db440`, range vtables `0x005dc650` / `0x005dc664`, and compact game-menu base vtable `0x005dc72c`.
- Instruction evidence includes `0x004d02a5 PUSH 0xe8`, `0x004d02d7 PUSH 0xe9`, `0x004d02ff CALL 0x004a3290`, `0x004d0e49 MOV [EAX], 0x5dc72c`, `0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI`, `0x004d3048 CALL [EDX + 0xe0]`, `0x004d3066 CALL [EAX + 0x154]`, and `0x004d3075 RET 0x4`.

Verified Ghidra backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified
```

Backup summary: `19` files, `173542279` bytes, `DiffCount=0`.

Wave911 focused re-audit progress after Wave962: `309/1408 = 21.95%`.
Static export-contract function-quality closure remains `6152/6152 = 100.00%`.

Probe anchor: Wave962; game-menu-options-bridge-review-wave962; 0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning; 0x004d0e40 CGameMenu__InitBase; 0x004d3020 CEngine__SetOptionValueAndNotifyTarget; 0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput; 0x004d02a5 PUSH 0xe8; 0x004d02d7 PUSH 0xe9; 0x004d0e49 MOV [EAX], 0x5dc72c; 0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI; 0x005dbc2c slot 3; 0x005dc72c; 309/1408 = 21.95%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified; no mutation.

## Boundary

This wave proves only saved static retail Ghidra evidence tying the cluster to pause-menu button dispatch, controller binding-capacity UI, and engine option notification. Runtime pause-menu/controller-binding/options persistence behavior, concrete `CGameMenu` / `CPauseMenu` / `CGameInterface` / option-target layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.
