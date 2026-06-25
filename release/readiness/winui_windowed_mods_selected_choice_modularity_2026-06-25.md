# WinUI Windowed & Mods Selected-Choice Modularity - 2026-06-25

Status: accepted focused WinUI modularity slice

## Scope

This slice reduced `BinaryPatchesPage` selected-choice UI plumbing for the
Windowed & Mods profile/menu-background controls. It did not change patch
catalog rows, selected patch semantics, safe-copy creation, launch behavior,
online status, music status, runtime proof, or installed-game mutation rules.

## Changes

- Added `OnslaughtCareerEditor.WinUI/Models/PatchBenchSelectedChoiceState.cs`
  for immutable selected/normal automation-name state.
- Added `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchChoiceVisualState.cs`
  to apply selected/normal button styles and UI Automation names.
- Kept `BinaryPatchesPage` as the owner of selected-key predicates, profile
  matching, menu-color matching, and safe-copy state.
- Extended the runtime UIA smoke to click `PatchBenchClearSelectionButton` and
  verify the compatibility-only selected-status copy.

## Consult Review

- Specialist WinUI modularity consult recommended a presentation-only
  selected-choice state shape under the WinUI layer and warned not to move
  safe-copy profile manifest logic in this slice.
- Adversarial UI/UX review found no blocker after the extraction stayed narrow.
  It called out risks around visible selected rows versus effective safe-copy
  patch keys, UIA selected names, stable `PatchBench*` AutomationIds, and
  direct patch-row exclusivity. The clear-selection UIA hardening was accepted.

## Validation

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
# PASS: 0 warnings, 0 errors.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
# PASS: 5 tests.

dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GameProfilePreflightServiceTests.PrepareWindowedCompatibilityProfile_AppliesSelectedVisiblePatchRowsToSafeCopyOnly|FullyQualifiedName~GameProfilePreflightServiceTests.PrepareWindowedCompatibilityProfile_RecordsEnhancedPreviewPresetInManifest|FullyQualifiedName~GameProfilePreflightServiceTests.BuildPrepareReceipt"
# PASS: 5 tests.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
# PASS: 1 runtime UIA smoke.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests"
# PASS: 15 tests.
```

Broad repo gates should still run before commit closeout.

Additional closeout gates passed:

```powershell
npm run test:hard-payload-safety
# PASS: 19316 public candidate files checked.

npm run test:public-allowlist
# PASS: hard-payload safety, submodule payload safety, and public-primary
# migration inventory. Public tracked paths: 19316.

npm run test:md-links
# PASS: 3625 Markdown files scanned, 6125 local links checked.

npm run test:repo-hygiene
# PASS: repo text hygiene and 18469 explicit text files checked.
```
