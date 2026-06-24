# Goodies Copied-Profile Runtime Prep - 2026-05-07

## Scope

This pass prepared the next Goodies runtime replay step without touching the installed Steam game. It added a scriptable patch-catalog helper for copied executables, added a bounded still-frame capture helper, created an ignored copied game profile, verified the copied `BEA.exe` windowed-patch state, launched that copied profile, scanned for the managed BEA window, captured one private frame, and stopped the copied process.

Private generated outputs remain ignored under:

```text
subagents/goodies-runtime-replay-2026-05-07/
```

## Commands

Patch helper self-test:

```powershell
py -3 tools\apply_bea_catalog_patch.py --self-test
```

Result: PASS

Important output:

```text
self-test passed
```

Installed-game guard check:

```powershell
py -3 tools\apply_bea_catalog_patch.py --exe <steam-install>\BEA.exe --patch-id force_windowed --dry-run
```

Result: PASS as a safety rejection

Important output:

```text
Error: refusing to patch an executable under Program Files; prepare a copied profile or app-owned artifact root first
```

Copied-profile preparation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\prepare_game_profile.ps1 `
  -SourceGameRoot <steam-install> `
  -OutputRoot subagents\goodies-runtime-replay-2026-05-07 `
  -ProfileName goodies-runtime-profile
```

Result: PASS

Important output:

```text
schemaVersion: game-profile-prepare.v1
mutation: true
profileName: goodies-runtime-profile
entries copied: BEA.exe, data, defaultoptions.bea, savegames, binkw32.dll, ogg.dll, vorbis.dll, zlib.dll
```

Windowed patch verification on the copied executable:

```powershell
py -3 tools\apply_bea_catalog_patch.py `
  --exe subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile\BEA.exe `
  --patch-id force_windowed `
  --apply `
  --json-out subagents\goodies-runtime-replay-2026-05-07\force-windowed-patch-report.json
```

Result: PASS

Important output:

```text
Result: verified: no bytes were written
force_windowed @ 0x12A644: already patched
```

This means the copied executable inherited the `force_windowed` patched state from the local source specimen. No bytes were written by this pass.

Copied-profile launch preview:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\start_game_profile.ps1 `
  -GameRoot subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile `
  -PrintOnly
```

Result: PASS

Copied-profile startup-movie bypass preview:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\start_game_profile.ps1 `
  -GameRoot subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile `
  -Arguments -skipfmv `
  -PrintOnly
```

Result: PASS

Copied-profile `-skipfmv` launch/capture probe:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\start_game_profile.ps1 `
  -GameRoot subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile `
  -Arguments -skipfmv

powershell -NoProfile -ExecutionPolicy Bypass -File tools\capture_game_window.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -OutputPath subagents\goodies-runtime-replay-2026-05-07\skipfmv-probe\frame-8s.png
```

Result: PASS

Important output summary:

```text
launch argument: -skipfmv
window scan: ready
private frame at 8s: Battle Engine Aquila title screen
```

Copied-profile Goodies wall replay probe:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\start_game_profile.ps1 `
  -GameRoot subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile `
  -Arguments -skipfmv

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessName BEA.exe `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "tap:ENTER,wait:1500,tap:SPACE,wait:2000,tap:ENTER,wait:3000,tap:ENTER,wait:5000,tap:ESCAPE,wait:3000,tap:ESCAPE,wait:3000"

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessName BEA.exe `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "tap:DOWN,wait:500,tap:DOWN,wait:500,tap:DOWN,wait:500,tap:ENTER"

powershell -NoProfile -ExecutionPolicy Bypass -File tools\capture_game_window.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -OutputPath subagents\goodies-runtime-replay-2026-05-07\goodies-wall-probe\goodies.png
```

Result: PASS

Important output summary:

```text
input delivery: scan-code keybd_event fallback after SendInput returned zero events
captured screen: Goodies wall grid
visible runtime copy: To Unlock: Complete Tutorial
post-stop scan: no-window
```

Copied-profile bounded launch/window/stop probe:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\start_game_profile.ps1 `
  -GameRoot subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile

powershell -NoProfile -ExecutionPolicy Bypass -File tools\list_game_windows.ps1 `
  -ProcessName BEA.exe `
  -Limit 20

Stop-Process -Id <copied-profile-process-id> -Force

powershell -NoProfile -ExecutionPolicy Bypass -File tools\list_game_windows.ps1 `
  -ProcessName BEA.exe `
  -Limit 20
