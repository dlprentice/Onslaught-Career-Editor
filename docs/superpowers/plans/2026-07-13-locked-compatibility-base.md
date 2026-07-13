# Locked Compatibility Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Windowed & Mods UI continuously show the exact required compatibility pair, keep those Lab rows visibly checked and intentionally disabled, and prevent invalid optional selections from reaching safe-copy confirmation.

**Architecture:** Keep patch selection and patch-byte authority unchanged in AppCore. Add key-derived presentation properties to `BinaryPatchItemModel`, make `BinaryPatchesPage` preserve the compatibility pair across every selection path, and project safe-copy enablement/status through one pure WinUI helper consumed by both Create buttons and the pre-confirm guard.

**Tech Stack:** C# 13/.NET 10, WinUI 3 XAML, NUnit reflected-source UI tests, AppCore patch/preflight tests, Windows UI Automation, native visual inspection.

## Global Constraints

- The only required compatibility keys are exactly `resolution_gate` and `force_windowed`.
- Preserve every existing patch row, profile ID, dynamic row/check-box/details automation ID, AppCore injection rule, catalog entry, byte definition, receipt, backup, and verification path.
- Required Lab check boxes stay checked and disabled; their details expanders stay enabled and reachable.
- Required-row user and assistive copy must include `Required and automatically included in every safe game copy`.
- Add the stable live-region automation ID `PatchBenchSafeCopySelectionReadiness` near the main Create action.
- Both Create buttons use the same pure readiness result, and the click handler revalidates before confirmation.
- Native verification must not click Create, launch a game, create a safe copy, or mutate an installed game folder or original `BEA.exe`.
- Do not edit AppCore/catalog/patch bytes/runtime/Ghidra/canonical goal or state files, merge main, or release.

---

### Task 1: Pure Required-Row and Readiness Contracts

**Files:**
- Create: `OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopySelectionReadinessState.cs`
- Create: `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopySelectionReadiness.cs`
- Modify: `OnslaughtCareerEditor.WinUI/Models/BinaryPatchItemModel.cs`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchPrimitiveProjectionBoundaryTests.cs`
- Create: `OnslaughtCareerEditor.UiTests/PatchBenchLockedCompatibilityBaseTests.cs`

**Interfaces:**
- Consumes: `BinaryPatchSpec.Key` and the existing bounded string returned by `BinaryPatchPlanBuilder.ValidateVisibleSelection`.
- Produces: `BinaryPatchItemModel.IsRequiredCompatibilityBase`, `BinaryPatchItemModel.CanChangeSelection`, required-row `AccessibilityHelpText`/`UserFacingStatus`, `PatchBenchSafeCopySelectionReadiness.Build(bool hasSourceExecutable, bool isBusy, string? validationError, int optionalPatchCount)`, and `PatchBenchSafeCopySelectionReadinessState(bool CanCreate, string Status)`.

- [ ] **Step 1: Write reflected-source tests before production code**

Add tests that dynamically compile the new helper/model sources through `ReflectedWinUiTestSupport` and assert:

```csharp
AssertRequiredRow("resolution_gate");
AssertRequiredRow("force_windowed");
AssertOptionalRow("extra_graphics_default_on");

AssertReadiness(hasSourceExecutable: true, isBusy: false, validationError: null, optionalPatchCount: 0,
    canCreate: true,
    status: "Required compatibility base ready. No optional mods selected.");
AssertReadiness(true, false, null, 2, true,
    "Required compatibility base ready with 2 optional mods selected.");
AssertReadiness(false, false, null, 0, false,
    "Selection is valid. Choose a read-only BEA.exe source to create a safe game copy.");
AssertReadiness(true, true, null, 1, false,
    "Safe game copy work is already in progress.");
AssertReadiness(true, false, "Choose only one frontend margin color.", 2, false,
    "Review optional mods: Choose only one frontend margin color.");
```

Register both new `PatchBench*` files in the `ChoiceVisualBinding` boundary profile so the boundary test still requires primitive-only projection code.

- [ ] **Step 2: Run the focused tests and record RED**

Run:

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --no-restore --filter "FullyQualifiedName~PatchBenchLockedCompatibilityBaseTests|FullyQualifiedName~PatchBenchPrimitiveProjectionBoundaryTests"
```

