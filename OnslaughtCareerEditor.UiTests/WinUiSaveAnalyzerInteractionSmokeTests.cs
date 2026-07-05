using System;
using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
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
    [Explicit("Requires a private real save path in ONSLAUGHT_WINUI_REAL_SAVE_PATH and writes only copied outputs under subagents/.")]
    [Apartment(ApartmentState.STA)]
    public void SaveEditor_PatchesCopiedRealSaveThroughUiWhenProvided()
    {
        string? savePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_SAVE_PATH");
        if (string.IsNullOrWhiteSpace(savePath) || !File.Exists(savePath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_SAVE_PATH to a private .bes file to run this copied-save editor smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-save-editor-interaction", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        string inputCopyPath = Path.Combine(evidenceDir, "input-copy.bes");
        string outputPath = Path.Combine(evidenceDir, "patched-output.bes");
        File.Copy(savePath, inputCopyPath, overwrite: true);
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
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = "1";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "File selection", TimeSpan.FromSeconds(20));
            SetTextBox(window, "SaveEditorInputFile", inputCopyPath);
            SetTextBox(window, "SaveEditorOutputFile", outputPath);

            AutomationElement patchButton = FindByAutomationId(window, "SaveEditorPatchButton");
            bool patchReady = Retry.WhileFalse(() => patchButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
            string? inputText = TryGetTextBoxText(FindByAutomationId(window, "SaveEditorInputFile"));
            string? outputText = TryGetTextBoxText(FindByAutomationId(window, "SaveEditorOutputFile"));
            string? pendingText = TryGetName(FindByAutomationId(window, "SaveEditorPendingChanges"));
            string? safetyText = TryGetName(FindByAutomationId(window, "SaveEditorSafetyHint"));
            Assert.That(
                patchReady,
                Is.True,
                $"Expected Write patched save copy to become enabled for copied input and distinct output paths. Input='{inputText}' Output='{outputText}' Pending='{pendingText}' Safety='{safetyText}'");
            Assert.That(pendingText, Does.Contain("Pending:"));
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

            string screenshotPath = Path.Combine(evidenceDir, "01-save-editor-patched.png");
            ScrollIntoView(outputLog);
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Save editor patch screenshot should not be empty.");
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
