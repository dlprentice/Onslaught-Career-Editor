# WinUI Windowed & Mods Patch-Group Helper Modularity - 2026-06-25

Status: accepted source slice

## Scope

This slice extracted Windowed & Mods patch-row grouping text from
`BinaryPatchesPage` into a small WinUI presentation helper.

Changed paths:

- `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchPatchGroups.cs`
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

## Accepted Evidence

- `BinaryPatchesPage` now calls
  `PatchBenchPatchGroups.Build(_allPatchItems)` after building the visible
  patch-item models.
- `PatchBenchPatchGroups` consumes `BinaryPatchItemModel.FunctionalArea` and
  returns `BinaryPatchGroupModel` rows only.
- Static PatchBench tests pin the exact rendered group titles, order,
  descriptions, and missing-group fail-closed message.
- Static boundary guards keep the helper free of raw frontend patch IDs,
  patch-plan builders, patch engines, safe-copy profile services, file/process
  APIs, tasks, and online wording.
- Runtime UIA smoke and existing patch-plan regression tests still pass after
  the extraction.

## Non-Claims

This is a presentation-only WinUI helper extraction. Patch group titles, order,
descriptions, and missing-group fail-closed behavior are preserved exactly.

No patch catalog rows, byte changes, `FunctionalArea` mappings,
selection policy, dependency/conflict policy, safe-copy creation or launch
behavior, music behavior, online behavior, runtime proof, release packaging,
or installed-game/original `BEA.exe` mutation rules changed.

## Consult Review

- Specialist consult accepted a narrow presentation-only extraction if
  `BinaryPatchItemModel.FunctionalArea` stayed the grouping source and patch
  semantics stayed out of the helper.
- Adversarial consult blocked any helper that gained patch keys, AppCore patch
  policy, safe-copy launch, file/process work, or online wording; the final
  helper keeps those boundaries out.

## Validation

Focused validation already passed:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests.BinaryPatchPlanBuilder_RejectsMultipleFrontendColorPresets|FullyQualifiedName~BinaryPatchRegressionTests.BinaryPatchPlanBuilder_SafeCopyProfilePresetsCarryExpectedPolicy"
```

Broad closeout validation passed:

```powershell
npm run test:doc-commands
npm run test:md-links
npm run test:hard-payload-safety
npm run test:public-allowlist
npm run test:repo-hygiene
```

Closeout counts:

- documented npm commands checked: 4295
- Markdown files scanned: 3633
- local Markdown links checked: 6125
- public candidate files checked by hard-payload safety: 19333
- public tracked paths in migration inventory: 19333
- submodule payload candidate files checked: 19517
- accepted private-only hard-payload/scratch paths: 5557
- explicit text files checked by repo line-ending guard: 18486
