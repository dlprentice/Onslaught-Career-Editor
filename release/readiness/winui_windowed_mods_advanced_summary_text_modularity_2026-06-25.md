# WinUI Windowed & Mods Advanced Summary Text Modularity - 2026-06-25

Status: accepted source slice

## Scope

This slice moved the Windowed & Mods advanced BEA.exe-only selection-summary
copy from `BinaryPatchesPage` into the existing selected-profile presentation
helper.

Changed paths:

- `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSelectedProfileText.cs`
- `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

## Accepted Evidence

- `BinaryPatchesPage` now assigns `SelectionSummaryTextBlock.Text` through
  `PatchBenchSelectedProfileText.BuildAdvancedCopySelectionSummary(...)`.
- `PatchBenchSelectedProfileText` formats the no-selection, known profile,
  graphics-only, and manual selection messages from
  `PatchBenchSelectedProfileTextState`.
- `BinaryPatchesPage` still owns selected-key and profile classification:
  `MatchSelectableSafeCopyProfileId(visibleSelectedKeys)`,
  `SetEquals(visibleSelectedKeys, s_modernGraphicsKeys)`, and
  `ProfilePresetId: MatchSelectableSafeCopyProfileId(selectedPatchKeys)` remain
  page-owned.
- Static tests pin the helper boundary so the helper may not gain selected-key
  collections, `BuildSafeCopyProfilePatchKeys`, visible-selection validation,
  profile preset IDs, music controls, launch controls, file/process work,
  online wording, or release/package behavior.

## Non-Claims

This is a WinUI presentation-text extraction only. It does not change patch
catalog rows, byte patches, selected-key semantics, safe-copy profile matching,
`ProfilePresetId`, launch arguments, safe-copy signatures or manifests, copied
profile launch behavior, music behavior, online readiness, runtime proof,
release packaging, app release assets, or installed-game/original `BEA.exe`
mutation rules.

## Consult Review

- Specialist consult recommended the extraction only if the helper receives
  already-classified presentation state and the page keeps selection/profile
  matching.
- Adversarial consult blocked moving `BuildSelectionSummary` wholesale because
  that would move selected-key/profile policy into a presentation helper.
- Codex root accepted the narrower formatter-only extraction and added static
  guards around both the page-owned classification and helper-owned copy.

## Focused Validation

Red check:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow"
```

Result: FAIL for the intended missing
`PatchBenchSelectedProfileText.BuildAdvancedCopySelectionSummary(...)` call.

Green checks:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow|FullyQualifiedName~WinUiProductLaneTests.PatchBench_PresentationHelpersStayBehaviorFree"
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Results:

- focused source-shape/helper-boundary filter: PASS, 2 tests
- full PatchBench static filter: PASS, 6 tests
- WinUI build: PASS, 0 warnings, 0 errors

## Broad Closeout

Broad closeout validation passed:

```powershell
npm run test:winui-primary-lane
npm run test:doc-commands
npm run test:md-links
npm run test:hard-payload-safety
npm run test:public-allowlist
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
npm run test:repo-hygiene
git diff --check
Get-Process BEA,cdb,OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue | Select-Object ProcessName,Id,Path
```

Closeout counts:

- WinUI primary lane: PASS
- WinUI solution build: PASS, 0 warnings, 0 errors
- AppCore tests: 1178 passed
- WinUI tests from primary lane: 88 passed, 2 catalog-dependent skips
- fresh WinUI UI test rerun after operator interference warning: PASS, 88
  passed, 2 catalog-dependent skips
- documented npm commands checked: 4301
- Markdown files scanned: 3634
- local Markdown links checked: 6125
- hard-payload public candidate files checked: 19335
- public allowlist submodule/payload candidate files checked: 19519
- public-primary migration inventory: 19334 public tracked paths, 5557
  accepted private-only hard-payload/scratch paths
- repo line-ending guard: 18487 explicit text files checked
- whitespace diff check: PASS
- process cleanup check: no `BEA`, `cdb`, or WinUI process rows returned

Final read-only review found no blockers. It suggested direct helper behavior
tests as a non-blocking future improvement, but this project currently keeps
WinUI helper coverage in source-shape/static guards rather than referencing the
WinUI assembly from `OnslaughtCareerEditor.UiTests`.
