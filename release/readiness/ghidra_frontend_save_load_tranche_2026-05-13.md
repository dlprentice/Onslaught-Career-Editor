# Ghidra Frontend Save/Load Tranche - 2026-05-13

Status: GREEN public-safe static RE evidence.

## Summary

Serialized headless dry/apply/read-back corrected and hardened `11` frontend save/load saved Ghidra targets in the Steam `BEA.exe` project. The pass creates missing FEPLoadGame and FEPSaveGame vtable-slot function objects, corrects old generic VFunc/render/process labels, and corrects two save/load dialog helpers to source-correlated save-game storage-message behavior.

## Saved Targets

| Address | Saved Ghidra state | Evidence summary |
| --- | --- | --- |
| `0x00461c40` | `bool __thiscall CFEPLoadGame__Init(void * this)` | Created missing FEPLoadGame init-slot function object; initializes load-game selection fields, sets the save slot to `-1`, clears the save-name head, and returns true. |
| `0x00461c60` | `void __thiscall CFEPLoadGame__ButtonPressed(void * this, int button, float value)` | Created missing FEPLoadGame button-slot function object; handles frontend directional/select/back input, clamps selection fields, plays frontend sounds, and routes back through `CFrontEnd__SetPage`. |
| `0x00461d60` | `void __thiscall CFEPLoadGame__Process(void * this, int state)` | Corrects the old generic process-slot label; calls the update-like helper outside inactive state, then calls `CFEPLoadGame__DoLoad` in active/no-message-box context. |
| `0x00461d90` | `void __thiscall CFEPLoadGame__Render(void * this, float transition, int dest_page)` | Corrects the old generic render-slot label; renders sliding text borders, the load-game title token, overlay effects, and the shared help prompt. |
| `0x00464620` | `bool __thiscall CFEPSaveGame__Init(void * this)` | Created missing FEPSaveGame init-slot function object; initializes save-game selection fields and returns true. |
| `0x00464630` | `void __thiscall CFEPSaveGame__ButtonPressed(void * this, int button, float value)` | Created missing FEPSaveGame button-slot function object; handles frontend directional/select/back input, clamps selection fields, plays frontend sounds, and routes back through `CFrontEnd__SetPage`. |
| `0x00464730` | `void __thiscall CFEPSaveGame__Process(void * this, int state)` | Created missing FEPSaveGame process-slot function object; calls `CFEPSaveGame__CreateSave` in active/no-message-box context and handles overwrite/delete prompt results. |
| `0x00464a80` | `void __thiscall CFEPSaveGame__Render(void * this, float transition, int dest_page)` | Corrects the old generic render-slot label; renders sliding text borders, the save-game title token, overlay effects, and the shared help prompt. |
| `0x00464b10` | `void __thiscall FEPSaveLoad__TransitionNotification(void * this, int from_page)` | Corrects the old base-page label to a shared save/load transition hook that stores a delayed start time at `this+0x4`. |
| `0x00464b30` | `void __cdecl CFEPSaveGame__RemovedMUWhinge(int reason_token)` | Corrects the old load-game text-resolver label; shared load/virtual-keyboard callers use it to build a localized storage-message dialog and clear `DAT_00677614`. |
| `0x00464bc0` | `void __thiscall CFEPSaveGame__AskIfYouWantToDelete(void * this, int career_in_progress, int because_4096, int no_space_for_bea)` | Corrects the old status-prompt label; caller stack and `RET 0x0c` evidence show three stack arguments, with current body selecting localized delete/no-space prompt text. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_frontend_save_load_probe_test.py` passed `2/2`. |
| Python compile | `py -3 -m py_compile tools\ghidra_frontend_save_load_probe.py tools\ghidra_frontend_save_load_probe_test.py` passed. |
| Headless apply | Initial `ApplyFrontendSaveLoadTranche.java` dry reported `updated=0 skipped=11 created=0 would_create=5 renamed=0 would_rename=6 missing=0 bad=0`; apply reported `updated=11 skipped=0 created=5 would_create=0 renamed=6 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`. |
| Comment hardening rerun | A follow-up dry/apply after tightening comment tokens reported dry `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0` and apply `updated=11 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`. |
| Read-back exports | Metadata `11`, decompile `11`, xrefs `15`, instruction rows `2871`, tags `11`, vtable-slot rows `20`, and callsite instruction rows `84`. |
| Focused package probe | `cmd.exe /c npm run test:ghidra-frontend-save-load` passed with targets `11`, xref evidence hits `14`, instruction evidence hits `29`, callsite evidence hits `4`, and vtable evidence hits `10`. |
| Whole-database queue | Refreshed headless `ExportFunctionQualitySnapshot.java` plus `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `6026` total functions, `1350` commented functions, `4676` commentless functions, `1939` undefined signatures, and `1973` `param_N` signatures. |
| Current proxies | Comment-backed `1350/6026 = 22.40%`; strict clean-signature `1288/6026 = 21.37%`. These are telemetry only, not milestones. |
| Ghidra backup | Live `BEA.gpr`/`BEA.rep` backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_124725_post_wave375_frontend_save_load_verified` with `19` files, `153586567` bytes, and `HashDiffCount=0`. |

## Claim Boundary

This is saved static retail Ghidra boundary/name/signature/comment/tag refinement. It does not prove exact FEPLoadGame or FEPSaveGame class layouts, concrete local variable types, runtime save/load behavior, packaged app behavior, BEA launch behavior, game patching, or rebuild parity.
