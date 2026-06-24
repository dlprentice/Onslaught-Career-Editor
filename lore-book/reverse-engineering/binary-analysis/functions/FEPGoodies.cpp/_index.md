# FEPGoodies.cpp - Function Index

> Source File: FEPGoodies.cpp | Category: Frontend/Goodies Gallery

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Frontend goodies gallery implementation. Displays unlockable content (artwork, models, videos) based on player progress and cheat codes.

**NOTE:** Ghidra analysis found inverted logic in this file, but user testing (Dec 2025) confirmed MALLOY works without any patch. The inverted logic may only affect the `g_bAllCheatsEnabled` dev mode code path.

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CFEPGoodies` as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CFEPGoodies__Process`, `CFrontEnd__SetPage`, `CController__DoMappings`, and `CGame__ReceiveButtonAction`. Verified backup: `G:\GhidraBackups\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime Goodies wall behavior, model/video playback behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Wave1045 (`frontend-vtable-boundary-wave1045`) recovered four additional `CFEPGoodies` vtable boundaries from vtable `0x005db998`: `0x0045c7a0 CFEPGoodies__Init`, `0x0045c9e0 CFEPGoodies__Shutdown`, `0x0045e0d0 CFEPGoodies__Render`, and `0x0045ffa0 CFEPGoodies__TransitionNotification`. The pass saved function objects, comments, tags, and signatures, and read back cleanly after a recovered defined-data obstruction at `0x0045e0d0`. Queue closure is `6246/6246 = 100.00%`; expanded static surface progress is `985/1501 = 65.62%`. Verified backup: `G:\GhidraBackups\BEA_20260601-112809_post_wave1045_frontend_vtable_boundary_verified`. Runtime Goodies wall/model/video behavior, visual parity, concrete `CFEPGoodies` layout, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1050 (`goodies-resource-wall-review-wave1050`) re-read the Goodies resource-wall surface and saved a comment/tag correction at `0x0045d7e0 CFEPGoodies__Process`. The corrected comment ties the process loop to `IsCheatActive(0/5)`, `CFEPGoodies__FreeUpGoodyResources`, `CFEPGoodies__LoadingGoodyPoll`, `get_goodie_number`, `CFEPCommon__StopVideo`, `CFMV__PlayFullscreenWithLoadingGate`, and `CFEPCommon__StartVideo`, with `0x005db998 CFEPGoodies_vtable` slot evidence. Queue closure is `6246/6246 = 100.00%`; Wave911 focused progress remains `744/1408 = 52.84%`; expanded static surface progress advances to `1021/1509 = 67.66%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified`. Runtime Goodies wall behavior, asset/model/image playback, FMV playback, visible render behavior, controller/mouse behavior, unlock behavior, cheat UI outcomes, complete hidden/non-grid Goodie reachability, exact layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x0045ac30 | [CFEPGoodies__BuildStaticGoodieDataTable](./CFEPGoodies__BuildStaticGoodieDataTable.md) | Verified | Static goodie entry table materializer (bulk `CGoodieData__ctor` writes into global goodies metadata array) |
| 0x0045c770 | [CGoodieData__ctor](./CGoodieData__ctor.md) | Verified | `CGoodieData` field ctor helper (`Method/Method2/Number/Number2/mT1/mT2`) |
| 0x0045c7a0 | `CFEPGoodies__Init` | Verified | Wave1045 vtable `0x005db998` slot 0 boundary recovery; initializes Goodies page fields and default table state. |
| 0x0045c870 | [CFEPGoodies__Deserialise](./CFEPGoodies__Deserialise.md) | Verified | `GDIE` resource chunk deserializer (textures/mesh load into current goody payload) |
| 0x0045c9e0 | `CFEPGoodies__Shutdown` | Verified | Wave1045 vtable `0x005db998` slot 1 boundary recovery; compact thunk to `CFEPGoodies__FreeUpGoodyResources`. |
| 0x0045c9f0 | [CFEPGoodies__StartLoadingGoody](./CFEPGoodies__StartLoadingGoody.md) | Verified | Computes selected goody id/type and starts async loading path |
| 0x0045cb80 | [get_goodie_number](./get_goodie_number.md) | Verified | Static helper mapping grid `(x,y)` to goodie id |
| 0x0045cc10 | [CFEPGoodies__LoadingGoodyPoll](./CFEPGoodies__LoadingGoodyPoll.md) | Verified | Polls async load and transitions to loaded state |
| 0x0045cd10 | [CFEPGoodies__FreeUpGoodyResources](./CFEPGoodies__FreeUpGoodyResources.md) | Verified | Releases current goody mesh/textures and resets loader state |
| 0x0045cde0 | [CFEPGoodies__ButtonPressed](./CFEPGoodies__ButtonPressed.md) | Verified | Goodies wall input/selection handler; recovered function boundary/name and source-aligned `this, button, val` signature on 2026-05-07; Wave 395 hardened saved comments/tags |
| 0x0045d7e0 | [CFEPGoodies__Process](./CFEPGoodies__Process.md) | Verified | Main goodies process/update loop; Wave1050 corrected the saved comment/tag evidence beyond the older cheat-flag-only framing to include resource free/load polling, grid lookup, Goodie state checks, image/model behavior, and common-video FMV path. |
| 0x0045e0d0 | `CFEPGoodies__Render` | Verified | Wave1045 vtable `0x005db998` slot 5 boundary recovery; render body reaches `CFrontEnd__RenderOverlayEffects` at `0x0045ff36`. |
| 0x0045ffa0 | `CFEPGoodies__TransitionNotification` | Verified | Wave1045 vtable `0x005db998` slot 6 boundary recovery; resets Goodies transition/selection state after `PLATFORM__GetSysTimeFloat`. |

## Wave1045 Frontend Vtable Boundary Recovery

Wave1045 recovered four `CFEPGoodies` function objects from vtable `0x005db998` and tied them to source-shape evidence from `references/Onslaught/FEPGoodies.cpp` where available. `0x0045e0d0 CFEPGoodies__Render` initially failed creation because Ghidra had defined data at the target; the recovery dry/apply/final-dry chain cleared that listing-state obstruction and read back the saved function.

Read-back evidence: post exports verified `8` metadata rows, `8` tag rows, `8` DATA xref rows, `3540` function-body instruction rows, `8` decompile rows, and `135` frontend vtable slot rows across Goodies and Wingmen. Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress is `985/1501 = 65.62%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-112809_post_wave1045_frontend_vtable_boundary_verified`.

This is static function-boundary recovery evidence only. It does not prove runtime Goodies wall/model/video behavior, visual parity, exact concrete `CFEPGoodies` layout, BEA patching, gameplay outcomes, or rebuild parity.

## Wave1050 Goodies Resource-Wall Review

Wave1050 saved a comment/tag correction for `0x0045d7e0 CFEPGoodies__Process` while re-reading the broader Goodies resource-wall surface. The pass made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Read-back evidence: dry/apply/final-dry reported `updated=0 skipped=1 comment_only_updated=1 tags_added=11 missing=0 bad=0`, then `updated=1 skipped=0 comment_only_updated=1 tags_added=11 missing=0 bad=0`, then `updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0`. Fresh exports verified pre/post `13` primary metadata/tag/decompile rows, `132` xref rows, `5274` instruction rows, pre/post `15` context metadata/tag/decompile rows, `462` context xref rows, `7241` context instruction rows, post `3` render-context metadata/tag/decompile rows, `17` render-context xref rows, `132` render-context instruction rows, and `9` vtable slot rows from `0x005db998 CFEPGoodies_vtable`.

Probe token anchor: Wave1050; goodies-resource-wall-review-wave1050; 0x0045d7e0 CFEPGoodies__Process; IsCheatActive(0/5); CFEPGoodies__FreeUpGoodyResources; CFEPGoodies__LoadingGoodyPoll; get_goodie_number; CFEPCommon__StopVideo; CFMV__PlayFullscreenWithLoadingGate; CFEPCommon__StartVideo; 0x005db998 CFEPGoodies_vtable; 744/1408 = 52.84%; 1021/1509 = 67.66%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified; comment/tag correction.

## Wave 395 Goodies Comment/Tag Hardening

Wave 395 serialized a saved-Ghidra comment/tag hardening pass for the eight Goodies metadata/resource/input helpers at `0x0045ac30`, `0x0045c770`, `0x0045c870`, `0x0045c9f0`, `0x0045cb80`, `0x0045cc10`, `0x0045cd10`, and `0x0045cde0`.

The pass preserved the current saved names and signatures, added behavior-bounded comments and tags, then read back `8` metadata rows, `8` decompile exports, `116` xref rows, `8` tag rows, and `712` instruction rows. `tools/ghidra_goodies_wave395_probe.py --check` validates the saved metadata, tags, selected decompile/instruction/xref tokens, dry/apply summaries, and public overclaim boundaries.

This is static saved-Ghidra evidence. It does not prove runtime Goodies behavior, hidden Goodies 71-73 reachability, all Goodies asset/playback/viewer coverage, exact concrete layouts, local variable/type recovery, BEA launch/patching, or rebuild parity.

## Wave 374 CFEPCommon Correction

Wave 374 supersedes earlier Goodies-owned names for the frontend video helpers at `0x00452db0` and `0x00452de0`. They are now saved in Ghidra as `CFEPCommon__StartVideo` and `CFEPCommon__StopVideo`; `CFEPGoodies__Process` calls them during the FMV path, but the helpers are common frontend video helpers rather than `CFEPGoodies` methods.

## Cheat Flags and Goodie State Overrides

The binary derives two runtime flags from the save-name cheat system and uses them in multiple goodies UI paths:

| Address | Name | Set By | Effect |
|---------|------|--------|--------|
| 0x006798b0 | `g_Cheat_MALLOY` | `IsCheatActive(0)` | Treats displayed goodie state as `GS_OLD` (3) |
| 0x006798b4 | `g_Cheat_LATETE` | `IsCheatActive(5)` | Treats displayed goodie state as `GS_INSTRUCTIONS` (1) |

Goodie state is read from the global career instance:

- `CCareer` base: `0x00660620`
- `CGoodie[300]` base: `0x00660620 + 0x1F44 = 0x00662564`

UI code patterns:

- Gating/selection logic near `0x0045d048` checks these flags before consulting `CCareer.mGoodies[i]`.
- Color/display logic (examples: `0x0045e4a9`, `0x0045e62c`) uses the flags to override the effective state used for rendering.

**Prior note (deprecated):** earlier docs suggested patching `0x0045D04E` / `0x0045D056` (JNZ/JZ). After deeper tracing, these jumps appear to be part of normal state/cheat gating and should not be patched.

If you want dev mode (`g_bAllCheatsEnabled`) to behave like “MALLOY only” inside the goodies gallery, the safer patch is:
- `0x0045D819` (file `0x5D819`): `F7 D8` (NEG EAX) -> `33 C0` (XOR EAX,EAX), forcing `g_Cheat_LATETE = 0` before it is stored.
- Script: `patches/patch_devmode_goodies_logic_fix.py`

## Goodie Unlock System

Goodies are unlocked based on:
1. Kill count thresholds (aircraft, vehicles, emplacements, infantry, mechs)
2. Mission completion grades (A-rank and S-rank bonuses)
3. Level completion
4. Cheat codes (MALLOY - works without patch)

Cheats relevant to goodies:

- `MALLOY` (index 0) sets `g_Cheat_MALLOY` and overrides displayed state to `GS_OLD` (3).
- `lat\xEAte` (index 5, decoded from BEA.exe) sets `g_Cheat_LATETE` and overrides displayed state to `GS_INSTRUCTIONS` (1).

## Cross-References

- Calls: `IsCheatActive` (0x00465490) - in [FEPSaveGame.cpp](../FEPSaveGame.cpp/_index.md)
- Related: [Career.cpp](../Career.cpp/_index.md) - goodie unlock conditions

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
- Bug discovered via Ghidra analysis comparing source code logic to compiled binary
