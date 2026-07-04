# PauseMenu.cpp Functions

> Source File: PauseMenu.cpp | Binary: BEA.exe

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Pause menu UI implementation. Handles the in-game pause menu, including cheat-dependent options like the god mode toggle.

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CPauseMenu` as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CPauseMenu__ResumeGameAndPersistOptions`, `CPauseMenu__ButtonPressed`, `CController__DoMappings`, and `CGame__Pause`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime pause/input/options persistence behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Wave923 (`hud-radar-pause-render-review-wave923`) re-reviewed `0x004d15d0 CPauseMenu__VFunc_03_HandleMenuControlInput` as part of a HUD/radar/pause/sprite/D3D visible-render support slice. Fresh metadata/tags/xref/instruction/decompile evidence kept the Wave474 three-stack-argument pause-menu vtable-slot claim intact; no mutation was needed. Wave911 focused re-audit progress after this slice is `86/1408 = 6.11%`, while export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-210516_post_wave923_hud_radar_pause_render_review_verified`. Runtime pause-menu input/render behavior, concrete CPauseMenu/layout constants, exact source-body identity, patch behavior, and rebuild parity remain separate proof.

Wave962 (`game-menu-options-bridge-review-wave962`) re-reviewed the pause-menu side of the game-menu/options bridge read-only: `0x004d0810 CPauseMenu__ButtonPressed`, `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText`, `0x004d0e40 CGameMenu__InitBase`, `0x004d3020 CEngine__SetOptionValueAndNotifyTarget`, `0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning`, and `0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput`. Fresh evidence ties the binding-capacity warning ids through `0x004d02a5 PUSH 0xe8` and `0x004d02d7 PUSH 0xe9`, temporary menu base setup through `0x004d0e49 MOV [EAX], 0x5dc72c` and `0x005dc72c`, option propagation through `0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI`, and GameInterface continuity through `0x005dbc2c slot 3`. No mutation was needed. Wave911 focused re-audit progress after Wave962 is `309/1408 = 21.95%`; static export-contract closure remains `6152/6152 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified`. Runtime pause-menu/controller-binding/options persistence behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave962; game-menu-options-bridge-review-wave962; 0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning; 0x004d0e40 CGameMenu__InitBase; 0x004d3020 CEngine__SetOptionValueAndNotifyTarget; 0x00472d50 CGameInterface__VFunc_03_HandleMenuControlInput; 0x004d02a5 PUSH 0xe8; 0x004d02d7 PUSH 0xe9; 0x004d0e49 MOV [EAX], 0x5dc72c; 0x004d302e MOV [EAX*0x4 + 0x662ab0], EDI; 0x005dbc2c slot 3; 0x005dc72c; 309/1408 = 21.95%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-132411_post_wave962_game_menu_options_bridge_review_verified; no mutation.

Wave1023 (`frontend-options-pause-menu-review-wave1023`) re-read the PauseMenu/SimpleGameMenu tail with no mutation: `0x004d04b0 CPauseMenu__scalar_deleting_dtor`, `0x004d0510 CPauseMenu__LoadPauseTextures`, `0x004d05e0 CPauseMenu__dtor_base`, `0x004d11d0 CPauseMenu__Render`, `0x004d1730 CSimpleGameMenu__scalar_deleting_dtor`, and `0x004d1750 CSimpleGameMenu__dtor_base`. Fresh exports kept the Wave465/Wave474/Wave481 comments and signatures intact, including `FE_Blank.tga` texture loading, `CMonitor__Shutdown` destructor cleanup, `CDXEngine__PostRender` caller evidence, and simple-game-menu active-reader/range cleanup. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified`. Runtime pause-menu/simple-game-menu rendering or input behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof.

