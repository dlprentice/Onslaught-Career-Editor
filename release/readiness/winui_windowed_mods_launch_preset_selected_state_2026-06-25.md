# WinUI Windowed & Mods Launch Preset Selected State - 2026-06-25

Status: accepted focused WinUI UX slice

## Scope

This slice adds visible selected-state styling and selected UI Automation names
for the Windowed & Mods launch preset buttons:

- `PatchBenchQuietCaptureLaunchPresetButton`
- `PatchBenchHighDetailLaunchPresetButton`
- `PatchBenchControlBaselinePresetButton`
- `PatchBenchControlSharpenedPresetButton`
- `PatchBenchControlConfig2PresetButton`
- `PatchBenchControlConfig3PresetButton`
- `PatchBenchControlConfig4PresetButton`

It is presentation/UIA only. It does not change launch arguments, launch preset
payloads, copied-profile launch behavior, safe-copy manifest/signature logic,
patch semantics, online status, runtime proof, music audible-output proof,
AppCore correctness logic, or installed-game mutation rules.

## Changes

- Reused the existing `PatchBenchChoiceButtonStyle`,
  `PatchBenchChoiceSelectedButtonStyle`, and `PatchBenchChoiceVisualState`
  helper for the seven launch preset buttons.
- Added page-local `LaunchPresetChoice` presentation state so the last selected
  launch preset has a visible selected border/weight and a selected UIA name.
- Kept `LaunchPresetSelection`, `ApplyLaunchPreset`,
  `BuildSelectedLaunchArguments`, `TryBuildCopiedProfileLaunchPlan`,
  safe-copy launch, manifest handling, music, online readiness, and all AppCore
  calls in `BinaryPatchesPage`.
- Cleared the selected marker when a user manually edits launch-preset-owned
  controls such as launch flags, mission id, controller config, mouse
  sensitivity, invert flags, or texture RAM.
- Deliberately did not clear launch-preset selected state from
  `PatchBenchIncludeSavegamesOption` or
  `PatchBenchCreateMusicSwapPresetComboBox`, because those are safe-copy
  create-time choices rather than launch-preset identity controls.
- Kept the local split-screen helper outside the seven selected launch presets;
  it clears the launch-preset marker and still says it is not Host/Join or
  online play.

## Consult Review

- Specialist consult recommended using the existing selected-choice helper,
  adding only page-local presentation state, clearing the marker only for
  launch-preset-owned manual edits, and keeping the local split-screen helper
  outside the selected launch-preset set.
- Adversarial review blocked selected-state from becoming a second source of
  truth for launch behavior. It required guards that launch arguments,
  copied-profile launch plans, safe-copy content signatures, music swap
  selection, and online wording do not depend on UIA names/styles/selection.
- Final implementation review found no blocker. It confirmed that selected
  launch-preset state only feeds style/UIA names, while launch arguments still
  come from the actual launch-option controls and copied-profile launch plans
  still flow through AppCore.
- Minor non-blocking test caveat: the UIA helper used for launch-preset buttons
  invokes and clicks the same element for reliability. The current uses are
  idempotent preset buttons only; do not reuse that helper for destructive or
  non-idempotent actions without changing it.

## Focused Validation

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
# PASS: 5 tests.

dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
# PASS: 0 warnings, 0 errors.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
# PASS: 1 runtime UIA smoke.
```

The runtime UIA smoke now verifies selected-state switching for the launch
preset buttons, confirms the create-time music swap selection stays independent,
and confirms a manual mission-id edit clears the selected launch-preset marker.

## Closeout Gates

```powershell
npm run test:doc-commands
# PASS: 4278 documented npm commands checked; public package command check passed.

npm run test:hard-payload-safety
# PASS: 19325 public candidate files checked.

npm run test:public-allowlist
# PASS: hard-payload safety, submodule payload safety, and public-primary
# migration inventory. Public tracked paths: 19324; submodule candidate files:
# 19509; allowed private-only hard-payload/scratch paths: 5557.

npm run test:md-links
# PASS: 3628 Markdown files scanned, 6125 local links checked.

npm run test:repo-hygiene
# PASS: repo text hygiene and 18477 explicit text files checked.

node -e "JSON.parse(require('fs').readFileSync('developer_agent_state.json','utf8')); JSON.parse(require('fs').readFileSync('documentation_agent_state.json','utf8')); console.log('state JSON parse PASS')"
# PASS: state JSON parse.

git diff --check
# PASS: whitespace diff check.

Get-Process BEA,cdb,OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue | Select-Object ProcessName,Id,Path
# PASS: no matching process output.
```