Expected: FAIL because `PatchBenchSafeCopySelectionReadiness`, its state record, and required-row model properties do not exist.

- [ ] **Step 3: Implement the smallest pure projection**

Create the immutable state record:

```csharp
namespace OnslaughtCareerEditor.WinUI.Models;

internal sealed record PatchBenchSafeCopySelectionReadinessState(bool CanCreate, string Status);
```

Create a helper whose precedence is invalid selection, busy work, missing source, then ready:

```csharp
internal static class PatchBenchSafeCopySelectionReadiness
{
    public static PatchBenchSafeCopySelectionReadinessState Build(
        bool hasSourceExecutable,
        bool isBusy,
        string? validationError,
        int optionalPatchCount)
    {
        if (!string.IsNullOrWhiteSpace(validationError))
            return new(false, $"Review optional mods: {validationError}");
        if (isBusy)
            return new(false, "Safe game copy work is already in progress.");
        if (!hasSourceExecutable)
            return new(false, "Required compatibility base selected. Choose a read-only BEA.exe source to create a safe game copy.");
        return optionalPatchCount == 0
            ? new(true, "Required compatibility base ready. No optional mods selected.")
            : new(true, $"Required compatibility base ready with {optionalPatchCount} optional {(optionalPatchCount == 1 ? "mod" : "mods")} selected.");
    }
}
```

Add exact-key model properties and prepend the required/automatic sentence to both visible and assistive required-row text:

```csharp
public bool IsRequiredCompatibilityBase =>
    Spec.Key is "resolution_gate" or "force_windowed";
public bool CanChangeSelection => !IsRequiredCompatibilityBase;
```

- [ ] **Step 4: Run the focused tests and record GREEN**

Run the Step 2 command. Expected: PASS, including boundary classification.

---

### Task 2: Selection Invariant, Profile Semantics, and Locked XAML

**Files:**
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchLockedCompatibilityBaseTests.cs`
- Modify: `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`

**Interfaces:**
- Consumes: the compatibility profile returned by `BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId)` and Task 1 model properties.
- Produces: `_requiredCompatibilityKeys`, `EnsureRequiredCompatibilitySelected()`, required-aware `SelectOnlyKeys`, optional-count/profile comparisons, and XAML `IsEnabled="{Binding CanChangeSelection}"` while preserving existing automation bindings.

- [ ] **Step 1: Add source-contract tests for every mutation path**

Assert the page source and XAML contain the following exact behavior anchors:

```csharp
Assert.That(code, Does.Contain("private readonly HashSet<string> _requiredCompatibilityKeys;"));
Assert.That(code, Does.Contain("selected.UnionWith(_requiredCompatibilityKeys);"));
Assert.That(code, Does.Contain("private void EnsureRequiredCompatibilitySelected()"));
Assert.That(code, Does.Contain("EnsureRequiredCompatibilitySelected();"));
Assert.That(code, Does.Contain("SetEquals(selectedKeys, _requiredCompatibilityKeys)"));
Assert.That(code, Does.Contain("SetEquals(selectedKeys, _requiredCompatibilityKeys.Concat(s_modernGraphicsKeys))"));
Assert.That(xaml, Does.Contain("IsEnabled=\"{Binding CanChangeSelection}\""));
Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"{Binding CheckBoxAutomationId}\""));
Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"{Binding DetailsAutomationId}\""));
```

Also replace the superseded `WinUiProductLaneTests` expectation that the top Create button directly mirrors the main button with the readiness assignment introduced in Task 3.

- [ ] **Step 2: Run the focused page tests and record RED**

Run:

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --no-restore --filter "FullyQualifiedName~PatchBenchLockedCompatibilityBaseTests|FullyQualifiedName~WinUiProductLaneTests"
```

Expected: FAIL because selection paths do not union/reassert the pair and the check boxes are still enabled.

- [ ] **Step 3: Implement the invariant and base-aware visual semantics**

Initialize one case-insensitive required set from the existing compatibility profile before constructing item models:

```csharp
IReadOnlyList<string> defaultProfileKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId);
_requiredCompatibilityKeys = defaultProfileKeys.ToHashSet(StringComparer.OrdinalIgnoreCase);
```

Change `SelectOnlyKeys` to union the pair, add `EnsureRequiredCompatibilitySelected`, and invoke it from initialization, preset/reset/quick paths through `SelectOnlyKeys`, and immediately inside `PatchCheckBox_Changed` before invalidation/control-state refresh. Compare base-only and graphics-only states as:

```csharp
SetEquals(selectedKeys, _requiredCompatibilityKeys)
SetEquals(selectedKeys, _requiredCompatibilityKeys.Concat(s_modernGraphicsKeys))
```

Count optional rows with:

```csharp
int optionalPatchCount = visibleSelectedKeys.Count(key => !_requiredCompatibilityKeys.Contains(key));
```

Bind `CheckBox.IsEnabled` to `CanChangeSelection`; do not bind or disable the sibling `Expander`.

- [ ] **Step 4: Run the focused page tests and record GREEN**

Run the Step 2 command. Expected: PASS with stable row/check/details IDs and required-aware selection anchors.

---

### Task 3: Continuous Readiness and Pre-Confirmation Guard

**Files:**
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`
- Modify: `OnslaughtCareerEditor.UiTests/PatchBenchLockedCompatibilityBaseTests.cs`

**Interfaces:**
- Consumes: `PatchBenchSafeCopySelectionReadiness.Build(...)`, `BinaryPatchPlanBuilder.ValidateVisibleSelection(IEnumerable<string>)`, source availability, busy/process state, and optional-row count.
- Produces: one readiness state for both Create buttons, live text `PatchBenchSafeCopySelectionReadiness`, and `TryBuildSafeCopySelectionReadiness(out PatchBenchSafeCopySelectionReadinessState readiness)` used by render and click paths.

- [ ] **Step 1: Add failing readiness and no-confirm source tests**

Assert that XAML defines:

```xml
<TextBlock x:Name="PatchBenchSafeCopySelectionReadiness"
           AutomationProperties.AutomationId="PatchBenchSafeCopySelectionReadiness"
           AutomationProperties.Name="Safe copy selection readiness"
           AutomationProperties.LiveSetting="Polite" />
```

Assert page source uses one `readiness.CanCreate` assignment for both `PatchBenchPrepareCopiedProfileButton` and `PatchBenchTopCreateSafeCopyButton`, sets readiness text/name, calls `ValidateVisibleSelection`, and contains a click-handler guard ordered before `ConfirmAsync`:

```csharp
if (!TryBuildSafeCopySelectionReadiness(out PatchBenchSafeCopySelectionReadinessState readiness) || !readiness.CanCreate)
{
    PatchBenchSafeCopySelectionReadiness.Text = readiness.Status;
    OperationLogTextBox.Text = readiness.Status;
    UpdateControlState();
    return;
}
```

The test must compare source indexes and prove the guard precedes the confirmation call.

- [ ] **Step 2: Run the focused readiness tests and record RED**

Run:

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --no-restore --filter "FullyQualifiedName~PatchBenchLockedCompatibilityBaseTests"
```

Expected: FAIL because the live region, shared readiness gating, and pre-confirm return do not exist.

- [ ] **Step 3: Implement centralized readiness and defensive recheck**

Add a pure-input adapter in the page that catches only the existing bounded selection-validation exception and converts it to `validationError`; do not inspect or mutate the filesystem beyond the already-computed `hasSourceExecutable` input. Use the existing busy/process flags for `isBusy`, compute optional count excluding `_requiredCompatibilityKeys`, call the Task 1 helper, and in `UpdateControlState` assign:

```csharp
PatchBenchPrepareCopiedProfileButton.IsEnabled = readiness.CanCreate;
PatchBenchTopCreateSafeCopyButton.IsEnabled = readiness.CanCreate;
PatchBenchSafeCopySelectionReadiness.Text = readiness.Status;
AutomationProperties.SetName(PatchBenchSafeCopySelectionReadiness, readiness.Status);
```