Wave1119 (`wave1119-mixed-score26-current-risk-review`) re-read the current-risk PauseMenu/GameMenu cleanup bridge with no mutation: `0x004d05e0 CPauseMenu__dtor_base`, `0x004d0e40 CGameMenu__InitBase`, and `0x004d1750 CSimpleGameMenu__dtor_base`. Fresh read-only evidence verified scalar-deleting destructor callers at `0x004d04b3` and `0x004d1733`, the `CPauseMenu__ButtonPressed` caller at `0x004d0917`, pause texture/shared blank texture cleanup, `PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c`, active-reader/range destruction, and monitor shutdown. Current focused accounting moves to `110/1179 = 9.33%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`. Runtime UI behavior, exact concrete layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1136 (`wave1136-pausemenu-current-risk-review`) re-read `8 rows` from the uncovered Wave1108 current-risk PauseMenu/SimpleGameMenu current-risk cluster with fresh Ghidra export evidence and read-only review; no mutation was needed. Primary rows are `0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning`, `0x004d04b0 CPauseMenu__scalar_deleting_dtor`, `0x004d0510 CPauseMenu__LoadPauseTextures`, `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions`, `0x004d0db0 CPauseMenu__InitBindingPromptAction`, `0x004d11d0 CPauseMenu__Render`, `0x004d15d0 CPauseMenu__VFunc_03_HandleMenuControlInput`, and `0x004d1730 CSimpleGameMenu__scalar_deleting_dtor`. Fresh read-only evidence verified DATA vtable xrefs `0x005de604`, `0x005de700`, `0x005de708`, and `0x005de720`, texture loading from `CGame__RunLevel`, resume/persist callers from `CPauseMenu__ButtonPressed` and `CPauseMenu__VFunc_03_HandleMenuControlInput`, render callers from `CDXEngine__PostRender` and `CFEPOptions__Update`, binding warning ids `0xe8` / `0xe9`, and `RET 0x0c` / `RET 0x4` stack cleanup on the binding prompt and scalar-deleting destructors. Context rows were re-read as context `0x004d04d0 CPauseMenu__ReloadSharedBlankTexture`, context `0x004d05e0 CPauseMenu__dtor_base`, context `0x004d0810 CPauseMenu__ButtonPressed`, context `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText`, context `0x004d0e40 CGameMenu__InitBase`, context `0x004d0ff0 CPauseMenu__InitPauseSession`, and context `0x004d1750 CSimpleGameMenu__dtor_base`. Current focused accounting moves to `204/1179 = 17.30%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 975; static debt remains `0 / 0 / 0`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified`; previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`. Runtime pause-menu behavior, runtime controller-binding behavior, runtime options/defaultoptions persistence behavior, runtime render behavior, exact concrete layouts, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

## Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x004cde60 | [PauseMenu__Init](./PauseMenu__Init.md) | Pause menu constructor - calls IsCheatActive(3) for god mode toggle |
| 0x004d04b0 | CPauseMenu__scalar_deleting_dtor | Scalar-deleting destructor wrapper - calls `CPauseMenu__dtor_base` and conditionally frees `this` (Wave465 corrected) |
| 0x004d04d0 | CPauseMenu__ReloadSharedBlankTexture | Reloads shared blank texture used by pause-menu panel rendering |
| 0x004d0510 | CPauseMenu__LoadPauseTextures | Loads pause-menu texture resources |
| 0x004d05e0 | CPauseMenu__dtor_base | Destructor body - restores vtable, destroys child menu ranges, clears prompt/menu objects, releases pause textures, and shuts down monitor state (Wave465 corrected) |
| 0x004d06e0 | [CPauseMenu__ResumeGameAndPersistOptions](./CPauseMenu__ResumeGameAndPersistOptions.md) | Resume/exit helper that also persists options/defaultoptions state |
| 0x004d0810 | CPauseMenu__ButtonPressed | Pause-menu button dispatch handler |
| 0x0044ae20 | CPauseMenu__InitAndSetActiveReader | Binding-prompt helper that stores an action id and binds an active reader |
| 0x004d0db0 | CPauseMenu__InitBindingPromptAction | Initializes binding-prompt action node with target menu item and dispatch id |
| 0x004d0e40 | CGameMenu__InitBase | Compact temporary game-menu base initializer used by pause-menu button-dispatch paths (Wave465 corrected) |
| 0x004d0de0 | CPauseMenu__GetBindingCapacityWarningText | Control-binding capacity localized warning-text helper (Wave824 corrected) |
| 0x004d0ff0 | CPauseMenu__InitPauseSession | Initializes pause-session state/resources |
| 0x004d10b0 | CPauseMenu__DeactivatePauseSession | Deactivates pause-session state/resources; supersedes the older GillMHead pause-latch label |
| 0x004d11d0 | [CPauseMenu__Render](./CPauseMenu__Render.md) | Pause-menu render body; Wave481 corrected stale CEngine ownership and title-text return type |
| 0x004d15d0 | [CPauseMenu__VFunc_03_HandleMenuControlInput](./CPauseMenu__VFunc_03_HandleMenuControlInput.md) | Pause-menu vtable-slot control-input handler; Wave474 removed stale extra stack argument |
| 0x004d1730 | [CSimpleGameMenu__scalar_deleting_dtor](./CSimpleGameMenu__scalar_deleting_dtor.md) | Scalar-deleting destructor wrapper for compact simple game-menu objects |
| 0x004d1750 | [CSimpleGameMenu__dtor_base](./CSimpleGameMenu__dtor_base.md) | Destructor body that clears active-reader nodes, embedded range state, and monitor base |

## Key Observations

### God Mode Toggle Discovery

At address 0x004ce328, PauseMenu UI logic uses `IsCheatActive(3)` (Maladim) for gating and uses `g_bGodModeEnabled` as the toggle state. This was a key discovery for separating:
1. Cheat gating (save-name substring check)
2. UI toggle state (persisted)
3. Per-player invincibility (runtime `CPlayer::mIsGod`; **not** a known persisted field in Steam saves)

- The pause menu checks `IsCheatActive(3)` (index 3 = "Maladim" cheat code)
- If active, a god mode toggle option appears in the pause menu
- The toggle reads/writes `g_bGodModeEnabled` (CCareer offset `0x2494`, file offset `0x2496`)

### Important Offsets

| CCareer Offset | File Offset | Field | Purpose |
|----------------|-------------|-------|---------|
| 0x2494 | 0x2496 | g_bGodModeEnabled | Pause-menu toggle state (cheat-gated) |
| 0x2498 | 0x249A | (unused/padding) | Observed 0 in Steam saves/options; preserve |
| 0x249C | 0x249E | Invert Y (Flight/Jet) (P1) | Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`) |
| 0x24A0 | 0x24A2 | Invert Y (Flight/Jet) (P2) | Steam stores `0=Off`, non-zero=On (verified in `FUN_00407540`) |
| 0x24A4 | 0x24A6 | Invert Y (Walker) (P1) | Steam stores `0=Off`, non-zero=On (verification pending on walker path) |
| 0x24A8 | 0x24AA | Invert Y (Walker) (P2) | Steam stores `0=Off`, non-zero=On (verification pending on walker path) |