```

Result: PASS

Important output summary:

```text
launch schema: game-launch-process.v1
window scan after launch: ready
window title: BEA
window bounds: 656 x 539
window scan after stop: no-window
```

Copied-profile bounded capture probe:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\capture_game_window.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -OutputPath subagents\goodies-runtime-replay-2026-05-07\initial-window-capture.png
```

Result: PASS

Important output summary:

```text
capture schema: game-window-capture-helper.v1
status: captured
captured bounds: 656 x 539
private frame: Lost Toys startup screen
```

The raw launch/window/stop JSON remains private at:

```text
subagents/goodies-runtime-replay-2026-05-07\copied-profile-launch-probe.json
subagents/goodies-runtime-replay-2026-05-07\copied-profile-capture-probe.json
subagents/goodies-runtime-replay-2026-05-07\initial-window-capture.png
subagents/goodies-runtime-replay-2026-05-07\skipfmv-probe\
subagents/goodies-runtime-replay-2026-05-07\title-input-probe\
subagents/goodies-runtime-replay-2026-05-07\scan-fallback-title-probe\
subagents/goodies-runtime-replay-2026-05-07\profile-select-probe\
subagents/goodies-runtime-replay-2026-05-07\briefing-nav-probe\
subagents/goodies-runtime-replay-2026-05-07\main-menu-probe\
subagents/goodies-runtime-replay-2026-05-07\goodies-wall-probe\
subagents/goodies-runtime-replay-2026-05-07\load-game-goodies-probe\
subagents/goodies-runtime-replay-2026-05-07\load-game-yes-probe\
subagents/goodies-runtime-replay-2026-05-07\loaded-save-goodies-probe\
subagents/goodies-runtime-replay-2026-05-07\goodies-click-scroll-probe\
subagents/goodies-runtime-replay-2026-05-07\goodies-hold-right-probe\
subagents/goodies-runtime-replay-2026-05-07\goodies-70-to-74-gap-proof\
subagents/goodies-runtime-replay-2026-05-07\goodies-74-77-label-proof-split\
subagents/goodies-runtime-replay-2026-05-07\goodies-runtime-profile\savegames\BEA 1.bes.before-goodies-runtime-proof.backup
```

Copied-profile loaded-save Goodie preview replay:

```powershell
# Copied-profile save mutation only: copied an existing all-Goodies save over
# copied-profile save slot BEA 1, after backing up the copied slot beside it.

powershell -NoProfile -ExecutionPolicy Bypass -File tools\start_game_profile.ps1 `
  -GameRoot subagents\goodies-runtime-replay-2026-05-07\goodies-runtime-profile `
  -Arguments -skipfmv

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "tap:ENTER,wait:1500,tap:SPACE,wait:2000,tap:ENTER,wait:3000,tap:ENTER,wait:5000,tap:ESCAPE,wait:3000,tap:ESCAPE,wait:3000"

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "tap:DOWN,wait:500,tap:ENTER,wait:1000,tap:UP,wait:500,tap:ENTER,wait:2500,tap:ENTER,wait:4000"

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "tap:ESCAPE,wait:2500,tap:DOWN,wait:500,tap:DOWN,wait:500,tap:ENTER,wait:2000"

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "tap:ENTER,wait:2500"
```

Result: PASS

Important output summary:

```text
copied BEA 1.bes backup created before mutation: yes
copied BEA 1.bes post-copy Goodies states: 233 entries with state 3, 67 entries with state 0
Load Game confirmation: confirmed Yes from retail UI
selected load slot: BEA 1
loaded screen: SELECT LEVEL, Episode 3, 3.11 - Muspell Counterattack
Goodies wall after load: unlocked wall state, selected text "Unlocked! Hawk Winter"
selected Goodie preview after Enter: artwork/details panel opened for Hawk Winter
window scan after stop: no-window
```

One intermediate probe intentionally failed before this success: it opened the Load Game confirmation while `No` was still selected, so the later sequence returned to the menu and drifted into Options. That failed branch is retained under the ignored private probe folders as navigation evidence, not as a positive proof.

Copied-profile Goodies wall gap replay:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "click:10x20" `
  -PrintOnly

powershell -NoProfile -ExecutionPolicy Bypass -File tools\send_game_window_input.ps1 `
  -ProcessId <copied-profile-process-id> `
  -HwndHex <exact-window-handle> `
  -Sequence "down:RIGHT,wait:1300,up:RIGHT,wait:1100"
