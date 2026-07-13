# FEPOptions.cpp - Function Index

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`); `0x004d2580` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: FEPOptions.cpp | Category: Frontend/Options Menu

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

Frontend options menu implementation. Saves configuration to `defaultoptions.bea` (Steam build). Contains UI state management and save file enumeration.

Wave907 (`frontend-input-game-loop-static-review-wave907`) records `CFEPOptions` and pause persistence rows as part of the `static-coherent frontend/input/game-loop core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The slice covers `436` rows across `33` families and includes `CFEPOptions__WriteDefaultOptionsFile`, `CPauseMenu__ResumeGameAndPersistOptions`, `CFrontEnd__SetPage`, `CController__DoMappings`, and `PlatformInput__InitDirectInput`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-111432_post_wave907_frontend_input_game_loop_static_review_verified`. Runtime options menu/input/filesystem behavior, visual QA, patch behavior, and rebuild parity remain separate proof.

Wave1023 (`frontend-options-pause-menu-review-wave1023`) re-read the options/detail helper strip with no mutation, including `0x004ceef0 LandscapeDetail_SetLevel`, `0x004cef30 LandscapeDetail_GetLevel`, `0x004cef50 CTreeDetail__SetQualityLevel`, `0x004cf030 CMouseSensitivityMenuItem__scalar_deleting_dtor`, `0x004cf8e0 CMultiSample__GetSampleCountLabel`, and `0x004cffd0 CVideoDetailLevel__GetCurrentPresetFromItems`. Fresh exports kept the Wave466 option-detail comments/signatures intact and tied the rows to landscape/tree-detail globals, `CRTMesh__SetQualityLevel`, localized MSAA labels, and active display-profile preset comparison. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-233831_post_wave1023_frontend_options_pause_menu_review_verified`. Runtime options-menu/device behavior, exact source-body identity, concrete menu-item/display-profile layouts, BEA patching, and rebuild parity remain separate proof.

Wave1212 (`wave1212-options-detail-tweak-current-risk-review`) re-read the options/detail subset from the active current-risk denominator with no mutation: `LandscapeDetail_SetLevel`, `LandscapeDetail_GetLevel`, `CTreeDetail__SetQualityLevel`, `CMouseSensitivityMenuItem__scalar_deleting_dtor`, and `CMultiSample__GetSampleCountLabel`, plus the adjacent tweak/reconnect rows documented in `CLIParams.cpp`. Fresh exports verified the option-detail DATA/COMPUTED_CALL xrefs, `CRTMesh__SetQualityLevel`, localized MSAA fallback id `0xd4`, and the mouse-sensitivity scalar-deleting destructor free path. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified`. Runtime options-menu behavior, runtime device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave858 FEPOptions core (`fepoptions-core-wave858`, `wave858-readback-verified`) created four previously missing CFEPOptions vtable-slot function objects and hardened nine important frontend/options connective rows. Static evidence ties the tranche to CFEPOptions vtable `0x005db8a8`, `g_pOptionsContext`, `defaultoptions.bea`, debug string `[maintainer-local-source-export-root]\FEPOptions.cpp`, page-state init/process/render/update/cleanup, and next raw commentless row `0x0051f9f0 CFEPScreenPos__Init`. Post-Wave858 queue telemetry is `6105` total, `5779` commented, `326` commentless, strict proxy `5779/6105 = 94.66%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260525-124939_post_wave858_fepoptions_core_verified`. Exact CFEPOptions layout, exact options-context class/layout, runtime options menu behavior, runtime filesystem behavior for `defaultoptions.bea`, BEA patching, and rebuild parity remain deferred.

Wave859 CFEPScreenPos core (`fepscreenpos-core-wave859`) confirmed the adjacent screen-position page uses `CFEPOptions__GetKillCounterTopBytes_23F4_23F8` and `CFEPOptions__SetKillCounterTopBytes_23F4_23F8` as the backing snapshot/restore bridge for calibration fields. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-131538_post_wave859_fepscreenpos_core_verified`. This remains static Ghidra evidence only; exact screen-axis semantics and runtime behavior remain deferred.