**NOTE (Feb 2026):** In the retail build, `CCareer::Load/Save` copies bytes from/to `file + 2` after a 16-bit version word. So file offsets are `file_off = 0x0002 + career_off` (the header often *looks* like a 4-byte `0x00004BD1` if the first CCareer dword is 0).

### Binding Prompt Active Reader Helper (Wave 365)

`0x0044ae20` was signature/comment/tag hardened on 2026-05-13 as `CPauseMenu__InitAndSetActiveReader` with saved signature:

```cpp
void* __thiscall CPauseMenu__InitAndSetActiveReader(void* this, int action_id, void* reader);
```

Static retail evidence shows the helper initializes the local active-reader cell, stores `action_id` into the 16-bit field at `+0x04`, binds `reader` through `CGenericActiveReader__SetReader`, returns `this`, and ends with `ret 0x8`. Exact source identity, concrete pause-menu action layout, runtime control-binding behavior, and rebuild parity remain unproven.

### Pause Session Activate/Deactivate Helpers (Wave 390)

Wave 390 hardened `0x004d0ff0` and corrected `0x004d10b0` to the pause-menu owner after read-back of `CGame__Pause` / `CGame__UnPause` callsites and Stuart `CGame::Pause()` / `CGame::UnPause()` source. The current saved evidence supports:

