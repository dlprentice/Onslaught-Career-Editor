using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiSaveAnalyzerInteractionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Requires a private real save path in ONSLAUGHT_WINUI_REAL_SAVE_PATH and captures ignored screenshots under subagents/.")]
    [Apartment(ApartmentState.STA)]
    public void SaveAnalyzer_AnalyzesRealSaveThroughUiWhenProvided()
    {
        string? savePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_SAVE_PATH");
        if (string.IsNullOrWhiteSpace(savePath) || !File.Exists(savePath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_SAVE_PATH to a private .bes or .bea file to run this visual smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-save-analyzer-interaction", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "saves";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = "0";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "1. Inspect a file", TimeSpan.FromSeconds(20));
            SetTextBox(window, "SaveAnalyzerFilePath", Path.GetFullPath(savePath));
            AutomationElement analyzeButton = FindByAutomationId(window, "SaveAnalyzerAnalyzeButton");
            bool analyzeReady = Retry.WhileFalse(() => analyzeButton.IsEnabled, TimeSpan.FromSeconds(5)).Success;
            Assert.That(analyzeReady, Is.True, "Expected Analyze / Reload to become enabled for the provided save path.");
            analyzeButton.AsButton().Invoke();

            bool analysisReady = Retry.WhileFalse(
                () => (TryGetName(FindByAutomationId(window, "SaveAnalyzerDocumentTitle")) ?? string.Empty)
                    .StartsWith("Analysis:", StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(analysisReady, Is.True, "Expected the analyzer document title to update after analysis.");
            Assert.That(TryGetName(FindByAutomationId(window, "SaveAnalyzerFileKindMetric")), Is.AnyOf("Career Save", "Global Options"));
            Assert.That(TryGetName(FindByAutomationId(window, "SaveAnalyzerSummaryTitle")), Is.EqualTo("Analysis Summary"));

            AutomationElement statusInfo = FindByAutomationId(window, "SaveAnalyzerStatusInfo");
            string statusName = TryGetName(statusInfo) ?? string.Empty;
            Assert.That(statusName, Does.Contain("Analysis complete").Or.Contain("Comparison complete"));

            string screenshotPath = Path.Combine(evidenceDir, "01-save-analysis.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Save analysis screenshot should not be empty.");
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Uses an OS-temp copy of the tracked gold save and writes only to an isolated app-owned output. Does not invoke File Explorer.")]
    [Apartment(ApartmentState.STA)]
    public void SaveEditor_GuidesAndWritesCopiedGoldSaveThroughUi()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string repoRoot = ResolveRepoRoot();
        string fixturePath = Path.Combine(repoRoot, "tests_shared", "fixtures", "gold_career_save.bin");
        Assert.That(File.Exists(fixturePath), Is.True, "Tracked gold career-save fixture is required.");

        string evidenceDir = Path.Combine(repoRoot, "subagents", "winui-save-editor-interaction", "2026-07-13");
        Directory.CreateDirectory(evidenceDir);
        string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-guided-first-save-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempRoot);
        string inputCopyPath = Path.Combine(tempRoot, "first-save-input.bes");
        File.Copy(fixturePath, inputCopyPath, overwrite: false);

        byte[] inputHashBefore = SHA256.HashData(File.ReadAllBytes(inputCopyPath));
        string appDataDir = PrepareIsolatedAppData(tempRoot);
        string outputPath = Path.Combine(
            appDataDir,
            "OnslaughtCareerEditor",
            "patched-output",
            "first-save-input_patched.bes");
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? repoRoot
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "saves";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = "1";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            var captureOperations = new FlaUiReceiptBoundVisualCaptureOperations(app, window, exePath);
            ReceiptBoundAppIdentity captureIdentity = captureOperations.ReadIdentity();

            WaitForText(window, "Your first copied save", TimeSpan.FromSeconds(20));
            SetTextBox(window, "SaveEditorInputFile", inputCopyPath);

            AutomationElement patchButton = FindByAutomationId(window, "SaveEditorPatchButton");
            bool outputSuggested = Retry.WhileFalse(
                () => string.Equals(
                    TryGetTextBoxText(FindByAutomationId(window, "SaveEditorOutputFile")),
                    outputPath,
                    StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(outputSuggested, Is.True, "Expected the app-owned separate output to follow the selected input.");
            AssertComboBoxSelectedText(window, "SaveEditorPatchPresetComboBox", "Start empty — choose sections");
            AssertCheckBoxState(window, "SaveEditorPatchNodesCheckBox", isChecked: false);
            AssertCheckBoxState(window, "SaveEditorPatchLinksCheckBox", isChecked: false);
            AssertCheckBoxState(window, "SaveEditorPatchGoodiesCheckBox", isChecked: false);
            AssertCheckBoxState(window, "SaveEditorPatchKillsCheckBox", isChecked: false);
            Assert.That(patchButton.IsEnabled, Is.False, "Start empty must keep Write disabled until a section is selected.");
            Assert.That(TryGetName(FindByAutomationId(window, "SaveEditorFirstSaveStatus")), Does.Contain("Choose at least one change"));
            Assert.That(TryGetName(FindByAutomationId(window, "SaveEditorAdvancedOverridesStatus")), Is.EqualTo("No advanced overrides active"));
            AutomationElement advancedExpander = FindByAutomationId(window, "SaveEditorAdvancedOverridesExpander");
            AutomationElement editorScroll = FindByAutomationId(window, "SaveEditorScrollViewer");
            ScrollIntoView(advancedExpander);
            Assert.That(advancedExpander.Patterns.ExpandCollapse.IsSupported, Is.True);
            Assert.That(advancedExpander.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value.ToString(), Is.EqualTo("Collapsed"));
            advancedExpander.Patterns.ExpandCollapse.Pattern.Expand();
            Assert.That(
                Retry.WhileFalse(
                    () => advancedExpander.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value.ToString() == "Expanded",
                    TimeSpan.FromSeconds(5)).Success,
                Is.True,
                "Advanced overrides should be reachable on demand.");
            _ = ScrollUntilAutomationIdIsRealized(window, editorScroll, "SaveEditorMissionOverridesHeading");
            _ = ScrollUntilAutomationIdIsRealized(window, editorScroll, "SaveEditorSetAllRanksDefaultButton");
            _ = ScrollUntilAutomationIdIsRealized(window, editorScroll, "SaveEditorCategoryKillOverridesHeading");
            _ = ScrollUntilAccessibleCheckBoxIsRealized(advancedExpander, editorScroll, "Aircraft");
            advancedExpander.Patterns.ExpandCollapse.Pattern.Collapse();
            Assert.That(
                Retry.WhileFalse(
                    () => advancedExpander.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value.ToString() == "Collapsed",
                    TimeSpan.FromSeconds(5)).Success,
                Is.True,
                "Advanced overrides should return to the compact first-save journey.");

            SetCheckBox(window, "SaveEditorPatchGoodiesCheckBox", isChecked: true);
            bool patchReady = Retry.WhileFalse(() => patchButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
            string? inputText = TryGetTextBoxText(FindByAutomationId(window, "SaveEditorInputFile"));
            string? outputText = TryGetTextBoxText(FindByAutomationId(window, "SaveEditorOutputFile"));
            string? pendingText = TryGetName(FindByAutomationId(window, "SaveEditorPendingChanges"));
            string? safetyText = TryGetName(FindByAutomationId(window, "SaveEditorSafetyHint"));
            Assert.That(
                patchReady,
                Is.True,
                $"Expected Write patched save copy after explicitly selecting Goodies. Input='{inputText}' Output='{outputText}' Pending='{pendingText}' Safety='{safetyText}'");
            Assert.That(pendingText, Does.Contain("goodies"));
            Assert.That(safetyText, Does.Contain("Save patching is ready"));

            ScrollIntoView(patchButton);
            patchButton.AsButton().Invoke();

            AutomationElement outputLog = FindByAutomationId(window, "SaveEditorOutputLog");
            bool outputReady = Retry.WhileFalse(
                () => File.Exists(outputPath)
                    && (TryGetTextBoxText(outputLog) ?? string.Empty).Contains("Successfully patched", StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(outputReady, Is.True, "Expected copied-save patch output to be written and reported in the UI.");
            string outputLogText = TryGetTextBoxText(outputLog) ?? string.Empty;
            Assert.That(outputLogText, Does.Contain("selected output file"));
            Assert.That(outputLogText, Does.Not.Contain(inputCopyPath), "Primary Save Editor output should not expose the copied input path.");
            Assert.That(outputLogText, Does.Not.Contain(outputPath), "Primary Save Editor output should not expose the copied output path.");
            Assert.That(new FileInfo(outputPath).Length, Is.EqualTo(BesFilePatcher.EXPECTED_FILE_SIZE));
            Assert.That(SHA256.HashData(File.ReadAllBytes(inputCopyPath)), Is.EqualTo(inputHashBefore), "Input copy should remain unchanged.");
            AutomationElement showWritten = FindByAutomationId(window, "SaveEditorShowWrittenSaveButton");
            bool completionReady = Retry.WhileFalse(
                () => showWritten.IsEnabled
                    && (TryGetName(FindByAutomationId(window, "SaveEditorFirstSaveStatus")) ?? string.Empty)
                        .Contains("Written copy ready", StringComparison.Ordinal),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(completionReady, Is.True, "Successful unchanged app-owned output should enable reveal and report completion.");

            string screenshotPath = Path.Combine(evidenceDir, "01-save-editor-patched.png");
            Rectangle normalBounds = captureOperations.ReadWindowState().Bounds;
            ReceiptBoundVisualCapture.Capture(
                captureOperations,
                BuildGuidedSaveCaptureRequest(
                    captureIdentity,
                    normalBounds,
                    screenshotPath,
                    () => RealizeGuidedSaveCompletionRegion(window, editorScroll, outputLog, showWritten)));

            string compactScreenshotPath = Path.Combine(evidenceDir, "02-save-editor-patched-760.png");
            Rectangle compactBounds = new(16, 16, 760, 820);
            ReceiptBoundVisualCapture.Capture(
                captureOperations,
                BuildGuidedSaveCaptureRequest(
                    captureIdentity,
                    compactBounds,
                    compactScreenshotPath,
                    () => RealizeGuidedSaveCompletionRegion(window, editorScroll, outputLog, showWritten)));
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }

            try
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
            catch
            {
                // The lease owner performs the authoritative post-run process/file cleanup check.
            }
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches WinUI directly into Game Options and verifies the modern-controller guidance without opening its external link.")]
    [Apartment(ApartmentState.STA)]
    public void ConfigurationEditor_ExposesModernControllerSetupWithoutOpeningBrowser()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(Path.GetTempPath(), "onslaught-winui-controller-guidance-2026-07-13");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "saves";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = "2";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            AutomationElement heading = FindByAutomationId(window, "ModernControllerSetupHeading");
            AutomationElement steps = FindByAutomationId(window, "ModernControllerSetupSteps");
            AutomationElement boundary = FindByAutomationId(window, "ModernControllerSetupBoundary");
            AutomationElement guideButton = FindByAutomationId(window, "OpenZigguratControllerGuideButton");
            AutomationElement numericCaveat = FindByAutomationId(window, "ControllerConfigNumericCaveat");

            Assert.Multiple(() =>
            {
                Assert.That(TryGetName(heading), Does.Contain("Modern controller setup"));
                Assert.That(TryGetName(steps), Does.Contain("Aquila - Gamepad with Mouse Aiming"));
                Assert.That(TryGetName(steps), Does.Contain("Movement: Forward"));
                Assert.That(TryGetName(steps), Does.Contain("mouse sensitivity to minimum"));
                Assert.That(TryGetName(boundary), Does.Contain("does not configure Steam Input"));
                Assert.That(TryGetName(boundary), Does.Contain("detect your connected controller"));
                Assert.That(TryGetName(boundary), Does.Contain("prove improved control feel"));
                Assert.That(TryGetName(guideButton), Is.EqualTo("Open Ziggurat's Steam setup guide in browser"));
                Assert.That(guideButton.IsEnabled, Is.True);
                Assert.That(TryGetName(numericCaveat), Does.Contain("raw numeric values"));
                Assert.That(TryGetName(numericCaveat), Does.Contain("not named modern-gamepad profiles"));
            });

            string screenshotPath = Path.Combine(evidenceDir, "01-modern-controller-setup.png");
            ScrollIntoView(heading);
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Controller guidance screenshot should not be empty.");
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Requires a private real options path in ONSLAUGHT_WINUI_REAL_OPTIONS_PATH and writes only copied outputs under subagents/.")]
    [Apartment(ApartmentState.STA)]
    public void ConfigurationEditor_PatchesCopiedOptionsThroughUiWhenProvided()
    {
        string? optionsPath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_OPTIONS_PATH");
        if (string.IsNullOrWhiteSpace(optionsPath) || !File.Exists(optionsPath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_OPTIONS_PATH to a private .bea file to run this copied-options editor smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-configuration-editor-interaction", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        string inputCopyPath = Path.Combine(evidenceDir, "input-copy.bea");
        string outputPath = Path.Combine(evidenceDir, "patched-output.bea");
        File.Copy(optionsPath, inputCopyPath, overwrite: true);
        if (File.Exists(outputPath))
        {
            File.Delete(outputPath);
        }

        byte[] inputHashBefore = SHA256.HashData(File.ReadAllBytes(inputCopyPath));
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "saves";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = "2";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            FindByAutomationId(window, "ConfigurationEditorTabButton").AsButton().Invoke();
            FindByAutomationId(window, "ConfigurationInputFile");
            SetTextBox(window, "ConfigurationInputFile", inputCopyPath);
            SetTextBox(window, "ConfigurationOutputFile", outputPath);
            SetTextBox(window, "ConfigurationControllerConfigP1", "1");

            AutomationElement patchButton = FindByAutomationId(window, "ConfigurationPatchButton");
            bool patchReady = Retry.WhileFalse(() => patchButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
            string? safetyText = TryGetName(FindByAutomationId(window, "ConfigurationSafetyHint"));
            Assert.That(
                patchReady,
                Is.True,
                $"Expected Write options copy to become enabled for copied input and distinct output paths. Safety='{safetyText}'");
            Assert.That(safetyText, Does.Contain("Game options patching is ready"));

            ScrollIntoView(patchButton);
            patchButton.AsButton().Invoke();

            AutomationElement outputLog = FindByAutomationId(window, "ConfigurationOutputLog");
            bool outputReady = Retry.WhileFalse(
                () => File.Exists(outputPath)
                    && (TryGetTextBoxText(outputLog) ?? string.Empty).Contains("Successfully patched", StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(outputReady, Is.True, "Expected copied-options patch output to be written and reported in the UI.");
            string outputLogText = TryGetTextBoxText(outputLog) ?? string.Empty;
            Assert.That(outputLogText, Does.Contain("selected output file"));
            Assert.That(outputLogText, Does.Not.Contain(inputCopyPath), "Primary Game Options output should not expose the copied input path.");
            Assert.That(outputLogText, Does.Not.Contain(outputPath), "Primary Game Options output should not expose the copied output path.");
            Assert.That(new FileInfo(outputPath).Length, Is.EqualTo(BesFilePatcher.EXPECTED_FILE_SIZE));
            Assert.That(SHA256.HashData(File.ReadAllBytes(inputCopyPath)), Is.EqualTo(inputHashBefore), "Input copy should remain unchanged.");

            string screenshotPath = Path.Combine(evidenceDir, "01-configuration-editor-patched.png");
            ScrollIntoView(outputLog);
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Game Options patch screenshot should not be empty.");
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        textBox.Focus();
        textBox.Text = text;
        bool valueApplied = Retry.WhileFalse(
            () => string.Equals(textBox.Text, text, StringComparison.Ordinal),
            TimeSpan.FromSeconds(5)).Success;
        Assert.That(valueApplied, Is.True, $"Expected {automationId} to accept the requested text value.");
    }

    private static void SetCheckBox(Window window, string automationId, bool isChecked)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Patterns.Toggle.IsSupported, Is.True, $"Expected toggle support: {automationId}");
        bool IsOn() => string.Equals(
            element.Patterns.Toggle.Pattern.ToggleState.Value.ToString(),
            "On",
            StringComparison.Ordinal);
        if (IsOn() != isChecked)
        {
            element.Patterns.Toggle.Pattern.Toggle();
        }

        bool applied = Retry.WhileFalse(() => IsOn() == isChecked, TimeSpan.FromSeconds(5)).Success;
        Assert.That(applied, Is.True, $"Expected {automationId} checked state to become {isChecked}.");
    }

    private static void AssertCheckBoxState(Window window, string automationId, bool isChecked)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Patterns.Toggle.IsSupported, Is.True, $"Expected toggle support: {automationId}");
        string expected = isChecked ? "On" : "Off";
        Assert.That(element.Patterns.Toggle.Pattern.ToggleState.Value.ToString(), Is.EqualTo(expected));
    }

    private static void AssertComboBoxSelectedText(Window window, string automationId, string expectedText)
    {
        bool selected = Retry.WhileFalse(
            () => string.Equals(
                FindByAutomationId(window, automationId).AsComboBox().SelectedItem?.Text,
                expectedText,
                StringComparison.Ordinal),
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(selected, Is.True, $"Expected {automationId} selected item: {expectedText}");
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static string? TryGetName(AutomationElement element)
    {
        try
        {
            return element.Name;
        }
        catch
        {
            return null;
        }
    }

    private static string? TryGetTextBoxText(AutomationElement element)
    {
        try
        {
            return element.AsTextBox().Text;
        }
        catch
        {
            return null;
        }
    }

    private static void ScrollIntoView(AutomationElement element)
    {
        try
        {
            if (element.Patterns.ScrollItem.IsSupported)
            {
                element.Patterns.ScrollItem.Pattern.ScrollIntoView();
            }
        }
        catch
        {
            // Best-effort visual positioning only; InvokePattern still drives the control.
        }
    }

    private static AutomationElement ScrollUntilAutomationIdIsRealized(
        Window window,
        AutomationElement scrollHost,
        string automationId)
    {
        Assert.That(scrollHost.Patterns.Scroll.IsSupported, Is.True, "Save Editor scroll host must expose ScrollPattern.");
        AutomationElement? realizedElement = null;
        bool realized = Retry.WhileFalse(
            () =>
            {
                realizedElement = window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
                if (realizedElement is not null)
                {
                    return true;
                }

                try
                {
                    scrollHost.Patterns.Scroll.Pattern.Scroll(ScrollAmount.NoAmount, ScrollAmount.LargeIncrement);
                }
                catch
                {
                    // Retry owns the bounded wait; the final assertion reports an unrealized exact ID.
                }

                return false;
            },
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(realized, Is.True, $"Expected exact automation element after bounded Save Editor scrolling: {automationId}");
        return realizedElement!;
    }

    private static AutomationElement ScrollUntilAccessibleCheckBoxIsRealized(
        AutomationElement scope,
        AutomationElement scrollHost,
        string accessibleName)
    {
        Assert.That(scrollHost.Patterns.Scroll.IsSupported, Is.True, "Save Editor scroll host must expose ScrollPattern.");
        AutomationElement? realizedElement = null;
        bool realized = Retry.WhileFalse(
            () =>
            {
                realizedElement = scope.FindFirstDescendant(cf =>
                    cf.ByName(accessibleName).And(cf.ByControlType(ControlType.CheckBox)));
                if (realizedElement is not null)
                {
                    return true;
                }

                try
                {
                    scrollHost.Patterns.Scroll.Pattern.Scroll(ScrollAmount.NoAmount, ScrollAmount.LargeIncrement);
                }
                catch
                {
                    // Retry owns the bounded wait; the final assertion reports the missing exact accessible target.
                }

                return false;
            },
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(realized, Is.True, $"Expected exact accessible category checkbox after bounded Save Editor scrolling: {accessibleName}");
        return realizedElement!;
    }

    private static ReceiptBoundVisualCaptureRequest BuildGuidedSaveCaptureRequest(
        ReceiptBoundAppIdentity identity,
        Rectangle targetBounds,
        string outputPath,
        Action postResizeRealization)
    {
        return new ReceiptBoundVisualCaptureRequest(
            identity,
            targetBounds,
            outputPath,
            new[] { "SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton" },
            TimeSpan.FromSeconds(3),
            postResizeRealization);
    }

    private static void RealizeGuidedSaveCompletionRegion(
        Window window,
        AutomationElement saveEditorScrollViewer,
        AutomationElement outputLog,
        AutomationElement showWritten)
    {
        Assert.That(
            saveEditorScrollViewer.AutomationId,
            Is.EqualTo("SaveEditorScrollViewer"),
            "Compact completion realization must use the exact Save Editor scroll host.");
        Assert.That(
            saveEditorScrollViewer.Patterns.Scroll.IsSupported,
            Is.True,
            "The exact Save Editor scroll host must expose ScrollPattern.");

        Rectangle? previousOutputBounds = null;
        Rectangle? previousRevealBounds = null;
        int stableSamples = 0;
        bool realizedAndStable = Retry.WhileFalse(
            () =>
            {
                Rectangle windowBounds = window.BoundingRectangle;
                Rectangle outputBounds = outputLog.BoundingRectangle;
                Rectangle revealBounds = showWritten.BoundingRectangle;
                bool bothInside = ContainsRectangle(windowBounds, outputBounds) &&
                                  ContainsRectangle(windowBounds, revealBounds);
                if (!bothInside)
                {
                    stableSamples = 0;
                    previousOutputBounds = null;
                    previousRevealBounds = null;
                    try
                    {
                        saveEditorScrollViewer.Patterns.Scroll.Pattern.Scroll(
                            ScrollAmount.NoAmount,
                            ScrollAmount.LargeIncrement);
                    }
                    catch
                    {
                        // The bounded retry reports failure against the exact named scroll host.
                    }

                    return false;
                }

                if (previousOutputBounds == outputBounds && previousRevealBounds == revealBounds)
                {
                    stableSamples++;
                }
                else
                {
                    stableSamples = 1;
                    previousOutputBounds = outputBounds;
                    previousRevealBounds = revealBounds;
                }

                return stableSamples >= 3;
            },
            TimeSpan.FromSeconds(5),
            TimeSpan.FromMilliseconds(100)).Success;

        Assert.That(
            realizedAndStable,
            Is.True,
            "SaveEditorOutputLog and SaveEditorShowWrittenSaveButton must be simultaneously visible and layout-stable after resizing the exact Save Editor viewport.");
    }

    private static bool ContainsRectangle(Rectangle container, Rectangle child)
    {
        return child.Width > 0 &&
               child.Height > 0 &&
               child.Left >= container.Left &&
               child.Top >= container.Top &&
               child.Right <= container.Right &&
               child.Bottom <= container.Bottom;
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByAutomationId(automationId)),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
    }

    private static Window WaitForMainWindow(Application app, UIA3Automation automation)
    {
        bool handleReady = Retry.WhileFalse(
            () => app.MainWindowHandle != IntPtr.Zero,
            TimeSpan.FromSeconds(30)).Success;

        if (!handleReady)
        {
            Assert.Ignore("Main window handle not available; ensure the app can launch in this desktop session.");
        }

        Window? window = Retry.WhileNull(
            () =>
            {
                try
                {
                    return automation.FromHandle(app.MainWindowHandle).AsWindow();
                }
                catch
                {
                    return null;
                }
            },
            TimeSpan.FromSeconds(30)).Result;

        Assert.That(window, Is.Not.Null);
        return window!;
    }

    private static string PrepareIsolatedAppData(string evidenceDir)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            $$"""
            {
              "gameDirectory": null,
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 820,
              "lastTab": 0,
              "lastSaveSubTab": 0,
              "lastMediaSubTab": 0,
              "assetCatalogPath": null,
              "allowBackgroundAudio": true,
              "allowBackgroundVideo": false,
              "preventAudioVideoOverlap": true
            }
            """);
        return appDataDir;
    }

    private static string ResolveWinUiAppPath()
    {
        string? explicitExePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_EXE_PATH");
        if (!string.IsNullOrWhiteSpace(explicitExePath))
        {
            return explicitExePath;
        }

        return Path.Combine(
            ResolveRepoRoot(),
            "OnslaughtCareerEditor.WinUI",
            "bin",
            "Debug",
            "net10.0-windows10.0.19041.0",
            "win-x64",
            "OnslaughtCareerEditor.WinUI.exe");
    }

    private static string ResolveRepoRoot()
    {
        return Path.GetFullPath(
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }

}
