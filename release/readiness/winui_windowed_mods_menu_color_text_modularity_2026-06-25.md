# WinUI Windowed & Mods Menu-Color Text Modularity - 2026-06-25

Status: accepted focused slice

## Scope

This slice keeps the existing Windowed & Mods menu-background behavior, but
moves the selected menu-background status copy into a small WinUI presentation
helper.

Changed paths:

- `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchMenuColorSelectionText.cs`
- `OnslaughtCareerEditor.WinUI/Models/PatchBenchMenuColorSelectionKind.cs`
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- `OnslaughtCareerEditor.UiTests/WinUiPatchBenchInteractionSmokeTests.cs`

## Accepted Evidence

- `BinaryPatchesPage` still owns the raw `frontend_clear_screen_*` patch keys,
  click handlers, selected-key predicates, menu-color matching, patch-row
  selection, and safe-copy behavior.
- `PatchBenchMenuColorSelectionText` formats only
  `PatchBenchMenuColorSelectionKind` values and contains no raw patch keys,
  patch planner calls, safe-copy calls, launch logic, online wording, process
  calls, or file IO.
- Runtime UIA smoke now selects red, green, black, and clear menu-background
  choices and verifies the visible selected-status text.

## Non-Claims

This slice did not change patch rows, byte patches, copied-profile launch
behavior, safe-copy manifests/signatures, music replacement behavior, online
status, runtime proof, AppCore correctness logic, release packaging, or
installed-game mutation rules.

## Consult Review

- Specialist review allowed a tiny presentation extraction only if the page
  retained patch-key ownership and selected-color mapping.
- Adversarial review blocked passing raw patch keys into a new helper. The
  accepted shape maps page-local raw keys to a presentation enum first, then
  formats the selected-status text through the helper.

## Validation

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests.BinaryPatchPlanBuilder_RejectsMultipleFrontendColorPresets|FullyQualifiedName~BinaryPatchRegressionTests.BinaryPatchPlanBuilder_SafeCopyProfilePresetsCarryExpectedPolicy"
```

Results: all matched tests passed.

Additional closeout gates passed:

```powershell
npm run build:winui
npm run test:winui-primary-lane
npm run test:doc-commands
npm run test:md-links
npm run test:hard-payload-safety
npm run test:public-allowlist
npm run test:repo-hygiene
```

Results: all passed. `test:winui-primary-lane` built the solution, passed
`1178/1178` AppCore tests, and passed `87` WinUI tests with `2` catalog-
dependent skips. `test:public-allowlist` passed hard-payload safety, submodule
payload safety, and public-primary migration inventory; public tracked paths
were `19331` and accepted private-only hard-payload/scratch paths remained
`5557`.
