# Ghidra FEPMultiplayerStart SubObj8848 Review Wave955 Readiness Note

Status: read-only static review
Date: 2026-05-28
Scope: `fepmultiplayerstart-subobj8848-review-wave955`

Wave955 re-reviewed the `CFEPMultiplayerStart` embedded `SubObj8848` multiplayer-start selection helper after fresh serialized headless Ghidra exports. no mutation was needed in Ghidra: the Wave399 corrections still match current metadata, xrefs, vtable slots, instruction exports, and decompile read-back.

Primary Wave911 targets:

| Address | Result |
| --- | --- |
| `0x00459920 CFEPMultiplayerStart__SubObj8848__ctor` | Still installs vtable `0x005db4fc`, zeros compact row data, seeds default level-code constants, sets row count at `+0x345c`, and clears the 300-entry selection/highlight grid. |
| `0x004599a0 CFEPMultiplayerStart__SubObj8848__Init` | Still matches vtable slot 0 and scans the seeded grid for `DAT_0089d94c`, records row/column fields at `+0x3468/+0x346c`, computes scroll state, and refreshes timing fields. |
| `0x00459e50 CFEPMultiplayerStart__SubObj8848__RenderPreCommon` | Still matches the `RET 0x8` stack-argument render-pre-common helper, clamps transition alpha, and calls `CFrontEnd__RenderVideoQuadScaledToWindow`. |

Context anchors:

- Embedded vtable `0x005db4fc` preserves the SubObj8848 dispatch slice: slot 0 init, slot 2 process, slot 3 button, slot 4 render-pre-common, slot 5 render, slot 6 transition notification, slot 7 active notification, and slot 8 inherited `CFrontEndPage__DeActiveNotification`.
- Primary vtable `0x005db8d0` preserves the outer `CFEPMultiplayerStart` dispatch slice: `Init`, `Shutdown`, `Process`, `ButtonPressed`, `RenderPreCommon`, `Render`, `TransitionNotification`, `SharedVFunc__NoOpOneArg_004014c0`, and inherited `CFrontEndPage__DeActiveNotification`.
- Constructor context `0x00465f10 CFEPMultiplayerStart__ctor` calls `0x00459920 CFEPMultiplayerStart__SubObj8848__ctor` for owner offset `this+0x8848`.
- Process and button context route timeout/back/select behavior through `0x00466ae0 CFrontEnd__SetPage`; render-pre-common reaches `0x00452ce0 CFrontEnd__RenderVideoQuadScaledToWindow`; `0x00459ee0 CFEPMultiplayerStart__SubObj8848__Render` resolves selected level and episode text and draws the `E3 2002` build/progress string.
- Debug string `0x0063fc24` is `C:\dev\ONSLAUGHT2\FEPMultiplayerStart.cpp`.

Read-back evidence:

- Exports: 15 metadata rows, 15 tag rows, 73 xref rows, 1581 instruction rows, 15 decompile rows, and 20 vtable rows.
- Existing continuity probe: `test:ghidra-fepmultiplayerstart-subobj-wave399` still passes against current saved Ghidra state.
- Verified backup: `G:\GhidraBackups\BEA_20260528-103114_post_wave955_fepmultiplayerstart_subobj8848_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.
- Static function-quality closure remains `6151/6151 = 100.00%`.
- Wave911 focused re-audit progress after Wave955 is `286/1408 = 20.31%`.

What this proves:

- The saved Ghidra function rows for the reviewed SubObj8848 cluster remain coherent with fresh read-back evidence.
- The Wave399 calling-convention corrections for the constructor/init/render-pre-common entries still hold.
- The selected multiplayer level grid, page-transition, and render handoff are statically tied to the expected vtable, xref, debug-string, and frontend context rows.

What remains unproven:

- Runtime multiplayer-start behavior.
- Runtime frontend navigation/rendering behavior.
- Concrete `CFEPMultiplayerStart` and SubObj8848 layout names.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
