# CFEPGoodies__Process

> Address: 0x0045d7e0 | Source: `references/Onslaught/FEPGoodies.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void __thiscall CFEPGoodies__Process(void * this, int state)`)
- **Verified vs Source:** Partial; function identity and signature are read-back verified, while exact struct-field typing remains incomplete.

## Purpose

Frontend goodies gallery update/process loop. It computes cheat-derived flags used to override goodie gating/display behavior, drives resource free/load polling, resolves the current grid Goodie, updates image/model interaction state, and handles the FMV Goodie path through common frontend video helpers.

## Evidence

- Calls `IsCheatActive(&FRONTEND.mFEPSaveGame, idx)` at `0x0045d7f4` and `0x0045d80b`, then normalizes the result to `0/1`.
  - `IsCheatActive(0)` (MALLOY) is stored into `g_Cheat_MALLOY` at `0x006798b0`.
  - `IsCheatActive(5)` (decoded as `lat\xEAte`) is stored into `g_Cheat_LATETE` at `0x006798b4`.
- Subsequent goodies UI logic uses these globals to override the effective goody state read from:
  - `CCareer.mGoodies[]` at `0x00660620 + 0x1F44 = 0x00662564`
  - Example reads: `0x0045e4cb`, `0x0045e64e`
- Read-only headless Ghidra export on 2026-05-07 dumped this function with signature
  `void __thiscall CFEPGoodies__Process(void * this, int state)`.
  Raw decompile output remains private under ignored `subagents/`; only this public-safe signature/status summary is committed.
- Wave 374 refreshed the saved Ghidra decompile after correcting the common video helper ownership. The FMV path now calls `CFEPCommon__StopVideo` and `CFEPCommon__StartVideo`; earlier Goodies-owned helper names for those common video routines are superseded.
- Wave1050 (`goodies-resource-wall-review-wave1050`) corrected the saved Ghidra comment/tags for `0x0045d7e0 CFEPGoodies__Process` because the old comment described only cheat-flag setup. Fresh post exports verified the broader body: `IsCheatActive(0/5)`, `CFEPGoodies__FreeUpGoodyResources`, `CFEPGoodies__LoadingGoodyPoll`, `get_goodie_number`, career Goodie state checks with cheat overrides, `CFEPCommon__StopVideo`, `CFMV__PlayFullscreenWithLoadingGate`, and `CFEPCommon__StartVideo`.
- Wave1050 read-back verified pre/post `13` primary metadata/tag/decompile rows, `132` xref rows, `5274` instruction rows, pre/post `15` context metadata/tag/decompile rows, `462` context xref rows, `7241` context instruction rows, post `3` render-context metadata/tag/decompile rows, `17` render-context xref rows, `132` render-context instruction rows, and `9` vtable rows from `0x005db998 CFEPGoodies_vtable`. Queue closure remained `6246/6246 = 100.00%`; Wave911 focused progress remained `744/1408 = 52.84%`; expanded static surface progress advanced to `1021/1509 = 67.66%`; top-500 coverage remained `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified`.

## Source Cross-Check

In Stuart's source (`references/Onslaught/FEPGoodies.cpp:1550`), `CFEPGoodies::Process()` computes a local `ischeatactive` using only `IsCheatActive(0)`. The ported binary extends this to a second cheat (index 5) and uses globals (`0x006798b0`, `0x006798b4`) to affect multiple UI paths.

## Partial Field / Branch Read-Back

The 2026-05-07 read-only decompile lines up several `CFEPGoodies` page fields with source names by behavior:

| Retail offset | Source-aligned field | Evidence shape |
| ---: | --- | --- |
| `this + 0x13C` | `mCX` | Passed as the first coordinate to `get_goodie_number` in FMV, level, and cheat branches. |
| `this + 0x140` | `mCY` | Passed as the second coordinate to `get_goodie_number` in FMV, level, and cheat branches. |
| `this + 0x154` | `mCurrentGoodyType` | Compared against content bucket values before FMV, level, cheat, image, and mesh handling. |
| `this + 0x194` | `mImageZoom` | Compared against `1.0f` before opening FMV or level paths, matching the source `mImageZoom == 1.0f` gates. |
| `this + 0x1D4` | `mDisplayGoody` | Outer display/close branch; cleared after FMV, level, or cheat actions finish. |
| `this + 0x1D8` | `mGoodyState` | Checked for loaded-state behavior before image/model update paths run. |

The content bucket branch matches the source-level split:

| Bucket value | Source enum meaning | Retail branch behavior |
| ---: | --- | --- |
| `0` | image | Mouse/scroll pan path for static artwork. |
| `1` | mesh | Manual camera/rotation path for the loaded model preview. |
| `2` | FMV | Builds a cutscene/dev-video path, stops frontend music, calls common frontend video stop/start helpers around the selected FMV, then restores frontend music. |
| `3` | level | Writes the target frontend level id for the selected race-level Goodie. |
| `4` | cheat/developer bucket | Resolves the selected Goodie id and clears the display state; exact side effect remains untyped. |

## Notes

- Treat the broad mapping to `CFEPGoodies::Process` as read-back verified.
  The remaining caution is narrower: animation/camera internals and the cheat/developer bucket side effect are still not fully typed.
- Wave1050 proves static Ghidra comment/tag correction only. It does not prove runtime Goodies wall behavior, asset/model/image playback, FMV playback, visible render behavior, controller/mouse behavior, unlock behavior, cheat UI outcomes, complete hidden/non-grid Goodie reachability, exact concrete layouts, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1050; goodies-resource-wall-review-wave1050; 0x0045d7e0 CFEPGoodies__Process; IsCheatActive(0/5); CFEPGoodies__FreeUpGoodyResources; CFEPGoodies__LoadingGoodyPoll; get_goodie_number; CFEPCommon__StopVideo; CFMV__PlayFullscreenWithLoadingGate; CFEPCommon__StartVideo; 0x005db998 CFEPGoodies_vtable; 744/1408 = 52.84%; 1021/1509 = 67.66%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-143021_post_wave1050_goodies_resource_wall_review_verified; comment/tag correction.
