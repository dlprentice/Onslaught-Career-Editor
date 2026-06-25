# WinUI Windowed & Mods Choice Style Helper Modularity - 2026-06-25

Status: accepted focused slice

## Scope

This slice keeps the existing Windowed & Mods selected-choice behavior, but
moves the repeated Patch Bench selected/normal button style resource lookup into
`PatchBenchChoiceVisualState.ApplyPatchBenchChoiceStyles`.

Changed paths:

- `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchChoiceVisualState.cs`
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- `OnslaughtCareerEditor.UiTests/WinUiPatchBenchInteractionSmokeTests.cs`

## Accepted Evidence

- `PatchBenchChoiceVisualState` remains a WinUI presentation helper over
  `Button`, `Style`, and `AutomationProperties.Name`.
- `BinaryPatchesPage` still owns the selected-key predicates, profile matching,
  menu-color matching, launch-preset selected marker, and manual-edit routing.
- Runtime UIA smoke now verifies launch-preset selected state clears after
  launch-owned checkbox, combo box, and text-box edits, while the create-time
  music-swap combo remains independent.

## Non-Claims

This slice did not change launch arguments, launch preset payloads, copied
profile launch behavior, safe-copy manifests/signatures, patch semantics, music
replacement behavior, online status, runtime proof, AppCore correctness logic,
release packaging, or installed-game mutation rules.

## Consult Review

- Specialist review recommended a tiny WinUI presentation extraction for the
  duplicated style lookup, while keeping page predicates and manual-clear
  routing local.
- Adversarial review allowed only guarded presentation cleanup and blocked any
  change where selected preset state could drive launch arguments, safe-copy
  prep, AppCore calls, Host/Join wording, or proof/status claims.

## Validation

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
```

Results: all passed.