```

Result: PASS with one limitation

Important output summary:

```text
click print-only plan: PASS, action kind click with client coordinates
live click path: PASS, mouseEventsSent=2, but the Goodies wall did not scroll from the clicked right-arrow area
hold-right path: PASS, keyboard hold advanced the Goodies wall at the visible edge
runtime wall sequence: 66 Race Challenge 1, 67 Race Challenge 2, 68 Race Challenge 3, 69 Race Challenge 4, 70 Race Challenge 5, then 74 Battle Engine Aquila Picture, 75 Intro Storyboard Sequence
developer labels captured: 74 Battle Engine Aquila Picture, 75 Intro Storyboard Sequence, 76 Team Photo, 77 Development
window scan after stop: no-window
```

The runtime sequence supports the static `get_goodie_number(x, y)` finding that normal top-row wall navigation skips 71-73. It does not prove that 71-73 have no hidden path elsewhere.

### Goodies 71-73 Asset Metadata Follow-Up

Command:

```powershell
py -3 tools\aya_archive_inventory.py `
  <local-game-root>\data\Resources\goodie_71_res_PC.aya `
  <local-game-root>\data\Resources\goodie_72_res_PC.aya `
  <local-game-root>\data\Resources\goodie_73_res_PC.aya `
  --resource-root <local-game-root>\data\Resources `
  --resolve-assets `
  --json-include-chunks `
  --json-out subagents\goodies-71-73-asset-inspection\current\goodies-71-73-inventory.json `
  --asset-manifest-out subagents\goodies-71-73-asset-inspection\current\goodies-71-73-assets.json `
  --show-chunks 8 `
  --preview-bytes 64
```

Result: PASS

Important output summary:

```text
goodie_71_res_PC.aya: raw_size 452, chunks LVLR/TARG/AYAD/GDIE, GDIE texture_only, texture ref goodies\ca_be_aquila\ca_be_final01.tga, no mesh refs
goodie_72_res_PC.aya: raw_size 452, chunks LVLR/TARG/AYAD/GDIE, GDIE texture_only, texture ref goodies\ca_be_aquila\ca_be_final02.tga, no mesh refs
goodie_73_res_PC.aya: raw_size 452, chunks LVLR/TARG/AYAD/GDIE, GDIE texture_only, texture ref goodies\ca_be_aquila\ca_bea_battle_pic.tga, no mesh refs
asset manifest: GDIE texture refs 3/3 resolved, GDIE mesh refs 0/0
```

The metadata confirms 71-73 are not missing shipped resources. They are tiny Goodie descriptor archives pointing at three resolved texture payloads, while the normal Goodies wall replay still skips directly from 70 to 74.

### Goodies 71-73 Source Reachability Follow-Up

Read-only source inspection target:

```text
references/Onslaught/FEPGoodies.cpp
references/Onslaught/Career.cpp
```

Result: PASS with remaining retail-runtime uncertainty

Important source findings:

```text
static table: CGoodieData(GOODIES_71), CGoodieData(GOODIES_72), CGoodieData(GOODIES_73)
texture lookup: cases 71, 72, and 73 return ca_be_final01, ca_be_final02, and ca_bea_battle_pic
type lookup: goodie_num <= 73 returns GT_IMAGE after race-level ids 66-70
unlock recomputation: Career.cpp sets Goodies 71, 72, and 73 new when COMPLETE_LEVEL_OR_EVO(741) is true
instruction hints: Career.cpp sets instructions for 71 in episode 7 and 72/73 in episode 8
normal selection: StartLoadingGoody and LoadingGoodyPoll request get_goodie_number(mCX, mCY)
normal render/navigation: ButtonPressed and RenderPreCommon operate on mCX/mCY coordinates and skip get_goodie_number(...) == -1
disabled source branch: STRESS_TEST_GOODIES can random-select coordinates, but it still selects coordinates and the source define is commented out
```

The source therefore treats 71-73 as intended image Goodies for resource/type/unlock purposes, but the ordinary Goodies wall path still needs a coordinate that maps to those ids. The inspected source does not reveal such a normal coordinate path.

Probe guard:

```powershell
py -3 tools\goodies_runtime_readback_probe.py --check
```

Result: PASS, `groups: 15/15 passing`. The probe now guards both the 71-73 source reachability group and the `Career.cpp` unlock/instruction tokens so this evidence remains repeatable.

### Goodies 71-73 Retail Ghidra Read-Back Follow-Up

Read-only headless export:

```powershell
<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript ExportFunctionsByAddressDecompile.java `
  subagents\goodies-71-73-ghidra-readback\current\goodies-addresses.txt `
  subagents\goodies-71-73-ghidra-readback\current\decompile `
  60 `
  -noanalysis