Wave860 CFEPVirtualKeyboard core (`fepvirtualkeyboard-core-wave860`) supersedes stale `CFEPOptions__EnumerateSaveFiles`: the row at `0x0051fff0 CFEPVirtualKeyboard__SeedUniqueDefaultSaveName` belongs to the virtual-keyboard edit buffer owner, not the CFEPOptions page. Static evidence shows it seeds a default save name with `BEA` plus ` %d`, enumerates existing savegames through `EnumerateSaveFiles_1/2`, and avoids duplicate names before clamping cursor state. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-134150_post_wave860_fepvirtualkeyboard_core_verified`. This remains static Ghidra evidence only; runtime save-name/filesystem behavior remains deferred.

Important nuance discovered via Ghidra:
- The functions previously labeled as "GetVolumes/SetVolumes" do **not** operate on the sound/music float volumes.
- They call `CCareer__GetKillCounterTopByte_23F4/23F8` and `CCareer__SetKillCounterTopByte_23F4/23F8` (top-byte metadata inside the first two kill counters). Their exact UI meaning is still TBD.
- The actual Sound/Music floats live in the global `CCareer` instance at `g_Career+0x248C` and `g_Career+0x2490` (`0x00662AAC` / `0x00662AB0`).

## Debug Path String

| Address | String |
|---------|--------|
| 0x0063fc88 | `"[maintainer-local-source-export-root]\\FEPOptions.cpp"` |

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x0051f370 | CFEPOptions__GetState | Named | Returns current menu state from `this+5` |
| 0x0051f4b0 | CFEPOptions__Init | Wave858 created | CFEPOptions vtable slot 0; clears page state at `this+0x04` and returns `1` |
| 0x0051f4c0 | CFEPOptions__Shutdown | Wave858 created | CFEPOptions vtable slot 1; frees non-null `g_pOptionsContext` through vtable slot `+4` and clears `0x0089bc30` |
| 0x0051f4e0 | CFEPOptions__ButtonPressed | Wave858 created | CFEPOptions vtable slot 3; delegates button/analog arguments to `g_pOptionsContext` vtable slot `+0x0c` |
| 0x0051f470 | CFEPOptions__GetKillCounterTopBytes_23F4_23F8 | Named | Gets **kill-counter top-byte metadata** for 0x23F4/0x23F8 (not float volumes) |
| 0x0051f490 | CFEPOptions__SetKillCounterTopBytes_23F4_23F8 | Named | Sets **kill-counter top-byte metadata** for 0x23F4/0x23F8 (not float volumes) |
| 0x0051f500 | CFEPOptions__SaveDefaultOptions | Named | Saves career settings to `defaultoptions.bea` |
| 0x0051f600 | CFEPOptions__ProcessInput | Named | State machine for menu input processing |
| 0x0051f6d0 | CFEPOptions__RenderPreCommon | Wave858 created | CFEPOptions vtable slot 4; forces transitions for destination/page ids `0x12`/`0x13` and calls `CFrontEnd__RenderPreCommonFade` |
| 0x0051f680 | [CFEPOptions__WriteDefaultOptionsFile](./CFEPOptions__WriteDefaultOptionsFile.md) | Named | Low-level writer for `defaultoptions.bea` (called from load/save flows) |
| 0x0051f700 | CFEPOptions__Update | Named | Updates UI, handles selection highlight |
| 0x0051f7e0 | CFEPOptions__EnsureOptionsContext | Named | Vtable helper: snapshots CCareer option globals into page state; lazily allocates `g_pOptionsContext` |
| 0x0051f8e0 | CFEPOptions__Cleanup | Named | Destroys resources, clears global pointer |
| 0x0051fff0 | CFEPVirtualKeyboard__SeedUniqueDefaultSaveName | Corrected in Wave860 | Supersedes stale `CFEPOptions__EnumerateSaveFiles`; see [`FEPVirtualKeyboard.cpp`](../FEPVirtualKeyboard.cpp/_index.md) |

**Total: 13 CFEPOptions functions identified; one stale adjacent row corrected to FEPVirtualKeyboard in Wave860**

## Key Data References

| Address | Type | Purpose |
|---------|------|---------|
| 0x0063fc74 | String | `"defaultoptions.bea"` - config filename |
| 0x0063fc54 | String | `"Couldn't write defaultoptions"` - error message |
| 0x00660620 | Data | Global CCareer instance |
| 0x0089bc30 | Pointer | Options context pointer (`g_pOptionsContext`, was `DAT_0089bc30`) |

## Function Details

### Wave858 FEPOptions Core (0x0051f370-0x0051f8e0)

Wave858 saved static retail Ghidra comments/tags/signatures for `0x0051f370 CFEPOptions__GetState`, `0x0051f4b0 CFEPOptions__Init`, `0x0051f4c0 CFEPOptions__Shutdown`, `0x0051f4e0 CFEPOptions__ButtonPressed`, `0x0051f500 CFEPOptions__SaveDefaultOptions`, `0x0051f600 CFEPOptions__ProcessInput`, `0x0051f6d0 CFEPOptions__RenderPreCommon`, `0x0051f700 CFEPOptions__Update`, and `0x0051f8e0 CFEPOptions__Cleanup`. The pass created the four missing vtable-slot function objects at `0x0051f4b0`, `0x0051f4c0`, `0x0051f4e0`, and `0x0051f6d0` after clean dry-run evidence.

| Address | Static read-back evidence |
| --- | --- |
| `0x0051f370 CFEPOptions__GetState` | Called by `CFrontEnd__Process` and `CGame__LoadLevel`; returns signed byte `this+0x05`. |
| `0x0051f4b0 CFEPOptions__Init` | CFEPOptions vtable `0x005db8a8` slot 0; clears page state at `this+0x04` and returns `1`. |
| `0x0051f4c0 CFEPOptions__Shutdown` | Vtable slot 1; frees non-null `g_pOptionsContext` through vtable slot `+4` with flag `1`, then clears global pointer `0x0089bc30`. |
| `0x0051f4e0 CFEPOptions__ButtonPressed` | Vtable slot 3; delegates button/analog arguments to `g_pOptionsContext` vtable slot `+0x0c` with a leading zero argument and returns with `RET 0x8`. |
| `0x0051f500 CFEPOptions__SaveDefaultOptions` | Called by `CFEPOptions__ProcessInput` and `CFEPGoodies__ButtonPressed`; serializes `CAREER`, writes `defaultoptions.bea`, prints `Couldn't write defaultoptions` on failure, and frees the buffer. |
| `0x0051f600 CFEPOptions__ProcessInput` | Vtable slot 2; advances page states 0/2/3/5, special-cases state 4, and calls `CFEPOptions__SaveDefaultOptions(1)` on the observed confirm path. |
| `0x0051f6d0 CFEPOptions__RenderPreCommon` | Vtable slot 4; forces transition to `1.0` for destination/page ids `0x12` and `0x13`, then calls `CFrontEnd__RenderPreCommonFade`. |
| `0x0051f700 CFEPOptions__Update` | Vtable slot 5; draws sliding text borders, renders `g_pOptionsContext` through `CPauseMenu__Render`, falls back to localized title id `0x265233`, renders help prompt id `1`, and calls `CFrontEnd__RenderOverlayEffects`. |
| `0x0051f8e0 CFEPOptions__Cleanup` | Called by `CFrontEnd__SetLanguage`; mirrors shutdown/context cleanup and clears `0x0089bc30`. |

