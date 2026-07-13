# Patch Bench Coherent Lab Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Patch Bench one complete, truthful Normal-versus-Lab boundary and disclose every active setting that can affect the next copied profile before Create.

**Architecture:** Recompose existing WinUI controls under one full-width outer Lab with five purpose groups; existing names, IDs, handlers, and state stay authoritative. Add a small primitive-only state record and pure text helper for creation-input disclosure, then project current page controls into that state for the live status and pre-confirmation copy.

**Tech Stack:** C#/.NET 10, WinUI 3 XAML, NUnit static/reflection tests, FlaUI native UIA.

## Global Constraints

- Preserve all existing control IDs, accessible names, handlers, values, recipe IDs, patch keys, patch bytes, AppCore injection, receipts, safe-copy semantics, and launch semantics.
- `PatchBenchLabSelectionStatus` and Create confirmation count only settings that can affect the next copied profile.
- Online artifact viewing, post-create music staging/restore, and BEA.exe-only operations remain separately labeled and never count as creation inputs.
- Keep the normal source/create/receipt/play/stop/local split-screen journey outside Lab.
- Do not touch Asset Library/exporter/bootstrap, runtime/Ghidra evidence, installed game files, original `BEA.exe`, canonical goal/state, release assets, or integration-owned observer docsync drift.

---

### Task 1: Pin the full boundary and disclosure model RED

**Files:**
- Create: `OnslaughtCareerEditor.UiTests/PatchBenchCoherentLabBoundaryTests.cs`
- Create: `OnslaughtCareerEditor.UiTests/PatchBenchLabCreationInputTextTests.cs`

**Interfaces:**
- Consumes: current `BinaryPatchesPage.xaml` and `BinaryPatchesPage.xaml.cs` source.
- Produces: required XAML ancestry and the exact `PatchBenchLabCreationInputState` / `PatchBenchLabCreationInputText` contract.

- [ ] **Step 1: Add failing XAML ancestry tests**

Parse the XAML and require these outer-Lab descendants:

```csharp
string[] labControls =
[
    "PatchBenchStableDefaultsButton",
    "PatchBenchPatchRows",
    "PatchBenchAdvancedLaunchOptionsExpander",
    "PatchBenchOnlineTechnicalDetailsExpander",
    "PatchBenchCreateMusicSwapPresetComboBox",
    "PatchBenchStageCopiedTrackSwapButton",
    "PatchBenchAdvancedTechnicalExpander",
];
```

Require these controls outside the outer Lab:

```csharp
string[] normalControls =
[
    "SourceExePathTextBox",
    "PatchBenchPrepareCopiedProfileButton",
    "PatchBenchCopiedProfileReceipt",
    "PatchBenchLaunchCopiedProfileButton",
    "PatchBenchStopCopiedProfileButton",
    "PatchBenchLocalMultiplayerProbeButton",
    "PatchBenchLabSelectionStatus",
];
```

Also require five collapsed named group expanders with stable IDs:
`PatchBenchLabPatchExperimentsExpander`,
`PatchBenchLabLaunchControlExpander`,
`PatchBenchLabOnlineResearchExpander`,
`PatchBenchLabMusicExperimentsExpander`, and
`PatchBenchLabBeaDiagnosticsExpander`.

- [ ] **Step 2: Add failing pure formatter tests**

Reflect the new state/helper and assert exact projections:

```csharp
[TestCase(0, 0, 0, false, "Extra settings for next copy: none active.")]
[TestCase(1, 0, 0, false, "Extra settings for next copy: 1 patch choice.")]
[TestCase(2, 1, 2, true,
    "Extra settings for next copy: 2 patch choices; 1 launch modifier; 2 copied-options changes; 1 create-time music experiment.")]
public void Status_ListsOnlyCreationInputCategories(
    int patches, int launch, int copiedOptions, bool music, string expected)
```

Require `BuildConfirmationSection(state)` to return
`"Settings affecting this copy:\n" + BuildStatus(state)` and verify that
neither public helper method accepts online-artifact, post-create music, or
BEA.exe-only operation state.

- [ ] **Step 3: Run focused tests and preserve RED output**