```

Result: PASS

Important output summary:

```text
targets=5 dumped=5 missing=0 failed=0
0x0045ac30 CFEPGoodies__BuildStaticGoodieDataTable OK
0x0045c9f0 CFEPGoodies__StartLoadingGoody OK
0x0045cb80 get_goodie_number OK
0x0045cc10 CFEPGoodies__LoadingGoodyPoll OK
0x0045d7e0 CFEPGoodies__Process OK
```

Public-safe verifier:

```powershell
py -3 tools\goodies_ghidra_readback_probe.py --check
```

Initial pre-recovery result: PASS, `functions: 5/5 passing`. The current verifier result after `ButtonPressed` recovery and unlock read-back is recorded below.

Read-only xref export:

```powershell
<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript ExportXrefsForAddresses.java `
  subagents\goodies-71-73-ghidra-readback\current\goodies-xref-addresses.txt `
  subagents\goodies-71-73-ghidra-readback\current\goodies-xrefs.tsv `
  -noanalysis
```

Result: PASS, `Wrote 13 rows`.

Read-only instruction-context export for the eight no-function xref rows:

```powershell
<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript ExportInstructionsAroundAddresses.java `
  subagents\goodies-71-73-ghidra-readback\current\goodies-unattributed-xref-addresses.txt `
  subagents\goodies-71-73-ghidra-readback\current\goodies-unattributed-instructions.tsv `
  20 `
  20 `
  -noanalysis
```

Result: PASS, `targets=8 missing=0`, `Wrote 328 instruction rows`.

### Goodies ButtonPressed Ghidra Function Recovery Follow-Up

Read-only instruction context identified `0x0045cde0` as the missing Goodies button/selection handler boundary. The address starts after `CFEPGoodies__FreeUpGoodyResources`, takes `this` in `ECX`, dispatches frontend button codes through a jump table, and contains the eight previously no-function `get_goodie_number` xrefs. This matched Stuart's `CFEPGoodies::ButtonPressed(SINT button, float val)` source structure.

Dry-run:

```powershell
<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript CreateFunctionsFromAddressList.java `
  subagents\goodies-buttonpressed-function\current\buttonpressed-function-map.txt `
  subagents\goodies-buttonpressed-function\current\buttonpressed-create-dry.tsv `
  dry `
  -noanalysis
```

Result: PASS, `would_create=1`, `failed=0`.

Apply:

```powershell
<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript CreateFunctionsFromAddressList.java `
  subagents\goodies-buttonpressed-function\current\buttonpressed-function-map.txt `
  subagents\goodies-buttonpressed-function\current\buttonpressed-create-apply.tsv `
  apply `
  -noanalysis
```

Result: PASS, `created=1`, `renamed=1`, `failed=0`.

Signature hardening dry/apply:

```powershell
<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript ApplyGoodiesButtonPressedSignature.java `
  dry `
  -noanalysis

<ghidra>\support\analyzeHeadless.bat `
  <ghidra-projects-root> BEA `
  -process BEA.exe `
  -scriptPath tools `
  -postScript ApplyGoodiesButtonPressedSignature.java `
  apply `
  -noanalysis
