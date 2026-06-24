# Goodies Runtime Read-Back Evidence - 2026-05-07

## Scope

This pass added a public-safe read-back probe for the Goodies runtime/static RE coverage. It compares source anchors, retail function documentation, current WinUI/AppCore unlock-copy support, and the real-install asset extraction evidence without launching the game or modifying Ghidra/BEA state.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-runtime-readback/current/goodies-runtime-readback.json
```

## Command

```powershell
py -3 tools\goodies_runtime_readback_probe.py --check
```

Result: PASS

Important output:

```text
PASS: wrote subagents/goodies-runtime-readback/current/goodies-runtime-readback.json
groups: 15/15 passing
```

## Anchors Checked

The probe checks token presence and line numbers only. It does not copy source excerpts into the public evidence.

- `references/Onslaught/Career.cpp` anchors `CCareer::UpdateGoodieStates()`, `TOTAL_C_GRADES(66)`, `SET_GOODIE_NEW(66)`, `SET_GOODIE_NEW(78)`, pending-new tracking, and instruction-state setup.
- `references/Onslaught/FEPGoodies.cpp` anchors the Goodies wall grid mapping, frontend state get/set helpers, and row buckets for race, FMV, and concept-art Goodies.
- `references/Onslaught/Game.cpp` anchors intro/outro FMV playback paths that map FMV ids to Goodies `201-232`, including the `fmv == 33` special case mapping to slot `232`.
- `reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__UpdateGoodieStates.md` anchors retail function `0x0041c470` and the documented `0x00FFFFFF` kill-counter mask behavior.
- `reverse-engineering/binary-analysis/functions/game.cpp/CGame__RunIntroFMV.md` and `CGame__RunOutroFMV.md` anchor the retail cutscene Goodie unlock handlers.
- `reverse-engineering/binary-analysis/functions/IScript.cpp.md` anchors retail mission-script Goodie get/set handlers and their 1-based script index behavior.
- `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/CFEPGoodies__Process.md` anchors retail frontend Goodies cheat/display override evidence.
- `reverse-engineering/binary-analysis/functions/FEPGoodies.cpp/CFEPGoodies__StartLoadingGoody.md` anchors selected-Goodie resource loading behavior.
- `OnslaughtCareerEditor.AppCore/GoodieUnlockRequirementService.cs` anchors the current WinUI-facing unlock requirement translation.
- `release/readiness/real_asset_extraction_smoke_2026-05-07.md` anchors the read-only real-install resource/export smoke.
- `reverse-engineering/quick-reference/save-goodies.md` anchors the corrected 233-displayable-slot range, FMV `201-232`, and Goodies `71-73` as shipped texture-only archives not exposed by the known wall mapping.
- `release/readiness/goodies_asset_matrix_2026-05-07.md` anchors the static 71-73 texture-only classification and remaining runtime/non-grid investigation gap.
- `release/readiness/winui_goodies_wall_visibility_2026-05-07.md` anchors the WinUI/AppCore visibility distinction for Goodies `71-73`.

## What This Proves

- Goodie save-state encoding and displayable range are documented.
- Default Goodie recomputation has source and retail function-document anchors.
- FMV Goodie unlocks have source and retail function-document anchors.
- Mission-script Goodie get/set has retail function-document anchors.
- Frontend Goodies grid/display/cheat override has source and retail function-document anchors.
- Actual PC install asset inventory/extraction has bounded read-only evidence.
- WinUI unlock requirement copy is now tied back to the current source/binary evidence set.
- Goodies `71-73` are no longer a generic unknown gap: static evidence classifies them as shipped texture-only archives with resolved refs, while runtime/non-grid access remains unproven.

## What This Does Not Prove

- No runtime process was launched in this probe.
- No live save recomputation was observed inside a running BEA process in this probe.
- No Ghidra names or signatures were changed in this probe.
- No exhaustive model viewer/runtime Goodies wall replay was performed in this probe.
- No private assets, screenshots, raw frames, raw decompile output, or proof JSON were committed.

## Safety

- The installed Steam game path was not mutated.
- The original `BEA.exe` was not read or patched by this probe.
- No Ghidra project mutation or rename-map apply was performed.
- Any future runtime replay should use a copied profile, the existing windowed patch on the copied executable, and app-owned private artifact roots.
