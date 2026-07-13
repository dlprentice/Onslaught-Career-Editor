# Patch Bench Narrow Action Labels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make both normal Compatibility action labels fully readable at a 760-pixel native window width without changing either action.

**Architecture:** Keep the existing two-column Compatibility-card grid and replace each button's string content with an explicit centered `TextBlock` that wraps whole words. Protect the presentation contract with one focused XAML test and add one 760-pixel screenshot checkpoint to the existing non-copying Patch Bench native smoke.

**Tech Stack:** C# 13, NUnit 4, WinUI 3 XAML, FlaUI/UIA3

## Global Constraints

- Preserve the exact labels `Reset to Compatibility Copy` and `Clear optional mods`.
- Preserve `PatchBenchWindowedPresetButton` and `PatchBenchClearSelectionButton`, their automation IDs, accessible names, click handlers, semantics, and normal-card placement.
- Use the existing two-column layout, centered whole-word wrapping, and equal minimum height.
- Product behavior changes are restricted to `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml`.
- Do not change AppCore, catalogs, profiles, patch bytes, receipts, runtime/Ghidra evidence, Asset Library behavior, canonical goal/state, distribution, or release state.
- The authoritative native run is hands-off, performs no copy/game action, and records zero relevant processes before and after.

---

### Task 1: Protect And Implement Readable Compatibility Actions

**Files:**
- Create: `OnslaughtCareerEditor.UiTests/PatchBenchNarrowActionLabelsTests.cs`
- Modify: `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml:177-198`
- Modify: `OnslaughtCareerEditor.UiTests/WinUiPatchBenchInteractionSmokeTests.cs:62-68`

**Interfaces:**
- Consumes: existing XAML buttons `PatchBenchWindowedPresetButton` and `PatchBenchClearSelectionButton`; existing native helper `CaptureChoiceStateScreenshot(Window, IntPtr, string, string, string, int, int)`.
- Produces: two explicit wrapping label `TextBlock` children and native evidence file `patch-compatibility-actions-narrow.png` under the smoke's temporary evidence directory.

- [ ] **Step 1: Write the failing source contract test**

Create `OnslaughtCareerEditor.UiTests/PatchBenchNarrowActionLabelsTests.cs`:

```csharp
using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[TestFixture]
public sealed class PatchBenchNarrowActionLabelsTests
{
    [Test]
    public void CompatibilityActions_UseReadableEqualHeightWrappingLabels()
    {
        XDocument document = XDocument.Parse(ReadRepoFile(
            "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"));

        XElement resetButton = FindByAutomationId(document, "PatchBenchWindowedPresetButton");
        XElement clearButton = FindByAutomationId(document, "PatchBenchClearSelectionButton");

        Assert.Multiple(() =>
        {
            AssertButton(resetButton, "Reset to Compatibility Copy", "Select Compatibility Copy profile", "WindowedPresetButton_Click");
            AssertButton(clearButton, "Clear optional mods", "Clear optional mod rows; safe copies still include required compatibility", "ClearSelectionButton_Click");
            Assert.That((string?)resetButton.Attribute("MinHeight"), Is.EqualTo("56"));
            Assert.That((string?)clearButton.Attribute("MinHeight"), Is.EqualTo("56"));
        });
    }

    private static void AssertButton(XElement button, string label, string accessibleName, string handler)
    {
        XElement content = button.Elements().Single(element => element.Name.LocalName == "TextBlock");
        Assert.Multiple(() =>
        {
            Assert.That((string?)button.Attribute("AutomationProperties.Name"), Is.EqualTo(accessibleName));
            Assert.That((string?)button.Attribute("Click"), Is.EqualTo(handler));
            Assert.That((string?)content.Attribute("Text"), Is.EqualTo(label));
            Assert.That((string?)content.Attribute("TextWrapping"), Is.EqualTo("WrapWholeWords"));
            Assert.That((string?)content.Attribute("TextAlignment"), Is.EqualTo("Center"));
            Assert.That((string?)content.Attribute("HorizontalAlignment"), Is.EqualTo("Center"));
        });
    }

    private static XElement FindByAutomationId(XContainer document, string automationId) =>
        document.Descendants().Single(element =>
            string.Equals((string?)element.Attribute("AutomationProperties.AutomationId"), automationId, StringComparison.Ordinal));

    private static string ReadRepoFile(params string[] parts)
    {
        string path = Path.Combine(parts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }
}
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~PatchBenchNarrowActionLabelsTests"
```

