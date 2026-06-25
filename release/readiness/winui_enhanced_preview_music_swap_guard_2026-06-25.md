# WinUI Enhanced Preview Music-Swap Guard - 2026-06-25

Status: accepted test-hardening slice

## Scope

This slice tightened tests around the `Windowed & Mods` Enhanced Profile Preview
selector and safe-copy create-time music-swap option. It did not change user
behavior, patch catalog rows, patch-row selection semantics, safe-copy profile
matching, safe-copy creation, launch behavior, online status, music audible
output, runtime proof, AppCore correctness logic, or installed-game mutation
rules.

## Changes

- Scoped the static `NoCreateMusicSwapPresetIndex` assertion to the
  `BinaryPatchesPage` constructor instead of treating any file-wide occurrence
  as proof.
- Added static guards that `EnhancedPreviewPresetButton_Click` does not touch
  `PatchBenchCreateMusicSwapPresetComboBox`, `NoCreateMusicSwapPresetIndex`, or
  the create-time music-swap preset constants.
- Pinned the default user-facing combo contract: `NoCreateMusicSwapPresetIndex`
  is `0` and the first XAML item is `No music swap`.
- Extended the existing runtime UIA PatchBench smoke: it selects
  `BEA_02 over BEA_01`, invokes Enhanced Profile Preview, and verifies the
  create-time music-swap selection remains unchanged.

## Consult Review

- Specialist review recommended exactly this no-behavior-change boundary:
  constructor-scoped default assertion plus a negative assertion that Enhanced
  Preview does not touch the music-swap combo.
- Adversarial review accepted the source-only guard as useful but asked for a
  stronger UIA preservation check. That UIA check was added and passed.

## Validation

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_CodeRequiresAppOwnedWorkingCopyBeforeApply"
# PASS: 1 test.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
# PASS: 1 runtime UIA smoke.

dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
# PASS: 5 tests.

dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
# PASS: 0 warnings, 0 errors.

npm run test:winui-primary-lane
# PASS: solution build 0 warnings/errors; AppCore 1177/1177; WinUI UI tests
# 87 passed / 2 expected catalog-dependent skips.
```

Additional closeout gates passed:

```powershell
npm run test:hard-payload-safety
# PASS: 19320 public candidate files checked.

npm run test:public-allowlist
# PASS: hard-payload safety, submodule payload safety, and public-primary
# migration inventory. Public tracked paths: 19319.

npm run test:md-links
# PASS: 3626 Markdown files scanned, 6125 local links checked.

npm run test:repo-hygiene
# PASS: repo text hygiene and 18472 explicit text files checked.

node -e "JSON.parse(require('fs').readFileSync('developer_agent_state.json','utf8')); JSON.parse(require('fs').readFileSync('documentation_agent_state.json','utf8')); console.log('state JSON parse PASS')" ; git diff --check
# PASS: state JSON parse and whitespace diff check.
```
