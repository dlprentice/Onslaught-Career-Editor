# Wave1136 PauseMenu Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Tag: `wave1136-pausemenu-current-risk-review`

Wave1136 accounts for `8 rows` from the Wave1108 current focused continuity denominator as a PauseMenu/SimpleGameMenu current-risk cluster. It advances Wave1108 current focused accounting to `204/1179 = 17.30%` with current focused candidates: 1178, live regenerated current focused candidates: 1178, and remaining active focused work: 975.

Static closure remains `6410/6410 = 100.00%`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 risk-ranked remains `500/500 = 100.00%`; static debt remains `0 / 0 / 0`.

This was a fresh Ghidra export plus read-only review. It made no mutation: no rename, signature, comment, tag, function-boundary, executable-byte, BEA launch, installed-game, or runtime-file mutation.

## Primary Rows

| Address | Static read-back evidence |
| --- | --- |
| `0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning` | DATA vtable xref `0x005de604`; checks free binding capacity through `Controls__FindFirstFreeBindingSlot`, uses localized warning ids `0xe8` and `0xe9`, then renders through `CMenuItem__RenderWithColor`. |
| `0x004d04b0 CPauseMenu__scalar_deleting_dtor` | DATA vtable xref `0x005de700`; calls `CPauseMenu__dtor_base` at `0x004d04b3`, conditionally frees `this` when flags bit 0 is set, returns `this`, and ends with `RET 0x4`. |
| `0x004d0510 CPauseMenu__LoadPauseTextures` | Called by `CGame__RunLevel` at `0x0046e3b2`; walks pause-menu child ranges, calls `CMenuItemRange__LoadTexture`, loads `pause_circle01/02`, releases any prior shared blank texture, and loads `FrontEnd_v2/FE_Blank.tga`. |
| `0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions` | Called by `CPauseMenu__VFunc_03_HandleMenuControlInput` at `0x004d16f9` and `CPauseMenu__ButtonPressed` at `0x004d0c8a`; releases pause-menu controller targets, unpauses, reinitializes mouse input, serializes current career/options, optionally writes the active save slot, writes `defaultoptions.bea`, clears transient prompt/menu objects, and timestamps the pause menu. |
| `0x004d0db0 CPauseMenu__InitBindingPromptAction` | Called twice from `CPauseMenu__ButtonPressed`; initializes a binding-prompt action node through `CPauseMenu__InitAndSetActiveReader`, stores the menu item at `+0x08`, and ends with `RET 0x0c` for three stack arguments. |
| `0x004d11d0 CPauseMenu__Render` | Called by `CDXEngine__PostRender` at `0x0053ee24` and `CFEPOptions__Update` at `0x0051f71d`; applies UI render states, draws pause/options ranges, optional child/prompt ranges, and may return the active range title text pointer. |
| `0x004d15d0 CPauseMenu__VFunc_03_HandleMenuControlInput` | DATA vtable xref `0x005de708`; gates by timestamp `this+0x2c`, fetches the current range through `this+0x14/this+0x24`, forwards menu item input, handles button `0x33`, and handles button `0x2e` through resume or range-reset paths. |
| `0x004d1730 CSimpleGameMenu__scalar_deleting_dtor` | DATA vtable xref `0x005de720`; calls `CSimpleGameMenu__dtor_base` at `0x004d1733`, conditionally frees `this` when flags bit 0 is set, returns `this`, and ends with `RET 0x4`. |

## Context Rows

These rows were re-read as context and are not newly counted primary rows:

- context `0x004d04d0 CPauseMenu__ReloadSharedBlankTexture`
- context `0x004d05e0 CPauseMenu__dtor_base`
- context `0x004d0810 CPauseMenu__ButtonPressed`
- context `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText`
- context `0x004d0e40 CGameMenu__InitBase`
- context `0x004d0ff0 CPauseMenu__InitPauseSession`
- context `0x004d1750 CSimpleGameMenu__dtor_base`

## Evidence Counts

| Export | Rows |
| --- | ---: |
| Primary metadata | 8 |
| Primary tags | 8 |
| Primary xrefs | 11 |
| Primary instructions | 670 |
| Primary decompile index | 8 |
| Context metadata | 7 |
| Context tags | 7 |
| Context xrefs | 10 |
| Context instructions | 624 |
| Context decompile index | 7 |

Verified backup: `G:\GhidraBackups\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified`.

Probe token anchor: Wave1136; wave1136-pausemenu-current-risk-review; 204/1179 = 17.30%; 8 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 975; PauseMenu/SimpleGameMenu current-risk cluster; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 0x004d0290 CControllerBackMenuItem__RenderBindingCapacityWarning; 0x004d04b0 CPauseMenu__scalar_deleting_dtor; 0x004d0510 CPauseMenu__LoadPauseTextures; 0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions; 0x004d0db0 CPauseMenu__InitBindingPromptAction; 0x004d11d0 CPauseMenu__Render; 0x004d15d0 CPauseMenu__VFunc_03_HandleMenuControlInput; 0x004d1730 CSimpleGameMenu__scalar_deleting_dtor; context 0x004d04d0 CPauseMenu__ReloadSharedBlankTexture; context 0x004d05e0 CPauseMenu__dtor_base; context 0x004d0810 CPauseMenu__ButtonPressed; context 0x004d0de0 CPauseMenu__GetBindingCapacityWarningText; context 0x004d0e40 CGameMenu__InitBase; context 0x004d0ff0 CPauseMenu__InitPauseSession; context 0x004d1750 CSimpleGameMenu__dtor_base; G:\GhidraBackups\BEA_20260605-114652_post_wave1136_pausemenu_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-111213_post_wave1135_groundattack_gillmhead_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; current risk candidates: 6165; focused threshold `15`; not Wave911 reconstruction; G:\GhidraBackups\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified.

## Boundary

This is static Ghidra evidence only. Runtime pause-menu behavior, runtime controller-binding behavior, runtime options/defaultoptions persistence behavior, runtime render behavior, exact concrete layouts, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