- `0x004d0ff0` as `CPauseMenu__InitPauseSession`, called on `CGame::mPauseMenu` during pause activation.
- `0x004d10b0` as `CPauseMenu__DeactivatePauseSession`, called on `CGame::mPauseMenu` during unpause/deactivation.

This corrects the older GillMHead-specific owner claim. UI runtime behavior, concrete `CPauseMenu` layout, exact source method names, locals/types, and rebuild parity remain unproven.

### PauseMenu Tail / CGameMenu Helpers (Wave 465)

Wave465 hardened ten compact menu-item and pause-menu tail targets. The PauseMenu-owned subset corrected:

- `0x004d04b0` to `CPauseMenu__scalar_deleting_dtor`.
- `0x004d05e0` to `CPauseMenu__dtor_base`.
- `0x004d0510`, `0x004d06e0`, `0x004d0810`, and `0x004d0db0` to explicit `pause_menu` / `menu_item` / `action_id` signatures with bounded comments.
- `0x004d0e40` to `CGameMenu__InitBase`, a compact initializer used while `CPauseMenu__ButtonPressed` builds temporary menu ranges.

Evidence artifacts live under `subagents/ghidra-static-reaudit/wave465-pausemenu-tail-current/`; the public-safe release note is `release/readiness/ghidra_pausemenu_tail_wave465_2026-05-16.md`.

This is static retail-binary evidence only. Runtime pause-menu input/render/save behavior, exact layouts, exact source identities, BEA launch, game patching, and rebuild parity remain unproven.

### MenuItem/PauseMenu Raw Head (Wave824)

Wave824 static read-back (`menuitem-pausemenu-raw-head-wave824`, `wave824-readback-verified`) hardened two PauseMenu-owned raw-head rows: `0x004d04d0 CPauseMenu__ReloadSharedBlankTexture` and `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-190751_post_wave824_menuitem_pausemenu_raw_head_verified`.

| Address | Saved state | Static evidence |
| --- | --- | --- |
| `0x004d04d0 CPauseMenu__ReloadSharedBlankTexture` | `void __cdecl CPauseMenu__ReloadSharedBlankTexture(void)` | Releases cached `DAT_0082b490` through `CTexture__DecrementRefCountFromNameField(DAT_0082b490+8)`, clears the global, reloads `FrontEnd_v2/FE_Blank.tga` through `CTexture__FindTexture(name,4,0,1,0,1)`, and stores the handle back to `DAT_0082b490`. |
| `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText` | `short * __cdecl CPauseMenu__GetBindingCapacityWarningText(void)` | Checks `Controls__FindFirstFreeBindingSlot(0)` and returns `Localization__GetStringById(0xe8)` when player-one slots are full; when `0 < DAT_008a9ac0 < 9` and `CGame__IsMultiplayer(&DAT_008a9a98)` is true, checks slot 1 and returns `Localization__GetStringById(0xe9)` when player-two slots are full. `CPauseMenu__ButtonPressed` uses non-null text to abort the binding-prompt flow. |

This is saved static retail Ghidra metadata only. Exact concrete pause-menu/control-binding layouts, exact source-body identity, runtime pause-menu rendering/input behavior, runtime controller remapping behavior, BEA patching, and rebuild parity remain deferred.

### PauseMenu / SimpleGameMenu Vfunc Tail (Wave474)

Wave474 corrected three adjacent pause/simple-game-menu tail targets:

- `0x004d15d0` to `CPauseMenu__VFunc_03_HandleMenuControlInput` with three stack arguments proved by `RET 0x0c`.
- `0x004d1730` to `CSimpleGameMenu__scalar_deleting_dtor`, the wrapper that calls the destructor body, conditionally frees `this` when `flags & 1`, returns `this`, and ends with `RET 0x4`.
- `0x004d1750` to `CSimpleGameMenu__dtor_base`, the destructor body that restores the shared no-op vtable, walks/frees active-reader nodes from the `+0x3c` set, clears the embedded set/range state, and calls `CMonitor__Shutdown`.