Read-back evidence: `CreateFunctionsFromAddressList.java` dry/apply reported `would_create=4` then `created=4 renamed=4 failed=0`. `ApplyFEPOptionsCoreWave858.java` final dry reported `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified 9 metadata rows, 9 tag rows, 11 xref rows, 333 instruction rows, 9 decompile rows, 15 context metadata rows, 15 context decompile rows, and 18 vtable slot rows. This remains static Ghidra evidence only; exact runtime behavior and rebuild parity are deferred.

### Wave466 Options Detail Menu Helpers (0x004ceef0-0x004cffd0)

Wave466 saved static retail-binary metadata for six options/detail menu helpers that sit outside the main `CFEPOptions` page range but are reached from `PauseMenu__Init` option item wiring and related option vtables:

| Address | Function | Evidence summary |
|---------|----------|------------------|
| `0x004ceef0` | `LandscapeDetail_SetLevel(int detail_level)` | Writes selected landscape detail level `0/1/2` into `g_LandscapeDetailLevel2` / `g_LandscapeDetailLevel1`. |
| `0x004cef30` | `LandscapeDetail_GetLevel(void)` | Returns `2` when `g_LandscapeDetailLevel2` is set, otherwise returns the boolean state of `g_LandscapeDetailLevel1`. |
| `0x004cef50` | `CTreeDetail__SetQualityLevel(int quality_level)` | Forwards the selected tree/detail quality level to `CRTMesh__SetQualityLevel`. |
| `0x004cf030` | `CMouseSensitivityMenuItem__scalar_deleting_dtor(void * this, int flags)` | Calls `CMenuItem__Destructor`, frees `this` when flags bit 0 is set, and returns `this`. |
| `0x004cf8e0` | `CMultiSample__GetSampleCountLabel(int available_sample_ordinal)` | Maps an available MSAA ordinal through active display-profile capability bits and returns a static/localized label pointer, with a fallback through `Localization__GetStringById(0xd4)`. |
| `0x004cffd0` | `CVideoDetailLevel__GetCurrentPresetFromItems(void * video_detail_menu)` | Compares child option-item values against active display-profile defaults and texture/multisample globals, returning preset `1`, `2`, `3`, or `0` for no exact preset match. |

This is static Ghidra evidence only. Exact source identities, concrete menu-item/profile layouts, runtime device/menu behavior, and rebuild parity remain unproven.

### CFEPOptions__SaveDefaultOptions (0x0051f500)
Saves the current career settings to `defaultoptions.bea`. Uses memory allocation with debug info from line 0xFA (250). Calls `CCareer__GetSaveSize()` and `CCareer__Save()` to serialize career data. Handles UI transition states.

Key operations:
1. Checks global state flags (DAT_008a1388, DAT_008a9584)
2. Allocates buffer using CCareer__GetSaveSize
3. Serializes career via CCareer__Save
4. Opens file for writing via `fopen` (0x0055e490, was `FUN_0055e490`)
5. Writes data and closes file
6. Frees allocated buffer

### CFEPOptions__WriteDefaultOptionsFile (0x0051f680)
Helper function that handles the low-level file I/O for writing default options. Opens `defaultoptions.bea`, writes the provided buffer, and closes the file. Shows error message on failure.

Signature (Steam build, verified):
- `void CFEPOptions__WriteDefaultOptionsFile(void * data, int size)`

Verified call chains:
- `CFEPLoadGame__DoLoad` (`0x00461e20`) on successful load when `DAT_0082b5b0 == 0`
- `Platform__AsyncSaveCareer` (`0x004d2580`) when prior `DAT_0082b5b0 == 2`
- `FUN_004d06e0` (PauseMenu path)
- `CFEPMain__Process` (`0x00462640`) at callsite `0x004628df` (paired with `CCareer__Save` at `0x00462893`)

### CFEPOptions__Update (0x0051f700)
Updates the options menu UI. Handles:
- Sound/music volume selection highlighting
- Float-based selection interpolation (0.75 to 1.0 range)
- Volume level visualization
- Wave481 read-back shows this path calls `CPauseMenu__Render(g_pOptionsContext)` and uses the returned range title text pointer for `CFrontEnd__DrawTitleBar`, falling back to localized title id `0x265233` when the render helper returns null.

Parameters:
- `param_1` (float): Current selection value
- `param_2` (int): Menu item index (0x12 and 0x13 are special cases)

### CFEPOptions__ProcessInput (0x0051f600)
State machine for processing menu input. Uses switch statement on `this+4` state field:
- Cases 0, 2, 3, 5: Increment state
- Case 4: Check for FEP transitions
- Default: Handle save confirmation

Calls CFEPOptions__SaveDefaultOptions when confirming settings.

### CFEPOptions__EnsureOptionsContext (0x0051f7e0)

SEH-protected vtable helper that snapshots current CCareer option globals into the options-page state and lazily allocates the options context pointer (`g_pOptionsContext` @ `0x0089bc30`) if needed.

Signature (Steam build, verified):
- `void CFEPOptions__EnsureOptionsContext(void * this, int msg)`

Behavior notes:
- When `msg == 0` or `msg == 0x16`, clears `this+0x04` and snapshots:
  - `CAREER_mSoundVolume`, `CAREER_mMusicVolume`
  - `CAREER_mVibration_P1/P2`, `CAREER_mControllerConfig_P1/P2`
  - kill-counter top-byte metadata via `CCareer__GetKillCounterTopByte_23F4/23F8`
- Updates a UI timer (`this+0x08 = PLATFORM__GetSysTimeFloat() + 2.0`) and lazily allocates `g_pOptionsContext` if NULL.

### CFEPOptions__EnumerateSaveFiles (0x0051fff0)
Populates the save file list for the options menu. Iterates through save directory:
1. Adds default entry from DAT_0063fd34
2. Enumerates save files using EnumerateSaveFiles_1/2
3. Checks for duplicates via FUN_0055f2e8
4. Limits list to 0x1f (31) entries maximum
5. Sets completion flag at `this+0x48`

### CFEPOptions__GetKillCounterTopBytes_23F4_23F8 (0x0051f470)
Getter that retrieves current **kill-counter top-byte metadata** from the global `CCareer` instance:

- `CCareer__GetKillCounterTopByte_23F4` (`0x004218f0`)
- `CCareer__GetKillCounterTopByte_23F8` (`0x00421900`)

These return `((killCounter >> 24) - 0x80)` (signed bias). Their use in the options UI needs further investigation.

### CFEPOptions__SetKillCounterTopBytes_23F4_23F8 (0x0051f490)
Setter that writes **kill-counter top-byte metadata** back into the global `CCareer` instance:

- `CCareer__SetKillCounterTopByte_23F4` (`0x00421910`)
- `CCareer__SetKillCounterTopByte_23F8` (`0x00421940`)

This sets the top byte while preserving the lower 24 bits: `((top+0x80)<<24) | (value & 0x00FFFFFF)`.

### Mapping Correction (0x0051fd50)
`0x0051fd50` was previously labeled `CFEPOptions__Init`, but live vtable/RTTI checks show it belongs to `CFEPScreenPos` slot 6:

- `CFEPScreenPos__TransitionNotification(void * this, int from_page)`

See [`FEPScreenPos.cpp/_index.md`](../FEPScreenPos.cpp/_index.md) for the class-local mapping.

### CFEPOptions__Cleanup (0x0051f8e0)
Cleanup handler that destroys resources:
1. Checks if `g_pOptionsContext` is non-null
2. Calls destructor via vtable (offset +4)
3. Sets global pointer to NULL

### CFEPOptions__GetState (0x0051f370)
Minimal getter that returns the state byte at `this+5`.

## Exception Handler

| Address | Function | Notes |
|---------|----------|-------|
| 0x005d6870 | Unwind@005d6870 | SEH exception unwind handler, not a class method |

This is a compiler-generated Structured Exception Handling (SEH) unwind function, not a CFEPOptions method. References the FEPOptions.cpp debug path at line 0x196 (406).

## Related Files

- [FEPSaveGame.cpp](../FEPSaveGame.cpp/_index.md) - Save game name checking, cheat codes
- [FEPLoadGame.cpp](../FEPLoadGame.cpp/_index.md) - Save file loading
- [Career.cpp](../Career.cpp/_index.md) - Career data structure (serialized by SaveDefaultOptions)

## Notes

- FEP = "Front End Page" - the game's menu system terminology
- `defaultoptions.bea` stores game settings separate from career saves
- Volume controls interact with global sound/music systems
- Menu uses a state machine pattern (state field at offset +4)
- Save file enumeration limits to 31 entries (0x1f)
