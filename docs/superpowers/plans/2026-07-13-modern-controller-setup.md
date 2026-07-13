# Modern Controller Setup Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add evidence-bounded, always-visible modern-controller setup guidance to Save Lab's Game Options tab without changing copied-options semantics.

**Architecture:** Extend the existing `SavesPage` Game Options XAML with one static guidance card and one fixed-URI click handler. Protect the copy, ordering, automation IDs, fixed URL, and nonclaims with a focused source test; extend the existing native Game Options smoke only to read the new UIA elements and capture the card without invoking the browser action.

**Tech Stack:** C#/.NET 10, WinUI 3 XAML, Windows URI launcher, NUnit, FlaUI UIA3.

## Global Constraints

- Do not change AppCore, catalogs, patch bytes, options-file semantics, runtime/Ghidra lanes, canonical goal/state, or release state.
- Do not open the external URL during automated smoke.
- Preserve every existing Game Options automation ID and write behavior.
- Keep the guidance to the approved three steps and exact nonclaims.

---

### Task 1: Add and prove the controller-guidance surface

**Files:**
- Create: `OnslaughtCareerEditor.UiTests/ModernControllerSetupGuidanceTests.cs`
- Modify: `OnslaughtCareerEditor.WinUI/Pages/SavesPage.xaml`
- Modify: `OnslaughtCareerEditor.WinUI/Pages/SavesPage.xaml.cs`

**Interfaces:**
- Consumes: existing Game Options tab and WinUI `Windows.System.Launcher`.
- Produces: `ModernControllerSetupCard`, `ModernControllerSetupHeading`, `ModernControllerSetupSteps`, `ModernControllerSetupBoundary`, `OpenZigguratControllerGuideButton`, `ControllerConfigNumericCaveat`, and `OpenZigguratControllerGuideButton_Click`.

- [ ] **Step 1: Write the failing source contract test**

  Add NUnit assertions that require the six stable automation IDs; the three
  ordered instructions; the copied-options/non-detection/non-feel boundary;
  the numeric-field caveat; the browser-labeled action; the fixed
  `https://steamcommunity.com/app/1346400/discussions/0/2942494909163878759/`
  URI; and `Launcher.LaunchUriAsync`.

- [ ] **Step 2: Run the focused test and verify RED**

  Run:
  `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter FullyQualifiedName~ModernControllerSetupGuidanceTests --no-restore`

  Expected: FAIL because `ModernControllerSetupCard` and the click handler do
  not exist.

- [ ] **Step 3: Implement the minimal WinUI guidance**

  Add one `SavesSectionCardStyle` border immediately after the Game Options
  InfoBar, with a level-2 heading, one compact numbered text block, one
  boundary text block, and the external button. Add the numeric caveat inside
  the existing Control and device overrides card above its grid. Implement the
  click handler with a private fixed `Uri` and
  `await Launcher.LaunchUriAsync(...)`.

- [ ] **Step 4: Run the focused test and verify GREEN**

  Run the Step 2 command.

  Expected: PASS with no warnings or errors.

- [ ] **Step 5: Run the focused product-lane regression**

  Run:
  `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~ModernControllerSetupGuidanceTests|FullyQualifiedName~SaveLab_InfoBars_ExposeStatusAutomationIdsAndVisibilityHelpers|FullyQualifiedName~Home_DeepLinksToConfigurationEditorTab" --no-restore`

  Expected: all selected tests pass.

### Task 2: Prove native accessibility and layout

**Files:**
- Modify: `OnslaughtCareerEditor.UiTests/WinUiSaveAnalyzerInteractionSmokeTests.cs`
- Evidence only: existing ignored/generated UI smoke output.

**Interfaces:**
- Consumes: the six stable automation IDs from Task 1.
- Produces: native evidence that guidance is exposed without launching a browser.

- [ ] **Step 1: Write the failing native assertions**

  Before any file mutation in the existing Game Options smoke, find the
  heading, steps, nonclaim, browser action, and numeric caveat by automation ID;
  assert their accessible names contain the approved terms; never invoke the
  browser action.

- [ ] **Step 2: Build WinUI and run the native smoke**

  Run `npm run build:winui`, then the focused explicit
  `GameOptions_PatchesCopiedOptionsFileAndPreservesInput` NUnit smoke.

  Expected: PASS; browser remains unopened; the copied input stays unchanged.

- [ ] **Step 3: Inspect the native screenshot**

  Capture the guidance card before scrolling to the write workflow. Inspect
  the image for clipped/wrapped copy, card density, action visibility, and
  clear continued access to file selection.

- [ ] **Step 4: Run proportionate regression gates**

  Run `npm run test:winui-primary-lane`, `npm run test:doc-commands`,
  `npm run test:md-links:public-core`, `npm run test:hard-payload-safety`, and
  `git diff --check`.

  Expected: all slice-owned gates pass; any known integration-owned baseline
  failure is reported without editing its files.

### Task 3: Review, commit, push, and hand off

**Files:**
- No additional product files unless a reviewer identifies a blocking defect.

**Interfaces:**
- Consumes: frozen diff and exact verification evidence.
- Produces: independently reviewed pushed commit and integration handoff.

- [ ] **Step 1: Obtain normal and adversarial review**

  Run independent Codex normal/adversarial review plus sanitized serial
  Cursor/Grok normal/adversarial consults using `cursor-grok-4.5-high-fast`.
  Resolve material dissent against the actual diff and rerun affected tests.

- [ ] **Step 2: Verify repository scope**

  Confirm no AppCore, catalog, patch-byte, runtime/Ghidra, canonical goal/state,
  or release files changed; confirm `git status --short` contains only the
  approved slice.

- [ ] **Step 3: Commit and push**

  Commit the bounded slice on `codex/player-value-ux-patch-quality`, push it,
  and send the primary task the commit, changed paths, exact evidence, skipped
  gates, and nonclaims.