At the beginning of `PrepareCopiedProfileButton_Click`, reassert the required pair and rebuild readiness before any confirmation text/dialog. On invalid state, update status/log and return. Do not change `GameProfilePreflightService.PrepareWindowedCompatibilityProfile`, `ApplyWindowedCompatibilityPatch: true`, `BuildRequestedPatchKeys`, output paths, receipt creation, or patch application.

- [ ] **Step 4: Run focused UI tests and build WinUI**

Run serially:

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --no-restore --filter "FullyQualifiedName~PatchBenchLockedCompatibilityBaseTests|FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~PatchBenchPrimitiveProjectionBoundaryTests"
npm run build:winui
```

Expected: all selected tests PASS and WinUI build succeeds.

---

### Task 4: Native Proof, Regression Envelope, Review, and Handoff

**Files:**
- Modify if needed for the proven UI contract only: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`, `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`, `OnslaughtCareerEditor.WinUI/Models/BinaryPatchItemModel.cs`, Task 1 readiness files, and focused UI tests.
- Do not create tracked screenshots, runtime logs, game copies, or canonical-state edits.

**Interfaces:**
- Consumes: the frozen Tasks 1-3 diff and fresh native WinUI build.
- Produces: clean native UIA/visual evidence, focused AppCore safety results, independent review convergence, one pushed bounded commit, and an exact primary-task handoff.

- [ ] **Step 1: Run the serial regression envelope**

Run:

```powershell
npm run test:winui-primary-lane
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-engine-safety
npm run test:hard-payload-safety
git diff --check
```

Expected: every command exits 0. These gates verify unchanged AppCore injection, patch planning/bytes, copied-target safety, and repository payload boundaries.

- [ ] **Step 2: Prove native state without invoking copy or game actions**

Before the authoritative run, tell the user the application test must remain hands-off. Record a pre-run process census, launch only the fresh WinUI build, navigate to Windowed & Mods, expand Lab, and use UIA to verify:

```text
PatchBenchPatchCheckBox-resolution_gate: checked=true, enabled=false
PatchBenchPatchCheckBox-force_windowed: checked=true, enabled=false
PatchBenchPatchDetails-resolution_gate: enabled=true and expandable
PatchBenchSafeCopySelectionReadiness: base-ready or source-required bounded text
PatchBenchClearSelectionButton after selecting one optional row: selected base-only state
```

Visually inspect the full app window and confirm adjacent copy makes both disabled rows intentional, details remain discoverable, no clipping/overlap occurs, and the readiness line sits with the main Create action. Never invoke either Create button or any Launch button. Close the app and record a post-run census proving zero leftover Toolkit, game, UIA, or test-host processes. If user input overlaps any run, mark it contaminated and repeat hands-off; the clean rerun supersedes it.

- [ ] **Step 3: Freeze and review the substantive diff**

After all tests and native proof are green, obtain:

- Codex normal review for spec coverage, maintainability, and test adequacy.
- Codex adversarial review for stale-state, event-ordering, invalid-selection, accessibility, and no-copy/no-game boundary failures.
- Sanitized serial Cursor/Grok normal then adversarial consults using the approved `cursor-grok-4.5-high-fast` binding in an empty temporary workspace; share only bounded source diff/spec, never local paths, raw proof, credentials, authority docs, or private payloads.

Resolve every blocking finding with a new focused RED/GREEN cycle and rerun any invalidated native/gate evidence. Record evidence-based Codex acceptance if one nonblocking advisory suggestion is declined.

- [ ] **Step 4: Verify scope, commit, push, and hand off**

Run:

```powershell
git status --short
git diff --stat
git diff -- OnslaughtCareerEditor.AppCore patches goal.md developer_agent_state.json documentation_agent_state.json
```

Expected: only the approved WinUI/UI-test/plan paths differ; the AppCore/catalog/canonical-state diff is empty. Stage only those paths, commit once as `feat(winui): lock required compatibility base`, push `codex/player-value-ux-patch-quality`, then send the primary task the commit hash, changed paths, exact test/native/review evidence, superseded contaminated-run note if applicable, nonclaims, and skipped release gates.
