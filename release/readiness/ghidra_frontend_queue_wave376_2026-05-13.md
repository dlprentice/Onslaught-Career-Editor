# Ghidra Frontend Queue Wave376 Evidence - 2026-05-13

Status: public-safe saved Ghidra evidence note

## Summary

Wave 376 is a serialized static Ghidra correction tranche for eight frontend queue-head targets. It corrects three old `CFEPMultiplayerStart`-only render helper labels to shared `FEPShared__...` names, corrects a broad text wrapper away from `CFEPLanguageTest` ownership, corrects a debriefing shutdown vtable slot, corrects a shared constructor-style callback away from a debriefing-only label, and hardens two `CFEPMultiplayerStart` tail-call clear helpers.

This note is public-safe. It records addresses, names, signatures, counts, and proof boundaries only. Raw decompile/read-back exports and generated proof JSON remain under ignored private artifact roots.

## Saved Targets

| Address | Saved Ghidra state | Evidence boundary |
| --- | --- | --- |
| `0x00452fd0` | `void __stdcall FEPShared__RenderSelectionBrackets(float transition_alpha)` | Corrects old `CFEPMultiplayerStart__RenderSelectionBrackets`; xrefs show shared frontend render use across BattleEngine config and multiplayer pages. |
| `0x004530b0` | `void __stdcall FEPShared__RenderSelectionMarker(float x_index, float y_index, float scale, int alpha)` | Corrects old `CFEPMultiplayerStart__RenderSelectionMarker`; xrefs show shared marker use across multiple frontend render paths. |
| `0x00453140` | `void __stdcall FEPShared__RenderContextHelpPrompt(int help_token, float transition)` | Corrects old `CFEPMultiplayerStart__RenderHelpPromptForSelection`; the first argument is a localized help-token selector and the second is transition/progress. |
| `0x00456830` | `void * __thiscall GlobalListNode__ClearField4AndPushGlobalList(void * this)` | Corrects old `CFEPDebriefing__ResetStateAndVector`; xrefs show a shared constructor-style callback used beyond debriefing. |
| `0x00456850` | `void __thiscall CFEPDebriefing__Shutdown(void * this)` | Corrects old `CFEPDebriefing__VFunc_01_00456850`; vtable data and cleanup behavior support a debriefing shutdown slot. |
| `0x00465a20` | `int __stdcall TextLayout__WrapWideTextToFixedLines(short * line_buffer, short * wide_text, float max_width)` | Corrects old `CFEPLanguageTest__WrapWideTextToFixedLines`; xrefs show shared use from frontend dialogs, language test rendering, overlays, and prompts. |
| `0x004661d0` | `void __thiscall CFEPMultiplayerStart__ClearJoinedPlayerSet(void * this)` | Hardens a constructor/unwind tail-call wrapper that clears the set at receiver offset `+0x20`. |
| `0x004661e0` | `void __thiscall CFEPMultiplayerStart__ClearSecondaryPlayerSet(void * this)` | Hardens a constructor/unwind tail-call wrapper that clears the set at receiver offset `+0x28`. |

## Validation

Serialized dry/apply used `tools/ApplyFrontendQueueWave376.java`. The dry run reported `updated=0 skipped=8 renamed=0 would_rename=6 missing=0 bad=0`; the apply run reported `updated=8 skipped=0 renamed=6 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.

Read-back verified `8` metadata rows, `8` decompile exports, `55` xref rows, `2088` instruction rows, and `8` tag rows. The focused probe reports `PASS` for `8` targets, with `14` xref evidence hits and `12` instruction evidence hits.

The refreshed whole-database queue reports `6026` functions, `1358` commented functions, `4668` commentless functions, `1939` undefined signatures, and `1965` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1358/6026 = 22.54%`, strict clean-signature `1296/6026 = 21.51%`.

The actual live Ghidra project backup was verified at `G:\GhidraBackups\BEA_20260513_132030_post_wave376_frontend_queue_verified` with `19` files, `153586567` bytes, and `HashDiffCount=0`.

## Not Proven

- Runtime frontend rendering, prompt layout, text wrapping, multiplayer setup, or debriefing behavior.
- Exact class layouts, local variable types, structure recovery, or source method identity for every branch.
- BEA launch behavior, game patching, packaged WinUI behavior, or rebuild parity.
