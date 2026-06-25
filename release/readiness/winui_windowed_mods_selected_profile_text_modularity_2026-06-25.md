# WinUI Windowed & Mods Selected-Profile Text Modularity - 2026-06-25

Status: accepted focused WinUI modularity slice

## Scope

This slice extracted selected-profile status/details text composition from
`BinaryPatchesPage` into a small WinUI presentation helper. It did not change
patch catalog rows, patch-row selection semantics, safe-copy profile matching,
safe-copy creation, launch behavior, online status, music status, runtime proof,
AppCore correctness logic, or installed-game mutation rules.

## Changes

- Added `OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedProfileTextState.cs`
  for the selected-profile text input shape.
- Added `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSelectedProfileText.cs`
  for selected-profile status/details copy plus module/evidence/restore/limit
  formatting.
- Kept `MatchSelectableSafeCopyProfileId`, `SetEquals`, selected patch keys,
  `ProfilePresetId`, safe-copy manifest logic, launch logic, music logic, and
  online readiness logic in `BinaryPatchesPage`.
- Guarded the helper against accidental behavior growth by checking that it does
  not contain patch-key expansion, `ProfilePresetId`, safe-copy prepare/launch,
  online rendering, or copied-profile state hooks.

## Consult Review

- Specialist WinUI modularity consult agreed the extraction is safe and helpful
  if it stays text/presentation-only. It recommended passing a reduced state
  shape rather than the full selected-key collection so future edits do not move
  patch-row selection semantics into the helper.
- Adversarial review caught the initial in-progress compile/test drift and a
  mismatch risk where a model could carry both a profile id and a preset object.
  The accepted fix removed duplicate profile identity from the model; the helper
  derives identity from the matched preset.
- Adversarial review also noted a pre-existing weak static guard around Enhanced
  Preview and create-time music-swap reset. That is tracked as follow-up test
  hardening, not changed in this presentation-only slice.

## Validation

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
# PASS: 0 warnings, 0 errors.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
# PASS: 5 tests.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
# PASS: 1 runtime UIA smoke.

dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfilePreflightServiceTests.PrepareWindowedCompatibilityProfile_AppliesSelectedVisiblePatchRowsToSafeCopyOnly|FullyQualifiedName~GameProfilePreflightServiceTests.PrepareWindowedCompatibilityProfile_RecordsEnhancedPreviewPresetInManifest|FullyQualifiedName~GameProfilePreflightServiceTests.PrepareWindowedCompatibilityProfile_RecordsDebugCameraPreviewPresetBoundary|FullyQualifiedName~GameProfilePreflightServiceTests.BuildPrepareReceipt"
# PASS: 6 tests.
```

Additional closeout gates passed:

```powershell
npm run test:hard-payload-safety
# PASS: 19319 public candidate files checked.

npm run test:public-allowlist
# PASS: hard-payload safety, submodule payload safety, and public-primary
# migration inventory. Public tracked paths: 19316.

npm run test:md-links
# PASS: 3625 Markdown files scanned, 6125 local links checked.

npm run test:repo-hygiene
# PASS: repo text hygiene and 18469 explicit text files checked.

node -e "JSON.parse(require('fs').readFileSync('developer_agent_state.json','utf8')); JSON.parse(require('fs').readFileSync('documentation_agent_state.json','utf8')); console.log('state JSON parse PASS')" ; git diff --check
# PASS: state JSON parse and whitespace diff check.
```
