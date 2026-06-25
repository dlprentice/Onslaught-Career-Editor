# WinUI Windowed & Mods Launch Text Modularity - 2026-06-25

Status: accepted focused WinUI modularity slice

## Scope

This slice extracted copied-profile launch status and launch-modifier text
composition from `BinaryPatchesPage` into small WinUI presentation models and a
helper. It did not change launch arguments, launch preset application,
copied-profile launch behavior, safe-copy manifest logic, patch semantics,
online status, runtime proof, music audible-output proof, AppCore correctness
logic, or installed-game mutation rules.

## Changes

- Added `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchText.cs` for
  launch boundary copy, launch modifier summaries, and copied-profile launch
  readiness text.
- Added `OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextState.cs`
  and `OnslaughtCareerEditor.WinUI/Models/PatchBenchLaunchReadinessTextResult.cs`
  so readiness formatting takes reduced value state and returns text only.
- Reused that helper from both `UpdateCopiedProfileLaunchReadiness` and
  `RefreshCopiedProfileLaunchPlanPreview`, removing duplicated stale/ready/error
  text branches from `BinaryPatchesPage`.
- Kept `LaunchPresetSelection`, `ApplyLaunchPreset`,
  `BuildSelectedLaunchArguments`, `TryBuildCopiedProfileLaunchPlan`,
  copied-profile launch, safe-copy manifest handling, music-swap selection,
  online readiness, and all AppCore calls in `BinaryPatchesPage`.
- Guarded the helper against accidental behavior growth by checking that it does
  not contain launch argument construction, launch-plan validation, runtime
  launch, music-swap manifest fields, online services, copied-profile private
  state, process start, or Host/Join handlers.

## Consult Review

- Specialist review recommended extracting launch/status presentation text, not
  launch preset application. It specifically identified duplicated stale/ready
  launch-plan text in `UpdateCopiedProfileLaunchReadiness` and
  `RefreshCopiedProfileLaunchPlanPreview`.
- Adversarial review found no current behavior bug, but blocked moving
  `BuildSelectedLaunchArguments`, `TryBuildCopiedProfileLaunchPlan`,
  `PrepareCopiedProfileButton_Click`, `LaunchCopiedProfileButton_Click`, music
  swap selection, online wording, or runtime proof language into a helper. Those
  constraints were accepted and pinned by tests.
- Public-boundary/docs audit confirmed repo-specific Codex skill knowledge is
  already durable through tracked docs/tools/state rather than committed
  `.codex/skills`, and reaffirmed that full Ghidra project stores remain
  local/ignored rather than hardlinked or published.

## Validation

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_CodeRequiresAppOwnedWorkingCopyBeforeApply"
# PASS: 1 test.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
# PASS: 5 tests.

dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
# PASS: 0 warnings, 0 errors.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
# PASS: 1 runtime UIA smoke.
```

Additional closeout gates:

```powershell
npm run test:hard-payload-safety
# PASS: 19324 public candidate files checked.

npm run test:public-allowlist
# PASS: hard-payload safety, submodule payload safety, and public-primary
# migration inventory. Public tracked paths: 19320.

npm run test:md-links
# PASS: 3627 Markdown files scanned, 6125 local links checked.

npm run test:repo-hygiene
# PASS: repo text hygiene and 18473 explicit text files checked.

node -e "JSON.parse(require('fs').readFileSync('developer_agent_state.json','utf8')); JSON.parse(require('fs').readFileSync('documentation_agent_state.json','utf8')); console.log('state JSON parse PASS')"
# PASS: state JSON parse.

git diff --check
# PASS: whitespace diff check.
```