Run:

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~PatchBenchCoherentLabBoundaryTests|FullyQualifiedName~PatchBenchLabCreationInputTextTests" --no-restore
```

Expected: FAIL because the new IDs and helper types do not exist and the
advanced/music/BEA diagnostics remain outside the outer Lab.

### Task 2: Implement the pure creation-input projection and live status

**Files:**
- Create: `OnslaughtCareerEditor.WinUI/Models/PatchBenchLabCreationInputState.cs`
- Create: `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLabCreationInputText.cs`
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchCoherentLabBoundaryTests.cs`

**Interfaces:**
- Produces: `PatchBenchLabCreationInputState(int OptionalPatchCount, int LaunchModifierCount, int CopiedOptionsCount, bool HasCreateTimeMusicExperiment)`.
- Produces: `PatchBenchLabCreationInputText.BuildStatus(state)` and `BuildConfirmationSection(state)`.
- Produces: page-local `BuildLabCreationInputState()` and
  `CountSelectedLaunchModifiers()` used by both live status and Create
  confirmation.

- [ ] **Step 1: Implement the primitive state and formatter**

Use invariant category order: patch choices, launch modifiers, copied-options
changes, create-time music experiment. Omit zero categories and pluralize each
label exactly. Required compatibility keys are excluded before state creation.

- [ ] **Step 2: Project current controls into one page-local state**

Implement `BuildLabCreationInputState()` using:

```csharp
int optionalPatchCount = GetVisibleSelectedKeys()
    .Count(key => !_requiredCompatibilityKeys.Contains(key));
int launchModifierCount = CountSelectedLaunchModifiers();
int copiedOptionsCount =
    (PatchBenchPersistControllerConfigOption.IsChecked == true ? 1 : 0) +
    (PatchBenchSharpenMouseLookOption.IsChecked == true ? 1 : 0) +
    (PatchBenchInvertWalkerYOption.IsChecked == true ? 1 : 0) +
    (PatchBenchInvertFlightYOption.IsChecked == true ? 1 : 0);
```

Implement `CountSelectedLaunchModifiers()` by counting the seven launch
checkboxes (`SkipFmv`, `NoMusic`, `NoSound`, `HighDetail`, `NoStaticShadows`,
`NoRumble`, and `ShowDebugTrace`), nonempty `PatchBenchLevelLaunchOption`, a
selected `PatchBenchConfigurationLaunchPresetComboBox` value, and nonempty
`PatchBenchTextureRamLimitLaunchOption`. One UI choice counts once even when it
emits a flag/value pair.

- [ ] **Step 3: Refresh the live status from `UpdateControlState`**

Set both text and accessible name:

```csharp
PatchBenchLabSelectionStatus.Text =
    PatchBenchLabCreationInputText.BuildStatus(BuildLabCreationInputState());
AutomationProperties.SetName(
    PatchBenchLabSelectionStatus,
    PatchBenchLabSelectionStatus.Text);
```

Retain existing checkbox/combo/text handlers. Add or adjust only a handler
needed to ensure every launch-level, texture-RAM, copied-options, and create-time
music change reaches `UpdateControlState()`.

- [ ] **Step 4: Run pure formatter and routing tests GREEN**

Run the Task 1 filter. Expected: formatter tests PASS; ancestry tests may remain
RED until Task 3.

### Task 3: Recompose XAML into one complete Lab boundary

**Files:**
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchPlayerLabCurationTests.cs`
- Modify: `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

**Interfaces:**
- Consumes: existing named controls and handlers unchanged.
- Produces: one full-width outer `PatchBenchLabExpander`, five named group expanders, and always-visible `PatchBenchLabSelectionStatus`.

- [ ] **Step 1: Move the outer Lab after the normal two-column surface**

Keep its existing name/ID/header and `IsExpanded="False"`. Close the normal grid
after the local split-screen journey, then place the Lab as the next full-width
page child. Do not clone any control.

- [ ] **Step 2: Add the five purpose groups and move existing blocks unchanged**

Wrap existing blocks under the group IDs from Task 1, each with
`IsExpanded="False"`. Keep local split-screen action/status outside Lab; move
the exact launch-plan preview into Launch and control diagnostics. Place online
technical details/artifact loaders under Online research, both create-time and
post-create music controls under Music experiments, and the existing
`PatchBenchAdvancedTechnicalExpander` under BEA.exe-only diagnostics.

- [ ] **Step 3: Add visible disclosure next to Create**

Add:

