# Ghidra CFEPDemoMain Review Wave956 Readiness Note

Status: read-only static review
Date: 2026-05-28
Scope: `cfepdemo-main-review-wave956`

Wave956 re-reviewed the compact `CFEPDemoMain` demo-menu dispatch slice after fresh serialized headless Ghidra exports. No mutation was needed in Ghidra; anchor phrase: no mutation. The Wave402 signatures, comments, tags, vtable mapping, data-table context, instruction exports, and decompile read-back still match the current saved database.

Primary Wave911 targets:

| Address | Result |
| --- | --- |
| `0x00457ec0 CFEPDemoMain__GetMenuType` | Still reads as a no-argument `__cdecl` helper returning constant menu type `3`; vtable `0x005db7c0` slot 4 points here. |
| `0x00457ed0 CFEPDemoMain__GetActionCount` | Still reads as a one-stack-argument `__stdcall` helper returning constant action count `1`; vtable `0x005db7c0` slot 3 points here. |
| `0x00457ee0 CFEPDemoMain__DoAction` | Still reads `this+0x8`, writes `DAT_008a956c` for action states `0` and `2`, calls `CFrontEnd__SetPage(&DAT_0089d758, 0x11, 0x46)` for action state `1`, and falls back to `CFEPMain__DoAction` otherwise. |
| `0x00457f20 CFEPDemoMain__Update` | Still maps stack-only `menu_state` to `FrontEndText__GetLocalizedOrFallbackTextByToken(0)`, fallback token `8`, and token `6`. |

Context anchors:

- Vtable `0x005db7c0` preserves the `CFEPDemoMain` dispatch slice: inherited/shared `CFEPMain__TransitionNotification`, `CFEPMain__ActiveNotification`, inherited `CFrontEndPage__DeActiveNotification`, then slots 3 through 6 for the four `CFEPDemoMain` targets.
- Data-table root `0x005e4a70` still has `0x005e4a78 -> 0x00457ec0 CFEPDemoMain__GetMenuType`, but the surrounding values mix function pointers and non-function float/data values, so this remains data-table context rather than a second demo-menu dispatch slice.
- `CFEPDemoMain__DoAction` bridges back into the Wave953 main-menu context through `0x004623e0 CFEPMain__DoAction` and `0x00466ae0 CFrontEnd__SetPage`.
- Stuart's currently available source snapshot does not include a matching `FEPDemoMain.cpp` body; the names remain retail vtable/action/text-token evidence, not source-body identity.

Read-back evidence:

- Exports: 11 metadata rows, 11 tag rows, 220 xref rows, 404 instruction rows, 11 decompile rows, and 20 vtable/data-table rows.
- Existing continuity probe: `test:ghidra-fepdemo-wave402` still passes against current saved Ghidra state.
- Verified backup: `G:\GhidraBackups\BEA_20260528-105733_post_wave956_cfepdemo_main_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.
- Static function-quality closure remains `6151/6151 = 100.00%`.
- Wave911 focused re-audit progress after Wave956 is `290/1408 = 20.60%`.

What this proves:

- The saved Ghidra function rows for the four-target `CFEPDemoMain` demo-menu slice remain coherent with fresh metadata, xref, vtable, instruction, and decompile evidence.
- The Wave402 calling-convention corrections for the constant getters and text-token update helper still hold.
- The demo action dispatcher is statically tied to the same global page/action state and CFEPMain fallback context recorded by the older correction.

What remains unproven:

- Runtime demo-menu behavior.
- Runtime frontend navigation/rendering behavior.
- Concrete `CFEPDemoMain` layout names.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
