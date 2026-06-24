# Ghidra Goodies Resource Wall Review Wave1050

Status: complete saved comment/tag correction
Date: 2026-06-01
Scope: `goodies-resource-wall-review-wave1050`

Wave1050 re-read the Goodies gallery resource-wall surface and saved one bounded comment/tag correction at `0x0045d7e0 CFEPGoodies__Process`. The correction replaces the older cheat-flag-only framing with the broader observed process/update loop: cheat flag refresh, resource unload/load polling, current grid lookup, career Goodie state checks, image/model interaction, and the FMV Goodie path through common frontend video helpers.

The wave made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x0045ac30 CFEPGoodies__BuildStaticGoodieDataTable` | `void CFEPGoodies__BuildStaticGoodieDataTable(void)` | Wave395 table-materializer evidence still matches the saved row. |
| `0x0045c770 CGoodieData__ctor` | `void __thiscall CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)` | Six-field `CGoodieData` ctor evidence remains coherent. |
| `0x0045c7a0 CFEPGoodies__Init` | `int __fastcall CFEPGoodies__Init(void * this)` | Wave1045 vtable `0x005db998` slot 0 boundary remains coherent. |
| `0x0045c870 CFEPGoodies__Deserialise` | `void __thiscall CFEPGoodies__Deserialise(void * this, void * chunk_reader)` | `GDAT` resource chunk deserialize evidence remains coherent. |
| `0x0045c9e0 CFEPGoodies__Shutdown` | `void __fastcall CFEPGoodies__Shutdown(void * this)` | Wave1045 vtable `0x005db998` slot 1 thunk to resource free remains coherent. |
| `0x0045c9f0 CFEPGoodies__StartLoadingGoody` | `void __fastcall CFEPGoodies__StartLoadingGoody(void * this)` | Selected Goodie id/type load-start evidence remains coherent. |
| `0x0045cb80 get_goodie_number` | `int __cdecl get_goodie_number(int x, int y)` | Grid `(x,y)` to Goodie id helper evidence remains coherent. |
| `0x0045cc10 CFEPGoodies__LoadingGoodyPoll` | `void __fastcall CFEPGoodies__LoadingGoodyPoll(void * this)` | Async load polling evidence remains coherent. |
| `0x0045cd10 CFEPGoodies__FreeUpGoodyResources` | `void __fastcall CFEPGoodies__FreeUpGoodyResources(void * this)` | Current Goodie resource release evidence remains coherent. |
| `0x0045cde0 CFEPGoodies__ButtonPressed` | `void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)` | Goodies wall input/selection evidence remains coherent. |
| `0x0045d7e0 CFEPGoodies__Process` | `void __thiscall CFEPGoodies__Process(void * this, int state)` | Saved comment/tag correction: body refreshes `g_Cheat_MALLOY`/`g_Cheat_LATETE` via `IsCheatActive(0/5)`, calls `CFEPGoodies__FreeUpGoodyResources` and `CFEPGoodies__LoadingGoodyPoll`, uses `get_goodie_number`, checks career Goodie state with cheat overrides, and stops/plays/restarts common frontend video around `CFMV__PlayFullscreenWithLoadingGate`. |
| `0x0045e0d0 CFEPGoodies__Render` | `void __thiscall CFEPGoodies__Render(void * this, float transition, int dest)` | Wave1045 vtable `0x005db998` slot 5 render boundary remains coherent. |
| `0x0045ffa0 CFEPGoodies__TransitionNotification` | `void __thiscall CFEPGoodies__TransitionNotification(void * this, int from_page)` | Wave1045 vtable `0x005db998` slot 6 transition callback remains coherent. |

Context rows:

- Career/Goodie state context: `TOTAL_S_GRADES`, `CCareer__CountGoodies`, `CCareer__UpdateGoodieStates`, `CCareer__GetAndResetGoodieNewCount`, `CCareer__GetAndResetFirstGoodie`, and `CCareer__GetGoodiePtr`.
- Frontend/common video context: `CFEPCommon__StartVideo`, `CFEPCommon__StopVideo`, `CFrontEnd__RenderVideoQuadScaledToWindow`, and `CFrontEnd__RenderPreCommonFade`.
- Resource context: `CResourceAccumulator__ReadResourceFile`, `CBinkOpenThread__IsRunning`, `CDXTexture__Deserialize`, and `CMesh__Deserialize`.
- Script/cheat context: `IsCheatActive`, `IScript__SetGoodieState`, and `IScript__GetGoodieState`.
- Vtable context: `0x005db998 CFEPGoodies_vtable` slots 0-8 resolve to `CFEPGoodies__Init`, `CFEPGoodies__Shutdown`, `CFEPGoodies__Process`, `CFEPGoodies__ButtonPressed`, `CFEPLanguageTest__RenderPreCommon`, `CFEPGoodies__Render`, `CFEPGoodies__TransitionNotification`, `SharedVFunc__NoOpOneArg_004014c0`, and `CFrontEndPage__DeActiveNotification`.

Evidence counts:

- Primary exports: pre/post `13` metadata rows, `13` tag rows, `132` xref rows, `5274` function-body instruction rows, and `13` decompile rows.
- Context exports: pre/post `15` metadata rows, `15` tag rows, `462` xref rows, `7241` function-body instruction rows, and `15` decompile rows.
- Render-context exports: post `3` metadata rows, `3` tag rows, `17` xref rows, `132` function-body instruction rows, and `3` decompile rows.
- Vtable export: post `1` vtable anchor and `9` slot rows.
- Apply gate: dry reported `updated=0 skipped=1 comment_only_updated=1 tags_added=11 missing=0 bad=0`; apply reported `updated=1 skipped=0 comment_only_updated=1 tags_added=11 missing=0 bad=0`; final dry reported `updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress remains `744/1408 = 52.84%`; expanded static surface progress advances to `1021/1509 = 67.66%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified`, 19 files, 174590855 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed Goodies rows still exist as saved Ghidra function objects in the loaded database.
- `CFEPGoodies__Process` now has saved static metadata that reflects the broader observed process/update body rather than only the cheat flag setup.
- The saved `CFEPGoodies__Process` tags include `goodies-resource-wall-review-wave1050` and `wave1050-readback-verified`.
- The static Goodies resource-wall surface is coherent across metadata, tags, xrefs, instruction bodies, decompile exports, vtable slots, context helpers, and a verified project backup.

What remains separate proof:

- Runtime Goodies wall behavior, asset/model/image playback, FMV playback, visible render behavior, controller/mouse behavior, unlock behavior, and cheat UI outcomes.
- Complete hidden/non-grid Goodie reachability.
- Exact concrete `CFEPGoodies`, `CGoodieData`, resource payload, career Goodie, and frontend video layouts beyond observed offsets.
- Exact source-body identity where retail code and Stuart source differ.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1050; goodies-resource-wall-review-wave1050; 0x0045d7e0 CFEPGoodies__Process; IsCheatActive(0/5); CFEPGoodies__FreeUpGoodyResources; CFEPGoodies__LoadingGoodyPoll; get_goodie_number; CFEPCommon__StopVideo; CFMV__PlayFullscreenWithLoadingGate; CFEPCommon__StartVideo; 0x005db998 CFEPGoodies_vtable; 744/1408 = 52.84%; 1021/1509 = 67.66%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified; comment/tag correction.