```xml
<TextBlock x:Name="PatchBenchLabSelectionStatus"
           AutomationProperties.AutomationId="PatchBenchLabSelectionStatus"
           AutomationProperties.Name="Extra settings affecting the next copied profile"
           AutomationProperties.LiveSetting="Polite"
           Text="Extra settings for next copy: none active."
           TextWrapping="WrapWholeWords" />
```

Add nearby copy stating that post-create music tools, online research artifacts,
and BEA.exe-only operations are reported separately and do not affect Create.

- [ ] **Step 4: Run focused hierarchy/product tests GREEN**

Run:

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~PatchBenchCoherentLabBoundaryTests|FullyQualifiedName~PatchBenchPlayerLabCurationTests|FullyQualifiedName~WinUiProductLaneTests" --no-restore
```

Expected: PASS with no duplicate XAML names and all representative ancestry
assertions green.

### Task 4: Put the fresh creation-input summary into pre-confirmation

**Files:**
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchCoherentLabBoundaryTests.cs`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchLockedCompatibilityBaseTests.cs`

**Interfaces:**
- Consumes: `BuildLabCreationInputState()` and `BuildConfirmationSection(state)`.
- Preserves: existing readiness revalidation, busy latch, source checks, `GameProfilePrepareOptions`, confirmation cancellation, and preflight ordering.

- [ ] **Step 1: Add RED source-order assertions**

Require `BuildLabCreationInputState()` after the click-time readiness check and
before `ConfirmAsync`, require `BuildConfirmationSection(...)` in confirmation
copy, and retain the existing assertion that no file/copy/preflight mutation
occurs before confirmation.

- [ ] **Step 2: Compute and show the fresh summary**

Immediately after reading selected keys, launch arguments, copied-options, and
create-time music selection into locals, build the state from those same values.
Append this exact section before the disk-space paragraph:

```csharp
$"\n\n{PatchBenchLabCreationInputText.BuildConfirmationSection(creationInputState)}"
```

Do not mention or inspect online artifacts, post-create music state, or
BEA.exe-only state in this path.

- [ ] **Step 3: Run focused safety tests GREEN**

Run the Task 3 filter plus `PatchBenchLockedCompatibilityBaseTests`. Expected:
all PASS; both Create buttons still route to the same guarded handler.

### Task 5: Native acceptance, review envelope, and handoff

**Files:**
- Modify: `OnslaughtCareerEditor.UiTests/WinUiPatchBenchInteractionSmokeTests.cs`
- Evidence only: ignored temp screenshots and command output.

**Interfaces:**
- Produces: authoritative hands-off UIA/visual evidence without copy/game action.

- [ ] **Step 1: Extend native smoke without mutating game/copy state**

Assert the outer Lab starts collapsed; normal readiness/Create/receipt/Play/Stop
and local split-screen IDs are reachable; representative specialist IDs are
unreachable until their outer and group expanders open. Select one reversible,
in-memory Lab creation choice, collapse Lab, and assert
`PatchBenchLabSelectionStatus` reports it. Do not click Create, Play, Stage,
Restore, Apply, or any BEA.exe action.

- [ ] **Step 2: Run serial focused gates**

Run the focused UI tests, then:

```powershell
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
npm run build:winui
```

Expected: all PASS; build has zero errors.

- [ ] **Step 3: Obtain an exclusive desktop lease and run native evidence**

With zero pre-census for Toolkit test hosts, BEA, and CDB, run only the focused
Patch Bench native smoke hands-off. Capture collapsed and expanded screenshots
at normal width and 760px, inspect hierarchy/wrapping/intent, and record zero
post-census. Any user click contaminates the run and requires a clean rerun.

- [ ] **Step 4: Run proportionate independent review**

Freeze the diff, then obtain Codex normal and adversarial review plus sanitized,
serial Cursor/Grok normal and adversarial consults using the approved binding.
Resolve blocking findings and rerun affected gates; Codex owns acceptance.

- [ ] **Step 5: Verify, commit, push, and hand off**

Run `git diff --check`, focused changed-contract tests, and `git status --short`.
Commit the bounded implementation and push
`codex/player-value-ux-patch-quality`. Send the primary task the commit, changed
paths, exact gates/results, screenshot paths, process census, nonclaims, skipped
release gates, and confirmation that installed game/original `BEA.exe` and
canonical state were untouched.