Expected: FAIL because each button still has a string `Content` attribute and no child `TextBlock` or local `MinHeight="56"`.

- [ ] **Step 3: Implement the minimal XAML presentation change**

Replace only the two button definitions with:

```xml
<Button x:Name="PatchBenchWindowedPresetButton"
        AutomationProperties.AutomationId="PatchBenchWindowedPresetButton"
        AutomationProperties.Name="Select Compatibility Copy profile"
        Grid.Column="0"
        HorizontalAlignment="Stretch"
        MinHeight="56"
        Style="{StaticResource PatchBenchChoiceButtonStyle}"
        Click="WindowedPresetButton_Click">
    <TextBlock Text="Reset to Compatibility Copy"
               TextWrapping="WrapWholeWords"
               TextAlignment="Center"
               HorizontalAlignment="Center" />
</Button>
<Button x:Name="PatchBenchClearSelectionButton"
        AutomationProperties.AutomationId="PatchBenchClearSelectionButton"
        AutomationProperties.Name="Clear optional mod rows; safe copies still include required compatibility"
        Grid.Column="1"
        HorizontalAlignment="Stretch"
        MinHeight="56"
        Style="{StaticResource PatchBenchChoiceButtonStyle}"
        Click="ClearSelectionButton_Click">
    <TextBlock Text="Clear optional mods"
               TextWrapping="WrapWholeWords"
               TextAlignment="Center"
               HorizontalAlignment="Center" />
</Button>
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the command from Step 2.

Expected: PASS, 1 test.

- [ ] **Step 5: Add the native 760-pixel evidence checkpoint**

In `WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia`, immediately after the initial Compatibility UIA assertions, add:

```csharp
CaptureChoiceStateScreenshot(
    window,
    app.MainWindowHandle,
    evidenceDir,
    "patch-compatibility-actions-narrow.png",
    "PatchBenchWindowedPresetButton",
    760,
    640);
```

The smoke finds both existing controls through UIA but does not invoke either Compatibility action before this capture. It must continue to avoid both Create buttons and any game launch.

- [ ] **Step 6: Run focused non-native regression tests**

Run:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~PatchBenchNarrowActionLabelsTests|FullyQualifiedName~PatchBenchLockedCompatibilityBaseTests|FullyQualifiedName~PatchBenchPlayerLabCurationTests"
```

Expected: PASS with no failed tests.

- [ ] **Step 7: Rebuild WinUI and run the authoritative hands-off native smoke**

First confirm no relevant process exists, then build and run serially:

```powershell
Get-Process OnslaughtCareerEditor.WinUI,BEA,testhost,vstest.console,dotnet -ErrorAction SilentlyContinue | Select-Object ProcessName,Id
npm run build:winui
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiPatchBenchInteractionSmokeTests.PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia"
Get-Process OnslaughtCareerEditor.WinUI,BEA,testhost,vstest.console,dotnet -ErrorAction SilentlyContinue | Select-Object ProcessName,Id
```

Expected: empty pre-census; zero-warning build; native smoke PASS; empty post-census. Keep the run hands-off. Inspect `%TEMP%\onslaught-patch-choice-state-20260625\patch-compatibility-actions-narrow.png` and confirm both complete labels are visible without ellipsis, overlap, or clipping.

- [ ] **Step 8: Run the proportionate lane gate and hygiene checks**

Run serially:

```powershell
npm run test:winui-primary-lane
npm run test:hard-payload-safety
git diff --check
```

Expected: WinUI primary lane PASS; hard-payload safety PASS; no whitespace errors. Do not run patch-engine/runtime/Ghidra gates because the slice changes no corresponding contract.

- [ ] **Step 9: Review, commit, push, and hand off**

Review the exact diff and confirm product changes remain XAML-only. If the diff remains within this presentation contract, no new four-role review envelope is required. Then run:

```powershell
git add OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml OnslaughtCareerEditor.UiTests/PatchBenchNarrowActionLabelsTests.cs OnslaughtCareerEditor.UiTests/WinUiPatchBenchInteractionSmokeTests.cs docs/superpowers/plans/2026-07-13-patch-bench-narrow-action-labels.md
git diff --cached --check
git commit -m "fix(winui): keep compatibility actions readable"
git push origin codex/player-value-ux-patch-quality
```

Expected: commit and push succeed; branch divergence is `0 0`; worktree is clean. Send primary coordination the commit hash, changed paths, exact focused/native/full evidence, screenshot path/visual result, zero-process census, and unchanged-scope nonclaims.
