# Wave1136 PauseMenu Current-Risk Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1136-pausemenu-current-risk-review`

Wave1136 accounts for `8 rows` from the Wave1108 current focused continuity denominator as a PauseMenu/SimpleGameMenu current-risk cluster with fresh Ghidra export evidence. This was a read-only review with no mutation: no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, and no runtime-file mutation.

Primary targets:

| Address | Evidence |
| --- | --- |
| `0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning` | DATA vtable xref `0x005de604`; instruction/decompile evidence checks controller binding capacity and uses localized warning ids `0xe8` / `0xe9` before rendering through `CMenuItem__RenderWithColor`. |
| `0x004d04b0 CPauseMenu__scalar_deleting_dtor` | DATA vtable xref `0x005de700`; wrapper calls `CPauseMenu__dtor_base` at `0x004d04b3`, conditionally frees `this`, returns `this`, and ends with `RET 0x4`. |
| `0x004d0510 CPauseMenu__LoadPauseTextures` | Called from `CGame__RunLevel` at `0x0046e3b2`; loads child menu textures, `pause_circle01/02`, and the shared `FrontEnd_v2/FE_Blank.tga` blank texture. |
| `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions` | Called from `CPauseMenu__ButtonPressed` and `CPauseMenu__VFunc_03_HandleMenuControlInput`; static evidence releases pause-menu controller targets, unpauses, persists active/default options, clears transient prompt/menu objects, and timestamps the pause menu. |
| `0x004d0db0 CPauseMenu__InitBindingPromptAction` | Called twice from `CPauseMenu__ButtonPressed`; initializes a binding-prompt action node via `CPauseMenu__InitAndSetActiveReader` and ends with `RET 0x0c` for three stack arguments. |
| `0x004d11d0 CPauseMenu__Render` | Called from `CDXEngine__PostRender` at `0x0053ee24` and `CFEPOptions__Update` at `0x0051f71d`; static evidence renders pause/options menu ranges and may return the active range title text pointer. |
| `0x004d15d0 CPauseMenu__VFunc_03_HandleMenuControlInput` | DATA vtable xref `0x005de708`; handler gates input by timestamp `this+0x2c`, dispatches through current range/menu-item slots, handles button `0x33`, and handles button `0x2e` through resume/range-reset paths. |
| `0x004d1730 CSimpleGameMenu__scalar_deleting_dtor` | DATA vtable xref `0x005de720`; wrapper calls `CSimpleGameMenu__dtor_base` at `0x004d1733`, conditionally frees `this`, returns `this`, and ends with `RET 0x4`. |

Context rows re-read for continuity: `0x004d04d0 CPauseMenu__ReloadSharedBlankTexture`, `0x004d05e0 CPauseMenu__dtor_base`, `0x004d0810 CPauseMenu__ButtonPressed`, `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText`, `0x004d0e40 CGameMenu__InitBase`, `0x004d0ff0 CPauseMenu__InitPauseSession`, and `0x004d1750 CSimpleGameMenu__dtor_base`.

Evidence counts:

- Primary exports: `8` metadata rows, `8` tag rows, `11` xref rows, `670` instruction rows, and `8` decompile rows.
- Context exports: `7` metadata rows, `7` tag rows, `10` xref rows, `624` instruction rows, and `7` decompile rows.
- Static closure remains `6410/6410 = 100.00%`.
- Static debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused remains `812/1408 = 57.67%`.
- Wave911 top-500 risk-ranked remains `500/500 = 100.00%`.
- Wave1108 current focused accounting advances to `204/1179 = 17.30%`.
- Current focused candidates: 1178.
- live regenerated current focused candidates: 1178.
- remaining active focused work: 975.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`.

What this proves:

- The eight target function rows exist in the saved Ghidra project with the expected names, signatures, comments, tags, xrefs, instruction exports, and decompile exports.
- The PauseMenu/SimpleGameMenu current-risk cluster remains statically coherent with earlier Wave465, Wave474, Wave481, Wave824, Wave923, Wave962, Wave1023, and Wave1119 evidence.
- No mutation was required for these rows.

What remains separate proof:

- Runtime pause-menu behavior.
- Runtime controller-binding behavior.
- Runtime options/defaultoptions persistence behavior.
- Runtime render behavior.
- Exact concrete layouts and exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