```

Result: PASS, read-back signature `void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)`.

Read-back after apply:

```powershell
py -3 tools\goodies_ghidra_readback_probe.py --check
```

Result: PASS, `functions: 6/6 passing`, `instruction contexts: 8/8 passing`.

Public-safe verifier after the instruction-context export:

```powershell
py -3 tools\goodies_ghidra_readback_probe.py --check
```

Result: PASS, `functions: 6/6 passing`, `instruction contexts: 8/8 passing`, `unlock read-back: PASS`, `field map: PASS`.

The verifier confirms retail `get_goodie_number` still maps top-row race slots to 66-70 and developer slots to 74-77, while `CFEPGoodies__StartLoadingGoody`, `CFEPGoodies__LoadingGoodyPoll`, `CFEPGoodies__ButtonPressed`, and `CFEPGoodies__Process` all read selected ids through `mCX/mCY` coordinates. It also confirms the retail loader still has a content bucket covering ids 71-73 as image Goodies, and the retail `CCareer__UpdateGoodieStates` decompile includes Goodie pointer constants `0x47`, `0x48`, and `0x49` matching source unlock entries 71-73. The xref export confirms those four expected named callers, and the instruction export classifies the former no-function call sites under `CFEPGoodies__ButtonPressed` as source-correlated Goodies wall navigation, selected-coordinate load gating, post-load state checks, and selected-state update paths. The field-map guard source-correlates `this+0x13c` as `mCX`, `this+0x140` as `mCY`, `this+0x154` as `mCurrentGoodyType`, and `this+0x1d8` as `mGoodyState` without mutating Ghidra types. This supports the current conclusion: 71-73 are intended shipped image Goodies, but no normal retail wall-coordinate path to those ids is proven.

## What This Proves

- The active tooling can prepare a copied runtime profile from the local PC install without overwriting existing targets.
- `tools\apply_bea_catalog_patch.py` can verify/apply catalog patch bytes on copied executables and refuses Program Files targets by default.
- The copied executable is in the `force_windowed` patched state needed for non-fullscreen runtime work.
- The copied profile can launch a visible BEA window and can be stopped cleanly.
- The copied profile can produce a bounded still-frame capture for the exact BEA process/window target.
- The copied profile accepts the `-skipfmv` diagnostic argument through the helper and reaches the title screen quickly.
- The scoped input helper can drive the copied profile from title screen to profile selection, mission briefing, level select, main menu, and the Goodies wall.
- The Goodies wall runtime path is now privately captured from the running copied profile.
- A copied all-Goodies save can be loaded through the retail Load Game UI in the copied profile.
- The loaded copied save changes the Goodies wall from a locked first item to an unlocked item state.
- The selected unlocked Goodie can open its runtime preview/details screen in the copied profile.
- The scoped input helper can now plan and send bounded client-coordinate mouse clicks against the exact managed BEA window, although the tested Goodies wall arrow click did not scroll the wall.
- Holding RIGHT at the visible edge advances the Goodies wall and privately captured the runtime jump from Race Challenge 5 at index 70 to the next visible slot at index 74.
- Runtime labels for 74-77 are `Battle Engine Aquila Picture`, `Intro Storyboard Sequence`, `Team Photo`, and `Development`.
- Shipped Goodie resource archives 71-73 exist and resolve to texture-only payloads, so the remaining 71-73 question is runtime/UI reachability rather than asset absence.
- Stuart's source treats 71-73 as valid image Goodies in static data, type selection, texture lookup, unlock recomputation, and instruction hints, but the ordinary source-level wall selection/render path still routes through coordinates that do not map to 71-73.
- Fresh Ghidra export confirms the same retail coordinate-selection shape for `get_goodie_number`, `StartLoadingGoody`, `LoadingGoodyPoll`, `ButtonPressed`, and `Process`, with 6/6 selected functions dumped and verified by a public-safe probe; `ButtonPressed` now has the source-aligned `this, button, val` signature, selected `CFEPGoodies` field offsets are guarded by source/decompile correlation, and retail `UpdateGoodieStates` decompile read-back includes 71-73 constants.
- Fresh xref export records 13 retail xrefs to `get_goodie_number`, including the expected named Goodies callers; follow-up instruction-context export classifies the former no-function rows under `CFEPGoodies__ButtonPressed` as Goodies navigation/selection-state paths.
- No BEA window remained after the stop step.

## What This Does Not Prove

- It does not prove every Goodies wall coordinate.
- It does not prove any hidden/non-grid runtime path for Goodies 71-73.
- It does not prove whether 71-73 are reachable through a developer command, direct selection path, cheat override, or non-wall runtime branch.
- The read-back exports do not prove absence of every possible hidden branch outside the selected functions.
- The function recovery does not mutate Ghidra field types, harden every `ButtonPressed` local variable, or type every related helper.
- It does not classify every runtime Goodies branch.
- It does not prove why the initial new-game/name flow ignored the copied all-Goodies save; explicit Load Game selection was required.
- It does not mutate the installed Steam executable.
- It does not mutate the installed Steam saves.
- It does not create or commit private screenshots, raw frames, or copied game files.

## Next RE Step

Use read-only source/Ghidra analysis to harden recovered `CFEPGoodies__ButtonPressed` locals/field types when safe, then look for any direct-selection or hidden branch that can request Goodie ids 71-73. Use the copied, windowed profile only for bounded runtime confirmation. Keep raw frames, local paths, and extracted payloads private.