The nearby code at `0x004d1810` still looks like possible function-boundary debt in raw disassembly, but Wave474 did not create a function there. Runtime UI behavior, exact layouts, source identities, BEA launch, game patching, and rebuild parity remain unproven.

### PauseMenu Unwind Continuation (Wave762)

Wave762 static read-back (`unwind-continuation-wave762`, `wave762-readback-verified`) saved PauseMenu.cpp-adjacent compiler-generated SEH cleanup callbacks from `0x005d4250 Unwind@005d4250` through `0x005d445b Unwind@005d445b` as `void __cdecl Unwind@...(void)` rows. The static evidence includes `CMonitor__Shutdown_Thunk(*(EBP-0x18))`, `CSPtrSet__Clear((*(EBP-0x18))+0x14)`, and nineteen `OID__FreeObject_Callback` rows tied to debug path `0x006314dc` (`[maintainer-local-source-export-root]\PauseMenu.cpp`) with allocation/type value `0x80`; representative anchors include `0x005d4263 Unwind@005d4263`, `0x005d427f Unwind@005d427f`, `0x005d43cf Unwind@005d43cf`, and `0x005d445b Unwind@005d445b`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-143913_post_wave762_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime pause-menu cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### PauseMenu Unwind Continuation (Wave763)

Wave763 static read-back (`unwind-continuation-wave763`, `wave763-readback-verified`) saved comments/tags/signatures for continued PauseMenu.cpp-adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4477 Unwind@005d4477` through `0x005d4653 Unwind@005d4653` as `void __cdecl Unwind@...(void)` rows. Evidence includes PauseMenu.cpp debug path `0x006314dc`, DATA scope-table xrefs `0x0061cde4` through `0x0061cee4`, thirteen `OID__FreeObject_Callback` rows with allocation/type value `0x80`, monitor shutdown callbacks, pointer-set clears at `+0x14` and `+0x3c`, and `CMenuItemRangeVariant__Destructor` callbacks at `+0x0c`. Exact anchors include `0x005d4477 Unwind@005d4477`, `0x005d44af Unwind@005d44af`, `0x005d45a0 Unwind@005d45a0`, `0x005d45a8 Unwind@005d45a8`, `0x005d45e4 Unwind@005d45e4`, `0x005d45ef Unwind@005d45ef`, and `0x005d4653 Unwind@005d4653`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-150812_post_wave763_unwind_continuation_verified`. This is saved static retail Ghidra evidence only; exact parent source-body identity, runtime pause-menu cleanup behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

### PauseMenu Render Body (Wave481)

Wave481 corrected `0x004d11d0` from stale `CEngine__RenderOverlayAndMenuTransitions` to `CPauseMenu__Render` and set the saved signature:

```c
short * __thiscall CPauseMenu__Render(void * this);
```

Evidence came from the `CDXEngine__PostRender` caller at the source-aligned `GAME.GetPauseMenu()->Render()` point and the `CFEPOptions__Update` path through a `g_pOptionsContext` object initialized by `PauseMenu__Init`. The body applies UI render states, handles menu fade timing, draws the black fade and paired transition sprites, renders the active `CMenuItemRange` plus optional child/prompt ranges, and returns the active range title text pointer only when the active range index is nonzero.

Wave481 also corrected `CMenuItemRange__Render` to return `short *`, because its body returns the range title text pointer from `this+0x04`. Runtime pause/options UI behavior, concrete layouts, exact source body identity, BEA launch, game patching, and rebuild parity remain unproven.

## Related Files

- Career.cpp - Contains CCareer persisted settings (`g_bGodModeEnabled`, invert-Y arrays, controller config, etc.)
- FEPSaveGame.cpp - Cheat code activation via save name

---
*Migrated from ghidra-analysis.md (Dec 2025)*
